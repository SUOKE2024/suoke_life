# 索克生活认证服务

认证服务负责处理用户认证、授权和账户管理，是索克生活平台的核心安全组件。

## 主要功能

- 用户注册与身份验证
- 多因素认证（MFA）
- OAuth 社交登录集成
- 基于角色的访问控制
- JWT 令牌管理
- 安全审计日志

## 技术栈

- 语言：Python 3.12+
- 数据库：PostgreSQL 13+
- 缓存：Redis 6+
- 通信协议：gRPC / REST
- 部署：Kubernetes / Docker

## 项目结构

```
auth-service/
├── api/                   # API定义
│   ├── grpc/              # gRPC服务定义
│   └── rest/              # REST API定义
├── cmd/                   # 服务入口点
│   └── server/            # 服务启动代码
├── config/                # 配置文件
├── deploy/                # 部署配置
│   ├── docker/            # Docker相关文件
│   └── kubernetes/        # Kubernetes配置文件
├── internal/              # 内部包
│   ├── db/                # 数据库连接管理
│   ├── delivery/          # API实现
│   ├── model/             # 数据模型
│   ├── observability/     # 监控和跟踪
│   ├── repository/        # 数据访问层
│   ├── schemas/           # 数据库Schema定义
│   ├── security/          # 安全相关功能
│   └── service/           # 业务逻辑层
├── pkg/                   # 可导出的包
│   ├── middleware/        # 中间件
│   └── utils/             # 工具函数
└── test/                  # 测试
    ├── integration/       # 集成测试
    └── unit/              # 单元测试
```

## 测试

我们使用 pytest 进行单元测试和集成测试。有关测试的详细信息，请参阅 [test/README.md](test/README.md)。

### 运行测试

项目提供了多个脚本来运行不同类型的测试：

- 运行所有单元测试：`./scripts/run_all_tests.sh`
- 运行安全模块测试：`./scripts/run_security_tests.sh`
- 运行仓储模块测试：`./scripts/run_repository_tests.sh`
- 运行集成测试：`./scripts/run_integration_tests.sh`

### 测试覆盖率

当前测试覆盖率统计（截至2025年5月22日）：

| 模块 | 覆盖率 |
|------|--------|
| 安全模块 (总体) | 92% |
| - JWT | 87% |
| - MFA | 93% |
| - 密码 | 94% |
| 仓储模块 (总体) | 81% |
| - 令牌仓储 | 95% |
| - OAuth仓储 | 93% |
| - 审计仓储 | 88% |
| - 用户仓储 | 57% |
| 整体覆盖率 | 85% |

测试覆盖率报告位于 `test/results/` 目录中。

## 环境变量

服务需要以下环境变量：

```
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auth_db
DB_USER=auth_user
DB_PASSWORD=auth_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT配置
JWT_SECRET=your-secret-key
JWT_ACCESS_EXPIRES=3600  # 1小时
JWT_REFRESH_EXPIRES=604800  # 7天

# 服务配置
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

## 开发

### 依赖安装

```bash
pip install -r requirements.txt
```

### 本地运行

```bash
python -m cmd.server.main
```

### Docker构建

```bash
docker build -t auth-service:latest -f deploy/docker/Dockerfile .
```

## API文档

API文档可通过以下方式获取：

- gRPC: 查看 `api/grpc/` 目录下的 *.proto 文件
- REST: 服务运行后访问 `/docs` 或 `/redoc` 端点

## 贡献

请参见 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解贡献指南。

## 许可证

本项目采用 Apache 2.0 许可证。