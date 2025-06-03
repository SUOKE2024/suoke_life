# 索克生活认证服务和用户服务

## 项目概述

本项目包含索克生活（Suoke Life）的核心微服务：认证服务（Auth-Service）和用户服务（User-Service）。这两个服务提供了完整的用户管理、认证授权、健康数据分析和个性化推荐功能。

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ 可用内存
- 10GB+ 可用磁盘空间

### 一键启动

```bash
# 进入服务目录
cd services

# 运行启动脚本
./start_services.sh
```

启动脚本会自动：
- 检查依赖
- 创建必要的目录和配置文件
- 构建Docker镜像
- 启动所有服务
- 等待服务就绪
- 显示访问地址

### 服务访问地址

启动完成后，您可以通过以下地址访问服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| 认证服务 | http://localhost:8001 | 用户认证和授权 |
| 用户服务 | http://localhost:8002 | 用户管理和健康分析 |
| Nginx代理 | http://localhost:80 | 反向代理和负载均衡 |
| Prometheus | http://localhost:9090 | 监控指标收集 |
| Grafana | http://localhost:3000 | 监控仪表板 (admin/admin) |

### API文档

| 服务 | Swagger文档 |
|------|-------------|
| 认证服务 | http://localhost:8001/docs |
| 用户服务 | http://localhost:8002/docs |

## 📋 功能特性

### 认证服务 (Auth-Service)

#### 🔐 核心认证功能
- JWT令牌生成和验证
- 用户注册和登录
- 密码加密和验证
- 会话管理
- 令牌刷新机制
- 多因素认证(MFA)支持

#### 📧 邮件服务集成
- 多邮件提供商支持（SMTP、SendGrid、AWS SES）
- 邮件模板系统（Jinja2）
- 多语言邮件模板
- 邮箱验证流程
- 密码重置邮件
- 欢迎邮件

#### 🔒 安全功能
- 密码强度验证
- 账户锁定机制
- 失败登录尝试跟踪
- IP地址阻止
- 安全审计日志
- 可疑活动监控

### 用户服务 (User-Service)

#### 👥 用户管理
- 用户CRUD操作
- 用户档案管理
- 权限控制
- 用户状态管理
- 批量操作
- 用户搜索和过滤

#### 🏥 健康数据分析
- 心率趋势分析
- 睡眠模式分析
- 活动水平分析
- 体重趋势分析
- 健康洞察生成
- 风险评估

#### 🎯 个性化推荐
- 基于用户画像的推荐
- 健康洞察驱动推荐
- 多维度推荐
- 推荐优先级排序
- 反馈收集

#### ⚡ 性能优化
- 查询优化器
- 连接池管理
- 内存优化
- 批处理器
- 性能监控
- 慢查询检测

## 🏗️ 技术架构

### 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 编程语言 | Python | 3.13.3 |
| Web框架 | FastAPI | 0.104.1 |
| 数据库 | PostgreSQL | 15 |
| 缓存 | Redis | 7 |
| 消息队列 | Redis | 7 |
| 监控 | Prometheus + Grafana | Latest |
| 容器化 | Docker + Docker Compose | Latest |

### 架构设计

```
┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │    Grafana      │
│   (Port 80)     │    │   (Port 3000)   │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Auth Service   │    │  Prometheus     │
│   (Port 8001)   │    │   (Port 9090)   │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  User Service   │    │    Metrics      │
│   (Port 8002)   │    │   Collection    │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │
│   (Port 5432)   │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘
```

## 🔧 配置说明

### 环境变量

#### 认证服务配置

```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Redis配置
REDIS_URL=redis://:password@host:port/db

# JWT配置
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 邮件配置
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### 用户服务配置

```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Redis配置
REDIS_URL=redis://:password@host:port/db

# 认证服务配置
AUTH_SERVICE_URL=http://auth-service:8000
AUTH_SERVICE_TIMEOUT=30

# 性能配置
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
CACHE_TTL=300
```

## 📊 监控和日志

### Prometheus指标

两个服务都导出以下类型的指标：

- **请求指标**: 请求数量、响应时间、错误率
- **业务指标**: 用户注册数、登录成功率、健康数据分析次数
- **系统指标**: CPU使用率、内存使用率、数据库连接数
- **缓存指标**: 缓存命中率、缓存大小、缓存操作次数

### 健康检查

| 端点 | 说明 |
|------|------|
| `/health` | 基本健康检查 |
| `/ready` | 就绪检查（依赖服务状态） |
| `/live` | 存活检查 |

### 日志级别

- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 🧪 测试

### 运行测试

```bash
# 认证服务测试
cd auth-service
python -m pytest tests/ -v --cov=auth_service

