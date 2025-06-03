"""
智能诊断助手API
提供中医辨证论治的高级功能
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.rest.deps import (
    get_knowledge_service,
    get_cache_service,
    get_metrics_service,
    optional_auth,
)
from app.core.logger import get_logger
from app.services.knowledge_service import KnowledgeService
from app.services.cache_service import CacheService
from app.services.metrics_service import MetricsService

logger = get_logger()
router = APIRouter(prefix="/diagnosis", tags=["智能诊断"])


class SymptomInput(BaseModel):
    """症状输入模型"""
    name: str = Field(..., description="症状名称")
    severity: int = Field(1, ge=1, le=5, description="严重程度(1-5)")
    duration: Optional[str] = Field(None, description="持续时间")
    description: Optional[str] = Field(None, description="详细描述")


class PatientProfile(BaseModel):
    """患者档案模型"""
    age: int = Field(..., ge=0, le=150, description="年龄")
    gender: str = Field(..., regex="^(male|female)$", description="性别")
    constitution_type: Optional[str] = Field(None, description="体质类型")
    symptoms: List[SymptomInput] = Field(..., description="症状列表")
    medical_history: Optional[List[str]] = Field(None, description="病史")
    lifestyle: Optional[Dict[str, Any]] = Field(None, description="生活方式")


class DiagnosisResult(BaseModel):
    """诊断结果模型"""
    syndrome_candidates: List[Dict[str, Any]] = Field(..., description="证型候选")
    constitution_analysis: Dict[str, Any] = Field(..., description="体质分析")
    treatment_suggestions: List[Dict[str, Any]] = Field(..., description="治疗建议")
    lifestyle_recommendations: List[Dict[str, Any]] = Field(..., description="生活方式建议")
    confidence_score: float = Field(..., ge=0, le=1, description="置信度")
    reasoning_path: List[str] = Field(..., description="推理路径")


class TreatmentPlan(BaseModel):
    """治疗方案模型"""
    plan_id: str = Field(..., description="方案ID")
    syndrome_id: str = Field(..., description="证型ID")
    herbs: List[Dict[str, Any]] = Field(..., description="中药配方")
    acupoints: List[Dict[str, Any]] = Field(..., description="穴位处方")
    lifestyle_interventions: List[Dict[str, Any]] = Field(..., description="生活干预")
    duration: str = Field(..., description="治疗周期")
    precautions: List[str] = Field(..., description="注意事项")


@router.post("/analyze", response_model=DiagnosisResult)
async def analyze_symptoms(
    patient_profile: PatientProfile,
    include_reasoning: bool = Query(True, description="是否包含推理过程"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    cache_service: CacheService = Depends(get_cache_service),
    metrics_service: MetricsService = Depends(get_metrics_service),
    current_user: Optional[Dict] = Depends(optional_auth),
):
    """
    智能症状分析和辨证
    
    基于患者症状和体质信息，进行中医辨证分析
    """
    try:
        # 记录请求指标
        if metrics_service:
            metrics_service.record_knowledge_request("diagnosis", "analyze_symptoms")
        
        # 生成缓存键
        cache_key = f"diagnosis:analyze:{hash(str(patient_profile.dict()))}"
        
        # 尝试从缓存获取
        if cache_service:
            cached_result = await cache_service.get(cache_key, DiagnosisResult)
            if cached_result:
                logger.info("从缓存返回诊断结果")
                return cached_result
        
        # 执行症状分析
        diagnosis_result = await _perform_symptom_analysis(
            patient_profile, include_reasoning, knowledge_service
        )
        
        # 缓存结果
        if cache_service:
            await cache_service.set(cache_key, diagnosis_result, ttl=1800)  # 30分钟
        
        logger.info(f"完成症状分析，置信度: {diagnosis_result.confidence_score}")
        return diagnosis_result
        
    except Exception as e:
        logger.error(f"症状分析失败: {e}")
        if metrics_service:
            metrics_service.record_knowledge_request("diagnosis", "analyze_symptoms_error")
        raise HTTPException(status_code=500, detail="症状分析失败")


@router.post("/treatment-plan", response_model=TreatmentPlan)
async def generate_treatment_plan(
    syndrome_id: str,
    patient_profile: PatientProfile,
    treatment_type: str = Query("comprehensive", regex="^(herbs|acupuncture|lifestyle|comprehensive)$"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    cache_service: CacheService = Depends(get_cache_service),
    metrics_service: MetricsService = Depends(get_metrics_service),
    current_user: Optional[Dict] = Depends(optional_auth),
):
    """
    生成个性化治疗方案
    
    基于辨证结果和患者特征，生成个性化的中医治疗方案
    """
    try:
        # 记录请求指标
        if metrics_service:
            metrics_service.record_knowledge_request("diagnosis", "generate_treatment_plan")
        
        # 验证证型存在
        syndrome = await knowledge_service.get_syndrome_by_id(syndrome_id)
        if not syndrome:
            raise HTTPException(status_code=404, detail="证型不存在")
        
        # 生成缓存键
        cache_key = f"treatment:plan:{syndrome_id}:{treatment_type}:{hash(str(patient_profile.dict()))}"
        
        # 尝试从缓存获取
        if cache_service:
            cached_plan = await cache_service.get(cache_key, TreatmentPlan)
            if cached_plan:
                logger.info("从缓存返回治疗方案")
                return cached_plan
        
        # 生成治疗方案
        treatment_plan = await _generate_personalized_treatment_plan(
            syndrome, patient_profile, treatment_type, knowledge_service
        )
        
        # 缓存结果
        if cache_service:
            await cache_service.set(cache_key, treatment_plan, ttl=3600)  # 1小时
        
        logger.info(f"生成治疗方案: {treatment_plan.plan_id}")
        return treatment_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成治疗方案失败: {e}")
        if metrics_service:
            metrics_service.record_knowledge_request("diagnosis", "generate_treatment_plan_error")
        raise HTTPException(status_code=500, detail="生成治疗方案失败")


@router.get("/syndrome-patterns/{syndrome_id}")
async def get_syndrome_patterns(
    syndrome_id: str,
    include_cases: bool = Query(False, description="是否包含病例"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    current_user: Optional[Dict] = Depends(optional_auth),
):
    """
    获取证型的典型模式和病例
    """
    try:
        syndrome = await knowledge_service.get_syndrome_by_id(syndrome_id)
        if not syndrome:
            raise HTTPException(status_code=404, detail="证型不存在")
        
        # 获取证型诊断路径
        pathways = await knowledge_service.get_syndrome_pathways(syndrome_id)
        
        result = {
            "syndrome": syndrome,
            "pathways": pathways,
            "typical_symptoms": await _get_typical_symptoms(syndrome_id, knowledge_service),
            "differential_diagnosis": await _get_differential_diagnosis(syndrome_id, knowledge_service),
        }
        
        if include_cases:
            result["clinical_cases"] = await _get_clinical_cases(syndrome_id, knowledge_service)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取证型模式失败: {e}")
        raise HTTPException(status_code=500, detail="获取证型模式失败")


@router.post("/constitution-assessment")
async def assess_constitution(
    symptoms: List[SymptomInput],
    lifestyle_data: Optional[Dict[str, Any]] = None,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    cache_service: CacheService = Depends(get_cache_service),
    current_user: Optional[Dict] = Depends(optional_auth),
):
    """
    体质评估
    
    基于症状和生活方式数据评估患者体质类型
    """
    try:
        # 生成缓存键
        cache_key = f"constitution:assess:{hash(str(symptoms) + str(lifestyle_data))}"
        
        # 尝试从缓存获取
        if cache_service:
            cached_result = await cache_service.get(cache_key)
            if cached_result:
                return cached_result
        
        # 执行体质评估
        assessment_result = await _perform_constitution_assessment(
            symptoms, lifestyle_data, knowledge_service
        )
        
        # 缓存结果
        if cache_service:
            await cache_service.set(cache_key, assessment_result, ttl=7200)  # 2小时
        
        return assessment_result
        
    except Exception as e:
        logger.error(f"体质评估失败: {e}")
        raise HTTPException(status_code=500, detail="体质评估失败")


# 辅助函数

async def _perform_symptom_analysis(
    patient_profile: PatientProfile,
    include_reasoning: bool,
    knowledge_service: KnowledgeService
) -> DiagnosisResult:
    """执行症状分析"""
    # 这里实现具体的症状分析逻辑
    # 包括症状匹配、证型推理、置信度计算等
    
    # 示例实现
    syndrome_candidates = []
    reasoning_path = []
    
    # 分析每个症状
    for symptom in patient_profile.symptoms:
        # 查找相关证型
        search_result = await knowledge_service.search_knowledge(
            query=symptom.name,
            entity_type="syndrome",
            limit=5,
            offset=0
        )
        
        for item in search_result.items:
            syndrome_candidates.append({
                "syndrome_id": item.id,
                "name": item.title,
                "relevance_score": item.score,
                "matching_symptoms": [symptom.name]
            })
        
        if include_reasoning:
            reasoning_path.append(f"症状 '{symptom.name}' 匹配到 {len(search_result.items)} 个相关证型")
    
    # 体质分析
    constitution_analysis = await _analyze_constitution(patient_profile, knowledge_service)
    
    # 生成治疗建议
    treatment_suggestions = await _generate_treatment_suggestions(
        syndrome_candidates, patient_profile, knowledge_service
    )
    
    # 生成生活方式建议
    lifestyle_recommendations = await _generate_lifestyle_recommendations(
        patient_profile, knowledge_service
    )
    
    # 计算置信度
    confidence_score = _calculate_confidence_score(syndrome_candidates, patient_profile)
    
    return DiagnosisResult(
        syndrome_candidates=syndrome_candidates[:5],  # 返回前5个候选
        constitution_analysis=constitution_analysis,
        treatment_suggestions=treatment_suggestions,
        lifestyle_recommendations=lifestyle_recommendations,
        confidence_score=confidence_score,
        reasoning_path=reasoning_path if include_reasoning else []
    )


async def _generate_personalized_treatment_plan(
    syndrome: Any,
    patient_profile: PatientProfile,
    treatment_type: str,
    knowledge_service: KnowledgeService
) -> TreatmentPlan:
    """生成个性化治疗方案"""
    import uuid
    
    plan_id = str(uuid.uuid4())
    
    # 根据治疗类型生成不同的方案
    herbs = []
    acupoints = []
    lifestyle_interventions = []
    
    if treatment_type in ["herbs", "comprehensive"]:
        # 获取相关中药
        herbs_result = await knowledge_service.search_knowledge(
            query=syndrome.name,
            entity_type="herb",
            limit=10,
            offset=0
        )
        herbs = [{"herb_id": item.id, "name": item.title, "dosage": "待医师确定"} 
                for item in herbs_result.items[:5]]
    
    if treatment_type in ["acupuncture", "comprehensive"]:
        # 获取相关穴位
        acupoints_result = await knowledge_service.search_knowledge(
            query=syndrome.name,
            entity_type="acupoint",
            limit=10,
            offset=0
        )
        acupoints = [{"acupoint_id": item.id, "name": item.title, "technique": "针刺"} 
                    for item in acupoints_result.items[:8]]
    
    if treatment_type in ["lifestyle", "comprehensive"]:
        # 获取生活方式干预
        if patient_profile.constitution_type:
            interventions_result = await knowledge_service.get_lifestyle_interventions_by_constitution(
                patient_profile.constitution_type, limit=5, offset=0
            )
            lifestyle_interventions = [
                {"intervention_id": item.id, "description": item.description}
                for item in interventions_result.items
            ]
    
    return TreatmentPlan(
        plan_id=plan_id,
        syndrome_id=syndrome.id,
        herbs=herbs,
        acupoints=acupoints,
        lifestyle_interventions=lifestyle_interventions,
        duration="4-6周",
        precautions=[
            "请在专业中医师指导下使用",
            "如有不适请及时就医",
            "定期复诊调整方案"
        ]
    )


async def _analyze_constitution(
    patient_profile: PatientProfile,
    knowledge_service: KnowledgeService
) -> Dict[str, Any]:
    """分析患者体质"""
    if patient_profile.constitution_type:
        constitution = await knowledge_service.get_constitution_by_id(
            patient_profile.constitution_type
        )
        if constitution:
            return {
                "primary_constitution": constitution.dict(),
                "confidence": 0.8,
                "characteristics": constitution.characteristics
            }
    
    # 基于症状推断体质
    return {
        "primary_constitution": None,
        "confidence": 0.0,
        "characteristics": [],
        "recommendation": "建议进行专业体质辨识"
    }


async def _generate_treatment_suggestions(
    syndrome_candidates: List[Dict[str, Any]],
    patient_profile: PatientProfile,
    knowledge_service: KnowledgeService
) -> List[Dict[str, Any]]:
    """生成治疗建议"""
    suggestions = []
    
    for candidate in syndrome_candidates[:3]:  # 取前3个候选证型
        # 获取治疗方案
        treatments = await knowledge_service.search_knowledge(
            query=f"治疗 {candidate['name']}",
            entity_type="treatment",
            limit=3,
            offset=0
        )
        
        for treatment in treatments.items:
            suggestions.append({
                "syndrome": candidate['name'],
                "treatment": treatment.title,
                "description": treatment.content[:200] + "..." if len(treatment.content) > 200 else treatment.content,
                "priority": "high" if candidate['relevance_score'] > 0.8 else "medium"
            })
    
    return suggestions


async def _generate_lifestyle_recommendations(
    patient_profile: PatientProfile,
    knowledge_service: KnowledgeService
) -> List[Dict[str, Any]]:
    """生成生活方式建议"""
    recommendations = []
    
    # 基于年龄的建议
    if patient_profile.age < 30:
        recommendations.append({
            "category": "运动",
            "recommendation": "适量有氧运动，如慢跑、游泳",
            "frequency": "每周3-4次"
        })
    elif patient_profile.age >= 60:
        recommendations.append({
            "category": "运动",
            "recommendation": "温和运动，如太极拳、散步",
            "frequency": "每日30分钟"
        })
    
    # 基于性别的建议
    if patient_profile.gender == "female":
        recommendations.append({
            "category": "饮食",
            "recommendation": "注意补血养颜，多食红枣、枸杞",
            "frequency": "日常饮食"
        })
    
    return recommendations


def _calculate_confidence_score(
    syndrome_candidates: List[Dict[str, Any]],
    patient_profile: PatientProfile
) -> float:
    """计算诊断置信度"""
    if not syndrome_candidates:
        return 0.0
    
    # 基于症状数量和匹配度计算
    symptom_count = len(patient_profile.symptoms)
    max_relevance = max(candidate['relevance_score'] for candidate in syndrome_candidates)
    
    # 简单的置信度计算公式
    base_confidence = max_relevance
    symptom_bonus = min(symptom_count * 0.1, 0.3)  # 症状越多，置信度稍微提高
    
    return min(base_confidence + symptom_bonus, 1.0)


async def _get_typical_symptoms(syndrome_id: str, knowledge_service: KnowledgeService) -> List[Dict[str, Any]]:
    """获取证型的典型症状"""
    # 这里应该从知识图谱中查询证型的典型症状
    return []


async def _get_differential_diagnosis(syndrome_id: str, knowledge_service: KnowledgeService) -> List[Dict[str, Any]]:
    """获取鉴别诊断信息"""
    # 这里应该从知识图谱中查询相似证型的鉴别要点
    return []


async def _get_clinical_cases(syndrome_id: str, knowledge_service: KnowledgeService) -> List[Dict[str, Any]]:
    """获取临床病例"""
    # 这里应该从数据库中查询相关的临床病例
    return []


async def _perform_constitution_assessment(
    symptoms: List[SymptomInput],
    lifestyle_data: Optional[Dict[str, Any]],
    knowledge_service: KnowledgeService
) -> Dict[str, Any]:
    """执行体质评估"""
    # 这里实现体质评估的具体逻辑
    return {
        "constitution_type": "平和质",
        "confidence": 0.75,
        "assessment_details": {
            "primary_characteristics": ["气血充盛", "脏腑功能正常"],
            "secondary_characteristics": [],
            "recommendations": ["保持现有生活方式", "适量运动"]
        }
    } 