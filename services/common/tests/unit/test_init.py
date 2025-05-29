#!/usr/bin/env python3
"""
测试 suoke_common 包的基本功能
"""

from unittest.mock import patch

import pytest

from suoke_common import (
    SuokeCommonComponents,
    __version__,
    get_components,
    shutdown_components,
)


class TestSuokeCommonComponents:
    """测试 SuokeCommonComponents 类"""

    def test_version_exists(self):
        """测试版本号存在"""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_component_manager_creation(self):
        """测试组件管理器创建"""
        manager = SuokeCommonComponents()
        assert manager is not None
        assert not manager.initialized
        assert manager.components == {}

    @pytest.mark.asyncio
    async def test_component_manager_initialization(self):
        """测试组件管理器初始化"""
        manager = SuokeCommonComponents()

        # 使用空配置进行初始化
        config = {}
        await manager.initialize(config)

        assert manager.initialized
        assert isinstance(manager.components, dict)

    @pytest.mark.asyncio
    async def test_component_manager_shutdown(self):
        """测试组件管理器关闭"""
        manager = SuokeCommonComponents()

        # 初始化
        config = {}
        await manager.initialize(config)

        # 关闭
        await manager.shutdown()

        # 验证状态
        assert not manager.initialized

    def test_get_component_not_initialized(self):
        """测试未初始化时获取组件抛出异常"""
        manager = SuokeCommonComponents()

        with pytest.raises(RuntimeError, match="组件尚未初始化"):
            manager.get_component("security", "encryption")

    @pytest.mark.asyncio
    async def test_get_component_not_found(self):
        """测试获取不存在的组件"""
        manager = SuokeCommonComponents()

        # 初始化
        config = {}
        await manager.initialize(config)

        # 获取不存在的组件
        with pytest.raises(ValueError, match="未知的组件类型"):
            manager.get_component("nonexistent", "component")

    @pytest.mark.asyncio
    async def test_global_component_manager(self):
        """测试全局组件管理器"""
        manager1 = await get_components()
        manager2 = await get_components()

        # 应该返回同一个实例
        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_shutdown_components(self):
        """测试全局组件关闭"""
        # 获取全局管理器
        manager = await get_components()

        # 初始化状态检查
        assert manager.initialized

        # 关闭
        await shutdown_components()

        # 验证状态
        assert not manager.initialized


class TestComponentManagerIntegration:
    """测试组件管理器集成功能"""

    @pytest.mark.asyncio
    async def test_component_lifecycle(self):
        """测试组件完整生命周期"""
        manager = SuokeCommonComponents()

        # 1. 初始化
        config = {
            "security": {"encryption": {"algorithm": "AES-256-GCM", "key_size": 32}}
        }

        await manager.initialize(config)
        assert manager.initialized

        # 2. 获取组件组
        security_components = manager.get_component("security")
        assert isinstance(security_components, dict)

        # 3. 关闭
        await manager.shutdown()
        assert not manager.initialized

    @pytest.mark.asyncio
    async def test_multiple_initialization(self):
        """测试多次初始化"""
        manager = SuokeCommonComponents()

        config = {}

        # 第一次初始化
        await manager.initialize(config)
        assert manager.initialized

        # 第二次初始化应该跳过
        with patch("suoke_common.logger") as mock_logger:
            await manager.initialize(config)
            mock_logger.warning.assert_called_once()

        # 状态应该保持不变
        assert manager.initialized

        # 清理
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        manager = SuokeCommonComponents()

        # 未初始化时的健康检查
        health = await manager.health_check()
        assert health["status"] == "not_initialized"

        # 初始化后的健康检查
        await manager.initialize({})
        health = await manager.health_check()
        assert health["status"] in ["healthy", "degraded"]
        assert "components" in health
        assert "timestamp" in health

        # 清理
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_error_handling_during_initialization(self):
        """测试初始化过程中的错误处理"""
        manager = SuokeCommonComponents()

        # 使用可能导致错误的配置
        config = {"invalid_component": {"invalid_setting": "invalid_value"}}

        # 初始化应该成功（因为我们的实现比较宽松）
        await manager.initialize(config)
        assert manager.initialized

        # 清理
        await manager.shutdown()
