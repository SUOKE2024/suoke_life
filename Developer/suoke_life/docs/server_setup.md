# 索克生活APP服务器设置指南

本文档详细说明了如何在阿里云ECS服务器上设置和部署索克生活APP的后端服务。

## 系统要求

- 阿里云ECS实例（推荐配置：4核8G及以上，CentOS/Ubuntu系统）
- 至少50GB可用存储空间
- 公网IP地址

## 多服务器架构

索克生活APP采用多服务器架构，根据功能划分不同角色：

### 服务器角色

| 服务器名称 | IP地址 | 角色 | 主要职责 |
|------------|----------|------|----------|
| master-node | 118.31.223.213 | 主节点/入口 | Nginx反向代理、负载均衡、SSL终止、静态资源服务 |
| suoke-core-np | 172.16.199.86 | 核心业务节点 | API网关、认证服务、用户服务等核心业务 |
| suoke-ai-np | 172.16.199.136 | AI计算节点 | AI服务、RAG服务、向量数据库等计算密集型服务 |
| suoke-db-np | 172.16.199.88 | 数据存储节点 | MySQL、MongoDB、Redis等数据存储服务 |

### 请求流向

1. 所有外部请求先到达主节点(118.31.223.213)
2. 主节点根据请求类型将流量分发到不同功能节点：
   - API请求 → 核心业务节点(172.16.199.86)
   - AI服务请求 → AI计算节点(172.16.199.136)
   - 数据查询请求 → 数据存储节点(172.16.199.88)

## 部署流程概述

1. 服务器环境初始化
2. 主节点Nginx配置
3. Kubernetes集群配置
4. 基础设施服务部署
5. 后端微服务部署
6. 配置和测试

## 1. 服务器环境初始化

### 1.1 克隆项目代码

```bash
git clone https://github.com/your-org/suoke-life.git
cd suoke-life
```

### 1.2 配置环境变量

复制示例环境变量文件并编辑：

```bash
cp .env.example .env
vi .env
```

确保填写以下关键配置：

```
# 阿里云容器镜像仓库配置
REGISTRY_URL=your-registry.cr.aliyuncs.com
REGISTRY_NAMESPACE=your-namespace
REGISTRY_USERNAME=your-username
REGISTRY_PASSWORD=your-password

# API密钥配置
GOOGLE_API_KEY=your-google-api-key
BING_API_KEY=your-bing-api-key
```

### 1.3 运行服务器初始化脚本

执行服务器初始化脚本，该脚本将自动安装和配置Docker、Kubernetes以及所需的系统依赖：

```bash
chmod +x scripts/server_setup.sh
sudo ./scripts/server_setup.sh
```

初始化过程包括：
- 系统更新和基础软件安装
- Docker和Kubernetes安装与配置
- 防火墙和安全设置
- Kubernetes集群初始化
- 监控和备份脚本配置

## 2. 主节点Nginx配置

### 2.1 Nginx安装与配置

在主节点(118.31.223.213)上，安装和配置Nginx作为反向代理：

```bash
# 安装Nginx
sudo yum install -y nginx

# 创建配置目录
sudo mkdir -p /etc/nginx/conf.d
```

### 2.2 部署Nginx配置

将项目中的Nginx配置文件复制到服务器：

```bash
# 从本地复制配置文件
chmod +x scripts/deploy/update-nginx-config.sh
./scripts/deploy/update-nginx-config.sh
```

Nginx配置将自动部署，并根据服务器角色设置以下路由规则：

- `/api/` → 核心业务节点 (172.16.199.86)
- `/auth/` → 核心业务节点 (172.16.199.86)
- `/ai/` → AI计算节点 (172.16.199.136)
- `/rag/` → AI计算节点 (172.16.199.136)
- `/data/` → 数据存储节点 (172.16.199.88)
- `/ws/` → AI计算节点 (172.16.199.136)，用于WebSocket连接

### 2.3 验证Nginx配置

验证Nginx配置是否正确：

```bash
# 测试健康检查端点
curl -I http://118.31.223.213/health
```

## 3. Kubernetes集群配置

### 3.1 配置节点选择器

为确保服务部署到正确的节点，需设置节点标签：

```bash
# 给核心业务节点添加标签
kubectl label nodes suoke-core-np kubernetes.io/hostname=suoke-core-np

# 给AI节点添加标签
kubectl label nodes suoke-ai-np kubernetes.io/hostname=suoke-ai-np

# 给数据库节点添加标签
kubectl label nodes suoke-db-np kubernetes.io/hostname=suoke-db-np
```

### 3.2 配置集群内部通信

确保节点间通信顺畅：

```bash
# 创建集群内部网络策略
kubectl apply -f scripts/deploy/kubernetes/network-policy.yaml
```

## 4. 基础设施服务部署

### 4.1 构建和推送自定义镜像

构建自定义的Redis、MySQL和MongoDB镜像，这些镜像包含针对索克生活应用优化的配置：

```bash
chmod +x scripts/build_push_custom_images.sh
./scripts/build_push_custom_images.sh
```

### 4.2 部署基础设施服务

部署基础设施服务容器（Redis、MySQL、MongoDB）：

```bash
chmod +x scripts/deploy_custom_images.sh
./scripts/deploy_custom_images.sh
```

验证基础设施服务是否正常运行：

