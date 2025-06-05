#!/usr/bin/env python3
"""
小艾服务的基本测试
"""

import asyncio
import logging
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# 添加项目根目录到PYTHONPATH
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from xiaoai.agent.agent_manager import AgentManager
from xiaoai.delivery.xiaoai_service_impl import XiaoAIServiceImpl
from xiaoai.orchestrator.diagnosis_coordinator import DiagnosisCoordinator

try:
    from xiaoai.api.grpc import xiaoai_pb2
except ImportError:
    logging.error("无法导入gRPC生成的代码。请确保先运行 'python -m grpc_tools.protoc' 命令来生成。")
    sys.exit(1)

class TestXiaoAIService(unittest.TestCase):
    """小艾服务的测试类"""

    def setUp(self):
        """测试初始化"""
        # 配置测试日志
        logging.basicConfig(level=logging.DEBUG)

        self.mock_agent_manager = MagicMock(spec=AgentManager)
        self.mock_diagnosis_coordinator = MagicMock(spec=DiagnosisCoordinator)

        self.service = XiaoAIServiceImpl()

        # 替换服务依赖为模拟对象
        self.service.agent_manager = self.mock_agent_manager
        self.service.diagnosis_coordinator = self.mock_diagnosis_coordinator

    async def test_health_check(self):
        """测试健康检查接口"""
        request = xiaoai_pb2.HealthCheckRequest(include_details=True)

        response = await self.service.HealthCheck(request, None)

        # 验证响应
        self.assertEqual(response.status, xiaoai_pb2.HealthCheckResponse.SERVING)
        self.assertIn('mongodb', response.details)

    async def test_chat_stream(self):
        """测试聊天流接口"""
        # 配置模拟对象的行为
        self.mock_agent_manager.chat.return_value = {
            'message_id': '123',
            'message': '你好,我是小艾',
            'confidence': 0.95,
            'suggested_actions': ['继续对话', '查看健康报告'],
            'metadata': {'model': 'gpt-4o-mini', 'timestamp': 1234567890}
        }

        request = xiaoai_pb2.ChatRequest(
            user_id='test_user',
            message='你好',
            session_id='test_session',
            context_size=5
        )

        responses = [r async for r in self.service.ChatStream(request, None)]

        # 验证响应
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0].message, '你好,我是小艾')
        self.assertEqual(responses[0].confidence, 0.95)
        self.assertEqual(len(responses[0].suggested_actions), 2)

        self.mock_agent_manager.chat.assert_called_once_with(
            'test_user', '你好', 'test_session', 5
        )

    async def test_coordinate_diagnosis(self):
        """测试四诊协调接口"""
        # 配置模拟对象的行为
        self.mock_diagnosis_coordinator.coordinate_diagnosis.return_value = xiaoai_pb2.DiagnosisCoordinationResponse(
            coordination_id='test_coordination',
            summary='诊断结果摘要',
            timestamp=1234567890
        )

        request = xiaoai_pb2.DiagnosisCoordinationRequest(
            user_id='test_user',
            session_id='test_session',
            include_looking=True,
            include_listening=False,
            include_inquiry=True,
            include_palpation=False,
            looking_data=b'test_image_data',
            inquiry_data='我最近感觉疲劳'
        )

        response = await self.service.CoordinateDiagnosis(request, None)

        # 验证响应
        self.assertEqual(response.coordination_id, 'test_coordination')
        self.assertEqual(response.summary, '诊断结果摘要')

        self.mock_diagnosis_coordinator.coordinate_diagnosis.assert_called_once_with(request)

    async def test_process_multimodal_input(self):
        """测试多模态输入处理接口"""
        # 配置模拟对象的行为
        self.mock_agent_manager.process_multimodal_input.return_value = {
            'request_id': 'test_request',
            'text_result': {
                'processed_text': '处理后的文本',
                'detected_language': 'zh-CN',
                'intent_scores': {'greeting': 0.8},
                'entities': {},
                'sentiment_score': 0.2
            },
            'confidence': 0.9,
            'metadata': {'session_id': 'test_session', 'timestamp': 1234567890}
        }

        text_input = xiaoai_pb2.TextInput(text='你好', language='zh-CN')
        request = xiaoai_pb2.MultimodalRequest(
            user_id='test_user',
            session_id='test_session',
            text=text_input
        )

        response = await self.service.ProcessMultimodalInput(request, None)

        # 验证响应
        self.assertEqual(response.request_id, 'test_request')
        self.assertEqual(response.confidence, 0.9)
        self.assertEqual(response.text_result.processed_text, '处理后的文本')

        self.mock_agent_manager.process_multimodal_input.assert_called_once()

def run_tests():
    """运行所有测试"""
    unittest.TestSuite()

    # 添加异步测试
    # 由于unittest不直接支持异步测试,所以需要使用协程包装器
    async def run_async_tests():
        # 测试实例
        test_case = TestXiaoAIService()
        test_case.setUp()

        # 运行测试方法
        await test_case.test_health_check()
        await test_case.test_chat_stream()
        await test_case.test_coordinate_diagnosis()
        await test_case.test_process_multimodal_input()

    # 运行异步测试
    asyncio.run(run_async_tests())

    print("所有测试通过!")

if __name__ == '__main__':
    run_tests()
