"""
工具函数模块
包含时间格式化等通用函数
"""

def format_time(seconds):
    """格式化时间显示为 MM:SS.mmm"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"

def get_frame_range_limits(total_frames):
    """获取帧范围的限制值"""
    if total_frames <= 0:
        return 0, 1
    max_frame_for_start = total_frames - 1  # 开始帧最大值：最后一帧的索引
    max_frame_for_end = total_frames - 1    # 结束帧最大值：最后一帧的索引
    return max_frame_for_start, max_frame_for_end

def generate_output_filename(video_path, crop_width=0, crop_height=0, 
                           trim_enabled=False, start_frame=0, end_frame=0):
    """生成输出文件名"""
    import os
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    suffix = ""
    
    if crop_width > 0 and crop_height > 0:
        suffix += f"_crop_{crop_width}x{crop_height}"
    if trim_enabled:
        suffix += f"_trim_{start_frame}-{end_frame}"
    
    return f"{base_name}{suffix}.mp4"
