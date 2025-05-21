# 区块链服务 (Blockchain Service)

区块链服务是SoKe Life平台的核心组件之一，负责健康数据的区块链存储、验证和访问控制。该服务通过智能合约确保健康数据的不可篡改性、可追溯性和隐私保护。

## 主要功能

* **健康数据区块链存储**：将用户健康数据的哈希值存储到区块链上，确保数据完整性
* **数据验证**：验证健康数据的完整性，防止篡改
* **零知识证明验证**：支持验证健康数据的特定属性而不暴露原始数据
* **访问控制**：基于智能合约的分级权限系统，管理健康数据的访问权限
* **数据隐私**：通过零知识证明和加密技术保护用户隐私
* **跨服务数据完整性验证**：确保不同服务之间的数据一致性

## 技术架构

* **语言**：Python 3.11+
* **区块链**：以太坊兼容链
* **通信协议**：gRPC
* **智能合约**：Solidity 0.8.x
* **数据库**：PostgreSQL
* **缓存**：Redis
* **消息队列**：通过Message Bus服务集成

## 智能合约

区块链服务使用以下智能合约：

1. **HealthDataStorage** - 负责健康数据的存储和验证
2. **ZKPVerifier** - 负责零知识证明验证
3. **AccessControl** - 负责健康数据的访问控制
4. **SuoKeLifeContractFactory** - 工厂合约，管理其他合约的部署和交互

## API 接口

服务通过gRPC提供以下主要接口：

* `StoreHealthData` - 存储健康数据到区块链
* `VerifyHealthData` - 验证健康数据的完整性
* `VerifyWithZKP` - 使用零知识证明验证健康数据的特定属性
* `GetHealthDataRecords` - 获取用户的健康数据记录
* `AuthorizeAccess` - 授权访问健康数据
* `RevokeAccess` - 撤销访问授权
* `GetBlockchainStatus` - 获取区块链状态

## 项目结构

```
blockchain-service/
├── api/                       # API定义和接口
│   └── grpc/                  # gRPC接口定义
├── cmd/                       # 命令行工具和主程序
│   └── server/                # 服务入口
├── config/                    # 配置文件
├── deploy/                    # 部署配置
│   ├── docker/                # Docker部署
│   └── kubernetes/            # Kubernetes部署
├── docs/                      # 文档
├── internal/                  # 内部实现代码
│   ├── blockchain/            # 区块链操作
│   │   └── contracts/         # 智能合约
│   ├── delivery/              # 服务交付层
│   ├── model/                 # 数据模型
│   ├── repository/            # 数据访问层
│   └── service/               # 业务逻辑层
├── pkg/                       # 可重用的公共包
│   └── utils/                 # 工具函数
└── test/                      # 测试
    ├── client/                # 测试客户端
    ├── integration/           # 集成测试
    └── unit/                  # 单元测试
```

## 开发状态

**开发状态**：✅ 已完成

已实现的功能：
- [x] 核心智能合约的设计和实现
- [x] 区块链存储和验证服务
- [x] 零知识证明验证
- [x] 访问控制和授权管理
- [x] 跨服务数据完整性验证
- [x] gRPC API实现
- [x] 单元测试和集成测试
- [x] Docker和Kubernetes部署配置

## 安装和启动

### 使用Docker

```bash
# 构建镜像
docker build -t suokelife/blockchain-service:latest -f deploy/docker/Dockerfile .

# 运行容器
docker run -d --name blockchain-service \
  -p 50055:50055 -p 9090:9090 \
  -v $(pwd)/config:/app/config \
  suokelife/blockchain-service:latest
```

### 直接运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
python cmd/server/main.py
```

## 测试

```bash
# 运行单元测试
python -m pytest test/unit

# 运行集成测试
python -m pytest test/integration

# 使用测试客户端
python -m test.client.test_client --server=localhost:50055
```

## 依赖服务

区块链服务依赖于以下服务：

* **区块链节点**：以太坊兼容节点 (Geth, Infura等)
* **用户服务**：用户认证和授权
* **消息总线**：事件发布与订阅
* **ZKP验证服务**：零知识证明的生成和验证 (可选)

## 配置

配置文件位于`config/config.yaml`，主要配置项包括：

* 服务端口和地址
* 区块链连接参数
* 智能合约地址
* 数据库连接
* 日志级别
* 认证与授权设置

## 贡献

欢迎贡献代码。请确保提交前运行测试，并遵循项目的代码风格。

## 许可证

Copyright © 2023 SoKe Life。保留所有权利。 