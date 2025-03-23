# 索克生活APP

索克生活APP由AI智能体驱动，自主学习、自主进化，自主运营。是一个现代生活（健康养生）管理平台，融合中国传统中医辨证治未病和现代预防医学理念，提供全方位的健康管理服务。

## 项目概述

- **项目名称**：索克生活APP (SUOKE Life)
- **技术栈**：Flutter, Riverpod, Clean Architecture
- **领域**：中国传统中医辨证治未病和现代预防医学
- **AI驱动**：融合多模态AI能力，实现智能健康管理

## 主要功能

- 首页（聊天频道）
- SUOKE（服务频道）
- 探索（搜索频道）
- LIFE（生活频道）
- 个人中心（系统设置）
- TCM特色功能
- 食农结合服务

## 开发环境设置

1. 确保已安装Flutter SDK
2. 克隆仓库
3. 在项目根目录运行 `flutter pub get`
4. 复制 `.env.example` 到 `.env` 并配置相应环境变量
5. 运行 `flutter run` 启动应用

## 项目架构

项目采用Clean Architecture架构模式，使用Riverpod进行状态管理和依赖注入，使用auto_route进行路由管理。

### 目录结构

```
lib/
  - core/：核心功能和工具
  - data/：数据层
  - domain/：领域层
  - presentation/：表现层
  - di/：依赖注入
  - ai_agents/：AI代理相关功能
  - app.dart：应用程序入口
  - main.dart：主函数
```

## 联系方式

如有问题，请联系项目维护团队。

## 项目架构

项目采用前后端分离架构：
- 前端：Flutter跨平台应用，Clean Architecture架构模式
- 后端：Kubernetes微服务架构，包含多个智能体和专业服务

## 环境配置

### 前端开发环境

```bash
flutter pub get
flutter run
```

### 后端开发环境

```bash
# 设置Kubernetes集群
kubectl apply -f scripts/deploy/kubernetes/setup/namespace.yaml
kubectl apply -f scripts/deploy/kubernetes/setup/volumes.yaml
```

## 自定义镜像构建与部署

项目使用阿里云容器镜像服务(ACR)存储自定义镜像，提供优化的运行环境和配置。

### 构建与推送自定义镜像

1. 首先配置`.env`文件中的镜像仓库信息：
```
REGISTRY_URL=your-registry.cr.aliyuncs.com
REGISTRY_NAMESPACE=your-namespace
REGISTRY_USERNAME=your-username
REGISTRY_PASSWORD=your-password
```

2. 执行构建脚本：
```bash
./scripts/build_push_custom_images.sh
```

该脚本会构建以下自定义镜像：
- Redis镜像：优化配置的Redis服务
- MySQL镜像：预配置的MySQL数据库
- MongoDB镜像：针对索克生活应用优化的MongoDB

### 部署自定义镜像到Kubernetes

1. 确保Kubernetes集群配置正确

2. 执行部署脚本：
```bash
./scripts/deploy_custom_images.sh
```

该脚本会：
- 创建必要的Kubernetes Secret用于拉取私有镜像
- 部署Redis、MySQL和MongoDB服务
- 创建应用配置ConfigMap
- 等待所有服务部署完成并检查状态

## 系统组件

### 前端模块
- 首页（聊天频道）
- SUOKE（服务频道）
- 探索（搜索频道）
- LIFE（健康生活方式）
- 我的（个人设置、系统管理员）

### 后端服务
- 健康助手智能体
- 老克智能体
- 知识图谱服务
- 体质辨识服务
- 食疗推荐服务
- 用户认证服务
- 数据同步服务

## API文档

API文档可通过以下方式访问：
```
http://118.31.223.213/api/docs
```

## 贡献指南

请参阅`CONTRIBUTING.md`文件了解如何为项目做出贡献。

## 许可证

该项目采用[MIT许可证](LICENSE)。

## 后端云服务架构

索克生活APP采用了现代云原生架构，前端与后端分离，前端专注于用户体验，后端提供强大的计算能力和业务逻辑。

### 后端服务组成

- **基础设施服务**：Redis、MySQL、MongoDB等，提供数据存储和缓存功能
- **微服务组件**：
  - Laoke Agent服务：核心智能体服务
  - 文件搜索服务：中医知识库检索
  - 网络搜索服务：健康资讯获取
  - API网关：统一的服务入口
  - 智能体协调器：多智能体协作

### 部署指南

完整的后端服务部署指南见：[后端部署指南](scripts/deploy/README.md)

部署主要包括以下步骤：
1. 设置本地开发环境
2. 部署基础设施服务
3. 部署微服务组件
4. 配置API网关 