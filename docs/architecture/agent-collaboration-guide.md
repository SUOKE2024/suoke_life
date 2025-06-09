# 索克生活智能体协同使用指南

## 📋 概述

索克生活平台采用事件驱动的智能体协同架构，四个智能体通过事件总线进行协同工作，为用户提供全方位的健康管理服务。

## 🤖 智能体角色分工

### 小艾（xiaoai）- 首页聊天频道版主
- **主要职责**：语音交互、中医望诊、智能问诊、无障碍服务、四诊合参统筹
- **核心能力**：
  - 多语种语音交互（含方言识别）
  - 中医面色分析与舌诊图像处理
  - 智能问诊系统（体质筛查、症状评估）
  - 医疗记录自动整理与健康档案管理
  - 无障碍服务（导盲、手语识别、老年友好界面）

### 小克（xiaoke）- SUOKE频道版主
- **主要职责**：服务订阅、农产品预定、名医资源匹配、第三方API集成
- **核心能力**：
  - 名医资源智能匹配与预约管理
  - 医疗服务订阅与个性化推荐
  - 农产品溯源与定制配送管理
  - 第三方医疗服务API集成
  - 在线店铺管理与健康商品推荐

### 老克（laoke）- 探索频道版主
- **主要职责**：知识传播、培训管理、社区内容管理、游戏NPC
- **核心能力**：
  - 中医知识库RAG检索与个性化学习路径
  - 社区内容管理与知识贡献奖励
  - 健康教育课程与认证系统
  - 玉米迷宫NPC角色扮演与游戏引导
  - 用户博客管理与内容质量保障

### 索儿（soer）- LIFE频道版主
- **主要职责**：生活健康管理、多设备数据整合、情感陪伴
- **核心能力**：
  - 健康生活习惯培养与行为干预
  - 多设备传感器数据整合与健康趋势分析
  - 环境与情绪智能感知与动态健康建议
  - 个性化养生计划生成与执行跟踪
  - 身心健康陪伴与情感支持

## 🔄 协同场景

### 1. 综合健康诊断（comprehensive_health_diagnosis）
**参与智能体**：小艾、小克、老克、索儿

**工作流程**：
1. **小艾**：启动四诊合参统筹，进行体质筛查、面色分析、舌诊
2. **索儿**：收集生活数据，分析健康趋势和生活习惯
3. **小克**：基于诊断结果匹配合适的医生资源
4. **老克**：提供相关的中医知识支持和学习资源

**使用示例**：
```python
# 启动综合健康诊断
session_id = await collaboration_manager.start_collaboration(
    scenario="comprehensive_health_diagnosis",
    user_id="user_123",
    context={
        "symptoms": ["疲劳", "食欲不振", "睡眠质量差"],
        "user_info": {
            "age": 30,
            "gender": "female",
            "occupation": "office_worker"
        }
    }
)
```

### 2. 个性化养生计划（personalized_wellness_plan）
**参与智能体**：索儿、小艾、小克

**工作流程**：
1. **索儿**：基于用户数据生成个性化养生方案
2. **小艾**：进行中医体质分析，提供体质调理建议
3. **小克**：推荐相关的健康产品和农产品

**使用示例**：
```python
# 启动个性化养生计划
session_id = await collaboration_manager.start_collaboration(
    scenario="personalized_wellness_plan",
    user_id="user_123",
    context={
        "health_goals": ["改善睡眠", "增强体质", "减轻压力"],
        "lifestyle_data": {
            "sleep_hours": 6,
            "exercise_frequency": 2,
            "stress_level": "high"
        }
    }
)
```

### 3. 健康教育学习（health_education_journey）
**参与智能体**：老克、小艾、索儿

**工作流程**：
1. **老克**：推荐个性化的知识内容和学习路径
2. **小艾**：提供互动式学习体验
3. **索儿**：跟踪实践指导和学习效果

### 4. 紧急健康支持（emergency_health_support）
**参与智能体**：索儿、小艾、小克

**工作流程**：
1. **索儿**：检测异常健康状态
2. **小艾**：进行紧急健康评估
3. **小克**：快速调度医疗资源

## 🛠 API使用指南

### 启动协同
```http
POST /api/v1/collaboration/start
Content-Type: application/json

{
    "scenario": "comprehensive_health_diagnosis",
    "user_id": "user_123",
    "context": {
        "symptoms": ["疲劳", "头痛"],
        "urgency": "normal"
    }
}
```

### 查询协同状态
```http
GET /api/v1/collaboration/sessions/{session_id}
```

### 取消协同
```http
DELETE /api/v1/collaboration/sessions/{session_id}
```

### 获取活跃会话
```http
GET /api/v1/collaboration/sessions
```

## 📊 事件类型

### 小艾事件
- `xiaoai.voice.interaction_started` - 语音交互开始
- `xiaoai.look.face_color_completed` - 面色分析完成
- `xiaoai.look.tongue_diagnosis_completed` - 舌诊完成
- `xiaoai.inquiry.constitution_screening_completed` - 体质筛查完成
- `xiaoai.coordination.four_diagnosis_completed` - 四诊合参完成

