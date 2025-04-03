# 索克生活 - 用户服务

## 项目概述

用户服务是索克生活APP的核心微服务之一，负责用户身份认证、个人信息管理、权限控制等功能。该服务采用Node.js开发，基于Express框架，以RESTful API的形式提供服务。

### 核心功能

- 用户注册与登录
- 用户资料管理
- JWT身份认证
- 权限控制
- 用户健康数据关联
- 第三方平台登录集成

## 目录结构

```
/services/user-service/
├── src/                    # 源代码目录
│   ├── controllers/        # 控制器
│   ├── middleware/         # 中间件
│   ├── models/             # 数据模型
│   ├── routes/             # 路由定义
│   ├── services/           # 业务逻辑服务
│   ├── utils/              # 工具函数
│   ├── config/             # 配置文件
│   └── server.js           # 服务入口
├── mock/                   # 模拟数据
├── tests/                  # 测试文件
├── k8s/                    # Kubernetes配置文件
│   ├── configmap.yaml      # 配置映射
│   ├── deployment.yaml     # 部署配置
│   ├── secret.yaml         # 密钥配置
│   ├── pv.yaml             # 持久卷配置
│   └── service.yaml        # 服务配置
├── Dockerfile              # 构建镜像配置
├── Dockerfile.multiarch    # 多架构镜像构建配置
├── package.json            # 依赖管理
├── mock-server.js          # 模拟服务器
├── DEPLOYMENT_GUIDE.md     # 部署指南
└── README.md               # 说明文档
```

## API接口文档

### 认证相关接口

#### 用户注册

- **URL**: `/auth/register`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "user": {
      "id": "string",
      "username": "string"
    },
    "token": "string"
  }
  ```

#### 用户登录

- **URL**: `/auth/login`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "user": {
      "id": "string",
      "username": "string"
    },
    "token": "string",
    "expires": "number"
  }
  ```

#### 刷新Token

- **URL**: `/auth/refresh-token`
- **方法**: `POST`
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "success": true,
    "token": "string",
    "expires": "number"
  }
  ```

### 用户资料接口

#### 获取用户资料

- **URL**: `/users/profile`
- **方法**: `GET`
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "success": true,
    "profile": {
      "id": "string",
      "username": "string",
      "email": "string",
      "avatar": "string",
      "preferences": "object",
      "createdAt": "string",
      "updatedAt": "string"
    }
  }
  ```

#### 更新用户资料

- **URL**: `/users/profile`
- **方法**: `PUT`
- **请求头**: `Authorization: Bearer {token}`
- **请求体**:
  ```json
  {
    "username": "string",
    "avatar": "string",
    "preferences": "object"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "profile": {
      "id": "string",
      "username": "string",
      "email": "string",
      "avatar": "string",
      "preferences": "object",
      "updatedAt": "string"
    }
  }
  ```

#### 上传头像

- **URL**: `/users/avatar`
- **方法**: `POST`
- **请求头**: `Authorization: Bearer {token}`
- **请求体**: `multipart/form-data`
- **响应**:
  ```json
  {
    "success": true,
    "avatar": "string"
  }
  ```

### 健康检查接口

- **URL**: `/health`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "status": "up",
    "version": "string",
    "uptime": "number"
  }
  ```

## 部署指南

用户服务支持多种部署方式，包括Docker容器、Kubernetes集群等。详细部署指南请参考[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)。

### 快速开始

#### 本地开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 启动模拟服务器
node mock-server.js
```

#### Docker部署

```bash
# 构建Docker镜像
docker build -t suoke/user-service:latest .

# 运行容器
docker run -d -p 3002:3002 \
  -e NODE_ENV=production \
  -e DB_HOST=db.example.com \
  -e JWT_SECRET=your_jwt_secret \
  suoke/user-service:latest
```

#### Kubernetes部署

```bash
# 部署配置
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pv.yaml
kubectl apply -f k8s/deployment.yaml

# 查看部署状态
kubectl get pods -n suoke
```

## 开发指南

### 环境要求

- Node.js 18+
- npm 8+
- Docker (用于容器化部署)
- Kubernetes (用于集群部署)

### 代码规范

项目遵循ES6+标准，使用ESLint进行代码风格检查。提交代码前请确保通过以下检查:

```bash
# 代码风格检查
npm run lint

# 运行测试
npm test
```

### 添加新路由

1. 在`src/routes`目录下创建路由文件
2. 在`src/controllers`目录下实现相应控制器
3. 在`src/server.js`中注册路由

### 数据库集成

用户服务使用MySQL数据库存储用户数据，使用Sequelize作为ORM工具。数据库连接配置位于`src/config/database.js`。

## 维护与监控

### 日志管理

服务使用Winston记录日志，日志级别可通过环境变量`LOGGING_LEVEL`配置。在生产环境中，日志将输出到标准输出，便于容器化环境收集。

### 健康检查

服务提供`/health`端点用于监控系统状态。可以通过Kubernetes的存活探针和就绪探针配置来自动化监控服务健康状态。

### 性能监控

服务集成了基础的性能指标收集功能，可以通过Prometheus进行监控。相关端点为`/metrics`。

## 贡献指南

欢迎为用户服务提交Pull Request。在提交前，请确保以下几点:

1. 所有测试通过
2. 代码符合项目风格要求
3. 提交消息清晰明了
4. 更新相关文档

## 版本历史

- v0.1.0 - 初始版本，提供基础用户认证功能
- v0.2.0 - 添加用户资料管理功能
- v0.3.0 - 集成第三方登录功能
- v0.4.0 - 添加权限控制功能
- v0.5.0 - 优化容器化部署配置
- v0.6.0 - 当前版本，集成Kubernetes部署支持