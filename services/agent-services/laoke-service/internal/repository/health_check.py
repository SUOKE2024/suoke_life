#!/usr/bin/env python

"""
健康检查存储库
"""

import asyncio
import logging
import time

from pkg.utils.config import Config
from pkg.utils.db_client import get_db_client
from pkg.utils.redis_client import get_redis_client

# 服务启动时间
START_TIME = time.time()

# 配置
config = Config()
logger = logging.getLogger(__name__)


class HealthCheckRepository:
    """健康检查存储库"""

    def __init__(self):
        """初始化健康检查存储库"""
        # 加载配置
        self.config = config

        # 超时设置
        self.db_timeout = self.config.get("metrics.health_check.timeout", 5)  # 数据库检查超时秒数
        self.cache_timeout = self.config.get("metrics.health_check.timeout", 2)  # 缓存检查超时秒数

    async def check_database_connection(self):
        """
        检查数据库连接

        返回:
            dict: 数据库连接状态
        """
        try:
            # 创建数据库客户端
            db_client = get_db_client()

            # 设置超时
            async with asyncio.timeout(self.db_timeout):
                # 执行简单查询
                if db_client.name == "mongodb":
                    # MongoDB
                    start_time = time.time()
                    result = await db_client.admin.command('ping')
                    latency = time.time() - start_time

                    return {
                        "status": result.get("ok", 0) == 1,
                        "details": {
                            "latency_ms": round(latency * 1000, 2),
                            "version": await self.get_db_version(db_client)
                        }
                    }
                elif db_client.name == "postgresql":
                    # PostgreSQL
                    start_time = time.time()
                    result = await db_client.fetch("SELECT 1")
                    latency = time.time() - start_time

                    return {
                        "status": len(result) > 0 and result[0][0] == 1,
                        "details": {
                            "latency_ms": round(latency * 1000, 2),
                            "version": await self.get_db_version(db_client)
                        }
                    }
                else:
                    # 不支持的数据库
                    return {
                        "status": False,
                        "details": {
                            "error": f"不支持的数据库类型: {db_client.name}"
                        }
                    }

        except TimeoutError:
            logger.error(f"数据库连接超时 (>{self.db_timeout}s)")
            return {
                "status": False,
                "details": {
                    "error": f"连接超时 (>{self.db_timeout}s)"
                }
            }
        except Exception as e:
            logger.error(f"数据库连接检查失败: {str(e)}")
            return {
                "status": False,
                "details": {
                    "error": str(e)
                }
            }

    async def get_db_version(self, db_client):
        """
        获取数据库版本

        参数:
            db_client: 数据库客户端

        返回:
            str: 数据库版本
        """
        try:
            if db_client.name == "mongodb":
                # MongoDB
                server_info = await db_client.admin.command('serverStatus')
                return server_info.get("version", "unknown")
            elif db_client.name == "postgresql":
                # PostgreSQL
                result = await db_client.fetch("SHOW server_version")
                return result[0][0] if result else "unknown"
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"获取数据库版本失败: {str(e)}")
            return "unknown"

    async def check_cache_connection(self):
        """
        检查缓存连接

        返回:
            dict: 缓存连接状态
        """
        try:
            # 获取Redis客户端
            redis_client = get_redis_client()

            # 设置超时
            async with asyncio.timeout(self.cache_timeout):
                # 执行简单命令
                start_time = time.time()
                pong = await redis_client.ping()
                latency = time.time() - start_time

                # 获取Redis信息
                info = await redis_client.info()

                return {
                    "status": pong,
                    "details": {
                        "latency_ms": round(latency * 1000, 2),
                        "version": info.get("redis_version", "unknown"),
                        "used_memory": info.get("used_memory_human", "unknown"),
                        "clients_connected": info.get("connected_clients", "unknown")
                    }
                }

        except TimeoutError:
            logger.error(f"缓存连接超时 (>{self.cache_timeout}s)")
            return {
                "status": False,
                "details": {
                    "error": f"连接超时 (>{self.cache_timeout}s)"
                }
            }
        except Exception as e:
            logger.error(f"缓存连接检查失败: {str(e)}")
            return {
                "status": False,
                "details": {
                    "error": str(e)
                }
            }

    def get_uptime(self):
        """
        获取服务运行时间

        返回:
            dict: 服务运行时间信息
        """
        uptime_seconds = int(time.time() - START_TIME)

        # 计算天、小时、分钟和秒
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        return {
            "total_seconds": uptime_seconds,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "formatted": f"{days}d {hours}h {minutes}m {seconds}s"
        }
