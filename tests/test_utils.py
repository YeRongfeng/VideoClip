"""
工具函数测试
"""

import unittest

from utils import format_time, generate_output_filename, get_frame_range_limits


class TestUtils(unittest.TestCase):
    def test_format_time(self):
        """测试时间格式化函数"""
        # 测试基本格式化
        self.assertEqual(format_time(0), "00:00.000")
        self.assertEqual(format_time(30), "00:30.000")
        self.assertEqual(format_time(60), "01:00.000")
        self.assertEqual(format_time(90.5), "01:30.500")
        self.assertEqual(format_time(3661.123), "61:01.123")

    def test_get_frame_range_limits(self):
        """测试帧范围限制计算"""
        # 正常情况
        max_start, max_end = get_frame_range_limits(100)
        self.assertEqual(max_start, 99)  # 开始帧最大为总帧数-1
        self.assertEqual(max_end, 99)  # 结束帧最大为总帧数-1

        # 边界情况
        max_start, max_end = get_frame_range_limits(1)
        self.assertEqual(max_start, 0)
        self.assertEqual(max_end, 0)

        # 异常情况
        max_start, max_end = get_frame_range_limits(0)
        self.assertEqual(max_start, 0)
        self.assertEqual(max_end, 1)

    def test_generate_output_filename(self):
        """测试输出文件名生成"""
        # 基本测试
        filename = generate_output_filename("/path/to/video.mp4")
        self.assertEqual(filename, "video.mp4")

        # 带裁切参数
        filename = generate_output_filename("/path/to/video.mp4", 800, 600)
        self.assertEqual(filename, "video_crop_800x600.mp4")

        # 带时间裁切
        filename = generate_output_filename("/path/to/video.mp4", 0, 0, True, 30, 300)
        self.assertEqual(filename, "video_trim_30-300.mp4")

        # 同时带空间和时间裁切
        filename = generate_output_filename("/path/to/video.mp4", 800, 600, True, 30, 300)
        self.assertEqual(filename, "video_crop_800x600_trim_30-300.mp4")


if __name__ == "__main__":
    unittest.main()
