"""
数据验证器

提供各种数据验证功能
"""

from datetime import datetime
import logging
import re
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def validate_diagnosis_data(data: Dict[str, Any]) -> bool:
    """
    验证诊断数据的有效性

    Args:
        data: 诊断数据字典

    Returns:
        bool: 验证是否通过
    """
    try:
        # 基本字段验证
        required_fields = ['session_id', 'user_id', 'timestamp']
        for field in required_fields:
            if field not in data:
                logger.warning(f"缺少必需字段: {field}")
                return False

        # 会话ID验证
        if not isinstance(data['session_id'], str) or len(data['session_id']) < 1:
            logger.warning("无效的session_id")
            return False

        # 用户ID验证
        if not isinstance(data['user_id'], str) or len(data['user_id']) < 1:
            logger.warning("无效的user_id")
            return False

        # 时间戳验证
        if not isinstance(data['timestamp'], (int, float, str, datetime)):
            logger.warning("无效的timestamp")
            return False

        return True

    except Exception as e:
        logger.error(f"诊断数据验证失败: {e}")
        return False


def validate_user_input(text: str, max_length: int = 1000) -> bool:
    """
    验证用户输入文本

    Args:
        text: 输入文本
        max_length: 最大长度

    Returns:
        bool: 验证是否通过
    """
    if not isinstance(text, str):
        return False

    if len(text.strip()) == 0:
        return False

    if len(text) > max_length:
        return False

    # 检查是否包含恶意内容
    malicious_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'exec\s*\(',
    ]

    for pattern in malicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False

    return True


def validate_image_data(image_data: bytes, max_size: int = 10 * 1024 * 1024) -> bool:
    """
    验证图像数据

    Args:
        image_data: 图像二进制数据
        max_size: 最大文件大小(字节)

    Returns:
        bool: 验证是否通过
    """
    if not isinstance(image_data, bytes):
        return False

    if len(image_data) == 0:
        return False

    if len(image_data) > max_size:
        return False

    # 检查文件头，确保是有效的图像格式
    image_headers = [
        b'\xff\xd8\xff',  # JPEG
        b'\x89PNG\r\n\x1a\n',  # PNG
        b'GIF87a',  # GIF87a
        b'GIF89a',  # GIF89a
        b'RIFF',  # WebP (需要进一步检查)
    ]

    for header in image_headers:
        if image_data.startswith(header):
            return True

    return False


def validate_audio_data(audio_data: bytes, max_size: int = 50 * 1024 * 1024) -> bool:
    """
    验证音频数据

    Args:
        audio_data: 音频二进制数据
        max_size: 最大文件大小(字节)

    Returns:
        bool: 验证是否通过
    """
    if not isinstance(audio_data, bytes):
        return False

    if len(audio_data) == 0:
        return False

    if len(audio_data) > max_size:
        return False

    # 检查音频文件头
    audio_headers = [
        b'RIFF',  # WAV
        b'\xff\xfb',  # MP3
        b'\xff\xf3',  # MP3
        b'\xff\xf2',  # MP3
        b'fLaC',  # FLAC
        b'OggS',  # OGG
    ]

    for header in audio_headers:
        if audio_data.startswith(header):
            return True

    return False


def validate_medical_data(data: Dict[str, Any]) -> bool:
    """
    验证医疗数据

    Args:
        data: 医疗数据字典

    Returns:
        bool: 验证是否通过
    """
    try:
        # 检查基本结构
        if not isinstance(data, dict):
            return False

        # 验证必需字段
        required_fields = ['patient_id', 'data_type', 'timestamp']
        for field in required_fields:
            if field not in data:
                logger.warning(f"医疗数据缺少必需字段: {field}")
                return False

        # 验证数据类型
        valid_data_types = [
            'vital_signs',
            'symptoms',
            'diagnosis',
            'treatment',
            'medication',
            'lab_results',
        ]

        if data['data_type'] not in valid_data_types:
            logger.warning(f"无效的医疗数据类型: {data['data_type']}")
            return False

        return True

    except Exception as e:
        logger.error(f"医疗数据验证失败: {e}")
        return False


def validate_tcm_syndrome(syndrome_data: Dict[str, Any]) -> bool:
    """
    验证中医证型数据

    Args:
        syndrome_data: 证型数据

    Returns:
        bool: 验证是否通过
    """
    try:
        # 检查基本结构
        if not isinstance(syndrome_data, dict):
            return False

        # 验证必需字段
        required_fields = ['syndrome_name', 'confidence', 'symptoms']
        for field in required_fields:
            if field not in syndrome_data:
                logger.warning(f"证型数据缺少必需字段: {field}")
                return False

        # 验证置信度
        confidence = syndrome_data['confidence']
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            logger.warning(f"无效的置信度值: {confidence}")
            return False

        # 验证症状列表
        symptoms = syndrome_data['symptoms']
        if not isinstance(symptoms, list) or len(symptoms) == 0:
            logger.warning("症状列表无效或为空")
            return False

        return True

    except Exception as e:
        logger.error(f"证型数据验证失败: {e}")
        return False


def validate_constitution_data(constitution_data: Dict[str, Any]) -> bool:
    """
    验证体质数据

    Args:
        constitution_data: 体质数据

    Returns:
        bool: 验证是否通过
    """
    try:
        # 检查基本结构
        if not isinstance(constitution_data, dict):
            return False

        # 验证必需字段
        required_fields = ['constitution_type', 'score', 'characteristics']
        for field in required_fields:
            if field not in constitution_data:
                logger.warning(f"体质数据缺少必需字段: {field}")
                return False

        # 验证体质类型
        valid_types = [
            'peaceful',
            'qi_deficiency',
            'yang_deficiency',
            'yin_deficiency',
            'phlegm_dampness',
            'damp_heat',
            'blood_stasis',
            'qi_stagnation',
            'special_diathesis',
        ]

        if constitution_data['constitution_type'] not in valid_types:
            logger.warning(f"无效的体质类型: {constitution_data['constitution_type']}")
            return False

        # 验证评分
        score = constitution_data['score']
        if not isinstance(score, (int, float)) or not (0 <= score <= 100):
            logger.warning(f"无效的体质评分: {score}")
            return False

        return True

    except Exception as e:
        logger.error(f"体质数据验证失败: {e}")
        return False