# 用户服务测试
cd user-service
python -m pytest tests/ -v --cov=user_service
```

### 测试覆盖率

- 认证服务: 95%+
- 用户服务: 90%+

## 🚀 部署

### 本地开发

```bash
# 启动开发环境
./start_services.sh

# 查看日志
docker-compose -f docker-compose.auth-user-services.yml logs -f

# 停止服务
docker-compose -f docker-compose.auth-user-services.yml down
```

### 生产部署

1. **环境准备**
   ```bash
   # 创建生产环境配置
   cp .env.example .env.production
   # 编辑生产配置
   vim .env.production
   ```

2. **数据库迁移**
   ```bash
   # 运行数据库迁移
   docker exec suoke_auth_service alembic upgrade head
   docker exec suoke_user_service alembic upgrade head
   ```

3. **SSL证书配置**
   ```bash
   # 将SSL证书放置到nginx/ssl目录
   cp your-cert.pem nginx/ssl/
   cp your-key.pem nginx/ssl/
   ```

4. **启动生产服务**
   ```bash
   # 使用生产配置启动
   docker-compose -f docker-compose.auth-user-services.yml --env-file .env.production up -d
   ```

### Kubernetes部署

```bash
# 应用Kubernetes配置
kubectl apply -f k8s/

# 检查部署状态
kubectl get pods -n suoke-life

# 查看服务
kubectl get services -n suoke-life
```

## 🔍 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 检查容器状态
docker-compose -f docker-compose.auth-user-services.yml ps

# 查看容器日志
docker-compose -f docker-compose.auth-user-services.yml logs [service-name]

# 重启服务
docker-compose -f docker-compose.auth-user-services.yml restart [service-name]
```

#### 2. 数据库连接问题

```bash
# 检查数据库状态
docker exec suoke_postgres pg_isready -U suoke_user -d suoke_life

# 查看数据库日志
docker logs suoke_postgres

# 重置数据库
docker-compose -f docker-compose.auth-user-services.yml down -v
docker-compose -f docker-compose.auth-user-services.yml up -d postgres
```

#### 3. Redis连接问题

```bash
# 检查Redis状态
docker exec suoke_redis redis-cli -a redis_password ping

# 查看Redis日志
docker logs suoke_redis

# 清理Redis缓存
docker exec suoke_redis redis-cli -a redis_password FLUSHALL
```

#### 4. 性能问题

```bash
# 查看系统资源使用
docker stats

# 查看慢查询
curl http://localhost:8002/monitoring/performance/slow-queries

# 查看缓存状态
curl http://localhost:8002/monitoring/cache/status
```

### 日志分析

```bash
# 实时查看所有服务日志
docker-compose -f docker-compose.auth-user-services.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.auth-user-services.yml logs -f auth-service

# 查看错误日志
docker-compose -f docker-compose.auth-user-services.yml logs | grep ERROR

# 导出日志到文件
docker-compose -f docker-compose.auth-user-services.yml logs > services.log
```

## 📈 性能优化

### 数据库优化

1. **索引优化**
   - 为常用查询字段创建索引
   - 定期分析查询性能
   - 使用复合索引优化复杂查询

2. **连接池优化**
   - 调整连接池大小
   - 设置合适的超时时间
   - 监控连接使用情况

### 缓存优化

1. **缓存策略**
   - 实施多层缓存
   - 设置合适的TTL
   - 使用缓存预热

2. **缓存监控**
   - 监控缓存命中率
   - 分析缓存使用模式
   - 优化缓存键设计

### 应用优化

1. **代码优化**
   - 使用异步编程
   - 优化数据库查询
   - 减少不必要的计算

2. **资源优化**
   - 调整容器资源限制
   - 优化内存使用
   - 监控CPU使用率

## 🤝 贡献指南

### 开发流程

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

### 代码规范

- 遵循PEP 8代码风格
- 使用类型注解
- 编写完整的文档字符串
- 保持测试覆盖率

### 提交规范

```
type(scope): description

[optional body]

[optional footer]
```

类型：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建过程或辅助工具的变动

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/suoke-life/issues)
- 邮件: support@suokelife.com
- 文档: [项目文档](https://docs.suokelife.com)

---

**索克生活开发团队**  
*让健康管理更智能，让生活更美好* 