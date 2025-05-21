#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据验证工具
提供各种数据验证和转换函数
"""

import re
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

def validate_email(email: str) -> bool:
    """
    验证电子邮件格式
    
    Args:
        email: 电子邮件地址
        
    Returns:
        是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    验证手机号码格式（中国大陆手机号）
    
    Args:
        phone: 手机号码
        
    Returns:
        是否有效
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_datetime(date_string: str) -> bool:
    """
    验证日期时间格式（ISO 8601）
    
    Args:
        date_string: 日期时间字符串
        
    Returns:
        是否有效
    """
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except (ValueError, TypeError):
        return False

def validate_price(price: Union[int, float]) -> bool:
    """
    验证价格格式
    
    Args:
        price: 价格
        
    Returns:
        是否有效
    """
    if not isinstance(price, (int, float)):
        return False
    
    return price >= 0

def validate_quantity(quantity: int) -> bool:
    """
    验证数量格式
    
    Args:
        quantity: 数量
        
    Returns:
        是否有效
    """
    if not isinstance(quantity, int):
        return False
    
    return quantity > 0

def sanitize_input(input_string: str) -> str:
    """
    清理输入字符串，防止XSS和SQL注入
    
    Args:
        input_string: 输入字符串
        
    Returns:
        清理后的字符串
    """
    if input_string is None:
        return ""
    
    # 移除HTML标签
    input_string = re.sub(r'<[^>]*>', '', input_string)
    
    # 移除SQL注入关键字
    sql_patterns = [
        r'(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)(\s|$)',
        r'(\s|^)(FROM|WHERE|JOIN|UNION|GROUP BY)(\s|$)',
        r'(--|\#)',
        r'(;)',
    ]
    
    for pattern in sql_patterns:
        input_string = re.sub(pattern, ' ', input_string, flags=re.IGNORECASE)
    
    # 移除多余空格
    input_string = re.sub(r'\s+', ' ', input_string)
    
    return input_string.strip()

def parse_json_safe(json_string: str) -> Dict[str, Any]:
    """
    安全解析JSON字符串
    
    Args:
        json_string: JSON字符串
        
    Returns:
        解析后的字典，如果失败则返回空字典
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return {}