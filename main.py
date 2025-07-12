import tkinter as tk
from tkinter import filedialog, messagebox
import os

from ui_components import VideoControlPanel, VideoCanvas, StatusBar
from video_processor import VideoProcessor, CallbackManager
from crop_controller import CropController
from utils import format_time, generate_output_filename
from config import *

class VideoCropper:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=WINDOW_BG)
        
        # 初始化组件和处理器
        self._init_components()
        self._setup_callbacks()
        
        # 绑定窗口调整事件
        self.root.bind("<Configure>", self.on_window_resize)

    def _init_components(self):
        """初始化UI组件和处理器"""
        # UI组件
        self.control_panel = VideoControlPanel(self.root, bg_color=CONTROL_BG)
        separator = tk.Frame(self.root, height=2, bg="gray")
        separator.pack(fill=tk.X, pady=5)
        self.video_canvas = VideoCanvas(self.root)
        self.status_bar = StatusBar(self.root)
        
        # 逻辑和处理组件
        self.callback_manager = CallbackManager(self.root)
        self.video_processor = VideoProcessor(self.callback_manager)
        self.crop_controller = CropController(self.video_canvas)
        
        # 状态变量
        self.video_loaded = False
        self.trim_enabled = False
        self.start_frame = 0
        self.end_frame = 0
        
        # 播放控制状态
        self.is_playing = False
        self.play_timer = None
        self.is_in_crop_preview = False  # 标识是否在裁切预览模式

    def _setup_callbacks(self):
        """设置组件之间的回调"""
        # 控制面板回调
        self.control_panel.set_callback('browse_file', self.browse_file)
        self.control_panel.set_callback('frame_change', self.update_preview)
        self.control_panel.set_callback('toggle_trim', self.toggle_trim)
        self.control_panel.set_callback('start_frame_change', self.update_start_frame)
        self.control_panel.set_callback('end_frame_change', self.update_end_frame)
        self.control_panel.set_callback('preview_crop', self.preview_crop)
        self.control_panel.set_callback('process_video', self.start_processing)
        self.control_panel.set_callback('reset_selection', self.reset_selection)
        
        # 新增的播放控制回调
        self.control_panel.set_callback('prev_frame', self.prev_frame)
        self.control_panel.set_callback('next_frame', self.next_frame)
        self.control_panel.set_callback('toggle_play', self.toggle_play)
        self.control_panel.set_callback('set_start_frame', self.set_start_frame_to_current)
        self.control_panel.set_callback('set_end_frame', self.set_end_frame_to_current)
        
        # 视频处理回调
        self.callback_manager.set_callbacks(
            progress_cb=self.on_progress,
            complete_cb=self.on_complete,
            error_cb=self.on_error,
            warning_cb=self.on_warning
        )
        
        # 裁切控制器回调
        self.crop_controller.on_crop_changed = self.on_crop_changed
        
        # 画布回调
        self.video_canvas.set_callback('back_to_preview', self.back_to_preview)

    def browse_file(self):
        """浏览并加载视频文件"""
        file_path = filedialog.askopenfilename(filetypes=SUPPORTED_VIDEO_FORMATS)
        if file_path:
            self.control_panel.set_file_path(file_path)
            self.load_video(file_path)

    def load_video(self, video_path):
        """加载视频"""
        success, message = self.video_processor.load_video(video_path)
        if not success:
            messagebox.showerror("错误", message)
            return
            
        self.video_loaded = True
        video_info = self.video_processor.get_video_info()
        
        # 初始化时间裁切状态变量
        self.start_frame = 0
        self.end_frame = video_info['total_frames'] - 1  # 设置为最后一帧的索引
        
        # 更新UI
        self.control_panel.update_video_info(video_info['total_frames'], video_info['fps'])
        self.control_panel.enable_controls(True)
        
        # 确保结束帧与UI控件同步
        self.end_frame = self.control_panel.get_end_frame()
        
        status_text = (f"已加载视频: {os.path.basename(video_path)} | "
                       f"尺寸: {video_info['width']}x{video_info['height']} | "
                       f"帧率: {video_info['fps']:.2f} | "
                       f"总帧数: {video_info['total_frames']}")
        self.status_bar.set_status(status_text)
        
        # 显示第一帧
        first_frame = self.video_processor.get_frame(0)
        if first_frame is not None:
            self.video_canvas.show_frame(first_frame)
            self.status_bar.set_scale_info(self.video_canvas.scale_x, self.video_canvas.scale_y,
                                           self.video_canvas.display_offset[0], self.video_canvas.display_offset[1])
        
        self.update_time_info()

    def on_window_resize(self, event=None):
        """窗口大小改变时重绘当前帧"""
        if self.video_loaded and not self.is_in_crop_preview:
            current_frame_num = self.control_panel.get_current_frame()
            frame = self.video_processor.get_frame(current_frame_num)
            if frame is not None:
                self.video_canvas.show_frame(frame)
                self.crop_controller.redraw_crop_rectangle()
                self.status_bar.set_scale_info(self.video_canvas.scale_x, self.video_canvas.scale_y,
                                               self.video_canvas.display_offset[0], self.video_canvas.display_offset[1])

    def update_preview(self, value):
        """更新预览帧"""
        if not self.video_loaded:
            return
            
        frame_num = int(value)
        
        # 如果启用了时间裁切，限制预览范围
        if self.trim_enabled:
            if frame_num < self.start_frame:
                frame_num = self.start_frame
                self.control_panel.set_current_frame(frame_num)
            elif frame_num > self.end_frame:
                frame_num = self.end_frame
                self.control_panel.set_current_frame(frame_num)
        
        frame = self.video_processor.get_frame(frame_num)
        if frame is not None:
            self.video_canvas.show_frame(frame)
            self.crop_controller.redraw_crop_rectangle()
        
        # 更新状态栏显示当前时间（使用1基索引显示更直观）
        video_info = self.video_processor.get_video_info()
        current_time = frame_num / video_info['fps'] if video_info['fps'] > 0 else 0
        time_str = format_time(current_time)
        self.status_bar.set_status(f"预览帧: {frame_num + 1}/{video_info['total_frames']} (时间: {time_str})")
    
    def update_preview_for_playback(self, frame_num):
        """播放时的优化预览更新（减少状态栏更新频率）"""
        if not self.video_loaded:
            return
            
        frame = self.video_processor.get_frame(frame_num)
        if frame is not None:
            self.video_canvas.show_frame(frame)
            self.crop_controller.redraw_crop_rectangle()

    def on_crop_changed(self, x, y, width, height):
        """裁切区域变化时的回调"""
        self.control_panel.update_crop_info(x, y, width, height)
        self.status_bar.set_status(f"已选择裁切区域: {width}x{height}")

    def reset_selection(self):
        """重置裁切选择"""
        self.crop_controller.reset_crop()
        self.status_bar.set_status("裁切区域已重置")
        self.update_preview(self.control_panel.get_current_frame())

    def preview_crop(self):
        """预览裁切效果"""
        if not self.video_loaded or not self.crop_controller.has_valid_crop():
            return
            
        current_frame_num = self.control_panel.get_current_frame()
        frame = self.video_processor.get_frame(current_frame_num)
        if frame is None:
            return
            
        crop_params = self.crop_controller.get_crop_params()
        try:
            cropped_frame = frame[crop_params['y']:crop_params['y']+crop_params['height'], 
                                  crop_params['x']:crop_params['x']+crop_params['width']]
            
            self.is_in_crop_preview = True  # 设置预览模式标志
            self.video_canvas.show_preview(cropped_frame)
            self.status_bar.set_status(f"裁切预览: {cropped_frame.shape[1]}x{cropped_frame.shape[0]} | 按'返回'按钮恢复")
        except Exception as e:
            messagebox.showerror("预览错误", f"预览时出错: {str(e)}")
            self.status_bar.set_status(f"预览错误: {str(e)}")

    def back_to_preview(self):
        """从预览裁切返回"""
        self.is_in_crop_preview = False  # 退出预览模式
        if self.video_loaded:
            current_frame_num = self.control_panel.get_current_frame()
            frame = self.video_processor.get_frame(current_frame_num)
            if frame is not None:
                self.video_canvas.show_frame(frame)
                self.crop_controller.redraw_crop_rectangle()
        self.status_bar.set_status("返回视频预览")

    def start_processing(self):
        """开始处理视频"""
        if not self.video_loaded:
            return
            
        has_spatial_crop = self.crop_controller.has_valid_crop()
        has_time_crop = self.trim_enabled and self.start_frame < self.end_frame
        
        if not has_spatial_crop and not has_time_crop:
            messagebox.showwarning("警告", "请至少选择空间裁切区域或启用时间裁切！")
            return
        
        crop_params = self.crop_controller.get_crop_params()
        
        default_name = generate_output_filename(
            self.video_processor.video_path,
            crop_params['width'], crop_params['height'],
            self.trim_enabled, self.start_frame, self.end_frame
        )
        
        output_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=DEFAULT_OUTPUT_EXTENSION,
            filetypes=OUTPUT_VIDEO_FORMATS
        )
        
        if not output_path:
            return
            
        self.control_panel.enable_controls(False)
        self.status_bar.set_status("正在处理视频，请稍候...")
        
        trim_params = {'start_frame': self.start_frame, 'end_frame': self.end_frame} if has_time_crop else None
        crop_params_to_pass = crop_params if has_spatial_crop else None
        
        self.video_processor.process_video(output_path, crop_params_to_pass, trim_params)

    def on_progress(self, processed, total):
        """处理进度回调"""
        percent = (processed / total) * 100
        operation_type = self._get_operation_type()
        self.status_bar.set_status(f"{operation_type}进度: {processed}/{total} 帧 ({percent:.1f}%)")

    def on_complete(self, output_path):
        """处理完成回调"""
        self.control_panel.enable_controls(True)
        operation_type = self._get_operation_type()
        file_name = os.path.basename(output_path)
        self.status_bar.set_status(f"{operation_type}完成! 已保存为: {file_name}")
        messagebox.showinfo("完成", f"视频{operation_type}成功!\n保存位置: {output_path}")

    def on_error(self, error_msg):
        """处理错误回调"""
        self.control_panel.enable_controls(True)
        self.status_bar.set_status(f"处理出错! {error_msg}")
        messagebox.showerror("错误", f"视频处理过程中发生错误:\n{error_msg}")

    def on_warning(self, warning_msg):
        """处理警告回调"""
        self.status_bar.set_status(f"警告: {warning_msg}")

    def toggle_trim(self):
        """切换时间裁切功能"""
        self.trim_enabled = self.control_panel.get_trim_enabled()
        self.control_panel.set_trim_enabled(self.trim_enabled)
        
        if self.trim_enabled:
            # 确保结束帧不小于开始帧
            if self.control_panel.get_end_frame() <= self.control_panel.get_start_frame():
                video_info = self.video_processor.get_video_info()
                new_end = min(self.control_panel.get_start_frame() + 1, video_info['total_frames'] - 1)
                self.control_panel.end_frame_slider.set(new_end)
        
        self.update_time_info()
    
    def update_start_frame(self, value):
        """更新开始帧"""
        start_frame = int(value)
        end_frame = self.control_panel.get_end_frame()
        
        if start_frame >= end_frame:
            start_frame = max(0, end_frame - 1)
            self.control_panel.start_frame_slider.set(start_frame)
        
        self.start_frame = start_frame
        self.update_time_info()
        
        current_frame = self.control_panel.get_current_frame()
        if current_frame < start_frame:
            self.update_preview(start_frame)
    
    def update_end_frame(self, value):
        """更新结束帧"""
        end_frame = int(value)
        start_frame = self.control_panel.get_start_frame()
        
        if end_frame <= start_frame:
            video_info = self.video_processor.get_video_info()
            end_frame = min(start_frame + 1, video_info['total_frames'] - 1)
            self.control_panel.end_frame_slider.set(end_frame)
        
        self.end_frame = end_frame
        self.update_time_info()
        
        current_frame = self.control_panel.get_current_frame()
        if current_frame > end_frame:
            self.update_preview(end_frame)
    
    def update_time_info(self):
        """更新时间信息显示"""
        if not self.video_loaded:
            return
            
        video_info = self.video_processor.get_video_info()
        fps = video_info['fps']
        
        if self.trim_enabled:
            self.start_frame = self.control_panel.get_start_frame()
            self.end_frame = self.control_panel.get_end_frame()
            
            start_time = self.start_frame / fps
            end_time = self.end_frame / fps
            duration = end_time - start_time
            
            start_time_str = format_time(start_time)
            end_time_str = format_time(end_time)
            duration_str = format_time(duration)
            
            trim_frames = self.end_frame - self.start_frame + 1
            
            info_text = (f"时间裁切: {start_time_str} - {end_time_str} "
                         f"(时长: {duration_str}, 帧数: {trim_frames})")
        else:
            total_time = video_info['duration']
            total_time_str = format_time(total_time)
            info_text = f"总时长: {total_time_str}"
        
        self.control_panel.update_time_info(info_text)
    
    def _get_operation_type(self):
        """获取操作类型字符串"""
        has_spatial_crop = self.crop_controller.has_valid_crop()
        has_time_crop = self.trim_enabled
        
        if has_spatial_crop and has_time_crop:
            return "裁切和剪辑"
        elif has_spatial_crop:
            return "裁切"
        elif has_time_crop:
            return "剪辑"
        return "处理"
    
    def prev_frame(self):
        """上一帧"""
        if not self.video_loaded:
            return
        current_frame = self.control_panel.get_current_frame()
        if current_frame > 0:
            new_frame = current_frame - 1
            self.control_panel.set_current_frame(new_frame)
            self.update_preview(new_frame)
    
    def next_frame(self):
        """下一帧"""
        if not self.video_loaded:
            return
        current_frame = self.control_panel.get_current_frame()
        video_info = self.video_processor.get_video_info()
        if current_frame < video_info['total_frames'] - 1:
            new_frame = current_frame + 1
            self.control_panel.set_current_frame(new_frame)
            self.update_preview(new_frame)
    
    def toggle_play(self):
        """播放/暂停切换"""
        if not self.video_loaded:
            return
            
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """开始播放"""
        self.is_playing = True
        self.control_panel.set_play_button_text("暂停")
        self.play_next_frame()
    
    def stop_playback(self):
        """停止播放"""
        self.is_playing = False
        self.control_panel.set_play_button_text("播放")
        if self.play_timer:
            self.root.after_cancel(self.play_timer)
            self.play_timer = None
    
    def play_next_frame(self):
        """播放下一帧"""
        if not self.is_playing:
            return
            
        current_frame = self.control_panel.get_current_frame()
        video_info = self.video_processor.get_video_info()
        
        # 检查是否到达结束
        max_frame = video_info['total_frames'] - 1
        if self.trim_enabled and current_frame >= self.end_frame:
            # 如果启用了时间裁切且到达结束帧，停止播放
            self.stop_playback()
            return
        elif not self.trim_enabled and current_frame >= max_frame:
            # 如果到达视频末尾，停止播放
            self.stop_playback()
            return
        
        # 播放下一帧
        new_frame = current_frame + 1
        self.control_panel.set_current_frame(new_frame)
        # 播放时使用优化的预览更新
        self.update_preview_for_playback(new_frame)
        
        # 计算播放间隔（基于帧率），使用浮点数计算提高精度
        fps = video_info['fps']
        if fps > 0:
            interval = max(16, round(1000.0 / fps))  # 最小16ms间隔（约60fps最大）
        else:
            interval = 33  # 默认30fps
        
        # 安排下一帧播放
        self.play_timer = self.root.after(interval, self.play_next_frame)
    
    def set_start_frame_to_current(self):
        """将起始帧设置为当前帧"""
        if not self.video_loaded:
            return
        current_frame = self.control_panel.get_current_frame()
        self.control_panel.start_frame_slider.set(current_frame)
        self.update_start_frame(current_frame)
    
    def set_end_frame_to_current(self):
        """将结束帧设置为当前帧"""
        if not self.video_loaded:
            return
        current_frame = self.control_panel.get_current_frame()
        self.control_panel.end_frame_slider.set(current_frame)
        self.update_end_frame(current_frame)

    def __del__(self):
        """释放资源"""
        self.stop_playback()
        if hasattr(self, 'video_processor'):
            self.video_processor.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCropper(root)
    root.mainloop()