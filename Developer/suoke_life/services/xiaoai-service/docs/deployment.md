# 小艾服务部署文档

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

小艾服务(xiaoai-service)是索克生活平台的AI健康诊断协调服务，主要负责整合四诊(望闻问切)数据，提供综合健康评估和建议。

## 部署架构

小艾服务采用微服务架构，与其他服务通过REST API进行通信。主要依赖服务包括：

- MongoDB - 存储用户健康档案和诊断历史
- Redis - 用于缓存和消息队列
- 四诊服务 - 包括望诊、闻诊、问诊和切诊服务

## 环境要求

- Kubernetes 1.20+
- Istio 1.10+
- Prometheus Operator
- MongoDB 5.0+
- Redis 6.2+

## 容器化配置

### Dockerfile

项目根目录下的Dockerfile实现了多阶段构建，包括开发环境和生产环境配置。

### 启动脚本

`docker-entrypoint.sh`负责服务启动前的准备工作，包括：

- 检查必要的环境变量
- 等待依赖服务（MongoDB、Redis）就绪
- 应用数据库迁移
- 设置优雅关闭处理

### 本地开发环境

使用`docker-compose.yml`可以在本地快速启动开发环境，包含服务本身及所有依赖。

命令：

```bash
# 启动本地开发环境
docker-compose up -d

# 查看服务日志
docker-compose logs -f xiaoai-service

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

### 自动扩缩容

- **hpa.yaml** - HorizontalPodAutoscaler配置，基于CPU和内存使用率自动扩缩容：
  - 最小副本数：2
  - 最大副本数：5
  - CPU目标利用率：70%
  - 内存目标利用率：80%
  - 自定义指标：请求队列长度

### 高可用配置

- **pdb.yaml** - PodDisruptionBudget配置，确保维护期间的服务可用性：
  - 保证至少有1个Pod可用
  - 防止Kubernetes节点维护导致服务中断

### 数据备份

- **backup-cronjob.yaml** - 定期备份配置：
  - 每天凌晨2点执行
  - 备份MongoDB数据
  - 保留最近30天的备份
  - 备份存储在专用PVC中

- **backup-pvc.yaml** - 备份专用存储卷：
  - 10Gi存储空间
  - ReadWriteOnce访问模式

### 监控配置

- **servicemonitor.yaml** - Prometheus监控配置：
  - 每15秒抓取一次指标
  - 监控HTTP请求持续时间、代理处理时间、缓存命中率等关键指标

### 网络安全

- **network-policy.yaml** - 网络策略配置：
  - 限制进入流量，只允许必要的通信
  - 控制出口流量，只允许访问已知的依赖服务

## 持续集成/部署

小艾服务使用GitOps流程进行部署，通过ArgoCD监控代码仓库变化并自动同步到集群。

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
kubectl apply -k services/xiaoai-service/k8s

# 单独更新部署
kubectl apply -f services/xiaoai-service/k8s/deployment.yaml
```

## 监控和日志

### 监控

服务暴露Prometheus格式的指标，通过ServiceMonitor收集，包括：

- HTTP请求持续时间
- 代理处理时间
- 响应长度
- MongoDB查询执行时间
- Redis缓存命中率
- 内存使用量
- CPU使用率
- 队列大小

### 日志

服务日志被整合到EFK/ELK堆栈，支持结构化JSON日志输出。

日志路径：
- 容器内：`/app/logs`
- 持久化：通过PVC持久保存

## 自动扩缩容

服务配置了HorizontalPodAutoscaler，支持基于多种指标的自动扩缩容：

### 扩容行为

- 当CPU利用率超过70%或内存利用率超过80%时触发扩容
- 请求队列长度超过10时也会触发扩容
- 扩容冷却期为60秒

### 缩容行为

- 缩容更保守，冷却期为300秒
- 每次最多减少20%的Pod或单个Pod（取较小值）

### 手动扩缩容

紧急情况下的手动扩缩容：

```bash
# 手动扩展到4个副本
kubectl scale deployment xiaoai-service -n suoke --replicas=4
```

## 网络安全

通过NetworkPolicy限制Pod的网络通信：

- 只允许来自API网关和必要的内部服务的入站流量
- 出站流量限制为只能访问MongoDB、Redis和四诊服务

## 数据备份

### 自动备份

通过CronJob实现每日自动备份：

```bash
# 查看备份作业状态
kubectl get cronjobs -n suoke

# 查看备份历史
kubectl get jobs -n suoke | grep xiaoai-backup

# 手动触发备份
kubectl create job --from=cronjob/xiaoai-backup xiaoai-backup-manual -n suoke
```

### 备份恢复

从备份恢复数据：

```bash
# 查看可用备份
kubectl exec -it xiaoai-backup-pod -n suoke -- ls -la /backups

# 恢复指定备份
kubectl exec -it xiaoai-backup-pod -n suoke -- /bin/bash -c "mongorestore --uri \$MONGODB_URI --dir /backups/xiaoai/mongo_20230515_020101"
```

## 常见问题与故障排除

### 健康检查失败

检查依赖服务是否可用：

```bash
# 检查MongoDB连接
kubectl exec -it xiaoai-service-pod -n suoke -- mongo --eval "db.adminCommand('ping')" $MONGODB_URI

# 检查Redis连接
kubectl exec -it xiaoai-service-pod -n suoke -- redis-cli -u $REDIS_URL ping
```

### 服务启动失败

检查日志和事件：

```bash
# 查看Pod事件
kubectl describe pod xiaoai-service-pod -n suoke

# 查看容器日志
kubectl logs xiaoai-service-pod -n suoke
```

## 维护操作

### 滚动更新

部署新版本时自动执行滚动更新：

```bash
# 更新镜像
kubectl set image deployment/xiaoai-service xiaoai-service=docker.io/suoke/xiaoai-service:v1.2.3 -n suoke

# 查看更新状态
kubectl rollout status deployment/xiaoai-service -n suoke
```

### 回滚

如果新版本有问题，可以回滚到之前的版本：

```bash
# 查看部署历史
kubectl rollout history deployment/xiaoai-service -n suoke

# 回滚到上一版本
kubectl rollout undo deployment/xiaoai-service -n suoke

# 回滚到特定版本
kubectl rollout undo deployment/xiaoai-service -n suoke --to-revision=2
```

## 安全考虑

### 敏感信息管理

所有敏感配置都通过Kubernetes Secrets管理，而不是直接嵌入在配置文件中：

- 数据库凭证
- API密钥
- 加密密钥

### 容器安全

- 容器以非root用户运行
- 使用只读文件系统，只有必要的目录有写入权限
- 资源限制防止DoS攻击 