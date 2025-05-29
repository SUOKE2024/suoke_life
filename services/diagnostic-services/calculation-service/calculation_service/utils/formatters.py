"""
格式化工具

用于格式化干支、五行等中医术语的显示
"""

from typing import Dict, List, Any


def format_ganzhi(tiangan: str, dizhi: str) -> str:
    """
    格式化干支
    
    Args:
        tiangan: 天干
        dizhi: 地支
        
    Returns:
        格式化的干支字符串
    """
    return f"{tiangan}{dizhi}"


def format_wuxing(wuxing_data: Dict[str, Any]) -> str:
    """
    格式化五行分布
    
    Args:
        wuxing_data: 五行数据
        
    Returns:
        格式化的五行字符串
    """
    if not isinstance(wuxing_data, dict):
        return str(wuxing_data)
    
    elements = []
    for element in ["wood", "fire", "earth", "metal", "water"]:
        if element in wuxing_data:
            count = wuxing_data[element]
            element_name = {
                "wood": "木",
                "fire": "火", 
                "earth": "土",
                "metal": "金",
                "water": "水"
            }[element]
            elements.append(f"{element_name}{count}")
    
    return " ".join(elements) 