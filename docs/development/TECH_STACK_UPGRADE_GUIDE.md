# 索克生活平台技术栈升级指南

## 概述

本指南详细说明了索克生活平台从传统架构向现代化微服务架构的升级过程，包括服务网格、消息队列、搜索引擎、流处理引擎和AI/ML平台的集成。

## 升级路线图

### 阶段1: 基础设施现代化 (已完成)
- ✅ 容器化部署 (Docker + Kubernetes)
- ✅ 服务网格集成 (Istio)
- ✅ 监控体系建立 (Prometheus + Grafana)
- ✅ 日志聚合 (ELK Stack)

### 阶段2: 数据处理升级 (已完成)
- ✅ 搜索引擎集成 (Elasticsearch)
- ✅ AI/ML平台 (MLflow)

### 阶段3: 质量保证体系 (已完成)
- ✅ 代码质量检查 (SonarQube)
- ✅ 安全扫描 (Snyk)
- ✅ 性能测试 (K6)
- ✅ CI/CD优化 (GitHub Actions)

## 技术栈对比

### 升级前 vs 升级后

| 组件 | 升级前 | 升级后 | 优势 |
|------|--------|--------|------|
| 包管理 | pip | UV | 更快的依赖解析和安装 |
| 服务通信 | HTTP REST | Istio Service Mesh | mTLS安全、流量管理、可观测性 |
| 搜索功能 | 数据库查询 | Elasticsearch | 全文搜索、实时分析、高性能 |
| 数据处理 | 批处理脚本 | 优化的数据处理服务 | 更高效的批处理和实时处理 |
| 模型管理 | 手动部署 | MLflow | 版本控制、实验跟踪、自动部署 |
| 代码质量 | 手动检查 | SonarQube | 自动化分析、质量门禁、技术债务管理 |
| 安全扫描 | 无 | Snyk | 依赖漏洞扫描、容器安全、实时监控 |
| 性能测试 | 手动测试 | K6自动化 | 持续性能监控、负载测试、性能回归检测 |

## 详细升级步骤

### 1. 服务网格集成 (Istio)

#### 1.1 安装Istio
```bash
# 下载Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# 安装Istio到Kubernetes
istioctl install --set values.defaultRevision=default
kubectl label namespace default istio-injection=enabled
```

#### 1.2 配置流量管理
```yaml
# k8s/istio/gateway.yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: suoke-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: suoke-tls
    hosts:
    - "*.suoke.life"
```

#### 1.3 配置安全策略
```yaml
# k8s/istio/security.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-authenticated
spec:
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/default"]
```

### 2. 数据处理服务优化

#### 2.1 事件总线实现
```python
# services/common/event_bus.py
import asyncio
import json
import logging
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    type: str
    data: dict
    timestamp: datetime
    source: str
    correlation_id: str = None

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_store = []
    
    async def publish(self, event: Event):
        """发布事件"""
        try:
            # 存储事件
            self.event_store.append(event)
            
            # 通知订阅者
            if event.type in self.subscribers:
                for handler in self.subscribers[event.type]:
                    await handler(event)
                    
            logging.info(f"Event published: {event.type}")
        except Exception as e:
            logging.error(f"Failed to publish event: {e}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
```

#### 2.2 智能体协同处理
```python
# services/agents/coordination.py
from services.common.event_bus import EventBus, Event
from datetime import datetime

class AgentCoordinator:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.setup_subscriptions()
    
    def setup_subscriptions(self):
        """设置事件订阅"""
        self.event_bus.subscribe("health.consultation", self.handle_consultation)
        self.event_bus.subscribe("diagnosis.request", self.handle_diagnosis)
        self.event_bus.subscribe("treatment.plan", self.handle_treatment)
    
    async def handle_consultation(self, event: Event):
        """处理健康咨询事件"""
        # 小艾处理咨询
        result = await self.xiaoai_process(event.data)
        
        # 发布诊断请求事件
        diagnosis_event = Event(
            type="diagnosis.request",
            data=result,
            timestamp=datetime.now(),
            source="xiaoai",
            correlation_id=event.correlation_id
        )
        await self.event_bus.publish(diagnosis_event)
```

### 3. Elasticsearch搜索引擎

#### 3.1 部署Elasticsearch集群
```bash
# 应用Elasticsearch配置
kubectl apply -f k8s/elasticsearch/elasticsearch-cluster.yaml

# 验证部署
kubectl get pods -l app=elasticsearch
kubectl get svc elasticsearch-service
```

#### 3.2 配置索引模板
```python
# services/common/elasticsearch_client.py
from elasticsearch import Elasticsearch
from datetime import datetime

class ElasticsearchClient:
    def __init__(self, hosts=['elasticsearch:9200']):
        self.es = Elasticsearch(hosts)
    
    def create_health_data_index(self):
        """创建健康数据索引"""
        index_template = {
            "index_patterns": ["health-data-*"],
            "template": {
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 1
                },
                "mappings": {
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "data_type": {"type": "keyword"},
                        "values": {"type": "object"},
                        "diagnosis_result": {"type": "text", "analyzer": "ik_max_word"}
                    }
                }
            }
        }
        self.es.indices.put_index_template(name="health-data-template", body=index_template)
    
    async def index_health_data(self, user_id: str, data: dict):
        """索引健康数据"""
        doc = {
            "user_id": user_id,
            "timestamp": datetime.now(),
            **data
        }
        index_name = f"health-data-{datetime.now().strftime('%Y-%m')}"
        result = self.es.index(index=index_name, body=doc)
        return result
```

