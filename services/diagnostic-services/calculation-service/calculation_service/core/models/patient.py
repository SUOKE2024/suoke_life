"""
患者信息数据模型

定义患者基本信息和出生信息的数据结构
"""

from datetime import date, time
from enum import Enum
from typing import Optional

from pydantic import Field, validator

from .base import BaseModel


class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class LocationModel(BaseModel):
    """地理位置模型"""
    
    latitude: float = Field(
        description="纬度",
        ge=-90.0,
        le=90.0
    )
    longitude: float = Field(
        description="经度", 
        ge=-180.0,
        le=180.0
    )
    timezone: str = Field(
        default="Asia/Shanghai",
        description="时区"
    )
    city: Optional[str] = Field(
        default=None,
        description="城市"
    )
    province: Optional[str] = Field(
        default=None,
        description="省份"
    )
    country: str = Field(
        default="中国",
        description="国家"
    )


class BirthInfoModel(BaseModel):
    """出生信息模型"""
    
    birth_date: date = Field(
        description="出生日期"
    )
    birth_time: Optional[time] = Field(
        default=None,
        description="出生时间"
    )
    birth_location: Optional[LocationModel] = Field(
        default=None,
        description="出生地点"
    )
    lunar_birth_date: Optional[str] = Field(
        default=None,
        description="农历出生日期"
    )
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        """验证出生日期"""
        from datetime import date
        if v > date.today():
            raise ValueError("出生日期不能晚于今天")
        return v


class PatientInfoModel(BaseModel):
    """患者信息模型"""
    
    patient_id: str = Field(
        description="患者ID"
    )
    name: Optional[str] = Field(
        default=None,
        description="姓名"
    )
    gender: Optional[Gender] = Field(
        default=None,
        description="性别"
    )
    birth_info: BirthInfoModel = Field(
        description="出生信息"
    )
    current_symptoms: Optional[list[str]] = Field(
        default=None,
        description="当前症状"
    )
    medical_history: Optional[list[str]] = Field(
        default=None,
        description="病史"
    )
    constitution_type: Optional[str] = Field(
        default=None,
        description="体质类型"
    )


class BaziModel(BaseModel):
    """八字模型"""
    
    year_ganzhi: str = Field(
        description="年柱干支"
    )
    month_ganzhi: str = Field(
        description="月柱干支"
    )
    day_ganzhi: str = Field(
        description="日柱干支"
    )
    hour_ganzhi: str = Field(
        description="时柱干支"
    )
    
    @validator('year_ganzhi', 'month_ganzhi', 'day_ganzhi', 'hour_ganzhi')
    def validate_ganzhi(cls, v):
        """验证干支格式"""
        if len(v) != 2:
            raise ValueError("干支必须是两个字符")
        return v


class WuxingModel(BaseModel):
    """五行模型"""
    
    wood: int = Field(
        default=0,
        ge=0,
        description="木"
    )
    fire: int = Field(
        default=0,
        ge=0,
        description="火"
    )
    earth: int = Field(
        default=0,
        ge=0,
        description="土"
    )
    metal: int = Field(
        default=0,
        ge=0,
        description="金"
    )
    water: int = Field(
        default=0,
        ge=0,
        description="水"
    )
    
    @property
    def total(self) -> int:
        """五行总数"""
        return self.wood + self.fire + self.earth + self.metal + self.water
    
    @property
    def dominant_element(self) -> str:
        """主导元素"""
        elements = {
            "木": self.wood,
            "火": self.fire,
            "土": self.earth,
            "金": self.metal,
            "水": self.water
        }
        return max(elements, key=elements.get)
    
    @property
    def weakest_element(self) -> str:
        """最弱元素"""
        elements = {
            "木": self.wood,
            "火": self.fire,
            "土": self.earth,
            "金": self.metal,
            "水": self.water
        }
        return min(elements, key=elements.get) 