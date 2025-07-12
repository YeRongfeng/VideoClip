"""
应用程序配置模块
包含应用程序的配置常量和设置
"""

# 窗口配置
WINDOW_TITLE = "视频尺寸裁切工具"
WINDOW_SIZE = "1000x700"
WINDOW_BG = "#f0f0f0"

# 颜色配置
CONTROL_BG = "#e0e0e0"
CANVAS_BG = "#d0d0d0"
STATUS_BG = "#d0d0d0"

# 文件类型
SUPPORTED_VIDEO_FORMATS = [
    ("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv"),
    ("所有文件", "*.*")
]

OUTPUT_VIDEO_FORMATS = [
    ("MP4视频", "*.mp4"),
    ("AVI视频", "*.avi"),
    ("所有文件", "*.*")
]

# 处理配置
PROGRESS_UPDATE_INTERVAL = 10  # 每多少帧更新一次进度
DEFAULT_OUTPUT_EXTENSION = ".mp4"
VIDEO_FOURCC = 'mp4v'

# UI配置
BUTTON_WIDTH = 15
SLIDER_LENGTH = 150
