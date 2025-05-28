# GitHub 仓库访问权限修改指南

本指南将帮助您将 GitHub 仓库的访问权限修改为邀请制（私有仓库）。

## 目录

- [概述](#概述)
- [前提条件](#前提条件)
- [方法一：手动操作](#方法一手动操作)
- [方法二：使用自动化脚本](#方法二使用自动化脚本)
- [权限级别说明](#权限级别说明)
- [注意事项](#注意事项)
- [常见问题](#常见问题)

## 概述

将仓库设置为私有（邀请制）可以：
- 限制仓库访问权限，只有被邀请的用户才能查看和操作
- 保护敏感代码和数据
- 更好地控制团队协作权限
- 符合企业级项目的安全要求

## 前提条件

1. **管理员权限**：您必须是仓库的所有者或具有管理员权限
2. **GitHub 账户**：确保您有有效的 GitHub 账户
3. **Personal Access Token**（仅脚本方式需要）：用于 API 认证

### 创建 Personal Access Token

1. 登录 GitHub，进入 Settings > Developer settings > Personal access tokens
2. 点击 "Generate new token (classic)"
3. 设置 Token 名称和过期时间
4. 选择以下权限：
   - `repo` - 完整的仓库访问权限
   - `admin:org` - 组织管理权限（如果是组织仓库）
5. 点击 "Generate token" 并保存 Token

## 方法一：手动操作

### 步骤 1：进入仓库设置

1. 访问您的仓库页面：`https://github.com/SUOKE2024/suoke_life`
2. 点击右上角的 **Settings** 选项卡
3. 确保您在 **General** 设置页面

### 步骤 2：修改仓库可见性

1. 滚动到页面底部的 **Danger Zone** 区域
2. 找到 **Change repository visibility** 选项
3. 点击 **Change visibility** 按钮
4. 选择 **Make private** 选项
5. 输入仓库名称 `suoke_life` 确认操作
6. 点击 **I understand, change repository visibility** 按钮

### 步骤 3：邀请协作者

1. 在左侧菜单中点击 **Manage access**
2. 点击 **Invite a collaborator** 按钮
3. 输入要邀请的用户名或邮箱地址
4. 选择适当的权限级别：
   - **Read**：只读权限
   - **Write**：读写权限
   - **Admin**：管理员权限
5. 点击 **Add [username] to this repository** 发送邀请

## 方法二：使用自动化脚本

我们提供了一个自动化脚本来批量修改仓库权限。

### 安装依赖

```bash
# 安装 Octokit（GitHub API 客户端）
npm install @octokit/rest
```

### 运行脚本

```bash
# 进入项目根目录
cd /Users/songxu/Developer/suoke_life

# 运行脚本
node scripts/update-repo-visibility.js
```

### 脚本使用流程

1. **输入 GitHub Token**：脚本会要求您输入 Personal Access Token
2. **确认操作**：脚本会显示要修改的仓库列表，需要您确认
3. **修改可见性**：脚本会自动将仓库设置为私有
4. **邀请协作者**：可选择邀请协作者并设置权限级别

### 脚本功能

- ✅ 批量修改多个仓库的可见性
- ✅ 自动邀请协作者
- ✅ 权限级别配置
- ✅ 错误处理和重试机制
- ✅ 操作确认和安全检查

## 权限级别说明

| 权限级别 | 描述 | 可执行操作 |
|---------|------|-----------|
| **Read** | 只读权限 | 查看代码、下载、克隆仓库 |
| **Write** | 读写权限 | 推送代码、创建分支、提交 PR |
| **Admin** | 管理员权限 | 所有操作，包括仓库设置、删除仓库 |

## 注意事项

### 🚨 重要提醒

1. **备份数据**：修改前请确保重要数据已备份
2. **CI/CD 配置**：私有仓库可能需要重新配置 CI/CD 访问权限
3. **依赖项目**：检查是否有其他项目依赖此仓库
4. **团队通知**：提前通知团队成员仓库访问权限的变更

### 🔧 技术影响

1. **GitHub Actions**：
   - 私有仓库的 Actions 分钟数有限制
   - 可能需要更新 workflow 中的权限设置

2. **外部集成**：
   - 第三方服务可能需要重新授权
   - Webhook 和 API 访问需要更新

3. **克隆和访问**：
   - 需要使用 Personal Access Token 或 SSH 密钥
   - 匿名访问将被禁止

## 常见问题

### Q: 修改为私有仓库后，原来的公开链接还能访问吗？

A: 不能。仓库变为私有后，只有被邀请的协作者才能访问。

### Q: 如何撤销对某个用户的邀请？

A: 在仓库的 Settings > Manage access 中，找到对应用户，点击 "Remove" 按钮。

### Q: 私有仓库是否影响 GitHub Pages？

A: 是的。私有仓库的 GitHub Pages 只有协作者才能访问，除非您有 GitHub Pro 或更高级别的账户。

### Q: 如何重新将仓库设置为公开？

A: 在仓库设置的 Danger Zone 中，选择 "Change visibility" > "Make public"。

### Q: 脚本执行失败怎么办？

A: 检查以下几点：
- Personal Access Token 是否有效且权限充足
- 网络连接是否正常
- 仓库名称是否正确
- 是否有足够的仓库管理权限

## 相关资源

- [GitHub 官方文档 - 仓库可见性](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [GitHub API 文档](https://docs.github.com/en/rest/repos/repos#update-a-repository)
- [Personal Access Token 管理](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## 支持

如果您在操作过程中遇到问题，请：

1. 查看本文档的常见问题部分
2. 检查 GitHub 官方文档
3. 在项目中创建 Issue 寻求帮助
4. 联系项目维护者

---

**最后更新时间**：2025-05-27 15:51:51  
**文档版本**：v1.0.0 