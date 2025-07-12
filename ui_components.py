"""
UI组件模块
包含各种界面组件和控件
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from utils import format_time, get_frame_range_limits


class VideoControlPanel:
    """视频控制面板"""
    
    def __init__(self, parent, bg_color="#e0e0e0"):
        self.parent = parent
        self.bg_color = bg_color
        self.callbacks = {}
        
        self.control_frame = tk.Frame(parent, bg=bg_color, padx=10, pady=10)
        self.control_frame.pack(fill=tk.X)
        
        self._create_file_selection()
        self._create_preview_controls()
        self._create_trim_controls()
        self._create_time_info()
        self._create_crop_params()
        self._create_action_buttons()
    
    def _create_file_selection(self):
        """创建文件选择控件"""
        file_frame = tk.Frame(self.control_frame, bg=self.bg_color)
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(file_frame, text="视频文件:", bg=self.bg_color).pack(side=tk.LEFT)
        self.file_entry = tk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="浏览...", 
                 command=self._browse_file).pack(side=tk.LEFT)
    
    def _create_preview_controls(self):
        """创建预览控制控件"""
        preview_frame = tk.Frame(self.control_frame, bg=self.bg_color)
        preview_frame.pack(fill=tk.X, pady=5)
        
        # 第一行：帧控制
        frame_control_frame = tk.Frame(preview_frame, bg=self.bg_color)
        frame_control_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(frame_control_frame, text="预览帧:", bg=self.bg_color).pack(side=tk.LEFT)
        self.frame_slider = tk.Scale(frame_control_frame, from_=0, to=100, 
                                   orient=tk.HORIZONTAL, showvalue=True,
                                   command=self._on_frame_change)
        self.frame_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 第二行：播放控制按钮
        playback_frame = tk.Frame(preview_frame, bg=self.bg_color)
        playback_frame.pack(fill=tk.X, pady=2)
        
        # 帧控制按钮
        self.prev_frame_btn = tk.Button(playback_frame, text="上一帧", 
                                       command=self._prev_frame, width=8)
        self.prev_frame_btn.pack(side=tk.LEFT, padx=2)
        
        self.play_pause_btn = tk.Button(playback_frame, text="播放", 
                                       command=self._toggle_play, width=8)
        self.play_pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.next_frame_btn = tk.Button(playback_frame, text="下一帧", 
                                       command=self._next_frame, width=8)
        self.next_frame_btn.pack(side=tk.LEFT, padx=2)
        
        # 设置起始/结束帧按钮
        tk.Label(playback_frame, text=" | ", bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        
        self.set_start_btn = tk.Button(playback_frame, text="设为起始帧", 
                                      command=self._set_start_frame, width=10)
        self.set_start_btn.pack(side=tk.LEFT, padx=2)
        
        self.set_end_btn = tk.Button(playback_frame, text="设为结束帧", 
                                    command=self._set_end_frame, width=10)
        self.set_end_btn.pack(side=tk.LEFT, padx=2)
        
        # 播放状态
        self.is_playing = False
    
    def _create_trim_controls(self):
        """创建时间裁切控件"""
        trim_frame = tk.Frame(self.control_frame, bg=self.bg_color)
        trim_frame.pack(fill=tk.X, pady=5)
        
        # 启用时间裁切复选框
        self.trim_var = tk.BooleanVar()
        self.trim_checkbox = tk.Checkbutton(trim_frame, text="启用时间裁切", 
                                          variable=self.trim_var, 
                                          command=self._toggle_trim,
                                          bg=self.bg_color)
        self.trim_checkbox.pack(side=tk.LEFT)
        
        # 开始帧控制
        tk.Label(trim_frame, text="开始帧:", bg=self.bg_color).pack(
            side=tk.LEFT, padx=(20, 5))
        self.start_frame_slider = tk.Scale(trim_frame, from_=0, to=1000, 
                                         orient=tk.HORIZONTAL, showvalue=True,
                                         command=self._on_start_frame_change,
                                         state=tk.DISABLED, length=150)
        self.start_frame_slider.pack(side=tk.LEFT, padx=5)
        
        # 结束帧控制
        tk.Label(trim_frame, text="结束帧:", bg=self.bg_color).pack(
            side=tk.LEFT, padx=(20, 5))
        self.end_frame_slider = tk.Scale(trim_frame, from_=1, to=1000, 
                                       orient=tk.HORIZONTAL, showvalue=True,
                                       command=self._on_end_frame_change,
                                       state=tk.DISABLED, length=150)
        self.end_frame_slider.pack(side=tk.LEFT, padx=5)
    
    def _create_time_info(self):
        """创建时间信息显示"""
        time_info_frame = tk.Frame(self.control_frame, bg=self.bg_color)
        time_info_frame.pack(fill=tk.X, pady=2)
        
        self.time_info_label = tk.Label(time_info_frame, text="", 
                                      bg=self.bg_color, fg="blue")
        self.time_info_label.pack(side=tk.LEFT)
    
    def _create_crop_params(self):
        """创建裁切参数显示"""
        param_frame = tk.Frame(self.control_frame, bg=self.bg_color)
        param_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(param_frame, text="裁切区域:", bg=self.bg_color).grid(
            row=0, column=0, sticky="w")
        self.pos_label = tk.Label(param_frame, text="X: 0, Y: 0", 
                                bg=self.bg_color)
        self.pos_label.grid(row=0, column=1, padx=5, sticky="w")
        
        tk.Label(param_frame, text="尺寸:", bg=self.bg_color).grid(
            row=0, column=2, padx=(20, 5), sticky="w")
        self.size_label = tk.Label(param_frame, text="宽: 0, 高: 0", 
                                 bg=self.bg_color)
        self.size_label.grid(row=0, column=3, padx=5, sticky="w")
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        button_frame = tk.Frame(self.control_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.preview_button = tk.Button(button_frame, text="预览裁切", 
                                      command=self._preview_crop,
                                      state=tk.DISABLED, width=15)
        self.preview_button.pack(side=tk.LEFT, padx=10)
        
        self.process_button = tk.Button(button_frame, text="处理视频", 
                                      command=self._process_video,
                                      state=tk.DISABLED, width=15)
        self.process_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(button_frame, text="重置选择", 
                                    command=self._reset_selection,
                                    state=tk.DISABLED, width=15)
        self.reset_button.pack(side=tk.LEFT, padx=10)
    
    def _browse_file(self):
        """浏览文件"""
        if 'browse_file' in self.callbacks:
            self.callbacks['browse_file']()
    
    def _on_frame_change(self, value):
        """帧变化回调"""
        if 'frame_change' in self.callbacks:
            self.callbacks['frame_change'](value)
    
    def _toggle_trim(self):
        """切换时间裁切"""
        if 'toggle_trim' in self.callbacks:
            self.callbacks['toggle_trim']()
    
    def _on_start_frame_change(self, value):
        """开始帧变化回调"""
        if 'start_frame_change' in self.callbacks:
            self.callbacks['start_frame_change'](value)
    
    def _on_end_frame_change(self, value):
        """结束帧变化回调"""
        if 'end_frame_change' in self.callbacks:
            self.callbacks['end_frame_change'](value)
    
    def _preview_crop(self):
        """预览裁切"""
        if 'preview_crop' in self.callbacks:
            self.callbacks['preview_crop']()
    
    def _process_video(self):
        """处理视频"""
        if 'process_video' in self.callbacks:
            self.callbacks['process_video']()
    
    def _reset_selection(self):
        """重置选择"""
        if 'reset_selection' in self.callbacks:
            self.callbacks['reset_selection']()
    
    def _prev_frame(self):
        """上一帧"""
        if 'prev_frame' in self.callbacks:
            self.callbacks['prev_frame']()
    
    def _next_frame(self):
        """下一帧"""
        if 'next_frame' in self.callbacks:
            self.callbacks['next_frame']()
    
    def _toggle_play(self):
        """播放/暂停切换"""
        if 'toggle_play' in self.callbacks:
            self.callbacks['toggle_play']()
    
    def _set_start_frame(self):
        """设置起始帧"""
        if 'set_start_frame' in self.callbacks:
            self.callbacks['set_start_frame']()
    
    def _set_end_frame(self):
        """设置结束帧"""
        if 'set_end_frame' in self.callbacks:
            self.callbacks['set_end_frame']()
    
    def set_play_button_text(self, text):
        """设置播放按钮文本"""
        self.play_pause_btn.config(text=text)
    
    def set_callback(self, event_name, callback):
        """设置回调函数"""
        self.callbacks[event_name] = callback
        """设置回调函数"""
        self.callbacks[event_name] = callback
    
    def update_video_info(self, total_frames, fps):
        """更新视频信息"""
        # 预览帧滑动条应该能到最大帧（total_frames-1是最后一帧的索引）
        self.frame_slider.config(from_=0, to=total_frames-1)
        
        # 修复帧范围设置 - 先启用控件再设置值
        max_start, max_end = get_frame_range_limits(total_frames)
        self.start_frame_slider.config(state=tk.NORMAL, from_=0, to=max_start)
        self.start_frame_slider.set(0)
        # 结束帧的最小值应该比开始帧大1，最大值是最后一帧索引
        self.end_frame_slider.config(state=tk.NORMAL, from_=1, to=max_end)
        self.end_frame_slider.set(max_end)  # 设置为最后一帧的索引
        
        # 根据当前时间裁剪状态重新设置控件状态
        trim_enabled = self.get_trim_enabled()
        self.set_trim_enabled(trim_enabled)
    
    def enable_controls(self, enabled=True):
        """启用/禁用控件"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.preview_button.config(state=state)
        self.process_button.config(state=state)
        self.reset_button.config(state=state)
        self.prev_frame_btn.config(state=state)
        self.play_pause_btn.config(state=state)
        self.next_frame_btn.config(state=state)
        self.set_start_btn.config(state=state)
        self.set_end_btn.config(state=state)
    
    def set_trim_enabled(self, enabled):
        """设置时间裁切是否启用"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.start_frame_slider.config(state=state)
        self.end_frame_slider.config(state=state)
    
    def update_crop_info(self, x, y, width, height):
        """更新裁切信息显示"""
        self.pos_label.config(text=f"X: {x}, Y: {y}")
        self.size_label.config(text=f"宽: {width}, 高: {height}")
    
    def update_time_info(self, info_text):
        """更新时间信息"""
        self.time_info_label.config(text=info_text)
    
    def get_file_path(self):
        """获取文件路径"""
        return self.file_entry.get()
    
    def set_file_path(self, path):
        """设置文件路径"""
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, path)
    
    def get_trim_enabled(self):
        """获取时间裁切是否启用"""
        return self.trim_var.get()
    
    def get_start_frame(self):
        """获取开始帧"""
        return self.start_frame_slider.get()
    
    def get_end_frame(self):
        """获取结束帧"""
        return self.end_frame_slider.get()
    
    def get_current_frame(self):
        """获取当前预览帧"""
        return self.frame_slider.get()
    
    def set_current_frame(self, frame):
        """设置当前预览帧"""
        self.frame_slider.set(frame)


class VideoCanvas:
    """视频显示画布"""
    
    def __init__(self, parent):
        self.parent = parent
        self.callbacks = {}
        
        # 图像显示区域
        img_frame = tk.Frame(parent, bg="#d0d0d0", padx=10, pady=10)
        img_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(img_frame, bg="black", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self._start_draw)
        self.canvas.bind("<B1-Motion>", self._draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self._stop_draw)
        
        # 绘制相关变量
        self.drawing = False
        self.rect_start = (0, 0)
        self.rect_end = (0, 0)
        self.display_offset = (0, 0)
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.display_image = None
        self.current_frame = None
    
    def _start_draw(self, event):
        """开始绘制"""
        if 'start_draw' in self.callbacks:
            self.callbacks['start_draw'](event)
    
    def _draw_rect(self, event):
        """绘制矩形"""
        if 'draw_rect' in self.callbacks:
            self.callbacks['draw_rect'](event)
    
    def _stop_draw(self, event):
        """停止绘制"""
        if 'stop_draw' in self.callbacks:
            self.callbacks['stop_draw'](event)
    
    def set_callback(self, event_name, callback):
        """设置回调函数"""
        self.callbacks[event_name] = callback
    
    def show_frame(self, frame):
        """显示帧图像"""
        if not hasattr(self, 'canvas') or self.canvas.winfo_width() < 10:
            return False
        
        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(self.current_frame)
        
        # 调整图像大小以适应画布
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        frame_height, frame_width = frame.shape[:2]
        img_ratio = frame_width / frame_height
        canvas_ratio = canvas_width / canvas_height
        
        # 计算缩放后的尺寸
        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(new_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(new_height * img_ratio)
        
        # 计算图像偏移量（居中显示）
        offset_x = (canvas_width - new_width) // 2
        offset_y = (canvas_height - new_height) // 2
        self.display_offset = (offset_x, offset_y)
        
        self.display_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(image=self.display_image)
        
        # 清除画布并显示新图像
        self.canvas.delete("all")
        self.canvas.create_image(
            offset_x + new_width // 2, 
            offset_y + new_height // 2, 
            image=tk_image, 
            anchor=tk.CENTER
        )
        
        # 更新缩放比例
        self.scale_x = new_width / frame_width
        self.scale_y = new_height / frame_height
        
        # 确保图像不在垃圾回收时被删除
        self.last_image = tk_image
        
        return True
    
    def draw_crop_rectangle(self, x, y, width, height):
        """绘制裁切矩形"""
        if width <= 0 or height <= 0:
            return
        
        # 将原始坐标转换为缩放后的坐标
        x1 = int(x * self.scale_x) + self.display_offset[0]
        y1 = int(y * self.scale_y) + self.display_offset[1]
        x2 = x1 + int(width * self.scale_x)
        y2 = y1 + int(height * self.scale_y)
        
        # 限制在画布内
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x1 = max(0, min(x1, canvas_width))
        y1 = max(0, min(y1, canvas_height))
        x2 = max(0, min(x2, canvas_width))
        y2 = max(0, min(y2, canvas_height))
        
        self.canvas.delete("rect")
        self.canvas.create_rectangle(
            x1, y1, x2, y2, 
            outline="red", width=2, tags="rect"
        )
    
    def clear_rectangle(self):
        """清除矩形"""
        self.canvas.delete("rect")
    
    def show_preview(self, cropped_frame):
        """显示裁切预览"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 转换为RGB
        cropped_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
        cropped_pil = Image.fromarray(cropped_rgb)
        
        # 保持宽高比缩放
        crop_ratio = cropped_frame.shape[1] / cropped_frame.shape[0]
        canvas_ratio = canvas_width / canvas_height
        
        if crop_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(new_width / crop_ratio)
        else:
            new_height = canvas_height
            new_width = int(new_height * crop_ratio)
        
        if new_width > 0 and new_height > 0:
            preview_img = cropped_pil.resize((new_width, new_height), Image.LANCZOS)
        else:
            preview_img = cropped_pil
        
        self.canvas.delete("all")
        tk_preview = ImageTk.PhotoImage(image=preview_img)
        self.canvas.create_image(
            canvas_width // 2, 
            canvas_height // 2, 
            image=tk_preview, 
            anchor=tk.CENTER
        )
        self.preview_tk_image = tk_preview  # 防止垃圾回收
        
        # 添加返回按钮
        self.back_button = tk.Button(self.canvas, text="返回预览", 
                                   command=self._back_to_preview, 
                                   bg="#e0e0e0", fg="#000000")
        self.back_button.place(x=10, y=10)
    
    def _back_to_preview(self):
        """返回预览模式"""
        if 'back_to_preview' in self.callbacks:
            self.callbacks['back_to_preview']()
        
        if hasattr(self, 'back_button'):
            self.back_button.destroy()


class StatusBar:
    """状态栏"""
    
    def __init__(self, parent):
        self.status_bar = tk.Label(parent, text="就绪", bd=1, relief=tk.SUNKEN, 
                                 anchor=tk.W, bg="#d0d0d0")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.scale_info = tk.Label(parent, text="缩放比例: -", bd=1, relief=tk.SUNKEN, 
                                 anchor=tk.W, bg="#d0d0d0")
        self.scale_info.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_status(self, text):
        """设置状态文本"""
        self.status_bar.config(text=text)
    
    def set_scale_info(self, scale_x, scale_y, offset_x, offset_y):
        """设置缩放信息"""
        self.scale_info.config(
            text=f"缩放比例: X: {scale_x:.4f}, Y: {scale_y:.4f} | 显示偏移: X: {offset_x}, Y: {offset_y}"
        )
