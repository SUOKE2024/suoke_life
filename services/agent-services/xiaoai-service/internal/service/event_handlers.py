# -*- coding: utf-8 -*-
"""
智能体服务事件处理器示例
演示如何订阅诊断结果事件并处理（如Kafka/RabbitMQ集成）
"""
from services.common.messaging.event_bus import EventBus

def handle_diagnosis_result(event: dict):
    print(f"[Xiaoai] 收到诊断结果事件: {event}")
    # TODO: 业务逻辑处理，如推送给前端、更新状态等

# 事件总线初始化（可配置为Kafka/RabbitMQ）
event_bus = EventBus(backend='kafka', config={})

def register_event_handlers():
    event_bus.subscribe('diagnosis.result', handle_diagnosis_result)
    print("[Xiaoai] 已注册诊断结果事件处理器")

# 启动时调用register_event_handlers() 