# GitHub Actions 工作流说明

本项目配置了完整的 CI/CD 工作流，包含代码质量检查、测试、构建和发布等流程。

## 工作流文件

### 1. CI 工作流 (`.github/workflows/ci.yml`)

**触发条件:**
- 推送到 `master`, `main`, `develop` 分支
- 向 `master`, `main` 分支提交 Pull Request

**功能:**
- 多平台测试 (Ubuntu, Windows, macOS)
- 多 Python 版本支持 (3.8, 3.9, 3.10, 3.11)
- 代码格式检查 (ruff)
- 类型检查 (mypy)
- 单元测试 (pytest)
- 代码覆盖率统计
- 安全扫描 (safety, bandit)

### 2. 构建和发布工作流 (`.github/workflows/release.yml`)

**触发条件:**
- 推送版本标签 (如 `v1.0.0`)
- 手动触发

**功能:**
- 多平台可执行文件构建
- 自动创建 GitHub Release
- 上传构建产物到 Release

**构建产物:**
- `VideoClip-Windows.zip` - Windows 可执行文件
- `VideoClip-macOS.tar.gz` - macOS 应用程序包
- `VideoClip-Linux.tar.gz` - Linux 可执行文件

### 3. 代码质量工作流 (`.github/workflows/code-quality.yml`)

**触发条件:**
- 推送到主分支
- Pull Request
- 每周定时运行

**功能:**
- 深度代码质量分析
- 复杂度分析 (radon)
- 依赖关系分析
- 文档覆盖率检查
- README 链接验证

### 4. 依赖更新工作流 (`.github/workflows/dependencies.yml`)

**触发条件:**
- 每周一定时运行
- 手动触发

**功能:**
- 自动检查依赖更新
- 安全漏洞扫描
- 自动创建更新 PR
- 过期依赖报告

## 使用说明

### 发布新版本

1. 确保所有测试通过
2. 更新版本号在 `pyproject.toml`
3. 创建版本标签:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. GitHub Actions 自动构建并发布

### 手动触发构建

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Build and Release" 工作流
3. 点击 "Run workflow"
4. 输入版本号并运行

### 本地开发环境设置

```bash
# 安装开发依赖
uv sync --all-extras --dev

# 运行测试
uv run pytest

# 代码格式检查
uv run ruff check .
uv run ruff format .

# 类型检查
uv run mypy .

# 安全检查
uv run safety check
uv run bandit -r .
```

## 徽章 (Badges)

可以在 README.md 中添加以下徽章:

```markdown
![CI](https://github.com/YeRongfeng/VideoClip/workflows/CI/badge.svg)
![Build](https://github.com/YeRongfeng/VideoClip/workflows/Build%20and%20Release/badge.svg)
![Code Quality](https://github.com/YeRongfeng/VideoClip/workflows/Code%20Quality/badge.svg)
[![codecov](https://codecov.io/gh/YeRongfeng/VideoClip/branch/master/graph/badge.svg)](https://codecov.io/gh/YeRongfeng/VideoClip)
```

## 配置说明

### 所需的 GitHub Secrets

目前使用的是默认的 `GITHUB_TOKEN`，无需额外配置。如果需要更高级的功能，可以添加:

- `CODECOV_TOKEN` - 用于代码覆盖率上传 (可选)
- `PYPI_TOKEN` - 用于发布到 PyPI (如需要)

### 依赖管理

- 使用 `uv` 进行快速依赖管理
- 支持 `pyproject.toml` 现代 Python 项目配置
- 自动依赖更新和安全扫描

### 测试环境

- 支持 GUI 应用测试 (pytest-qt)
- 跨平台兼容性测试
- 代码覆盖率统计和报告
