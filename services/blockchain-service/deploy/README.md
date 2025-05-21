# 区块链服务部署指南

本文档提供了SoKe Life区块链服务的部署说明。区块链服务可以使用Docker容器或Kubernetes集群进行部署。

## 环境要求

- Docker 20.10+
- Kubernetes 1.22+ (如果使用Kubernetes部署)
- 以太坊节点(如Geth或Ganache，用于开发环境)
- PostgreSQL 14+
- Redis 6+
- 消息队列服务(如RabbitMQ)

## Docker部署

### 构建镜像

```bash
# 在项目根目录执行
cd /path/to/services/blockchain-service
docker build -t sokelife/blockchain-service:latest -f deploy/docker/Dockerfile .
```

### 运行容器

```bash
# 创建网络（如果还没有）
docker network create sokelife-network

# 运行容器
docker run -d \
  --name blockchain-service \
  --network sokelife-network \
  -p 50055:50055 \
  -p 9090:9090 \
  -e DB_PASSWORD=your_db_password \
  -e MESSAGE_BUS_PASSWORD=your_mq_password \
  -e REDIS_PASSWORD=your_redis_password \
  -v /path/to/config:/app/config \
  -v /path/to/keys:/app/config/keys:ro \
  -v /path/to/zkp:/app/config/zkp:ro \
  sokelife/blockchain-service:latest
```

### 使用Docker Compose

创建`docker-compose.yml`文件：

```yaml
version: '3.8'

services:
  blockchain-service:
    image: sokelife/blockchain-service:latest
    container_name: blockchain-service
    ports:
      - "50055:50055"
      - "9090:9090"
    environment:
      - DB_PASSWORD=your_db_password
      - MESSAGE_BUS_PASSWORD=your_mq_password
      - REDIS_PASSWORD=your_redis_password
    volumes:
      - ./config:/app/config
      - ./keys:/app/config/keys:ro
      - ./zkp:/app/config/zkp:ro
    networks:
      - sokelife-network
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
      - rabbitmq
      - ethereum-node

  ethereum-node:
    image: ethereum/client-go:stable
    container_name: ethereum-node
    ports:
      - "8545:8545"
      - "8546:8546"
    volumes:
      - ethereum-data:/root/.ethereum
    command: >
      --http --http.addr=0.0.0.0 --http.port=8545 --http.api=eth,net,web3,personal
      --ws --ws.addr=0.0.0.0 --ws.port=8546 --ws.api=eth,net,web3,personal
      --allow-insecure-unlock --dev --dev.period=0
    networks:
      - sokelife-network

  postgres:
    image: postgres:14
    container_name: postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=sokelife
      - POSTGRES_PASSWORD=your_db_password
      - POSTGRES_DB=blockchain_service
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - sokelife-network

  redis:
    image: redis:6
    container_name: redis
    ports:
      - "6379:6379"
    command: redis-server --requirepass your_redis_password
    volumes:
      - redis-data:/data
    networks:
      - sokelife-network

  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=your_mq_password
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    networks:
      - sokelife-network

networks:
  sokelife-network:
    driver: bridge

volumes:
  ethereum-data:
  postgres-data:
  redis-data:
  rabbitmq-data:
```

运行Docker Compose:

```bash
docker-compose up -d
```

## Kubernetes部署

### 前提条件

- 运行中的Kubernetes集群
- `kubectl` 工具配置好
- 已创建的 `sokelife` 命名空间

### 部署步骤

1. 创建配置和密钥

```bash
# 创建数据库凭证密钥
kubectl create secret generic blockchain-db-credentials \
  --namespace sokelife \
  --from-literal=password=your_db_password

# 创建消息队列凭证密钥
kubectl create secret generic message-bus-credentials \
  --namespace sokelife \
  --from-literal=password=your_mq_password

# 创建Redis凭证密钥
kubectl create secret generic redis-credentials \
  --namespace sokelife \
  --from-literal=password=your_redis_password

# 创建区块链服务密钥
kubectl create secret generic blockchain-service-keys \
  --namespace sokelife \
  --from-file=encryption_key.pem=/path/to/encryption_key.pem \
  --from-file=jwt_private_key.pem=/path/to/jwt_private_key.pem \
  --from-file=jwt_public_key.pem=/path/to/jwt_public_key.pem
```

