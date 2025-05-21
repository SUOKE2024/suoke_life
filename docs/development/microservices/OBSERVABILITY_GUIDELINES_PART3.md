# 索克生活APP微服务可观测性指南 - 第三部分

## 健康检查

### 标准健康检查端点

每个微服务必须实现以下标准健康检查端点：

1. **就绪检查 (Readiness)**：`/health/ready` - 检查服务是否准备好接受流量
2. **存活检查 (Liveness)**：`/health/live` - 检查服务是否正在运行
3. **全面健康检查**：`/health` - 提供服务所有组件的详细健康状态

### FastAPI健康检查实现

使用FastAPI实现标准健康检查：

```python
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import time
import psutil
import aiohttp

app = FastAPI()

# 健康检查模型
class ComponentHealth(BaseModel):
    """组件健康状态"""
    status: str  # "UP" | "DOWN" | "DEGRADED"
    name: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthStatus(BaseModel):
    """整体健康状态"""
    status: str  # "UP" | "DOWN" | "DEGRADED"
    version: str
    timestamp: int
    components: List[ComponentHealth]

# 健康检查函数
async def check_database():
    """检查数据库连接"""
    try:
        # 执行简单查询验证连接
        await db.execute("SELECT 1")
        return ComponentHealth(
            name="database",
            status="UP",
            details={"type": "postgresql", "version": "13.3"}
        )
    except Exception as e:
        return ComponentHealth(
            name="database",
            status="DOWN",
            error=str(e)
        )

async def check_redis():
    """检查Redis连接"""
    try:
        # 执行PING命令验证连接
        result = await redis.ping()
        return ComponentHealth(
            name="redis",
            status="UP",
            details={"command": "PING", "result": "PONG"}
        )
    except Exception as e:
        return ComponentHealth(
            name="redis",
            status="DOWN",
            error=str(e)
        )

async def check_downstream_service(service_name, url):
    """检查下游服务健康状态"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2) as response:
                if response.status == 200:
                    return ComponentHealth(
                        name=f"service:{service_name}",
                        status="UP"
                    )
                else:
                    return ComponentHealth(
                        name=f"service:{service_name}",
                        status="DEGRADED",
                        error=f"Status code: {response.status}"
                    )
    except Exception as e:
        return ComponentHealth(
            name=f"service:{service_name}",
            status="DOWN",
            error=str(e)
        )

async def check_system_resources():
    """检查系统资源使用情况"""
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    status = "UP"
    # 如果内存或磁盘使用率超过90%，标记为DEGRADED
    if memory.percent > 90 or disk.percent > 90:
        status = "DEGRADED"
    
    return ComponentHealth(
        name="system",
        status=status,
        details={
            "cpu_usage": f"{cpu_usage}%",
            "memory_used": f"{memory.percent}%",
            "disk_used": f"{disk.percent}%"
        }
    )

# 健康检查端点
@app.get("/health/live", status_code=200)
async def liveness_check():
    """存活检查 - 服务是否在运行"""
    # 简单检查，只要服务响应就是健康的
    return {"status": "UP"}

@app.get("/health/ready", status_code=200)
async def readiness_check(response: Response):
    """就绪检查 - 服务是否准备好接受流量"""
    # 检查关键依赖
    db_health = await check_database()
    redis_health = await check_redis()
    
    # 只有当所有关键依赖都健康时，服务才准备好
    if db_health.status == "DOWN" or redis_health.status == "DOWN":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "DOWN",
            "components": [db_health, redis_health]
        }
    
    return {"status": "UP"}

@app.get("/health", response_model=HealthStatus)
async def health_check(response: Response):
    """全面健康检查 - 返回所有组件健康状态"""
    # 并行检查所有组件
    db_health = await check_database()
    redis_health = await check_redis()
    user_service_health = await check_downstream_service(
        "user-service", 
        "http://user-service:8080/health/ready"
    )
    system_health = await check_system_resources()
    
    components = [db_health, redis_health, user_service_health, system_health]
    
    # 确定整体状态
    overall_status = "UP"
    for component in components:
        if component.status == "DOWN":
            overall_status = "DOWN"
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            break
        elif component.status == "DEGRADED" and overall_status != "DOWN":
            overall_status = "DEGRADED"
    
    return HealthStatus(
        status=overall_status,
        version="1.2.3",  # 从配置或构建信息中获取
        timestamp=int(time.time()),
        components=components
    )
```

