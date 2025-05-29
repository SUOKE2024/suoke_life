#!/usr/bin/env python

"""
通用工具函数模块
"""

import asyncio
from collections.abc import Callable
from datetime import timedelta
import hashlib
import json
import re
import time
from typing import Any
import uuid

from .exceptions import ValidationError


def validate_input(data: Any, schema: dict[str, Any]) -> bool:
    """验证输入数据"""
    if not isinstance(data, dict):
        raise ValidationError("输入数据必须是字典类型")

    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"缺少必需字段: {field}", field=field)

    field_types = schema.get("types", {})
    for field, expected_type in field_types.items():
        if field in data:
            if not isinstance(data[field], expected_type):
                raise ValidationError(
                    f"字段 {field} 类型错误，期望 {expected_type.__name__}，实际 {type(data[field]).__name__}",
                    field=field,
                    value=data[field],
                )

    return True


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """清理和标准化文本"""
    if not isinstance(text, str):
        raise ValidationError("输入必须是字符串类型")

    # 移除多余的空白字符
    text = re.sub(r"\s+", " ", text.strip())

    # 移除特殊字符（保留中文、英文、数字、基本标点）
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s\.,;:!?()（），。；：！？]", "", text)

    # 长度限制
    if len(text) > max_length:
        text = text[:max_length]

    return text


def calculate_confidence(
    factors: list[float], weights: list[float] | None = None
) -> float:
    """计算置信度"""
    if not factors:
        return 0.0

    if weights is None:
        weights = [1.0] * len(factors)

    if len(factors) != len(weights):
        raise ValueError("因子和权重数量不匹配")

    # 加权平均
    weighted_sum = sum(f * w for f, w in zip(factors, weights, strict=False))
    weight_sum = sum(weights)

    if weight_sum == 0:
        return 0.0

    confidence = weighted_sum / weight_sum

    # 确保在0-1范围内
    return max(0.0, min(1.0, confidence))


def generate_session_id() -> str:
    """生成会话ID"""
    return str(uuid.uuid4())


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """生成数据哈希"""
    if algorithm == "md5":
        return hashlib.md5(data.encode("utf-8")).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode("utf-8")).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")


def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def parse_time_expression(expression: str) -> timedelta | None:
    """解析时间表达式"""
    patterns = {
        r"(\d+)\s*天": lambda m: timedelta(days=int(m.group(1))),
        r"(\d+)\s*小时": lambda m: timedelta(hours=int(m.group(1))),
        r"(\d+)\s*分钟": lambda m: timedelta(minutes=int(m.group(1))),
        r"(\d+)\s*周": lambda m: timedelta(weeks=int(m.group(1))),
        r"(\d+)\s*月": lambda m: timedelta(days=int(m.group(1)) * 30),
        r"(\d+)\s*年": lambda m: timedelta(days=int(m.group(1)) * 365),
    }

    for pattern, converter in patterns.items():
        match = re.search(pattern, expression)
        if match:
            return converter(match)

    return None


def extract_numbers(text: str) -> list[float]:
    """从文本中提取数字"""
    pattern = r"-?\d+\.?\d*"
    matches = re.findall(pattern, text)
    return [float(match) for match in matches if match]


def fuzzy_match(
    query: str, candidates: list[str], threshold: float = 0.6
) -> list[tuple]:
    """模糊匹配"""
    try:
        from difflib import SequenceMatcher
    except ImportError:
        # 简单的包含匹配作为后备
        results = []
        query_lower = query.lower()
        for candidate in candidates:
            if query_lower in candidate.lower():
                results.append((candidate, 1.0))
        return results

    results = []
    for candidate in candidates:
        ratio = SequenceMatcher(None, query.lower(), candidate.lower()).ratio()
        if ratio >= threshold:
            results.append((candidate, ratio))

    # 按相似度排序
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def chunk_list(lst: list[Any], chunk_size: int) -> list[list[Any]]:
    """将列表分块"""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(
    d: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """扁平化字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    """反扁平化字典"""
    result = {}
    for key, value in d.items():
        keys = key.split(sep)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    return result


def safe_json_loads(data: str, default: Any = None) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default


def retry_async(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """异步重试装饰器"""

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception

            raise last_exception

        return wrapper

    return decorator


def rate_limit(calls_per_second: float):
    """速率限制装饰器"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

            last_called[0] = time.time()
            return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

            last_called[0] = time.time()
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def memoize(ttl_seconds: float | None = None):
    """内存缓存装饰器"""

    def decorator(func: Callable) -> Callable:
        cache = {}

        async def async_wrapper(*args, **kwargs):
            # 创建缓存键
            key = str(args) + str(sorted(kwargs.items()))

            # 检查缓存
            if key in cache:
                value, timestamp = cache[key]
                if ttl_seconds is None or time.time() - timestamp < ttl_seconds:
                    return value

            # 调用函数并缓存结果
            result = await func(*args, **kwargs)
            cache[key] = (result, time.time())

            return result

        def sync_wrapper(*args, **kwargs):
            # 创建缓存键
            key = str(args) + str(sorted(kwargs.items()))

            # 检查缓存
            if key in cache:
                value, timestamp = cache[key]
                if ttl_seconds is None or time.time() - timestamp < ttl_seconds:
                    return value

            # 调用函数并缓存结果
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class CircuitBreaker:
    """熔断器"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs):
        """调用函数，应用熔断逻辑"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("熔断器开启，拒绝调用")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # 成功调用，重置计数器
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
            self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

            raise e


def batch_process(items: list[Any], batch_size: int, processor: Callable) -> list[Any]:
    """批量处理"""
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batch_results = processor(batch)
        results.extend(batch_results)

    return results


async def batch_process_async(
    items: list[Any], batch_size: int, processor: Callable
) -> list[Any]:
    """异步批量处理"""
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        if asyncio.iscoroutinefunction(processor):
            batch_results = await processor(batch)
        else:
            batch_results = processor(batch)
        results.extend(batch_results)

    return results


def get_nested_value(data: dict[str, Any], path: str, default: Any = None) -> Any:
    """获取嵌套字典的值"""
    keys = path.split(".")
    current = data

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def set_nested_value(data: dict[str, Any], path: str, value: Any) -> None:
    """设置嵌套字典的值"""
    keys = path.split(".")
    current = data

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """合并多个字典"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def deep_merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """深度合并字典"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result
