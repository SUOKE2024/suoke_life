# 小艾智能体服务开发文档

## 概述

本文档提供小艾智能体服务的开发指南，包括环境搭建、代码结构、开发流程和最佳实践。

## 技术栈

- **Python**: 3.13.3
- **包管理**: UV (Python包管理器)
- **异步框架**: asyncio, aiohttp
- **API框架**: FastAPI
- **数据库**: PostgreSQL + Redis
- **AI/ML**: PyTorch, Transformers, ONNX
- **通信**: gRPC, HTTP
- **测试**: pytest, pytest-asyncio
- **代码质量**: ruff, black, mypy
- **容器化**: Docker
- **监控**: Prometheus, Grafana

## 环境搭建

### 1. 系统要求

- Python 3.13.3+
- UV包管理器
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (可选)

### 2. 安装UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. 克隆项目

```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life/services/agent-services/xiaoai-service
```

### 4. 环境配置

```bash
# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装核心依赖
uv pip install -e .

# 安装开发依赖
uv pip install -e ".[dev]"

# 安装AI依赖（可选，需要较大存储空间）
uv pip install -e ".[ai]"

# 安装所有依赖
uv pip install -e ".[all]"
```

### 5. 配置文件

复制配置模板并修改：

```bash
cp config/config.yaml.example config/config.yaml
cp .env.example .env
```

编辑配置文件：

```yaml
# config/config.yaml
app:
  name: "xiaoai-service"
  version: "1.0.0"
  debug: true
  log_level: "DEBUG"

database:
  host: "localhost"
  port: 5432
  name: "xiaoai_db"
  user: "xiaoai_user"
  password: "your_password"

redis:
  host: "localhost"
  port: 6379
  db: 0
  password: ""

ai_models:
  base_path: "./models"
  cache_size: 1000
  auto_unload_timeout: 3600
```

### 6. 数据库初始化

```bash
# 创建数据库
createdb xiaoai_db

# 运行数据库迁移
alembic upgrade head
```

### 7. 启动服务

```bash
# 开发模式启动
python -m xiaoai.main

# 或使用uvicorn
uvicorn xiaoai.api.app:app --reload --host 0.0.0.0 --port 8000
```

## 项目结构

```
xiaoai-service/
├── xiaoai/                     # 主要源代码
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── api/                    # API层
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI应用
│   │   ├── routes/             # API路由
│   │   │   ├── __init__.py
│   │   │   ├── diagnosis.py    # 诊断相关API
│   │   │   ├── sessions.py     # 会话管理API
│   │   │   ├── multimodal.py   # 多模态处理API
│   │   │   ├── recommendations.py # 建议API
│   │   │   ├── accessibility.py   # 无障碍API
│   │   │   └── health.py       # 健康检查API
│   │   ├── middleware/         # 中间件
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # 认证中间件
│   │   │   ├── logging.py      # 日志中间件
│   │   │   └── rate_limit.py   # 限流中间件
│   │   └── schemas/            # Pydantic模型
│   │       ├── __init__.py
│   │       ├── diagnosis.py
│   │       ├── session.py
│   │       └── common.py
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── five_diagnosis_coordinator.py  # 五诊协调器
│   │   ├── syndrome_analyzer.py           # 辨证分析器
│   │   ├── constitution_analyzer.py       # 体质分析器
│   │   ├── multimodal_processor.py        # 多模态处理器
│   │   ├── recommendation_engine.py       # 建议引擎
│   │   └── ai_model_manager.py            # AI模型管理器
│   ├── integration/            # 外部服务集成
│   │   ├── __init__.py
│   │   └── service_clients.py  # 服务客户端
│   ├── data/                   # 数据层
│   │   ├── __init__.py
│   │   ├── models.py           # 数据模型
│   │   └── repositories.py     # 数据仓库
│   ├── accessibility/          # 无障碍服务
│   │   ├── __init__.py
│   │   └── accessibility_service.py
│   ├── monitoring/             # 监控和健康检查
│   │   ├── __init__.py
│   │   └── health_checker.py
│   ├── config/                 # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── exceptions.py       # 自定义异常
│   │   ├── cache.py           # 缓存工具
│   │   └── logging.py         # 日志工具
│   └── cli.py                 # 命令行接口
├── tests/                     # 测试代码
│   ├── __init__.py
│   ├── unit/                  # 单元测试
│   │   ├── __init__.py
│   │   ├── test_five_diagnosis_coordinator.py
│   │   ├── test_syndrome_analyzer.py
│   │   ├── test_constitution_analyzer.py
│   │   ├── test_multimodal_processor.py
│   │   ├── test_recommendation_engine.py
│   │   └── test_ai_model_manager.py
│   ├── integration/           # 集成测试
│   │   ├── __init__.py
│   │   └── test_xiaoai_service_integration.py
│   ├── e2e/                   # 端到端测试
│   │   ├── __init__.py
│   │   └── test_api_endpoints.py
│   ├── fixtures/              # 测试数据
│   │   ├── __init__.py
│   │   ├── sample_data.py
│   │   └── mock_responses.py
│   └── conftest.py           # pytest配置
├── config/                   # 配置文件
│   ├── config.yaml          # 主配置文件
│   ├── config.yaml.example  # 配置模板
│   └── logging.yaml         # 日志配置
├── docs/                    # 文档
│   ├── api.md              # API文档
│   ├── development.md      # 开发文档
│   ├── deployment.md       # 部署文档
│   └── architecture.md     # 架构文档
├── scripts/                # 脚本文件
│   ├── setup.sh           # 环境搭建脚本
│   ├── test.sh            # 测试脚本
│   └── deploy.sh          # 部署脚本
├── migrations/             # 数据库迁移
│   └── alembic/
├── docker/                 # Docker配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
├── pyproject.toml         # 项目配置
├── uv.lock               # 依赖锁定文件
├── .env.example          # 环境变量模板
├── .gitignore
├── README.md
└── Makefile              # 构建脚本
```

