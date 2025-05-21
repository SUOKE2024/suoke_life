# 索克生活APP微服务可观测性指南 - 第二部分

## 分布式追踪

### OpenTelemetry集成

使用OpenTelemetry实现分布式追踪：

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.aiohttp import AioHttpClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_tracing(app, service_name):
    """配置OpenTelemetry分布式追踪"""
    # 创建TracerProvider
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)
    
    # 创建Jaeger导出器
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_HOST", "jaeger"),
        agent_port=int(os.getenv("JAEGER_PORT", "6831")),
    )
    
    # 添加批处理器
    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    
    # 自动检测常用库
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
    AioHttpClientInstrumentor().instrument()
    
    # 如果使用SQLAlchemy，也可以对其进行检测
    if 'db_engine' in globals():
        SQLAlchemyInstrumentor().instrument(engine=db_engine)
    
    return trace.get_tracer(service_name)
```

### 手动追踪关键流程

对于需要详细追踪的业务逻辑，添加手动追踪点：

```python
async def process_health_data(user_id, data):
    """处理用户健康数据"""
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("process_health_data") as parent_span:
        parent_span.set_attribute("user_id", user_id)
        parent_span.set_attribute("data_type", data.get("type"))
        
        # 第一步：数据验证
        with tracer.start_as_current_span("validate_health_data") as span:
            try:
                validate_result = await validate_health_data(data)
                if not validate_result.valid:
                    span.set_attribute("error", True)
                    span.set_attribute("validation_errors", str(validate_result.errors))
                    return {"success": False, "errors": validate_result.errors}
            except Exception as e:
                span.record_exception(e)
                span.set_attribute("error", True)
                raise
        
        # 第二步：数据处理
        with tracer.start_as_current_span("transform_health_data") as span:
            try:
                processed_data = await transform_health_data(data)
                span.set_attribute("transformed_fields", str(list(processed_data.keys())))
            except Exception as e:
                span.record_exception(e)
                span.set_attribute("error", True)
                raise
        
        # 第三步：保存数据
        with tracer.start_as_current_span("save_health_data") as span:
            try:
                span.set_attribute("storage_type", "database")
                result = await save_to_database(user_id, processed_data)
                span.set_attribute("record_id", result.id)
            except Exception as e:
                span.record_exception(e)
                span.set_attribute("error", True)
                raise
        
        # 第四步：发送事件通知
        with tracer.start_as_current_span("send_health_data_event") as span:
            try:
                span.set_attribute("event_type", "health_data_processed")
                await publish_event("health_data_processed", {
                    "user_id": user_id,
                    "data_id": result.id,
                    "data_type": data.get("type")
                })
            except Exception as e:
                span.record_exception(e)
                span.set_attribute("error", True)
                # 这里我们只记录错误但不抛出，因为这是非关键流程
                logger.error(f"Failed to publish event: {str(e)}")
        
        return {"success": True, "data_id": result.id}
```

### 追踪上下文传播

在服务间调用中传播追踪上下文：

```python
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

async def call_external_service(url, payload):
    """调用外部服务，传递追踪上下文"""
    # 创建headers字典
    headers = {}
    
    # 注入当前追踪上下文到headers
    inject(headers)
    
    # 发起HTTP请求，传递追踪上下文
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await response.json()

# gRPC上下文传播示例
class OpenTelemetryClientInterceptor(grpc.UnaryUnaryClientInterceptor):
    """gRPC客户端拦截器，注入追踪上下文"""
    
    def __init__(self):
        self._propagator = TraceContextTextMapPropagator()
    
    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        
        # 将当前追踪上下文注入元数据
        carrier = {}
        inject(carrier)
        for key, value in carrier.items():
            metadata.append((key, value))
        
        new_details = client_call_details._replace(metadata=metadata)
        return continuation(new_details, request)
```

### Jaeger查询API集成

在问题诊断中集成Jaeger查询API：

```python
import requests

