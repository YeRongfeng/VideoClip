# 🚀 CI/CD 跳过触发快速参考

## 📋 跳过关键字一览

在 git commit 消息中使用以下关键字可以跳过相应的自动化检查：

### 🔄 跳过 CI 测试 (ci.yml)
```bash
[skip test]      # 跳过 CI 测试
[no test]        # 跳过 CI 测试  
[skip testing]   # 跳过 CI 测试
```
**注意**: 
- 这些关键字只会跳过CI测试，不会影响代码质量检查
- 不使用 `[skip ci]` 是因为它是GitHub内置关键字，会跳过所有工作流

### 🔍 跳过代码质量检查 (code-quality.yml)  
```bash
[skip quality]   # 跳过代码质量检查
[no quality]     # 跳过代码质量检查
[skip lint]      # 跳过 lint 检查
```
**注意**: 这些关键字只会跳过代码质量检查，不会影响CI测试

### 🚫 跳过所有自动化
```bash
[skip all]       # 跳过所有检查
[no automation]  # 跳过所有自动化
```

## 💡 使用示例

```bash
# 仅文档更新，跳过所有检查
git commit -m "docs: 更新用户手册 [skip all]"

# 临时提交，只跳过 CI 测试（代码质量检查仍会运行）
git commit -m "wip: 正在开发新功能 [skip test]"

# 配置文件修改，只跳过代码质量检查（CI测试仍会运行）
git commit -m "config: 调整 ruff 配置 [skip quality]"

# 修复拼写错误，只跳过 CI 测试
git commit -m "fix: 修正注释中的拼写错误 [no test]"

# 格式调整，只跳过代码质量检查
git commit -m "style: 调整代码格式 [skip lint]"
```

## ⚠️ 注意事项

1. **关键字必须在提交消息中**: 关键字需要出现在 `git commit -m` 的消息中
2. **大小写敏感**: 请使用小写字母，如 `[skip ci]` 而不是 `[SKIP CI]`
3. **方括号必需**: 必须使用方括号包围关键字
4. **最终检查**: 确保最终合并的代码通过所有质量检查
5. **定时任务不受影响**: 定时运行的检查（如依赖更新）不会被跳过

## 🎯 适用场景

- **文档更新**: README、注释、用户手册等
- **配置修改**: .gitignore、工作流配置等  
- **临时提交**: 开发过程中的中间状态
- **格式调整**: 仅调整代码格式、空格等
- **紧急修复**: 需要快速部署的关键问题

## 🔧 工作流状态

| 工作流 | 支持跳过 | 跳过关键字 |
|--------|---------|-----------|
| CI (ci.yml) | ✅ | `[skip test]`, `[no test]`, `[skip testing]` |
| 代码质量 (code-quality.yml) | ✅ | `[skip quality]`, `[no quality]`, `[skip lint]` |
| 依赖更新 (dependencies.yml) | ❌ | 定时任务，无法跳过 |
| 发布 (release.yml) | ❌ | 标签触发，无需跳过 |
| **全局跳过** | ✅ | `[skip all]`, `[no automation]` |

## ⚠️ 重要说明

**GitHub 内置跳过关键字**:
- `[skip ci]`, `[ci skip]` 等是 GitHub Actions 的内置关键字
- 这些关键字会跳过 **所有工作流**，无法精确控制
- 因此我们使用自定义关键字来实现精确的跳过控制
