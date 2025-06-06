"""
__init__ - 索克生活项目模块
"""

from .cache_manager import CacheLevel, CacheStrategy, SmartCacheManager
from .config_manager import (
from .container import (
from .database import *
from .database_pool import (
from .event_bus import (
from .models import *
from .performance_monitor import (

"""
基础设施模块初始化
提供便捷的导入和初始化函数
"""

    ConfigManager,
    get_config,
    get_config_manager,
    init_config_manager,
)
    DependencyInjectionContainer,
    get_container,
    init_container,
    init_global_container,
)
    DatabasePoolManager,
    get_database_connection,
    get_database_pool_manager,
    init_database_pools,
)
    Event,
    EventBus,
    EventPriority,
    event_handler,
    get_event_bus,
    init_event_bus,
)
    PerformanceMonitor,
    get_performance_monitor,
    init_performance_monitor,
)

__all__ = [
    # 性能监控
    "PerformanceMonitor",
    "init_performance_monitor",
    "get_performance_monitor",
    # 缓存管理
    "SmartCacheManager",
    "CacheLevel",
    "CacheStrategy",
    # 配置管理
    "ConfigManager",
    "init_config_manager",
    "get_config_manager",
    "get_config",
    # 依赖注入
    "DependencyInjectionContainer",
    "init_container",
    "get_container",
    "init_global_container",
    # 数据库连接池
    "DatabasePoolManager",
    "init_database_pools",
    "get_database_pool_manager",
    "get_database_connection",
    # 事件总线
    "EventBus",
    "Event",
    "EventPriority",
    "init_event_bus",
    "get_event_bus",
    "event_handler",
]


async def init_infrastructure(config: dict) -> dict:
    """
    初始化所有基础设施组件

    Args:
        config: 配置字典

    Returns:
        dict: 初始化后的组件实例
    """
    components = {}

    # 初始化配置管理器
    config_paths = config.get("config_paths", ["config/config.yaml"])
    config_manager = await init_config_manager(config_paths)
    components["config_manager"] = config_manager

    # 初始化性能监控
    performance_config = config.get("performance", {})
    performance_monitor = await init_performance_monitor(performance_config)
    components["performance_monitor"] = performance_monitor

    # 初始化数据库连接池
    database_config = config.get("database", {})
    if database_config:
        pool_manager = await init_database_pools(database_config)
        components["database_pool_manager"] = pool_manager

    # 初始化事件总线
    event_config = config.get("event_bus", {})
    if event_config:
        event_bus = await init_event_bus(event_config)
        components["event_bus"] = event_bus

    # 初始化依赖注入容器
    container = await init_global_container(config)
    components["container"] = container

    return components


async def cleanup_infrastructure():
    """清理所有基础设施组件"""
    try:
        # 清理容器
        container = get_container()
        await container.cleanup_all()
    except:
        pass

    try:
        # 清理数据库连接池
        pool_manager = get_database_pool_manager()
        await pool_manager.close_all()
    except:
        pass

    try:
        # 清理事件总线
        event_bus = get_event_bus()
        await event_bus.stop_workers()
    except:
        pass

    try:
        # 清理性能监控
        performance_monitor = get_performance_monitor()
        await performance_monitor.stop()
    except:
        pass
