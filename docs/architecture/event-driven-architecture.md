# 索克生活事件驱动架构

## 概述

索克生活项目采用事件驱动架构（Event-Driven Architecture, EDA）来实现智能体协同、健康数据处理和系统间通信。该架构提供了高度解耦、可扩展和可靠的服务间通信机制。

## 架构特点

### 🎯 核心优势

1. **智能体协同** - 四个智能体（小艾、小克、老克、索儿）通过事件进行协同诊断
2. **数据一致性** - 事件溯源确保数据的一致性和可追溯性
3. **混合数据访问** - 事件驱动 + 缓存 + 数据库的智能路由策略
4. **高可用性** - 异步处理和故障恢复机制
5. **可扩展性** - 微服务架构支持水平扩展

### 🏗️ 架构组件

```
┌─────────────────────────────────────────────────────────────┐
│                    索克生活事件驱动架构                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   小艾      │  │   小克      │  │   老克      │          │
│  │  (望诊)     │  │  (闻诊)     │  │  (问诊)     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│  ┌─────────────┐         │         ┌─────────────┐          │
│  │   索儿      │         │         │ 事件总线    │          │
│  │  (切诊)     │◄────────┼────────►│ (Redis)     │          │
│  └─────────────┘         │         └─────────────┘          │
│                          │                │                 │
│  ┌─────────────┐         │         ┌─────────────┐          │
│  │ 智能数据    │◄────────┼────────►│ 事件存储    │          │
│  │ 访问路由    │         │         │(PostgreSQL) │          │
│  └─────────────┘         │         └─────────────┘          │
│         │                │                │                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   缓存      │  │   数据库    │  │   区块链    │          │
│  │  (Redis)    │  │(PostgreSQL) │  │   服务      │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 启动Redis
docker run -d --name suoke-redis -p 6379:6379 redis:7-alpine

# 启动PostgreSQL
docker run -d --name suoke-postgres \
  -e POSTGRES_DB=suoke_db \
  -e POSTGRES_USER=suoke \
  -e POSTGRES_PASSWORD=suoke123 \
  -p 5432:5432 postgres:15
```

### 2. 配置环境变量

```bash
# .env 文件
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://suoke:suoke123@localhost:5432/suoke_db
SERVICE_NAME=suoke-event-bus
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### 3. 启动事件总线服务

```bash
cd services/communication-service
python -m communication_service.message_bus.main
```

### 4. 启动智能体服务

```bash
# 启动小艾服务
cd services/agent-services/xiaoai-service
python -m xiaoai.agent.event_driven_agent

# 启动其他智能体服务...
```

## 事件类型定义

### 智能体协同事件

```python
# 诊断流程事件
DIAGNOSIS_STARTED = "diagnosis.started"
DIAGNOSIS_COMPLETED = "diagnosis.completed"

# 小艾（望诊）事件
XIAOAI_LOOK_STARTED = "xiaoai.look.started"
XIAOAI_LOOK_COMPLETED = "xiaoai.look.completed"

# 小克（闻诊）事件
XIAOKE_LISTEN_STARTED = "xiaoke.listen.started"
XIAOKE_LISTEN_COMPLETED = "xiaoke.listen.completed"

# 老克（问诊）事件
LAOKE_INQUIRY_STARTED = "laoke.inquiry.started"
LAOKE_INQUIRY_COMPLETED = "laoke.inquiry.completed"

# 索儿（切诊）事件
SOER_PALPATION_STARTED = "soer.palpation.started"
SOER_PALPATION_COMPLETED = "soer.palpation.completed"
```

### 健康数据事件

```python
# 数据收集事件
HEALTH_DATA_RECEIVED = "health.data.received"
HEALTH_DATA_VALIDATED = "health.data.validated"
HEALTH_DATA_STORED = "health.data.stored"

# 生命体征事件
VITAL_SIGNS_UPDATED = "health.vital_signs.updated"
VITAL_SIGNS_ABNORMAL = "health.vital_signs.abnormal"
VITAL_SIGNS_CRITICAL = "health.vital_signs.critical"
```

## API 使用示例

### 1. 启动诊断流程

```python
import requests

