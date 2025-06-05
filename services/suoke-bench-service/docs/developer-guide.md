# SuokeBench 开发者指南

## 快速开始

### 环境要求

- Python 3.11+
- Docker & Docker Compose
- Git
- uv (Python 包管理器)

### 本地开发环境搭建

#### 1. 克隆项目

```bash
git clone <repository-url>
cd suoke_life/services/suoke-bench-service
```

#### 2. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync

# 或使用 pip
pip install -r requirements.txt
```

#### 3. 启动开发环境

```bash
# 启动依赖服务
docker-compose -f deploy/docker-compose.yml up -d redis postgresql

# 启动开发服务器
make dev
```

#### 4. 验证安装

```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs
```

## 项目结构

```
suoke-bench-service/
├── cmd/                    # 命令行入口
│   └── server/            # 服务器启动
├── internal/              # 内部模块
│   ├── benchmark/         # 基准测试引擎
│   ├── evaluation/        # 评估分析
│   ├── metrics/          # 指标计算
│   ├── observability/    # 监控观测
│   ├── resilience/       # 容错恢复
│   └── suokebench/       # 核心框架
├── api/                   # API 定义
│   └── grpc/             # gRPC 协议
├── config/               # 配置文件
├── data/                 # 数据文件
├── deploy/               # 部署配置
├── docs/                 # 文档
├── examples/             # 示例代码
├── pkg/                  # 公共包
├── test/                 # 测试代码
└── suoke_bench_service/  # Python 包
```

## 核心概念

### 1. 基准测试 (Benchmark)

基准测试是评估模型性能的标准化测试。每个基准测试包含：

- **测试数据集**: 标准化的输入数据
- **评估指标**: 性能衡量标准
- **执行配置**: 测试参数设置

```python
from internal.benchmark.benchmark_service import BenchmarkExecutor

# 创建基准测试执行器
executor = BenchmarkExecutor(config)

# 提交测试任务
task_id = await executor.submit_benchmark(
    benchmark_id="sentiment-analysis",
    model_id="bert-base",
    model_version="v1.0",
    test_data=test_samples,
    config={"batch_size": 32}
)
```

### 2. 模型接口 (Model Interface)

统一的模型接口抽象，支持多种模型框架：

```python
from internal.benchmark.model_interface import ModelInterface

class CustomModel(ModelInterface):
    def __init__(self, model_config):
        self.model = load_model(model_config)
    
    async def predict_batch(self, inputs):
        predictions = []
        for input_data in inputs:
            result = self.model.predict(input_data)
            predictions.append(ModelPrediction(
                input_data=input_data,
                prediction=result,
                confidence=0.95,
                latency=100.0
            ))
        return predictions
```

### 3. 评估指标 (Metrics)

支持多种评估指标的计算：

```python
from internal.metrics.calculator import MetricsCalculator

calculator = MetricsCalculator()

# 计算分类指标
metrics = calculator.calculate_classification_metrics(
    predictions=predictions,
    ground_truth=labels
)

# 计算中医特色指标
tcm_metrics = calculator.calculate_tcm_metrics(
    predictions=tcm_predictions,
    ground_truth=tcm_labels
)
```

## 开发工作流

### 1. 功能开发

#### 创建新的基准测试

1. 定义基准测试配置：

```yaml
# config/benchmarks/new_benchmark.yaml
name: "新基准测试"
description: "测试描述"
dataset:
  path: "data/new_benchmark_dataset.json"
  format: "json"
metrics:
  - accuracy
  - precision
  - recall
  - f1
config:
  batch_size: 32
  timeout: 300
```

2. 实现评估逻辑：

```python
# internal/evaluation/new_benchmark_evaluator.py
from .base_evaluator import BaseEvaluator

class NewBenchmarkEvaluator(BaseEvaluator):
    def evaluate(self, predictions, ground_truth):
        # 实现具体的评估逻辑
        return metrics
```

3. 注册基准测试：

```python
# internal/suokebench/registry.py
from internal.evaluation.new_benchmark_evaluator import NewBenchmarkEvaluator

BENCHMARK_REGISTRY = {
    "new_benchmark": NewBenchmarkEvaluator,
    # ... 其他基准测试
}
```

#### 添加新的模型支持

1. 实现模型接口：

```python
# internal/benchmark/models/new_model.py
from ..model_interface import ModelInterface

class NewModelInterface(ModelInterface):
    def __init__(self, config):
        # 初始化模型
        pass
    
    async def predict_batch(self, inputs):
        # 实现批量预测
        pass
```

2. 注册模型类型：

```python
# internal/benchmark/model_registry.py
from .models.new_model import NewModelInterface

