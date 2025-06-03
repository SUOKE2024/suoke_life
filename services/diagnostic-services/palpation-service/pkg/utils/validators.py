#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据验证工具函数
"""

import re
from typing import Any, Dict, List, Union, Optional

def validate_user_id(user_id: str) -> bool:
    """
    验证用户ID格式
    
    Args:
        user_id: 待验证的用户ID
        
    Returns:
        bool: 验证结果
    """
    if not user_id:
        return False
        
    # 用户ID应为24位十六进制字符串(MongoDB ObjectId格式)或UUID格式
    pattern = r'^[0-9a-fA-F]{24}$|^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, user_id))

def validate_session_id(session_id: str) -> bool:
    """
    验证会话ID格式
    
    Args:
        session_id: 待验证的会话ID
        
    Returns:
        bool: 验证结果
    """
    if not session_id:
        return False
        
    # 会话ID应为24位十六进制字符串(MongoDB ObjectId格式)或UUID格式
    pattern = r'^[0-9a-fA-F]{24}$|^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, session_id))

def validate_pulse_data(pulse_data: List[float]) -> bool:
    """
    验证脉搏数据格式和有效性
    
    Args:
        pulse_data: 脉搏波形数据
        
    Returns:
        bool: 验证结果
    """
    if not isinstance(pulse_data, list):
        return False
        
    # 数据长度检查
    if len(pulse_data) < 100:  # 采样率1000Hz，至少需要100ms数据
        return False
        
    # 数据类型检查
    if not all(isinstance(x, (int, float)) for x in pulse_data):
        return False
        
    # 数据范围检查
    if max(pulse_data) > 10000 or min(pulse_data) < -10000:
        return False
        
    # 基本质量检查 - 标准差太小说明信号可能是平直线
    if np.std(pulse_data) < 1e-6:
        return False
        
    return True

def validate_position(position: str) -> bool:
    """
    验证脉诊位置是否有效
    
    Args:
        position: 脉诊位置
        
    Returns:
        bool: 验证结果
    """
    valid_positions = [
        'left_cun', 'left_guan', 'left_chi',
        'right_cun', 'right_guan', 'right_chi'
    ]
    return position in valid_positions

def validate_abdominal_region(region: str) -> bool:
    """
    验证腹诊区域是否有效
    
    Args:
        region: 腹诊区域
        
    Returns:
        bool: 验证结果
    """
    valid_regions = [
        'epigastric', 'left_hypochondriac', 'right_hypochondriac', 
        'umbilical', 'left_lumbar', 'right_lumbar',
        'hypogastric', 'left_iliac', 'right_iliac'
    ]
    return region in valid_regions

def validate_skin_region(region: str) -> bool:
    """
    验证皮肤触诊区域是否有效
    
    Args:
        region: 皮肤触诊区域
        
    Returns:
        bool: 验证结果
    """
    valid_regions = [
        'forehead', 'cheek', 'neck', 'chest', 'back',
        'abdomen', 'arm', 'forearm', 'hand', 'thigh', 
        'leg', 'foot'
    ]
    return region in valid_regions

def validate_abdominal_data(data: Dict[str, Any]) -> bool:
    """
    验证腹诊数据格式和有效性
    
    Args:
        data: 腹诊数据
        
    Returns:
        bool: 验证结果
    """
    required_keys = ['region', 'tenderness', 'tension', 'texture', 'mass']
    
    # 检查必要字段
    if not all(key in data for key in required_keys):
        return False
        
    # 验证区域
    if not validate_abdominal_region(data['region']):
        return False
        
    # 验证评分范围
    for key in ['tenderness', 'tension']:
        if not (isinstance(data[key], (int, float)) and 0 <= data[key] <= 10):
            return False
            
    # 验证质地类型
    valid_textures = ['soft', 'firm', 'hard', 'normal']
    if data['texture'] not in valid_textures:
        return False
        
    # 验证肿块信息
    if not isinstance(data['mass'], bool):
        return False
        
    return True

def validate_skin_data(data: Dict[str, Any]) -> bool:
    """
    验证皮肤触诊数据格式和有效性
    
    Args:
        data: 皮肤触诊数据
        
    Returns:
        bool: 验证结果
    """
    required_keys = ['region', 'moisture', 'elasticity', 'texture', 'temperature', 'color']
    
    # 检查必要字段
    if not all(key in data for key in required_keys):
        return False
        
    # 验证区域
    if not validate_skin_region(data['region']):
        return False
        
    # 验证评分范围
    for key in ['moisture', 'elasticity']:
        if not (isinstance(data[key], (int, float)) and 0 <= data[key] <= 10):
            return False
            
    # 验证质地类型
    valid_textures = ['smooth', 'rough', 'oily', 'dry', 'normal']
    if data['texture'] not in valid_textures:
        return False
        
    # 验证温度
    valid_temperatures = ['cold', 'cool', 'normal', 'warm', 'hot']
    if data['temperature'] not in valid_temperatures:
        return False
        
    # 验证颜色
    valid_colors = ['pale', 'red', 'yellow', 'cyanotic', 'normal']
    if data['color'] not in valid_colors:
        return False
        
    return True 