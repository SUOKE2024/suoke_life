"""
历法数据模型

定义农历、阳历和天文数据的数据结构
"""

from datetime import date, datetime
from typing import Optional, Dict, Any

from pydantic import Field

from .base import BaseModel


class LunarDateModel(BaseModel):
    """农历日期模型"""
    
    year: int = Field(description="农历年")
    month: int = Field(description="农历月", ge=1, le=12)
    day: int = Field(description="农历日", ge=1, le=30)
    is_leap: bool = Field(default=False, description="是否闰月")
    ganzhi_year: str = Field(description="年份干支")
    ganzhi_month: str = Field(description="月份干支")
    ganzhi_day: str = Field(description="日期干支")
    zodiac: str = Field(description="生肖")


class SolarDateModel(BaseModel):
    """阳历日期模型"""
    
    year: int = Field(description="阳历年")
    month: int = Field(description="阳历月", ge=1, le=12)
    day: int = Field(description="阳历日", ge=1, le=31)
    solar_term: Optional[str] = Field(default=None, description="节气")
    season: str = Field(description="季节")


class AstronomicalDataModel(BaseModel):
    """天文数据模型"""
    
    target_date: date = Field(description="目标日期")
    sunrise: Optional[str] = Field(default=None, description="日出时间")
    sunset: Optional[str] = Field(default=None, description="日落时间")
    moon_phase: Optional[str] = Field(default=None, description="月相")
    constellation: Optional[str] = Field(default=None, description="星座")
    planetary_positions: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="行星位置"
    ) 