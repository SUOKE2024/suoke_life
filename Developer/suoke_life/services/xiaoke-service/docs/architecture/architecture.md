# 小克服务架构文档

## 1. 系统概述

小克服务是索克生活APP的核心微服务之一，主要负责供应链与农产品服务智能体的功能实现。本服务集成了区块链、物联网(IoT)和人工智能技术，为用户提供全方位的农产品溯源、订购和农事活动体验等服务。

## 2. 技术栈

- **后端框架**: Node.js + Express
- **开发语言**: TypeScript
- **数据库**: MongoDB (主数据库), Redis (缓存)
- **消息队列**: RocketMQ
- **容器化**: Docker + Kubernetes
- **区块链**: 自定义供应链区块链网络
- **AI模型**: 专用供应链和农产品领域模型
- **监控**: Prometheus + Grafana
- **分布式追踪**: OpenTelemetry

## 3. 系统架构图

```
+-------------------+    +-------------------+    +-------------------+
|                   |    |                   |    |                   |
|   移动客户端       |    |   Web客户端       |    |   第三方应用       |
|                   |    |                   |    |                   |
+--------+----------+    +--------+----------+    +--------+----------+
         |                       |                        |
         |                       |                        |
+--------v-----------------------v------------------------v----------+
|                                                                   |
|                           API网关                                 |
|                                                                   |
+----+-------------------------------+-----------------------------+
     |                               |                             |
+----v----+                     +----v----+                   +----v----+
|         |                     |         |                   |         |
| 认证服务 |                     | 用户服务 |                   | 小克服务 |
|         |                     |         |                   |         |
+----+----+                     +----+----+                   +----+----+
     |                               |                             |
     |                               |                             |
+----v-------------------------------v-----------------------------v---+
|                                                                     |
|                           服务网格(Istio)                           |
|                                                                     |
+---------------------------------------------------------------------+
     |                   |                |                  |
+----v----+         +----v----+      +----v----+        +----v----+
|         |         |         |      |         |        |         |
| 数据库集群 |         | 缓存集群  |      | 消息队列  |        | 区块链网络 |
|         |         |         |      |         |        |         |
+---------+         +---------+      +---------+        +---------+
```

## 4. 核心组件

### 4.1 供应链模块

负责农产品从生产到销售的全流程管理，包括：

- 产品生命周期管理
- 供应商管理
- 库存管理
- 物流跟踪

### 4.2 区块链溯源模块

使用区块链技术确保农产品数据的不可篡改性和可追溯性：

- 农产品数字身份生成
- 生产过程记录
- 交易信息验证
- 溯源证书生成

### 4.3 物联网(IoT)模块

集成各类传感器数据，监控农产品生产和物流环境：

- 环境数据采集
- 实时状态监控
- 异常情况报警
- 数据可视化分析

### 4.4 智能预测模块

基于AI模型进行供应链风险预测和优化：

- 需求预测
- 库存优化
- 风险评估
- 质量预测

### 4.5 农事活动模块

提供农事体验活动的管理和参与功能：

- 活动发布管理
- 预约报名系统
- 参与者互动
- 活动反馈与评价

## 5. 数据流

### 5.1 产品溯源流程

1. 农产品生产者录入产品信息
2. 系统生成唯一溯源码并记录到区块链
3. 物联网设备实时监控生产环境并上传数据
4. 运输过程中的转运信息记录到区块链
5. 消费者扫码查询完整溯源信息

### 5.2 订单处理流程

1. 用户提交订单
2. 系统验证库存并锁定商品
3. 支付确认后更新订单状态
4. 触发物流处理流程
5. 订单状态变更发送通知

## 6. API设计

采用RESTful API设计原则，主要接口分组：

- `/api/supply-chain/*` - 供应链相关接口
- `/api/blockchain/*` - 区块链验证接口
- `/api/iot/*` - 物联网数据接口
- `/api/consumer/*` - 消费者查询接口
- `/api/prediction/*` - 预测分析接口

详细API文档见 Swagger 文档 (`/api-docs`)

## 7. 安全架构

- JWT身份验证
- 基于角色的访问控制(RBAC)
- API请求速率限制
- 敏感数据加密存储
- 区块链数据不可篡改保证

## 8. 服务间通信

小克服务与以下服务直接交互：

- **用户服务**: 获取用户信息和权限
- **RAG服务**: 知识查询增强
- **小艾服务**: 智能体协作
- **索儿服务**: 健康生活推荐

## 9. 部署架构

服务部署在Kubernetes集群上，具体配置参见部署文档。主要特点：

- 多副本高可用
- 自动扩缩容
- 蓝绿部署
- 容器健康检查
- 分布式追踪

## 10. 监控与可观测性

- Prometheus指标监控
- OpenTelemetry分布式追踪
- 集中式日志管理
- 自定义业务指标
- 告警与通知机制
