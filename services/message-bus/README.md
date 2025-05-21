# Message Bus 服务

消息总线服务是索克生命（Suoke Life）平台的核心基础设施服务，提供可靠、高性能、安全的消息发布/订阅功能，支持系统中各微服务间的异步通信。

## 功能概述

- **主题管理**：创建、删除、查询和列出主题
- **消息发布**：向指定主题发布消息，支持属性过滤和优先级设置
- **消息订阅**：基于主题和属性过滤订阅消息
- **可靠传递**：确保消息的可靠传递，支持持久化和重试机制
- **安全机制**：身份验证和授权，确保消息安全
- **可观测性**：全面的监控、日志记录和追踪

## 技术架构

消息总线服务采用以下技术栈：

- **语言/框架**：Python 3.11+，AsyncIO
- **通信协议**：gRPC (主要)，REST (辅助)
- **消息存储**：Apache Kafka
- **主题管理**：Redis / 文件系统 (开发环境)
- **可观测性**：Prometheus + Grafana
- **容器化**：Docker
- **编排**：Kubernetes

### 架构图

```
+-------------------+      +------------------+
| 微服务/客户端     | gRPC | 消息总线服务     |
| (发布/订阅)      +------>+ (Message Bus)    |
+-------------------+      +--------+---------+
                                    |
                                    v
     +---------------+     +--------+---------+
     | Redis         |<--->+ 主题管理         |
     | (主题管理)     |     |                 |
     +---------------+     +--------+---------+
                                    |
                                    v
     +---------------+     +--------+---------+
     | Kafka         |<--->+ 消息存储/检索    |
     | (消息存储)     |     |                 |
     +---------------+     +-----------------+
```

## API 接口

消息总线服务主要通过gRPC提供服务，包含以下主要接口：

### 主题管理

- `CreateTopic`: 创建新主题
- `GetTopic`: 获取主题详情
- `ListTopics`: 列出所有主题
- `DeleteTopic`: 删除主题

### 消息发布/订阅

- `PublishMessage`: 向主题发布消息
- `Subscribe`: 订阅主题消息
- `GetMessage`: 获取指定消息详情

### 健康检查

- `HealthCheck`: 服务健康状态检查

详细接口定义请查看 [api/grpc/message_bus.proto](api/grpc/message_bus.proto) 文件。

## 消息格式

消息包含以下字段：

- `message_id`: 消息唯一标识符
- `topic`: 主题名称
- `payload`: 消息内容 (二进制)
- `attributes`: 消息属性 (键值对)
- `publish_time`: 发布时间戳
- `publisher_id`: 发布者标识符

## 开发指南

### 环境准备

1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

2. 启动开发环境依赖 (使用Docker Compose)

```bash
cd deploy/docker
docker-compose -f docker-compose.dev.yml up -d
```

3. 运行服务

```bash
python cmd/server/main.py
```

### 测试

运行单元测试：

```bash
pytest
```

运行集成测试：

```bash
pytest test/integration
```

### 生成gRPC代码

如果修改了proto文件，需要重新生成gRPC代码：

```bash
python -m grpc_tools.protoc -I./api/grpc --python_out=./api/grpc --grpc_python_out=./api/grpc message_bus.proto
```

## 部署指南

### Docker部署

1. 构建镜像

```bash
docker build -t sokelife/message-bus:latest -f deploy/docker/Dockerfile --target production .
```

2. 运行容器

```bash
docker run -d --name message-bus -p 50051:50051 -p 9090:9090 \
  -e MB_KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  -e MB_REDIS_HOST=redis \
  sokelife/message-bus:latest
```

### Kubernetes部署

使用Helm进行部署：

```bash
cd deploy/kubernetes
helm install message-bus ./helm/message-bus -f values.yaml
```

#### 生产环境配置

生产环境中，需要设置以下环境变量或配置：

- `APP_ENV=production`: 设置环境为生产环境
- Kafka连接信息和安全认证
- Redis连接信息和安全认证
- JWT公钥路径
- TLS证书

## 监控和告警

服务在`/metrics`端点上暴露Prometheus指标，包括：

- **请求指标**：请求计数、延迟、错误率
- **消息指标**：发布/订阅计数、处理延迟
- **资源使用**：内存、CPU使用率
- **依赖健康**：Kafka、Redis连接状态

建议配置以下告警：

- 服务实例不可用
- 高错误率 (>5%)
- 高请求延迟 (P95 > 500ms)
- Kafka或Redis连接异常

## 性能和扩展性

消息总线服务设计为水平可扩展，可通过以下方式调整性能：

- 增加服务实例数量
- 调整Kafka分区数
- 配置消息批处理大小
- 增加工作线程数量

## 故障排除

常见问题和解决方案：

1. **服务无法启动**
   - 检查配置文件和环境变量
   - 验证Kafka和Redis连接

2. **消息发布失败**
   - 检查主题是否存在
   - 验证Kafka集群状态
   - 检查权限设置

3. **高延迟问题**
   - 监控Kafka消费者延迟
   - 调整批处理设置
   - 检查网络连接问题

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork仓库
2. 创建功能分支
3. 提交变更
4. 创建Pull Request

请确保所有测试通过，并遵循代码风格指南。

## 许可证

索克生命专有软件，未经授权不得使用、复制或分发。 