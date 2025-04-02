# 索克生活服务平台 - 供应链溯源系统

本项目实现索克生活平台的食品供应链追溯系统，提供全链路的食品产品追踪、区块链验证、物联网监控和智能风险预测功能。

## 核心功能

### 1. 区块链集成
- 数据不可篡改保证
- 区块链验证API
- 链上追溯证明

### 2. 消费者端APP查询功能
- 产品QR码生成和查询
- 用户友好的产品旅程展示
- 支持分享和验证

### 3. 物联网设备集成
- 多类型传感器数据接入
- 环境条件异常监控和预警
- 实时数据监测和历史记录

### 4. AI预测分析
- 供应链风险智能预测
- 多维度风险评估和建议
- 风险可视化和预警

## 技术架构

### 后端服务
- Node.js + Express
- TypeScript
- RESTful API
- 多服务模块化架构

### 移动端
- Flutter跨平台开发
- Riverpod状态管理
- Clean Architecture架构

## API文档

### 区块链API
- `GET /api/blockchain/verify/:eventId` - 验证事件真实性
- `GET /api/blockchain/proof/:productId` - 获取产品区块链证明
- `POST /api/blockchain/save` - 保存事件到区块链

### 消费者API
- `POST /api/consumer/qrcode` - 生成产品QR码
- `GET /api/consumer/trace/:qrId` - 获取产品追溯信息

### 物联网API
- `POST /api/iot/sensor-data` - 接收传感器数据
- `GET /api/iot/environment/:productId` - 获取产品环境数据

### 预测API
- `GET /api/prediction/risks/:productId` - 获取产品风险预测

## 未来计划

1. 进一步完善农产品区块链追溯系统
2. 整合卫星遥感数据监控种植环境
3. 开发AR溯源体验功能
4. 实现虚拟农场数字孪生
5. 建立产品碳足迹计算系统

## 部署指南

### 本地开发环境

可以使用Docker Compose快速搭建本地开发环境：

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f xiaoke-service

# 停止所有服务
docker-compose down
```

本地开发环境包括：
- 小克服务 (xiaoke-service)
- MongoDB 数据库
- Redis 缓存服务器
- OpenTelemetry 收集器

### 生产环境部署

小克服务使用Kubernetes进行生产环境部署，配置文件位于`k8s/`目录下：

```bash
# 使用kustomize部署
kubectl apply -k k8s/

# 或单独应用各个资源
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
# ... 其他资源
```

生产环境配置包括：
- 部署配置 (deployment.yaml)
- 服务配置 (service.yaml)
- 水平自动缩放 (hpa.yaml)
- 网络策略 (network-policy.yaml)
- Istio配置 (istio-config.yaml)
- 持久卷声明 (pvc.yaml)
- 服务账户和RBAC (serviceaccount.yaml)
- 备份作业 (backup-job.yaml)
- 中断预算 (pdb.yaml)

### 环境变量

小克服务需要以下环境变量才能正常工作，可以参考`.env.example`文件：

```
# 服务配置
NODE_ENV=production
PORT=3011
METRICS_PORT=9464
WEBSOCKET_PORT=3012

# 数据库连接
MONGODB_URI=mongodb://username:password@hostname:27017/xiaoke
REDIS_HOST=redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# 日志和数据路径
LOG_DIR=/app/logs
DATA_DIR=/app/data
CACHE_DIR=/app/cache
```

### 健康检查

服务提供以下健康检查端点：
- `/health` - 服务整体健康状态
- `/health/live` - 存活探针
- `/health/ready` - 就绪探针

### 监控指标

服务在`/metrics`端点暴露Prometheus格式的指标，包括：
- HTTP请求计数和耗时
- 农产品订单处理统计
- 农事活动参与指标
- 系统资源使用情况

### CI/CD集成

小克服务已与GitOps工作流集成，每次代码合并到main分支时会自动构建和部署。具体流程参见部署文档