class JaegerClient:
    """Jaeger API客户端，用于查询追踪数据"""
    
    def __init__(self, base_url="http://jaeger-query:16686"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def get_trace(self, trace_id):
        """获取特定追踪的详细信息"""
        url = f"{self.api_url}/traces/{trace_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def search_traces(self, service_name, operation=None, tags=None, 
                     min_duration=None, max_duration=None, 
                     start_time=None, end_time=None, limit=20):
        """搜索符合条件的追踪"""
        params = {
            "service": service_name,
            "limit": limit
        }
        
        if operation:
            params["operation"] = operation
        
        if tags:
            for key, value in tags.items():
                params[f"tags[{key}]"] = value
        
        if min_duration:
            params["minDuration"] = min_duration
        
        if max_duration:
            params["maxDuration"] = max_duration
        
        if start_time:
            params["start"] = int(start_time.timestamp() * 1000000)
        
        if end_time:
            params["end"] = int(end_time.timestamp() * 1000000)
        
        url = f"{self.api_url}/traces"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_services(self):
        """获取所有服务列表"""
        url = f"{self.api_url}/services"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_operations(self, service_name):
        """获取服务的所有操作列表"""
        url = f"{self.api_url}/services/{service_name}/operations"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

# 使用示例
async def troubleshoot_request(request_id):
    """通过请求ID查找相关追踪并分析"""
    jaeger = JaegerClient()
    
    # 查找相关追踪
    traces = jaeger.search_traces(
        service_name="api-gateway",
        tags={"request_id": request_id},
        limit=1
    )
    
    if not traces or not traces.get("data") or not traces["data"]:
        return {"status": "not_found", "message": "No trace found for this request ID"}
    
    trace = traces["data"][0]
    trace_id = trace["traceID"]
    
    # 获取完整追踪详情
    full_trace = jaeger.get_trace(trace_id)
    
    # 分析追踪数据
    spans = full_trace["data"][0]["spans"]
    services_involved = set(span["process"]["serviceName"] for span in spans)
    
    # 查找错误
    error_spans = [
        span for span in spans
        if any(tag["key"] == "error" and tag["value"] == True 
               for tag in span.get("tags", []))
    ]
    
    # 查找性能问题（超过100ms的span）
    slow_spans = [
        span for span in spans
        if span["duration"] > 100000  # 微秒
    ]
    
    return {
        "status": "found",
        "trace_id": trace_id,
        "services_involved": list(services_involved),
        "span_count": len(spans),
        "error_count": len(error_spans),
        "slow_span_count": len(slow_spans),
        "jaeger_url": f"{jaeger.base_url}/trace/{trace_id}",
        "errors": [
            {
                "service": span["process"]["serviceName"],
                "operation": span["operationName"],
                "duration_ms": span["duration"] / 1000,
                "error_message": next((tag["value"] for tag in span.get("tags", []) 
                                      if tag["key"] == "error.message"), None)
            }
            for span in error_spans
        ],
        "slow_operations": [
            {
                "service": span["process"]["serviceName"],
                "operation": span["operationName"],
                "duration_ms": span["duration"] / 1000
            }
            for span in slow_spans
        ]
    }
