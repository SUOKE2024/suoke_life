# 索克生活 - 监控告警系统

## 系统概述

### 监控目标
建立全面的监控告警体系，确保索克生活平台的稳定运行，及时发现和处理各类异常情况。

### 监控架构
- **数据收集**: Prometheus + Node Exporter + Application Metrics
- **数据存储**: Prometheus TSDB + InfluxDB
- **数据可视化**: Grafana Dashboard
- **告警管理**: Alertmanager + PagerDuty
- **日志分析**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **APM监控**: Jaeger + OpenTelemetry

## 监控指标体系

### 1. 基础设施监控

#### 1.1 服务器监控
- **CPU使用率**: 平均使用率、峰值使用率
- **内存使用率**: 物理内存、虚拟内存、缓存使用
- **磁盘使用率**: 磁盘空间、I/O性能、读写延迟
- **网络监控**: 带宽使用、网络延迟、丢包率
- **系统负载**: Load Average、进程数量

#### 1.2 Kubernetes监控
- **集群状态**: 节点状态、Pod状态、服务状态
- **资源使用**: CPU/内存请求和限制、存储使用
- **网络监控**: Service网络、Ingress流量
- **事件监控**: Pod重启、调度失败、资源不足

#### 1.3 数据库监控
- **PostgreSQL监控**:
  - 连接数、活跃连接、慢查询
  - 数据库大小、表大小、索引使用
  - 锁等待、死锁检测
  - 复制延迟、备份状态

- **Redis监控**:
  - 内存使用、键数量、过期键
  - 命令执行统计、慢日志
  - 主从同步状态、集群状态

### 2. 应用性能监控

#### 2.1 API网关监控
- **请求指标**: QPS、响应时间、错误率
- **状态码分布**: 2xx、4xx、5xx状态码统计
- **端点性能**: 各API端点的性能指标
- **限流统计**: 限流触发次数、被限流的请求

#### 2.2 智能体服务监控
- **小艾服务**:
  - 对话响应时间、准确率
  - AI模型推理时间、GPU使用率
  - 用户会话数、并发对话数

- **小克服务**:
  - 数据分析任务数、处理时间
  - 预测准确率、模型性能
  - 数据处理吞吐量

- **老克服务**:
  - 诊断请求数、诊断时间
  - 中医知识库查询性能
  - 辨证准确率统计

- **索儿服务**:
  - 生活管理任务数、完成率
  - 用户交互频率、满意度
  - 推荐系统性能

#### 2.3 业务服务监控
- **用户管理服务**:
  - 用户注册/登录成功率
  - 用户活跃度、留存率
  - 认证失败次数

- **健康数据服务**:
  - 数据采集频率、数据质量
  - 存储使用量、查询性能
  - 数据同步状态

- **知识服务**:
  - 知识库查询性能
  - 知识更新频率
  - 搜索准确率

### 3. 业务指标监控

#### 3.1 用户行为指标
- **用户活跃度**: DAU、MAU、用户留存率
- **功能使用**: 各功能模块使用频率
- **用户满意度**: 评分、反馈统计
- **转化率**: 注册转化、付费转化

#### 3.2 健康管理指标
- **诊断统计**: 诊断次数、诊断类型分布
- **健康数据**: 数据采集量、数据完整性
- **调理效果**: 用户健康改善指标
- **专家咨询**: 咨询次数、满意度

#### 3.3 商业化指标
- **收入指标**: 日收入、月收入、年收入
- **付费用户**: 付费用户数、ARPU值
- **产品销售**: 健康产品销售量、转化率
- **会员体系**: 会员数量、会员活跃度

### 4. 安全监控指标

#### 4.1 访问安全
- **异常登录**: 异地登录、多设备登录
- **暴力破解**: 密码尝试次数、IP黑名单
- **API安全**: 异常API调用、频率限制
- **数据访问**: 敏感数据访问审计

#### 4.2 系统安全
- **漏洞扫描**: 安全漏洞检测结果
- **入侵检测**: 异常网络流量、恶意请求
- **数据完整性**: 数据篡改检测
- **合规监控**: 数据保护法规合规性

## 告警规则配置

### 1. P0级别告警 (紧急)

#### 服务不可用
```yaml
groups:
- name: service_availability
  rules:
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
      priority: P0
    annotations:
      summary: "服务 {{ $labels.instance }} 不可用"
      description: "服务已停止响应超过1分钟"
      runbook_url: "https://docs.suoke-life.com/runbooks/service-down"
```

#### 数据库连接失败
```yaml
- alert: DatabaseConnectionFailure
  expr: postgresql_up == 0
  for: 30s
  labels:
    severity: critical
    priority: P0
  annotations:
    summary: "数据库连接失败"
    description: "PostgreSQL数据库连接失败"
```

#### 高错误率
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1
  for: 2m
  labels:
    severity: critical
    priority: P0
  annotations:
    summary: "高错误率告警"
    description: "5xx错误率超过10%"
