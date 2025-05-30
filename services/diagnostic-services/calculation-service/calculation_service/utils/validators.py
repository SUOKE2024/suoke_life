"""
数据验证工具

提供各种数据验证功能
"""

import re
from datetime import datetime, date
from typing import Dict, Any, Optional

from ..exceptions import InvalidBirthInfoError, InvalidTimeError, ValidationError


def validate_birth_info(birth_info: Dict[str, Any]) -> bool:
    """
    验证出生信息
    
    Args:
        birth_info: 出生信息字典
        
    Returns:
        验证是否通过
        
    Raises:
        InvalidBirthInfoError: 出生信息无效
    """
    required_fields = ["year", "month", "day", "hour", "gender"]
    
    # 检查必需字段
    for field in required_fields:
        if field not in birth_info:
            raise InvalidBirthInfoError(f"缺少必需字段: {field}")
        
        if birth_info[field] is None:
            raise InvalidBirthInfoError(f"字段 {field} 不能为空")
    
    # 验证年份
    year = birth_info["year"]
    if not isinstance(year, int) or year < 1900 or year > 2100:
        raise InvalidBirthInfoError("年份必须在1900-2100之间")
    
    # 验证月份
    month = birth_info["month"]
    if not isinstance(month, int) or month < 1 or month > 12:
        raise InvalidBirthInfoError("月份必须在1-12之间")
    
    # 验证日期
    day = birth_info["day"]
    if not isinstance(day, int) or day < 1 or day > 31:
        raise InvalidBirthInfoError("日期必须在1-31之间")
    
    # 验证日期有效性
    try:
        date(year, month, day)
    except ValueError:
        raise InvalidBirthInfoError("无效的日期")
    
    # 验证时辰
    hour = birth_info["hour"]
    if not isinstance(hour, int) or hour < 0 or hour > 23:
        raise InvalidBirthInfoError("时辰必须在0-23之间")
    
    # 验证性别
    gender = birth_info["gender"]
    if gender not in ["男", "女"]:
        raise InvalidBirthInfoError("性别必须是'男'或'女'")
    
    return True


def validate_time_format(time_str: str, format_str: str = "%Y-%m-%d %H:%M") -> bool:
    """
    验证时间格式
    
    Args:
        time_str: 时间字符串
        format_str: 时间格式
        
    Returns:
        验证是否通过
        
    Raises:
        InvalidTimeError: 时间格式无效
    """
    try:
        datetime.strptime(time_str, format_str)
        return True
    except ValueError as e:
        raise InvalidTimeError(f"时间格式错误: {str(e)}")