### 小克事件
- `xiaoke.doctor.matching_completed` - 医生匹配完成
- `xiaoke.subscription.service_completed` - 服务订阅完成
- `xiaoke.agriculture.product_customized` - 农产品定制完成

### 老克事件
- `laoke.knowledge.search_completed` - 知识搜索完成
- `laoke.training.course_started` - 培训课程开始
- `laoke.game.maze_started` - 迷宫游戏开始

### 索儿事件
- `soer.sensor.data_collected` - 传感器数据收集
- `soer.wellness.plan_created` - 养生计划创建
- `soer.emotion.support_provided` - 情感支持提供

### 协同事件
- `collaboration.multi_agent_consultation_started` - 多智能体协同开始
- `collaboration.agent_handoff_initiated` - 智能体交接发起
- `collaboration.seamless_experience_orchestrated` - 无缝体验编排

## 🔧 开发指南

### 创建新的智能体
```python
from communication_service.event_bus.core.event_bus import SuokeEventBus
from communication_service.event_bus.orchestration import AgentCollaborationManager

class CustomAgent:
    def __init__(self, event_bus: SuokeEventBus):
        self.event_bus = event_bus
        
    async def initialize(self):
        # 订阅相关事件
        await self.event_bus.subscribe(
            "custom.event.type",
            self._handle_custom_event
        )
    
    async def _handle_custom_event(self, event_data):
        # 处理事件逻辑
        pass
```

### 添加新的协同场景
```python
# 在 agent_event_types.py 中添加新场景
COLLABORATION_SCENARIOS["new_scenario"] = {
    "description": "新协同场景",
    "participating_agents": ["xiaoai", "xiaoke"],
    "workflow": [
        "xiaoai.某项任务",
        "xiaoke.某项任务"
    ]
}
```

### 自定义事件处理器
```python
class CustomEventHandler:
    async def handle_event(self, event_type: str, event_data: Dict[str, Any]):
        if event_type == "custom.event":
            # 自定义处理逻辑
            await self._process_custom_logic(event_data)
    
    async def _process_custom_logic(self, data):
        # 实现具体的业务逻辑
        pass
```

## 📈 监控与运维

### 协同指标监控
```http
GET /api/v1/collaboration/metrics
```

返回示例：
```json
{
    "total_active_sessions": 5,
    "state_distribution": {
        "executing": 3,
        "completed": 2
    },
    "scenario_distribution": {
        "comprehensive_health_diagnosis": 3,
        "personalized_wellness_plan": 2
    }
}
```

### 智能体状态监控
```http
GET /api/v1/collaboration/agents/status
```

### 日志监控
- 协同会话日志：`/logs/collaboration/`
- 智能体日志：`/logs/agents/`
- 事件总线日志：`/logs/event_bus/`

## 🚨 故障排除

### 常见问题

1. **协同会话超时**
   - 检查智能体服务状态
   - 查看事件总线连接
   - 调整超时配置

2. **智能体无响应**
   - 检查智能体服务健康状态
   - 验证事件订阅配置
   - 查看错误日志

3. **事件丢失**
   - 检查Redis连接状态
   - 验证事件发布配置
   - 查看事件存储日志

### 调试工具

```python
# 启用调试模式
import logging
logging.getLogger("collaboration").setLevel(logging.DEBUG)

# 测试协同
await collaboration_manager.start_collaboration(
    scenario="comprehensive_health_diagnosis",
    user_id="debug_user",
    context={"debug_mode": True}
)
```

## 🔒 安全考虑

### 数据隐私
- 健康数据加密传输
- 事件数据脱敏处理
- 用户授权验证

### 访问控制
- API接口鉴权
- 智能体权限管理
- 协同会话隔离

### 审计日志
- 协同操作记录
- 数据访问日志
- 异常事件追踪

## 📚 最佳实践

### 协同设计原则
1. **松耦合**：智能体间通过事件通信，避免直接依赖
2. **异步处理**：使用异步事件处理，提高系统响应性
3. **容错机制**：实现重试、降级和故障恢复
4. **可观测性**：完善的日志、监控和追踪

### 性能优化
1. **事件批处理**：合并相关事件减少网络开销
2. **缓存策略**：缓存频繁访问的数据
3. **负载均衡**：分布式部署智能体服务
4. **资源管理**：合理配置超时和重试参数

### 扩展性设计
1. **插件化架构**：支持动态加载新的智能体
2. **配置驱动**：通过配置文件管理协同流程
3. **版本兼容**：保持事件格式的向后兼容性
4. **水平扩展**：支持智能体服务的水平扩展

## 🎯 未来规划

### 短期目标
- [ ] 完善智能体协同测试用例
- [ ] 优化事件处理性能
- [ ] 增加更多协同场景

### 中期目标
- [ ] 实现智能体学习能力
- [ ] 支持动态协同流程配置
- [ ] 集成更多第三方服务

### 长期目标
- [ ] 构建智能体生态系统
- [ ] 实现自适应协同优化
- [ ] 支持跨平台智能体协同 