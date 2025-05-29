import base64
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

# 导入服务层组件
from internal.lifecycle.emotional_analyzer.emotional_service import EmotionalService

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/emotion",
    tags=["情绪分析"],
    responses={404: {"description": "未找到"}},
)

# 请求和响应模型
class EmotionalInput(BaseModel):
    input_type: str  # "text", "voice", "physiological"
    data: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class EmotionalAnalysisRequest(BaseModel):
    user_id: str
    inputs: list[EmotionalInput]
    analysis_context: str | None = None

class HealthImpact(BaseModel):
    affected_systems: list[str]
    tcm_interpretation: str
    severity: float  # 0.0-1.0

class Suggestion(BaseModel):
    intervention_type: str
    description: str
    estimated_effectiveness: float  # 0.0-1.0
    is_urgent: bool = False

class EmotionalAnalysisResponse(BaseModel):
    emotion_scores: dict[str, float]
    primary_emotion: str
    emotional_tendency: str
    health_impact: HealthImpact
    suggestions: list[Suggestion]

# 情绪分析服务实例
emotional_service = EmotionalService()

@router.post("/analyze", response_model=EmotionalAnalysisResponse)
async def analyze_emotional_state(request: EmotionalAnalysisRequest):
    """
    分析情绪状态
    """
    try:
        # 转换输入格式
        inputs = []
        for input_item in request.inputs:
            # 处理Base64编码的数据
            data = input_item.data
            if input_item.input_type in ["voice", "physiological"] and data:
                # 如果是二进制数据格式，解码Base64
                try:
                    data = base64.b64decode(data)
                except Exception as e:
                    logger.warning(f"Base64解码失败: {str(e)}")

            # 创建格式化的输入
            formatted_input = {
                "input_type": input_item.input_type,
                "data": data or "",
                "metadata": input_item.metadata
            }
            inputs.append(formatted_input)

        # 调用情绪分析服务
        result = await emotional_service.analyze_emotional_state(
            request.user_id,
            inputs,
            request.analysis_context
        )

        # 转换健康影响数据
        health_impact = HealthImpact(
            affected_systems=result["health_impact"]["affected_systems"],
            tcm_interpretation=result["health_impact"]["tcm_interpretation"],
            severity=result["health_impact"]["severity"]
        )

        # 转换建议数据
        suggestions = []
        for suggestion_data in result["suggestions"]:
            suggestion = Suggestion(
                intervention_type=suggestion_data["intervention_type"],
                description=suggestion_data["description"],
                estimated_effectiveness=suggestion_data["estimated_effectiveness"],
                is_urgent=suggestion_data.get("is_urgent", False)
            )
            suggestions.append(suggestion)

        # 组装响应
        response = EmotionalAnalysisResponse(
            emotion_scores=result["emotion_scores"],
            primary_emotion=result["primary_emotion"],
            emotional_tendency=result["emotional_tendency"],
            health_impact=health_impact,
            suggestions=suggestions
        )

        return response
    except Exception as e:
        logger.error(f"情绪分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"情绪分析失败: {str(e)}"
        )

@router.post("/analyze/text")
async def analyze_text_emotion(
    user_id: str = Form(...),
    text: str = Form(...),
    context: str | None = Form(None)
):
    """
    分析文本情绪
    """
    try:
        # 创建情绪分析请求
        request = EmotionalAnalysisRequest(
            user_id=user_id,
            inputs=[
                EmotionalInput(
                    input_type="text",
                    data=text,
                    metadata={"timestamp": datetime.now().isoformat()}
                )
            ],
            analysis_context=context
        )

        # 调用情绪分析通用接口
        return await analyze_emotional_state(request)
    except Exception as e:
        logger.error(f"文本情绪分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文本情绪分析失败: {str(e)}"
        )

@router.post("/analyze/voice")
async def analyze_voice_emotion(
    user_id: str = Form(...),
    audio_file: UploadFile = File(...),
    context: str | None = Form(None)
):
    """
    分析语音情绪
    """
    try:
        # 读取音频文件内容
        audio_data = await audio_file.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        # 创建情绪分析请求
        request = EmotionalAnalysisRequest(
            user_id=user_id,
            inputs=[
                EmotionalInput(
                    input_type="voice",
                    data=audio_base64,
                    metadata={
                        "filename": audio_file.filename,
                        "content_type": audio_file.content_type,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            ],
            analysis_context=context
        )

        # 调用情绪分析通用接口
        return await analyze_emotional_state(request)
    except Exception as e:
        logger.error(f"语音情绪分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音情绪分析失败: {str(e)}"
        )

@router.get("/mappings/tcm")
async def get_tcm_emotion_mappings():
    """
    获取中医情志理论映射
    """
    try:
        return emotional_service.tcm_emotion_mappings
    except Exception as e:
        logger.error(f"获取中医情志映射失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取中医情志映射失败: {str(e)}"
        )

@router.get("/interventions")
async def get_intervention_strategies(emotion: str | None = None):
    """
    获取情绪干预策略
    """
    try:
        strategies = emotional_service.intervention_strategies

        # 如果指定了情绪类型，只返回相关策略
        if emotion:
            if emotion in strategies:
                return {emotion: strategies[emotion]}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"未找到'{emotion}'情绪的干预策略"
                )

        return strategies
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取干预策略失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取干预策略失败: {str(e)}"
        )
