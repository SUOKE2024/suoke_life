"""
通用工具函数模块
"""

from difflib import SequenceMatcher
from .exceptions import ValidationError
from collections.abc import Callable
from datetime import timedelta
from typing import Any
import asyncio
import hashlib
import json
import re
import time
import uuid


def calculate_confidence(score: float, threshold: float = 0.5) -> float:
    """计算置信度"""
    if score < 0:
        return 0.0
    if score > 1:
        return 1.0
    
    # 应用阈值调整
    if score < threshold:
        return score * 0.5
    else:
        return 0.5 + (score - threshold) * 0.5 / (1 - threshold)


def normalize_text(text: str) -> str:
    """标准化文本"""
    if not text:
        return ""
    
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 转换为小写
    text = text.lower()
    
    return text


def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度"""
    if not text1 or not text2:
        return 0.0
    
    # 标准化文本
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    
    # 使用SequenceMatcher计算相似度
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def generate_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())


def generate_hash(data: str) -> str:
    """生成数据哈希"""
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        return default


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def format_duration(seconds: float) -> str:
    """格式化时间间隔"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def retry_async(max_retries: int = 3, delay: float = 1.0):
    """异步重试装饰器"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
                    
            raise last_exception
        return wrapper
    return decorator


def main()-> None:
    """主函数 - 自动生成的最小可用版本"""
    pass


def sanitize_text(text: str) -> str:
    """清理和标准化文本"""
    if not text:
        return ""
    
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 去除特殊字符，保留中文、英文、数字和基本标点
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,;:!?()（），。；：！？]', '', text)
    
    # 标准化空格
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text


if __name__ == "__main__":
    main()
