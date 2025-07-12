"""
裁切控制器模块
负责处理用户的裁切操作和坐标计算
"""


class CropController:
    """裁切控制器"""

    def __init__(self, canvas):
        """
        初始化裁切控制器

        Args:
            canvas: 视频显示画布对象
        """
        self.canvas = canvas
        self.crop_x = 0
        self.crop_y = 0
        self.crop_width = 0
        self.crop_height = 0
        self.drawing = False
        self.rect_start = (0, 0)
        self.rect_end = (0, 0)

        # 设置画布回调
        self.canvas.set_callback("start_draw", self.start_draw)
        self.canvas.set_callback("draw_rect", self.draw_rect)
        self.canvas.set_callback("stop_draw", self.stop_draw)

        # 回调函数
        self.on_crop_changed = None

    def start_draw(self, event):
        """开始绘制裁切区域"""
        if not hasattr(self.canvas, "display_image") or not self.canvas.display_image:
            return

        # 确保点击在图像范围内
        if (
            event.x < self.canvas.display_offset[0]
            or event.x > self.canvas.display_offset[0] + self.canvas.display_image.width
            or event.y < self.canvas.display_offset[1]
            or event.y > self.canvas.display_offset[1] + self.canvas.display_image.height
        ):
            return

        self.drawing = True
        self.rect_start = (event.x, event.y)

    def draw_rect(self, event):
        """绘制裁切矩形"""
        if not self.drawing:
            return

        # 限制在图像区域内
        x = max(
            self.canvas.display_offset[0],
            min(event.x, self.canvas.display_offset[0] + self.canvas.display_image.width),
        )
        y = max(
            self.canvas.display_offset[1],
            min(event.y, self.canvas.display_offset[1] + self.canvas.display_image.height),
        )

        self.rect_end = (x, y)
        self.canvas.canvas.delete("rect")
        self.canvas.canvas.create_rectangle(
            self.rect_start[0],
            self.rect_start[1],
            self.rect_end[0],
            self.rect_end[1],
            outline="red",
            width=2,
            tags="rect",
        )

    def stop_draw(self, event):
        """停止绘制并计算裁切参数"""
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
        x1 -= self.canvas.display_offset[0]
        y1 -= self.canvas.display_offset[1]
        x2 -= self.canvas.display_offset[0]
        y2 -= self.canvas.display_offset[1]

        # 确保在图像范围内
        x1 = max(0, min(x1, self.canvas.display_image.width))
        y1 = max(0, min(y1, self.canvas.display_image.height))
        x2 = max(0, min(x2, self.canvas.display_image.width))
        y2 = max(0, min(y2, self.canvas.display_image.height))

        # 计算原始坐标（考虑缩放）
        if hasattr(self.canvas, "current_frame") and self.canvas.current_frame is not None:
            frame_height, frame_width = self.canvas.current_frame.shape[:2]

            self.crop_x = int(x1 / self.canvas.scale_x)
            self.crop_y = int(y1 / self.canvas.scale_y)
            self.crop_width = int((x2 - x1) / self.canvas.scale_x)
            self.crop_height = int((y2 - y1) / self.canvas.scale_y)

            # 限制在原始视频范围内
            self.crop_x = max(0, min(self.crop_x, frame_width - 1))
            self.crop_y = max(0, min(self.crop_y, frame_height - 1))
            self.crop_width = min(self.crop_width, frame_width - self.crop_x)
            self.crop_height = min(self.crop_height, frame_height - self.crop_y)

            # 重新绘制矩形
            self.canvas.draw_crop_rectangle(
                self.crop_x, self.crop_y, self.crop_width, self.crop_height
            )

            # 通知裁切参数变化
            if self.on_crop_changed:
                self.on_crop_changed(self.crop_x, self.crop_y, self.crop_width, self.crop_height)

    def reset_crop(self):
        """重置裁切区域"""
        self.crop_x = 0
        self.crop_y = 0
        self.crop_width = 0
        self.crop_height = 0

        self.canvas.clear_rectangle()

        if self.on_crop_changed:
            self.on_crop_changed(0, 0, 0, 0)

    def get_crop_params(self):
        """获取裁切参数"""
        return {
            "x": self.crop_x,
            "y": self.crop_y,
            "width": self.crop_width,
            "height": self.crop_height,
        }

    def has_valid_crop(self):
        """检查是否有有效的裁切区域"""
        return self.crop_width > 0 and self.crop_height > 0

    def redraw_crop_rectangle(self):
        """重新绘制裁切矩形"""
        if self.has_valid_crop():
            self.canvas.draw_crop_rectangle(
                self.crop_x, self.crop_y, self.crop_width, self.crop_height
            )