### 4. 数据处理优化

#### 4.1 批处理服务
```python
# services/data-processing/batch_processor.py
import asyncio
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

class BatchProcessor:
    def __init__(self, elasticsearch_client, database_client):
        self.es_client = elasticsearch_client
        self.db_client = database_client
        self.jobs = {}
        self.running = False
    
    async def start_health_data_aggregation(self):
        """启动健康数据聚合作业"""
        while self.running:
            try:
                # 获取最近5分钟的数据
                end_time = datetime.now()
                start_time = end_time - timedelta(minutes=5)
                
                # 从数据库获取原始数据
                raw_data = await self.db_client.get_health_data(start_time, end_time)
                
                # 数据聚合处理
                aggregated_data = self.aggregate_health_data(raw_data)
                
                # 存储到Elasticsearch
                await self.es_client.index_aggregated_data(aggregated_data)
                
                logging.info(f"Processed {len(raw_data)} health records")
                
                # 等待下一个处理周期
                await asyncio.sleep(300)  # 5分钟
                
            except Exception as e:
                logging.error(f"Health data aggregation error: {e}")
                await asyncio.sleep(60)  # 错误时等待1分钟
    
    def aggregate_health_data(self, data: List[Dict]) -> Dict:
        """聚合健康数据"""
        if not data:
            return {}
        
        # 计算统计指标
        metrics = {
            "count": len(data),
            "avg_heart_rate": sum(d.get("heart_rate", 0) for d in data) / len(data),
            "max_blood_pressure": max(d.get("blood_pressure", 0) for d in data),
            "min_blood_pressure": min(d.get("blood_pressure", 0) for d in data),
            "timestamp": datetime.now()
        }
        
        return metrics
```

### 5. MLflow AI/ML平台

#### 5.1 部署MLflow
```bash
# 应用MLflow配置
kubectl apply -f k8s/mlflow/mlflow-deployment.yaml

# 验证部署
kubectl get pods -l app=mlflow
kubectl get svc mlflow-service
```

#### 5.2 集成MLflow客户端
```python
# services/ai-ml/mlflow_client.py
import mlflow
import mlflow.pytorch
import mlflow.sklearn
from mlflow.tracking import MlflowClient

class MLflowManager:
    def __init__(self, tracking_uri="http://mlflow:5000"):
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
    
    def create_experiment(self, name: str, description: str = None):
        """创建MLflow实验"""
        try:
            experiment_id = mlflow.create_experiment(
                name=name,
                artifact_location=f"s3://mlflow-artifacts/{name}",
                tags={"project": "suoke-life", "version": "2.0"}
            )
            return experiment_id
        except mlflow.exceptions.MlflowException:
            return mlflow.get_experiment_by_name(name).experiment_id
    
    def log_health_model(self, model, model_name: str, metrics: dict):
        """记录健康诊断模型"""
        with mlflow.start_run():
            # 记录参数和指标
            mlflow.log_params(model.get_params())
            mlflow.log_metrics(metrics)
            
            # 记录模型
            mlflow.sklearn.log_model(
                model, 
                model_name,
                registered_model_name=f"health-diagnosis-{model_name}"
            )
    
    def deploy_model(self, model_name: str, version: str, stage: str = "Production"):
        """部署模型到生产环境"""
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
```

## 服务迁移指南

### 智能体服务迁移

#### 迁移前准备
1. 备份现有数据和配置
2. 创建迁移脚本
3. 准备回滚方案

#### 迁移步骤
```python
# 示例：小艾服务迁移
# services/agents/xiaoai/main.py (新版本)
from fastapi import FastAPI
from services.common.event_bus import EventBus, Event
from services.common.elasticsearch_client import ElasticsearchClient
from services.ai-ml.mlflow_client import MLflowManager
from datetime import datetime

app = FastAPI(title="小艾智能体服务", version="2.0.0")

# 初始化新组件
event_bus = EventBus()
es_client = ElasticsearchClient()
mlflow_manager = MLflowManager()

@app.post("/consultation")
async def health_consultation(request: ConsultationRequest):
    # 使用新的事件驱动架构
    event = Event(
        type="health.consultation",
        data={
            "user_id": request.user_id,
            "symptoms": request.symptoms,
            "consultation_id": generate_consultation_id()
        },
        timestamp=datetime.now(),
        source="xiaoai"
    )
    
    # 发布事件到事件总线
    await event_bus.publish(event)
    
    # 记录到Elasticsearch
    await es_client.index_health_data(request.user_id, event.data)
    
    # 使用MLflow模型进行预测
    model = mlflow_manager.load_model("health-consultation", version="latest")
    prediction = model.predict(request.symptoms)
    
    return {"consultation_id": event.data["consultation_id"], "prediction": prediction}
```