### Kubernetes健康检查配置

在Kubernetes配置中添加健康检查：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  template:
    spec:
      containers:
      - name: auth-service
        image: suokelife/auth-service:1.0.0
        ports:
        - containerPort: 8080
        # 就绪探针 - 确定服务何时准备好接受流量
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        # 存活探针 - 确定何时需要重启容器
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        # 启动探针 - 保护慢启动服务
        startupProbe:
          httpGet:
            path: /health/live
            port: 8080
          failureThreshold: 30
          periodSeconds: 10
```

## 可观测性最佳实践

### 实现金丝雀发布监控

使用Istio和Prometheus实现金丝雀发布监控：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: auth-service
spec:
  hosts:
  - auth-service
  http:
  - name: "canary"
    match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: auth-service
        subset: v2
  - name: "production"
    route:
    - destination:
        host: auth-service
        subset: v1
        weight: 90
    - destination:
        host: auth-service
        subset: v2
        weight: 10
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: auth-service
spec:
  host: auth-service
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

并创建版本比较监控面板：

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: canary-comparison
spec:
  groups:
  - name: canary
    rules:
    - record: canary:request_latency_seconds:p95
      expr: histogram_quantile(0.95, sum(rate(app_request_latency_seconds_bucket{service="auth-service", version="v2"}[5m])) by (le))
    - record: production:request_latency_seconds:p95
      expr: histogram_quantile(0.95, sum(rate(app_request_latency_seconds_bucket{service="auth-service", version="v1"}[5m])) by (le))
    - record: canary:error_rate
      expr: sum(rate(app_request_count_total{service="auth-service", version="v2", status=~"5.."}[5m])) / sum(rate(app_request_count_total{service="auth-service", version="v2"}[5m]))
    - record: production:error_rate
      expr: sum(rate(app_request_count_total{service="auth-service", version="v1", status=~"5.."}[5m])) / sum(rate(app_request_count_total{service="auth-service", version="v1"}[5m]))
    - alert: CanaryHighErrorRate
      expr: canary:error_rate > production:error_rate * 1.5
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "金丝雀版本错误率异常"
        description: "金丝雀版本错误率 ({{ $value | humanizePercentage }}) 比生产版本高50%以上"
    - alert: CanaryHighLatency
      expr: canary:request_latency_seconds:p95 > production:request_latency_seconds:p95 * 1.5
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "金丝雀版本延迟异常"
        description: "金丝雀版本P95延迟 ({{ $value | humanizeDuration }}) 比生产版本高50%以上"
```

### 可观测性成熟度模型

建立可观测性成熟度模型，分级评估微服务的可观测性：

| 级别 | 名称 | 要求 | 
|-----|------|------|
| 0 | 基础 | 基本健康检查、访问日志、错误日志 |
| 1 | 标准 | RED指标、结构化日志、简单追踪、基本告警 |
| 2 | 完善 | 详细指标、完整追踪、业务指标、高级告警规则 |
| 3 | 高级 | 自动异常检测、相关性分析、SLO监控、自定义仪表盘 |
| 4 | 卓越 | AI辅助分析、预测性监控、自愈能力、可观测性即代码 |

每个服务应至少达到级别2（完善），关键服务应达到级别3（高级）以上。

### 事件驱动监控

实现基于事件的监控，补充传统的度量指标监控：

