"""
视频处理模块
负责视频的读取、裁切和剪辑功能
"""

import os
import threading

import cv2
import numpy as np


class VideoProcessor:
    """
    视频处理器

    负责视频文件的加载、帧提取、裁切和剪辑等核心功能。
    """

    def __init__(self, callback_manager):
        """
        初始化视频处理器

        Args:
            callback_manager: 回调管理器，用于与UI通信
        """
        self.callback_manager = callback_manager
        self.cap = None
        self.video_path = ""
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
        self.total_frames = 0

    def load_video(self, video_path):
        """加载视频文件"""
        if self.cap:
            self.cap.release()

        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            return False, "无法打开视频文件"

        # 获取视频元数据
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        return True, "视频加载成功"

    def get_frame(self, frame_number):
        """获取指定帧"""
        if not self.cap or not self.cap.isOpened():
            return None

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = self.cap.read()

        if success:
            return frame
        return None

    def get_video_info(self):
        """获取视频信息"""
        return {
            "width": self.frame_width,
            "height": self.frame_height,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "duration": self.total_frames / self.fps if self.fps > 0 else 0,
        }

    def process_video(self, output_path, crop_params=None, trim_params=None):
        """
        在后台线程中处理视频

        Args:
            output_path: 输出文件路径
            crop_params: 裁切参数 {'x': int, 'y': int, 'width': int, 'height': int}
            trim_params: 时间裁切参数 {'start_frame': int, 'end_frame': int}
        """
        threading.Thread(
            target=self._process_video_thread,
            args=(output_path, crop_params, trim_params),
            daemon=True,
        ).start()

    def _process_video_thread(self, output_path, crop_params, trim_params):
        """视频处理线程"""
        try:
            # 确定输出尺寸
            if crop_params and crop_params["width"] > 0 and crop_params["height"] > 0:
                output_width = crop_params["width"]
                output_height = crop_params["height"]
            else:
                output_width = self.frame_width
                output_height = self.frame_height

            # 创建VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_path, fourcc, self.fps, (output_width, output_height))

            if not out.isOpened():
                self.callback_manager.on_error("无法创建输出文件")
                return

            # 保存当前帧位置
            original_frame_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)

            # 确定处理的帧范围
            if trim_params:
                start_frame = trim_params["start_frame"]
                end_frame = trim_params["end_frame"]
            else:
                start_frame = 0
                end_frame = self.total_frames - 1

            # 设置起始帧位置
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            # 计算进度
            total_frames = end_frame - start_frame + 1
            processed = 0

            current_frame_num = start_frame
            while current_frame_num <= end_frame:
                ret, frame = self.cap.read()
                if not ret:
                    break

                try:
                    processed_frame = frame

                    # 空间裁切（如果启用）
                    if crop_params and crop_params["width"] > 0 and crop_params["height"] > 0:
                        if (
                            crop_params["x"] + crop_params["width"] <= frame.shape[1]
                            and crop_params["y"] + crop_params["height"] <= frame.shape[0]
                        ):
                            processed_frame = frame[
                                crop_params["y"] : crop_params["y"] + crop_params["height"],
                                crop_params["x"] : crop_params["x"] + crop_params["width"],
                            ]
                        else:
                            # 如果超出范围，创建黑色帧
                            processed_frame = np.zeros(
                                (crop_params["height"], crop_params["width"], 3), dtype=np.uint8
                            )
                            self.callback_manager.on_warning(
                                f"帧 {current_frame_num} 裁切区域超出范围！"
                            )

                    out.write(processed_frame)

                except Exception as e:
                    self.callback_manager.on_error(f"帧 {current_frame_num}: {str(e)}")
                    out.release()
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return

                processed += 1
                current_frame_num += 1

                if processed % 10 == 0:  # 每10帧更新一次进度
                    self.callback_manager.on_progress(processed, total_frames)

            # 释放资源
            out.release()

            # 恢复原始帧位置
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, original_frame_pos)

            # 通知完成
            self.callback_manager.on_complete(output_path)

        except Exception as e:
            self.callback_manager.on_error(str(e))

    def release(self):
        """释放视频资源"""
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def __del__(self):
        """析构函数"""
        self.release()


class CallbackManager:
    """回调管理器，用于视频处理器与UI通信"""

    def __init__(self, root):
        """
        初始化回调管理器

        Args:
            root: Tkinter根窗口对象，用于线程间通信
        """
        self.root = root
        self.progress_callback = None
        self.complete_callback = None
        self.error_callback = None
        self.warning_callback = None

    def set_callbacks(self, progress_cb=None, complete_cb=None, error_cb=None, warning_cb=None):
        """设置回调函数"""
        self.progress_callback = progress_cb
        self.complete_callback = complete_cb
        self.error_callback = error_cb
        self.warning_callback = warning_cb

    def on_progress(self, processed, total):
        """进度回调"""
        if self.progress_callback:
            self.root.after(10, self.progress_callback, processed, total)

    def on_complete(self, output_path):
        """完成回调"""
        if self.complete_callback:
            self.root.after(10, self.complete_callback, output_path)

    def on_error(self, error_msg):
        """错误回调"""
        if self.error_callback:
            self.root.after(10, self.error_callback, error_msg)

    def on_warning(self, warning_msg):
        """警告回调"""
        if self.warning_callback:
            self.root.after(10, self.warning_callback, warning_msg)
