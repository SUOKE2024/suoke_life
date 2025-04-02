# 用户服务部署文档

## 目录

1. [简介](#简介)
2. [部署架构](#部署架构)
3. [环境要求](#环境要求)
4. [容器化配置](#容器化配置)
5. [Kubernetes资源](#kubernetes资源)
6. [持续集成/部署](#持续集成部署)
7. [监控和日志](#监控和日志)
8. [自动扩缩容](#自动扩缩容)
9. [网络安全](#网络安全)
10. [数据备份](#数据备份)
11. [常见问题与故障排除](#常见问题与故障排除)
12. [维护操作](#维护操作)
13. [安全考虑](#安全考虑)

## 简介

用户服务(user-service)是索克生活平台的核心服务之一，负责用户管理、认证授权、用户资料和偏好设置管理。

## 部署架构

用户服务采用微服务架构，与其他服务通过REST API进行通信。主要依赖服务包括：

- MongoDB - 存储用户数据和配置信息
- Redis - 用于缓存和会话管理
- 知识库服务 - 用于用户兴趣和知识查询
- 知识图谱服务 - 用于用户关系网络分析

## 环境要求

- Kubernetes 1.20+
- Istio 1.10+
- Prometheus Operator
- MongoDB 5.0+
- Redis 6.2+

## 容器化配置

### Dockerfile

Dockerfile实现了多阶段构建，包括开发环境和生产环境配置：
- 使用Node.js 18 Alpine作为基础镜像
- 非root用户运行
- 健康检查配置
- 时区设置为上海
- 启用只读文件系统

### 启动脚本

`docker-entrypoint.sh`负责服务启动前的准备工作，包括：

- 检查必要的环境变量
- 等待依赖服务（Redis、MongoDB）就绪
- 应用数据库迁移
- 设置优雅关闭处理

### 本地开发环境

使用`docker-compose.yml`可以在本地快速启动开发环境，包含服务本身及所有依赖。

命令：

```bash
# 启动本地开发环境
docker-compose up -d

# 查看服务日志
docker-compose logs -f user-service

# 关闭环境
docker-compose down
```

## Kubernetes资源

所有Kubernetes资源定义文件位于`k8s/`目录，通过Kustomize统一管理。

### 主要资源

- **deployment.yaml** - 定义Pod规格、副本数量、环境变量等
- **service.yaml** - 定义服务访问方式
- **pvc.yaml** - 持久化存储配置
- **serviceaccount.yaml** - 服务账号及权限配置
- **istio-config.yaml** - Istio VirtualService和DestinationRule配置
- **opentelemetry-config.yaml** - OpenTelemetry采集配置
- **network-policy.yaml** - 网络策略配置

### 自动扩缩容

- **hpa.yaml** - HorizontalPodAutoscaler配置，基于CPU和内存使用率自动扩缩容：
  - 最小副本数：2
  - 最大副本数：5
  - CPU目标利用率：70%
  - 内存目标利用率：80%

### 高可用配置

- **pdb.yaml** - PodDisruptionBudget配置，确保维护期间的服务可用性：
  - 保证至少有1个Pod可用
  - 防止Kubernetes节点维护导致服务中断

### 数据备份

- **backup-cronjob.yaml** - 定期备份配置：
  - 每天凌晨2点执行
  - 备份MongoDB数据和上传文件
  - 保留最近30天的备份
  - 备份存储在专用PVC中

- **backup-pvc.yaml** - 备份专用存储卷：
  - 10Gi存储空间
  - ReadWriteOnce访问模式

### 监控配置

- **servicemonitor.yaml** - Prometheus监控配置：
  - 每15秒抓取一次指标
  - 监控HTTP请求持续时间、API调用、缓存命中率等关键指标

### 网络安全

- **network-policy.yaml** - 网络策略配置：
  - 限制进入流量，只允许API网关和认证服务访问
  - 控制出口流量，只允许访问已知的依赖服务

## 持续集成/部署

用户服务使用GitOps流程进行部署，通过ArgoCD监控代码仓库变化并自动同步到集群。

### CI工作流

1. 代码提交触发GitHub Actions
2. 运行单元测试和集成测试
3. 构建Docker镜像并推送到镜像仓库
4. 更新部署清单中的镜像标签
5. ArgoCD检测到变更并同步到集群

### 部署操作

执行部署：

```bash
# 应用所有资源
kubectl apply -k services/user-service/k8s

# 单独更新部署
kubectl apply -f services/user-service/k8s/deployment.yaml
```

## 监控和日志

### 监控

服务暴露Prometheus格式的指标，通过ServiceMonitor收集，包括：

- HTTP请求持续时间
- API调用计数
- 用户活动指标
- Redis缓存命中率
- 内存使用量
- CPU使用率

### 日志

服务日志被整合到EFK/ELK堆栈，支持结构化JSON日志输出。

日志路径：
- 容器内：`/app/logs`
- 持久化：通过PVC持久保存

## 自动扩缩容

服务配置了HorizontalPodAutoscaler，支持基于多种指标的自动扩缩容：

### 扩容行为

- 当CPU利用率超过70%或内存利用率超过80%时触发扩容
- 扩容冷却期为0秒，快速响应流量增加

### 缩容行为

- 缩容更保守，冷却期为300秒
- 每次最多减少一个Pod

### 手动扩缩容

紧急情况下的手动扩缩容：

```bash
# 手动扩展到4个副本
kubectl scale deployment user-service -n suoke --replicas=4
```

## 网络安全

通过NetworkPolicy限制Pod的网络通信：

- 只允许来自API网关和认证服务的入站流量
- 出站流量限制为只能访问MongoDB、Redis和其他必要服务

## 数据备份

### 自动备份

通过CronJob实现每日自动备份：

```bash
# 查看备份作业状态
kubectl get cronjobs -n suoke

# 查看备份历史
kubectl get jobs -n suoke | grep user-service-backup

# 手动触发备份
kubectl create job --from=cronjob/user-service-backup user-service-backup-manual -n suoke
```

### 备份恢复

从备份恢复数据：

```bash
# 查看可用备份
kubectl exec -it user-service-backup-pod -n suoke -- ls -la /backups

# 恢复指定备份
kubectl exec -it user-service-backup-pod -n suoke -- /bin/bash -c "mongorestore --uri \$MONGODB_URI --dir /backups/user-service/mongo_20230515_020101"

# 恢复上传文件
kubectl exec -it user-service-backup-pod -n suoke -- /bin/bash -c "tar -xzf /backups/user-service/uploads_20230515_020101.tar.gz -C /restore"
```

## 常见问题与故障排除

### 健康检查失败

检查依赖服务是否可用：

```bash
# 检查Redis连接
kubectl exec -it user-service-pod -n suoke -- redis-cli -h $REDIS_HOST -p $REDIS_PORT ping

# 检查MongoDB连接
kubectl exec -it user-service-pod -n suoke -- mongo --eval "db.adminCommand('ping')" $MONGODB_URI
```

### 服务启动失败

检查日志和事件：

```bash
# 查看Pod事件
kubectl describe pod user-service-pod -n suoke

# 查看容器日志
kubectl logs user-service-pod -n suoke
```

### 认证问题

检查JWT配置：

```bash
# 检查JWT密钥是否正确配置
kubectl describe secret user-service-secrets -n suoke
```

### 性能问题

检查资源使用情况：

```bash
# 查看Pod资源使用情况
kubectl top pod -l app=user-service -n suoke

# 查看详细性能指标
kubectl port-forward service/prometheus-operated -n monitoring 9090:9090
```

## 维护操作

### 滚动更新

部署新版本时自动执行滚动更新：

```bash
# 更新镜像
kubectl set image deployment/user-service user-service=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/user-service:v1.2.3 -n suoke

# 查看更新状态
kubectl rollout status deployment/user-service -n suoke
```

### 回滚

如果新版本有问题，可以回滚到之前的版本：

```bash
# 查看部署历史
kubectl rollout history deployment/user-service -n suoke

# 回滚到上一版本
kubectl rollout undo deployment/user-service -n suoke

# 回滚到特定版本
kubectl rollout undo deployment/user-service -n suoke --to-revision=2
```

### 配置更新

更新ConfigMap配置：

```bash
# 更新ConfigMap
kubectl edit configmap user-service-config -n suoke

# 重启Pods应用新配置
kubectl rollout restart deployment/user-service -n suoke
```

## 安全考虑

### 敏感信息管理

所有敏感配置都通过Kubernetes Secrets管理，而不是直接嵌入在配置文件中：

- 数据库凭证
- JWT密钥
- API密钥

### 容器安全

- 容器以非root用户运行 (UID 1000)
- 使用只读文件系统，只有必要的目录有写入权限
- 资源限制防止DoS攻击

### 数据隐私

- 实施数据加密存储
- 遵循数据最小化原则
- 实现结构化访问控制