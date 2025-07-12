"""
测试配置文件
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_video_info():
    """提供测试用的视频信息"""
    return {
        'width': 1920,
        'height': 1080,
        'fps': 30.0,
        'total_frames': 900,  # 30秒视频
        'duration': 30.0
    }

@pytest.fixture
def sample_crop_params():
    """提供测试用的裁切参数"""
    return {
        'x': 100,
        'y': 100,
        'width': 800,
        'height': 600
    }

@pytest.fixture
def sample_trim_params():
    """提供测试用的时间裁切参数"""
    return {
        'start_frame': 30,  # 1秒
        'end_frame': 300   # 10秒
    }
