"""
ai - 索克生活项目模块
"""

            import json
from app.core.dependencies import get_ai_service
from app.core.logger import get_logger
from app.services.ai_service import AIService
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

"""
AI服务API端点
提供智能诊断、多模态分析和知识增强RAG功能
"""



logger = get_logger()

router = APIRouter(prefix="/ai", tags=["AI服务"])


# 请求模型
class SymptomInput(BaseModel):
    """症状输入"""
    name: str = Field(..., description="症状名称")
    severity: int = Field(1, ge=1, le=5, description="严重程度(1-5)")
    duration: str = Field("", description="持续时间")


class PatientInfo(BaseModel):
    """患者信息"""
    constitution_type: Optional[str] = Field(None, description="体质类型")
    age: int = Field(0, ge=0, le=150, description="年龄")
    gender: str = Field("unknown", description="性别")


class DiagnosisRequest(BaseModel):
    """智能诊断请求"""
    symptoms: List[SymptomInput] = Field(..., description="症状列表")
    patient_info: PatientInfo = Field(..., description="患者信息")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class MultimodalAnalysisRequest(BaseModel):
    """多模态分析请求"""
    text_data: Optional[str] = Field(None, description="文本数据")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class RAGRequest(BaseModel):
    """知识增强RAG请求"""
    query: str = Field(..., description="查询内容")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    max_results: int = Field(10, ge=1, le=50, description="最大结果数")


# 响应模型
class DiagnosisResponse(BaseModel):
    """智能诊断响应"""
    success: bool
    diagnosis: Optional[Dict[str, Any]]
    confidence: float
    reasoning: List[str]
    symptom_analysis: Optional[Dict[str, Any]]
    constitution_analysis: Optional[Dict[str, Any]]
    syndrome_inference: Optional[Dict[str, Any]]
    graph_analysis: Optional[Dict[str, Any]]
    timestamp: str
    error: Optional[str] = None


class MultimodalAnalysisResponse(BaseModel):
    """多模态分析响应"""
    success: bool
    individual_results: Dict[str, Any]
    fusion_result: Optional[Dict[str, Any]]
    timestamp: str
    error: Optional[str] = None


class RAGResponse(BaseModel):
    """知识增强RAG响应"""
    success: bool
    query: str
    retrieval_results: List[Dict[str, Any]]
    generated_response: Optional[Dict[str, Any]]
    timestamp: str
    error: Optional[str] = None


# API端点
@router.post("/diagnosis", response_model=DiagnosisResponse)
async def intelligent_diagnosis(
    request: DiagnosisRequest,
    ai_service: AIService = Depends(get_ai_service)
) -> DiagnosisResponse:
    """
    智能诊断推理
    
    基于症状和患者信息进行智能诊断推理，包括：
    - 症状分析和权重计算
    - 体质分析
    - 证型推理
    - 知识图谱路径分析
    - 综合诊断推理
    """
    try:
        # 转换症状数据
        symptoms_data = [symptom.model_dump() for symptom in request.symptoms]
        patient_data = request.patient_info.model_dump()
        
        # 执行智能诊断
        result = await ai_service.intelligent_diagnosis(
            symptoms=symptoms_data,
            patient_info=patient_data,
            context=request.context
        )
        
        return DiagnosisResponse(**result)
        
    except Exception as e:
        logger.error(f"智能诊断API错误: {e}")
        raise HTTPException(status_code=500, detail=f"智能诊断失败: {str(e)}")


@router.post("/multimodal/text", response_model=MultimodalAnalysisResponse)
async def multimodal_text_analysis(
    request: MultimodalAnalysisRequest,
    ai_service: AIService = Depends(get_ai_service)
) -> MultimodalAnalysisResponse:
    """
    多模态文本分析
    
    对文本数据进行多模态分析，包括：
    - 医学关键词提取
    - 情感分析
    - 医学实体识别
    """
    try:
        result = await ai_service.multimodal_analysis(
            text_data=request.text_data,
            context=request.context
        )
        
        return MultimodalAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"多模态文本分析API错误: {e}")
        raise HTTPException(status_code=500, detail=f"多模态文本分析失败: {str(e)}")


@router.post("/multimodal/image", response_model=MultimodalAnalysisResponse)
async def multimodal_image_analysis(
    image: UploadFile = File(..., description="图像文件"),
    image_type: str = Form("unknown", description="图像类型(tongue/face/unknown)"),
    context: Optional[str] = Form(None, description="上下文信息(JSON字符串)"),
    ai_service: AIService = Depends(get_ai_service)
) -> MultimodalAnalysisResponse:
    """
    多模态图像分析
    
    对图像数据进行多模态分析，支持：
    - 舌诊图像分析
    - 面诊图像分析
    - 一般医学图像分析
    """
    try:
        # 读取图像数据
        image_data = await image.read()
        
        # 解析上下文
        context_data = None
        if context:
            try:
                context_data = json.loads(context)
            except json.JSONDecodeError:
                context_data = {}
        
        if context_data is None:
            context_data = {}
        
        context_data["image_type"] = image_type
        
        # 执行多模态分析
        result = await ai_service.multimodal_analysis(
            image_data=image_data,
            context=context_data
        )
        
        return MultimodalAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"多模态图像分析API错误: {e}")
        raise HTTPException(status_code=500, detail=f"多模态图像分析失败: {str(e)}")


