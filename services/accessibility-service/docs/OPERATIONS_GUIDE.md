# 无障碍服务运维指南

本文档提供无障碍服务(accessibility-service)的运维指南，包括部署、监控、故障排查和常见运维任务。

## 目录

- [部署指南](#部署指南)
- [监控指南](#监控指南)
- [日志管理](#日志管理)
- [故障排查](#故障排查)
- [常见运维任务](#常见运维任务)
- [性能调优](#性能调优)
- [安全最佳实践](#安全最佳实践)
- [灾难恢复](#灾难恢复)

## 部署指南

### 生产环境部署流程

1. **准备环境变量**

   创建 `.env.production` 文件并设置环境变量：
   
   ```bash
   cp .env.example .env.production
   # 编辑 .env.production 文件设置生产环境参数
   ```

2. **构建和部署**

   使用部署脚本：
   
   ```bash
   scripts/deploy.sh -e production -v 1.0.0 -r suoke-registry.io
   ```

3. **验证部署**

   ```bash
   # 检查Pod状态
   kubectl get pods -n suoke-ai-np -l app=accessibility-service
   
   # 验证服务可用性
   grpcurl -plaintext accessibility-service.suoke-ai-np:50051 list
   ```

### 环境特定配置

不同环境的配置存储在 `k8s/overlays/<environment>` 目录中：

- `development`: 开发环境 - 单副本、调试功能开启
- `staging`: 测试环境 - 多副本、模拟生产资源配置
- `production`: 生产环境 - 高可用配置、严格的资源限制

## 监控指南

### 关键指标

| 指标 | 描述 | 警报阈值 | 处理方法 |
|------|------|---------|---------|
| `accessibility_request_duration_seconds` | 请求处理时间 | p95 > 0.5s | 检查性能瓶颈、扩容 |
| `accessibility_error_count` | 错误计数 | > 10/分钟 | 检查日志、分析错误类型 |
| `accessibility_active_connections` | 活动连接数 | > 800 | 检查客户端行为、考虑扩容 |
| `accessibility_cpu_usage_percent` | CPU使用率 | > 80% | 优化性能或扩容 |
| `accessibility_memory_usage_bytes` | 内存使用 | > 3.5GB | 检查内存泄漏、调整限制 |

### Grafana仪表盘

访问Grafana监控仪表盘：`https://grafana.suoke.life/d/accessibility-service`

主要仪表盘包括：
- **概览**: 服务健康状态与核心指标
- **API性能**: 各API方法的详细性能数据
- **资源使用**: CPU、内存、网络IO等资源使用情况
- **错误分析**: 错误率和错误分布
- **集成健康**: 与其他服务的集成状态

### 告警规则

告警配置位于 `deploy/prometheus/rules/accessibility.yaml`。主要告警包括：

- **高错误率**: 服务错误率超过5%
- **高延迟**: 响应时间p95超过500ms
- **资源不足**: CPU或内存使用率持续高于阈值
- **集成失败**: 与其他服务通信失败率高
- **副本不足**: 可用副本数低于预期

## 日志管理

### 日志收集架构

服务日志通过以下流程收集：
1. 应用日志输出到标准输出和文件
2. Fluent Bit容器边车采集日志
3. 日志传输到Elasticsearch集群
4. Kibana提供日志查询和可视化

### 常用日志查询

在Kibana中使用以下查询检索特定日志：

- 错误日志:
  ```
  kubernetes.labels.app:accessibility-service AND log.level:ERROR
  ```

- 特定用户的日志:
  ```
  kubernetes.labels.app:accessibility-service AND json.user_id:<user_id>
  ```

- 慢请求:
  ```
  kubernetes.labels.app:accessibility-service AND json.duration_ms:>500
  ```

### 日志轮换

容器内日志文件配置了以下轮换策略：
- 大小限制: 100MB
- 保留时间: 7天
- 压缩格式: gzip

## 故障排查

### 常见问题与解决方案

#### 1. 服务启动失败

**症状**: Pod无法启动，状态为`CrashLoopBackOff`

**诊断步骤**:
```bash
kubectl logs -n suoke-ai-np -l app=accessibility-service
kubectl describe pod -n suoke-ai-np -l app=accessibility-service
```

**常见原因与解决方案**:
- 配置错误: 检查ConfigMap内容
- 数据库连接问题: 验证数据库凭据和连接
- 资源限制: 检查资源请求和限制是否合理

#### 2. 高延迟

**症状**: 请求处理时间过长，`accessibility_request_duration_seconds`指标升高

**诊断步骤**:
```bash
# 检查负载
kubectl top pod -n suoke-ai-np -l app=accessibility-service

# 查看慢请求日志
kubectl logs -n suoke-ai-np -l app=accessibility-service | grep "duration_ms"
```

**常见原因与解决方案**:
- CPU负载高: 检查是否需要扩容
- 外部服务延迟: 检查与其他服务的集成
- 模型加载慢: 检查模型缓存机制

#### 3. 内存泄漏

**症状**: 内存使用持续增长，最终OOM

**诊断步骤**:
```bash
# 监控内存使用
kubectl top pod -n suoke-ai-np -l app=accessibility-service --containers

# 检查日志中的内存警告
kubectl logs -n suoke-ai-np -l app=accessibility-service | grep "memory"
```

**解决方案**:
- 增加内存限制作为临时措施
- 检查大对象缓存配置
- 重启Pod释放内存
- 收集堆转储分析根因

### 调试模式

启用调试模式获取更详细日志：

```bash
# 编辑ConfigMap
kubectl edit cm -n suoke-ai-np accessibility-config

# 设置日志级别为DEBUG
# 在config.yaml中:
logging:
  level: DEBUG

# 应用更改
kubectl rollout restart deployment -n suoke-ai-np accessibility-service
```

### 紧急联系人

- 运维团队: ops@suoke.life
- 开发团队: accessibility-devs@suoke.life

## 常见运维任务

### 回滚部署

如需回滚到之前版本：

```bash
# 查看部署历史
kubectl rollout history deployment -n suoke-ai-np accessibility-service

# 回滚到上一版本
kubectl rollout undo deployment -n suoke-ai-np accessibility-service

# 回滚到特定版本
kubectl rollout undo deployment -n suoke-ai-np accessibility-service --to-revision=2
```

### 扩容/缩容

手动调整副本数：

```bash
# 扩容到5个副本
kubectl scale deployment -n suoke-ai-np accessibility-service --replicas=5
```

### 更新配置

1. 更新ConfigMap:
   ```bash
   kubectl edit cm -n suoke-ai-np accessibility-config
   ```

2. 重启Pod使配置生效:
   ```bash
   kubectl rollout restart deployment -n suoke-ai-np accessibility-service
   ```

### 数据库迁移

数据库架构迁移流程：

1. 创建备份
2. 应用新架构迁移
3. 验证迁移结果
4. 如有问题回滚备份

详细步骤见 `scripts/db_migration.sh`

## 性能调优

### JVM调优

为Java进程优化JVM参数：

```
-Xms1G -Xmx2G -XX:+UseG1GC -XX:MaxGCPauseMillis=200
```

### 连接池调优

数据库连接池参数:
- 最小连接数: 5
- 最大连接数: 20
- 连接超时: 30秒
- 空闲超时: 10分钟

### 资源配置指南

根据负载调整资源配置：

| 负载级别 | 副本数 | CPU请求 | 内存请求 | CPU限制 | 内存限制 |
|---------|-------|---------|----------|--------|----------|
| 低 | 2 | 0.5 | 1Gi | 1 | 2Gi |
| 中 | 3-5 | 1 | 2Gi | 2 | 4Gi |
| 高 | 8-10 | 2 | 4Gi | 4 | 8Gi |

## 安全最佳实践

### 凭据轮换流程

数据库密码轮换步骤：

1. 生成新密码
2. 更新数据库用户密码
3. 更新Kubernetes Secret
4. 重启服务使用新密码

### 安全补丁应用

关键安全更新应用流程：

1. 评估安全风险和紧急程度
2. 在测试环境验证补丁
3. 按预定维护窗口应用到生产
4. 验证服务正常运行

## 灾难恢复

### 备份策略

- 配置备份: 每次更改时备份到Git仓库
- 数据备份: 数据库每日备份，保留30天
- 模型备份: 模型文件存储在对象存储中

### 恢复流程

1. **服务恢复**
   - 使用最新镜像重新部署服务
   - 应用配置备份
   - 验证服务功能

2. **数据恢复**
   - 从备份恢复数据库
   - 验证数据完整性

### 灾难演练

每季度进行一次灾难恢复演练，测试以下场景：
- 服务完全失效恢复
- 数据库故障恢复
- 配置错误恢复 