```

### 2. P1级别告警 (高优先级)

#### 响应时间过长
```yaml
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
  for: 5m
  labels:
    severity: warning
    priority: P1
  annotations:
    summary: "响应时间过长"
    description: "95%分位响应时间超过2秒"
```

#### 内存使用率过高
```yaml
- alert: HighMemoryUsage
  expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
  for: 5m
  labels:
    severity: warning
    priority: P1
  annotations:
    summary: "内存使用率过高"
    description: "内存使用率超过85%"
```

#### CPU使用率过高
```yaml
- alert: HighCPUUsage
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 10m
  labels:
    severity: warning
    priority: P1
  annotations:
    summary: "CPU使用率过高"
    description: "CPU使用率超过80%"
```

### 3. P2级别告警 (中等优先级)

#### 磁盘空间不足
```yaml
- alert: DiskSpaceLow
  expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 80
  for: 15m
  labels:
    severity: warning
    priority: P2
  annotations:
    summary: "磁盘空间不足"
    description: "磁盘使用率超过80%"
```

#### 连接数过多
```yaml
- alert: TooManyConnections
  expr: postgresql_stat_database_numbackends > 80
  for: 10m
  labels:
    severity: warning
    priority: P2
  annotations:
    summary: "数据库连接数过多"
    description: "数据库连接数超过80"
```

### 4. P3级别告警 (低优先级)

#### 慢查询增多
```yaml
- alert: SlowQueryIncrease
  expr: increase(postgresql_stat_database_tup_fetched[1h]) > 1000
  for: 30m
  labels:
    severity: info
    priority: P3
  annotations:
    summary: "慢查询增多"
    description: "慢查询数量在过去1小时内增加超过1000"
```

## 告警通知配置

### 1. 通知渠道

#### 即时通知
- **钉钉/企业微信**: P0、P1级别告警
- **短信**: P0级别告警
- **电话**: P0级别告警（5分钟内未确认）
- **邮件**: 所有级别告警

#### 通知配置
```yaml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'
  routes:
  - match:
      priority: P0
    receiver: 'critical-alerts'
    group_wait: 0s
    repeat_interval: 5m
  - match:
      priority: P1
    receiver: 'warning-alerts'
    repeat_interval: 15m
  - match:
      priority: P2
    receiver: 'info-alerts'
    repeat_interval: 1h

receivers:
- name: 'critical-alerts'
  webhook_configs:
  - url: 'https://hooks.dingtalk.com/critical'
  - url: 'https://sms.provider.com/send'
  - url: 'https://voice.provider.com/call'
  email_configs:
  - to: 'oncall@suoke-life.com'
    subject: '[P0] {{ .GroupLabels.alertname }}'

- name: 'warning-alerts'
  webhook_configs:
  - url: 'https://hooks.dingtalk.com/warning'
  email_configs:
  - to: 'team@suoke-life.com'
    subject: '[P1] {{ .GroupLabels.alertname }}'
