"""
问诊分析API路由

提供智能对话分析、症状提取、中医问诊的接口
"""

import asyncio
import logging
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from ...core.dialogue_analyzer import (
    DialogueAnalyzer,
    DialogueAnalysisResult,
    SymptomExtractionResult,
    PatientProfileResult,
    TCMDiagnosisResult
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["问诊分析"])

# 全局对话分析器实例
dialogue_analyzer = DialogueAnalyzer()

# 请求模型
class DialogueMessage(BaseModel):
    """对话消息模型"""
    role: str = Field(..., description="角色：doctor/patient")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")

class DialogueRequest(BaseModel):
    """对话分析请求模型"""
    patient_id: str = Field(..., description="患者ID")
    session_id: str = Field(..., description="会话ID")
    dialogue_history: List[DialogueMessage] = Field(..., description="对话历史")
    analysis_type: str = Field(default="comprehensive", description="分析类型")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="上下文信息")

class SymptomExtractionRequest(BaseModel):
    """症状提取请求模型"""
    text: str = Field(..., description="待分析文本")
    context: Optional[str] = Field(default="", description="上下文")
    extract_severity: bool = Field(default=True, description="是否提取严重程度")
    extract_duration: bool = Field(default=True, description="是否提取持续时间")

class IntelligentInquiryRequest(BaseModel):
    """智能问诊请求模型"""
    patient_id: str = Field(..., description="患者ID")
    current_symptoms: List[str] = Field(..., description="当前症状")
    inquiry_stage: str = Field(default="initial", description="问诊阶段")
    previous_answers: Optional[Dict[str, Any]] = Field(default_factory=dict, description="之前的回答")

@router.post("/dialogue", response_model=Dict[str, Any])
async def analyze_dialogue(request: DialogueRequest):
    """
    对话分析接口
    
    分析医患对话，提取症状、生成诊断建议
    """
    try:
        logger.info(f"开始对话分析，患者: {request.patient_id}, 会话: {request.session_id}")
        
        # 验证对话历史
        if not request.dialogue_history:
            raise HTTPException(status_code=400, detail="对话历史不能为空")
        
        # 转换对话格式
        dialogue_data = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "metadata": msg.metadata
            }
            for msg in request.dialogue_history
        ]
        
        # 执行对话分析
        result = await dialogue_analyzer.analyze_dialogue(
            dialogue_data,
            context=request.context
        )
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": "dialogue",
            "patient_info": {
                "patient_id": request.patient_id,
                "session_id": request.session_id,
                "dialogue_length": len(request.dialogue_history),
                "analysis_timestamp": datetime.now().isoformat()
            },
            "extracted_symptoms": {
                "primary_symptoms": result.primary_symptoms,
                "secondary_symptoms": result.secondary_symptoms,
                "symptom_details": result.symptom_details,
                "severity_assessment": result.severity_assessment,
                "duration_analysis": result.duration_analysis
            },
            "patient_profile": {
                "basic_info": result.patient_profile.basic_info,
                "medical_history": result.patient_profile.medical_history,
                "lifestyle_factors": result.patient_profile.lifestyle_factors,
                "psychological_state": result.patient_profile.psychological_state
            },
            "tcm_analysis": {
                "syndrome_patterns": result.tcm_diagnosis.syndrome_patterns,
                "organ_systems": result.tcm_diagnosis.organ_systems,
                "pathogenesis": result.tcm_diagnosis.pathogenesis,
                "constitution_type": result.tcm_diagnosis.constitution_type,
                "confidence": result.tcm_diagnosis.confidence
            },
            "dialogue_quality": {
                "completeness": result.dialogue_quality.completeness,
                "clarity": result.dialogue_quality.clarity,
                "relevance": result.dialogue_quality.relevance,
                "missing_information": result.dialogue_quality.missing_information
            },
            "recommendations": {
                "further_questions": _generate_further_questions(result),
                "diagnostic_suggestions": _generate_diagnostic_suggestions(result),
                "treatment_directions": _generate_treatment_directions(result)
            },
            "confidence_scores": {
                "overall_confidence": result.overall_confidence,
                "symptom_extraction_confidence": result.symptom_extraction_confidence,
                "diagnosis_confidence": result.diagnosis_confidence
            }
        }
        
        logger.info(f"对话分析完成，提取症状: {len(result.primary_symptoms)}, 置信度: {result.overall_confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"对话分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"对话分析失败: {str(e)}")

