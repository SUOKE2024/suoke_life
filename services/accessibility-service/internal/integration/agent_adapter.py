#!/usr/bin/env python

"""
无障碍服务与智能体集成适配器
"""

import json
import logging
import time
from typing import Any

import grpc

from config.config import config

logger = logging.getLogger(__name__)


class AgentAdapter:
    """智能体集成适配器，处理与四大智能体的通信"""

    def __init__(self):
        """初始化适配器，连接到各个智能体服务"""
        self.channels = {}
        self.stubs = {}
        self._init_connections()
        logger.info("智能体适配器初始化完成")

    def _init_connections(self) -> None:
        """初始化与各个智能体服务的连接"""
        # 获取智能体服务的配置
        agents = [
            "xiaoai_service",  # 小艾服务 - 四诊协调引擎
            "xiaoke_service",  # 小克服务 - 医疗资源调度
            "laoke_service",  # 老克服务 - 知识传播平台
            "soer_service",  # 索儿服务 - 健康管理引擎
        ]

        for agent in agents:
            try:
                # 获取服务地址
                host = config.get(
                    f"integration.{agent}.host", f"{agent.replace('_', '-')}"
                )
                port = config.get(f"integration.{agent}.port", 50052)
                timeout_ms = config.get(f"integration.{agent}.timeout_ms", 5000)

                # 创建通道
                channel = grpc.insecure_channel(
                    f"{host}:{port}",
                    options=[
                        ("grpc.max_send_message_length", 50 * 1024 * 1024),
                        ("grpc.max_receive_message_length", 50 * 1024 * 1024),
                        ("grpc.enable_retries", 1),
                        (
                            "grpc.service_config",
                            json.dumps(
                                {
                                    "methodConfig": [
                                        {
                                            "name": [{}],
                                            "retryPolicy": {
                                                "maxAttempts": 3,
                                                "initialBackoff": "0.1s",
                                                "maxBackoff": "1s",
                                                "backoffMultiplier": 2,
                                                "retryableStatusCodes": ["UNAVAILABLE"],
                                            },
                                            "timeout": f"{timeout_ms}ms",
                                        }
                                    ]
                                }
                            ),
                        ),
                    ],
                )
                self.channels[agent] = channel

                # 实际项目中应导入相应的stub
                # self.stubs[agent] = agent_pb2_grpc.AgentServiceStub(channel)
                # 这里为简化，不创建实际的stub
                logger.info(f"连接到{agent}服务: {host}:{port}")

            except Exception as e:
                logger.error(f"连接{agent}服务失败: {e!s}", exc_info=True)

    def register_accessibility_features(self) -> bool:
        """向所有智能体注册无障碍服务功能"""
        features = {
            "blind_assistance": config.get("features.blind_assistance.enabled", True),
            "sign_language": config.get("features.sign_language.enabled", True),
            "screen_reading": config.get("features.screen_reading.enabled", True),
            "voice_assistance": config.get("features.voice_assistance.enabled", True),
            "content_conversion": config.get(
                "features.content_conversion.enabled", True
            ),
        }

        success = True
        for agent in self.channels.keys():
            try:
                # 实际项目中应使用stub调用对应的方法
                # response = self.stubs[agent].RegisterAccessibilityFeatures(
                #     agent_pb2.RegisterFeaturesRequest(features=features)
                # )
                # success = success and response.success

                logger.info(f"向{agent}注册无障碍功能: {features}")
            except Exception as e:
                logger.error(f"向{agent}注册无障碍功能失败: {e!s}", exc_info=True)
                success = False

        return success

    def process_accessibility_request(
        self, agent_name: str, request_type: str, data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        处理来自智能体的无障碍请求

        Args:
            agent_name: 智能体名称
            request_type: 请求类型
            data: 请求数据

        Returns:
            处理结果，如果失败则返回None
        """
        agent_key = f"{agent_name}_service"
        if agent_key not in self.channels:
            logger.error(f"未知智能体: {agent_name}")
            return None

        logger.info(f"处理来自{agent_name}的{request_type}请求")
        start_time = time.time()

        try:
            # 实际项目中应根据请求类型调用相应的服务方法
            # 这里简化实现，返回预设响应

            if request_type == "blind_assistance":
                # 模拟处理导盲服务请求
                result = {
                    "success": True,
                    "scene_description": "前方是一条宽阔的人行道，左侧有一棵大树，右侧是小区入口",
                    "navigation_guidance": "可以继续直行，前方5米处有一个路口",
                }

            elif request_type == "sign_language":
                # 模拟处理手语识别请求
                result = {"success": True, "text": "我需要查询今天的体检预约"}

            elif request_type == "screen_reading":
                # 模拟处理屏幕阅读请求
                result = {
                    "success": True,
                    "screen_description": "当前屏幕显示体质测评结果页面，您的主要体质类型为阳虚质",
                    "elements": [
                        "体质测评结果",
                        "阳虚质",
                        "分数：85分",
                        "查看详情",
                        "健康建议",
                    ],
                }

            elif request_type == "voice_assistance":
                # 模拟处理语音辅助请求
                result = {
                    "success": True,
                    "response_text": "已为您找到最近的中医诊所，共有3家，最近的一家在步行10分钟的位置",
                }

            elif request_type == "content_conversion":
                # 模拟处理内容转换请求
                result = {
                    "success": True,
                    "accessible_content": "阳虚体质的主要特点是怕冷，手脚凉，喜热饮。建议多吃温补阳气的食物，如羊肉、韭菜等。",
                }

            else:
                logger.warning(f"未知请求类型: {request_type}")
                result = {"success": False, "error": f"未知请求类型: {request_type}"}

            elapsed_time = time.time() - start_time
            logger.info(
                f"处理来自{agent_name}的{request_type}请求完成，耗时: {elapsed_time:.2f}秒"
            )
            return result

        except Exception as e:
            logger.error(
                f"处理来自{agent_name}的{request_type}请求失败: {e!s}", exc_info=True
            )
            return {"success": False, "error": str(e)}

    def notify_accessibility_event(
        self, event_type: str, data: dict[str, Any]
    ) -> dict[str, bool]:
        """
        向所有智能体发送无障碍事件通知

        Args:
            event_type: 事件类型
            data: 事件数据

        Returns:
            各智能体处理结果，键为智能体名称，值为是否成功
        """
        results = {}
        logger.info(f"向智能体发送{event_type}事件")

        for agent_key in self.channels.keys():
            agent_name = agent_key.replace("_service", "")
            try:
                # 实际项目中应使用stub调用对应的方法
                # event_request = agent_pb2.AccessibilityEventRequest(
                #     event_type=event_type,
                #     data=json.dumps(data)
                # )
                # response = self.stubs[agent].NotifyAccessibilityEvent(event_request)
                # results[agent_name] = response.success

                # 模拟发送事件
                logger.info(f"已向{agent_name}发送{event_type}事件")
                results[agent_name] = True

            except Exception as e:
                logger.error(
                    f"向{agent_name}发送{event_type}事件失败: {e!s}", exc_info=True
                )
                results[agent_name] = False

        return results

    def get_agent_accessibility_capabilities(
        self, agent_name: str
    ) -> dict[str, Any] | None:
        """
        获取指定智能体的无障碍能力

        Args:
            agent_name: 智能体名称

        Returns:
            无障碍能力列表，如果失败则返回None
        """
        agent_key = f"{agent_name}_service"
        if agent_key not in self.channels:
            logger.error(f"未知智能体: {agent_name}")
            return None

        try:
            # 实际项目中应使用stub调用对应的方法
            # response = self.stubs[agent_key].GetAccessibilityCapabilities(
            #     agent_pb2.GetCapabilitiesRequest()
            # )
            # return json.loads(response.capabilities)

            # 模拟能力查询结果
            if agent_name == "xiaoai":
                return {
                    "voice_assistance": True,
                    "screen_reading": True,
                    "sign_language": True,
                    "blind_assistance": True,
                    "content_conversion": True,
                    "supported_languages": ["zh-CN", "en-US"],
                    "supported_dialects": ["mandarin", "cantonese", "sichuanese"],
                }
            elif agent_name == "xiaoke":
                return {
                    "voice_assistance": True,
                    "screen_reading": True,
                    "content_conversion": True,
                    "supported_languages": ["zh-CN"],
                }
            elif agent_name == "laoke":
                return {
                    "voice_assistance": True,
                    "content_conversion": True,
                    "supported_languages": ["zh-CN", "en-US"],
                }
            elif agent_name == "soer":
                return {
                    "voice_assistance": True,
                    "screen_reading": True,
                    "supported_languages": ["zh-CN"],
                }
            else:
                return {}

        except Exception as e:
            logger.error(f"获取{agent_name}无障碍能力失败: {e!s}", exc_info=True)
            return None

    def close(self) -> None:
        """关闭与智能体服务的连接"""
        for agent, channel in self.channels.items():
            try:
                channel.close()
                logger.info(f"关闭与{agent}的连接")
            except Exception as e:
                logger.error(f"关闭与{agent}的连接失败: {e!s}", exc_info=True)


# 单例实例
agent_adapter = AgentAdapter()
