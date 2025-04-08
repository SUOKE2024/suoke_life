# 知识库服务部署指南

本文档详细说明了知识库服务的部署步骤和解决方案。

## 目录结构

```
/k8s
  ├── deployment.yaml    # 主要部署清单
  ├── milvus.yaml        # Milvus向量数据库配置
  ├── postgres.yaml      # PostgreSQL数据库配置
  ├── monitoring.yaml    # 监控和日志配置
  └── backup.yaml        # 备份策略配置
/scripts
  ├── build-image.sh     # 镜像构建脚本
  └── kb-health-check.sh # 健康检查脚本
```

## 部署步骤

### 1. 准备依赖服务

在部署知识库服务前，需要先部署其依赖的数据库和向量存储服务：

```bash
# 创建PostgreSQL数据库
kubectl apply -f k8s/postgres.yaml

# 创建Milvus向量数据库
kubectl apply -f k8s/milvus.yaml

# 检查服务状态
kubectl get pods -n suoke-prod -l app=postgres
kubectl get pods -n suoke-prod -l app=milvus

# 等待依赖服务就绪
```

### 2. 构建并推送镜像

使用提供的脚本构建并推送知识库服务镜像：

```bash
# 设置镜像仓库凭证
export REGISTRY_USER=你的用户名
export REGISTRY_PASSWORD=你的密码

# 构建并推送镜像
./scripts/build-image.sh
```

### 3. 部署知识库服务

使用完整的部署配置部署知识库服务：

```bash
# 删除临时部署（如果存在）
kubectl delete deployment knowledge-base-service -n suoke-prod

# 应用正式部署
kubectl apply -f k8s/deployment.yaml

# 检查部署状态
kubectl get pods -l app=knowledge-base-service -n suoke-prod
```

### 4. 设置监控和备份

部署监控和备份配置：

```bash
# 部署监控配置
kubectl apply -f k8s/monitoring.yaml

# 部署备份策略
kubectl apply -f k8s/backup.yaml
```

## 故障排查

如果部署失败或服务不可用，可以执行以下步骤：

### 检查服务健康状态

使用健康检查脚本验证服务状态：

```bash
./scripts/kb-health-check.sh
```

### 查看日志

```bash
# 查看服务日志
kubectl logs -l app=knowledge-base-service -n suoke-prod

# 查看PostgreSQL日志
kubectl logs -l app=postgres -n suoke-prod

# 查看Milvus日志
kubectl logs -l app=milvus -n suoke-prod
```

### 重启服务

```bash
# 重启服务
kubectl rollout restart deployment knowledge-base-service -n suoke-prod

# 查看重启进度
kubectl rollout status deployment knowledge-base-service -n suoke-prod
```

### 回滚到上一版本

```bash
# 回滚到上一个稳定版本
kubectl rollout undo deployment knowledge-base-service -n suoke-prod
```

## 维护操作

### 手动备份数据

```bash
# 手动触发数据库备份
kubectl create job --from=cronjob/knowledge-base-backup knowledge-base-manual-backup -n suoke-prod

# 手动触发配置备份
kubectl create job --from=cronjob/knowledge-base-config-backup knowledge-base-config-manual-backup -n suoke-prod
```

### 扩展服务实例

```bash
# 扩展实例数量
kubectl scale deployment knowledge-base-service --replicas=2 -n suoke-prod
```

### 查看资源使用情况

```bash
# 查看资源使用情况
kubectl top pods -l app=knowledge-base-service -n suoke-prod
```