```

### 2. 值班制度

#### 值班安排
- **7x24小时值班**: 确保随时有人响应P0告警
- **值班轮换**: 每周轮换，确保负载均衡
- **升级机制**: P0告警5分钟内无响应自动升级
- **备用联系**: 主值班人员无法联系时的备用方案

#### 响应时间要求
- **P0告警**: 5分钟内响应，15分钟内开始处理
- **P1告警**: 30分钟内响应，2小时内开始处理
- **P2告警**: 2小时内响应，1个工作日内处理
- **P3告警**: 1个工作日内响应，3个工作日内处理

## 监控面板配置

### 1. 系统概览面板

#### 关键指标
- 系统整体健康状态
- 服务可用性统计
- 关键业务指标
- 告警统计

#### 面板配置
```json
{
  "dashboard": {
    "title": "索克生活系统概览",
    "panels": [
      {
        "title": "服务状态",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{ instance }}"
          }
        ]
      },
      {
        "title": "请求量",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ service }}"
          }
        ]
      },
      {
        "title": "响应时间",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### 2. 智能体监控面板

#### 小艾服务面板
- 对话会话数量
- 响应时间分布
- AI模型性能
- 用户满意度

#### 老克服务面板
- 诊断请求统计
- 辨证准确率
- 知识库查询性能
- 中医专家在线状态

### 3. 业务监控面板

#### 用户行为面板
- 实时在线用户数
- 用户注册/登录趋势
- 功能使用热力图
- 用户地域分布

#### 健康管理面板
- 健康数据采集统计
- 诊断类型分布
- 调理方案执行率
- 健康改善趋势

## 日志管理

### 1. 日志收集

#### 应用日志
- **结构化日志**: JSON格式，包含时间戳、级别、消息、上下文
- **日志级别**: ERROR、WARN、INFO、DEBUG
- **敏感信息**: 自动脱敏处理
- **日志轮转**: 按大小和时间轮转

#### 系统日志
- **系统事件**: 服务启动/停止、配置变更
- **安全日志**: 登录尝试、权限变更、异常访问
- **审计日志**: 数据访问、操作记录
- **性能日志**: 慢查询、长时间操作

### 2. 日志分析

#### ELK配置
```yaml
# Logstash配置
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "suoke-life" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    if [level] == "ERROR" {
      mutate {
        add_tag => [ "error" ]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "suoke-life-%{+YYYY.MM.dd}"
  }
}
```

#### 日志告警
- **错误日志激增**: 5分钟内错误日志超过阈值
- **异常模式**: 检测异常的日志模式
- **安全事件**: 检测可疑的安全相关日志
- **性能问题**: 检测性能相关的日志

## 性能监控

### 1. APM监控

#### 分布式追踪
- **Jaeger配置**: 追踪微服务间的调用链
- **OpenTelemetry**: 统一的可观测性标准
- **采样策略**: 智能采样，减少性能影响
- **追踪分析**: 识别性能瓶颈和异常

#### 代码级监控
- **方法级性能**: 关键方法的执行时间
- **数据库查询**: SQL查询性能分析
- **外部调用**: 第三方API调用监控
- **内存分析**: 内存使用和泄漏检测

### 2. 用户体验监控

#### 前端监控
- **页面加载时间**: 首屏时间、完全加载时间
- **用户交互**: 点击响应时间、操作成功率
- **错误监控**: JavaScript错误、网络错误
- **性能指标**: Core Web Vitals

#### 移动端监控
- **应用性能**: 启动时间、内存使用、电池消耗
- **网络性能**: 请求成功率、网络延迟
- **崩溃监控**: 应用崩溃率、崩溃原因分析
- **用户行为**: 页面访问路径、功能使用统计

## 容量规划

### 1. 资源预测

#### 历史数据分析
- **趋势分析**: 基于历史数据预测资源需求
- **季节性模式**: 识别业务的季节性变化
- **增长预测**: 预测用户增长对资源的影响
- **峰值预测**: 预测业务峰值时的资源需求

#### 容量模型
- **CPU模型**: 基于请求量预测CPU需求
- **内存模型**: 基于用户数预测内存需求
- **存储模型**: 基于数据增长预测存储需求
- **网络模型**: 基于流量预测网络带宽需求

### 2. 自动扩缩容

#### HPA配置
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### VPA配置
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: xiaoai-service-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: xiaoai-service
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: xiaoai-service
      maxAllowed:
        cpu: 2
        memory: 4Gi
      minAllowed:
        cpu: 100m
        memory: 128Mi
```

## 故障处理

### 1. 故障响应流程

#### 告警接收
1. **告警确认**: 值班人员确认告警
2. **初步评估**: 评估故障影响范围和严重程度
3. **团队通知**: 通知相关技术团队
4. **状态更新**: 更新故障处理状态

#### 故障处理
1. **问题定位**: 使用监控数据快速定位问题
2. **临时修复**: 实施临时解决方案恢复服务
3. **根因分析**: 深入分析故障根本原因
4. **永久修复**: 实施永久解决方案

#### 故障复盘
1. **时间线整理**: 整理故障发生和处理的完整时间线
2. **影响评估**: 评估故障对业务和用户的影响
3. **改进措施**: 制定预防类似故障的改进措施
4. **文档更新**: 更新运维文档和应急预案

### 2. 应急预案

#### 服务降级
- **智能体服务**: 降级到基础功能模式
- **诊断服务**: 使用缓存的诊断结果
- **推荐服务**: 使用预设的推荐内容
- **支付服务**: 暂停非关键支付功能

#### 流量控制
- **限流策略**: 动态调整API限流阈值
- **熔断机制**: 自动熔断异常服务
- **负载均衡**: 调整流量分配策略
- **CDN配置**: 增加静态资源缓存时间

## 监控系统维护

### 1. 定期维护

#### 数据清理
- **指标数据**: 定期清理过期的监控数据
- **日志数据**: 按保留策略清理历史日志
- **告警历史**: 清理过期的告警记录
- **面板优化**: 定期优化监控面板性能

#### 配置更新
- **告警规则**: 根据业务变化调整告警规则
- **监控指标**: 添加新的业务监控指标
- **面板配置**: 更新监控面板配置
- **权限管理**: 更新监控系统访问权限

### 2. 系统优化

#### 性能优化
- **查询优化**: 优化Prometheus查询性能
- **存储优化**: 优化时序数据存储
- **网络优化**: 优化监控数据传输
- **缓存策略**: 优化监控面板缓存

#### 可靠性提升
- **高可用部署**: 监控系统高可用配置
- **备份策略**: 监控配置和数据备份
- **灾难恢复**: 监控系统灾难恢复预案
- **监控监控**: 监控系统自身的监控

---

**监控负责人**: 运维经理  
**技术负责人**: SRE工程师  
**业务负责人**: 产品经理  
**更新频率**: 每月评估和更新 