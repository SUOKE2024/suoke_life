# 索克生活微服务架构

本目录包含索克生活APP的后端微服务架构实现。

## 服务概述

### 核心服务
- **API网关服务 (api-gateway)**: 所有服务的统一入口点，负责请求路由和转发
- **认证服务 (auth-service)**: 处理用户认证、授权和token管理
- **用户服务 (user-service)**: 管理用户资料和用户数据

### 中医特色服务
- **四诊协调服务 (four-diagnosis-coordinator)**: 协调四诊法数据收集和分析
- **望诊服务 (looking-diagnosis-service)**: 处理望诊相关功能
- **闻诊服务 (smell-diagnosis-service)**: 处理闻诊相关功能
- **问诊服务 (inquiry-diagnosis-service)**: 处理问诊相关功能
- **切诊服务 (touch-diagnosis-service)**: 处理切诊相关功能

### 知识管理服务
- **知识库服务 (knowledge-base-service)**: 管理结构化知识内容
- **知识图谱服务 (knowledge-graph-service)**: 构建和查询中医知识图谱
- **RAG服务 (rag-service)**: 实现检索增强生成功能

### AI智能体服务
- **智能体协调服务 (agent-coordinator-service)**: 协调多个AI智能体的工作
- **小爱服务 (xiaoai-service)**: AI助手智能体实现
- **小柯服务 (xiaoke-service)**: 中医专家智能体实现
- **老柯服务 (laoke-service)**: 老中医专家智能体实现

### 特色应用服务
- **索耳服务 (soer-service)**: 声音诊断智能体实现
- **玉米迷宫服务 (corn-maze-service)**: AR玉米迷宫游戏服务

## 技术架构

### 开发语言和框架
- **Go**: 用于API网关、认证服务和用户服务
- **Python**: 用于AI服务和知识管理服务
- **Node.js**: 用于部分工具和辅助服务

### 数据存储
- **MySQL**: 关系型数据库，存储用户数据和结构化信息
- **Redis**: 缓存和会话存储
- **Vector DB**: 向量数据库，用于知识检索

### 通信
- **REST API**: 服务间同步通信
- **gRPC**: 高性能服务间通信
- **消息队列**: 异步通信和事件驱动架构

## 快速开始

### 系统要求
- Docker 20.10+
- Docker Compose 2.0+
- Go 1.21+
- MySQL 8.0+
- Redis 6.2+

### 本地开发环境设置

1. 克隆仓库
```bash
git clone https://github.com/your-org/suoke_life.git
cd suoke_life/services
```

2. 启动所有服务
```bash
docker-compose up -d
```

3. 运行集成测试
```bash
./tests/integration_test.sh
```

4. 单独构建和运行特定服务
```bash
# 构建特定服务
cd api-gateway
docker build -t suoke-api-gateway .

# 运行特定服务
docker run -p 8080:8080 -e CONFIG_PATH=/app/configs/config.json suoke-api-gateway
```

### 部署

使用部署脚本可以轻松部署服务：

```bash
# 部署所有服务到开发环境
./deploy.sh --env dev --service all

# 仅构建但不部署
./deploy.sh --build true --deploy false

# 部署特定服务到生产环境
./deploy.sh --env prod --service auth-service --push true
```

## 项目结构

每个服务遵循类似的项目结构：

```
service-name/
├── cmd/                    # 主应用程序入口点
│   └── main.go            # 主函数
├── internal/               # 私有应用和库代码
│   ├── config/            # 配置管理
│   ├── controllers/       # 控制器/处理器
│   ├── database/          # 数据库访问和迁移
│   ├── middleware/        # HTTP中间件
│   ├── models/            # 数据模型
│   ├── repository/        # 数据存储库实现
│   ├── server/            # HTTP服务器
│   └── services/          # 业务逻辑
├── configs/                # 配置文件
├── Dockerfile              # Docker构建文件
└── go.mod                  # Go模块定义
```

## 贡献指南

### 代码风格
- Go代码必须通过`gofmt`和`golint`
- 提交前运行单元测试和集成测试
- 遵循仓库中的代码风格和最佳实践

### 工作流程
1. 为新功能或修复创建分支
2. 实现更改并添加测试
3. 提交Pull Request进行代码审查
4. 合并至主分支

## 许可证

版权所有 © 2023-2024 索克生活 