def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串
        format_str: 日期格式
        
    Returns:
        验证是否通过
        
    Raises:
        InvalidTimeError: 日期格式无效
    """
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError as e:
        raise InvalidTimeError(f"日期格式错误: {str(e)}")


def validate_name(name: Optional[str]) -> bool:
    """
    验证姓名
    
    Args:
        name: 姓名
        
    Returns:
        验证是否通过
        
    Raises:
        ValidationError: 姓名验证失败
    """
    if name is None:
        return True
    
    if not isinstance(name, str):
        raise ValidationError("name", "姓名必须是字符串")
    
    if len(name.strip()) == 0:
        raise ValidationError("name", "姓名不能为空")
    
    if len(name) > 50:
        raise ValidationError("name", "姓名长度不能超过50个字符")
    
    # 检查是否包含特殊字符
    if re.search(r'[<>"\'/\\&]', name):
        raise ValidationError("name", "姓名不能包含特殊字符")
    
    return True


def validate_year_range(year: int, min_year: int = 1900, max_year: int = 2100) -> bool:
    """
    验证年份范围
    
    Args:
        year: 年份
        min_year: 最小年份
        max_year: 最大年份
        
    Returns:
        验证是否通过
        
    Raises:
        ValidationError: 年份验证失败
    """
    if not isinstance(year, int):
        raise ValidationError("year", "年份必须是整数")
    
    if year < min_year or year > max_year:
        raise ValidationError("year", f"年份必须在{min_year}-{max_year}之间")
    
    return True


def validate_analysis_options(options: Dict[str, bool]) -> bool:
    """
    验证分析选项
    
    Args:
        options: 分析选项字典
        
    Returns:
        验证是否通过
        
    Raises:
        ValidationError: 选项验证失败
    """
    valid_options = [
        "include_ziwu",
        "include_constitution", 
        "include_bagua",
        "include_wuyun_liuqi"
    ]
    
    for key, value in options.items():
        if key not in valid_options:
            raise ValidationError("options", f"无效的分析选项: {key}")
        
        if not isinstance(value, bool):
            raise ValidationError("options", f"选项 {key} 必须是布尔值")
    
    return True


def validate_date_range(input_date: date, min_year: int = 1900, max_year: int = 2100) -> None:
    """
    验证日期范围
    
    Args:
        input_date: 输入日期
        min_year: 最小年份
        max_year: 最大年份
        
    Raises:
        HTTPException: 日期超出范围时抛出异常
    """
    if input_date.year < min_year or input_date.year > max_year:
        raise HTTPException(
            status_code=400,
            detail=f"日期年份必须在{min_year}-{max_year}之间"
        )
    
    if input_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="日期不能晚于今天"
        )


def validate_patient_info(patient_info: Dict[str, Any]) -> None:
    """
    验证患者信息
    
    Args:
        patient_info: 患者信息字典
        
    Raises:
        HTTPException: 患者信息无效时抛出异常
    """
    required_fields = ["birth_date"]
    
    for field in required_fields:
        if field not in patient_info:
            raise HTTPException(
                status_code=400,
                detail=f"患者信息缺少必需字段: {field}"
            )
    
    # 验证出生日期格式
    try:
        birth_date_str = patient_info["birth_date"]
        birth_date = datetime.fromisoformat(birth_date_str).date()
        validate_date_range(birth_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="出生日期格式无效，请使用YYYY-MM-DD格式"
        )
    
    # 验证出生时间格式（如果提供）
    if "birth_time" in patient_info and patient_info["birth_time"]:
        birth_time = patient_info["birth_time"]
        if not validate_time_format(birth_time):
            raise HTTPException(
                status_code=400,
                detail="出生时间格式无效，请使用HH:MM格式"
            )
    
    # 验证出生地点（如果提供）
    if "birth_location" in patient_info and patient_info["birth_location"]:
        location = patient_info["birth_location"]
        if not validate_location_format(location):
            raise HTTPException(
                status_code=400,
                detail="出生地点信息格式无效"
            )


def validate_location_format(location: Dict[str, Any]) -> bool:
    """
    验证地理位置格式
    
    Args:
        location: 地理位置字典
        
    Returns:
        是否为有效格式
    """
    if not isinstance(location, dict):
        return False
    
    # 检查必需字段
    if "latitude" not in location or "longitude" not in location:
        return False
    
    try:
        lat = float(location["latitude"])
        lng = float(location["longitude"])
        
        # 验证经纬度范围
        if not (-90 <= lat <= 90):
            return False
        if not (-180 <= lng <= 180):
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_symptoms(symptoms: list) -> None:
    """
    验证症状列表
    
    Args:
        symptoms: 症状列表
        
    Raises:
        HTTPException: 症状列表无效时抛出异常
    """
    if not isinstance(symptoms, list):
        raise HTTPException(
            status_code=400,
            detail="症状必须是列表格式"
        )
    
    if len(symptoms) == 0:
        raise HTTPException(
            status_code=400,
            detail="症状列表不能为空"
        )
    
    if len(symptoms) > 10:
        raise HTTPException(
            status_code=400,
            detail="症状数量不能超过10个"
        )
    
    for symptom in symptoms:
        if not isinstance(symptom, str) or len(symptom.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="每个症状必须是非空字符串"
            )
        
        if len(symptom) > 50:
            raise HTTPException(
                status_code=400,
                detail="单个症状描述不能超过50个字符"
            )


def validate_ganzhi(ganzhi: str) -> bool:
    """
    验证干支格式
    
    Args:
        ganzhi: 干支字符串
        
    Returns:
        是否为有效干支
    """
    if not isinstance(ganzhi, str) or len(ganzhi) != 2:
        return False
    
    tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    return ganzhi[0] in tiangan and ganzhi[1] in dizhi


def validate_treatment_type(treatment_type: str) -> None:
    """
    验证治疗类型
    
    Args:
        treatment_type: 治疗类型
        
    Raises:
        HTTPException: 治疗类型无效时抛出异常
    """
    valid_types = [
        "针灸", "推拿", "中药", "食疗", "运动", "气功", 
        "综合治疗", "预防保健", "康复理疗"
    ]
    
    if treatment_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"治疗类型必须是以下之一: {', '.join(valid_types)}"
        )


def validate_condition(condition: str) -> None:
    """
    验证病症名称
    
    Args:
        condition: 病症名称
        
    Raises:
        HTTPException: 病症名称无效时抛出异常
    """
    if not isinstance(condition, str) or len(condition.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="病症名称不能为空"
        )
    
    if len(condition) > 100:
        raise HTTPException(
            status_code=400,
            detail="病症名称不能超过100个字符"
        )
    
    # 检查是否包含特殊字符
    invalid_chars = ['<', '>', '&', '"', "'", '\\', '/', ';']
    if any(char in condition for char in invalid_chars):
        raise HTTPException(
            status_code=400,
            detail="病症名称不能包含特殊字符"
        ) 