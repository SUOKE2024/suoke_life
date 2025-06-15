#!/usr/bin/env python

"""
缓存装饰器
提供函数级别的缓存功能
"""

import asyncio
import functools
import hashlib
import json
import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)

# 全局缓存管理器实例
_cache_manager = None


def set_cache_manager(manager):
    """设置全局缓存管理器"""
    global _cache_manager
    _cache_manager = manager


def _generate_cache_key(
    func: Callable,
    args: tuple,
    kwargs: dict,
    key_prefix: str = None,
    include_args: bool = True,
) -> str:
    """
    生成缓存键

    Args:
        func: 函数对象
        args: 位置参数
        kwargs: 关键字参数
        key_prefix: 键前缀
        include_args: 是否包含参数

    Returns:
        缓存键字符串
    """
    # 基础键
    base_key = key_prefix or f"{func.__module__}.{func.__name__}"

    if not include_args:
        return base_key

    # 参数序列化
    try:
        # 过滤掉不可序列化的参数
        serializable_args = []
        for arg in args:
            if isinstance(arg, str | int | float | bool | type(None)):
                serializable_args.append(arg)
            elif isinstance(arg, list | tuple | dict):
                try:
                    json.dumps(arg)
                    serializable_args.append(arg)
                except (TypeError, ValueError):
                    serializable_args.append(str(arg))
            else:
                serializable_args.append(str(arg))

        serializable_kwargs = {}
        for k, v in kwargs.items():
            if isinstance(v, str | int | float | bool | type(None)):
                serializable_kwargs[k] = v
            elif isinstance(v, list | tuple | dict):
                try:
                    json.dumps(v)
                    serializable_kwargs[k] = v
                except (TypeError, ValueError):
                    serializable_kwargs[k] = str(v)
            else:
                serializable_kwargs[k] = str(v)

        # 生成参数哈希
        args_str = json.dumps([serializable_args, serializable_kwargs], sort_keys=True)
        args_hash = hashlib.sha256(args_str.encode()).hexdigest()[:16]

        return f"{base_key}:{args_hash}"

    except Exception as e:
        logger.warning(f"生成缓存键失败: {e!s}, 使用基础键")
        return base_key