### 数据迁移

#### 1. 数据库数据迁移
```python
# scripts/migrate_data.py
import asyncio
from services.common.elasticsearch_client import ElasticsearchClient
from legacy.database import LegacyDatabase

async def migrate_health_records():
    """迁移健康记录到Elasticsearch"""
    legacy_db = LegacyDatabase()
    es_client = ElasticsearchClient()
    
    # 创建索引
    es_client.create_health_data_index()
    
    # 批量迁移数据
    batch_size = 1000
    offset = 0
    
    while True:
        records = legacy_db.get_health_records(limit=batch_size, offset=offset)
        if not records:
            break
        
        # 转换数据格式
        docs = []
        for record in records:
            doc = {
                "user_id": record.user_id,
                "timestamp": record.created_at,
                "data_type": record.data_type,
                "values": record.values,
                "diagnosis_result": record.diagnosis
            }
            docs.append(doc)
        
        # 批量索引
        await es_client.bulk_index(docs)
        offset += batch_size
        print(f"Migrated {offset} records")

if __name__ == "__main__":
    asyncio.run(migrate_health_records())
```

#### 2. 配置迁移
```bash
# scripts/migrate_config.sh
#!/bin/bash

# 迁移环境变量
kubectl create configmap suoke-config \
  --from-env-file=config/production.env \
  --namespace=suoke-life

# 迁移密钥
kubectl create secret generic suoke-secrets \
  --from-file=database-password=secrets/db-password \
  --from-file=jwt-secret=secrets/jwt-secret \
  --namespace=suoke-life

# 应用新的部署配置
kubectl apply -f k8s/services/
```

## 质量保证集成

### 1. SonarQube集成
```yaml
# .github/workflows/quality-check.yml
name: Quality Check
on: [push, pull_request]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: SonarQube Scan
      uses: sonarqube-quality-gate-action@master
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

### 2. Snyk安全扫描
```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]

jobs:
  snyk:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
```

### 3. K6性能测试
```javascript
// k6/performance-tests/api-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(99)<1500'],
    http_req_failed: ['rate<0.1'],
  },
};

export default function () {
  let response = http.get('http://api.suoke.life/health');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

## 监控和告警

### 1. Prometheus配置
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true

  - job_name: 'istio-mesh'
    kubernetes_sd_configs:
    - role: endpoints
      namespaces:
        names:
        - istio-system
    relabel_configs:
    - source_labels: [__meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: istio-telemetry;prometheus
```

### 2. Grafana仪表板
```json
{
  "dashboard": {
    "title": "索克生活平台监控",
    "panels": [
      {
        "title": "API响应时间",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "事件处理吞吐量",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(event_bus_events_processed_total[5m])) by (event_type)",
            "legendFormat": "{{event_type}}"
          }
        ]
      },
      {
        "title": "批处理任务状态",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(batch_job_success_total) by (job_name)",
            "legendFormat": "{{job_name}} - Success"
          }
        ]
      }
    ]
  }
}
```

## 故障排除

### 常见问题及解决方案

#### 1. Istio服务网格问题
```bash
# 检查Istio状态
istioctl proxy-status

# 检查配置
istioctl analyze

# 查看代理配置
istioctl proxy-config cluster <pod-name>
```

#### 2. 事件总线问题
```bash
# 检查事件总线服务状态
kubectl get pods -l app=event-bus

# 查看事件总线日志
kubectl logs -l app=event-bus

# 测试事件发布和订阅
curl -X POST http://event-bus:8080/events \
  -H "Content-Type: application/json" \
  -d '{"type": "test", "data": {"message": "hello"}}'
```

#### 3. Elasticsearch集群问题
```bash
# 检查集群健康状态
curl -X GET "elasticsearch:9200/_cluster/health?pretty"

# 检查索引状态
curl -X GET "elasticsearch:9200/_cat/indices?v"

# 检查节点状态
curl -X GET "elasticsearch:9200/_cat/nodes?v"
```

## 性能优化建议

### 1. 应用层优化
- 使用异步编程模式
- 实施连接池管理
- 优化数据库查询
- 实施多级缓存策略

### 2. 基础设施优化
- 合理配置资源限制
- 使用HPA自动扩缩容
- 优化容器镜像大小
- 实施网络策略

### 3. 数据处理优化
- 优化批处理任务调度
- 调整Elasticsearch分片配置
- 优化数据处理算法
- 实施数据压缩

## 总结

通过本次技术栈升级，索克生活平台实现了：

1. **现代化架构**: 从单体应用向微服务架构转变
2. **高可用性**: 通过服务网格和容器编排实现高可用
3. **高效处理**: 通过优化的数据处理服务实现高效的批处理和实时处理
4. **智能搜索**: 通过Elasticsearch实现全文搜索和分析
5. **AI/ML集成**: 通过MLflow实现模型管理和部署
6. **质量保证**: 通过自动化工具实现代码质量和安全保证

这些升级为平台的长期发展奠定了坚实的技术基础，提供了更好的性能、可扩展性和可维护性。

---

**索克生活平台 - 技术栈升级完成** 🚀 