"""
基础数据模型

定义所有模型的基类和通用字段
"""

from datetime import datetime
from typing import Any, Dict, Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict


class BaseModel(PydanticBaseModel):
    """基础模型类"""
    
    model_config = ConfigDict(
        # 允许使用枚举值
        use_enum_values=True,
        # 验证赋值
        validate_assignment=True,
        # 允许额外字段
        extra="forbid",
        # 序列化时排除None值
        exclude_none=True,
        # 使用字符串表示日期时间
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class CalculationBaseModel(BaseModel):
    """算诊基础模型"""
    
    # 身份标识
    id: UUID = Field(
        default_factory=uuid4,
        description="唯一标识符"
    )
    
    # 时间戳
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="更新时间"
    )
    
    # 元数据
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="元数据"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="标签"
    )
    
    # 算诊相关字段
    patient_id: Optional[str] = Field(
        default=None,
        description="患者ID"
    )
    analysis_type: str = Field(
        description="分析类型"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="置信度分数"
    )
    notes: Optional[str] = Field(
        default=None,
        description="备注"
    ) 