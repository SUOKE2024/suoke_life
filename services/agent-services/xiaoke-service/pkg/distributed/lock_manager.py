"""
lock_manager - 索克生活项目模块
"""

from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from enum import Enum
from typing import Any
import aioredis
import asyncio
import logging
import time
import uuid

#!/usr/bin/env python3
"""
分布式锁管理器
基于Redis实现分布式锁，支持可重入锁、读写锁，包含自动过期和死锁检测功能
"""



logger = logging.getLogger(__name__)


class LockType(Enum):
    """锁类型枚举"""

    EXCLUSIVE = "exclusive"  # 排他锁
    SHARED = "shared"  # 共享锁（读锁）
    REENTRANT = "reentrant"  # 可重入锁


@dataclass
class LockConfig:
    """锁配置"""

    timeout: float = 30.0  # 锁超时时间（秒）
    retry_interval: float = 0.1  # 重试间隔（秒）
    max_retries: int = 100  # 最大重试次数
    auto_extend: bool = True  # 是否自动延长锁
    extend_interval: float = 10.0  # 延长间隔（秒）


class DistributedLock:
    """分布式锁实现"""

    def __init__(
        self,
        redis_client: aioredis.Redis,
        key: str,
        lock_type: LockType = LockType.EXCLUSIVE,
        config: LockConfig = None,
    ):
        """
        初始化分布式锁

        Args:
            redis_client: Redis客户端
            key: 锁键名
            lock_type: 锁类型
            config: 锁配置
        """
        self.redis_client = redis_client
        self.key = key
        self.lock_type = lock_type
        self.config = config or LockConfig()

        # 锁标识符
        self.lock_id = str(uuid.uuid4())
        self.thread_id = id(asyncio.current_task())

        # 锁状态
        self.is_locked = False
        self.lock_count = 0  # 重入计数
        self.acquired_at = None

        # 自动延长任务
        self._extend_task: asyncio.Task | None = None

        logger.debug(
            "创建分布式锁: %s, 类型: %s, ID: %s", key, lock_type.value, self.lock_id
        )

    async def acquire(self, timeout: float | None = None) -> bool:
        """
        获取锁

        Args:
            timeout: 获取超时时间

        Returns:
            是否成功获取锁
        """
        timeout = timeout or self.config.timeout
        start_time = time.time()
        retries = 0

        while retries < self.config.max_retries:
            try:
                if self.lock_type == LockType.EXCLUSIVE:
                    success = await self._acquire_exclusive()
                elif self.lock_type == LockType.SHARED:
                    success = await self._acquire_shared()
                elif self.lock_type == LockType.REENTRANT:
                    success = await self._acquire_reentrant()
                else:
                    success = False

                if success:
                    self.is_locked = True
                    self.acquired_at = time.time()

                    # 启动自动延长任务
                    if self.config.auto_extend:
                        self._extend_task = asyncio.create_task(self._auto_extend())

                    logger.debug("成功获取锁: %s, 重试次数: %d", self.key, retries)
                    return True

                # 检查超时
                if time.time() - start_time >= timeout:
                    logger.warning(
                        "获取锁超时: %s, 耗时: %.2f秒",
                        self.key,
                        time.time() - start_time,
                    )
                    return False

                # 等待重试
                await asyncio.sleep(self.config.retry_interval)
                retries += 1

            except Exception as e:
                logger.error("获取锁异常: %s, 错误: %s", self.key, str(e))
                return False

        logger.warning("获取锁失败，已达最大重试次数: %s", self.key)
        return False

    async def _acquire_exclusive(self) -> bool:
        """获取排他锁"""
        # 使用SET命令的NX和EX选项实现原子操作
        result = await self.redis_client.set(
            self.key,
            self.lock_id,
            nx=True,  # 只在键不存在时设置
            ex=int(self.config.timeout),  # 设置过期时间
        )
        return result is not None

    async def _acquire_shared(self) -> bool:
        """获取共享锁（读锁）"""
        # 共享锁使用哈希表存储多个读者
        pipe = self.redis_client.pipeline()

        # 检查是否有写锁
        pipe.exists(f"{self.key}:write")
        # 添加读锁
        pipe.hset(f"{self.key}:read", self.lock_id, time.time())
        # 设置过期时间
        pipe.expire(f"{self.key}:read", int(self.config.timeout))

        results = await pipe.execute()

        # 如果有写锁，则获取失败
        if results[0]:
            await self.redis_client.hdel(f"{self.key}:read", self.lock_id)
            return False

        return True

    async def _acquire_reentrant(self) -> bool:
        """获取可重入锁"""
        # 检查是否已经持有锁
        current_holder = await self.redis_client.hget(self.key, "holder")

        if current_holder == f"{self.thread_id}:{self.lock_id}":
            # 已经持有锁，增加重入计数
            await self.redis_client.hincrby(self.key, "count", 1)
            await self.redis_client.expire(self.key, int(self.config.timeout))
            self.lock_count += 1
            return True

        # 尝试获取新锁
        pipe = self.redis_client.pipeline()
        pipe.hsetnx(self.key, "holder", f"{self.thread_id}:{self.lock_id}")
        pipe.hsetnx(self.key, "count", 1)
        pipe.expire(self.key, int(self.config.timeout))

        results = await pipe.execute()

        if results[0]:  # 成功设置holder
            self.lock_count = 1
            return True

        return False

    async def release(self) -> bool:
        """
        释放锁

        Returns:
            是否成功释放锁
        """
        if not self.is_locked:
            logger.warning("尝试释放未持有的锁: %s", self.key)
            return False

        try:
            # 停止自动延长任务
            if self._extend_task:
                self._extend_task.cancel()
                with suppress(asyncio.CancelledError):
                    await self._extend_task
                self._extend_task = None

            if self.lock_type == LockType.EXCLUSIVE:
                success = await self._release_exclusive()
            elif self.lock_type == LockType.SHARED:
                success = await self._release_shared()
            elif self.lock_type == LockType.REENTRANT:
                success = await self._release_reentrant()
            else:
                success = False

            if success:
                self.is_locked = False
                self.lock_count = 0
                logger.debug("成功释放锁: %s", self.key)

            return success

        except Exception as e:
            logger.error("释放锁异常: %s, 错误: %s", self.key, str(e))
            return False

    async def _release_exclusive(self) -> bool:
        """释放排他锁"""
        # 使用Lua脚本确保原子性
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """

        result = await self.redis_client.eval(lua_script, 1, self.key, self.lock_id)

        return result == 1

    async def _release_shared(self) -> bool:
        """释放共享锁"""
        # 从读锁哈希表中移除
        result = await self.redis_client.hdel(f"{self.key}:read", self.lock_id)

        # 检查是否还有其他读者
        readers_count = await self.redis_client.hlen(f"{self.key}:read")
        if readers_count == 0:
            await self.redis_client.delete(f"{self.key}:read")

        return result > 0

    async def _release_reentrant(self) -> bool:
        """释放可重入锁"""
        # 使用Lua脚本确保原子性
        lua_script = """
        local holder = redis.call("hget", KEYS[1], "holder")
        if holder == ARGV[1] then
            local count = redis.call("hincrby", KEYS[1], "count", -1)
            if count <= 0 then
                return redis.call("del", KEYS[1])
            else
                redis.call("expire", KEYS[1], ARGV[2])
                return 1
            end
        else
            return 0
        end
        """

        result = await self.redis_client.eval(
            lua_script,
            1,
            self.key,
            f"{self.thread_id}:{self.lock_id}",
            int(self.config.timeout),
        )

        if result > 0:
            self.lock_count -= 1
            if self.lock_count <= 0:
                return True

        return False

    async def _auto_extend(self):
        """自动延长锁的生存时间"""
        while self.is_locked:
            try:
                await asyncio.sleep(self.config.extend_interval)

                if not self.is_locked:
                    break

                # 延长锁的过期时间
                if self.lock_type == LockType.EXCLUSIVE:
                    await self._extend_exclusive()
                elif self.lock_type == LockType.SHARED:
                    await self._extend_shared()
                elif self.lock_type == LockType.REENTRANT:
                    await self._extend_reentrant()

                logger.debug("自动延长锁: %s", self.key)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("自动延长锁失败: %s, 错误: %s", self.key, str(e))
                break

    async def _extend_exclusive(self):
        """延长排他锁"""
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """

        await self.redis_client.eval(
            lua_script, 1, self.key, self.lock_id, int(self.config.timeout)
        )

    async def _extend_shared(self):
        """延长共享锁"""
        await self.redis_client.expire(f"{self.key}:read", int(self.config.timeout))

    async def _extend_reentrant(self):
        """延长可重入锁"""
        lua_script = """
        local holder = redis.call("hget", KEYS[1], "holder")
        if holder == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """

        await self.redis_client.eval(
            lua_script,
            1,
            self.key,
            f"{self.thread_id}:{self.lock_id}",
            int(self.config.timeout),
        )

    async def is_locked_by_me(self) -> bool:
        """检查锁是否被当前实例持有"""
        if self.lock_type == LockType.EXCLUSIVE:
            current_holder = await self.redis_client.get(self.key)
            return current_holder == self.lock_id
        elif self.lock_type == LockType.SHARED:
            return await self.redis_client.hexists(f"{self.key}:read", self.lock_id)
        elif self.lock_type == LockType.REENTRANT:
            current_holder = await self.redis_client.hget(self.key, "holder")
            return current_holder == f"{self.thread_id}:{self.lock_id}"

        return False

    async def __aenter__(self):
        """异步上下文管理器入口"""
        success = await self.acquire()
        if not success:
            raise RuntimeError(f"无法获取锁: {self.key}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.release()


class LockManager:
    """分布式锁管理器"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        初始化锁管理器

        Args:
            redis_url: Redis连接URL
        """
        self.redis_url = redis_url
        self.redis_client: aioredis.Redis | None = None

        # 活跃锁跟踪
        self.active_locks: dict[str, DistributedLock] = {}

        # 死锁检测
        self.deadlock_detector_task: asyncio.Task | None = None

        # 统计信息
        self.stats = {
            "locks_acquired": 0,
            "locks_released": 0,
            "lock_timeouts": 0,
            "deadlocks_detected": 0,
        }

        logger.info("分布式锁管理器初始化完成")

    async def initialize(self):
        """初始化Redis连接"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()

            # 启动死锁检测
            self.deadlock_detector_task = asyncio.create_task(self._deadlock_detector())

            logger.info("分布式锁管理器连接建立成功")

        except Exception as e:
            logger.error("分布式锁管理器连接失败: %s", str(e))
            raise

    def create_lock(
        self,
        key: str,
        lock_type: LockType = LockType.EXCLUSIVE,
        config: LockConfig = None,
    ) -> DistributedLock:
        """
        创建分布式锁

        Args:
            key: 锁键名
            lock_type: 锁类型
            config: 锁配置

        Returns:
            分布式锁实例
        """
        if not self.redis_client:
            raise RuntimeError("锁管理器未初始化")

        lock = DistributedLock(self.redis_client, key, lock_type, config)
        self.active_locks[key] = lock

        return lock

    @asynccontextmanager
    async def acquire_lock(
        self,
        key: str,
        lock_type: LockType = LockType.EXCLUSIVE,
        config: LockConfig = None,
        timeout: float | None = None,
    ):
        """
        获取锁的上下文管理器

        Args:
            key: 锁键名
            lock_type: 锁类型
            config: 锁配置
            timeout: 获取超时时间
        """
        lock = self.create_lock(key, lock_type, config)

        try:
            success = await lock.acquire(timeout)
            if not success:
                raise RuntimeError(f"无法获取锁: {key}")

            self.stats["locks_acquired"] += 1
            yield lock

        finally:
            if lock.is_locked:
                await lock.release()
                self.stats["locks_released"] += 1

            # 从活跃锁中移除
            if key in self.active_locks:
                del self.active_locks[key]

    async def force_release_lock(self, key: str) -> bool:
        """
        强制释放锁

        Args:
            key: 锁键名

        Returns:
            是否成功释放
        """
        try:
            # 删除所有相关的锁键
            keys_to_delete = [key, f"{key}:read", f"{key}:write"]

            result = await self.redis_client.delete(*keys_to_delete)

            # 从活跃锁中移除
            if key in self.active_locks:
                del self.active_locks[key]

            logger.warning("强制释放锁: %s", key)
            return result > 0

        except Exception as e:
            logger.error("强制释放锁失败: %s, 错误: %s", key, str(e))
            return False

    async def get_lock_info(self, key: str) -> dict[str, Any] | None:
        """
        获取锁信息

        Args:
            key: 锁键名

        Returns:
            锁信息字典
        """
        try:
            # 检查排他锁
            exclusive_holder = await self.redis_client.get(key)
            if exclusive_holder:
                ttl = await self.redis_client.ttl(key)
                return {"type": "exclusive", "holder": exclusive_holder, "ttl": ttl}

            # 检查共享锁
            readers = await self.redis_client.hgetall(f"{key}:read")
            if readers:
                ttl = await self.redis_client.ttl(f"{key}:read")
                return {
                    "type": "shared",
                    "readers": readers,
                    "reader_count": len(readers),
                    "ttl": ttl,
                }

            # 检查可重入锁
            reentrant_info = await self.redis_client.hgetall(key)
            if reentrant_info and "holder" in reentrant_info:
                ttl = await self.redis_client.ttl(key)
                return {
                    "type": "reentrant",
                    "holder": reentrant_info.get("holder"),
                    "count": int(reentrant_info.get("count", 0)),
                    "ttl": ttl,
                }

            return None

        except Exception as e:
            logger.error("获取锁信息失败: %s, 错误: %s", key, str(e))
            return None

    async def _deadlock_detector(self):
        """死锁检测器"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒检测一次

                # 获取所有锁键
                lock_keys = await self.redis_client.keys("*:lock:*")

                # 检测过期但未释放的锁
                for key in lock_keys:
                    ttl = await self.redis_client.ttl(key)
                    if ttl == -1:  # 没有设置过期时间
                        logger.warning("检测到可能的死锁: %s", key)
                        self.stats["deadlocks_detected"] += 1

                        # 可以选择强制释放
                        # await self.force_release_lock(key)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("死锁检测器错误: %s", str(e))
                await asyncio.sleep(60)  # 错误后延长检测间隔

    async def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        stats["active_locks_count"] = len(self.active_locks)
        stats["active_locks"] = list(self.active_locks.keys())

        return stats

    async def close(self):
        """关闭锁管理器"""
        # 停止死锁检测
        if self.deadlock_detector_task:
            self.deadlock_detector_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.deadlock_detector_task

        # 释放所有活跃锁
        for lock in list(self.active_locks.values()):
            if lock.is_locked:
                await lock.release()

        # 关闭Redis连接
        if self.redis_client:
            await self.redis_client.close()

        logger.info("分布式锁管理器已关闭")


# 装饰器函数
def distributed_lock(
    key: str,
    lock_type: LockType = LockType.EXCLUSIVE,
    config: LockConfig = None,
    timeout: float | None = None,
):
    """
    分布式锁装饰器

    Args:
        key: 锁键名
        lock_type: 锁类型
        config: 锁配置
        timeout: 获取超时时间
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            lock_manager = get_lock_manager()

            async with lock_manager.acquire_lock(key, lock_type, config, timeout):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# 全局锁管理器实例
_lock_manager: LockManager | None = None


async def get_lock_manager(redis_url: str = "redis://localhost:6379") -> LockManager:
    """获取锁管理器实例"""
    global _lock_manager

    if _lock_manager is None:
        _lock_manager = LockManager(redis_url)
        await _lock_manager.initialize()

    return _lock_manager


async def close_lock_manager():
    """关闭锁管理器"""
    global _lock_manager

    if _lock_manager:
        await _lock_manager.close()
        _lock_manager = None
