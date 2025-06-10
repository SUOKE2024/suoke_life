# Claude GitHub 应用安装指南

## 📋 概述

本指南将帮助您在 `SUOKE2024/suoke_life` 仓库中安装和配置 Claude GitHub 应用，以实现 AI 辅助代码审查、自动化开发和智能协作。

## 🚀 安装步骤

### 步骤 1：访问 GitHub 仓库设置

1. 打开浏览器，访问：https://github.com/SUOKE2024/suoke_life
2. 点击仓库页面右上角的 **Settings** 标签
3. 在左侧菜单中找到 **Integrations** 部分

### 步骤 2：安装 GitHub Apps

1. 在 Settings 页面左侧菜单中，点击 **Integrations** → **GitHub Apps**
2. 点击 **Browse GitHub Marketplace** 按钮
3. 在搜索框中输入 "Claude" 或 "Anthropic"
4. 找到 Claude 的官方应用并点击

### 步骤 3：配置 Claude 应用

1. 点击 **Install** 或 **Set up a plan**
2. 选择安装范围：
   - **Only select repositories**: 选择 `SUOKE2024/suoke_life`
   - 或 **All repositories**: 如果您想在所有仓库中使用
3. 点击 **Install** 确认安装

### 步骤 4：配置权限

Claude 应用通常需要以下权限：
- ✅ **Read access to code**
- ✅ **Read and write access to pull requests**
- ✅ **Read and write access to issues**
- ✅ **Read access to repository metadata**

## 🔧 配置 Claude 集成

### 创建 Claude 配置文件

在项目根目录创建 `.claude.yml` 配置文件：

```yaml
# Claude AI 配置
version: "1.0"

# 项目信息
project:
  name: "索克生活平台"
  description: "智能健康管理平台"
  language: ["TypeScript", "Python", "React Native"]

# AI 辅助功能
features:
  code_review: true
  auto_documentation: true
  bug_detection: true
  performance_optimization: true
  security_analysis: true

# 代码审查规则
code_review:
  auto_approve_minor: false
  require_human_review: true
  focus_areas:
    - "安全性检查"
    - "性能优化"
    - "代码质量"
    - "最佳实践"

# 文档生成
documentation:
  auto_generate: true
  languages: ["zh-CN", "en-US"]
  include_api_docs: true
  include_architecture_docs: true
```

### 配置 GitHub Actions 工作流

创建 Claude 集成的 GitHub Actions 工作流：

```yaml
# .github/workflows/claude-integration.yml
name: Claude AI Integration

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main, develop]

jobs:
  claude-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Claude Code Review
        uses: anthropic/claude-github-action@v1
        with:
          api-key: ${{ secrets.CLAUDE_API_KEY }}
          review-type: "comprehensive"
          focus: "security,performance,quality"

      - name: Generate Documentation
        uses: anthropic/claude-docs-action@v1
        with:
          api-key: ${{ secrets.CLAUDE_API_KEY }}
          output-path: "./docs/ai-generated/"
```

## 🔐 安全配置

### 设置 API 密钥

1. 在 GitHub 仓库中，转到 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下密钥：
   - `CLAUDE_API_KEY`: 您的 Claude API 密钥
   - `ANTHROPIC_API_KEY`: Anthropic API 密钥（如果需要）

### 配置环境变量

```bash
# 在 .env 文件中添加
CLAUDE_API_KEY=your_claude_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-sonnet-20240229
```

## 🎯 使用场景

### 1. 自动代码审查

Claude 将自动审查每个 Pull Request，提供：
- 代码质量建议
- 安全漏洞检测
- 性能优化建议
- 最佳实践推荐

### 2. 智能文档生成

- 自动生成 API 文档
- 更新架构文档
- 生成用户指南
- 创建开发者文档

### 3. Bug 检测和修复

- 自动检测潜在 bug
- 提供修复建议
- 生成测试用例
- 代码重构建议

### 4. 性能优化

- 分析性能瓶颈
- 提供优化建议
- 监控代码复杂度
- 建议架构改进

## 📊 监控和分析

### Claude 使用统计

在 GitHub Insights 中查看：
- Claude 审查的 PR 数量
- 发现的问题数量
- 修复建议的采纳率
- 代码质量改进趋势

### 集成健康检查

```bash
# 检查 Claude 集成状态
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/SUOKE2024/suoke_life/installations

# 验证 API 连接
curl -H "Authorization: Bearer $CLAUDE_API_KEY" \
     https://api.anthropic.com/v1/models
```

## 🔧 故障排除

### 常见问题

1. **Claude 应用未响应**
   - 检查 API 密钥是否正确
   - 验证网络连接
   - 查看 GitHub Actions 日志

2. **权限不足**
   - 确认应用权限设置
   - 检查仓库访问权限
   - 验证 API 密钥权限

3. **配置错误**
   - 检查 `.claude.yml` 语法
   - 验证工作流配置
   - 查看错误日志

### 支持联系

- **技术支持**: tech@suoke.life
- **GitHub Issues**: https://github.com/SUOKE2024/suoke_life/issues
- **Claude 官方支持**: https://support.anthropic.com

## 📈 最佳实践

1. **定期更新配置**
   - 保持 Claude 应用最新版本
   - 更新 API 密钥
   - 优化配置参数

2. **监控使用情况**
   - 跟踪 API 使用量
   - 分析审查质量
   - 收集团队反馈

3. **安全考虑**
   - 定期轮换 API 密钥
   - 限制应用权限
   - 监控异常活动

---

**安装完成后，Claude 将开始为您的索克生活项目提供智能 AI 辅助！** 🤖✨ 