```bash
kubectl get pods -n suoke
```

## 5. 后端微服务部署

### 5.1 部署后端微服务组件

部署索克生活APP的核心微服务组件，包括API网关、智能体服务、搜索服务等：

```bash
chmod +x scripts/deploy/deploy-to-k8s.sh
./scripts/deploy/deploy-to-k8s.sh api-gateway
./scripts/deploy/deploy-to-k8s.sh auth-service
./scripts/deploy/deploy-to-k8s.sh user-service
./scripts/deploy/deploy-to-k8s.sh rag-service
```

该脚本将部署以下微服务：
- API网关（api-gateway）→ 部署到核心业务节点
- 用户服务（user-service）→ 部署到核心业务节点
- 认证服务（auth-service）→ 部署到核心业务节点
- RAG服务（rag-service）→ 部署到AI计算节点
- 智能体协调器服务（agent-coordinator）→ 部署到AI计算节点
- 数据库服务（mongodb, mysql）→ 部署到数据存储节点

### 5.2 验证部署状态

检查所有服务是否已成功启动：

```bash
kubectl get pods -n suoke
kubectl get services -n suoke
```

所有Pod的状态应为`Running`，这表示服务已成功部署。

## 6. 配置与测试

### 6.1 访问API网关

API网关通过NodePort暴露在30080端口，可通过以下URL访问：

```
http://<服务器IP>:30080
```

### 6.2 访问Kubernetes Dashboard

Kubernetes Dashboard通过NodePort暴露在30443端口，可通过以下URL访问：

```
https://<服务器IP>:30443
```

使用服务器初始化过程中生成的访问令牌进行登录。令牌输出在初始化脚本结束时，也可通过以下命令重新获取：

```bash
SECRET_NAME=$(kubectl get serviceaccount admin-user -n kubernetes-dashboard -o jsonpath='{.secrets[0].name}')
kubectl get secret $SECRET_NAME -n kubernetes-dashboard -o jsonpath='{.data.token}' | base64 --decode
```

### 6.3 检查系统状态

使用监控脚本检查服务器状态：

```bash
sudo /opt/suoke/scripts/monitor.sh
```

使用环境检查脚本验证所有组件是否正常工作：

```bash
sudo /opt/suoke/scripts/check_env.sh
```

## 7. 维护操作

### 7.1 备份数据

手动触发备份：

```bash
sudo /opt/suoke/scripts/backup.sh
```

备份文件将保存在`/opt/suoke/backups`目录下。

### 7.2 更新服务

更新特定服务（以老克智能体为例）：

```bash
kubectl set image deployment/laoke-agent laoke-agent=${REGISTRY_URL}/${REGISTRY_NAMESPACE}/laoke-agent:new-version -n suoke
```

### 7.3 查看日志

查看特定服务的日志：

```bash
kubectl logs -f deployment/laoke-agent -n suoke
```

### 7.4 扩展服务

扩展服务的副本数（以API网关为例）：

```bash
kubectl scale deployment/api-gateway --replicas=2 -n suoke
```

## 8. 故障排除

### 8.1 Pod无法启动

检查Pod详情：

```bash
kubectl describe pod <pod-name> -n suoke
```

### 8.2 服务无法访问

检查服务端点：

```bash
kubectl get endpoints -n suoke
```

### 8.3 持久化存储问题

检查持久化卷状态：

```bash
kubectl get pv,pvc -n suoke
```

### 8.4 重启服务

重启特定服务：

```bash
kubectl rollout restart deployment/laoke-agent -n suoke
```

## 9. 安全建议

- 定期更新系统和容器镜像
- 使用强密码并定期轮换
- 限制访问Kubernetes Dashboard和API的IP地址
- 定期审查系统日志以识别潜在安全问题
- 实施网络策略以限制Pod之间的通信

## 10. 后续步骤

- 设置SSL证书以启用HTTPS
- 配置CDN加速静态资源
- 实施更详细的监控和告警系统
- 配置自动扩缩容以应对负载变化
- 优化资源分配，确保各节点资源利用率最大化
- 实施跨节点日志收集和集中监控
- 建立节点故障自动切换机制

## 11. 多服务器架构优化

### 11.1 资源监控

在主节点配置集中式监控：

```bash
# 安装Prometheus和Grafana
kubectl apply -f scripts/deploy/kubernetes/monitoring/prometheus.yaml
kubectl apply -f scripts/deploy/kubernetes/monitoring/grafana.yaml
```

### 11.2 负载均衡优化

微调Nginx配置以实现更好的负载均衡：

```bash
# 编辑Nginx配置
vi /etc/nginx/conf.d/suoke.conf

# 添加负载均衡配置
upstream api_servers {
    server 172.16.199.86:80 weight=5;
    server 172.16.199.86:80 backup;
}
```

### 11.3 安全隔离

加固节点间通信安全：

```bash
# 配置内部防火墙规则
sudo firewall-cmd --permanent --zone=internal --add-source=172.16.199.0/24
sudo firewall-cmd --permanent --zone=internal --add-service=http
sudo firewall-cmd --permanent --zone=internal --add-service=https
sudo firewall-cmd --permanent --zone=internal --add-port=27017/tcp
sudo firewall-cmd --reload
```

如需更多帮助，请参阅项目文档或联系开发团队。 