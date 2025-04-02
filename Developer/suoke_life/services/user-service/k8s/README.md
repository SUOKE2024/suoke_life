# 用户服务 Kubernetes 部署配置

本目录包含用户服务的 Kubernetes 部署配置文件，遵循 MICROSERVICES_DEPLOYMENT.md 中的标准和规范。

## 配置文件说明

### deployment.yaml
- **功能**：定义用户服务的部署配置、服务和持久卷声明
- **特点**：
  - 设置资源请求和限制（CPU: 200m/500m, 内存: 256Mi/512Mi）
  - 配置健康检查（存活、就绪、启动探针）
  - 设置节点亲和性，部署在核心服务节点池(suoke-core-np)
  - 配置安全上下文，以非root用户运行
  - 使用持久卷存储上传文件

### hpa.yaml
- **功能**：配置水平自动扩缩容
- **特点**：
  - 基于CPU和内存使用率自动扩缩容
  - 设置最小2个副本，最大5个副本
  - 配置扩缩容行为，避免频繁扩缩容

### network-policy.yaml
- **功能**：定义网络策略，实现零信任网络架构
- **特点**：
  - 限制入站流量来源（只允许API网关和认证服务访问）
  - 限制出站流量目标（只允许访问知识库、知识图谱服务和Redis）
  - 允许访问DNS和监控服务

### istio-config.yaml
- **功能**：配置Istio服务网格
- **特点**：
  - 启用严格的mTLS加密通信
  - 配置流量管理和负载均衡策略
  - 设置重试和超时策略
  - 配置熔断机制

### opentelemetry-config.yaml
- **功能**：配置OpenTelemetry观测性框架
- **特点**：
  - 定义采样策略
  - 配置导出端点
  - 设置服务标识和属性

## 使用说明

1. 确保集群中已部署Istio和OpenTelemetry
2. 创建所需的ConfigMap和Secret：
   ```bash
   kubectl create secret generic user-service-env \
     --from-literal=DB_HOST=mysql.suoke \
     --from-literal=DB_USER=user_service \
     --from-literal=DB_PASSWORD=<密码> \
     --from-literal=DB_NAME=user_service_db \
     --from-literal=REDIS_PASSWORD=<密码> \
     --from-literal=JWT_SECRET=<密钥> \
     -n suoke
   ```
3. 应用配置文件：
   ```bash
   kubectl apply -f k8s/ -n suoke
   ```

## 监控和日志

- 监控指标通过`/metrics`端点暴露，被Prometheus自动抓取
- 分布式追踪数据通过OpenTelemetry导出到监控服务
- 日志通过OpenTelemetry收集器发送到集中日志系统

## 注意事项

- 所有配置已根据MICROSERVICES_DEPLOYMENT.md中的标准进行设计
- 用户服务作为核心服务，部署在`suoke-core-np`节点池上
- 已实现严格的安全配置和访问控制