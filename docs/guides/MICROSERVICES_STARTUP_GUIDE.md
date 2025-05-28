# 索克生活微服务启动指南

## 🚀 快速开始

索克生活项目提供了多种启动方式，您可以根据需要选择合适的启动方案。

### 📋 前置条件

在启动微服务之前，请确保您的系统已安装以下工具：

- **Docker** (>= 20.10)
- **Docker Compose** (>= 2.0)
- **uv** (>= 0.5.0) - Python包管理器
- **Python** (>= 3.11)

### 🎯 启动方案

#### 方案一：快速启动（推荐）

适用于开发和测试环境，启动基础设施和核心服务：

```bash
# 启动所有服务
./scripts/quick_start.sh start

# 查看服务状态
./scripts/quick_start.sh status

# 停止所有服务
./scripts/quick_start.sh stop
```

#### 方案二：完整启动

启动所有微服务，包括智能体服务和诊断服务：

```bash
# 启动所有微服务
python scripts/start_all_services.py

# 仅启动基础设施
python scripts/start_all_services.py --infrastructure-only

# 查看服务状态
python scripts/start_all_services.py --status

# 停止所有服务
python scripts/start_all_services.py --stop
```

#### 方案三：仅基础设施

如果您只需要启动数据库和缓存等基础设施：

```bash
./scripts/quick_start.sh infrastructure
```

## 🏗️ 服务架构

### 基础设施服务

| 服务 | 端口 | 描述 | 访问地址 |
|------|------|------|----------|
| PostgreSQL | 5432 | 主数据库 | localhost:5432 |
| Redis | 6379 | 缓存和消息队列 | localhost:6379 |
| Consul | 8500 | 服务发现 | http://localhost:8500 |
| Prometheus | 9090 | 监控指标 | http://localhost:9090 |
| Grafana | 3000 | 监控仪表板 | http://localhost:3000 |

### 核心微服务

| 服务 | 端口 | 描述 | API文档 |
|------|------|------|---------|
| API网关 | 8080 | 统一入口 | http://localhost:8080/docs |
| 认证服务 | 50052 | 用户认证 | gRPC |
| 用户服务 | 50051 | 用户管理 | gRPC |
| 健康数据服务 | 50056 | 健康数据 | gRPC |
| 医学知识服务 | 8000 | 知识库 | http://localhost:8000/docs |

### 智能体服务

| 智能体 | 端口 | 描述 | 功能 |
|--------|------|------|------|
| 小艾 (XiaoAi) | 50053 | AI助手 | 健康咨询、症状分析 |
| 小克 (XiaoKe) | 50054 | 诊断助手 | 辅助诊断、病历分析 |
| 老克 (LaoKe) | 9000 | 专家系统 | 中医辨证、方案推荐 |
| 索儿 (Soer) | 50060 | 健康管家 | 健康监测、生活建议 |

### 诊断服务

| 服务 | 端口 | 描述 | 诊断类型 |
|------|------|------|----------|
| 问诊服务 | 50052 | 问诊分析 | 症状询问、病史收集 |
| 望诊服务 | 50051 | 视觉诊断 | 面色、舌象分析 |
| 闻诊服务 | 50052 | 听觉诊断 | 声音、气味分析 |
| 切诊服务 | 8000 | 触觉诊断 | 脉象、触诊分析 |

## 🔧 配置说明

### 数据库配置

默认数据库连接信息：
- **主机**: localhost
- **端口**: 5432
- **用户名**: suoke
- **密码**: suoke123
- **数据库**: 各服务独立数据库

### Redis配置

默认Redis连接信息：
- **主机**: localhost
- **端口**: 6379
- **密码**: suoke123

### 环境变量

您可以通过环境变量自定义配置：

```bash
# 数据库配置
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=suoke
export DB_PASSWORD=suoke123

# Redis配置
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=suoke123

# 服务配置
export LOG_LEVEL=INFO
export ENVIRONMENT=development
```

## 📊 监控和日志

### 监控仪表板

- **Grafana**: http://localhost:3000
  - 用户名: admin
  - 密码: suoke123

- **Prometheus**: http://localhost:9090
  - 指标收集和查询

### 日志查看

#### 基础设施日志
```bash
# 查看所有基础设施日志
docker-compose -f deploy/docker/docker-compose.yml logs -f

# 查看特定服务日志
docker-compose -f deploy/docker/docker-compose.yml logs -f postgres
docker-compose -f deploy/docker/docker-compose.yml logs -f redis
```

#### 应用服务日志
```bash
# 查看服务日志文件
tail -f services/auth-service/logs/auth-service.log
tail -f services/api-gateway/logs/api-gateway.log
tail -f services/med-knowledge/logs/med-knowledge.log
```

## 🛠️ 开发指南

### 添加新服务

1. 在 `services/` 目录下创建新服务
2. 确保服务有 `pyproject.toml` 配置文件
3. 在启动脚本中添加服务配置
4. 更新监控配置

### 服务间通信

- **gRPC**: 用于服务间高性能通信
- **HTTP/REST**: 用于外部API和Web界面
- **消息队列**: 使用Redis进行异步通信

### 健康检查

所有服务都应实现健康检查端点：
- **HTTP服务**: `/health`
- **gRPC服务**: 实现Health Check协议

## 🚨 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
lsof -i :5432
lsof -i :6379
lsof -i :8080

# 停止冲突的服务
./scripts/quick_start.sh stop
```

#### 2. Docker容器启动失败
```bash
# 查看容器状态
docker ps -a

# 查看容器日志
docker logs suoke-postgres
docker logs suoke-redis

# 重启容器
docker-compose -f deploy/docker/docker-compose.yml restart
```

#### 3. 服务启动失败
```bash
# 检查服务依赖
./scripts/quick_start.sh status

# 查看服务日志
tail -f services/*/logs/*.log

# 重启特定服务
cd services/auth-service
uv run python -m cmd.server
```

#### 4. 数据库连接失败
```bash
# 测试数据库连接
docker exec -it suoke-postgres psql -U suoke -d suoke_life

# 重置数据库
docker-compose -f deploy/docker/docker-compose.yml down -v
./scripts/quick_start.sh start
```

### 性能优化

#### 1. 内存使用优化
- 调整Docker容器内存限制
- 优化Python服务内存使用
- 使用连接池减少数据库连接

#### 2. 启动速度优化
- 使用uv加速包安装
- 并行启动非依赖服务
- 预热缓存和连接池

## 📚 相关文档

- [项目架构文档](./README.md)
- [API文档](./docs/api/)
- [部署指南](./deploy/README.md)
- [开发指南](./docs/development/)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📞 支持

如果您遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目Issues
3. 创建新的Issue描述问题

---

**索克生活团队** - 致力于AI驱动的健康管理平台 🏥🤖 