# 启动诊断
response = requests.post("http://localhost:8000/api/v1/events/diagnosis/start", json={
    "user_id": "user_123",
    "user_data": {
        "age": 35,
        "gender": "female",
        "symptoms": ["头痛", "失眠"]
    },
    "priority": "normal"
})

session_id = response.json()["session_id"]
print(f"诊断会话ID: {session_id}")
```

### 2. 更新健康数据

```python
# 更新生命体征
requests.post("http://localhost:8000/api/v1/events/health-data/update", json={
    "user_id": "user_123",
    "data_type": "heart_rate",
    "data_value": 75,
    "source": "wearable_device"
})

# 更新血压数据
requests.post("http://localhost:8000/api/v1/events/health-data/update", json={
    "user_id": "user_123",
    "data_type": "blood_pressure",
    "data_value": {"systolic": 120, "diastolic": 80},
    "source": "manual_input"
})
```

### 3. 查询诊断状态

```python
# 查询诊断进度
response = requests.get(f"http://localhost:8000/api/v1/events/diagnosis/{session_id}/status")
status = response.json()
print(f"当前步骤: {status['current_step']}")
print(f"进度: {status['progress']}")
```

### 4. 获取健康趋势

```python
# 获取心率趋势
response = requests.get(
    f"http://localhost:8000/api/v1/events/health/trends/user_123",
    params={"data_type": "heart_rate", "period": "week"}
)
trends = response.json()
print(f"趋势: {trends['trend']}")
print(f"变化率: {trends['change_rate']}%")
```

## 智能体开发指南

### 1. 创建事件驱动智能体

```python
from communication_service.event_bus.core.event_bus import SuokeEventBus

class MyAgent:
    def __init__(self):
        self.event_bus = SuokeEventBus()
    
    async def start(self):
        await self.event_bus.initialize()
        await self.event_bus.start()
        
        # 订阅事件
        await self.event_bus.subscribe("my.event.type", self.handle_event)
    
    async def handle_event(self, event):
        # 处理事件逻辑
        print(f"收到事件: {event.type}")
        
        # 发布响应事件
        await self.event_bus.publish("my.response.event", {
            "result": "处理完成",
            "original_event_id": event.id
        })
```

### 2. 智能体协同模式

```python
# 顺序协同（四诊合参）
async def sequential_diagnosis(self, user_data):
    # 1. 小艾望诊
    await self.event_bus.publish("xiaoai.look.started", user_data)
    
    # 等待望诊完成，自动触发下一步
    # 2. 小克闻诊 -> 3. 老克问诊 -> 4. 索儿切诊

# 并行协同（特定场景）
async def parallel_analysis(self, user_data):
    # 同时进行多项分析
    await asyncio.gather(
        self.event_bus.publish("xiaoai.tongue_analysis.requested", user_data),
        self.event_bus.publish("xiaoai.face_analysis.requested", user_data),
        self.event_bus.publish("xiaoke.voice_analysis.requested", user_data)
    )
```

## 数据访问策略

### 1. 智能数据路由

```python
from communication_service.event_bus.utils.event_router import SmartDataAccessRouter

router = SmartDataAccessRouter(event_bus, cache_service, database_service)

# 实时数据访问（优先缓存）
data = await router.get_user_health_data(
    user_id="user_123",
    data_type="heart_rate",
    access_mode="real_time"
)

# 历史数据访问（直接数据库）
data = await router.get_user_health_data(
    user_id="user_123",
    data_type="heart_rate",
    access_mode="historical",
    start_date=datetime.now() - timedelta(days=7)
)

