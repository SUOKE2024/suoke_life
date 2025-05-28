# 索克生活认证服务 (Suoke Life Auth Service)

索克生活认证服务是一个现代化的微服务，为索克生活健康管理平台提供用户认证、授权和账户管理功能。

## 🌟 特性

### 核心功能
- **用户认证**: 支持用户名/邮箱/手机号登录
- **多因素认证 (MFA)**: TOTP、SMS、邮箱验证
- **OAuth集成**: 支持Google、微信等第三方登录
- **会话管理**: 安全的会话令牌和刷新机制
- **权限控制**: 基于角色的访问控制 (RBAC)
- **账户安全**: 密码策略、登录限制、账户锁定

### 技术特性
- **现代Python**: 基于Python 3.13.3和FastAPI
- **异步架构**: 全异步设计，高性能处理
- **类型安全**: 完整的类型注解和验证
- **微服务架构**: 独立部署，易于扩展
- **可观测性**: 结构化日志、Prometheus指标
- **容器化**: Docker和Docker Compose支持

## 🏗️ 架构设计

```
auth-service/
├── auth_service/           # 主应用包
│   ├── api/               # API接口层
│   │   └── rest/          # REST API
│   ├── cmd/               # 命令行工具
│   │   └── server/        # 服务器启动
│   ├── config/            # 配置管理
│   ├── core/              # 核心组件
│   │   ├── database.py    # 数据库管理
│   │   └── redis.py       # Redis管理
│   ├── middleware/        # 中间件
│   │   ├── logging.py     # 日志中间件
│   │   ├── metrics.py     # 指标中间件
│   │   └── security.py    # 安全中间件
│   └── models/            # 数据模型
│       ├── base.py        # 基础模型
│       ├── user.py        # 用户模型
│       └── auth.py        # 认证模型
├── scripts/               # 脚本工具
├── monitoring/            # 监控配置
├── Dockerfile            # Docker镜像
├── docker-compose.yml    # 容器编排
└── pyproject.toml        # 项目配置
```

## 🚀 快速开始

### 环境要求

- Python 3.13.3+
- UV包管理器
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (可选)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life/services/auth-service
```

2. **运行设置脚本**
```bash
./scripts/setup.sh
```

3. **配置环境变量**
```bash
# 编辑 .env 文件
cp env.example .env
vim .env
```

4. **启动服务**

**方式一：Docker Compose (推荐)**
```bash
./scripts/start.sh
```

**方式二：开发模式**
```bash
./scripts/dev.sh
```

### 验证安装

访问以下地址验证服务是否正常运行：

- 🌐 认证服务: http://localhost:8000
- 📚 API文档: http://localhost:8000/docs
- 📊 Prometheus: http://localhost:9091
- 📈 Grafana: http://localhost:3000 (admin/admin)

## 📖 API文档

### 认证端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/logout` | 用户登出 |
| POST | `/api/v1/auth/refresh` | 刷新令牌 |

### 用户端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/users/register` | 用户注册 |
| GET | `/api/v1/users/profile` | 获取用户档案 |
| PUT | `/api/v1/users/profile` | 更新用户档案 |

### 安全端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/security/change-password` | 修改密码 |
| POST | `/api/v1/security/enable-mfa` | 启用MFA |
| POST | `/api/v1/security/disable-mfa` | 禁用MFA |

### OAuth端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/oauth/{provider}/authorize` | OAuth授权 |
| POST | `/api/v1/oauth/{provider}/callback` | OAuth回调 |

## 🔧 配置说明

### 环境变量

主要配置项说明：

