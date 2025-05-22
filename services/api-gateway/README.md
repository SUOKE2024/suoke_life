# 索克生活API网关服务

API网关服务是索克生活APP平台的核心基础设施，为平台提供统一的API入口，负责请求路由、负载均衡、认证授权、请求限流、监控和日志等功能，确保各微服务系统安全、高效、可靠地运行。

## 功能特性

- **统一接入点**：为所有微服务提供统一的API入口，简化客户端与后端的交互
- **请求路由**：基于路径、请求方法、Header等规则智能路由请求到相应的微服务
- **负载均衡**：支持多种负载均衡策略，优化后端服务资源利用
- **认证授权**：统一的用户认证与权限控制，支持多种认证方式（JWT、OAuth2.0）
- **限流熔断**：保护后端服务不被过载，提供服务降级和熔断机制
- **请求转换**：在HTTP、gRPC等不同协议间进行转换，支持RESTful API和gRPC双模式
- **缓存代理**：智能缓存常用请求响应，提高系统性能
- **日志监控**：统一收集API访问日志，提供实时监控和报警
- **跨域支持**：内置CORS支持，解决前端跨域问题
- **版本管理**：支持API版本控制，实现平滑升级
- **健康检查**：监控所有微服务健康状态，自动处理故障转移

## 系统架构

服务采用模块化设计，主要组件包括：

- **API层**：支持REST和gRPC的双协议服务接口定义
- **服务层**：实现路由、负载均衡、限流等核心网关功能
- **中间件层**：提供认证、日志、监控等横切关注点功能
- **集成层**：集成各微服务的服务发现和健康监控

服务架构图：

```
┌────────────────────────────────────────────────────────────┐
│                    API网关 (api-gateway)                    │
├────────────────┬───────────────────────┬───────────────────┤
│   REST API     │      服务发现/注册      │     gRPC API     │
├────────────────┴───────────────────────┴───────────────────┤
│                          中间件层                           │
├────────────────┬───────────────────────┬───────────────────┤
│     认证授权     │    限流/熔断/降级     │   监控/日志/追踪   │
├────────────────┴───────────────────────┴───────────────────┤
│                          服务路由                           │
├────────────────┬───────────────────────┬───────────────────┤
│   路径重写      │       请求转换        │     响应缓存       │
├────────────────┼───────────────────────┼───────────────────┤
│   负载均衡      │       健康检查        │     失败转移       │
└────────────────┴───────────────────────┴───────────────────┘
```

## 新增功能特性

除了基本的API网关功能外，该服务还实现了以下高级特性：

### 1. 双协议支持

提供REST和gRPC双协议支持，允许客户端使用多种方式与后端服务通信：

- **REST API**：标准HTTP接口，适用于大多数客户端
- **gRPC API**：高性能二进制通信，适用于服务间通信

### 2. 路径重写

支持基于正则表达式的路径重写，可以在不修改后端服务的情况下调整API路径：

```yaml
routes:
  - name: user
    prefix: /api/user/
    service: user-service
    rewrite_path: "^/api/user/([0-9]+)/profile(.*)$ => /users/$1/profile$2"
```

### 3. 响应缓存

提供灵活的响应缓存机制，减轻后端服务压力并提高响应速度：

- **多级缓存**：支持内存和Redis缓存
- **精细控制**：可按服务、路径和请求头定制缓存策略
- **自动失效**：支持基于时间的自动过期和手动清除

### 4. 安全增强

提供完整的JWT认证和授权机制：

- **JWT验证**：验证访问令牌有效性和过期时间
- **角色控制**：基于令牌中的角色信息控制API访问
- **令牌刷新**：支持通过刷新令牌获取新的访问令牌

### 5. 监控和可观测性

集成全面的监控和可观测性工具：

- **Prometheus指标**：收集请求数、响应时间、错误率等关键指标
- **Grafana仪表盘**：直观展示网关性能和健康状况
- **结构化日志**：详细记录请求处理过程和异常情况

## 部署指南

### 容器镜像构建

API网关服务使用 containerd 作为容器运行时，推荐使用 buildah 构建容器镜像：

```bash
# 克隆代码仓库
git clone https://github.com/suoke/life.git
cd life/services/api-gateway

# 使用 buildah 构建镜像
./scripts/build_containerd.sh

# 自定义构建参数
REGISTRY=your-registry.com IMAGE_NAME=suoke/api-gateway TAG=v1.0 USE_ENHANCED=true PUSH_IMAGE=true ./scripts/build_containerd.sh
```

> **注意**：从 Kubernetes v1.20 开始，containerd 已替代 Docker 成为推荐的容器运行时。详情请参阅 [docs/containerd-migration.md](docs/containerd-migration.md)。

### Kubernetes部署

在Kubernetes集群中部署：

```bash
# 创建命名空间
kubectl create namespace suoke

# 部署 containerd RuntimeClass
kubectl apply -f deploy/kubernetes/runtime-class.yaml

# 部署服务
kubectl apply -f deploy/kubernetes/deployment-containerd.yaml

# 验证部署
kubectl get pods -n suoke -l app=api-gateway
```

### 本地开发部署（支持Docker兼容性）

尽管生产环境使用 containerd，本地开发仍可使用 Docker：

```bash
# 使用增强版 Dockerfile 构建 Docker 镜像
docker build -t suoke/api-gateway:dev -f deploy/docker/Dockerfile.containerd .

# 运行容器
docker run -p 8080:8080 -p 50050:50050 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  -e LOG_LEVEL=DEBUG \
  suoke/api-gateway:dev
```

### 配置环境变量

可通过环境变量调整服务行为：

| 环境变量 | 说明 | 默认值 |
|---------|------|-------|
| CONFIG_PATH | 配置文件路径 | config/config.yaml |
| LOG_LEVEL | 日志级别 | INFO |
| LOGGING_FILE | 日志文件路径 | logs/api_gateway.log |
| JWT_SECRET_KEY | JWT密钥 | 无（必须设置） |

## 本地开发

### 环境要求

- Python 3.10+
- 虚拟环境 (推荐使用venv)

### 安装依赖

```bash
# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate.bat  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 启动服务

```bash
# 启动API网关服务
./scripts/start_service.sh
```

### 测试

```bash
# 运行单元测试
pytest test/

# 运行集成测试
pytest test/integration/
```

## 配置文件说明

配置文件采用YAML格式，主要包含以下部分：

```yaml
server:
  rest:
    host: 0.0.0.0
    port: 8080
  grpc:
    host: 0.0.0.0
    port: 50050
  production: false

middleware:
  cors:
    enabled: true
    # CORS配置...

  rate_limit:
    enabled: true
    # 限流配置...

  auth:
    enabled: true
    # 认证配置...

cache:
  enabled: true
  type: memory  # memory或redis
  # 缓存配置...

routes:
  - name: auth
    prefix: /api/auth/
    service: auth-service
    # 路由配置...
```

## 贡献指南

欢迎贡献代码和提交问题，请遵循以下步骤：

1. Fork仓库并创建特性分支
2. 运行测试确保代码质量
3. 提交PR并描述变更内容

## 许可证

索克生活平台专有软件，未经授权不得使用、复制或分发。

## 联系我们

如有任何疑问或需要进一步支持，请联系API网关团队：api-gateway-team@suoke.life 