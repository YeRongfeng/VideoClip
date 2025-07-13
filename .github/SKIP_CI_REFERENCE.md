# 🚀 CI/CD 跳过触发快速参考

## 📋 跳过关键字一览

在 git commit 消息中使用以下关键字可以跳过相应的自动化检查：

### 🔄 跳过 CI 测试 (ci.yml)
```bash
[skip ci]        # 跳过 CI 检查
[ci skip]        # 跳过 CI 检查  
[no ci]          # 跳过 CI 检查
[skip actions]   # 跳过 Actions
```

### 🔍 跳过代码质量检查 (code-quality.yml)  
```bash
[skip quality]   # 跳过代码质量检查
[no quality]     # 跳过代码质量检查
[skip lint]      # 跳过 lint 检查
```

### 🚫 跳过所有自动化
```bash
[skip all]       # 跳过所有检查
[no automation]  # 跳过所有自动化
```

## 💡 使用示例

```bash
# 仅文档更新，跳过所有检查
git commit -m "docs: 更新用户手册 [skip all]"

# 临时提交，跳过 CI 测试
git commit -m "wip: 正在开发新功能 [skip ci]"

# 配置文件修改，跳过代码质量检查
git commit -m "config: 调整 ruff 配置 [skip quality]"

# 修复拼写错误，跳过 CI
git commit -m "fix: 修正注释中的拼写错误 [ci skip]"
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
| CI (ci.yml) | ✅ | `[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]` |
| 代码质量 (code-quality.yml) | ✅ | `[skip quality]`, `[no quality]`, `[skip lint]` |
| 依赖更新 (dependencies.yml) | ❌ | 定时任务，无法跳过 |
| 发布 (release.yml) | ❌ | 标签触发，无需跳过 |
| **全局跳过** | ✅ | `[skip all]`, `[no automation]` |
