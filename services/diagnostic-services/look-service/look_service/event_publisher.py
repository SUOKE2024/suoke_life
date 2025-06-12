from typing import Any, Dict, List, Optional, Union

"""
event_publisher - 索克生活项目模块
"""

from services.common.messaging.event_bus import EventBus

# - * - coding: utf - 8 - * -
"""
诊断服务事件发布器示例
诊断完成后发布诊断结果事件到消息队列（Kafka / RabbitMQ）
"""

event_bus = EventBus(backend="kafka", config={})


def publish_diagnosis_result(result: dict):
    """TODO: 添加文档字符串"""
    event = {"type": "diagnosis.result", "payload": result}
    event_bus.publish("diagnosis.result", event)
    print(f"[LookService] 已发布诊断结果事件: {event}")