## 开发流程

### 1. 分支管理

我们使用Git Flow工作流：

- `main`: 生产分支
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 热修复分支
- `release/*`: 发布分支

### 2. 功能开发流程

```bash
# 1. 从develop分支创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 开发功能
# ... 编写代码 ...

# 3. 运行测试
make test

# 4. 代码质量检查
make lint

# 5. 提交代码
git add .
git commit -m "feat: add new feature"

# 6. 推送分支
git push origin feature/new-feature

# 7. 创建Pull Request
# 在GitHub上创建PR，请求合并到develop分支
```

### 3. 代码规范

#### 3.1 Python代码风格

我们使用以下工具确保代码质量：

- **ruff**: 代码检查和格式化
- **black**: 代码格式化
- **isort**: 导入排序
- **mypy**: 类型检查

```bash
# 运行所有检查
make lint

# 自动修复格式问题
make format

# 类型检查
make typecheck
```

#### 3.2 提交信息规范

使用Conventional Commits规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(diagnosis): add syndrome analysis algorithm

Implement traditional Chinese medicine syndrome differentiation
algorithm based on eight principles.

Closes #123
```

### 4. 测试策略

#### 4.1 测试分类

- **单元测试**: 测试单个函数或类
- **集成测试**: 测试组件间的交互
- **端到端测试**: 测试完整的用户场景

#### 4.2 运行测试

```bash
# 运行所有测试
make test

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/unit/test_syndrome_analyzer.py

# 运行带覆盖率的测试
pytest --cov=xiaoai tests/

# 运行性能测试
pytest --benchmark-only tests/
```

#### 4.3 测试编写指南

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestSyndromeAnalyzer:
    """辨证分析器测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """创建分析器实例"""
        return SyndromeAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_syndrome_success(self, analyzer):
        """测试成功的辨证分析"""
        # 准备测试数据
        diagnosis_results = [
            # ... 测试数据 ...
        ]
        
        # 执行测试
        result = analyzer.analyze_syndrome(diagnosis_results)
        
        # 验证结果
        assert result is not None
        assert result.primary_syndromes is not None
        assert result.overall_confidence > 0.0
    
    def test_analyze_syndrome_invalid_input(self, analyzer):
        """测试无效输入的处理"""
        with pytest.raises(ValueError):
            analyzer.analyze_syndrome([])
```

## 核心组件开发

### 1. 五诊协调器

五诊协调器是系统的核心组件，负责协调望、闻、问、切四诊的结果。

```python
from xiaoai.core.five_diagnosis_coordinator import FiveDiagnosisCoordinator

# 创建协调器实例
coordinator = FiveDiagnosisCoordinator()

# 初始化
await coordinator.initialize()

# 开始诊断流程
diagnosis_results = await coordinator.start_diagnosis_process(
    user_id="user_123",
    session_id="session_456",
    diagnosis_data={
        DiagnosisType.LOOKING: {"tongue_image": "..."},
        DiagnosisType.INQUIRY: {"chief_complaint": "..."}
    }
)
```

### 2. 辨证分析器

实现中医辨证分析算法：

```python
from xiaoai.core.syndrome_analyzer import SyndromeAnalyzer

analyzer = SyndromeAnalyzer()

# 执行辨证分析
syndrome_result = analyzer.analyze_syndrome(diagnosis_results)

print(f"主要证型: {syndrome_result.primary_syndromes}")
print(f"置信度: {syndrome_result.overall_confidence}")
```

### 3. 多模态处理器

处理文本、图像、音频等多种模态数据：

