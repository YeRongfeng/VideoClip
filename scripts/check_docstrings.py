#!/usr/bin/env python3
"""
简单的docstring覆盖率检查脚本
"""

import ast
import sys
from pathlib import Path


def check_docstrings():
    """检查所有Python文件的docstring覆盖率"""
    total_items = 0
    missing_docstrings = 0

    # 要检查的文件
    py_files = [
        "main.py",
        "ui_components.py",
        "video_processor.py",
        "crop_controller.py",
        "utils.py",
        "config.py",
    ]

    for file_path in py_files:
        if not Path(file_path).exists():
            continue

        print(f"检查文件: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    total_items += 1
                    if ast.get_docstring(node) is None:
                        print(f"  缺少docstring: {node.name} (第{node.lineno}行)")
                        missing_docstrings += 1

        except Exception as e:
            print(f"  错误: {e}")
            continue

    coverage = (total_items - missing_docstrings) / total_items * 100 if total_items > 0 else 100
    print(f"\n总计: {total_items} 个函数/类")
    print(f"缺少docstring: {missing_docstrings} 个")
    print(f"覆盖率: {coverage:.1f}%")

    if missing_docstrings > 0:
        sys.exit(1)
    else:
        print("✅ 所有函数和类都有docstring！")


if __name__ == "__main__":
    check_docstrings()
