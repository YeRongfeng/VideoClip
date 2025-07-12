import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
import sys

class VideoCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("视频尺寸裁切工具")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # 视频相关变量
        self.video_path = ""
        self.cap = None
        self.total_frames = 0
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0
        
        # 裁切参数
        self.crop_x = 0
        self.crop_y = 0
        self.crop_width = 0
        self.crop_height = 0
        self.drawing = False
        self.rect_start = (0, 0)
        self.rect_end = (0, 0)
        self.display_offset = (0, 0)  # 添加图像显示偏移量
        
        # 创建界面
        self.create_widgets()
        
        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.root.bind("<Configure>", self.on_window_resize)

    def create_widgets(self):
        # 顶部控制区域
        control_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=10)
        control_frame.pack(fill=tk.X)
        
        # 文件选择
        file_frame = tk.Frame(control_frame, bg="#e0e0e0")
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(file_frame, text="视频文件:", bg="#e0e0e0").pack(side=tk.LEFT)
        self.file_entry = tk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="浏览...", command=self.browse_file).pack(side=tk.LEFT)
        
        # 预览控制
        preview_frame = tk.Frame(control_frame, bg="#e0e0e0")
        preview_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(preview_frame, text="预览帧:", bg="#e0e0e0").pack(side=tk.LEFT)
        self.frame_slider = tk.Scale(preview_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                    showvalue=True, command=self.update_preview)
        self.frame_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 裁切参数显示
        param_frame = tk.Frame(control_frame, bg="#e0e0e0")
        param_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(param_frame, text="裁切区域:", bg="#e0e0e0").grid(row=0, column=0, sticky="w")
        self.pos_label = tk.Label(param_frame, text="X: 0, Y: 0", bg="#e0e0e0")
        self.pos_label.grid(row=0, column=1, padx=5, sticky="w")
        
        tk.Label(param_frame, text="尺寸:", bg="#e0e0e0").grid(row=0, column=2, padx=(20, 5), sticky="w")
        self.size_label = tk.Label(param_frame, text="宽: 0, 高: 0", bg="#e0e0e0")
        self.size_label.grid(row=0, column=3, padx=5, sticky="w")
        
        # 操作按钮
        button_frame = tk.Frame(control_frame, bg="#e0e0e0")
        button_frame.pack(fill=tk.X, pady=10)
        
        self.preview_button = tk.Button(button_frame, text="预览裁切", command=self.preview_crop, 
                                      state=tk.DISABLED, width=15)
        self.preview_button.pack(side=tk.LEFT, padx=10)
        
        self.crop_button = tk.Button(button_frame, text="裁切视频", command=self.start_cropping, 
                                    state=tk.DISABLED, width=15)
        self.crop_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(button_frame, text="重置选择", command=self.reset_selection,
                                    state=tk.DISABLED, width=15)
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        # 分割线
        separator = tk.Frame(self.root, height=2, bg="gray")
        separator.pack(fill=tk.X, pady=5)
        
        # 图像显示区域
        img_frame = tk.Frame(self.root, bg="#d0d0d0", padx=10, pady=10)
        img_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(img_frame, bg="black", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_bar = tk.Label(self.root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#d0d0d0")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 添加缩放信息显示
        self.scale_info = tk.Label(self.root, text="缩放比例: -", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#d0d0d0")
        self.scale_info.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.video_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.load_video()

    def load_video(self):
        if self.cap:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            messagebox.showerror("错误", "无法打开视频文件")
            return
            
        # 获取元数据
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        self.frame_slider.config(from_=0, to=self.total_frames-1)
        
        # 获取第一帧作为预览
        success, frame = self.cap.read()
        if success:
            self.show_frame(frame)
            self.preview_button.config(state=tk.NORMAL)
            self.crop_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.status_bar.config(text=f"已加载视频: {os.path.basename(self.video_path)} | 尺寸: {self.frame_width}x{self.frame_height} | 帧率: {self.fps:.2f} | 总帧数: {self.total_frames}")
        else:
            messagebox.showerror("错误", "无法读取视频帧")
    
    def show_frame(self, frame, reset_canvas=False):
        if not hasattr(self, 'canvas') or self.canvas.winfo_width() < 10:
            return
            
        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.pil_image = Image.fromarray(self.current_frame)
        
        # 调整图像大小以适应画布
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_ratio = self.frame_width / self.frame_height
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
        
        self.display_image = self.pil_image.resize((new_width, new_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(image=self.display_image)
        
        # 清除画布并显示新图像
        self.canvas.delete("all")
        self.canvas.create_image(
            offset_x + new_width // 2, 
            offset_y + new_height // 2, 
            image=self.tk_image, 
            anchor=tk.CENTER
        )
        
        # 更新缩放比例
        self.scale_x = new_width / self.frame_width
        self.scale_y = new_height / self.frame_height
        self.scale_info.config(text=f"缩放比例: X: {self.scale_x:.4f}, Y: {self.scale_y:.4f} | 显示偏移: X: {offset_x}, Y: {offset_y}")
        
        # 如果已有裁切区域，则显示
        if self.crop_width > 0 and self.crop_height > 0:
            self.draw_crop_rectangle()
        
        # 确保图像不在垃圾回收时被删除
        self.last_image = self.tk_image

    def on_window_resize(self, event=None):
        """窗口大小改变时重绘当前帧"""
        if self.cap and self.cap.isOpened() and hasattr(self, 'current_frame'):
            # 获取当前帧位置
            frame_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            success, frame = self.cap.read()
            if success:
                self.show_frame(frame, True)

    def update_preview(self, value):
        if self.cap and self.cap.isOpened():
            frame_num = int(value)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            success, frame = self.cap.read()
            if success:
                self.show_frame(frame)
            self.status_bar.config(text=f"预览帧: {frame_num}/{self.total_frames}")

    def start_draw(self, event):
        if not self.cap or not self.cap.isOpened():
            return
            
        # 确保点击在图像范围内
        if (event.x < self.display_offset[0] or 
            event.x > self.display_offset[0] + self.display_image.width or
            event.y < self.display_offset[1] or 
            event.y > self.display_offset[1] + self.display_image.height):
            return
            
        self.drawing = True
        self.rect_start = (event.x, event.y)
        
    def draw_rect(self, event):
        if self.drawing:
            # 限制在图像区域内
            x = max(self.display_offset[0], min(event.x, self.display_offset[0] + self.display_image.width))
            y = max(self.display_offset[1], min(event.y, self.display_offset[1] + self.display_image.height))
            
            self.rect_end = (x, y)
            self.canvas.delete("rect")
            self.canvas.create_rectangle(
                self.rect_start[0], self.rect_start[1], 
                self.rect_end[0], self.rect_end[1], 
                outline="red", width=2, tags="rect"
            )

    def stop_draw(self, event):
        if not self.drawing:
            return
            
        self.drawing = False
        
        # 确保左上角和右下角的坐标正确
        x1, y1 = self.rect_start
        x2, y2 = self.rect_end
        
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
            
        # 调整坐标到图像实际位置
        x1 -= self.display_offset[0]
        y1 -= self.display_offset[1]
        x2 -= self.display_offset[0]
        y2 -= self.display_offset[1]
            
        # 确保在图像范围内
        x1 = max(0, min(x1, self.display_image.width))
        y1 = max(0, min(y1, self.display_image.height))
        x2 = max(0, min(x2, self.display_image.width))
        y2 = max(0, min(y2, self.display_image.height))
        
        # 计算原始坐标（考虑缩放）
        self.crop_x = int(x1 / self.scale_x)
        self.crop_y = int(y1 / self.scale_y)
        self.crop_width = int((x2 - x1) / self.scale_x)
        self.crop_height = int((y2 - y1) / self.scale_y)
        
        # 限制在原始视频范围内
        self.crop_x = max(0, min(self.crop_x, self.frame_width - 1))
        self.crop_y = max(0, min(self.crop_y, self.frame_height - 1))
        self.crop_width = min(self.crop_width, self.frame_width - self.crop_x)
        self.crop_height = min(self.crop_height, self.frame_height - self.crop_y)
        
        # 更新UI显示
        self.pos_label.config(text=f"X: {self.crop_x}, Y: {self.crop_y}")
        self.size_label.config(text=f"宽: {self.crop_width}, 高: {self.crop_height}")
        self.status_bar.config(text=f"已选择裁切区域: {self.crop_width}x{self.crop_height}")
        
        # 重新绘制矩形
        self.draw_crop_rectangle()

    def draw_crop_rectangle(self):
        """根据裁切参数在画布上绘制矩形"""
        if self.crop_width <= 0 or self.crop_height <= 0:
            return
            
        # 将原始坐标转换为缩放后的坐标
        x1 = int(self.crop_x * self.scale_x) + self.display_offset[0]
        y1 = int(self.crop_y * self.scale_y) + self.display_offset[1]
        x2 = x1 + int(self.crop_width * self.scale_x)
        y2 = y1 + int(self.crop_height * self.scale_y)
        
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

    def reset_selection(self):
        """重置裁切区域选择"""
        self.crop_x = 0
        self.crop_y = 0
        self.crop_width = 0
        self.crop_height = 0
        
        self.pos_label.config(text="X: 0, Y: 0")
        self.size_label.config(text="宽: 0, 高: 0")
        
        self.canvas.delete("rect")
        self.status_bar.config(text="裁切区域已重置")
        
        # 重新显示当前帧
        if self.cap and self.cap.isOpened():
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            success, frame = self.cap.read()
            if success:
                self.show_frame(frame)

    def preview_crop(self):
        """预览裁切效果"""
        if not self.cap or not self.cap.isOpened() or self.crop_width <= 0 or self.crop_height <= 0:
            return
            
        # 获取当前帧
        current_frame_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_pos)
        success, frame = self.cap.read()
        if not success:
            return
            
        # 裁切图像
        try:
            cropped = frame[self.crop_y:self.crop_y+self.crop_height, 
                           self.crop_x:self.crop_x+self.crop_width]
            
            # 显示在画布上
            cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            cropped_pil = Image.fromarray(cropped_rgb)
            
            # 获取当前画布大小
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 创建预览图片
            preview_img = cropped_pil.copy()
            
            # 保持宽高比缩放
            crop_ratio = cropped.shape[1] / cropped.shape[0]
            canvas_ratio = canvas_width / canvas_height
            
            if crop_ratio > canvas_ratio:
                new_width = canvas_width
                new_height = int(new_width / crop_ratio)
            else:
                new_height = canvas_height
                new_width = int(new_height * crop_ratio)
            
            if new_width > 0 and new_height > 0:
                preview_img = preview_img.resize((new_width, new_height), Image.LANCZOS)
            
            # 计算居中的位置
            offset_x = (canvas_width - new_width) // 2
            offset_y = (canvas_height - new_height) // 2
            
            self.canvas.delete("all")
            tk_preview = ImageTk.PhotoImage(image=preview_img)
            self.canvas.create_image(
                canvas_width // 2, 
                canvas_height // 2, 
                image=tk_preview, 
                anchor=tk.CENTER
            )
            self.preview_tk_image = tk_preview  # 防止垃圾回收
            
            self.status_bar.config(text=f"裁切预览: {cropped.shape[1]}x{cropped.shape[0]} | 按'返回'按钮恢复")
            
            # 添加返回按钮
            self.back_button = tk.Button(self.canvas, text="返回预览", 
                                      command=self.back_to_preview, 
                                      bg="#e0e0e0", fg="#000000")
            self.back_button.place(x=10, y=10)
            
        except Exception as e:
            messagebox.showerror("预览错误", f"预览时出错: {str(e)}")
            self.status_bar.config(text=f"预览错误: {str(e)}")
    
    def back_to_preview(self):
        """返回预览模式"""
        if self.cap and self.cap.isOpened():
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            success, frame = self.cap.read()
            if success:
                self.show_frame(frame)
                
        if hasattr(self, 'back_button'):
            self.back_button.destroy()
        
        self.status_bar.config(text="返回视频预览")

    def start_cropping(self):
        """开始裁切视频（在新线程中）"""
        if not self.cap or not self.cap.isOpened() or self.crop_width <= 0 or self.crop_height <= 0:
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4视频", "*.mp4"), ("AVI视频", "*.avi"), ("所有文件", "*.*")]
        )
        
        if not output_path:
            return
            
        # 禁用按钮
        self.crop_button.config(state=tk.DISABLED)
        self.preview_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.status_bar.config(text="正在裁切视频，请稍候...")
        
        # 创建并启动裁切线程
        threading.Thread(
            target=self.crop_video_thread,
            args=(output_path,),
            daemon=True
        ).start()

    def crop_video_thread(self, output_path):
        """在后台线程中执行裁切操作"""
        try:
            # 创建VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4格式
            out = cv2.VideoWriter(
                output_path, 
                fourcc, 
                self.fps, 
                (self.crop_width, self.crop_height)
            )
            
            if not out.isOpened():
                self.root.after(10, self.cropping_error, "无法创建输出文件")
                return
                
            # 保存当前帧位置
            original_frame_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            
            # 重置视频到第一帧
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # 计算进度
            total_frames = self.total_frames
            processed = 0
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                try:
                    # 确保裁切区域在帧内
                    if (self.crop_x + self.crop_width <= frame.shape[1] and
                        self.crop_y + self.crop_height <= frame.shape[0]):
                        
                        # 裁切帧并写入
                        cropped_frame = frame[
                            self.crop_y:self.crop_y+self.crop_height,
                            self.crop_x:self.crop_x+self.crop_width
                        ]
                        out.write(cropped_frame)
                    else:
                        # 如果超出范围，用黑色填充
                        self.root.after(10, lambda: self.status_bar.config(
                            text=f"警告: 帧 {processed} 裁切区域超出范围！"))
                    
                except Exception as e:
                    self.root.after(10, self.cropping_error, f"帧 {processed}: {str(e)}")
                    out.release()
                    os.remove(output_path)
                    return
                
                processed += 1
                if processed % 10 == 0:  # 每10帧更新一次进度
                    self.root.after(10, self.update_progress, processed, total_frames)
            
            # 释放资源
            out.release()
            
            # 恢复原始帧位置
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, original_frame_pos)
            
            # 更新UI
            self.root.after(10, self.cropping_complete, output_path)
            
        except Exception as e:
            self.root.after(10, self.cropping_error, str(e))

    def update_progress(self, processed, total):
        """更新进度显示"""
        percent = (processed / total) * 100
        self.status_bar.config(
            text=f"裁切进度: {processed}/{total} 帧 ({percent:.1f}%)"
        )

    def cropping_complete(self, output_path):
        """裁切完成回调"""
        self.crop_button.config(state=tk.NORMAL)
        self.preview_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        
        file_name = os.path.basename(output_path)
        self.status_bar.config(text=f"裁切完成! 已保存为: {file_name}")
        messagebox.showinfo("完成", f"视频裁切成功!\n保存位置: {output_path}")

    def cropping_error(self, error_msg):
        """裁切错误回调"""
        self.crop_button.config(state=tk.NORMAL)
        self.preview_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        
        self.status_bar.config(text=f"裁切出错! {error_msg}")
        messagebox.showerror("错误", f"视频裁切过程中发生错误:\n{error_msg}")
        
    def __del__(self):
        """释放资源"""
        if self.cap and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCropper(root)
    root.mainloop()