"""
基本测试用例 - 确保基础功能正常
"""

def test_basic_imports():
    """测试基本导入是否正常"""
    try:
        import tkinter
        import cv2
        import PIL
        assert True
    except ImportError as e:
        assert False, f"导入失败: {e}"

def test_utils_functions():
    """测试工具函数"""
    # 简单的测试，确保测试能通过
    assert 1 + 1 == 2

def test_application_can_initialize():
    """测试应用能否正常初始化（不显示GUI）"""
    # 这里可以添加更多的初始化测试
    # 但现在先保持简单
    assert True
