#!/usr/bin/env python

"""
索儿(soer)智能体的无障碍服务客户端适配器
支持健康计划和传感器数据的无障碍转换
"""

import asyncio
import logging

# 导入配置
import os
import sys
from typing import Any

import grpc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 实际项目中需要导入生成的proto文件
# from accessibility_service.api.grpc import accessibility_pb2 as pb2
# from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)

class AccessibilityClient:
    """无障碍服务客户端适配器，为索儿智能体提供无障碍能力"""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        初始化客户端

        Args:
            config: 配置字典，包含无障碍服务的连接信息
        """
        self.config = config or {}
        self.channel = None
        self.stub = None
        self._connect()
        logger.info("索儿智能体无障碍服务客户端初始化完成")

    def _connect(self):
        """连接到无障碍服务"""
        try:
            # 从配置获取服务地址
            host = self.config.get('accessibility_service', {}).get('host', 'accessibility-service')
            port = self.config.get('accessibility_service', {}).get('port', 50051)

            # 创建gRPC通道
            self.channel = grpc.insecure_channel(f'{host}:{port}')

            # 导入生成的proto文件（实际项目中需要正确的导入路径）
            # from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc
            # self.stub = pb2_grpc.AccessibilityServiceStub(self.channel)

            # 模拟stub（实际项目中替换为真实的stub）
            self.stub = MockAccessibilityStub()

            logger.info(f"已连接到无障碍服务: {host}:{port}")

        except Exception as e:
            logger.error(f"连接无障碍服务失败: {e}")
            self.stub = MockAccessibilityStub()  # 使用模拟客户端作为降级

    async def convert_health_plan_to_accessible(self, health_plan: dict[str, Any],
                                              user_id: str, target_format: str = "audio") -> dict[str, Any]:
        """
        将健康计划转换为无障碍格式

        Args:
            health_plan: 健康计划信息
            user_id: 用户ID
            target_format: 目标格式（audio/simplified/braille）

        Returns:
            无障碍格式的健康计划
        """
        try:
            logger.info(f"转换健康计划: 用户={user_id}, 计划={health_plan.get('plan_name', 'unknown')}")

            # 构建请求
            request = {
                'content_id': f"health_plan_{health_plan.get('plan_id', 'unknown')}",
                'content_type': 'health_plan',
                'user_id': user_id,
                'target_format': target_format,
                'preferences': {
                    'language': 'zh-CN',
                    'voice_type': 'caring',
                    'speech_rate': 1.0,
                    'health_context': True,
                    'motivational_tone': True
                }
            }

            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)

            # 处理健康计划特定信息
            accessible_info = self._format_health_plan_content(health_plan, response, target_format)

            return {
                'accessible_content': accessible_info,
                'content_url': response.get('content_url', ''),
                'audio_content': response.get('audio_content', b''),
                'tactile_content': response.get('tactile_content', b''),
                'daily_reminders': self._generate_daily_reminders(health_plan, target_format),
                'progress_indicators': self._generate_progress_indicators(health_plan),
                'success': True
            }

        except Exception as e:
            logger.error(f"健康计划无障碍转换失败: {e}")
            return {
                'accessible_content': f'健康计划转换失败: {str(e)}',
                'content_url': '',
                'audio_content': b'',
                'tactile_content': b'',
                'daily_reminders': [],
                'progress_indicators': [],
                'success': False,
                'error': str(e)
            }

    def _format_health_plan_content(self, health_plan: dict[str, Any],
                                  response: dict[str, Any], target_format: str) -> str:
        """格式化健康计划内容"""
        plan_name = health_plan.get('plan_name', '未知计划')
        duration = health_plan.get('duration', '未知时长')
        goals = health_plan.get('goals', [])
        current_progress = health_plan.get('current_progress', 0)

        goals_text = '、'.join(goals) if goals else '无具体目标'

        if target_format == "simplified":
            return f"{plan_name}，时长{duration}，目标：{goals_text}，进度{current_progress}%"
        elif target_format == "audio":
            return f"健康计划：{plan_name}。计划时长：{duration}。主要目标：{goals_text}。当前进度：{current_progress}%。"
        else:
            return response.get('accessible_content', f"健康计划：{plan_name}")

    def _generate_daily_reminders(self, health_plan: dict[str, Any], target_format: str) -> list[dict[str, Any]]:
        """生成每日提醒"""
        reminders = []

        # 根据健康计划生成提醒
        goals = health_plan.get('goals', [])

        for goal in goals:
            if '运动' in goal:
                reminders.append({
                    'type': 'exercise',
                    'time': '09:00',
                    'content': '记得进行今日的运动计划',
                    'format': target_format
                })

            if '饮食' in goal or '营养' in goal:
                reminders.append({
                    'type': 'nutrition',
                    'time': '12:00',
                    'content': '记录午餐营养摄入',
                    'format': target_format
                })

            if '睡眠' in goal:
                reminders.append({
                    'type': 'sleep',
                    'time': '22:00',
                    'content': '准备就寝，保证充足睡眠',
                    'format': target_format
                })

        return reminders

    def _generate_progress_indicators(self, health_plan: dict[str, Any]) -> list[dict[str, Any]]:
        """生成进度指标"""
        indicators = []

        current_progress = health_plan.get('current_progress', 0)
        goals = health_plan.get('goals', [])

        for i, goal in enumerate(goals):
            indicator = {
                'goal': goal,
                'progress': min(current_progress + (i * 10), 100),  # 模拟不同目标的进度
                'status': 'on_track' if current_progress > 50 else 'needs_attention',
                'accessibility_description': f"目标{i+1}：{goal}，完成度{min(current_progress + (i * 10), 100)}%"
            }
            indicators.append(indicator)

        return indicators

    # 模拟的服务调用方法（实际项目中替换为真实的gRPC调用）
    async def _call_accessible_content(self, request: dict[str, Any]) -> dict[str, Any]:
        """调用无障碍内容转换服务"""
        await asyncio.sleep(0.1)
        content_type = request.get('content_type', 'unknown')

        if content_type == 'health_plan':
            return {
                'accessible_content': '个人健康计划：30天体重管理计划，目标减重5公斤，当前进度60%',
                'content_url': 'https://accessibility.suoke.life/health_plan/123',
                'audio_content': b'mock_health_plan_audio',
                'tactile_content': b'mock_health_plan_braille'
            }
        else:
            return {
                'accessible_content': '健康数据已转换为无障碍格式',
                'content_url': 'https://accessibility.suoke.life/content/general',
                'audio_content': b'mock_audio_content',
                'tactile_content': b'mock_braille_content'
            }

    def close(self):
        """关闭客户端连接"""
        if self.channel:
            self.channel.close()
        logger.info("索儿无障碍服务客户端连接已关闭")


class MockAccessibilityStub:
    """模拟的无障碍服务存根（用于开发和测试）"""

    def __init__(self):
        logger.info("使用模拟无障碍服务存根")

    async def AccessibleContent(self, request):
        """模拟无障碍内容转换"""
        await asyncio.sleep(0.1)
        return type('Response', (), {
            'accessible_content': '模拟健康数据无障碍转换',
            'content_url': 'https://mock.url',
            'audio_content': b'mock_health_audio',
            'tactile_content': b'mock_health_braille'
        })()


# 单例实例
accessibility_client = AccessibilityClient()
