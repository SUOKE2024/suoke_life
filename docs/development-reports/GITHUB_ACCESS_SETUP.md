# GitHub 仓库访问权限设置

## 快速开始

将您的 GitHub 仓库设置为邀请制访问（私有仓库），只需运行一个命令：

```bash
npm run github:setup-access
```

这个命令会：
1. ✅ 检查必要的依赖环境
2. ✅ 安装 GitHub API 客户端
3. ✅ 引导您创建 Personal Access Token
4. ✅ 将仓库设置为私有
5. ✅ 可选择邀请协作者

## 手动操作

如果您更喜欢手动操作，请参考详细指南：

📖 **[完整操作指南](docs/GITHUB_REPOSITORY_ACCESS_GUIDE.md)**

## 其他命令

```bash
# 仅安装 GitHub API 依赖
npm run github:setup

# 仅运行权限修改脚本（需要先设置 GITHUB_TOKEN）
npm run github:update-visibility
```

## 需要帮助？

- 查看 [详细文档](docs/GITHUB_REPOSITORY_ACCESS_GUIDE.md)
- 检查 [常见问题](docs/GITHUB_REPOSITORY_ACCESS_GUIDE.md#常见问题)
- 在项目中创建 Issue

---

**注意**：修改仓库为私有后，只有被邀请的协作者才能访问。请确保提前通知团队成员。 