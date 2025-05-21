# 索儿智能体服务 (Soer Service)

## 服务简介

索儿智能体服务是索克生活APP LIFE频道的核心智能体，作为健康管理引擎，负责为用户提供生活（健康）管理、陪伴等服务，整合用户饮食起居、实时感知（通过手机、智能手表、运动装备、医疗装备等）数据。本服务采用Python编写，运行在suoke-ai-np节点池上，通过gRPC协议与其他服务通信。

## 核心功能

- **健康生活习惯培养与行为干预**：基于中医体质和现代健康理论，为用户定制饮食、运动、睡眠等生活方式指导
- **多设备传感器数据整合与健康趋势分析**：集成来自智能手表、手机、可穿戴设备的多源异构生物数据
- **环境与情绪智能感知与动态健康建议**：根据环境、天气、情绪状态提供实时健康指导
- **个性化养生计划生成与执行跟踪**：结合节气、体质特点制定养生方案并跟踪执行情况
- **身心健康陪伴与情感支持**：提供压力管理、情绪疏导、心理健康辅导服务
- **全生命周期健康管理**：从亚健康预防到慢病管理的全套健康监测与干预方案

## 技术架构

- **开发语言**：Python 3.10+
- **核心框架**：FastAPI, gRPC, LangChain, TensorFlow, PyTorch
- **AI模型**：
  - 健康行为预测模型：基于用户历史行为与生物数据预测健康趋势
  - 情绪识别模型：融合语音、文本及生理信号的多模态情绪识别
  - 营养分析引擎：基于中医五味理论的食物推荐系统
  - 时间序列分析模型：用于生物指标异常检测和趋势预测
- **数据存储**：
  - PostgreSQL：用户档案和基础健康数据
  - TimescaleDB：传感器时序数据高效存储与分析
  - MongoDB：非结构化健康知识和分析结果
  - Redis：实时数据缓存与会话状态管理
- **通信方式**：
  - gRPC：内部服务高效通信
  - REST API：与前端及第三方健康设备API交互
  - WebSocket：实时传感器数据流接收

## 项目结构

```
soer-service/
├── api/               # API定义
│   ├── rest/          # REST接口定义
│   └── grpc/          # gRPC接口定义
├── cmd/               # 服务入口点
├── config/            # 配置文件
├── deploy/            # 部署配置
│   ├── grafana/       # Grafana监控配置
│   ├── kubernetes/    # Kubernetes部署配置 
│   └── prometheus/    # Prometheus监控配置
├── internal/          # 内部实现
│   ├── lifecycle/     # 全生命周期健康管理
│   ├── nutrition/     # 膳食营养引擎
│   ├── delivery/      # 接口实现层
│   ├── agent/         # 智能体核心逻辑
│   ├── integration/   # 外部集成层
│   └── repository/    # 数据存储层
├── integration/       # 集成层
│   └── western/       # 西医预防医学集成
├── pkg/               # 公共包
│   └── utils/         # 工具函数
└── test/              # 测试代码
    ├── integration/   # 集成测试
    ├── performance/   # 性能测试
    └── unit/          # 单元测试
```

## 环境要求

- Python 3.10+
- CUDA 11.4+ (用于GPU加速)
- PostgreSQL 16+
- TimescaleDB (PostgreSQL扩展)
- MongoDB 6.0+
- Redis 7.0+

## 安装与运行

### 通过 Docker 运行

1. 构建 Docker 镜像
```bash
docker-compose build
```

2. 启动服务
```bash
docker-compose up -d
```

### 手动安装

1. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行服务
```bash
python -m cmd.server
```

## Kubernetes部署

```bash
# 创建ConfigMap和Secret
kubectl create namespace suoke-ai-np
kubectl apply -f deploy/kubernetes/soer-service.yaml
```

## API接口

### 主要gRPC接口

- `GenerateHealthPlan`: 生成个性化健康计划
- `GetLifestyleRecommendation`: 获取生活方式建议
- `AnalyzeSensorData`: 分析传感器数据
- `TrackNutrition`: 追踪并分析用户营养摄入
- `DetectAbnormalPattern`: 检测异常健康模式
- `PredictHealthTrend`: 预测健康趋势

### 示例代码

```python
import grpc
from api.grpc import soer_service_pb2, soer_service_pb2_grpc

# 创建连接
channel = grpc.insecure_channel('localhost:50054')
stub = soer_service_pb2_grpc.SoerServiceStub(channel)

# 请求健康计划
request = soer_service_pb2.HealthPlanRequest(
    user_id="user123",
    constitution_type="阳虚质",
    health_goals=["改善睡眠", "增强体质"],
    preferences={
        "diet_restrictions": ["无麸质", "少油"],
        "exercise_preferences": ["瑜伽", "散步"]
    },
    current_season="冬季"
)

# 获取响应
response = stub.GenerateHealthPlan(request)
print(f"健康计划ID: {response.plan_id}")
print(f"饮食建议: {response.diet_recommendations}")
print(f"运动建议: {response.exercise_recommendations}")
print(f"作息建议: {response.lifestyle_recommendations}")
```

### REST API接口

服务同时提供REST API接口，主要包括：

