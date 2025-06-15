"""
通用工具函数
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    读取JSON文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        解析后的JSON对象
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON解析错误
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到文件: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(file_path: Union[str, Path], data: Any, indent: int = 2) -> None:
    """
    写入JSON文件
    
    Args:
        file_path: 文件路径
        data: 要写入的数据
        indent: 缩进空格数
        
    Raises:
        IOError: 写入失败
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def timer(func):
    """
    函数执行时间装饰器
    
    Args:
        func: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"函数 {func.__name__} 执行时间: {end_time - start_time:.4f} 秒")
        return result
    return wrapper


def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    确保目录存在
    
    Args:
        directory: 目录路径
        
    Returns:
        目录路径对象
        
    Raises:
        IOError: 创建目录失败
    """
    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原文本
        max_length: 最大长度
        suffix: 截断后添加的后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_filename(name: str) -> str:
    """
    生成安全的文件名
    
    Args:
        name: 原文件名
        
    Returns:
        安全的文件名
    """
    # 替换特殊字符
    for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ']:
        name = name.replace(char, '_')
    return name