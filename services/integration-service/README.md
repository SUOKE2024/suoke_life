# Integration Service

第三方平台集成服务 - 索克生活健康管理平台的核心微服务

## 概述

Integration Service 负责管理与第三方健康平台的集成，包括OAuth认证、数据同步、API适配等功能。

## 支持的平台

- Apple Health - iOS健康应用数据
- Google Fit - Google健康数据平台  
- Fitbit - Fitbit设备和应用数据
- 小米运动 - 小米生态健康数据
- 华为运动健康 - 华为生态健康数据
- 微信运动 - 微信运动步数数据
- 支付宝运动 - 支付宝运动数据

## 核心功能

### 1. 平台集成管理
- 创建、更新、删除第三方平台集成
- 管理集成状态和配置
- 支持批量操作

### 2. OAuth认证
- 标准OAuth 2.0流程
- 访问令牌管理和自动刷新
- 权限范围控制

### 3. 数据同步
- 自动定时同步
- 手动触发同步
- 增量数据更新
- 同步状态监控

## 技术架构

### 技术栈
- Python 3.11+
- FastAPI - Web框架
- SQLAlchemy - ORM
- PostgreSQL - 主数据库
- Redis - 缓存和会话存储
- Pydantic - 数据验证

### 架构模式
- 分层架构: API层 → Service层 → Repository层 → Model层
- 适配器模式: 统一的平台适配器接口
- 依赖注入: FastAPI依赖管理
- 异步编程: 全异步架构

## 快速开始

### 1. 安装依赖

```bash
cd services/integration-service
pip install -r requirements.txt
```

### 2. 启动服务

使用快速启动脚本：

```bash
python scripts/quick_start.py
```

### 3. 验证服务

访问健康检查：

```bash
curl http://localhost:8003/api/v1/health
```

查看API文档：

```
http://localhost:8003/docs
```

## API端点

### 健康检查
- GET /api/v1/health - 服务健康状态
- GET /api/v1/health/ready - 服务就绪状态

### 平台认证
- GET /api/v1/auth/platforms - 获取支持的平台列表
- GET /api/v1/auth/{platform}/url - 获取授权URL
- GET /api/v1/auth/{platform}/callback - 处理认证回调

### 集成管理
- GET /api/v1/integrations - 获取用户集成列表
- POST /api/v1/integrations - 创建新集成
- GET /api/v1/integrations/{id} - 获取集成详情
- PUT /api/v1/integrations/{id} - 更新集成配置
- DELETE /api/v1/integrations/{id} - 删除集成

## 项目结构

```
integration-service/
├── api/rest/              # REST API路由
├── cmd/server/            # 应用入口
├── config/                # 配置文件
├── internal/              # 内部模块
│   ├── adapters/          # 平台适配器
│   ├── model/             # 数据模型
│   ├── repository/        # 数据访问层
│   └── service/           # 业务逻辑层
├── scripts/               # 脚本
├── test/                  # 测试
└── requirements.txt       # Python依赖
```

## 开发状态

✅ 已完成：
- 基础架构搭建
- 数据模型定义
- 平台适配器框架
- API路由设计
- 依赖注入系统
- 健康检查功能

🚧 进行中：
- 数据库集成
- Redis缓存
- 完整的OAuth流程
- 数据同步功能

📋 待完成：
- 单元测试
- 集成测试
- 性能优化
- 监控和日志
- 部署配置 