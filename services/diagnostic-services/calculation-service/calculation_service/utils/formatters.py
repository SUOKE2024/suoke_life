"""
数据格式化工具

提供各种数据格式化功能
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


def format_analysis_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化分析结果
    
    Args:
        result: 原始分析结果
        
    Returns:
        格式化后的结果
    """
    # 处理新格式的综合分析结果
    if "analysis_metadata" in result and "individual_analyses" in result:
        metadata = result["analysis_metadata"]
        individual_analyses = result["individual_analyses"]
        birth_info = result.get("birth_info", {})
        recommendations = result.get("recommendations", {})
        
        formatted_result = {
            "分析概要": {
                "分析时间": metadata.get("analysis_date", ""),
                "个人信息": birth_info,
                "分析类型": metadata.get("included_analyses", [])
            },
            "详细分析": {},
            "综合建议": recommendations,
            "调养重点": recommendations.get("lifestyle_adjustments", []),
            "注意事项": recommendations.get("monitoring_advice", [])
        }
        
        # 格式化各项分析结果
        if "ziwu" in individual_analyses and "error" not in individual_analyses["ziwu"]:
            formatted_result["详细分析"]["子午流注"] = _format_ziwu_result(individual_analyses["ziwu"])
        
        if "constitution" in individual_analyses and "error" not in individual_analyses["constitution"]:
            formatted_result["详细分析"]["体质分析"] = _format_constitution_result(individual_analyses["constitution"])
        
        if "bagua" in individual_analyses and "error" not in individual_analyses["bagua"]:
            formatted_result["详细分析"]["八卦分析"] = _format_bagua_result(individual_analyses["bagua"])
        
        if "wuyun_liuqi" in individual_analyses and "error" not in individual_analyses["wuyun_liuqi"]:
            formatted_result["详细分析"]["运气分析"] = _format_wuyun_result(individual_analyses["wuyun_liuqi"])
        
        return formatted_result
    
    # 处理旧格式的结果（向后兼容）
    formatted_result = {
        "分析概要": {
            "分析时间": result.get("分析时间", ""),
            "个人信息": result.get("个人信息", {}),
            "分析类型": _extract_analysis_types(result)
        },
        "详细分析": {},
        "综合建议": result.get("综合建议", {}),
        "调养重点": result.get("调养重点", []),
        "注意事项": result.get("注意事项", [])
    }
    
    # 格式化各项分析结果
    if "子午流注分析" in result:
        formatted_result["详细分析"]["子午流注"] = _format_ziwu_result(result["子午流注分析"])
    
    if "体质分析" in result:
        formatted_result["详细分析"]["体质分析"] = _format_constitution_result(result["体质分析"])
    
    if "八卦分析" in result:
        formatted_result["详细分析"]["八卦分析"] = _format_bagua_result(result["八卦分析"])
    
    if "运气分析" in result:
        formatted_result["详细分析"]["运气分析"] = _format_wuyun_result(result["运气分析"])
    
    return formatted_result


def format_health_advice(advice: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化健康建议
    
    Args:
        advice: 原始健康建议
        
    Returns:
        格式化后的建议
    """
    return {
        "日常调养": {
            "饮食建议": advice.get("饮食调养", []),
            "起居建议": advice.get("起居调养", []),
            "运动建议": advice.get("运动调养", []),
            "情志建议": advice.get("情志调养", [])
        },
        "预防措施": advice.get("预防措施", []),
        "最佳时机": advice.get("最佳调理时间", []),
        "注意事项": advice.get("注意事项", [])
    }


def format_time_display(dt: datetime) -> str:
    """
    格式化时间显示
    
    Args:
        dt: 日期时间对象
        
    Returns:
        格式化的时间字符串
    """
    return dt.strftime("%Y年%m月%d日 %H:%M")


def format_date_display(dt: datetime) -> str:
    """
    格式化日期显示
    
    Args:
        dt: 日期时间对象
        
    Returns:
        格式化的日期字符串
    """
    return dt.strftime("%Y年%m月%d日")


def format_birth_info_display(birth_info: Dict[str, Any]) -> str:
    """
    格式化出生信息显示
    
    Args:
        birth_info: 出生信息
        
    Returns:
        格式化的出生信息字符串
    """
    year = birth_info.get("year", "")
    month = birth_info.get("month", "")
    day = birth_info.get("day", "")
    hour = birth_info.get("hour", "")
    gender = birth_info.get("gender", "")
    
    return f"{year}年{month}月{day}日{hour}时 {gender}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    格式化百分比显示
    
    Args:
        value: 数值（0-1之间）
        decimal_places: 小数位数
        
    Returns:
        格式化的百分比字符串
    """
    return f"{value * 100:.{decimal_places}f}%"


def format_score_display(score: float, max_score: float = 100) -> str:
    """
    格式化分数显示
    
    Args:
        score: 分数
        max_score: 最大分数
        
    Returns:
        格式化的分数字符串
    """
    return f"{score:.1f}/{max_score}"


def _extract_analysis_types(result: Dict[str, Any]) -> List[str]:
    """提取分析类型"""
    types = []
    
    if "子午流注分析" in result:
        types.append("子午流注")
    if "体质分析" in result:
        types.append("体质分析")
    if "八卦分析" in result:
        types.append("八卦分析")
    if "运气分析" in result:
        types.append("运气分析")
    
    return types


def _format_ziwu_result(ziwu_result: Dict[str, Any]) -> Dict[str, Any]:
    """格式化子午流注结果"""
    return {
        "当前状态": {
            "时辰": ziwu_result.get("当前时辰", ""),
            "经络": ziwu_result.get("当前经络", ""),
            "特点": ziwu_result.get("经络特点", "")
        },
        "最佳时机": ziwu_result.get("最佳治疗时间", []),
        "调养建议": ziwu_result.get("调养建议", {}),
        "注意事项": ziwu_result.get("注意事项", [])
    }


def _format_constitution_result(constitution_result: Dict[str, Any]) -> Dict[str, Any]:
    """格式化体质分析结果"""
    return {
        "八字信息": constitution_result.get("八字信息", {}),
        "体质特征": {
            "主要体质": constitution_result.get("体质类型", ""),
            "五行特点": constitution_result.get("五行强弱", {}),
            "体质特征": constitution_result.get("体质特征", {})
        },
        "调理方案": constitution_result.get("调理建议", {}),
        "养生要点": constitution_result.get("养生要点", [])
    }


def _format_bagua_result(bagua_result: Dict[str, Any]) -> Dict[str, Any]:
    """格式化八卦分析结果"""
    return {
        "本命卦象": {
            "卦名": bagua_result.get("本命卦", ""),
            "卦象特点": bagua_result.get("卦象特点", {}),
            "五行属性": bagua_result.get("五行属性", "")
        },
        "健康分析": bagua_result.get("健康分析", {}),
        "方位指导": bagua_result.get("方位指导", {}),
        "调理建议": bagua_result.get("调理建议", {})
    }


def _format_wuyun_result(wuyun_result: Dict[str, Any]) -> Dict[str, Any]:
    """格式化五运六气结果"""
    return {
        "运气概况": {
            "年运": wuyun_result.get("五运分析", {}),
            "司天在泉": wuyun_result.get("司天在泉", {}),
            "当前气": wuyun_result.get("当前气分析", {})
        },
        "疾病预测": wuyun_result.get("疾病预测", {}),
        "调养指导": wuyun_result.get("调养建议", {}),
        "总体特点": wuyun_result.get("总体特点", "")
    } 