```

## 告警与通知

### Prometheus告警规则

配置Prometheus告警规则：

```yaml
groups:
- name: service_alerts
  rules:
  # 服务可用性告警
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "服务宕机：{{ $labels.job }}"
      description: "服务 {{ $labels.job }} 实例 {{ $labels.instance }} 已经宕机超过1分钟."
      runbook_url: "https://wiki.suokelife.com/operations/runbooks/service-down"

  # API错误率告警
  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) by (service, instance) / sum(rate(http_requests_total[5m])) by (service, instance) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "高错误率：{{ $labels.service }}"
      description: "服务 {{ $labels.service }} 实例 {{ $labels.instance }} 的错误率超过5%，当前值: {{ $value | humanizePercentage }}"
      runbook_url: "https://wiki.suokelife.com/operations/runbooks/high-error-rate"

  # 响应时间告警
  - alert: SlowResponse
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (service, instance, le)) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "响应缓慢：{{ $labels.service }}"
      description: "服务 {{ $labels.service }} 实例 {{ $labels.instance }} 的95%请求响应时间超过500ms，当前值: {{ $value | humanizeDuration }}"
      runbook_url: "https://wiki.suokelife.com/operations/runbooks/slow-response"

  # 磁盘空间告警
  - alert: LowDiskSpace
    expr: node_filesystem_avail_bytes / node_filesystem_size_bytes * 100 < 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "磁盘空间不足：{{ $labels.instance }}"
      description: "节点 {{ $labels.instance }} 的文件系统 {{ $labels.mountpoint }} 可用空间低于10%，当前值: {{ $value | humanizePercentage }}"
      runbook_url: "https://wiki.suokelife.com/operations/runbooks/low-disk-space"

  # 内存使用告警
  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "内存使用率高：{{ $labels.instance }}"
      description: "节点 {{ $labels.instance }} 的内存使用率超过90%，当前值: {{ $value | humanizePercentage }}"
      runbook_url: "https://wiki.suokelife.com/operations/runbooks/high-memory-usage"

  # CPU使用告警
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "CPU使用率高：{{ $labels.instance }}"
      description: "节点 {{ $labels.instance }} 的CPU使用率超过85%，当前值: {{ $value | humanizePercentage }}"
      runbook_url: "https://wiki.suokelife.com/operations/runbooks/high-cpu-usage"

  # 智能体服务专用告警
  - alert: AIInferenceLatencyHigh
    expr: histogram_quantile(0.95, sum(rate(ai_inference_time_seconds_bucket[5m])) by (model, agent_type, le)) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "AI推理延迟高：{{ $labels.agent_type }}"
      description: "模型 {{ $labels.model }} 的智能体类型 {{ $labels.agent_type }} 的95%推理时间超过2秒，当前值: {{ $value | humanizeDuration }}"
      runbook_url: "https://wiki.suokelife.com/operations/runbooks/ai-inference-latency-high"

  # 认证服务专用告警
  - alert: HighAuthFailureRate
    expr: sum(rate(auth_login_attempts_total{success="false"}[5m])) by (instance) / sum(rate(auth_login_attempts_total[5m])) by (instance) > 0.3
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "高认证失败率"
      description: "认证服务失败率超过30%，可能存在暴力破解攻击，当前值: {{ $value | humanizePercentage }}"
      runbook_url: "https://wiki.suokelife.com/operations/runbooks/high-auth-failure-rate"
```

### 告警管理器配置

配置Alertmanager处理告警：

```yaml
global:
  resolve_timeout: 5m

# 告警通知模板
templates:
  - '/etc/alertmanager/template/*.tmpl'