- `GET /health`：服务健康检查
- `POST /health-plans/`：创建健康计划
- `GET /health-plans/{plan_id}`：获取健康计划详情
- `POST /health-plans/progress`：更新健康计划进度
- `POST /emotion/analyze`：分析情绪状态
- `POST /emotion/analyze/text`：分析文本情绪
- `POST /emotion/analyze/voice`：分析语音情绪
- `GET /emotion/mappings/tcm`：获取中医情志理论映射
- `GET /emotion/interventions`：获取情绪干预策略

完整的API文档可通过访问 `http://localhost:8054/docs` 获取。

## 传感器数据集成

索儿服务支持多种传感器数据源：

- **穿戴设备**：Apple Watch, Samsung Galaxy Watch, Fitbit, Oura Ring等
- **健康App**：Apple Health, Google Fit, Samsung Health
- **专业医疗设备**：血压计、血糖仪、心电图仪等
- **智能家居设备**：智能体重秤、睡眠监测器、智能空气检测仪等
- **手机内置传感器**：加速度计、陀螺仪、GPS、光感传感器等

### 数据集成示例

```python
# 集成Apple Health数据
from pkg.utils.health_data_connectors import AppleHealthConnector

connector = AppleHealthConnector(api_key="your_api_key")
health_data = connector.fetch_recent_data(
    user_id="user123",
    data_types=["心率", "步数", "睡眠"],
    time_range_days=7
)

# 分析数据
from internal.lifecycle.health_analyzer import HealthDataAnalyzer

analyzer = HealthDataAnalyzer()
insights = analyzer.analyze(health_data)
print(f"健康见解: {insights}")
```

## 监控与可观测性

### 指标监控

服务提供全面的Prometheus指标监控，包括：

- **API请求指标**：请求计数、响应时间、错误率等
- **服务指标**：健康计划生成、情绪分析等功能的使用情况
- **资源指标**：数据库连接、缓存使用、内存消耗等
- **LLM指标**：模型调用次数、令牌使用量、响应时间等

主要指标访问点：
- Prometheus 指标: http://localhost:9098/metrics
- Grafana 仪表盘: http://localhost:3008

### 日志

服务使用结构化日志记录，支持不同级别的日志和灵活的输出格式。主要日志文件：
- 应用日志: `logs/soer-service.log`
- 访问日志: `logs/access.log`
- 错误日志: `logs/error.log`

### 分布式追踪

服务集成了OpenTelemetry分布式追踪，可以追踪请求在不同服务间的传播路径和性能指标。
追踪数据可以通过以下方式查看：
- Jaeger UI: http://localhost:16686
- Zipkin: http://localhost:9411

## 测试与质量保证

### 测试策略

服务采用多层次测试策略，确保代码质量和功能正确性：

- **单元测试**：测试各个组件的独立功能
- **集成测试**：测试组件间的交互和外部依赖
- **性能测试**：测试服务在不同负载下的表现
- **端到端测试**：模拟真实用户场景的完整功能测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest test/unit/

# 运行集成测试
pytest test/integration/

# 运行性能测试
python test/performance/load_test.py --requests 1000 --concurrency 50
```

### 测试覆盖率

执行测试覆盖率分析：

```bash
pytest --cov=internal --cov=pkg --cov-report=html
```

生成的覆盖率报告位于`htmlcov/index.html`。

## 集成服务

- **xiaoai-service**: 小艾服务，提供四诊协调
- **med-knowledge**: 医学知识库服务
- **rag-service**: 检索增强生成服务
- **streaming-service**: 流式数据处理服务
- **look-service**: 望诊服务，提供可视化健康分析
- **listen-service**: 闻诊服务，提供语音情绪分析

## 开发指南

### 添加新传感器数据源

1. 在 `internal/repository/sensor_data` 目录下创建新的数据源连接器
2. 实现 `ISensorDataConnector` 接口
3. 在 `config/sensors.yaml` 中添加传感器配置
4. 在 `internal/repository/sensor_registry.py` 中注册新数据源

### 添加新的健康分析算法

1. 在 `internal/lifecycle/algorithms` 目录下创建新算法
2. 在 `config/algorithms.yaml` 中添加算法配置
3. 在 `internal/lifecycle/health_analyzer.py` 中注册新算法

### 添加新的营养分析组件

1. 在 `internal/nutrition/analyzers` 目录下创建新组件
2. 在 `config/nutrition.yaml` 中添加配置
3. 在 `internal/nutrition/nutrition_engine.py` 中集成新组件

### 代码风格与质量

我们使用以下工具确保代码质量：

- **pylint**: 静态代码分析
- **black**: 代码格式化
- **isort**: 导入语句排序
- **mypy**: 类型检查

提交代码前请运行以下命令检查代码质量：

```bash
# 格式化代码
black . 
isort .

# 运行代码分析
pylint internal pkg

# 类型检查
mypy internal pkg
```

## 故障排除

### 常见问题

- **服务启动失败**：检查配置文件和环境变量设置
- **数据库连接错误**：确认数据库服务可访问，并验证连接凭据
- **LLM API调用失败**：检查API密钥和网络连接
- **内存使用过高**：调整并发限制和缓存设置

### 日志分析

使用以下命令查看最近的错误日志：

```bash
tail -f logs/error.log | grep ERROR
```

### 性能优化

如果遇到性能问题，可以尝试：

1. 增加缓存使用，减少重复计算
2. 优化数据库查询和索引
3. 启用请求批处理
4. 增加服务实例水平扩展
5. 使用异步处理非关键路径任务

## 许可证

本项目采用 MIT 许可证 - 详情参见 [LICENSE](LICENSE) 文件