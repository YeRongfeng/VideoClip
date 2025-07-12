import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os

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
        
        # 创建界面
        self.create_widgets()
        
        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

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
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            messagebox.showerror("错误", "无法打开视频文件")
            return
            
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
    
    def show_frame(self, frame):
        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.pil_image = Image.fromarray(self.current_frame)
        
        # 调整图像大小以适应画布
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:  # 初始画布大小判断
            canvas_width = 800
            canvas_height = 450
            
        img_ratio = self.frame_width / self.frame_height
        canvas_ratio = canvas_width / canvas_height
        
        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(new_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(new_height * img_ratio)
            
        self.display_image = self.pil_image.resize((new_width, new_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(image=self.display_image)
        
        # 清除画布并显示新图像
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.tk_image, anchor=tk.CENTER)
        
        # 更新缩放比例
        self.scale_factor = new_width / self.frame_width
        
        # 如果已有裁切区域，则显示
        if self.crop_width > 0 and self.crop_height > 0:
            self.draw_crop_rectangle()

    def update_preview(self, value):
        if self.cap and self.cap.isOpened():
            frame_num = int(value)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            success, frame = self.cap.read()
            if success:
                self.show_frame(frame)
            self.status_bar.config(text=f"预览帧: {frame_num}/{self.total_frames}")

    def start_draw(self, event):
        self.drawing = True
        self.rect_start = (event.x, event.y)
        
    def draw_rect(self, event):
        if self.drawing:
            self.rect_end = (event.x, event.y)
            self.canvas.delete("rect")
            self.canvas.create_rectangle(
                self.rect_start[0], self.rect_start[1], 
                self.rect_end[0], self.rect_end[1], 
                outline="red", width=2, tags="rect"
            )

    def stop_draw(self, event):
        self.drawing = False
        self.rect_end = (event.x, event.y)
        
        # 确保左上角和右下角的坐标正确
        x1, y1 = self.rect_start
        x2, y2 = self.rect_end
        
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
            
        # 计算裁切参数（转换为原始坐标）
        self.crop_x = int(x1 / self.scale_factor)
        self.crop_y = int(y1 / self.scale_factor)
        self.crop_width = int((x2 - x1) / self.scale_factor)
        self.crop_height = int((y2 - y1) / self.scale_factor)
        
        # 更新UI显示
        self.pos_label.config(text=f"X: {self.crop_x}, Y: {self.crop_y}")
        self.size_label.config(text=f"宽: {self.crop_width}, 高: {self.crop_height}")
        self.status_bar.config(text=f"已选择裁切区域: {self.crop_width}x{self.crop_height}")

    def draw_crop_rectangle(self):
        """根据裁切参数在画布上绘制矩形"""
        if self.crop_width <= 0 or self.crop_height <= 0:
            return
            
        # 将原始坐标转换为缩放后的坐标
        x1 = int(self.crop_x * self.scale_factor)
        y1 = int(self.crop_y * self.scale_factor)
        x2 = x1 + int(self.crop_width * self.scale_factor)
        y2 = y1 + int(self.crop_height * self.scale_factor)
        
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
        self.canvas.delete("crop_preview")
        self.status_bar.config(text="裁切区域已重置")

    def preview_crop(self):
        """预览裁切效果"""
        if not self.cap or not self.cap.isOpened() or self.crop_width <= 0 or self.crop_height <= 0:
            return
            
        # 获取当前帧
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        success, frame = self.cap.read()
        if not success:
            return
            
        # 裁切图像
        cropped = frame[self.crop_y:self.crop_y+self.crop_height, 
                        self.crop_x:self.crop_x+self.crop_width]
        
        # 显示在画布上
        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        cropped_pil = Image.fromarray(cropped_rgb)
        
        # 调整大小以适合原始预览区域
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10:
            canvas_width = 800
            canvas_height = 450
            
        preview_width = min(canvas_width, cropped.shape[1])
        preview_height = min(canvas_height, cropped.shape[0])
        
        preview_img = cropped_pil.resize((preview_width, preview_height), Image.LANCZOS)
        preview_tk = ImageTk.PhotoImage(image=preview_img)
        
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                image=preview_tk, anchor=tk.CENTER, tags="crop_preview")
        
        # 防止图像被垃圾回收
        self.preview_tk_image = preview_tk
        
        self.status_bar.config(text=f"裁切预览: {self.crop_width}x{self.crop_height} | 按任意键返回")

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
            
            # 重置视频到第一帧
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # 计算进度
            total_frames = self.total_frames
            processed = 0
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # 裁切帧并写入
                cropped_frame = frame[
                    self.crop_y:self.crop_y+self.crop_height,
                    self.crop_x:self.crop_x+self.crop_width
                ]
                out.write(cropped_frame)
                
                processed += 1
                if processed % 10 == 0:  # 每10帧更新一次进度
                    self.root.after(10, self.update_progress, processed, total_frames)
            
            # 释放资源
            out.release()
            
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
        
        self.status_bar.config(text="裁切出错!")
        messagebox.showerror("错误", f"视频裁切过程中发生错误:\n{error_msg}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCropper(root)
    root.mainloop()