# 路由规则
route:
  group_by: ['alertname', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'ops-team'
  routes:
  - match:
      severity: critical
    receiver: 'ops-team'
    continue: true
  - match:
      severity: warning
    receiver: 'dev-team'
    continue: true
  - match_re:
      service: ^(auth-service|user-service)$
    receiver: 'security-team'
  - match_re:
      service: ^(xiaoai-service|xiaoke-service|laoke-service|soer-service)$
    receiver: 'ai-team'

# 接收器配置
receivers:
- name: 'ops-team'
  webhook_configs:
  - url: 'http://dingtalk-webhook:8060/dingtalk/ops-team/send'
    send_resolved: true
  email_configs:
  - to: 'ops-team@suokelife.com'
    send_resolved: true

- name: 'dev-team'
  webhook_configs:
  - url: 'http://dingtalk-webhook:8060/dingtalk/dev-team/send'
    send_resolved: true
  email_configs:
  - to: 'dev-team@suokelife.com'
    send_resolved: true

- name: 'security-team'
  webhook_configs:
  - url: 'http://dingtalk-webhook:8060/dingtalk/security-team/send'
    send_resolved: true
  email_configs:
  - to: 'security-team@suokelife.com'
    send_resolved: true

- name: 'ai-team'
  webhook_configs:
  - url: 'http://dingtalk-webhook:8060/dingtalk/ai-team/send'
    send_resolved: true
  email_configs:
  - to: 'ai-team@suokelife.com'
    send_resolved: true

# 抑制规则
inhibit_rules:
  # 当服务宕机时抑制来自该服务的其他告警
  - source_match:
      alertname: 'ServiceDown'
    target_match_re:
      service: ^(.*)$
    equal: ['instance']
```

### 钉钉告警集成

配置钉钉告警通知：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dingtalk-webhook
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dingtalk-webhook
  template:
    metadata:
      labels:
        app: dingtalk-webhook
    spec:
      containers:
      - name: dingtalk-webhook
        image: timonwong/prometheus-webhook-dingtalk:latest
        args:
        - '--config.file=/etc/dingtalk/config.yml'
        volumeMounts:
        - name: config
          mountPath: /etc/dingtalk
      volumes:
      - name: config
        configMap:
          name: dingtalk-webhook-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: dingtalk-webhook-config
data:
  config.yml: |
    templates:
      - /etc/dingtalk/templates/default.tmpl
    
    targets:
      ops-team:
        url: https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxx
        mention:
          mobiles: ['13800138000', '13800138001']
      
      dev-team:
        url: https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxx
        mention:
          mobiles: ['13800138002', '13800138003']
      
      security-team:
        url: https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxx
        mention:
          mobiles: ['13800138004', '13800138005']
      
      ai-team:
        url: https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxx
        mention:
          mobiles: ['13800138006', '13800138007']
  
  templates/default.tmpl: |
    {{ define "dingtalk.default.message" }}
    # {{ if eq .Status "firing" }}🔥 告警触发{{ else }}✅ 告警解除{{ end }}
    
    ## 摘要: {{ .CommonAnnotations.summary }}
    
    {{ if eq .Status "firing" }}
    **告警详情:**
    {{ range .Alerts }}
    ### {{ .Labels.alertname }}
    * 级别: {{ .Labels.severity }}
    * 服务: {{ .Labels.service }}
    * 实例: {{ .Labels.instance }}
    * 详情: {{ .Annotations.description }}
    * 开始时间: {{ .StartsAt.Format "2006-01-02 15:04:05" }}
    {{ end }}
    {{ else }}
    **已解决的告警:**
    {{ range .Alerts }}
    ### {{ .Labels.alertname }}
    * 级别: {{ .Labels.severity }}
    * 服务: {{ .Labels.service }}
    * 实例: {{ .Labels.instance }}
    * 解决时间: {{ .EndsAt.Format "2006-01-02 15:04:05" }}
    {{ end }}
    {{ end }}
    
    {{ if .CommonAnnotations.runbook_url }}
    [📖 处理手册]({{ .CommonAnnotations.runbook_url }})
    {{ end }}
    {{ end }}
```

## 可视化与监控面板

### Grafana标准面板

为微服务创建标准Grafana面板：

1. **总览面板**：基础架构与服务健康状态
2. **服务详情面板**：每个服务的详细指标
3. **业务指标面板**：关键业务流程的监控
4. **告警面板**：告警历史与当前状态

服务监控面板示例（JSON模型）：

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      },
      {
        "datasource": "Prometheus",
        "enable": true,
        "expr": "changes(kube_pod_container_status_restarts_total{namespace=~\"$namespace\", pod=~\"$service.*\"}[10m]) > 0",
        "hide": false,
        "iconColor": "rgba(255, 96, 96, 1)",
        "name": "容器重启",
        "showIn": 0,
        "step": "1m",
        "tagKeys": "container_name,pod_name",
        "tags": [],
        "type": "tags"
      }
    ]
  },
  "description": "微服务详细监控面板",
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "iteration": 1636553892801,
  "links": [],
  "panels": [
    {
      "collapsed": false,
      "datasource": null,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 20,
      "panels": [],
      "title": "服务概览",
      "type": "row"
    },
    {
      "cacheTimeout": null,
      "colorBackground": false,
      "colorPostfix": false,
      "colorPrefix": false,
      "colorValue": true,
      "colors": [
        "#299c46",
        "rgba(237, 129, 40, 0.89)",
        "#d44a3a"
      ],
      "datasource": "Prometheus",
      "decimals": 0,
      "format": "none",
      "gauge": {
        "maxValue": 100,
        "minValue": 0,
        "show": false,
        "thresholdLabels": false,
        "thresholdMarkers": true
      },
      "gridPos": {
        "h": 5,
        "w": 6,
        "x": 0,
        "y": 1
      },
      "id": 2,
      "interval": null,
      "links": [],
      "mappingType": 1,
      "mappingTypes": [],
      "maxDataPoints": 100,
      "nullPointMode": "connected",
      "nullText": null,
      "postfix": "",
      "postfixFontSize": "50%",
      "prefix": "",
      "prefixFontSize": "50%",
      "rangeMaps": [],
      "sparkline": {
        "fillColor": "rgba(31, 118, 189, 0.18)",
        "full": false,
        "lineColor": "rgb(31, 120, 193)",
        "show": true
      },
      "tableColumn": "",
      "targets": [
        {
          "expr": "sum(rate(app_request_count_total{service=\"$service\"}[5m]))",
          "instant": false,
          "intervalFactor": 1,
          "legendFormat": "",
          "refId": "A"
        }
      ],
      "thresholds": "300,600",
      "title": "请求率（每秒）",
      "type": "singlestat",
      "valueFontSize": "80%",
      "valueMaps": [],
      "valueName": "current"
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "decimals": 2,
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 6
      },
      "hiddenSeries": false,
      "id": 6,
      "legend": {
        "alignAsTable": true,
        "avg": true,
        "current": true,
        "max": true,
        "min": false,
        "rightSide": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "links": [],
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 5,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(app_request_latency_seconds_bucket{service=\"$service\"}[5m])) by (le))",
          "format": "time_series",
          "intervalFactor": 1,
          "legendFormat": "P95",
          "refId": "A"
        },
        {
          "expr": "histogram_quantile(0.50, sum(rate(app_request_latency_seconds_bucket{service=\"$service\"}[5m])) by (le))",
          "format": "time_series",
          "intervalFactor": 1,
          "legendFormat": "P50",
          "refId": "B"
        },
        {
          "expr": "sum(rate(app_request_latency_seconds_sum{service=\"$service\"}[5m])) / sum(rate(app_request_latency_seconds_count{service=\"$service\"}[5m]))",
          "format": "time_series",
          "intervalFactor": 1,
          "legendFormat": "平均",
          "refId": "C"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "响应时间",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "s",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": "0",
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "refresh": "10s",
  "schemaVersion": 22,
  "style": "dark",
  "tags": ["microservice", "suokelife"],
  "templating": {
    "list": [
      {
        "allValue": null,
        "current": {},
        "datasource": "Prometheus",
        "definition": "label_values(app_request_count_total, service)",
        "hide": 0,
        "includeAll": false,
        "label": "服务",
        "multi": false,
        "name": "service",
        "options": [],
        "query": "label_values(app_request_count_total, service)",
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "sort": 1,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      },
      {
        "allValue": null,
        "current": {},
        "datasource": "Prometheus",
        "definition": "label_values(kube_pod_info, namespace)",
        "hide": 0,
        "includeAll": false,
        "label": "命名空间",
        "multi": false,
        "name": "namespace",
        "options": [],
        "query": "label_values(kube_pod_info, namespace)",
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "sort": 1,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      }
    ]
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ],
    "time_options": [
      "5m",
      "15m",
      "1h",
      "6h",
      "12h",
      "24h",
      "2d",
      "7d",
      "30d"
    ]
  },
  "timezone": "",
  "title": "微服务监控面板 - $service",
  "uid": "microservice-detail",
  "version": 1
}
```