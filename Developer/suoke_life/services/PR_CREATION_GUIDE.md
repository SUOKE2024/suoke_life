# 索克生活APP PR创建指南

本文档提供了如何从已完成的特性分支创建Pull Request (PR)的说明。

## 创建PR步骤

1. **确保特性分支与远程仓库同步**:
   ```bash
   git checkout feature/your-feature-name
   git push origin feature/your-feature-name
   ```

2. **通过GitHub界面创建PR**:
   - 访问GitHub仓库页面 https://github.com/SUOKE2024/suoke_life
   - 点击"Pull requests"选项卡
   - 点击绿色的"New pull request"按钮
   - 设置"base"为main分支，"compare"为feature/your-feature-name分支
   - 点击"Create pull request"按钮
   - 填写PR标题，如："添加CI/CD自动化部署配置"
   - 添加PR描述，解释实现的功能和更改内容
   - 点击"Create pull request"完成创建

3. **或通过命令行创建PR**:
   ```bash
   # 安装GitHub CLI (如果尚未安装)
   brew install gh
   
   # 登录GitHub CLI
   gh auth login
   
   # 创建PR
   gh pr create --base main --head feature/your-feature-name --title "添加CI/CD自动化部署配置" --body "本PR添加了生产环境CI/CD配置，包括GitHub Actions工作流和Kubernetes部署文件，实现自动化部署到阿里云Kubernetes集群。"
   ```

## PR合并前检查项

确保您的PR包含以下内容并满足以下要求:

1. **必要文件检查**:
   - CI/CD工作流文件 (`.github/workflows/deploy-prod.yml`)
   - Kubernetes部署配置文件 (`services/k8s/`)
   - CI/CD配置指南文档 (`services/CI_CD_GUIDE.md`)

2. **代码质量要求**:
   - 所有CI/CD配置文件使用正确的格式和缩进
   - 环境变量和敏感信息通过密钥引用，而不是硬编码
   - Kubernetes配置遵循最佳实践

3. **安全注意事项**:
   - 确保没有提交任何敏感信息（密码、密钥等）
   - 确保`.env.prod`文件被`.gitignore`排除
   - 确保Kubernetes Secret资源使用安全方式管理

## PR审核和合并

1. **请求审核**:
   - 指派适当的团队成员进行审核
   - 通过GitHub界面的"Reviewers"部分选择审核人员

2. **处理审核反馈**:
   - 针对审核评论进行必要的修改
   - 提交更改到同一分支，PR会自动更新

3. **合并PR**:
   - 当PR获得批准后，点击"Merge pull request"按钮
   - 选择适当的合并方式（通常是"Squash and merge"）
   - 完成合并 