# 索克生活健康数据服务 (Health Data Service)

索克生活健康数据服务是一个专为索克生活应用打造的现代化健康数据管理平台。该服务负责存储、分析和管理来自多种来源的健康数据，提供中医体质分析、健康趋势洞察以及数据区块链存证等功能。

## 核心功能

- **健康数据管理**：收集、存储和检索各类健康数据，包括步数、心率、睡眠、血压等
- **可穿戴设备集成**：支持从Apple Health、Fitbit、Garmin、小米等可穿戴设备导入数据
- **中医体质分析**：基于多模态健康数据和中医四诊数据（望、闻、问、切）进行体质辨识
- **健康洞察**：分析健康数据趋势，提供有价值的健康洞察和建议
- **数据区块链存证**：通过区块链技术确保健康数据的不可篡改性和真实性
- **零知识证明**：支持健康数据的隐私保护和选择性披露
- **REST和gRPC API**：提供多种集成方式，满足不同的应用场景

## 技术架构

健康数据服务采用微服务架构，主要包括以下组件：

- **API层**：REST和gRPC接口，负责与客户端通信
- **服务层**：业务逻辑处理，包括健康数据管理、中医体质分析、健康洞察等
- **数据层**：数据存储和检索
- **区块链集成**：与区块链服务交互，提供数据存证和验证
- **分析引擎**：实现健康数据分析和中医体质辨识

### 开发技术

- **编程语言**：Python 3.9+
- **Web框架**：FastAPI (REST API), gRPC (RPC API)
- **数据库**：PostgreSQL
- **ORM**：SQLAlchemy
- **消息队列**：RabbitMQ
- **容器**：Docker
- **编排**：Kubernetes
- **监控**：Prometheus, Grafana
- **日志**：ELK Stack

## 部署指南

### 先决条件

- Python 3.9+
- PostgreSQL 13+
- Docker（可选，用于容器化部署）
- Kubernetes（可选，用于集群部署）

### 本地开发环境设置

1. 克隆代码库
   ```bash
   git clone https://github.com/SUOKE2024/suoke_life.git
   cd services/health-data-service
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑.env文件，填写必要的配置项
   ```

5. 启动开发服务器
   ```bash
   python -m cmd.server
   ```

### Docker部署

```bash
# 构建Docker镜像
docker build -t health-data-service:latest .

# 运行容器
docker run -p 8080:8080 --env-file .env health-data-service:latest
```

### Kubernetes部署

```bash
# 应用Kubernetes配置
kubectl apply -f deploy/kubernetes/
```

## API文档

### REST API

REST API文档可通过Swagger UI访问：
```
http://<service-host>:<port>/docs
```

### gRPC API

gRPC API定义在`api/grpc/health_data.proto`文件中。可以使用Protocol Buffers编译器生成客户端代码：

```bash
protoc --go_out=. --go-grpc_out=. api/grpc/health_data.proto  # Go
protoc --python_out=. --grpc_python_out=. api/grpc/health_data.proto  # Python
```

## 功能示例

### 存储健康数据

```python
import requests

url = "http://localhost:8080/api/v1/health-data"
headers = {
    "Content-Type": "application/json",
    "X-User-ID": "user-uuid"
}
data = {
    "data_type": "heart_rate",
    "timestamp": "2023-07-01T12:00:00Z",
    "device_type": "apple_health",
    "value": 75,
    "unit": "bpm",
    "metadata": {}
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

### 获取中医体质分析

```python
import requests

url = "http://localhost:8080/api/v1/tcm/constitution"
headers = {
    "X-User-ID": "user-uuid"
}

response = requests.get(url, headers=headers)
print(response.json())
```

### 导入可穿戴设备数据

```python
import requests

url = "http://localhost:8080/api/v1/wearables/process"
headers = {
    "X-User-ID": "user-uuid"
}
files = {
    "file": ("export.xml", open("export.xml", "rb"), "application/xml")
}
data = {
    "device_type": "apple_health"
}

response = requests.post(url, headers=headers, data=data, files=files)
print(response.json())
```

## 项目目录结构

```
health-data-service/
├── api/                  # API定义
│   ├── grpc/             # gRPC API
│   └── rest/             # REST API模型定义
├── cmd/                  # 命令行入口
│   └── server/           # 服务器启动
├── config/               # 配置文件
├── deploy/               # 部署配置
│   ├── docker/           # Docker配置
│   ├── kubernetes/       # Kubernetes配置
│   └── prometheus/       # 监控配置
├── docs/                 # 文档
├── internal/             # 内部实现
│   ├── delivery/         # 传输层
│   │   ├── grpc/         # gRPC实现
│   │   └── rest/         # REST实现
│   ├── model/            # 数据模型
│   ├── repository/       # 数据访问
│   └── service/          # 业务逻辑
│       ├── analytics/    # 分析引擎
│       ├── blockchain/   # 区块链集成
│       └── parsers/      # 数据解析器
├── pkg/                  # 公共包
│   └── utils/            # 工具函数
├── test/                 # 测试
│   ├── integration/      # 集成测试
│   └── unit/             # 单元测试
├── .dockerignore         # Docker忽略文件
├── .env.example          # 环境变量示例
├── .gitignore            # Git忽略文件
├── Dockerfile            # Docker构建文件
├── README.md             # 项目说明
└── requirements.txt      # 依赖列表
```

## 开发贡献

1. Fork 代码库
2. 创建新的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

请确保提交前运行测试：
```bash
python -m pytest
```

## 最近更新功能

### 数据隐私与安全

- **区块链存证集成**：通过区块链技术确保健康数据的不可篡改性和真实性
- **零知识证明**：支持健康数据的隐私保护和选择性披露，允许用户控制共享健康数据的范围
- **数据安全加密**：采用RSA非对称加密确保数据传输和存储安全

### 中医体质分析

- **多模态数据融合**：集成望闻问切四诊数据，结合现代健康指标进行全面分析
- **个性化体质辨识**：基于传统中医理论，辨识九种常见体质类型
- **动态体质评估**：根据用户健康数据变化，动态调整体质评估结果
- **个性化调理建议**：根据体质特点，提供饮食、作息、运动等个性化调理建议

### 健康数据解析

- **多设备数据导入**：支持导入多种可穿戴设备数据
- **Apple Health导入**：解析Apple Health导出的XML健康数据
- **数据标准化处理**：统一不同数据源的健康数据格式
- **时间序列处理**：处理和分析健康数据的时间序列特性

### 数据分析与洞察

- **健康趋势分析**：识别健康数据的长期趋势变化
- **异常检测**：自动识别健康数据中的异常点
- **生活方式关联分析**：挖掘生活方式与健康指标的关联性
- **个性化健康洞察**：基于用户健康数据提供个性化洞察

## 许可证

版权所有 © 2024 索克生活 