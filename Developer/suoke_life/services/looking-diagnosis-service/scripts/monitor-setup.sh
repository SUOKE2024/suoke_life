#!/bin/bash
set -e

echo "开始生成望诊服务的监控配置..."

# 创建目录结构
mkdir -p ./prometheus/dashboards

# 创建Grafana仪表板配置
cat > ./prometheus/grafana-dashboards.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'LookingDiagnosisDashboards'
    orgId: 1
    folder: '望诊服务'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards/looking-diagnosis
      foldersFromFilesStructure: true
EOF

echo "已生成Grafana仪表板提供者配置"

# 创建Grafana仪表板JSON
cat > ./prometheus/dashboards/looking-diagnosis-overview.json << 'EOF'
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "注释",
        "type": "dashboard"
      },
      {
        "datasource": "Prometheus",
        "enable": true,
        "expr": "changes(looking_diagnosis_service_deployments_total{namespace=~\"$namespace\"}[1m]) > 0",
        "hide": false,
        "iconColor": "rgba(255, 96, 96, 1)",
        "limit": 100,
        "name": "部署",
        "showIn": 0,
        "step": "1m",
        "tagKeys": "instance,pod",
        "tags": [],
        "titleFormat": "部署更新",
        "type": "tags"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "iteration": 1631234567890,
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
      "id": 1,
      "panels": [],
      "title": "服务概览",
      "type": "row"
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "links": []
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 1
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "alignAsTable": false,
        "avg": true,
        "current": true,
        "max": true,
        "min": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "histogram_quantile(0.5, sum(rate(http_request_duration_seconds_bucket{service=\"looking-diagnosis-service\", namespace=~\"$namespace\"}[5m])) by (le, path))",
          "interval": "",
          "legendFormat": "p50 {{path}}",
          "refId": "A"
        },
        {
          "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=\"looking-diagnosis-service\", namespace=~\"$namespace\"}[5m])) by (le, path))",
          "interval": "",
          "legendFormat": "p95 {{path}}",
          "refId": "B"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "API响应时间",
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
          "label": "响应时间",
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
      },
      "description": "API请求的p50和p95响应时间，按路径分组"
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "links": []
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 1
      },
      "hiddenSeries": false,
      "id": 3,
      "legend": {
        "alignAsTable": false,
        "avg": true,
        "current": true,
        "max": true,
        "min": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{service=\"looking-diagnosis-service\", namespace=~\"$namespace\"}[5m])) by (path, method)",
          "interval": "",
          "legendFormat": "{{method}} {{path}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "请求速率",
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
          "format": "reqps",
          "label": "请求/秒",
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
      },
      "description": "每秒API请求数，按路径和方法分组"
    }
  ],
  "schemaVersion": 27,
  "style": "dark",
  "tags": [
    "looking-diagnosis",
    "望诊服务",
    "四诊",
    "索克"
  ],
  "templating": {
    "list": [
      {
        "allValue": null,
        "current": {
          "selected": false,
          "text": "suoke",
          "value": "suoke"
        },
        "datasource": "Prometheus",
        "definition": "label_values(kube_namespace_created, namespace)",
        "description": null,
        "error": null,
        "hide": 0,
        "includeAll": false,
        "label": "命名空间",
        "multi": false,
        "name": "namespace",
        "options": [],
        "query": {
          "query": "label_values(kube_namespace_created, namespace)",
          "refId": "StandardVariableQuery"
        },
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
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
    ]
  },
  "timezone": "browser",
  "title": "望诊服务概览",
  "uid": "looking-diagnosis-overview",
  "version": 1
}
EOF

echo "已生成Grafana仪表板JSON配置"

# 创建Prometheus告警规则
cat > ./prometheus/rules.yaml << 'EOF'
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: looking-diagnosis-service-rules
  labels:
    app: looking-diagnosis-service
    prometheus: app-prometheus
    role: alert-rules
spec:
  groups:
  - name: looking-diagnosis-service.alerts
    rules:
    - alert: LookingDiagnosisHighErrorRate
      expr: sum(rate(http_requests_total{service="looking-diagnosis-service", status_code=~"5.."}[5m])) / sum(rate(http_requests_total{service="looking-diagnosis-service"}[5m])) > 0.05
      for: 5m
      labels:
        severity: warning
        team: four-diagnosis
      annotations:
        summary: "望诊服务错误率过高"
        description: "望诊服务的错误率超过5%，已持续{{ $value | humanizePercentage }}超过5分钟。"
        runbook_url: "https://wiki.suoke.life/ops/looking-diagnosis/runbooks/high-error-rate"
        dashboard_url: "https://grafana.suoke.life/d/looking-diagnosis-overview"

    - alert: LookingDiagnosisHighLatency
      expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service="looking-diagnosis-service"}[5m])) by (le)) > 1.5
      for: 5m
      labels:
        severity: warning
        team: four-diagnosis
      annotations:
        summary: "望诊服务响应延迟过高"
        description: "望诊服务的P95响应时间超过1.5秒，当前值为{{ $value }}秒。"
        runbook_url: "https://wiki.suoke.life/ops/looking-diagnosis/runbooks/high-latency"
        dashboard_url: "https://grafana.suoke.life/d/looking-diagnosis-overview"

    - alert: LookingDiagnosisHighMemoryUsage
      expr: sum(container_memory_usage_bytes{container="looking-diagnosis"}) / sum(kube_pod_container_resource_limits_memory_bytes{container="looking-diagnosis"}) > 0.85
      for: 10m
      labels:
        severity: warning
        team: four-diagnosis
      annotations:
        summary: "望诊服务内存使用率过高"
        description: "望诊服务的内存使用率超过85%，当前值为{{ $value | humanizePercentage }}。"
        runbook_url: "https://wiki.suoke.life/ops/looking-diagnosis/runbooks/high-memory-usage"
        dashboard_url: "https://grafana.suoke.life/d/looking-diagnosis-overview"
EOF

echo "已生成Prometheus告警规则"

# 创建ServiceMonitor
cat > ./prometheus/service-monitor.yaml << 'EOF'
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: looking-diagnosis-service-monitor
  labels:
    app: looking-diagnosis-service
    release: prometheus
spec:
  selector:
    matchLabels:
      app: looking-diagnosis-service
  namespaceSelector:
    matchNames:
      - suoke
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
      scrapeTimeout: 10s
      honorLabels: true
      metricRelabelings:
        - sourceLabels: [__name__]
          regex: 'http_.*'
          action: keep
        - sourceLabels: [__name__]
          regex: 'nodejs_.*'
          action: keep
        - sourceLabels: [__name__]
          regex: 'looking_diagnosis_.*'
          action: keep
  targetLabels:
    - app
    - version
EOF

echo "已生成ServiceMonitor配置"

echo "监控配置已成功生成"
echo "请使用以下命令将prometheus目录应用到kubernetes集群："
echo "kubectl apply -f ./prometheus/ -n suoke"