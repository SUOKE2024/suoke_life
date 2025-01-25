# 索克生活项目文档

## 项目概述

索克生活是一个基于 Flutter 开发的智能生活助手应用,集成了多种 AI 助手服务,帮助用户管理日常生活、健康和工作。

## 目录结构

```
suoke_life/
├── lib/                # 源代码目录
│   ├── app/           # 应用主目录
│   │   ├── bindings/  # 依赖注入绑定
│   │   ├── core/      # 核心功能
│   │   ├── data/      # 数据层
│   │   ├── modules/   # 功能模块
│   │   ├── routes/    # 路由配置
│   │   └── services/  # 服务层
├── test/              # 测试代码
├── docs/              # 项目文档
│   ├── api/           # API 文档
│   ├── database/      # 数据库设计
│   ├── deployment/    # 部署指南
│   ├── security/      # 安全规范
│   └── ui/            # UI 设计规范
├── assets/            # 资源文件
└── scripts/           # 工具脚本
```

## 技术栈

- Flutter 3.0+
- GetX 状态管理
- SQLite 本地数据库
- 豆包 AI SDK
- 阿里云 OSS

## 核心功能

### AI 助手服务
- 小艾: 生活管家(128K 模型)
- 老克: 知识助手(Embedding 模型)  
- 小克: 商业助手(32K 模型)

### 健康管理
- 健康数据记录
- 体质评估
- 健康建议

### 生活记录
- 日记
- 待办事项
- 备忘录

### 社交功能
- 好友系统
- 群组
- 动态分享

## 文档索引

- [API 文档](api/README.md) - API 接口说明
- [数据库设计](database/schema.md) - 数据库表结构设计
- [部署指南](deployment/README.md) - 环境配置与部署流程
- [安全规范](security/README.md) - 安全策略与最佳实践
- [UI 设计规范](ui/README.md) - UI 设计标准与组件库

## 开发规范

### 代码风格
- 遵循 [analysis_options.yaml](../analysis_options.yaml) 配置
- 使用 `flutter format` 格式化代码
- 类型安全,避免 dynamic

### Git 工作流
- 主分支: main
- 开发分支: develop
- 功能分支: feature/*
- 发布分支: release/*
- 修复分支: hotfix/*

### 提交规范
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建

## 环境配置

### 开发环境
- Flutter SDK: 3.0.0+
- Dart SDK: 3.0.0+
- Android Studio / VS Code
- Git

### 运行环境
- iOS 12.0+
- Android 5.0+
- 内存 2GB+
- 存储空间 100MB+

## 相关资源

- [项目仓库](https://github.com/suoke2024/suoke-life)
- [接口文档](https://api.suoke.life/docs)
- [设计稿](https://www.figma.com/file/xxx/suoke-life)
- [产品原型](https://www.axure.com/xxx)

## 联系方式

- 技术支持: support@suoke.life
- 商务合作: bd@suoke.life
- 官方网站: https://www.suoke.life 