MODEL_TYPES = {
    "new_model_type": NewModelInterface,
    # ... 其他模型类型
}
```

### 2. 测试开发

#### 单元测试

```python
# test/test_new_feature.py
import pytest
from internal.benchmark.new_feature import NewFeature

class TestNewFeature:
    def test_basic_functionality(self):
        feature = NewFeature()
        result = feature.process("test_input")
        assert result == "expected_output"
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        feature = NewFeature()
        result = await feature.async_process("test_input")
        assert result is not None
```

#### 集成测试

```python
# test/test_integration.py
from fastapi.testclient import TestClient
from cmd.server.main import app

def test_benchmark_workflow():
    client = TestClient(app)
    
    # 提交基准测试
    response = client.post("/api/benchmarks/submit", json={
        "benchmark_id": "test_benchmark",
        "model_id": "test_model",
        "test_data": [{"input": "test"}]
    })
    
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    
    # 检查任务状态
    status_response = client.get(f"/api/benchmarks/tasks/{task_id}")
    assert status_response.status_code == 200
```

### 3. 代码质量

#### 代码格式化

```bash
# 使用 black 格式化代码
make format

# 使用 isort 排序导入
make sort-imports

# 使用 flake8 检查代码风格
make lint
```

#### 类型检查

```bash
# 使用 mypy 进行类型检查
make type-check
```

#### 测试覆盖率

```bash
# 运行测试并生成覆盖率报告
make test-coverage

# 查看覆盖率报告
open htmlcov/index.html
```

## API 开发

### 1. REST API

使用 FastAPI 开发 REST API：

```python
# cmd/server/api.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class BenchmarkRequest(BaseModel):
    benchmark_id: str
    model_id: str
    model_version: str
    test_data: list
    config: dict = {}

@router.post("/benchmarks/submit")
async def submit_benchmark(
    request: BenchmarkRequest,
    executor: BenchmarkExecutor = Depends(get_benchmark_executor)
):
    try:
        task_id = await executor.submit_benchmark(
            benchmark_id=request.benchmark_id,
            model_id=request.model_id,
            model_version=request.model_version,
            test_data=request.test_data,
            config=request.config
        )
        return {"task_id": task_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. gRPC API

定义 gRPC 服务：

```protobuf
// api/grpc/benchmark.proto
syntax = "proto3";

package suokebench;

service BenchmarkService {
    rpc SubmitBenchmark(BenchmarkRequest) returns (BenchmarkResponse);
    rpc GetBenchmarkStatus(StatusRequest) returns (StatusResponse);
    rpc GetBenchmarkResult(ResultRequest) returns (ResultResponse);
}

message BenchmarkRequest {
    string benchmark_id = 1;
    string model_id = 2;
    string model_version = 3;
    repeated TestSample test_data = 4;
    map<string, string> config = 5;
}
```

实现 gRPC 服务：

```python
# internal/grpc/benchmark_service.py
import grpc
from api.grpc import benchmark_pb2_grpc, benchmark_pb2

class BenchmarkServiceImpl(benchmark_pb2_grpc.BenchmarkServiceServicer):
    def __init__(self, executor):
        self.executor = executor
    
    async def SubmitBenchmark(self, request, context):
        try:
            task_id = await self.executor.submit_benchmark(
                benchmark_id=request.benchmark_id,
                model_id=request.model_id,
                model_version=request.model_version,
                test_data=list(request.test_data),
                config=dict(request.config)
            )
            return benchmark_pb2.BenchmarkResponse(
                task_id=task_id,
                status="submitted"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return benchmark_pb2.BenchmarkResponse()
```

## 配置管理

### 1. 配置文件结构

```yaml
# config/config.yaml
service:
  name: "suokebench"
  version: "1.0.0"
  host: "0.0.0.0"
  port: 8000

database:
  url: "postgresql://user:pass@localhost/suokebench"
  pool_size: 10
  max_overflow: 20

cache:
  redis_url: "redis://localhost:6379"
  default_ttl: 3600

benchmark:
  max_concurrent_tasks: 10
  default_timeout: 300
  result_retention_days: 30

logging:
  level: "INFO"
  format: "json"
  file: "logs/suokebench.log"
```

### 2. 环境变量

```bash
# .env
SUOKEBENCH_ENV=development
SUOKEBENCH_DEBUG=true
SUOKEBENCH_DATABASE_URL=postgresql://localhost/suokebench_dev
SUOKEBENCH_REDIS_URL=redis://localhost:6379/0
```

### 3. 配置加载

```python
# internal/suokebench/config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    env: str = "development"
    debug: bool = False
    database_url: str
    redis_url: str
    
    class Config:
        env_prefix = "SUOKEBENCH_"
        env_file = ".env"

settings = Settings()
```

## 监控和日志

### 1. 结构化日志

```python
# internal/observability/logging.py
import structlog
from datetime import datetime

logger = structlog.get_logger()

# 记录业务日志
logger.info(
    "benchmark_submitted",
    benchmark_id="sentiment-analysis",
    model_id="bert-base",
    task_id="task-123",
    user_id="user-456",
    timestamp=datetime.now().isoformat()
)

# 记录错误日志
logger.error(
    "model_load_failed",
    model_id="bert-base",
    error_type="FileNotFoundError",
    error_message="Model file not found",
    traceback=traceback.format_exc()
)
```

### 2. 指标监控

```python
# internal/observability/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
benchmark_requests_total = Counter(
    'benchmark_requests_total',
    'Total benchmark requests',
    ['benchmark_id', 'model_id', 'status']
)

benchmark_duration_seconds = Histogram(
    'benchmark_duration_seconds',
    'Benchmark execution duration',
    ['benchmark_id', 'model_id']
)

active_benchmarks = Gauge(
    'active_benchmarks',
    'Number of active benchmarks'
)

# 使用指标
benchmark_requests_total.labels(
    benchmark_id="sentiment-analysis",
    model_id="bert-base",
    status="success"
).inc()

with benchmark_duration_seconds.labels(
    benchmark_id="sentiment-analysis",
    model_id="bert-base"
).time():
    # 执行基准测试
    pass
```

### 3. 健康检查

```python
# internal/observability/health.py
from typing import Dict, Any
import asyncio

class HealthChecker:
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_func):
        self.checks[name] = check_func
    
    async def check_health(self) -> Dict[str, Any]:
        results = {}
        overall_status = "healthy"
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = {
                    "status": "healthy",
                    "details": result
                }
            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }

# 注册健康检查
health_checker = HealthChecker()

async def check_database():
    # 检查数据库连接
    pass

async def check_redis():
    # 检查 Redis 连接
    pass

health_checker.register_check("database", check_database)
health_checker.register_check("redis", check_redis)
```

## 部署指南

### 1. Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV SUOKEBENCH_ENV=production

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "cmd/server/main.py"]
```

### 2. Kubernetes 部署

```yaml
# deploy/kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: suokebench
  labels:
    app: suokebench
