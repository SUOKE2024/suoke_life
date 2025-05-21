# 小克服务 (xiaoke-service)

小克服务是索克生活平台的核心智能体服务之一，主要负责医疗资源平台服务，包括索克生活服务订阅、优质农产品定制、供应链管理、农事活动体验和索克店铺管理等。

## 功能特性

小克服务具有以下核心功能：

1. **医疗资源调度**
   - 根据用户体质和需求匹配医疗资源
   - 智能预约管理
   - 资源可用性实时监控

2. **农产品定制与管理**
   - 基于体质的个性化产品推荐
   - 产品溯源与区块链验证
   - 订单和支付处理
   - 产品生命周期管理

3. **食疗建议**
   - 根据用户体质生成食疗方案
   - 食物与药物相互作用检查
   - 个性化食谱推荐

4. **区块链溯源**
   - 农产品从种植到销售全流程溯源
   - 区块链数据验证
   - 食品安全追踪

5. **服务订阅管理**
   - 不同级别会员服务订阅
   - 自动续费和账单管理
   - 服务定制与升级

6. **农事活动体验**
   - 农场体验活动组织与推荐
   - 活动预约与管理
   - 体验反馈收集

## 技术架构

### 架构概览

```
+-----------------------+        +--------------------+
|  索克生活APP前端        |  <---> |  API网关           |
+-----------------------+        +--------------------+
                                          |
                                          v
                          +--------------------------------+
                          |           小克服务              |
                          +--------------------------------+
                          |  - 资源管理器                   |
                          |  - 产品管理器                   |
                          |  - 食疗管理器                   |
                          |  - 订阅管理器                   |
                          +--------------------------------+
                              |           |           |
                              v           v           v
                +---------------+  +-------------+  +-----------------+
                | 数据库         |  | 消息队列     |  | 区块链服务       |
                +---------------+  +-------------+  +-----------------+
                      |                                    
                      v                                    
          +--------------------------+                     
          |        外部集成           |                     
          | - ERP系统                |                     
          | - 支付服务               |                     
          | - 第三方平台API          |                     
          +--------------------------+                     
```

### 核心组件

1. **Agent模块**
   - `agent_manager.py`: 智能体管理器，控制智能体行为和规划
   - `food_therapy_manager.py`: 食疗建议管理器，负责体质食物匹配和食疗方案

2. **Scheduler模块**
   - `resource_manager.py`: 医疗资源管理器，负责资源调度和预约

3. **Inventory模块**
   - `product_manager.py`: 产品管理器，负责产品定制、溯源和推荐

4. **Repository模块**
   - 数据访问层，连接各种存储服务
   - `resource_repository.py`: 资源数据访问
   - `product_repository.py`: 产品数据访问
   - `food_repository.py`: 食物数据访问
   - `blockchain_repository.py`: 区块链数据访问

5. **Domain模块**
   - `models.py`: 领域模型定义，包括体质类型、产品类型等枚举

6. **Delivery模块**
   - gRPC服务端实现
   - API处理和请求映射

## 部署指南

### 环境要求

- Python 3.9+
- MongoDB 4.4+
- PostgreSQL 13+
- Redis 6.0+
- Docker & Docker Compose (推荐)

### 配置项

关键配置项存储在 `config/config.yaml` 中，可通过环境变量覆盖：

```yaml
service:
  name: xiaoke-service
  version: 1.0.0

server:
  host: 0.0.0.0
  port: 9083

database:
  postgres:
    host: ${POSTGRES_HOST:-postgres}
    port: ${POSTGRES_PORT:-5432}
    # 其他配置...
```

### Docker部署

1. 构建镜像：

```bash
docker build -t xiaoke-service:latest .
```

2. 使用Docker Compose启动服务：

```bash
docker-compose up -d
```

### 直接运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 设置环境变量或更新配置文件

3. 启动服务：

```bash
python -m cmd.server
```

## API文档

服务提供gRPC接口，主要接口包括：

1. 资源调度相关
   - `ScheduleResources`: 调度医疗资源
   - `ManageAppointment`: 管理预约

2. 产品管理相关
   - `CustomizeProducts`: 定制农产品
   - `TraceProduct`: 产品溯源
   - `ProcessPayment`: 处理支付
   - `RecommendProducts`: 推荐产品

3. 食疗服务相关
   - `GenerateDietPlan`: 生成食疗方案
   - `CheckFoodMedicinePairing`: 检查食物药物配伍
   - `RecommendRecipes`: 推荐食谱

4. 服务订阅相关
   - `ManageSubscription`: 管理订阅
   - `ProcessSubscriptionPayment`: 处理订阅支付

完整接口定义请参考 `api/grpc/xiaoke_service.proto` 文件。

## 测试

运行单元测试：

```bash
pytest test/
```

运行集成测试：

```bash
pytest test/integration/
```

## 监控与运维

服务提供以下监控端点：

- 健康检查: `/health`
- 就绪检查: `/ready`
- 指标暴露: `/metrics`

支持与Prometheus和Grafana集成，预定义的仪表盘配置位于 `deploy/grafana/dashboards/` 目录。

## 贡献指南

1. Fork该仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

索克生活内部项目，保留所有权利。

## 联系方式

若有问题，请联系索克生活技术团队。