# 聚合数据访问（缓存+计算）
data = await router.get_user_health_data(
    user_id="user_123",
    data_type="heart_rate",
    access_mode="aggregated",
    aggregation="avg",
    period="day"
)
```

### 2. 缓存策略配置

```python
# 不同数据类型的缓存策略
cache_strategies = {
    'vital_signs': {'ttl': 300, 'strategy': 'latest'},      # 5分钟
    'diagnostic_results': {'ttl': 3600, 'strategy': 'versioned'},  # 1小时
    'tcm_data': {'ttl': 1800, 'strategy': 'latest'},       # 30分钟
    'user_profile': {'ttl': 7200, 'strategy': 'versioned'}, # 2小时
    'aggregated_stats': {'ttl': 1800, 'strategy': 'computed'} # 30分钟
}
```

## 监控和运维

### 1. 健康检查

```bash
# 检查事件总线状态
curl http://localhost:8000/api/v1/events/statistics

# 检查智能体状态
curl http://localhost:8000/api/v1/events/agents/status
```

### 2. 性能监控

```bash
# Prometheus指标
curl http://localhost:8000/metrics
```

### 3. 事件查询

```python
# 查询特定类型的事件
response = requests.post("http://localhost:8000/api/v1/events/events/query", json={
    "event_type": "diagnosis.completed",
    "start_time": "2024-01-01T00:00:00Z",
    "end_time": "2024-01-31T23:59:59Z",
    "limit": 100
})
```

## 故障排除

### 常见问题

1. **Redis连接失败**
   ```bash
   # 检查Redis状态
   docker ps | grep redis
   redis-cli ping
   ```

2. **事件处理延迟**
   ```bash
   # 检查事件队列长度
   redis-cli llen suoke:events:queue
   ```

3. **数据库连接问题**
   ```bash
   # 检查数据库连接
   psql -h localhost -U suoke -d suoke_db -c "SELECT 1;"
   ```

### 日志分析

```bash
# 查看事件总线日志
tail -f logs/event-bus.log | jq '.'

# 过滤特定事件类型
tail -f logs/event-bus.log | jq 'select(.event_type == "diagnosis.started")'
```

## 最佳实践

### 1. 事件设计原则

- **事件命名**: 使用动词过去式，如 `user.registered`, `diagnosis.completed`
- **事件大小**: 保持事件负载小于1MB
- **幂等性**: 确保事件处理的幂等性
- **版本控制**: 为事件添加版本字段

### 2. 错误处理

```python
async def handle_event_with_retry(self, event):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await self.process_event(event)
            break
        except Exception as e:
            if attempt == max_retries - 1:
                # 发布失败事件
                await self.event_bus.publish("event.processing.failed", {
                    "original_event": event.to_dict(),
                    "error": str(e),
                    "attempts": max_retries
                })
            else:
                await asyncio.sleep(2 ** attempt)  # 指数退避
```

### 3. 性能优化

- **批量处理**: 对于高频事件，使用批量处理
- **异步处理**: 所有事件处理都应该是异步的
- **连接池**: 使用连接池管理数据库和Redis连接
- **监控指标**: 监控事件处理延迟和错误率

## 扩展指南

### 1. 添加新的事件类型

```python
# 1. 在 event_types.py 中定义新事件
class NewFeatureEvents:
    FEATURE_STARTED = "new_feature.started"
    FEATURE_COMPLETED = "new_feature.completed"

# 2. 创建事件处理器
class NewFeatureHandler:
    async def handle_feature_started(self, event):
        # 处理逻辑
        pass

# 3. 注册处理器
await event_bus.subscribe("new_feature.started", handler.handle_feature_started)
```

### 2. 集成新的智能体

```python
# 继承基础智能体类
class NewAgent(EventDrivenXiaoaiAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = 'new_agent'
    
    async def _subscribe_to_events(self):
        await super()._subscribe_to_events()
        # 订阅新的事件类型
        await self._listen_to_event("new_agent.task.started")
```

## 总结

索克生活的事件驱动架构提供了：

1. **智能体协同**: 通过事件实现四诊合参的协同诊断
2. **数据一致性**: 事件溯源确保数据的可追溯性
3. **混合访问**: 智能的缓存+数据库访问策略
4. **高可用性**: 异步处理和故障恢复机制
5. **可扩展性**: 微服务架构支持水平扩展

这种架构设计既满足了中医诊断的复杂协同需求，又保证了现代化系统的性能和可靠性要求。 