"""
converters - 索克生活项目模块
"""

from datetime import datetime, date
from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct
from typing import Any, Dict, List, Union
import json

#! / usr / bin / env python
# - * - coding: utf - 8 - * -
"""
数据转换工具函数
"""



def dict_to_proto_struct(data: Dict[str, Any]) - > Struct:
    """
    将字典转换为Protobuf Struct

    Args:
        data: 要转换的字典

    Returns:
        Struct: Protobuf Struct对象
    """
    struct = Struct()
    struct.update(sanitize_dict_for_proto(data))
    return struct


def sanitize_dict_for_proto(data: Dict[str, Any]) - > Dict[str, Any]:
    """
    清理字典，使其可用于Protobuf转换

    Args:
        data: 原始字典

    Returns:
        Dict: 清理后的字典
    """
    result = {}

    for key, value in data.items():
        # 处理嵌套字典
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_proto(value)
        # 处理列表
        elif isinstance(value, list):
            result[key] = [
                sanitize_dict_for_proto(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        # 处理datetime和date
        elif isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
        # 处理其他类型
        else:
            result[key] = value

    return result


def proto_to_dict(message) - > Dict[str, Any]:
    """
    将Protobuf消息转换为字典

    Args:
        message: Protobuf消息

    Returns:
        Dict: 转换后的字典
    """
    return MessageToDict(
        message,
        preserving_proto_field_name = True,
        including_default_value_fields = True
    )


def pulse_features_to_dict(pulse_features) - > Dict[str, Any]:
    """
    将脉象特征proto对象转换为字典

    Args:
        pulse_features: 脉象特征proto对象

    Returns:
        Dict: 特征字典
    """
    features_dict = proto_to_dict(pulse_features)

    # 转换特征组
    if 'time_domain_features' in features_dict:
        features_dict['time_domain'] = {}
        for feature in features_dict['time_domain_features']:
            features_dict['time_domain'][feature['name']] = feature['value']
        del features_dict['time_domain_features']

    if 'frequency_domain_features' in features_dict:
        features_dict['frequency_domain'] = {}
        for feature in features_dict['frequency_domain_features']:
            features_dict['frequency_domain'][feature['name']] = feature['value']
        del features_dict['frequency_domain_features']

    if 'wavelet_features' in features_dict:
        features_dict['wavelet'] = {}
        for feature in features_dict['wavelet_features']:
            features_dict['wavelet'][feature['name']] = feature['value']
        del features_dict['wavelet_features']

    return features_dict


def abdominal_data_to_dict(abdominal_data) - > Dict[str, Any]:
    """
    将腹诊数据proto对象转换为字典

    Args:
        abdominal_data: 腹诊数据proto对象

    Returns:
        Dict: 转换后的字典
    """
    return proto_to_dict(abdominal_data)


def skin_data_to_dict(skin_data) - > Dict[str, Any]:
    """
    将皮肤触诊数据proto对象转换为字典

    Args:
        skin_data: 皮肤触诊数据proto对象

    Returns:
        Dict: 转换后的字典
    """
    return proto_to_dict(skin_data)


def list_to_bytes(data_list: List[float]) - > bytes:
    """
    将浮点数列表转换为字节流

    Args:
        data_list: 浮点数列表

    Returns:
        bytes: 字节流
    """
    return json.dumps(data_list).encode('utf - 8')


def bytes_to_list(data_bytes: bytes) - > List[float]:
    """
    将字节流转换为浮点数列表

    Args:
        data_bytes: 字节流

    Returns:
        List[float]: 浮点数列表
    """
    return json.loads(data_bytes.decode('utf - 8'))


def format_timestamp(timestamp: Union[float, datetime]) - > str:
    """
    格式化时间戳

    Args:
        timestamp: 时间戳或datetime对象

    Returns:
        str: 格式化的时间字符串
    """
    if isinstance(timestamp, float):
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = timestamp

    return dt.strftime('%Y - %m - %d %H:%M:%S.%f')[: - 3]  # 精确到毫秒