```python
from xiaoai.core.multimodal_processor import MultimodalProcessor, ModalityType

processor = MultimodalProcessor()
await processor.initialize()

# 处理多模态数据
inputs = [
    {
        "modality_type": ModalityType.TEXT,
        "data": "患者主诉症状",
        "metadata": {"language": "zh"}
    },
    {
        "modality_type": ModalityType.IMAGE,
        "data": image_bytes,
        "metadata": {"image_type": "tongue"}
    }
]

results = await processor.process_batch(inputs)
```

### 4. AI模型管理器

管理和优化AI模型的加载、调用和缓存：

```python
from xiaoai.core.ai_model_manager import get_model_manager, predict

# 获取模型管理器
model_manager = await get_model_manager()

# 预加载模型
await model_manager.preload_models(["syndrome_classifier", "constitution_analyzer"])

# 使用模型进行预测
result = await predict("syndrome_classifier", "输入文本", use_cache=True)

# 批量预测
results = await model_manager.batch_predict("model_name", ["输入1", "输入2"])
```

## 配置管理

### 1. 配置文件结构

```yaml
# config/config.yaml
app:
  name: "xiaoai-service"
  version: "1.0.0"
  debug: false
  log_level: "INFO"
  cors_origins: ["*"]

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

database:
  host: "${DB_HOST:localhost}"
  port: "${DB_PORT:5432}"
  name: "${DB_NAME:xiaoai_db}"
  user: "${DB_USER:xiaoai_user}"
  password: "${DB_PASSWORD}"
  pool_size: 10
  max_overflow: 20

redis:
  host: "${REDIS_HOST:localhost}"
  port: "${REDIS_PORT:6379}"
  db: "${REDIS_DB:0}"
  password: "${REDIS_PASSWORD:}"
  max_connections: 100

ai_models:
  base_path: "./models"
  cache_size: 1000
  auto_unload_timeout: 3600
  models:
    syndrome_classifier:
      path: "bert-base-chinese"
      task: "classification"
      device: "cpu"
    constitution_analyzer:
      path: "constitution-bert"
      task: "classification"
      device: "cpu"

external_services:
  look_service:
    url: "http://look-service:8001"
    timeout: 30
    retry_count: 3
  listen_service:
    url: "http://listen-service:8002"
    timeout: 30
    retry_count: 3

monitoring:
  enable_metrics: true
  metrics_port: 9090
  health_check_interval: 30
```

### 2. 环境变量

```bash
# .env
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=xiaoai_db
DB_USER=xiaoai_user
DB_PASSWORD=your_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 外部服务
LOOK_SERVICE_URL=http://look-service:8001
LISTEN_SERVICE_URL=http://listen-service:8002
INQUIRY_SERVICE_URL=http://inquiry-service:8003
PALPATION_SERVICE_URL=http://palpation-service:8004

# AI模型配置
AI_MODELS_PATH=./models
HUGGINGFACE_TOKEN=your_token

# 监控配置
PROMETHEUS_ENABLED=true
GRAFANA_URL=http://grafana:3000
```

### 3. 配置加载

```python
from xiaoai.config.settings import get_settings

# 获取配置
settings = get_settings()

# 使用配置
database_url = f"postgresql://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port}/{settings.database.name}"
```

## 数据库设计

### 1. 数据模型

```python
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DiagnosisSession(Base):
    """诊断会话表"""
    __tablename__ = "diagnosis_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    metadata = Column(JSON)

class DiagnosisResult(Base):
    """诊断结果表"""
    __tablename__ = "diagnosis_results"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    diagnosis_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    confidence = Column(Float)
    features = Column(JSON)
    raw_result = Column(JSON)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, nullable=False)

class SyndromeAnalysis(Base):
    """辨证分析表"""
    __tablename__ = "syndrome_analyses"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    primary_syndromes = Column(JSON)
    secondary_syndromes = Column(JSON)
    overall_confidence = Column(Float)
    analysis_method = Column(String)
    created_at = Column(DateTime, nullable=False)
```

### 2. 数据库迁移

```bash
# 创建迁移文件
alembic revision --autogenerate -m "Add diagnosis tables"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 监控和日志

### 1. 日志配置

```python
import structlog
from xiaoai.utils.logging import setup_logging

# 设置日志
setup_logging()

# 使用结构化日志
logger = structlog.get_logger(__name__)

logger.info("诊断开始", user_id="user_123", session_id="session_456")
logger.error("诊断失败", error="模型不可用", user_id="user_123")
```

### 2. 性能监控

```python
from xiaoai.monitoring.health_checker import HealthChecker
import time

# 创建健康检查器
health_checker = HealthChecker()
await health_checker.initialize()

# 执行健康检查
health_report = await health_checker.check_health()