2. 应用Kubernetes配置

```bash
# 应用部署配置
kubectl apply -f deploy/kubernetes/deployment.yaml
```

3. 检查部署状态

```bash
# 检查Pod状态
kubectl get pods -n sokelife -l app=blockchain-service

# 检查服务状态
kubectl get services -n sokelife -l app=blockchain-service

# 查看日志
kubectl logs -n sokelife -l app=blockchain-service
```

## 验证部署

确认服务正常运行：

```bash
# 使用gRPC工具
grpcurl -plaintext localhost:50055 sokelife.blockchain.BlockchainService/GetBlockchainStatus

# 或使用测试客户端
cd /path/to/services/blockchain-service
python -m test.client.test_client --server=localhost:50055
```

## 配置选项

### 配置文件

区块链服务使用YAML配置文件。主要配置选项包括：

- **服务器配置**: 端口、工作线程数等
- **日志配置**: 日志级别、格式、文件等
- **区块链配置**: 节点端点、合约地址等
- **数据库配置**: 连接信息、连接池等
- **安全配置**: 加密密钥、JWT配置等
- **零知识证明配置**: 证明密钥、验证密钥等
- **服务集成配置**: 与其他服务的集成
- **监控配置**: Prometheus、追踪等
- **缓存配置**: Redis连接等

详细配置选项请参考`config/config.yaml`文件。

### 环境变量

区块链服务支持通过环境变量设置敏感配置，主要包括：

- `DB_PASSWORD`: 数据库密码
- `MESSAGE_BUS_PASSWORD`: 消息队列密码
- `REDIS_PASSWORD`: Redis密码

## 监控和调试

### Prometheus指标

服务暴露Prometheus指标在`:9090/metrics`端点。

### 日志

容器化部署时，日志被发送到标准输出，可以使用Docker或Kubernetes的日志工具查看：

```bash
# Docker
docker logs blockchain-service

# Kubernetes
kubectl logs -n sokelife deployment/blockchain-service
```

## 维护

### 备份

定期备份数据库和区块链数据：

```bash
# 备份PostgreSQL数据库
pg_dump -h postgres -U sokelife blockchain_service > blockchain_backup_$(date +%Y%m%d).sql

# 备份区块链数据
# 根据具体区块链实现方式进行备份
```

### 更新

```bash
# 更新Docker镜像
docker pull sokelife/blockchain-service:latest
docker-compose down
docker-compose up -d

# 更新Kubernetes部署
kubectl set image deployment/blockchain-service -n sokelife blockchain-service=sokelife/blockchain-service:latest
```

## 故障排除

### 常见问题

1. **无法连接到区块链节点**
   - 检查区块链节点是否运行
   - 检查网络连接和防火墙设置
   - 验证区块链节点地址配置是否正确

2. **数据库连接错误**
   - 检查数据库凭证
   - 验证数据库服务是否正常运行
   - 检查网络连接

3. **gRPC服务不可用**
   - 检查端口映射
   - 验证服务是否正常启动
   - 检查日志中的错误消息

### 日志解析

```bash
# 提取错误日志
docker logs blockchain-service 2>&1 | grep ERROR

# Kubernetes
kubectl logs -n sokelife -l app=blockchain-service | grep ERROR
```

## 安全考虑

- 所有密钥和敏感信息应使用Kubernetes Secrets或环境变量管理
- 定期更新依赖包和Docker基础镜像
- 启用网络策略限制服务间通信
- 为重要数据配置备份策略

## 参考资源

- [区块链服务API文档](../docs/api.md)
- [以太坊文档](https://ethereum.org/developers/docs/)
- [零知识证明文档](https://zkp.science/)
- [gRPC文档](https://grpc.io/docs/) 