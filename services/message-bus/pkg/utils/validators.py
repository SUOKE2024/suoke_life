"""
验证工具，提供各种数据验证功能
"""
import re
import json
from typing import Dict, Any, Optional

def validate_topic_name(topic_name: str) -> bool:
    """
    验证主题名称格式是否有效
    
    规则:
    - 2-64个字符
    - 只能包含字母、数字、连字符和点
    - 不能以点或连字符开头或结尾
    
    Args:
        topic_name: 主题名称
        
    Returns:
        bool: 是否有效
    """
    if not topic_name or not isinstance(topic_name, str):
        return False
        
    # 长度检查
    if len(topic_name) < 2 or len(topic_name) > 64:
        return False
        
    # 字符检查
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$', topic_name):
        return False
        
    return True


def validate_json_message(message: str) -> bool:
    """
    验证消息是否为有效的JSON格式
    
    Args:
        message: 消息内容
        
    Returns:
        bool: 是否有效的JSON
    """
    if not message:
        return False
        
    try:
        json.loads(message)
        return True
    except json.JSONDecodeError:
        return False


def validate_message_attributes(attributes: Dict[str, str]) -> bool:
    """
    验证消息属性是否有效
    
    规则:
    - 属性键必须是字符串
    - 属性值必须是字符串
    - 属性键长度不超过128个字符
    - 属性值长度不超过1024个字符
    
    Args:
        attributes: 消息属性
        
    Returns:
        bool: 是否有效
    """
    if not attributes:
        return True
        
    if not isinstance(attributes, dict):
        return False
        
    for key, value in attributes.items():
        # 检查键类型
        if not isinstance(key, str):
            return False
            
        # 检查值类型
        if not isinstance(value, str):
            return False
            
        # 检查键长度
        if len(key) > 128:
            return False
            
        # 检查值长度
        if len(value) > 1024:
            return False
            
    return True


def validate_subscription_name(name: str) -> bool:
    """
    验证订阅名称格式是否有效
    
    规则:
    - 2-64个字符
    - 只能包含字母、数字、连字符和下划线
    - 不能以连字符或下划线开头或结尾
    
    Args:
        name: 订阅名称
        
    Returns:
        bool: 是否有效
    """
    if not name or not isinstance(name, str):
        return False
        
    # 长度检查
    if len(name) < 2 or len(name) > 64:
        return False
        
    # 字符检查
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\_]*[a-zA-Z0-9])?$', name):
        return False
        
    return True 