```bash
# 应用配置
APP_NAME=索克生活认证服务
ENVIRONMENT=development  # development/testing/staging/production
DEBUG=false

# 数据库配置
DATABASE__HOST=localhost
DATABASE__PORT=5432
DATABASE__NAME=auth_db
DATABASE__USER=auth_user
DATABASE__PASSWORD=auth_password

# Redis配置
REDIS__HOST=localhost
REDIS__PORT=6379
REDIS__DB=0

# JWT配置
JWT__SECRET_KEY=your-secret-key
JWT__ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT__REFRESH_TOKEN_EXPIRE_DAYS=7

# 安全配置
SECURITY__MAX_LOGIN_ATTEMPTS=5
SECURITY__LOCKOUT_DURATION_MINUTES=30
SECURITY__PASSWORD_MIN_LENGTH=8
```

### 数据库配置

支持PostgreSQL数据库，配置示例：

```python
DATABASE_SETTINGS = {
    "host": "localhost",
    "port": 5432,
    "name": "auth_db",
    "user": "auth_user", 
    "password": "auth_password",
    "pool_size": 10,
    "max_overflow": 20
}
```

## 🛠️ 开发指南

### 项目结构

- `auth_service/`: 主应用包
- `config/`: 配置管理模块
- `models/`: 数据模型定义
- `core/`: 核心组件 (数据库、Redis等)
- `api/`: API接口层
- `middleware/`: 中间件组件
- `cmd/`: 命令行工具

### 代码规范

项目使用以下工具确保代码质量：

- **Ruff**: 代码检查和格式化
- **Black**: 代码格式化
- **isort**: 导入排序
- **mypy**: 类型检查
- **pytest**: 单元测试

运行代码检查：
```bash
uv run ruff check .
uv run black --check .
uv run mypy .
```

运行测试：
```bash
uv run pytest
```

### 数据库迁移

使用Alembic进行数据库迁移：

```bash
# 生成迁移文件
uv run alembic revision --autogenerate -m "描述"

# 执行迁移
uv run alembic upgrade head

# 回滚迁移
uv run alembic downgrade -1
```

## 🔒 安全特性

### 密码安全
- BCrypt哈希加密
- 密码复杂度要求
- 密码历史记录
- 定期密码更新提醒

### 会话安全
- JWT令牌认证
- 刷新令牌机制
- 会话超时控制
- 设备绑定验证

### 访问控制
- 基于角色的权限控制
- 细粒度权限管理
- API访问限制
- 审计日志记录

### 防护措施
- 登录尝试限制
- 账户锁定机制
- IP白名单/黑名单
- 异常登录检测

## 📊 监控和日志

### 日志系统
- 结构化日志记录
- 请求追踪ID
- 错误堆栈跟踪
- 性能指标记录

### 监控指标
- HTTP请求指标
- 数据库连接池状态
- Redis连接状态
- 业务指标统计

### 告警配置
- 服务健康检查
- 错误率监控
- 响应时间监控
- 资源使用监控

## 🚀 部署指南

### Docker部署

1. **构建镜像**
```bash
docker build -t suoke-auth-service .
```

2. **运行容器**
```bash
docker-compose up -d
```

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: suoke-auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
```

### 生产环境配置

生产环境需要注意的配置项：

- 设置强密码和密钥
- 启用HTTPS
- 配置防火墙规则
- 设置监控告警
- 定期备份数据库
- 配置日志轮转

## 🤝 贡献指南

### 开发流程

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

### 代码提交规范

使用Conventional Commits规范：

```
feat: 添加用户注册功能
fix: 修复登录验证问题
docs: 更新API文档
test: 添加单元测试
refactor: 重构认证逻辑
```

### 测试要求

- 单元测试覆盖率 > 80%
- 集成测试通过
- 安全测试通过
- 性能测试达标

## 📄 许可证

本项目采用Apache 2.0许可证。详见[LICENSE](LICENSE)文件。

## 🆘 支持

如有问题或建议，请通过以下方式联系：

- 📧 邮箱: song.xu@icloud.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/SUOKE2024/suoke_life/issues)
- 📖 文档: [项目文档](https://github.com/SUOKE2024/suoke_life/blob/main/services/auth-service/README.md)

---

**索克生活认证服务** - 为健康管理平台提供安全可靠的认证服务 🔐