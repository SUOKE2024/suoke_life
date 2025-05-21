# 索克生活APP微服务开发规范

## 目录

- [概述](#概述)
- [目录结构规范](#目录结构规范)
- [命名规范](#命名规范)
- [代码组织原则](#代码组织原则)
- [依赖管理](#依赖管理)
- [错误处理](#错误处理)
- [日志规范](#日志规范)
- [配置管理](#配置管理)
- [注释与文档](#注释与文档)
- [代码质量](#代码质量)

## 概述

本文档定义了索克生活APP微服务开发的标准规范，旨在确保所有微服务的一致性、可维护性和高质量。所有团队成员在开发微服务时必须遵循这些准则。

## 目录结构规范

每个微服务必须遵循以下标准目录结构：

```
service-name/               # 微服务根目录
├── api/                    # API定义
│   ├── grpc/               # gRPC接口定义
│   │   └── proto/          # Protobuf文件
│   └── rest/               # REST API定义（如使用）
├── cmd/                    # 应用程序入口
│   └── server/             # 服务主程序
├── config/                 # 配置文件目录
│   ├── config.yaml         # 基础配置
│   ├── config.dev.yaml     # 开发环境配置
│   ├── config.prod.yaml    # 生产环境配置
│   └── prompts/            # AI提示配置（如适用）
├── deploy/                 # 部署相关文件
│   ├── docker/             # Docker配置
│   ├── kubernetes/         # Kubernetes配置
│   ├── grafana/            # Grafana仪表盘配置
│   └── prometheus/         # Prometheus监控配置
├── docs/                   # 服务文档
│   ├── api/                # API文档
│   ├── design/             # 设计文档
│   └── development/        # 开发指南
├── internal/               # 内部实现代码（不可被外部导入）
│   ├── delivery/           # 接口实现层（HTTP/gRPC处理器）
│   │   ├── grpc/           # gRPC服务实现
│   │   └── rest/           # REST控制器（如使用）
│   ├── service/            # 业务逻辑层（领域服务）
│   ├── repository/         # 数据访问层（数据存储）
│   ├── model/              # 领域模型（业务实体）
│   └── integration/        # 外部服务集成
├── pkg/                    # 公共包（可被外部服务导入）
│   └── utils/              # 通用工具函数
├── scripts/                # 构建和部署脚本
├── test/                   # 测试代码（唯一的测试目录）
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── e2e/                # 端到端测试
├── .gitignore              # Git忽略文件
├── Dockerfile              # Docker构建文件
├── docker-compose.yml      # 本地开发Docker Compose配置
├── requirements.txt        # 项目依赖（Python项目）
├── README.md               # 项目说明文档
└── CHANGELOG.md            # 变更日志
```

特殊说明：
- 不允许同时存在 `test/` 和 `tests/` 目录，统一使用 `test/`
- 每个微服务必须有自己的 `README.md` 文件
- 特殊功能的微服务可以添加额外目录，但必须遵循上述基本结构

## 命名规范

### 文件命名

- **Python文件**：使用蛇形命名法（`snake_case.py`）
- **配置文件**：使用蛇形命名法（`config_name.yaml`）
- **Protobuf文件**：使用蛇形命名法（`service_name.proto`）
- **Markdown文档**：使用大写并用下划线分隔（`README.md`, `API_GUIDE.md`）

### 代码命名

#### Python代码
- **变量和函数**：使用蛇形命名法（`variable_name`, `function_name()`）
- **类**：使用帕斯卡命名法（`ClassName`）
- **常量**：使用大写蛇形命名法（`CONSTANT_NAME`）
- **私有成员**：使用下划线前缀（`_private_variable`, `_private_method()`）

### API命名

- **REST API路径**：使用kebab-case小写（`/api/v1/user-profiles`）
- **HTTP方法**：遵循RESTful约定（GET查询、POST创建、PUT更新、DELETE删除）
- **gRPC服务**：使用帕斯卡命名法（`UserService`）
- **gRPC方法**：使用帕斯卡命名法（`CreateUser`, `GetUserProfile`）

## 代码组织原则

所有微服务应遵循以下架构设计原则：

### 1. 关注点分离

- **delivery层**：负责请求处理和响应生成，不包含业务逻辑
- **service层**：实现核心业务逻辑，不关心数据存储细节
- **repository层**：负责数据访问和持久化，屏蔽底层存储实现
- **model层**：定义领域模型和业务实体，不包含业务逻辑

### 2. 依赖倒置

- 高层模块不应依赖低层模块，两者都应依赖抽象
- 使用接口定义跨层调用，便于模拟测试
- 各层之间的数据传输使用专用DTO/VO对象

### 3. 单一职责

- 每个服务、模块、函数只负责一项任务
- 避免"上帝类"和"上帝函数"
- 当函数超过50行时，考虑拆分为更小的函数

### 4. 显式优于隐式

- 避免使用魔法常量和隐式转换
- 函数参数应明确表达意图
- 异常情况应显式处理

## 依赖管理

### Python项目

- 使用`requirements.txt`精确指定依赖版本
- 依赖版本应使用固定版本号（例如`package==1.2.3`）
- 虚拟环境必须使用`venv`管理
- 考虑使用`poetry`作为依赖管理工具

### 第三方库选择标准

选择第三方库时应考虑以下因素：

1. 活跃度：有持续维护和更新
2. 社区支持：足够的用户量和社区支持
3. 稳定性：API接口稳定，版本更新频率合理
4. 安全性：无已知严重安全漏洞
5. 许可证：与项目兼容的开源许可证

## 错误处理

### 错误传播原则

- 错误应向上传播，在适当的层级处理
- 底层错误应包装为业务错误再传播给上层
- 避免在日志中暴露敏感信息

### 错误类型

每个微服务应定义以下标准错误类型：

1. **ValidationError**: 输入验证错误
2. **AuthenticationError**: 身份验证错误
3. **AuthorizationError**: 权限错误
4. **ResourceNotFoundError**: 资源不存在
5. **ConflictError**: 资源冲突错误
6. **InternalError**: 内部服务错误
7. **ExternalServiceError**: 外部服务调用错误
8. **RateLimitError**: 限流错误

### 错误响应格式

REST API错误响应应遵循以下JSON格式：

```json
{
  "code": "ERROR_CODE",
  "message": "Human readable error message",
  "details": {
    "field1": "Field specific error",
    "field2": "Another field error"
  },
  "request_id": "unique-request-identifier"
}
```

gRPC错误应使用标准Status消息并附加元数据。

## 日志规范

### 日志级别使用原则

- **ERROR**: 需要立即关注的错误
- **WARNING**: 潜在问题，但不影响当前请求
- **INFO**: 重要业务事件
- **DEBUG**: 调试信息，仅在开发环境启用

### 日志格式

- 使用结构化日志（JSON格式）
- 必须包含时间戳、服务名、请求ID、日志级别
- 敏感信息（密码、令牌）必须脱敏

### 关键事件日志要求

以下事件必须记录日志：

1. 服务启动和关闭
2. 鉴权失败
3. 输入验证失败
4. 业务操作失败
5. 外部服务调用失败
6. 性能异常（慢请求）

## 配置管理

### 配置优先级

配置加载优先级从高到低：

1. 命令行参数
2. 环境变量
3. 环境特定配置文件（`config.prod.yaml`）
4. 基础配置文件（`config.yaml`）
5. 代码默认值

### 配置项命名规范

- 环境变量使用大写并用下划线分隔（`SERVICE_DB_HOST`）
- 配置文件中使用小驼峰或下划线命名（YAML格式）
- 敏感配置应支持从外部安全存储（如Vault）加载

### 必要配置项

每个服务必须支持以下基本配置项：

```yaml
service:
  name: "service-name"
  version: "1.0.0"
  env: "development"
  
server:
  host: "0.0.0.0"
  port: 8080
  grpc_port: 50051
  
database:
  host: "localhost"
  port: 5432
  name: "dbname"
  user: "username"
  password: "${DB_PASSWORD}"  # 从环境变量加载
  
logging:
  level: "info"
  format: "json"
  
metrics:
  enabled: true
  endpoint: "/metrics"
```

## 注释与文档

### 代码注释

- 每个包、类、接口、公共函数必须有文档注释
- 复杂算法或业务逻辑需要详细注释
- 注释应解释"为什么"而不是"是什么"
- TODO、FIXME等注释必须包含日期和开发者标识

### API文档

- REST API必须提供OpenAPI规范文档
- gRPC服务必须提供详细的Protobuf注释
- API文档应包括请求/响应示例

### README要求

每个微服务的README.md必须包含：

1. 服务概述和职责
2. 主要功能列表
3. 技术栈说明
4. 本地开发环境设置指南
5. API接口概览
6. 配置项说明
7. 部署指南
8. 依赖服务列表
9. 故障排除指南

## 代码质量

### 代码风格

- Python代码必须遵循PEP 8风格指南
- 使用Linter确保代码质量（如`flake8`, `pylint`）

### 单元测试要求

- 所有公共函数必须有单元测试
- 测试覆盖率目标：
  - 业务逻辑层（service）: >90%
  - 数据访问层（repository）: >85%
  - 接口层（delivery）: >75%
- 测试应包括正常路径和异常路径

### 代码审查

- 所有代码必须经过代码审查才能合并
- 代码审查关注点：功能正确性、设计质量、代码可读性、测试覆盖率、安全问题
- 严重问题必须修复，建议性问题可酌情处理

### 性能考量

- 数据库查询应有索引
- 批量操作优于循环操作
- 大型列表应使用分页
- 慢操作应考虑异步处理
- 高频调用应使用缓存

## 结论

遵循本规范可确保微服务的一致性、可维护性和高质量。所有开发者须遵守这些准则，特殊情况需提出例外申请并获得技术负责人批准。