def cache_result(
    ttl: int = 3600,
    key_prefix: str = None,
    include_args: bool = True,
    cache_level: str = "memory",
    condition: Callable = None,
):
    """
    缓存结果装饰器

    Args:
        ttl: 缓存过期时间（秒）
        key_prefix: 缓存键前缀
        include_args: 是否在缓存键中包含参数
        cache_level: 缓存级别 (memory, redis, disk)
        condition: 缓存条件函数，返回True时才缓存
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(
                func, args, kwargs, key_prefix, include_args
            )

            # 尝试从缓存获取
            if _cache_manager:
                try:
                    cached_result = await _cache_manager.get(
                        cache_key, level=cache_level
                    )
                    if cached_result is not None:
                        logger.debug(f"缓存命中: {cache_key}")
                        return cached_result
                except Exception as e:
                    logger.warning(f"缓存获取失败: {e!s}")

            # 执行函数
            result = await func(*args, **kwargs)

            # 检查缓存条件
            should_cache = True
            if condition:
                try:
                    should_cache = condition(result, *args, **kwargs)
                except Exception as e:
                    logger.warning(f"缓存条件检查失败: {e!s}")
                    should_cache = True

            # 缓存结果
            if should_cache and _cache_manager:
                try:
                    await _cache_manager.set(
                        cache_key, result, ttl=ttl, level=cache_level
                    )
                    logger.debug(f"缓存设置: {cache_key}")
                except Exception as e:
                    logger.warning(f"缓存设置失败: {e!s}")

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(
                func, args, kwargs, key_prefix, include_args
            )

            # 尝试从缓存获取
            if _cache_manager:
                try:
                    # 对于同步函数，需要使用同步方法
                    import asyncio

                    loop = None
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    cached_result = loop.run_until_complete(
                        _cache_manager.get(cache_key, level=cache_level)
                    )
                    if cached_result is not None:
                        logger.debug(f"缓存命中: {cache_key}")
                        return cached_result
                except Exception as e:
                    logger.warning(f"缓存获取失败: {e!s}")

            # 执行函数
            result = func(*args, **kwargs)

            # 检查缓存条件
            should_cache = True
            if condition:
                try:
                    should_cache = condition(result, *args, **kwargs)
                except Exception as e:
                    logger.warning(f"缓存条件检查失败: {e!s}")
                    should_cache = True

            # 缓存结果
            if should_cache and _cache_manager:
                try:
                    import asyncio

                    loop = None
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    loop.run_until_complete(
                        _cache_manager.set(
                            cache_key, result, ttl=ttl, level=cache_level
                        )
                    )
                    logger.debug(f"缓存设置: {cache_key}")
                except Exception as e:
                    logger.warning(f"缓存设置失败: {e!s}")

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def cache_invalidate(
    key_pattern: str = None,
    key_prefix: str = None,
    include_args: bool = True,
    cache_level: str = "memory",
):
    """
    缓存失效装饰器

    Args:
        key_pattern: 缓存键模式
        key_prefix: 缓存键前缀
        include_args: 是否在缓存键中包含参数
        cache_level: 缓存级别
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 执行函数
            result = await func(*args, **kwargs)

            # 失效缓存
            if _cache_manager:
                try:
                    if key_pattern:
                        # 使用模式删除
                        await _cache_manager.delete_pattern(
                            key_pattern, level=cache_level
                        )
                    else:
                        # 生成具体的缓存键
                        cache_key = _generate_cache_key(
                            func, args, kwargs, key_prefix, include_args
                        )
                        await _cache_manager.delete(cache_key, level=cache_level)

                    logger.debug(f"缓存失效: {key_pattern or cache_key}")
                except Exception as e:
                    logger.warning(f"缓存失效失败: {e!s}")

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 执行函数
            result = func(*args, **kwargs)

            # 失效缓存
            if _cache_manager:
                try:
                    import asyncio

                    loop = None
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    if key_pattern:
                        # 使用模式删除
                        loop.run_until_complete(
                            _cache_manager.delete_pattern(
                                key_pattern, level=cache_level
                            )
                        )
                    else:
                        # 生成具体的缓存键
                        cache_key = _generate_cache_key(
                            func, args, kwargs, key_prefix, include_args
                        )
                        loop.run_until_complete(
                            _cache_manager.delete(cache_key, level=cache_level)
                        )

                    logger.debug(f"缓存失效: {key_pattern or cache_key}")
                except Exception as e:
                    logger.warning(f"缓存失效失败: {e!s}")

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def cache_warm_up(cache_keys: list, cache_level: str = "memory"):
    """
    缓存预热装饰器

    Args:
        cache_keys: 需要预热的缓存键列表
        cache_level: 缓存级别
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 预热缓存
            if _cache_manager:
                for cache_key in cache_keys:
                    try:
                        # 检查缓存是否存在
                        cached_value = await _cache_manager.get(
                            cache_key, level=cache_level
                        )
                        if cached_value is None:
                            logger.debug(f"缓存预热: {cache_key} 不存在，跳过")
                        else:
                            logger.debug(f"缓存预热: {cache_key} 已存在")
                    except Exception as e:
                        logger.warning(f"缓存预热失败: {cache_key}, 错误: {e!s}")

            # 执行函数
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 预热缓存
            if _cache_manager:
                import asyncio

                loop = None
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                for cache_key in cache_keys:
                    try:
                        # 检查缓存是否存在
                        cached_value = loop.run_until_complete(
                            _cache_manager.get(cache_key, level=cache_level)
                        )
                        if cached_value is None:
                            logger.debug(f"缓存预热: {cache_key} 不存在，跳过")
                        else:
                            logger.debug(f"缓存预热: {cache_key} 已存在")
                    except Exception as e:
                        logger.warning(f"缓存预热失败: {cache_key}, 错误: {e!s}")

            # 执行函数
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
