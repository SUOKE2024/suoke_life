# 索克生活平台 - 通用组件库

## 概述

本目录包含索克生活（Suoke Life）健康管理平台的通用组件库，为平台的四个智能体（小艾、小克、老克、索儿）提供统一的基础设施支持。这些组件实现了现代微服务架构所需的核心功能，包括服务网格、API文档生成、图数据库、测试框架等。

## 核心特性

- 🕸️ **服务网格支持** - 集成Istio、Linkerd、Envoy
- 📚 **API文档生成** - 自动生成OpenAPI/Swagger文档
- 🧪 **测试框架** - 统一的测试工具集
- 🔒 **安全组件** - 认证、授权、加密
- 📊 **可观测性** - 监控、日志、链路追踪
- 🚀 **性能优化** - 缓存、异步处理
- 📨 **消息队列** - Kafka、RabbitMQ支持
- ⚙️ **配置管理** - 统一配置中心

## 目录结构

```
services/common/
├── api-docs/              # API文档生成
│   ├── openapi_generator.py    # OpenAPI文档生成器
│   ├── doc_decorators.py       # API文档装饰器
│   └── swagger_ui.py           # Swagger UI服务器
├── service-mesh/          # 服务网格
│   ├── mesh_manager.py         # 服务网格管理器
│   ├── istio_client.py         # Istio客户端
│   ├── linkerd_client.py       # Linkerd客户端
│   └── envoy_config.py         # Envoy配置管理
├── testing/               # 测试框架
│   └── test_framework.py       # 统一测试框架
├── messaging/             # 消息队列
│   ├── message_queue.py        # 消息队列抽象接口
│   ├── kafka_client.py         # Kafka客户端
│   └── rabbitmq_client.py      # RabbitMQ客户端
├── config/                # 配置管理
│   ├── config_manager.py       # 配置管理器
│   └── config_center.py        # 配置中心
├── security/              # 安全组件
│   ├── encryption.py           # 加密管理
│   └── auth.py                 # 认证授权
├── observability/         # 可观测性
│   ├── metrics.py              # 指标收集
│   ├── logging.py              # 日志管理
│   └── tracing.py              # 链路追踪
├── examples/              # 使用示例
│   └── service_mesh_example.py # 服务网格示例
└── requirements.txt       # 依赖包列表
```

## 快速开始

### 1. 安装依赖

```bash
cd services/common
pip install -r requirements.txt
```

### 2. 运行示例

```bash
python examples/service_mesh_example.py
```

## 功能模块详解

### 🕸️ 服务网格 (Service Mesh)

服务网格模块提供了对Istio、Linkerd和Envoy的完整支持，实现微服务间的通信管理、流量控制、安全策略等功能。

#### 主要功能

- **流量管理**: 负载均衡、金丝雀发布、蓝绿部署
- **安全策略**: mTLS、访问控制、身份验证
- **可观测性**: 分布式追踪、指标收集、日志聚合
- **故障处理**: 熔断器、重试、超时控制

#### 使用示例

```python
from service_mesh.mesh_manager import ServiceMeshManager, TrafficPolicyType

# 创建服务网格管理器
mesh_manager = ServiceMeshManager()

# 配置金丝雀发布
await mesh_manager.configure_traffic_policy(
    service_name="xiaoai-service",
    policy_type=TrafficPolicyType.CANARY,
    config={
        "stable_version": "v1",
        "canary_version": "v2", 
        "canary_weight": 10
    }
)
```

### 📚 API文档生成

自动生成符合OpenAPI 3.0规范的API文档，支持Swagger UI可视化界面。

#### 主要功能

- **自动文档生成**: 从代码注释和装饰器生成文档
- **多格式输出**: 支持JSON、YAML格式
- **Swagger UI**: 提供交互式API文档界面
- **健康管理专用**: 预定义健康管理相关的数据模型

#### 使用示例

```python
from api_docs.doc_decorators import api_doc, post_api, success_response

@api_doc(
    summary="健康评估",
    description="基于中医辨证论治进行个性化健康评估",
    tags=["健康评估"]
)
@post_api("/api/v1/health/assessment")
@success_response("评估结果", {
    "syndrome_type": "证型",
    "health_score": "健康评分"
})
async def health_assessment(user_id: str):
    """健康评估接口"""
    pass
```



### 🧪 测试框架

统一的测试框架，支持单元测试、集成测试、性能测试等多种测试类型。

#### 主要功能

- **多测试类型**: 单元、集成、性能、端到端测试
- **异步支持**: 支持异步测试函数
- **并行执行**: 支持测试用例并行执行
- **详细报告**: 生成详细的测试报告

#### 使用示例

