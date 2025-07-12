# GitHub Actions 工作流说明

本项目配置了完整的 CI/CD 工作流，包含代码质量检查、测试、构建和发布等流程。

## 工作流概览

| 工作流 | 触发条件 | 主要功能 |
|--------|----------|----------|
| CI | 推送/PR到主分支 | 测试、代码检查、安全扫描 |
| Release | 版本标签 | 构建可执行文件、创建发布 |
| Code Quality | 推送/PR/定时 | 代码质量分析、文档检查 |
| Dependencies | 定时/手动 | 依赖更新、安全检查 |

## 详细说明

### 1. CI 工作流 (`ci.yml`)

**触发条件:**
- 推送到 `master`, `main`, `develop` 分支
- 向 `master`, `main` 分支提交 Pull Request

**执行环境:**
- 操作系统: Ubuntu Latest, Windows Latest
- Python 版本: 3.8, 3.9, 3.10, 3.11

**主要步骤:**
1. **环境设置**: 安装 Python 和 uv
2. **依赖安装**: `uv sync --dev`
3. **代码检查**: `ruff check` 和 `ruff format`
4. **单元测试**: `pytest` 运行所有测试
5. **覆盖率报告**: 生成并上传到 Codecov
6. **安全扫描**: safety 和 bandit 安全检查

### 2. 构建和发布工作流 (`release.yml`)

**触发条件:**
- 推送版本标签 (格式: `v*.*.*`)
- 手动触发 (workflow_dispatch)

**构建产物:**
- `VideoClip-Windows.exe` - Windows 可执行文件
- `VideoClip-Linux` - Linux 可执行文件

**发布流程:**
1. 在多平台构建可执行文件
2. 使用 PyInstaller 打包
3. 创建 GitHub Release
4. 上传构建产物

### 3. 代码质量工作流 (`code-quality.yml`)

**触发条件:**
- 推送到主分支
- Pull Request
- 每周日 UTC 00:00 定时运行

**分析内容:**
- **静态分析**: ruff 代码风格检查
- **复杂度分析**: radon 计算代码复杂度
- **安全分析**: bandit 安全漏洞扫描
- **依赖分析**: 生成依赖关系图
- **文档检查**: docstring 覆盖率检查

### 4. 依赖更新工作流 (`dependencies.yml`)

**触发条件:**
- 每周一 UTC 00:00 定时运行
- 手动触发

**功能:**
- 检查依赖更新
- 安全漏洞扫描
- 自动创建更新 PR (计划中)

## 工作流文件结构

```
.github/
├── workflows/
│   ├── ci.yml              # 持续集成
│   ├── release.yml         # 构建发布
│   ├── code-quality.yml    # 代码质量
│   └── dependencies.yml    # 依赖管理
├── ISSUE_TEMPLATE/
│   ├── bug_report.md       # Bug 报告模板
│   ├── feature_request.md  # 功能请求模板
│   └── question.md         # 问题模板
└── pull_request_template.md # PR 模板
```

## 状态徽章

在 README.md 中使用以下徽章显示工作流状态：

```markdown
[![CI](https://github.com/YeRongfeng/VideoClip/workflows/CI/badge.svg)](https://github.com/YeRongfeng/VideoClip/actions/workflows/ci.yml)
[![Code Quality](https://github.com/YeRongfeng/VideoClip/workflows/Code%20Quality/badge.svg)](https://github.com/YeRongfeng/VideoClip/actions/workflows/code-quality.yml)
```

## 开发者指南

### 本地开发

```bash
# 安装开发依赖
uv sync --dev

# 运行代码检查
uv run ruff check .

# 运行测试
uv run pytest

# 格式化代码
uv run ruff format .
```

### 发布流程

1. 更新版本号在 `pyproject.toml`
2. 创建版本标签: `git tag v1.0.0`
3. 推送标签: `git push origin v1.0.0`
4. GitHub Actions 自动构建和发布

### 故障排除

**常见问题:**

1. **测试失败**: 检查本地是否通过 `uv run pytest`
2. **格式检查失败**: 运行 `uv run ruff format .` 修复
3. **依赖问题**: 确保 `uv.lock` 文件是最新的

**调试工作流:**
- 查看 Actions 页面的详细日志
- 检查工作流文件语法
- 验证环境变量和密钥设置

## 贡献

如需修改工作流配置，请：

1. 在本地测试更改
2. 提交 Pull Request
3. 等待 CI 验证通过
4. 合并到主分支

更多信息请参考 [GitHub Actions 文档](https://docs.github.com/en/actions)。
