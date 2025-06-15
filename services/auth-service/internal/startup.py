"""
应用启动初始化

初始化所有性能优化组件和服务。
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any

from fastapi import FastAPI

from .config.settings import get_settings
from .database.connection_manager import init_connection_manager, close_connection_manager
from .cache.redis_cache import init_cache, close_cache
from .async_tasks.task_manager import init_task_manager, shutdown_task_manager
from .middleware.rate_limiter import init_rate_limiter
from .database.query_optimizer import get_query_optimizer
from .discovery.service_registry import init_service_registry, shutdown_service_registry
from .grpc_client.client_manager import init_grpc_client_manager, shutdown_grpc_client_manager
from .ha.failover_manager import init_failover_manager, shutdown_failover_manager, NodeRole

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时初始化
    logger.info("🚀 开始初始化索克生活认证服务...")
    
    try:
        # 1. 初始化数据库连接池
        logger.info("📊 初始化数据库连接池...")
        await init_connection_manager()
        
        # 2. 初始化Redis缓存
        if settings.redis_enabled:
            logger.info("🗄️ 初始化Redis缓存...")
            await init_cache()
        
        # 3. 初始化任务管理器
        if settings.task_manager_enabled:
            logger.info("⚡ 初始化异步任务管理器...")
            await init_task_manager()
        
        # 4. 初始化速率限制器
        if settings.rate_limit_enabled:
            logger.info("🛡️ 初始化速率限制器...")
            await init_rate_limiter()
        
        # 5. 初始化查询优化器
        logger.info("🔧 初始化查询优化器...")
        query_optimizer = get_query_optimizer()
        
        # 6. 初始化服务注册中心
        if settings.service_discovery_enabled:
            logger.info("🔍 初始化服务注册中心...")
            await init_service_registry()
        
        # 7. 初始化gRPC客户端管理器
        if settings.grpc_enabled:
            logger.info("🌐 初始化gRPC客户端管理器...")
            await init_grpc_client_manager()
        
        # 8. 初始化故障转移管理器
        if settings.ha_enabled:
            logger.info("🔄 初始化高可用故障转移管理器...")
            # 根据配置确定节点角色
            node_role = NodeRole.PRIMARY if settings.ha_node_role == "primary" else NodeRole.SECONDARY
            node_priority = getattr(settings, 'ha_node_priority', 1)
            await init_failover_manager(role=node_role, priority=node_priority)
        
        # 9. 创建推荐的数据库索引（试运行模式）
        logger.info("📈 检查数据库索引优化...")
        try:
            index_results = await query_optimizer.create_recommended_indexes(dry_run=True)
            missing_indexes = [r for r in index_results if r["status"] == "would_create"]
            if missing_indexes:
                logger.warning(f"发现 {len(missing_indexes)} 个缺失的推荐索引，建议创建以提升性能")
                for idx in missing_indexes:
                    logger.info(f"  - {idx['index']} (表: {idx['table']})")
        except Exception as e:
            logger.warning(f"索引检查失败: {str(e)}")
        
        logger.info("✅ 索克生活认证服务初始化完成！")
        logger.info("🎯 服务已就绪，开始处理请求...")
        
        # 应用运行期间
        yield
        
    except Exception as e:
        logger.error(f"❌ 服务初始化失败: {str(e)}")
        raise
    
    finally:
        # 关闭时清理
        logger.info("🔄 开始关闭索克生活认证服务...")
        
        try:
            # 关闭故障转移管理器
            if settings.ha_enabled:
                logger.info("🔄 关闭故障转移管理器...")
                await shutdown_failover_manager()
            
            # 关闭gRPC客户端管理器
            if settings.grpc_enabled:
                logger.info("🌐 关闭gRPC客户端管理器...")
                await shutdown_grpc_client_manager()
            
            # 关闭服务注册中心
            if settings.service_discovery_enabled:
                logger.info("🔍 关闭服务注册中心...")
                await shutdown_service_registry()
            
            # 关闭任务管理器
            if settings.task_manager_enabled:
                logger.info("⚡ 关闭异步任务管理器...")
                await shutdown_task_manager()
            
            # 关闭Redis缓存
            if settings.redis_enabled:
                logger.info("🗄️ 关闭Redis缓存连接...")
                await close_cache()
            
            # 关闭数据库连接池
            logger.info("📊 关闭数据库连接池...")
            await close_connection_manager()
            
            logger.info("✅ 索克生活认证服务已安全关闭")
            
        except Exception as e:
            logger.error(f"❌ 服务关闭时发生错误: {str(e)}")


async def health_check_startup() -> bool:
    """
    启动时健康检查
    
    Returns:
        bool: 健康检查是否通过
    """
    logger.info("🔍 执行启动健康检查...")
    
    try:
        from .database.connection_manager import get_connection_manager
        from .cache.redis_cache import get_redis_cache
        
        # 检查数据库连接
        db_manager = get_connection_manager()
        db_health = await db_manager.health_check()
        
        if db_health.get("status") != "healthy":
            logger.error("❌ 数据库健康检查失败")
            return False
        
        logger.info(f"✅ 数据库连接正常 (响应时间: {db_health.get('response_time_ms', 0):.2f}ms)")
        
        # 检查Redis连接（如果启用）
        if settings.redis_enabled:
            cache = get_redis_cache()
            cache_health = await cache.health_check()
            
            if cache_health.get("status") != "healthy":
                logger.warning("⚠️ Redis缓存健康检查失败，将以降级模式运行")
            else:
                logger.info(f"✅ Redis缓存连接正常 (响应时间: {cache_health.get('response_time_ms', 0):.2f}ms)")
        
        logger.info("✅ 启动健康检查通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 启动健康检查失败: {str(e)}")
        return False


def setup_logging() -> None:
    """
    设置日志配置
    """
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 根据环境设置日志级别
    if settings.environment == "development":
        log_level = logging.DEBUG
    elif settings.environment == "testing":
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # 控制台输出
        ]
    )
    
    # 设置特定模块的日志级别
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    logger.info(f"📝 日志系统已配置 (级别: {logging.getLevelName(log_level)})")


async def performance_optimization_check() -> Dict[str, Any]:
    """
    性能优化检查
    
    Returns:
        Dict[str, Any]: 优化建议
    """
    logger.info("🔍 执行性能优化检查...")
    
    try:
        from .database.connection_manager import get_connection_manager
        from .cache.redis_cache import get_redis_cache
        from .database.query_optimizer import get_query_optimizer
        
        recommendations = []
        
        # 检查数据库配置
        db_manager = get_connection_manager()
        pool_metrics = await db_manager.get_pool_metrics()
        
        if pool_metrics.get("max_size", 0) < 10:
            recommendations.append("建议增加数据库连接池大小以提升并发性能")
        
        # 检查缓存配置
        if not settings.redis_enabled:
            recommendations.append("建议启用Redis缓存以提升查询性能")
        
        # 检查查询优化
        query_optimizer = get_query_optimizer()
        table_stats = await query_optimizer.get_table_statistics()
        
        for table_name, stats in table_stats.items():
            dead_rows = stats.get('dead_rows', 0)
            live_rows = stats.get('live_rows', 0)
            
            if dead_rows > 0 and live_rows > 0:
                dead_ratio = dead_rows / (live_rows + dead_rows)
                if dead_ratio > 0.1:
                    recommendations.append(f"表 {table_name} 需要执行 VACUUM 清理死行")
        
        # 检查任务队列配置
        if not settings.task_manager_enabled:
            recommendations.append("建议启用异步任务管理器以提升响应性能")
        
        result = {
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "status": "optimal" if len(recommendations) == 0 else "needs_optimization"
        }
        
        if recommendations:
            logger.info(f"📊 发现 {len(recommendations)} 个性能优化建议")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec}")
        else:
            logger.info("✅ 系统性能配置良好")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 性能优化检查失败: {str(e)}")
        return {
            "total_recommendations": 0,
            "recommendations": [],
            "status": "error",
            "error": str(e)
        }