# 获取性能指标
metrics = await health_checker.get_metrics()
```

### 3. Prometheus指标

```python
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
diagnosis_requests = Counter('diagnosis_requests_total', 'Total diagnosis requests', ['user_id', 'diagnosis_type'])
diagnosis_duration = Histogram('diagnosis_duration_seconds', 'Diagnosis processing time')
active_sessions = Gauge('active_sessions', 'Number of active diagnosis sessions')

# 使用指标
diagnosis_requests.labels(user_id="user_123", diagnosis_type="looking").inc()
with diagnosis_duration.time():
    # 执行诊断逻辑
    pass
active_sessions.set(len(coordinator.active_sessions))
```

## 部署和运维

### 1. Docker部署

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装UV
RUN pip install uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装Python依赖
RUN uv pip install --system -e .

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "xiaoai.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  xiaoai-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: xiaoai_db
      POSTGRES_USER: xiaoai_user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  grafana_data:
```

### 3. Kubernetes部署

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xiaoai-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: xiaoai-service
  template:
    metadata:
      labels:
        app: xiaoai-service
    spec:
      containers:
      - name: xiaoai-service
        image: xiaoai-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: REDIS_HOST
          value: "redis-service"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 最佳实践

### 1. 代码组织

- 使用清晰的模块结构
- 遵循单一职责原则
- 使用依赖注入
- 编写可测试的代码

### 2. 异步编程

```python
import asyncio
from typing import List

async def process_diagnosis_batch(diagnosis_requests: List[DiagnosisRequest]) -> List[DiagnosisResult]:
    """批量处理诊断请求"""
    tasks = []
    for request in diagnosis_requests:
        task = asyncio.create_task(process_single_diagnosis(request))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理异常
    valid_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error("诊断处理失败", error=str(result))
        else:
            valid_results.append(result)
    
    return valid_results
```

### 3. 错误处理

```python
from xiaoai.utils.exceptions import DiagnosisError, ModelError

async def safe_model_predict(model_name: str, input_data: str) -> str:
    """安全的模型预测"""
    try:
        result = await predict(model_name, input_data)
        return result
    except ModelError as e:
        logger.error("模型预测失败", model=model_name, error=str(e))
        # 使用备用策略
        return await fallback_predict(input_data)
    except Exception as e:
        logger.error("未知错误", error=str(e))
        raise DiagnosisError(f"预测失败: {e}")
```

### 4. 性能优化

```python
from functools import lru_cache
from xiaoai.utils.cache import CacheManager

# 使用缓存
cache_manager = CacheManager()

@lru_cache(maxsize=1000)
def expensive_computation(input_data: str) -> str:
    """昂贵的计算操作"""
    # 复杂计算逻辑
    return result

async def cached_predict(model_name: str, input_data: str) -> str:
    """带缓存的预测"""
    cache_key = f"{model_name}:{hash(input_data)}"
    
    # 尝试从缓存获取
    cached_result = await cache_manager.get(cache_key)
    if cached_result:
        return cached_result
    
    # 执行预测
    result = await predict(model_name, input_data)
    
    # 存储到缓存
    await cache_manager.set(cache_key, result, ttl=3600)
    
    return result
```

## 故障排查

### 1. 常见问题

#### 问题1: 模型加载失败
```
错误: ModelError: 无法加载模型 'syndrome_classifier'
```

解决方案：
1. 检查模型文件是否存在
2. 验证模型路径配置
3. 确认有足够的内存
4. 检查模型格式是否正确

#### 问题2: 数据库连接失败
```
错误: asyncpg.exceptions.ConnectionDoesNotExistError
```

解决方案：
1. 检查数据库服务是否运行
2. 验证连接配置
3. 确认网络连通性
4. 检查用户权限

#### 问题3: Redis连接超时
```
错误: redis.exceptions.TimeoutError
```

解决方案：
1. 检查Redis服务状态
2. 调整连接超时设置
3. 检查网络延迟
4. 优化Redis配置

### 2. 调试技巧

```python
import logging
import pdb

# 启用调试日志
logging.getLogger('xiaoai').setLevel(logging.DEBUG)

# 使用断点调试
async def debug_diagnosis(diagnosis_data):
    pdb.set_trace()  # 设置断点
    result = await process_diagnosis(diagnosis_data)
    return result

# 使用性能分析
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 执行需要分析的代码
    result = expensive_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

## 贡献指南

### 1. 提交代码

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 确保所有测试通过
5. 提交Pull Request

### 2. 代码审查

- 代码风格符合规范
- 有充分的测试覆盖
- 文档更新完整
- 性能影响可接受

### 3. 发布流程

1. 更新版本号
2. 更新CHANGELOG
3. 创建发布分支
4. 执行完整测试
5. 合并到main分支
6. 创建Git标签
7. 部署到生产环境

## 联系方式

- **开发团队**: dev@suoke.life
- **技术支持**: tech-support@suoke.life
- **GitHub**: https://github.com/SUOKE2024/suoke_life
- **文档**: https://docs.suoke.life