#!/usr/bin/env python3

"""
修复后的集成测试
测试服务之间的协调工作和完整业务流程
"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

# 导入服务组件
from internal.service.coordinators import AccessibilityServiceCoordinator
from internal.service.dependency_injection import DIContainer
from internal.service.factories import AccessibilityServiceFactory


class TestServiceIntegrationFixed:
    """修复后的服务集成测试类"""

    @pytest_asyncio.fixture
    async def coordinator(self):
        """创建协调器"""
        # 创建mock依赖
        mock_model_manager = Mock()
        mock_cache_manager = Mock()
        mock_config_manager = Mock()
        mock_config_manager.get = Mock(return_value=True)

        # 创建DIContainer
        container = DIContainer()
        container.register(
            "model_manager", type(mock_model_manager), mock_model_manager
        )
        container.register(
            "cache_manager", type(mock_cache_manager), mock_cache_manager
        )
        container.register(
            "config_manager", type(mock_config_manager), mock_config_manager
        )

        # 创建工厂和协调器
        factory = AccessibilityServiceFactory(container)
        await factory.initialize()

        coordinator = AccessibilityServiceCoordinator(factory)
        await coordinator.initialize()

        return coordinator

    @pytest.mark.asyncio
    async def test_coordinator_initialization(self, coordinator):
        """测试协调器初始化"""
        assert coordinator is not None
        assert coordinator._initialized is True

        status = await coordinator.get_status()
        assert status["coordinator"]["initialized"] is True

        print("✅ 协调器初始化成功")

    @pytest.mark.asyncio
    async def test_cross_service_coordination(self, coordinator):
        """测试跨服务协调"""
        # 创建mock服务
        mock_blind_service = Mock()
        mock_blind_service.analyze_scene = AsyncMock(
            return_value={
                "user_id": "test_user",
                "scene_type": "indoor",
                "obstacles": [],
                "confidence": 0.85,
            }
        )

        mock_voice_service = Mock()
        mock_voice_service.text_to_speech = AsyncMock(return_value=b"fake_audio_data")

        coordinator._blind_assistance_service = mock_blind_service
        coordinator._voice_assistance_service = mock_voice_service

        # 测试综合辅助
        request_data = {
            "type": "scene_analysis_with_voice",
            "image_data": b"fake_image_data",
            "preferences": {
                "voice_enabled": True,
                "language": "zh-CN",
                "voice": {"speed": "normal"},
            },
            "location": {"lat": 39.9, "lng": 116.4},
        }

        result = await coordinator.comprehensive_assistance(request_data, "test_user")

        assert result is not None
        assert "scene_analysis" in result

        print("✅ 跨服务协调成功")

    @pytest.mark.asyncio
    async def test_parallel_execution(self, coordinator):
        """测试并行执行"""
        # 创建mock服务
        mock_blind_service = Mock()
        mock_blind_service.analyze_scene = AsyncMock(
            return_value={"scene_type": "outdoor", "obstacles": [], "confidence": 0.9}
        )

        coordinator._blind_assistance_service = mock_blind_service

        # 并行执行多个任务
        tasks = [
            coordinator.analyze_scene(b"fake_image_1", "user1", {}, {}),
            coordinator.analyze_scene(b"fake_image_2", "user2", {}, {}),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 2
        for result in results:
            assert "scene_type" in result

        print(f"✅ 并行执行成功: {len(results)} 个任务")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