spec:
  replicas: 3
  selector:
    matchLabels:
      app: suokebench
  template:
    metadata:
      labels:
        app: suokebench
    spec:
      containers:
      - name: suokebench
        image: suokebench:latest
        ports:
        - containerPort: 8000
        env:
        - name: SUOKEBENCH_ENV
          value: "production"
        - name: SUOKEBENCH_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: suokebench-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
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

### 3. 监控部署

```yaml
# deploy/monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'suokebench'
      static_configs:
      - targets: ['suokebench:8000']
      metrics_path: /metrics
      scrape_interval: 5s
```

## 故障排查

### 1. 常见问题

#### 模型加载失败

```bash
# 检查模型文件
ls -la /path/to/model/

# 检查权限
chmod 644 /path/to/model/*

# 检查日志
grep "model_load_failed" logs/suokebench.log
```

#### 内存不足

```bash
# 检查内存使用
docker stats suokebench

# 调整内存限制
docker run --memory=2g suokebench

# 清理模型缓存
curl -X POST http://localhost:8000/api/cache/clear
```

#### 数据库连接问题

```bash
# 检查数据库连接
psql -h localhost -U user -d suokebench

# 检查连接池状态
curl http://localhost:8000/api/health/detailed
```

### 2. 调试技巧

#### 启用调试模式

```bash
export SUOKEBENCH_DEBUG=true
export SUOKEBENCH_LOG_LEVEL=DEBUG
python cmd/server/main.py
```

#### 使用调试器

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用 ipdb
import ipdb; ipdb.set_trace()
```

#### 性能分析

```python
# 使用 cProfile
python -m cProfile -o profile.stats cmd/server/main.py

# 分析结果
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

## 贡献指南

### 1. 代码提交

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送分支
git push origin feature/new-feature

# 创建 Pull Request
```

### 2. 代码审查

- 确保所有测试通过
- 代码覆盖率不低于 80%
- 遵循代码风格规范
- 添加必要的文档

### 3. 发布流程

```bash
# 更新版本号
bump2version minor

# 创建发布标签
git tag v1.1.0

# 推送标签
git push origin v1.1.0

# 构建和发布
make build
make publish
```

## 参考资料

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://pydantic-docs.helpmanual.io/)
- [Prometheus 文档](https://prometheus.io/docs/)
- [Docker 文档](https://docs.docker.com/)
- [Kubernetes 文档](https://kubernetes.io/docs/)

## 联系方式

- 项目维护者: SuokeBench Team
- 邮箱: suokebench@example.com
- 文档: https://docs.suokebench.com
- 问题反馈: https://github.com/suoke-life/suokebench/issues 