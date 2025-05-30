# -*- coding: utf-8 -*-
"""
集成服务事件处理器示例
订阅外部健康数据同步事件并进行格式转换与合规校验
"""
from services.common.messaging.event_bus import EventBus
from .health_data_service import HealthDataIntegrationService

def handle_external_health_data(event: dict):
    print(f"[IntegrationService] 收到外部健康数据事件: {event}")
    data = event.get('payload', {})
    service = HealthDataIntegrationService()
    try:
        fhir_data = service.receive_external_data(data)
        print(f"[IntegrationService] FHIR格式数据: {fhir_data}")
    except Exception as e:
        print(f"[IntegrationService] 数据合规校验失败: {e}")

# 事件总线初始化
event_bus = EventBus(backend='kafka', config={})

def register_event_handlers():
    event_bus.subscribe('external.healthdata.sync', handle_external_health_data)
    print("[IntegrationService] 已注册外部健康数据事件处理器") 