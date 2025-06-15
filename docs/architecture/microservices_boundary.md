# 索克生活微服务边界与接口职责梳理

## 1. 总体原则
- 每个微服务聚焦单一领域/能力，接口清晰、职责单一。
- 服务间通过标准API（REST/gRPC）或消息总线解耦通信。
- 共享数据通过API/事件流交互，避免直接数据库耦合。
- 复用通用能力（如用户、权限、健康数据标准化）通过独立服务或共享库实现。

---

## 2. 核心服务边界与接口

### 2.1 agent-services（智能体服务）
- **职责**：封装四大智能体（小艾、小克、老克、索儿）的业务逻辑、决策与个性化服务。
- **接口**：
  - 提供面向前端/用户的智能体API（如健康建议、个性化推送、服务编排）。
  - 通过gRPC/REST调用diagnostic-services获取诊断结果。
  - 通过消息总线/事件流与integration-service协作，实现跨服务编排。
- **边界**：
  - 只负责智能体业务逻辑与服务编排，不直接处理底层诊断算法和原始数据采集。
  - 所有诊断请求均通过gRPC/REST调用diagnostic-services，不做算法处理。
  - 聚合和编排诊断结果，面向前端/用户提供智能体API。

### 2.2 diagnostic-services（诊断服务）
- **职责**：实现望、闻、问、切等中医五诊、AI算法、健康指标分析等底层诊断能力。
- **接口**：
  - 提供标准化诊断API（REST/gRPC），如/diagnose/look、/diagnose/listen等。
  - 仅对agent-services、integration-service等授权服务开放。
  - 支持批量/异步诊断任务，结果通过事件流/回调返回。
- **边界**：
  - 专注于诊断算法和健康指标分析，不与前端直接通信。
  - 仅暴露标准化API（如REST/gRPC），推荐返回FHIR等国际标准格式。
  - 不负责用户交互、个性化推荐、服务编排。

### 2.3 integration-service（集成服务）
- **职责**：对接第三方系统（如医院HIS、健康云、IoT设备）、统一外部API、数据同步与转换。
- **接口**：
  - 提供标准化对外API（如FHIR、HL7），供外部系统调用。
  - 负责数据格式转换、同步、合规校验。
  - 通过事件流/消息队列与agent-services、diagnostic-services解耦集成。
- **边界**：
  - 只负责第三方系统对接、数据格式转换与合规校验，不实现业务决策逻辑。
  - 所有健康数据、诊断结果等接口均推荐采用FHIR、OpenAPI Schema等标准格式。
  - 不直接与前端或智能体服务交互，只做数据桥接和合规校验。

---

## 3. 去耦与优化建议
- **接口标准化**：所有健康数据、诊断结果、用户信息等均采用标准数据结构（如FHIR、OpenAPI Schema）。
- **事件驱动解耦**：跨服务编排、异步任务、通知等通过内存事件总线实现，避免同步耦合。
- **通用能力下沉**：用户、权限、日志、健康数据标准化等通用能力下沉为独立服务或共享库，避免重复实现。
- **API网关统一入口**：所有外部流量通过API Gateway路由，内部服务仅暴露必要接口。
- **文档与契约驱动开发**：所有服务接口均有OpenAPI/Proto文档，前后端/服务间协作基于契约开发。

---

## 4. 典型调用链与数据流

1. **用户健康咨询流程**：
   - 前端 → agent-services（小艾）→ diagnostic-services（五诊）→ agent-services聚合建议 → 前端
2. **健康数据同步到第三方**：
   - agent-services → integration-service（FHIR格式转换）→ 第三方健康云/医院HIS
3. **外部诊断结果回流**：
   - integration-service（监听外部事件）→ diagnostic-services（标准化分析）→ agent-services

---

## 5. 未来扩展建议
- 持续梳理服务边界，定期架构评审，防止"胖服务"与重复实现。
- 推动领域驱动设计（DDD），以业务能力为核心划分服务。
- 引入服务目录与依赖图，提升可观测性与维护效率。

---

如需详细接口定义、服务契约示例或具体优化方案，请查阅各服务API文档或联系架构团队。

### 跨服务通信
- 推荐采用内存事件总线进行解耦，提升可维护性和可扩展性。
- 服务间不直接共享数据库，所有数据交互通过API或事件流完成。

---

## 6. 事件流/消息队列落地实现示例

- 所有核心服务均通过事件总线（EventBus）模块实现事件发布与订阅。
- 事件流转示例：
  1. diagnostic-services 诊断完成后，调用 `event_bus.publish('diagnosis.result', event)` 发布诊断结果事件。
  2. agent-services 通过 `event_bus.subscribe('diagnosis.result', handler)` 订阅诊断结果事件，收到后聚合并推送给前端。
  3. integration-service 通过 `event_bus.subscribe('external.healthdata.sync', handler)` 订阅外部健康数据同步事件，收到后进行格式转换与合规校验。
- 事件总线模块基于内存实现，支持高性能的事件处理。
- 推荐所有跨服务异步通信、批量任务、通知等均通过事件流实现，提升解耦性和可观测性。

### 代码示例

```python
# 发布事件（诊断服务）
from services.common.messaging.event_bus import EventBus

event_bus = EventBus()
event_bus.publish('diagnosis.result', {'type': 'diagnosis.result', 'payload': result})

# 订阅事件（智能体服务）
def handle_diagnosis_result(event):
    print(f"收到诊断结果: {event}")
event_bus.subscribe('diagnosis.result', handle_diagnosis_result) 