# 索克生活认证服务 (Auth Service)

认证服务是索克生活微服务架构的关键组件，负责用户认证、授权和会话管理。

## 功能特性

- 用户注册和账户管理
- 用户认证（用户名/密码, OAuth等）
- JWT令牌生成和验证
- 访问控制和权限管理
- 会话管理
- 安全审计日志

## 技术栈

- 语言: Go 1.21+
- 框架: 标准库 + Gin
- 数据库: PostgreSQL
- 缓存: Redis
- 认证: JWT
- API文档: Swagger/OpenAPI

## 目录结构

```
auth-service/
├── cmd/                  # 应用入口
│   └── main.go          # 主程序入口
├── configs/              # 配置文件
│   └── config.json      # 默认配置文件
├── internal/             # 内部包
│   ├── config/          # 配置管理
│   ├── controllers/     # 控制器
│   ├── database/        # 数据库访问
│   │   └── migrations/  # 数据库迁移
│   ├── models/          # 数据模型
│   ├── repository/      # 存储库
│   ├── server/          # HTTP服务器
│   └── services/        # 业务服务
├── integration-tests/    # 集成测试
├── Dockerfile           # Docker构建文件
└── README.md            # 项目文档
```

## 开始使用

### 前置条件

- Go 1.21或更高版本
- PostgreSQL 13+
- Redis 6+

### 安装依赖

```bash
go mod download
```

### 配置

在`configs/config.json`中配置服务，或使用环境变量覆盖默认配置。

### 数据库迁移

服务启动时会自动运行数据库迁移，或手动运行：

```bash
# 待实现
```

### 启动服务

```bash
go run cmd/main.go
```

或使用Docker:

```bash
docker build -t suoke/auth-service .
docker run -p 8081:8081 suoke/auth-service
```

## API文档

### 主要端点

- `GET /health` - 健康检查
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新令牌
- `GET /auth/validate` - 验证令牌

### 认证流程

1. 客户端向`/auth/login`发送凭据
2. 服务器验证凭据并返回JWT访问令牌和刷新令牌
3. 客户端在后续请求中使用`Authorization: Bearer {token}`头
4. 当访问令牌过期时，客户端使用刷新令牌获取新的访问令牌

## 开发

### 测试

运行单元测试:

```bash
go test ./...
```

运行集成测试:

```bash
cd integration-tests
go test -v
```

### 构建

```bash
go build -o auth-service ./cmd/main.go
```

## 部署

服务可以部署为独立二进制文件、Docker容器或Kubernetes Pod。

### Docker部署

```bash
docker build -t suoke/auth-service:latest .
docker run -p 8081:8081 -e CONFIG_PATH=/app/configs/config.json suoke/auth-service:latest
```

## 监控和可观测性

服务提供以下监控端点:

- 健康检查: `/health`
- 指标: (待实现)
- 跟踪: (待实现)

## 安全考虑

- 所有敏感信息使用环境变量或安全存储
- 密码使用bcrypt算法哈希
- JWT令牌使用强密钥签名
- 定期轮换密钥
- 合理的令牌过期时间

## 扩展和集成

认证服务可以与其他索克生活微服务无缝集成，并可以通过以下方式扩展:

- 添加社交登录提供商
- 实现多因素认证
- 集成SAML或OIDC协议

## 贡献指南

请遵循项目的代码规范和提交消息约定。所有合并请求必须包含测试。

## 许可证

版权所有 © 索克生活技术团队
