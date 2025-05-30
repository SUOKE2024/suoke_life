# -*- coding: utf-8 -*-
"""
诊断服务事件发布器示例
诊断完成后发布诊断结果事件到消息队列（Kafka/RabbitMQ）
"""
from services.common.messaging.event_bus import EventBus

event_bus = EventBus(backend='kafka', config={})

def publish_diagnosis_result(result: dict):
    event = {
        'type': 'diagnosis.result',
        'payload': result
    }
    event_bus.publish('diagnosis.result', event)
    print(f"[LookService] 已发布诊断结果事件: {event}") 