```python
from dataclasses import dataclass, asdict
import json
import time
import uuid
from typing import Optional, Dict, Any, List

@dataclass
class BusinessEvent:
    """业务事件模型"""
    id: str
    type: str
    source: str
    time: str
    subject: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

class EventPublisher:
    """业务事件发布器"""
    
    def __init__(self, kafka_producer):
        self.producer = kafka_producer
        self.service_name = "auth-service"  # 从配置中获取
    
    def publish(self, event_type: str, data: Dict[str, Any], 
               subject: Optional[str] = None, 
               context: Optional[Dict[str, Any]] = None) -> str:
        """发布业务事件"""
        event_id = str(uuid.uuid4())
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime())
        
        event = BusinessEvent(
            id=event_id,
            type=event_type,
            source=self.service_name,
            time=timestamp,
            subject=subject,
            data=data,
            context=context
        )
        
        # 发送到Kafka
        self.producer.send(
            topic=f"events.{self.service_name}.{event_type}",
            key=subject.encode('utf-8') if subject else None,
            value=json.dumps(asdict(event)).encode('utf-8')
        )
        
        return event_id

# 使用示例
publisher = EventPublisher(kafka_producer)

# 记录用户登录事件
publisher.publish(
    event_type="user.login.succeeded",
    data={
        "auth_method": "password",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "192.168.1.1"
    },
    subject="user:123456",
    context={
        "trace_id": "abc123",
        "request_id": "req789"
    }
)

# 记录异常登录事件
publisher.publish(
    event_type="user.login.suspicious",
    data={
        "auth_method": "password",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "192.168.1.1",
        "reason": "unusual_location",
        "risk_score": 85
    },
    subject="user:123456"
)
```

### 可观测性自动化检查

在CI/CD流水线中添加自动化可观测性检查：

```yaml
# .github/workflows/observability-check.yml
name: Observability Check

on:
  pull_request:
    branches: [ main, develop ]
    paths:
      - '**.py'
      - '**.go'
      - 'prometheus/**'
      - 'grafana/**'

jobs:
  check-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install promtool-prometheus prometheus-client
      
      - name: Check Prometheus metrics naming
        run: |
          python scripts/check_metrics_naming.py
      
      - name: Validate Prometheus rules
        run: |
          promtool check rules prometheus/rules/*.yml
  
  check-logs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Check structured logging
        run: |
          python scripts/check_structured_logging.py
  
  check-tracing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Check tracing integration
        run: |
          python scripts/check_tracing_integration.py
```

## 总结与最佳实践

1. **标准化指标命名和收集**
   - 使用RED方法监控微服务
   - 遵循一致的指标命名约定
   - 为每个微服务实现核心指标和服务特定指标

2. **结构化、上下文丰富的日志**
   - 统一使用JSON格式的结构化日志
   - 在日志中包含请求ID、追踪ID等上下文信息
   - 实现合理的日志级别使用策略
   - 保护敏感数据，防止泄露

3. **端到端分布式追踪**
   - 使用OpenTelemetry实现一致的跨服务追踪
   - 确保追踪上下文在服务间正确传播
   - 对关键业务流程添加详细的手动追踪点

4. **主动监控与告警策略**
   - 为每个服务定义明确的SLO/SLI
   - 实施多级别告警策略
   - 建立告警路由和通知渠道
   - 维护问题处理运行手册

5. **可视化与报告**
   - 创建标准化的服务监控面板
   - 建立业务和技术指标的关联视图
   - 实现异常分析和根因定位工具

6. **健康检查模式**
   - 每个服务实现标准健康检查端点
   - 区分就绪检查和存活检查
   - 在健康检查中验证关键依赖

7. **持续改进**
   - 定期审查和更新监控策略
   - 基于实际事件更新告警规则
   - 将监控数据用于性能优化
   - 建立可观测性成熟度评估模型

遵循这些指南，可以构建一个全面、深入且可行的微服务可观测性体系，帮助团队快速发现并解决问题，持续优化系统性能，确保用户体验。