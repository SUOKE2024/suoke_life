"""
配置管理模块

提供统一的配置管理功能，包括：
- 动态配置管理
- 配置中心集成
- 配置热更新
- 多格式配置支持
"""

from typing import Dict, List, Any, Optional, Union

try:
    from .config_manager import ConfigManager, get_config_manager, config
    from .config_center import ConfigCenter, ConsulConfigCenter, EtcdConfigCenter
    
    __all__ = [
        "ConfigManager",
        "get_config_manager", 
        "config",
        "ConfigCenter",
        "ConsulConfigCenter",
        "EtcdConfigCenter",
    ]
    
except ImportError as e:
    import logging
    logging.warning(f"配置模块导入失败: {e}")
    __all__ = []


def main() -> None:
    """主函数 - 用于测试配置管理功能"""
    import asyncio
    
    async def test_config():
        """测试配置管理"""
        try:
            # 创建配置管理器
            manager = get_config_manager("test_service")
            
            # 设置配置
            manager.set("test.key", "test_value")
            
            # 获取配置
            value = manager.get("test.key")
            print(f"配置值: {value}")
            
        except Exception as e:
            print(f"配置测试失败: {e}")
    
    asyncio.run(test_config())


if __name__ == "__main__":
    main()
