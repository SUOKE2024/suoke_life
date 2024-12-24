# 贡献指南

## 开发流程

1. Fork 项目仓库
2. 创建特性分支
3. 提交代码修改
4. 创建 Pull Request

## 分支管理

- main: 主分支
- develop: 开发分支
- feature/*: 特性分支
- release/*: 发布分支
- hotfix/*: 紧急修复分支

## 提交规范

### 格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建

### 示例
```
feat(ai): 添加小艾助手功能

- 实现对话功能
- 添加数据分析
- 集成知识库

Closes #123
```

## 代码规范

- 遵循 analysis_options.yaml 配置
- 使用 flutter format 格式化代码
- 编写单元测试
- 添加必要注释

## Pull Request

1. PR 标题清晰描述改动
2. 详细说明修改内容
3. 关联相关 Issue
4. 确保 CI 检查通过
5. 等待代码评审

## 发布流程

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建发布分支
4. 执行测试
5. 合并到 main 分支
6. 创建 Tag 