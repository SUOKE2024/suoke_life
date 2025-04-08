# 索克生活代理协调服务

代理协调服务是索克生活AI代理系统的核心组件，负责管理用户会话、协调多代理协作、处理用户请求。

## 项目架构

采用Clean Architecture架构模式：

```
/
├── cmd/                # 应用程序入口点
│   └── server/        # 服务器启动代码
├── config/             # 配置文件
├── internal/           # 内部包
│   ├── config/        # 配置管理
│   ├── handlers/      # HTTP处理器
│   ├── middleware/    # HTTP中间件
│   ├── models/        # 数据模型
│   ├── repositories/  # 数据存储层
│   ├── services/      # 业务逻辑层
│   └── tests/         # 测试目录
│       ├── integration/ # 集成测试
│       └── unit/      # 单元测试
├── pkg/                # 公开的包
│   ├── errors/        # 错误处理
│   └── utils/         # 工具函数
└── scripts/            # 脚本文件
```

## 测试指南

### 单元测试

单元测试位于项目内部对应模块旁边或`internal/tests/unit`目录中，使用Go标准测试框架。

运行单元测试：

```bash
./scripts/run_unit_tests.sh
```

### 集成测试

集成测试位于`internal/tests/integration`目录中，测试API接口的完整功能。

运行集成测试：

```bash
./scripts/run_integration_tests.sh
```

### 测试覆盖率

生成测试覆盖率报告：

```bash
./scripts/run_coverage.sh
```

当前测试覆盖率：

| 包 | 覆盖率 |
|-----|------|
| handlers | 83.3% |
| middleware | 40.9% |
| **总体** | **25.9%** |

函数级别覆盖率：
- `HealthCheck`: 100.0%
- `CreateSession`: 60.0%
- `GetSessions`: 100.0%
- `JWTAuthMiddleware`: 85.7%

## 已实现的测试用例

### 单元测试

- `TestHealthCheck`: 测试健康检查接口
- `TestCreateSession`: 测试创建会话接口
- `TestGetSessions`: 测试获取会话列表接口
- `TestGetSessionsWithoutUserId`: 测试无userId参数情况
- `TestJWTAuthMiddleware`: 测试JWT认证中间件，多场景测试

### 集成测试

- `TestCreateSession`: 测试创建会话API
- `TestGetSessions`: 测试获取会话列表API
- `TestJWTAuthMiddleware`: 测试JWT认证中间件，包含四个子用例：
  - `NoAuthHeader`: 测试无认证头的情况
  - `InvalidTokenFormat`: 测试无效Token格式
  - `InvalidToken`: 测试无效Token
  - `ValidToken`: 测试有效Token

## API文档

服务API文档基于Swagger生成，启动服务后访问：

```
http://localhost:8080/swagger/index.html
```

## 依赖项

- Gin Web框架
- Testify测试工具
- Swagger API文档
- GORM数据库ORM
- 更多依赖见`go.mod`文件

## 授权协议

Copyright © 2023 索克生活 All Rights Reserved.