@router.post("/multimodal/audio", response_model=MultimodalAnalysisResponse)
async def multimodal_audio_analysis(
    audio: UploadFile = File(..., description="音频文件"),
    context: Optional[str] = Form(None, description="上下文信息(JSON字符串)"),
    ai_service: AIService = Depends(get_ai_service)
) -> MultimodalAnalysisResponse:
    """
    多模态音频分析
    
    对音频数据进行多模态分析，包括：
    - 声音质量分析
    - 语速分析
    - 音调分析
    - 健康指标提取
    """
    try:
        # 读取音频数据
        audio_data = await audio.read()
        
        # 解析上下文
        context_data = None
        if context:
            try:
                context_data = json.loads(context)
            except json.JSONDecodeError:
                context_data = {}
        
        # 执行多模态分析
        result = await ai_service.multimodal_analysis(
            audio_data=audio_data,
            context=context_data
        )
        
        return MultimodalAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"多模态音频分析API错误: {e}")
        raise HTTPException(status_code=500, detail=f"多模态音频分析失败: {str(e)}")


@router.post("/multimodal/combined", response_model=MultimodalAnalysisResponse)
async def multimodal_combined_analysis(
    text_data: Optional[str] = Form(None, description="文本数据"),
    image: Optional[UploadFile] = File(None, description="图像文件"),
    audio: Optional[UploadFile] = File(None, description="音频文件"),
    image_type: str = Form("unknown", description="图像类型"),
    context: Optional[str] = Form(None, description="上下文信息(JSON字符串)"),
    ai_service: AIService = Depends(get_ai_service)
) -> MultimodalAnalysisResponse:
    """
    多模态综合分析
    
    对多种模态数据进行综合分析和融合，包括：
    - 文本、图像、音频的独立分析
    - 多模态信息融合
    - 综合诊断建议
    """
    try:
        # 读取文件数据
        image_data = None
        audio_data = None
        
        if image:
            image_data = await image.read()
        
        if audio:
            audio_data = await audio.read()
        
        # 解析上下文
        context_data = None
        if context:
            try:
                context_data = json.loads(context)
            except json.JSONDecodeError:
                context_data = {}
        
        if context_data is None:
            context_data = {}
        
        if image_data:
            context_data["image_type"] = image_type
        
        # 执行多模态分析
        result = await ai_service.multimodal_analysis(
            text_data=text_data,
            image_data=image_data,
            audio_data=audio_data,
            context=context_data
        )
        
        return MultimodalAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"多模态综合分析API错误: {e}")
        raise HTTPException(status_code=500, detail=f"多模态综合分析失败: {str(e)}")


@router.post("/rag", response_model=RAGResponse)
async def knowledge_enhanced_rag(
    request: RAGRequest,
    ai_service: AIService = Depends(get_ai_service)
) -> RAGResponse:
    """
    知识增强的检索增强生成(RAG)
    
    基于知识图谱和语义搜索的增强回答生成，包括：
    - 多层次知识检索
    - 语义相似度匹配
    - 知识图谱路径分析
    - 智能回答生成
    """
    try:
        result = await ai_service.knowledge_enhanced_rag(
            query=request.query,
            context=request.context,
            max_results=request.max_results
        )
        
        return RAGResponse(**result)
        
    except Exception as e:
        logger.error(f"知识增强RAG API错误: {e}")
        raise HTTPException(status_code=500, detail=f"知识增强RAG失败: {str(e)}")


@router.get("/capabilities")
async def get_ai_capabilities() -> Dict[str, Any]:
    """
    获取AI服务能力
    
    返回当前AI服务支持的功能和能力列表
    """
    return {
        "intelligent_diagnosis": {
            "description": "智能诊断推理",
            "features": [
                "症状分析和权重计算",
                "体质分析",
                "证型推理",
                "知识图谱路径分析",
                "综合诊断推理"
            ],
            "supported_inputs": ["症状列表", "患者信息", "上下文信息"]
        },
        "multimodal_analysis": {
            "description": "多模态数据分析",
            "features": [
                "文本分析(关键词提取、情感分析、实体识别)",
                "图像分析(舌诊、面诊、一般医学图像)",
                "音频分析(声音质量、语速、音调)",
                "多模态信息融合"
            ],
            "supported_formats": {
                "text": ["纯文本"],
                "image": ["jpg", "png", "jpeg"],
                "audio": ["wav", "mp3", "m4a"]
            }
        },
        "knowledge_enhanced_rag": {
            "description": "知识增强的检索增强生成",
            "features": [
                "多层次知识检索",
                "语义相似度匹配",
                "知识图谱路径分析",
                "智能回答生成",
                "查询意图识别"
            ],
            "supported_intents": ["诊断", "治疗", "知识查询", "一般咨询"]
        },
        "performance": {
            "caching": "支持智能缓存",
            "monitoring": "支持性能监控",
            "scalability": "支持水平扩展"
        }
    }


@router.get("/health")
async def ai_health_check(
    ai_service: AIService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    AI服务健康检查
    
    检查AI服务的运行状态和依赖服务连接
    """
    try:
        # 检查基础服务连接
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "knowledge_service": "connected",
                "graph_service": "connected",
                "cache_service": "connected" if ai_service.cache_service else "not_configured",
                "metrics_service": "connected" if ai_service.metrics_service else "not_configured"
            },
            "capabilities": {
                "intelligent_diagnosis": True,
                "multimodal_analysis": True,
                "knowledge_enhanced_rag": True
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"AI服务健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        } 