@router.post("/symptoms/extract", response_model=Dict[str, Any])
async def extract_symptoms(request: SymptomExtractionRequest):
    """
    症状提取接口
    
    从文本中提取症状信息
    """
    try:
        logger.info(f"开始症状提取，文本长度: {len(request.text)}")
        
        # 执行症状提取
        result = await dialogue_analyzer.extract_symptoms(
            text=request.text,
            context=request.context,
            extract_severity=request.extract_severity,
            extract_duration=request.extract_duration
        )
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": "symptom_extraction",
            "input_text": request.text[:200] + "..." if len(request.text) > 200 else request.text,
            "extracted_symptoms": {
                "symptoms": result.symptoms,
                "symptom_categories": result.symptom_categories,
                "severity_levels": result.severity_levels if request.extract_severity else {},
                "duration_info": result.duration_info if request.extract_duration else {},
                "location_info": result.location_info,
                "trigger_factors": result.trigger_factors
            },
            "tcm_classification": {
                "symptom_nature": result.tcm_classification.symptom_nature,
                "organ_correlation": result.tcm_classification.organ_correlation,
                "pathological_patterns": result.tcm_classification.pathological_patterns
            },
            "clinical_significance": {
                "urgency_level": result.clinical_significance.urgency_level,
                "diagnostic_value": result.clinical_significance.diagnostic_value,
                "follow_up_needed": result.clinical_significance.follow_up_needed
            },
            "confidence": result.confidence,
            "processing_metadata": {
                "extraction_method": "NLP + TCM knowledge base",
                "processing_time": result.processing_time,
                "text_quality": "良好" if result.confidence > 0.7 else "一般"
            }
        }
        
        logger.info(f"症状提取完成，提取症状: {len(result.symptoms)}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"症状提取失败: {e}")
        raise HTTPException(status_code=500, detail=f"症状提取失败: {str(e)}")

@router.post("/intelligent-inquiry", response_model=Dict[str, Any])
async def intelligent_inquiry(request: IntelligentInquiryRequest):
    """
    智能问诊接口
    
    基于当前症状生成智能问诊问题
    """
    try:
        logger.info(f"开始智能问诊，患者: {request.patient_id}, 症状数: {len(request.current_symptoms)}")
        
        # 执行智能问诊
        result = await dialogue_analyzer.generate_intelligent_questions(
            current_symptoms=request.current_symptoms,
            inquiry_stage=request.inquiry_stage,
            previous_answers=request.previous_answers
        )
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": "intelligent_inquiry",
            "patient_id": request.patient_id,
            "inquiry_context": {
                "current_symptoms": request.current_symptoms,
                "inquiry_stage": request.inquiry_stage,
                "completed_questions": len(request.previous_answers)
            },
            "generated_questions": {
                "priority_questions": result.priority_questions,
                "follow_up_questions": result.follow_up_questions,
                "differential_questions": result.differential_questions,
                "lifestyle_questions": result.lifestyle_questions
            },
            "question_rationale": {
                "diagnostic_purpose": result.diagnostic_purpose,
                "information_gaps": result.information_gaps,
                "clinical_reasoning": result.clinical_reasoning
            },
            "inquiry_strategy": {
                "recommended_sequence": result.recommended_sequence,
                "estimated_duration": result.estimated_duration,
                "completion_percentage": result.completion_percentage
            },
            "adaptive_features": {
                "personalized_questions": result.personalized_questions,
                "cultural_considerations": result.cultural_considerations,
                "communication_style": result.communication_style
            }
        }
        
        logger.info(f"智能问诊完成，生成问题: {len(result.priority_questions)}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"智能问诊失败: {e}")
        raise HTTPException(status_code=500, detail=f"智能问诊失败: {str(e)}")

@router.post("/comprehensive", response_model=Dict[str, Any])
async def comprehensive_inquiry_analysis(
    dialogue_request: DialogueRequest,
    additional_context: Optional[Dict[str, Any]] = Body(default_factory=dict)
):
    """
    综合问诊分析接口
    
    提供完整的问诊分析，包括对话分析、症状提取、智能问诊建议
    """
    try:
        logger.info(f"开始综合问诊分析，患者: {dialogue_request.patient_id}")
        
        # 并行执行多项分析
        tasks = [
            _analyze_dialogue_comprehensive(dialogue_request),
            _extract_all_symptoms(dialogue_request),
            _generate_follow_up_plan(dialogue_request)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理分析结果
        dialogue_result = results[0] if not isinstance(results[0], Exception) else None
        symptom_result = results[1] if not isinstance(results[1], Exception) else None
        follow_up_result = results[2] if not isinstance(results[2], Exception) else None
        
        # 生成综合评估
        comprehensive_assessment = _generate_comprehensive_assessment(
            dialogue_result, symptom_result, follow_up_result, additional_context
        )
        
        response_data = {
            "success": True,
            "analysis_type": "comprehensive_inquiry",
            "patient_info": {
                "patient_id": dialogue_request.patient_id,
                "session_id": dialogue_request.session_id,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "dialogue_analysis": dialogue_result,
            "symptom_analysis": symptom_result,
            "follow_up_plan": follow_up_result,
            "comprehensive_assessment": comprehensive_assessment,
            "clinical_summary": {
                "key_findings": comprehensive_assessment.get("key_findings", []),
                "diagnostic_impression": comprehensive_assessment.get("diagnostic_impression", ""),
                "confidence_level": comprehensive_assessment.get("confidence_level", 0.0),
                "next_steps": comprehensive_assessment.get("next_steps", [])
            },
            "quality_metrics": {
                "information_completeness": comprehensive_assessment.get("completeness_score", 0.0),
                "diagnostic_clarity": comprehensive_assessment.get("clarity_score", 0.0),
                "clinical_relevance": comprehensive_assessment.get("relevance_score", 0.0)
            }
        }
        
        logger.info(f"综合问诊分析完成，患者: {dialogue_request.patient_id}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"综合问诊分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"综合问诊分析失败: {str(e)}")

# 辅助函数

async def _analyze_dialogue_comprehensive(request: DialogueRequest) -> Dict[str, Any]:
    """综合对话分析"""
    try:
        dialogue_data = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in request.dialogue_history
        ]
        
        result = await dialogue_analyzer.analyze_dialogue(dialogue_data, context=request.context)
        return {
            "symptoms": result.primary_symptoms + result.secondary_symptoms,
            "patient_profile": result.patient_profile,
            "tcm_diagnosis": result.tcm_diagnosis,
            "confidence": result.overall_confidence
        }
    except Exception as e:
        logger.error(f"综合对话分析失败: {e}")
        return {}

async def _extract_all_symptoms(request: DialogueRequest) -> Dict[str, Any]:
    """提取所有症状"""
    try:
        # 合并所有对话内容
        all_text = " ".join([msg.content for msg in request.dialogue_history if msg.role == "patient"])
        
        result = await dialogue_analyzer.extract_symptoms(all_text)
        return {
            "all_symptoms": result.symptoms,
            "symptom_categories": result.symptom_categories,
            "severity_levels": result.severity_levels,
            "confidence": result.confidence
        }
    except Exception as e:
        logger.error(f"症状提取失败: {e}")
        return {}

async def _generate_follow_up_plan(request: DialogueRequest) -> Dict[str, Any]:
    """生成随访计划"""
    try:
        # 基于对话内容生成随访建议
        current_symptoms = []
        for msg in request.dialogue_history:
            if msg.role == "patient":
                # 简化的症状提取
                current_symptoms.extend(_extract_simple_symptoms(msg.content))
        
        result = await dialogue_analyzer.generate_intelligent_questions(
            current_symptoms=current_symptoms,
            inquiry_stage="follow_up"
        )
        
        return {
            "follow_up_questions": result.priority_questions,
            "monitoring_plan": result.recommended_sequence,
            "timeline": result.estimated_duration
        }
    except Exception as e:
        logger.error(f"随访计划生成失败: {e}")
        return {}

def _extract_simple_symptoms(text: str) -> List[str]:
    """简单症状提取"""
    # 简化的症状关键词匹配
    symptom_keywords = [
        "头痛", "发热", "咳嗽", "胸闷", "腹痛", "恶心", "呕吐", "腹泻",
        "失眠", "疲劳", "食欲不振", "心悸", "气短", "头晕", "乏力"
    ]
    
    found_symptoms = []
    for keyword in symptom_keywords:
        if keyword in text:
            found_symptoms.append(keyword)
    
    return found_symptoms

def _generate_further_questions(result: DialogueAnalysisResult) -> List[str]:
    """生成进一步问题"""
    questions = []
    
    # 基于缺失信息生成问题
    if not result.patient_profile.medical_history:
        questions.append("您有什么既往病史吗？")
    
    if not result.patient_profile.lifestyle_factors:
        questions.append("请描述一下您的生活习惯，包括饮食、睡眠、运动等。")
    
    # 基于症状生成问题
    for symptom in result.primary_symptoms:
        if symptom not in result.symptom_details:
            questions.append(f"关于{symptom}，能详细描述一下具体情况吗？")
    
    return questions[:5]  # 限制问题数量

def _generate_diagnostic_suggestions(result: DialogueAnalysisResult) -> List[str]:
    """生成诊断建议"""
    suggestions = []
    
    if result.tcm_diagnosis.syndrome_patterns:
        for pattern in result.tcm_diagnosis.syndrome_patterns:
            suggestions.append(f"考虑{pattern}的可能性")
    
    if result.tcm_diagnosis.organ_systems:
        for organ in result.tcm_diagnosis.organ_systems:
            suggestions.append(f"建议进一步检查{organ}功能")
    
    return suggestions

def _generate_treatment_directions(result: DialogueAnalysisResult) -> List[str]:
    """生成治疗方向"""
    directions = []
    
    if result.tcm_diagnosis.constitution_type:
        directions.append(f"针对{result.tcm_diagnosis.constitution_type}体质进行调理")
    
    if result.tcm_diagnosis.pathogenesis:
        directions.append(f"治疗原则：{result.tcm_diagnosis.pathogenesis}")
    
    return directions

def _generate_comprehensive_assessment(
    dialogue_result: Dict[str, Any],
    symptom_result: Dict[str, Any],
    follow_up_result: Dict[str, Any],
    additional_context: Dict[str, Any]
) -> Dict[str, Any]:
    """生成综合评估"""
    assessment = {
        "key_findings": [],
        "diagnostic_impression": "",
        "confidence_level": 0.0,
        "next_steps": [],
        "completeness_score": 0.0,
        "clarity_score": 0.0,
        "relevance_score": 0.0
    }
    
    # 收集关键发现
    if dialogue_result and dialogue_result.get("symptoms"):
        assessment["key_findings"].extend(dialogue_result["symptoms"][:3])
    
    if symptom_result and symptom_result.get("all_symptoms"):
        assessment["key_findings"].extend(symptom_result["all_symptoms"][:3])
    
    # 生成诊断印象
    if dialogue_result and dialogue_result.get("tcm_diagnosis"):
        tcm_diagnosis = dialogue_result["tcm_diagnosis"]
        if tcm_diagnosis.syndrome_patterns:
            assessment["diagnostic_impression"] = f"初步考虑：{', '.join(tcm_diagnosis.syndrome_patterns[:2])}"
    
    # 计算置信度
    confidences = []
    if dialogue_result and dialogue_result.get("confidence"):
        confidences.append(dialogue_result["confidence"])
    if symptom_result and symptom_result.get("confidence"):
        confidences.append(symptom_result["confidence"])
    
    if confidences:
        assessment["confidence_level"] = sum(confidences) / len(confidences)
    
    # 生成下一步建议
    if follow_up_result and follow_up_result.get("follow_up_questions"):
        assessment["next_steps"].extend(follow_up_result["follow_up_questions"][:3])
    
    # 计算质量评分
    assessment["completeness_score"] = min(1.0, len(assessment["key_findings"]) / 5)
    assessment["clarity_score"] = assessment["confidence_level"]
    assessment["relevance_score"] = 0.8 if assessment["diagnostic_impression"] else 0.5
    
    return assessment

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "inquiry-service",
        "version": "1.0.0",
        "analyzer_status": "ready"
    } 