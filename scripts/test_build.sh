#!/bin/bash

# 测试发布工作流的脚本
# 这个脚本可以帮助本地测试构建过程

echo "🚀 开始测试VideoClip构建流程..."

# 检查依赖
echo "📦 检查依赖..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，请先安装 uv"
    exit 1
fi

# 安装依赖
echo "📥 安装依赖..."
uv sync

# 添加PyInstaller
echo "🛠️ 添加PyInstaller..."
uv add pyinstaller

# 构建可执行文件
echo "🔨 构建可执行文件..."
uv run pyinstaller --name=VideoClip --onefile --windowed --add-data="*.py:." main.py

# 检查构建结果
if [ -f "dist/VideoClip" ] || [ -f "dist/VideoClip.exe" ]; then
    echo "✅ 构建成功！"
    ls -la dist/
else
    echo "❌ 构建失败！"
    exit 1
fi

echo "🎉 本地构建测试完成！"