```python
from testing.test_framework import get_test_framework, TestType

test_framework = get_test_framework()

@test_framework.test_case(
    name="健康评估API测试",
    description="测试健康评估API的功能",
    test_type=TestType.INTEGRATION
)
async def test_health_assessment():
    """测试健康评估功能"""
    assert True, "健康评估API正常工作"
    return {"status": "passed"}

# 运行所有测试
results = await test_framework.run_all_tests()
```

## 索克生活平台专用功能

### 智能体服务支持

为四个智能体（小艾、小克、老克、索儿）提供专门的基础设施支持：

- **小艾 (Xiaoai)**: 健康咨询和初步诊断
- **小克 (Xiaoke)**: 个性化健康方案制定
- **老克 (Laoke)**: 中医养生指导
- **索儿 (Soer)**: 健康数据分析和预测

### 中医辨证论治数字化

- **证型识别**: 基于症状的证型自动识别
- **方剂推荐**: 个性化中药方剂推荐
- **养生建议**: 基于体质的养生方案
- **疗效追踪**: 治疗效果的持续监测

### 健康数据管理

- **多模态数据**: 支持文本、图像、音频等多种数据类型
- **隐私保护**: 零知识证明的健康数据验证
- **区块链存储**: 不可篡改的健康记录
- **智能分析**: AI驱动的健康趋势分析

## 配置说明

### 环境变量

```bash
# 图数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# 服务网格配置
ISTIO_NAMESPACE=istio-system
LINKERD_NAMESPACE=linkerd

# API文档配置
SWAGGER_UI_PORT=8081
API_DOCS_TITLE=索克生活API文档
```

### 配置文件

```yaml
# config.yaml
service_mesh:
  type: istio
  namespace: suoke-life
  gateway:
    name: suoke-gateway
    hosts:
      - "*.suoke.local"

graph_database:
  type: neo4j
  uri: bolt://localhost:7687
  pool_size: 10

api_docs:
  title: 索克生活健康管理平台API
  version: 1.0.0
  swagger_ui:
    enabled: true
    port: 8081
```

## 性能优化

### 连接池管理

所有数据库客户端都使用连接池来优化性能：

```python
# Neo4j连接池配置
neo4j_client = Neo4jClient(
    uri="bolt://localhost:7687",
    max_connection_pool_size=50,
    connection_acquisition_timeout=30
)
```

### 异步处理

所有I/O操作都使用异步处理，提高并发性能：

```python
# 异步批量操作
async def batch_create_nodes(nodes_data):
    tasks = [
        graph_db.create_node(labels=data["labels"], properties=data["props"])
        for data in nodes_data
    ]
    return await asyncio.gather(*tasks)
```

### 缓存策略

使用多级缓存提高查询性能：

```python
from cachetools import TTLCache

# 内存缓存
cache = TTLCache(maxsize=1000, ttl=300)

@cached(cache)
async def get_user_health_profile(user_id: str):
    """获取用户健康档案（带缓存）"""
    return await graph_db.get_user_profile(user_id)
```

## 监控和可观测性

### 指标收集

```python
from prometheus_client import Counter, Histogram

# 定义指标
api_requests_total = Counter('api_requests_total', 'API请求总数', ['method', 'endpoint'])
api_request_duration = Histogram('api_request_duration_seconds', 'API请求耗时')

# 使用指标
@api_request_duration.time()
async def health_assessment(user_id: str):
    api_requests_total.labels(method='POST', endpoint='/health/assessment').inc()
    # 业务逻辑
```

### 分布式追踪

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_health_data(user_id: str):
    with tracer.start_as_current_span("process_health_data") as span:
        span.set_attribute("user_id", user_id)
        # 处理逻辑
```

## 安全考虑

### 数据加密

```python
from cryptography.fernet import Fernet

# 敏感数据加密
cipher_suite = Fernet(encryption_key)
encrypted_data = cipher_suite.encrypt(sensitive_data.encode())
```

### 访问控制

```python
from functools import wraps

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 检查权限
            if not check_permission(permission):
                raise PermissionError("权限不足")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@require_permission("health.assessment.read")
async def get_health_assessment(user_id: str):
    """获取健康评估结果"""
    pass
```

## 故障处理

### 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def reliable_api_call():
    """可靠的API调用"""
    # 可能失败的操作
    pass
```

### 熔断器

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("熔断器开启")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise e
```

## 贡献指南

### 代码规范

- 使用Python 3.8+
- 遵循PEP 8代码风格
- 使用类型提示
- 编写详细的中文注释
- 使用异步编程模式

### 测试要求

- 单元测试覆盖率 > 80%
- 集成测试覆盖核心功能
- 性能测试验证关键指标

### 提交流程

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request
5. 代码审查
6. 合并到主分支

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目主页: https://github.com/SUOKE2024/suoke_life
- 文档站点: https://github.com/SUOKE2024/suoke_life/tree/main/docs
- 技术支持: song.xu@icloud.com

---

**索克生活平台** - 将中医智慧数字化，融入现代生活场景 🌿 