# 视频裁切工具 (VideoClip)

[![CI](https://github.com/YeRongfeng/VideoClip/workflows/CI/badge.svg)](https://github.com/YeRongfeng/VideoClip/actions/workflows/ci.yml)
[![Code Quality](https://github.com/YeRongfeng/VideoClip/workflows/Code%20Quality/badge.svg)](https://github.com/YeRongfeng/VideoClip/actions/workflows/code-quality.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个功能强大的基于 Python 和 Tkinter 的图形化视频裁切和剪辑工具，支持可视化选择裁切区域、时间剪辑和实时预览功能。

## ✨ 功能特性

### 核心功能
- 🎬 **空间裁切**: 通过鼠标拖拽在视频预览界面直接选择裁切区域
- ⏱️ **时间剪辑**: 支持选择视频的起始和结束时间，实现精确剪辑
- 🎥 **实时预览**: 支持拖拽进度条预览视频任意帧，播放控制功能
- 📏 **精确控制**: 实时显示裁切区域的坐标和尺寸信息
- 🖼️ **裁切预览**: 裁切前可以预览裁切效果，支持预览模式下的播放

### 播放控制
- ▶️ **播放/暂停**: 视频播放控制，支持实时播放预览
- ⏭️ **逐帧控制**: 上一帧/下一帧精确控制
- 📍 **时间定位**: 快速设置起始帧和结束帧到当前位置
- 📊 **实时信息**: 显示当前帧数、时间和播放状态

### 用户体验
- 📱 **用户友好**: 简洁直观的图形界面，操作简单
- 🔄 **智能缩放**: 自动适应窗口大小，保持视频比例
- 📈 **进度显示**: 实时显示处理进度和详细状态信息
- 🎯 **智能输出**: 自动生成带有裁切信息的文件名

## 🔧 系统要求

- Python 3.8 或更高版本
- Windows/Linux 操作系统
- 足够的磁盘空间用于视频处理

## 📦 安装

### 使用 uv (推荐)

```bash
# 克隆项目
git clone https://github.com/YeRongfeng/VideoClip.git
cd VideoClip

# 安装依赖
uv sync

# 或者安装开发依赖
uv sync --dev
```

### 使用 pip

```bash
# 克隆项目
git clone https://github.com/YeRongfeng/VideoClip.git
cd VideoClip

# 安装核心依赖
pip install opencv-python pillow

# 或者安装所有依赖
pip install -e .[dev,build]
```

## 🚀 使用方法

### 启动程序

```bash
# 使用 uv (推荐)
uv run python main.py

# 或者使用 videoclip 命令
uv run videoclip

# 直接运行
python main.py
```

### 详细操作步骤

#### 1. 选择视频文件
- 点击"浏览..."按钮选择要处理的视频文件
- 支持常见视频格式（MP4、AVI、MOV、MKV、FLV等）
- 视频加载后会显示基本信息（尺寸、帧率、总帧数）

#### 2. 视频预览和导航
- **进度条预览**: 拖动进度条查看视频的不同帧
- **播放控制**: 使用播放/暂停按钮控制视频播放
- **逐帧控制**: 使用上一帧/下一帧按钮精确导航
- **实时信息**: 底部状态栏显示当前帧数和时间信息

#### 3. 空间裁切设置
- 在视频预览区域按住鼠标左键拖拽选择裁切区域
- 实时显示裁切区域的坐标和尺寸
- 可以重复调整直到满意
- 点击"重置选择"清除当前选择

#### 4. 时间剪辑设置（可选）
- 勾选"启用时间裁切"选项
- 使用起始帧和结束帧滑块设置时间范围
- 或者使用"设为起始"/"设为结束"按钮快速设置当前帧
- 实时显示剪辑时长和帧数信息

#### 5. 预览和确认
- 点击"预览裁切"按钮查看裁切后的效果
- 在预览模式下也可以播放视频查看连续效果
- 点击"返回"按钮退出预览模式

#### 6. 执行处理
- 点击"处理视频"按钮开始处理
- 选择输出文件位置和文件名
- 程序会显示详细的进度信息
- 完成后自动打开保存位置

## 🎮 界面说明

### 控制面板
- **文件选择**: 浏览和选择视频文件
- **播放控制**: 播放/暂停、上一帧/下一帧按钮
- **进度控制**: 预览帧滑块，可拖拽到任意位置
- **时间裁切**: 启用选项和起始/结束帧设置
- **空间裁切**: 显示选中区域的坐标和尺寸信息
- **操作按钮**: 预览裁切、处理视频、重置选择等

### 显示区域
- **主预览区**: 显示原始视频，可在此选择裁切区域
- **预览窗口**: 显示裁切后的效果（预览模式）
- **状态栏**: 显示当前状态、帧信息和缩放比例

## 🛠️ 技术栈

### 核心依赖
- **Python 3.8+**: 主要编程语言
- **Tkinter**: 图形用户界面框架
- **OpenCV**: 视频处理和计算机视觉库
- **PIL/Pillow**: 图像处理和显示库

### 开发工具
- **uv**: 现代Python包管理器
- **ruff**: 代码格式化和检查工具
- **pytest**: 测试框架
- **GitHub Actions**: 持续集成和部署

## 📁 项目结构

```
VideoClip/
├── main.py                 # 主程序入口
├── ui_components.py        # UI组件模块
├── video_processor.py      # 视频处理模块
├── crop_controller.py      # 裁切控制器
├── utils.py               # 工具函数
├── config.py              # 配置常量
├── pyproject.toml         # 项目配置
├── uv.lock               # 依赖锁定文件
├── .github/              # GitHub Actions 工作流
│   └── workflows/
├── tests/                # 测试文件
├── scripts/              # 辅助脚本
└── README.md            # 项目文档
```

## 🧩 架构设计

### 主要模块

#### `VideoCropper` (主应用类)
- **初始化**: `__init__()` - 设置UI和组件
- **文件处理**: `browse_file()`, `load_video()` - 文件选择和加载
- **预览控制**: `update_preview()`, `toggle_play()` - 视频预览和播放
- **裁切功能**: `preview_crop()`, `start_processing()` - 裁切预览和处理
- **时间剪辑**: `toggle_trim()`, `update_start_frame()` - 时间范围控制

#### `VideoProcessor` (视频处理器)
- **视频加载**: `load_video()` - 视频文件加载和信息获取
- **帧提取**: `get_frame()` - 获取指定帧的图像数据
- **视频处理**: `process_video()` - 执行裁切和剪辑操作
- **线程管理**: 使用后台线程进行视频处理

#### `CropController` (裁切控制器)
- **区域选择**: `start_draw()`, `draw_rect()` - 鼠标拖拽选择
- **坐标转换**: 画布坐标到视频坐标的转换
- **参数管理**: `get_crop_params()` - 获取裁切参数

#### `UI Components` (UI组件)
- **VideoControlPanel**: 控制面板，包含所有控制元素
- **VideoCanvas**: 视频显示画布，支持缩放和交互
- **StatusBar**: 状态栏，显示实时信息

### 核心功能实现

1. **视频处理**: 使用 OpenCV 进行视频读取、帧提取和输出
2. **界面渲染**: OpenCV → PIL → Tkinter 的图像转换流程
3. **事件处理**: 鼠标拖拽、滑块变化等UI交互事件
4. **线程协调**: 主线程UI + 后台线程视频处理
5. **状态管理**: 播放状态、预览模式、处理进度等

## 🔧 开发指南

### 环境设置

```bash
# 克隆项目
git clone https://github.com/YeRongfeng/VideoClip.git
cd VideoClip

# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest

# 代码检查
uv run ruff check .

# 代码格式化
uv run ruff format .
```

### 构建可执行文件

```bash
# 安装构建依赖
uv sync --dev

# 构建可执行文件
uv run pyinstaller --onefile --windowed main.py
```

## ⚠️ 注意事项

### 性能优化
- 对于大视频文件，建议先预览确定裁切区域再处理
- 处理过程中请勿关闭程序，等待处理完成
- 确保有足够的磁盘空间（至少是原视频文件大小的2倍）

### 文件管理
- 输出文件会保存到用户选择的位置
- 文件名会自动添加裁切和剪辑信息后缀
- 支持的输出格式：MP4（推荐）、AVI

### 系统兼容性
- Windows: 完全支持，推荐使用
- Linux: 支持，需要安装tkinter
- macOS: 理论支持，但未在CI中测试

## ❓ 常见问题

### 安装和运行问题

**Q: 如何安装 uv？**  
A: 参考 [uv官方文档](https://docs.astral.sh/uv/) 进行安装，或使用 `pip install uv`

**Q: 为什么提示缺少 tkinter？**  
A: 在某些Linux发行版中需要手动安装：`sudo apt-get install python3-tk`

**Q: 视频无法加载？**  
A: 确保视频文件格式受支持，或尝试转换为MP4格式

### 功能使用问题

**Q: 支持哪些视频格式？**  
A: 支持 OpenCV 能够读取的所有格式，包括 MP4、AVI、MOV、MKV、FLV 等

**Q: 可以同时进行空间裁切和时间剪辑吗？**  
A: 是的，两种功能可以同时使用，程序会先进行时间剪辑，再进行空间裁切

**Q: 裁切后的视频质量如何？**  
A: 程序会尽量保持原始视频的编码设置，确保输出质量

**Q: 处理大视频文件需要多长时间？**  
A: 处理时间取决于视频大小、长度和计算机性能，通常每分钟视频需要几十秒到几分钟

**Q: 可以批量处理视频吗？**  
A: 当前版本只支持单个视频处理，批量功能在计划中

### 错误处理

**Q: 处理过程中出现错误怎么办？**  
A: 程序会显示详细错误信息，请检查：
- 视频文件是否损坏
- 磁盘空间是否充足
- 是否有文件写入权限

## 🤝 贡献指南

我们欢迎所有形式的贡献！请参考以下步骤：

### 提交Issue
- 使用清晰的标题描述问题
- 提供详细的复现步骤
- 包含系统信息和错误日志

### 提交Pull Request
1. Fork项目到你的GitHub账户
2. 创建功能分支: `git checkout -b feature/your-feature`
3. 提交更改: `git commit -am 'Add some feature'`
4. 推送分支: `git push origin feature/your-feature`
5. 创建Pull Request

### 开发规范
- 遵循PEP 8代码风格
- 添加适当的文档字符串
- 编写测试用例
- 确保CI检查通过

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。您可以自由使用、修改和分发此软件。

## 🔄 版本历史

### v0.1.0 (2024-12-XX)
- ✨ 初始版本发布
- 🎬 实现基础的视频空间裁切功能
- ⏱️ 添加时间剪辑功能
- 🎥 支持实时预览和播放控制
- 📱 完整的图形用户界面
- 🧪 完善的测试覆盖
- 🚀 CI/CD自动化流程

### 计划中的功能
- 📦 批量处理支持
- 🎨 更多输出格式选项
- 🎵 音频处理功能
- 🔧 更多高级裁切选项
- 🌐 多语言支持

## 📞 联系方式

- **项目主页**: [https://github.com/YeRongfeng/VideoClip](https://github.com/YeRongfeng/VideoClip)
- **问题反馈**: [GitHub Issues](https://github.com/YeRongfeng/VideoClip/issues)
- **功能建议**: [GitHub Discussions](https://github.com/YeRongfeng/VideoClip/discussions)

## 🙏 致谢

感谢所有贡献者和使用者的支持！

---

⭐ 如果这个项目对您有帮助，请给我们一个 Star！