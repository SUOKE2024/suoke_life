"""
切诊分析API路由

提供脉象分析、腹诊分析、穴位分析的智能接口
"""

import asyncio
import logging
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Body, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from ...core.tactile_analyzer import (
    TactileAnalyzer,
    PulseAnalysisResult,
    AbdominalAnalysisResult,
    AcupointAnalysisResult,
    TactileAnalysisResult
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["切诊分析"])

# 全局触觉分析器实例
tactile_analyzer = TactileAnalyzer()

# 请求模型
class PulseDataPoint(BaseModel):
    """脉象数据点"""
    timestamp: float = Field(..., description="时间戳")
    pressure: float = Field(..., description="压力值")
    amplitude: float = Field(..., description="振幅")
    frequency: float = Field(..., description="频率")

class PulseAnalysisRequest(BaseModel):
    """脉象分析请求模型"""
    patient_id: str = Field(..., description="患者ID")
    pulse_data: List[PulseDataPoint] = Field(..., description="脉象数据")
    measurement_duration: float = Field(..., description="测量时长(秒)")
    sensor_position: str = Field(..., description="传感器位置：寸/关/尺")
    hand_side: str = Field(..., description="手侧：left/right")
    measurement_conditions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="测量条件")

class AbdominalPalpationRequest(BaseModel):
    """腹诊请求模型"""
    patient_id: str = Field(..., description="患者ID")
    palpation_areas: List[str] = Field(..., description="触诊区域")
    pressure_levels: Dict[str, float] = Field(..., description="各区域压力")
    tactile_findings: Dict[str, str] = Field(..., description="触觉发现")
    patient_responses: Dict[str, str] = Field(..., description="患者反应")
    examination_notes: Optional[str] = Field(default="", description="检查备注")

class AcupointAnalysisRequest(BaseModel):
    """穴位分析请求模型"""
    patient_id: str = Field(..., description="患者ID")
    acupoints: List[str] = Field(..., description="检查穴位")
    sensitivity_data: Dict[str, float] = Field(..., description="敏感度数据")
    pressure_tolerance: Dict[str, float] = Field(..., description="压力耐受")
    temperature_data: Optional[Dict[str, float]] = Field(default_factory=dict, description="温度数据")
    electrical_conductance: Optional[Dict[str, float]] = Field(default_factory=dict, description="电导率数据")

@router.post("/pulse", response_model=Dict[str, Any])
async def analyze_pulse(request: PulseAnalysisRequest):
    """
    脉象分析接口
    
    分析脉象数据，返回脉象特征、中医诊断等结果
    """
    try:
        logger.info(f"开始脉象分析，患者: {request.patient_id}, 位置: {request.sensor_position}")
        
        # 验证脉象数据
        if not request.pulse_data:
            raise HTTPException(status_code=400, detail="脉象数据不能为空")
        
        if request.measurement_duration < 30:
            raise HTTPException(status_code=400, detail="测量时长至少需要30秒")
        
        # 转换脉象数据格式
        pulse_data = [
            {
                "timestamp": point.timestamp,
                "pressure": point.pressure,
                "amplitude": point.amplitude,
                "frequency": point.frequency
            }
            for point in request.pulse_data
        ]
        
        # 执行脉象分析
        result = await tactile_analyzer.analyze_pulse(
            pulse_data=pulse_data,
            measurement_duration=request.measurement_duration,
            sensor_position=request.sensor_position,
            hand_side=request.hand_side,
            conditions=request.measurement_conditions
        )
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": "pulse",
            "patient_info": {
                "patient_id": request.patient_id,
                "measurement_timestamp": datetime.now().isoformat(),
                "sensor_position": request.sensor_position,
                "hand_side": request.hand_side,
                "measurement_duration": request.measurement_duration
            },
            "pulse_characteristics": {
                "pulse_rate": result.pulse_rate,
                "pulse_rhythm": result.pulse_rhythm,
                "pulse_strength": result.pulse_strength,
                "pulse_depth": result.pulse_depth,
                "pulse_width": result.pulse_width,
                "pulse_tension": result.pulse_tension,
                "pulse_smoothness": result.pulse_smoothness
            },
            "tcm_pulse_classification": {
                "pulse_type": result.pulse_type,
                "pulse_quality": result.pulse_quality,
                "pulse_position": result.pulse_position,
                "pulse_force": result.pulse_force,
                "pulse_speed": result.pulse_speed
            },
            "clinical_significance": {
                "organ_correlation": result.organ_correlation,
                "pathological_patterns": result.pathological_patterns,
                "constitution_indicators": result.constitution_indicators,
                "disease_tendency": result.disease_tendency
            },
            "diagnostic_insights": {
                "qi_blood_status": result.qi_blood_status,
                "yin_yang_balance": result.yin_yang_balance,
                "organ_function": result.organ_function,
                "pathogen_nature": result.pathogen_nature
            },
            "data_quality": {
                "signal_quality": result.signal_quality,
                "measurement_stability": result.measurement_stability,
                "artifact_detection": result.artifact_detection,
                "confidence": result.confidence
            },
            "recommendations": _generate_pulse_recommendations(result),
            "follow_up": {
                "monitoring_frequency": _determine_monitoring_frequency(result),
                "key_indicators": _identify_key_pulse_indicators(result),
                "improvement_targets": _set_pulse_improvement_targets(result)
            }
        }
        
        logger.info(f"脉象分析完成，脉型: {result.pulse_type}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"脉象分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"脉象分析失败: {str(e)}")

@router.post("/abdominal", response_model=Dict[str, Any])
async def analyze_abdominal_palpation(request: AbdominalPalpationRequest):
    """
    腹诊分析接口
    
    分析腹部触诊结果，返回脏腑功能、病理状态等诊断
    """
    try:
        logger.info(f"开始腹诊分析，患者: {request.patient_id}, 区域数: {len(request.palpation_areas)}")
        
        # 验证腹诊数据
        if not request.palpation_areas:
            raise HTTPException(status_code=400, detail="触诊区域不能为空")
        
        # 执行腹诊分析
        result = await tactile_analyzer.analyze_abdominal_palpation(
            palpation_areas=request.palpation_areas,
            pressure_levels=request.pressure_levels,
            tactile_findings=request.tactile_findings,
            patient_responses=request.patient_responses,
            examination_notes=request.examination_notes
        )
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": "abdominal_palpation",
            "patient_info": {
                "patient_id": request.patient_id,
                "examination_timestamp": datetime.now().isoformat(),
                "examined_areas": request.palpation_areas,
                "examination_notes": request.examination_notes
            },
            "physical_findings": {
                "abdominal_shape": result.abdominal_shape,
                "muscle_tension": result.muscle_tension,
                "tenderness_areas": result.tenderness_areas,
                "mass_detection": result.mass_detection,
                "organ_enlargement": result.organ_enlargement,
                "fluid_detection": result.fluid_detection
            },
            "tcm_abdominal_diagnosis": {
                "qi_stagnation_areas": result.qi_stagnation_areas,
                "blood_stasis_signs": result.blood_stasis_signs,
                "dampness_indicators": result.dampness_indicators,
                "heat_cold_patterns": result.heat_cold_patterns,
                "organ_qi_status": result.organ_qi_status
            },
            "organ_assessment": {
                "liver_status": result.liver_assessment,
                "spleen_status": result.spleen_assessment,
                "stomach_status": result.stomach_assessment,
                "kidney_status": result.kidney_assessment,
                "intestinal_status": result.intestinal_assessment
            },
            "pathological_patterns": {
                "inflammation_signs": result.inflammation_signs,
                "obstruction_indicators": result.obstruction_indicators,
                "deficiency_patterns": result.deficiency_patterns,
                "excess_patterns": result.excess_patterns
            },
            "clinical_correlations": {
                "symptom_correlation": result.symptom_correlation,
                "disease_progression": result.disease_progression,
                "treatment_response": result.treatment_response
            },
            "diagnostic_confidence": {
                "overall_confidence": result.confidence,
                "finding_reliability": result.finding_reliability,
                "examination_quality": result.examination_quality
            },
            "recommendations": _generate_abdominal_recommendations(result),
            "follow_up_plan": {
                "monitoring_areas": _identify_monitoring_areas(result),
                "examination_frequency": _determine_abdominal_monitoring_frequency(result),
                "warning_signs": _identify_abdominal_warning_signs(result)
            }
        }
        
        logger.info(f"腹诊分析完成，发现: {len(result.tenderness_areas)}个压痛点, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"腹诊分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"腹诊分析失败: {str(e)}")

@router.post("/acupoints", response_model=Dict[str, Any])
async def analyze_acupoints(request: AcupointAnalysisRequest):
    """
    穴位分析接口
    
    分析穴位敏感性、电导率等数据，返回经络状态诊断
    """
    try:
        logger.info(f"开始穴位分析，患者: {request.patient_id}, 穴位数: {len(request.acupoints)}")
        
        # 验证穴位数据
        if not request.acupoints:
            raise HTTPException(status_code=400, detail="检查穴位不能为空")
        
        # 执行穴位分析
        result = await tactile_analyzer.analyze_acupoints(
            acupoints=request.acupoints,
            sensitivity_data=request.sensitivity_data,
            pressure_tolerance=request.pressure_tolerance,
            temperature_data=request.temperature_data,
            electrical_conductance=request.electrical_conductance
        )
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": "acupoint_analysis",
            "patient_info": {
                "patient_id": request.patient_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "examined_acupoints": request.acupoints,
                "measurement_types": _get_measurement_types(request)
            },
            "acupoint_characteristics": {
                "sensitivity_levels": result.sensitivity_levels,
                "pressure_responses": result.pressure_responses,
                "temperature_variations": result.temperature_variations,
                "electrical_properties": result.electrical_properties,
                "tactile_qualities": result.tactile_qualities
            },
            "meridian_analysis": {
                "meridian_status": result.meridian_status,
                "qi_flow_patterns": result.qi_flow_patterns,
                "blockage_points": result.blockage_points,
                "energy_levels": result.energy_levels,
                "meridian_balance": result.meridian_balance
            },
            "tcm_diagnosis": {
                "organ_correlations": result.organ_correlations,
                "pathological_patterns": result.pathological_patterns,
                "constitution_indicators": result.constitution_indicators,
                "treatment_points": result.treatment_points
            },
            "clinical_findings": {
                "abnormal_acupoints": result.abnormal_acupoints,
                "reactive_points": result.reactive_points,
                "tender_points": result.tender_points,
                "diagnostic_points": result.diagnostic_points
            },
            "therapeutic_insights": {
                "treatment_priorities": result.treatment_priorities,
                "acupuncture_recommendations": result.acupuncture_recommendations,
                "massage_points": result.massage_points,
                "contraindicated_points": result.contraindicated_points
            },
            "measurement_quality": {
                "data_reliability": result.data_reliability,
                "measurement_consistency": result.measurement_consistency,
                "confidence": result.confidence
            },
            "recommendations": _generate_acupoint_recommendations(result),
            "treatment_plan": {
                "primary_points": _select_primary_treatment_points(result),
                "supporting_points": _select_supporting_points(result),
                "treatment_frequency": _determine_treatment_frequency(result),
                "expected_outcomes": _predict_treatment_outcomes(result)
            }
        }
        
        logger.info(f"穴位分析完成，异常穴位: {len(result.abnormal_acupoints)}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"穴位分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"穴位分析失败: {str(e)}")

@router.post("/comprehensive", response_model=Dict[str, Any])
async def comprehensive_tactile_analysis(
    pulse_request: Optional[PulseAnalysisRequest] = Body(None),
    abdominal_request: Optional[AbdominalPalpationRequest] = Body(None),
    acupoint_request: Optional[AcupointAnalysisRequest] = Body(None)
):
    """
    综合切诊分析接口
    
    整合脉象、腹诊、穴位分析，提供综合诊断结果
    """
    try:
        logger.info("开始综合切诊分析")
        
        if not any([pulse_request, abdominal_request, acupoint_request]):
            raise HTTPException(status_code=400, detail="至少需要提供一种切诊数据")
        
        results = {}
        
        # 并行执行多项分析
        tasks = []
        
        if pulse_request:
            tasks.append(_process_pulse_analysis(pulse_request))
        
        if abdominal_request:
            tasks.append(_process_abdominal_analysis(abdominal_request))
        
        if acupoint_request:
            tasks.append(_process_acupoint_analysis(acupoint_request))
        
        # 执行并行分析
        analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, result in enumerate(analysis_results):
            if isinstance(result, Exception):
                logger.error(f"分析任务 {i} 失败: {result}")
                continue
            
            if result:
                results.update(result)
        
        # 生成综合诊断
        comprehensive_diagnosis = _generate_comprehensive_tactile_diagnosis(results)
        
        response_data = {
            "success": True,
            "analysis_type": "comprehensive_tactile",
            "individual_results": results,
            "comprehensive_diagnosis": comprehensive_diagnosis,
            "integrated_assessment": {
                "overall_health_status": comprehensive_diagnosis.get("overall_health_status", "未知"),
                "primary_patterns": comprehensive_diagnosis.get("primary_patterns", []),
                "organ_function_summary": comprehensive_diagnosis.get("organ_function_summary", {}),
                "treatment_priority": comprehensive_diagnosis.get("treatment_priority", "")
            },
            "clinical_synthesis": {
                "diagnostic_confidence": comprehensive_diagnosis.get("diagnostic_confidence", 0.0),
                "pattern_consistency": comprehensive_diagnosis.get("pattern_consistency", 0.0),
                "treatment_urgency": comprehensive_diagnosis.get("treatment_urgency", "低")
            },
            "integrated_recommendations": comprehensive_diagnosis.get("recommendations", []),
            "holistic_treatment_plan": comprehensive_diagnosis.get("treatment_plan", {})
        }
        
        logger.info("综合切诊分析完成")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"综合切诊分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"综合切诊分析失败: {str(e)}")

# 辅助函数

async def _process_pulse_analysis(request: PulseAnalysisRequest) -> Dict[str, Any]:
    """处理脉象分析"""
    try:
        pulse_data = [
            {
                "timestamp": point.timestamp,
                "pressure": point.pressure,
                "amplitude": point.amplitude,
                "frequency": point.frequency
            }
            for point in request.pulse_data
        ]
        
        result = await tactile_analyzer.analyze_pulse(
            pulse_data=pulse_data,
            measurement_duration=request.measurement_duration,
            sensor_position=request.sensor_position,
            hand_side=request.hand_side,
            conditions=request.measurement_conditions
        )
        
        return {"pulse_analysis": result}
    except Exception as e:
        logger.error(f"脉象分析处理失败: {e}")
        return {}

async def _process_abdominal_analysis(request: AbdominalPalpationRequest) -> Dict[str, Any]:
    """处理腹诊分析"""
    try:
        result = await tactile_analyzer.analyze_abdominal_palpation(
            palpation_areas=request.palpation_areas,
            pressure_levels=request.pressure_levels,
            tactile_findings=request.tactile_findings,
            patient_responses=request.patient_responses,
            examination_notes=request.examination_notes
        )
        
        return {"abdominal_analysis": result}
    except Exception as e:
        logger.error(f"腹诊分析处理失败: {e}")
        return {}

async def _process_acupoint_analysis(request: AcupointAnalysisRequest) -> Dict[str, Any]:
    """处理穴位分析"""
    try:
        result = await tactile_analyzer.analyze_acupoints(
            acupoints=request.acupoints,
            sensitivity_data=request.sensitivity_data,
            pressure_tolerance=request.pressure_tolerance,
            temperature_data=request.temperature_data,
            electrical_conductance=request.electrical_conductance
        )
        
        return {"acupoint_analysis": result}
    except Exception as e:
        logger.error(f"穴位分析处理失败: {e}")
        return {}

def _get_measurement_types(request: AcupointAnalysisRequest) -> List[str]:
    """获取测量类型"""
    types = ["sensitivity", "pressure_tolerance"]
    
    if request.temperature_data:
        types.append("temperature")
    
    if request.electrical_conductance:
        types.append("electrical_conductance")
    
    return types

def _generate_pulse_recommendations(result: PulseAnalysisResult) -> List[str]:
    """生成脉象分析建议"""
    recommendations = []
    
    if result.pulse_type == "数脉":
        recommendations.extend([
            "注意清热降火",
            "避免辛辣刺激食物",
            "保持心情平静"
        ])
    elif result.pulse_type == "迟脉":
        recommendations.extend([
            "注意温阳补气",
            "适当运动增强体质",
            "避免寒凉食物"
        ])
    
    if result.pulse_strength == "弱":
        recommendations.extend([
            "加强营养补充",
            "适当休息",
            "避免过度劳累"
        ])
    
    return recommendations

def _generate_abdominal_recommendations(result: AbdominalAnalysisResult) -> List[str]:
    """生成腹诊分析建议"""
    recommendations = []
    
    if result.qi_stagnation_areas:
        recommendations.extend([
            "进行腹部按摩",
            "适当运动促进气血流通",
            "保持情绪舒畅"
        ])
    
    if result.dampness_indicators:
        recommendations.extend([
            "注意饮食清淡",
            "避免油腻甜食",
            "适当除湿"
        ])
    
    if result.tenderness_areas:
        recommendations.extend([
            "避免腹部受凉",
            "注意饮食规律",
            "及时就医检查"
        ])
    
    return recommendations

def _generate_acupoint_recommendations(result: AcupointAnalysisResult) -> List[str]:
    """生成穴位分析建议"""
    recommendations = []
    
    if result.abnormal_acupoints:
        recommendations.extend([
            "针对异常穴位进行针灸治疗",
            "定期按摩相关穴位",
            "注意相关脏腑调理"
        ])
    
    if result.blockage_points:
        recommendations.extend([
            "疏通经络阻滞",
            "加强相关部位运动",
            "避免长期保持同一姿势"
        ])
    
    return recommendations

def _determine_monitoring_frequency(result: PulseAnalysisResult) -> str:
    """确定脉象监测频率"""
    if result.confidence < 0.6 or result.pulse_type in ["促脉", "结脉", "代脉"]:
        return "每日监测"
    elif result.pulse_type in ["数脉", "迟脉"]:
        return "每周监测"
    else:
        return "每月监测"

def _identify_key_pulse_indicators(result: PulseAnalysisResult) -> List[str]:
    """识别关键脉象指标"""
    indicators = []
    
    indicators.append(f"脉率: {result.pulse_rate}")
    indicators.append(f"脉型: {result.pulse_type}")
    indicators.append(f"脉力: {result.pulse_strength}")
    
    return indicators

def _set_pulse_improvement_targets(result: PulseAnalysisResult) -> List[str]:
    """设置脉象改善目标"""
    targets = []
    
    if result.pulse_rate > 90:
        targets.append("脉率降至正常范围(60-90次/分)")
    elif result.pulse_rate < 60:
        targets.append("脉率提升至正常范围(60-90次/分)")
    
    if result.pulse_strength == "弱":
        targets.append("增强脉力")
    
    return targets

def _identify_monitoring_areas(result: AbdominalAnalysisResult) -> List[str]:
    """识别需要监测的腹部区域"""
    areas = []
    
    areas.extend(result.tenderness_areas)
    areas.extend(result.qi_stagnation_areas)
    
    if result.mass_detection:
        areas.extend(result.mass_detection.keys())
    
    return list(set(areas))

def _determine_abdominal_monitoring_frequency(result: AbdominalAnalysisResult) -> str:
    """确定腹诊监测频率"""
    if result.tenderness_areas or result.mass_detection:
        return "每周检查"
    elif result.qi_stagnation_areas:
        return "每两周检查"
    else:
        return "每月检查"

def _identify_abdominal_warning_signs(result: AbdominalAnalysisResult) -> List[str]:
    """识别腹诊警示征象"""
    warning_signs = []
    
    if result.mass_detection:
        warning_signs.append("腹部包块增大")
    
    if result.tenderness_areas:
        warning_signs.append("压痛加重")
    
    warning_signs.extend([
        "腹痛加剧",
        "腹胀明显",
        "恶心呕吐"
    ])
    
    return warning_signs

def _select_primary_treatment_points(result: AcupointAnalysisResult) -> List[str]:
    """选择主要治疗穴位"""
    primary_points = []
    
    # 基于异常穴位选择治疗点
    for point in result.abnormal_acupoints:
        if point in result.treatment_points:
            primary_points.append(point)
    
    # 基于脏腑相关性选择
    for organ, points in result.organ_correlations.items():
        if points:
            primary_points.extend(points[:2])  # 每个脏腑选择前2个穴位
    
    return list(set(primary_points))[:6]  # 限制主要穴位数量

def _select_supporting_points(result: AcupointAnalysisResult) -> List[str]:
    """选择辅助治疗穴位"""
    supporting_points = []
    
    # 基于经络平衡选择辅助穴位
    for meridian, status in result.meridian_status.items():
        if status != "正常":
            # 选择该经络的调节穴位
            supporting_points.extend(_get_meridian_regulation_points(meridian))
    
    return list(set(supporting_points))[:4]  # 限制辅助穴位数量

def _get_meridian_regulation_points(meridian: str) -> List[str]:
    """获取经络调节穴位"""
    meridian_points = {
        "肺经": ["太渊", "列缺"],
        "大肠经": ["合谷", "曲池"],
        "胃经": ["足三里", "三阴交"],
        "脾经": ["太白", "血海"],
        "心经": ["神门", "少海"],
        "小肠经": ["后溪", "小海"],
        "膀胱经": ["委中", "昆仑"],
        "肾经": ["太溪", "涌泉"],
        "心包经": ["内关", "大陵"],
        "三焦经": ["外关", "支沟"],
        "胆经": ["阳陵泉", "风池"],
        "肝经": ["太冲", "行间"]
    }
    
    return meridian_points.get(meridian, [])

def _determine_treatment_frequency(result: AcupointAnalysisResult) -> str:
    """确定治疗频率"""
    if len(result.abnormal_acupoints) > 5:
        return "每日治疗"
    elif len(result.abnormal_acupoints) > 2:
        return "隔日治疗"
    else:
        return "每周2-3次"

def _predict_treatment_outcomes(result: AcupointAnalysisResult) -> Dict[str, str]:
    """预测治疗效果"""
    outcomes = {}
    
    if result.confidence > 0.8:
        outcomes["预期效果"] = "良好"
        outcomes["改善时间"] = "2-4周"
    elif result.confidence > 0.6:
        outcomes["预期效果"] = "中等"
        outcomes["改善时间"] = "4-8周"
    else:
        outcomes["预期效果"] = "需要观察"
        outcomes["改善时间"] = "8周以上"
    
    return outcomes

def _generate_comprehensive_tactile_diagnosis(results: Dict[str, Any]) -> Dict[str, Any]:
    """生成综合切诊诊断"""
    diagnosis = {
        "overall_health_status": "正常",
        "primary_patterns": [],
        "organ_function_summary": {},
        "treatment_priority": "低",
        "diagnostic_confidence": 0.0,
        "pattern_consistency": 0.0,
        "treatment_urgency": "低",
        "recommendations": [],
        "treatment_plan": {}
    }
    
    confidences = []
    patterns = []
    
    # 分析脉象结果
    if "pulse_analysis" in results:
        pulse_result = results["pulse_analysis"]
        confidences.append(pulse_result.confidence)
        
        if pulse_result.pulse_type != "平脉":
            patterns.append(f"脉象异常: {pulse_result.pulse_type}")
        
        diagnosis["organ_function_summary"]["心血管"] = pulse_result.qi_blood_status
    
    # 分析腹诊结果
    if "abdominal_analysis" in results:
        abdominal_result = results["abdominal_analysis"]
        confidences.append(abdominal_result.confidence)
        
        if abdominal_result.tenderness_areas:
            patterns.append("腹部压痛")
            diagnosis["treatment_urgency"] = "中"
        
        diagnosis["organ_function_summary"]["消化系统"] = abdominal_result.organ_qi_status
    
    # 分析穴位结果
    if "acupoint_analysis" in results:
        acupoint_result = results["acupoint_analysis"]
        confidences.append(acupoint_result.confidence)
        
        if acupoint_result.abnormal_acupoints:
            patterns.append("经络异常")
        
        diagnosis["organ_function_summary"]["经络系统"] = acupoint_result.meridian_status
    
    # 计算整体置信度
    if confidences:
        diagnosis["diagnostic_confidence"] = sum(confidences) / len(confidences)
    
    # 设置主要证候
    diagnosis["primary_patterns"] = patterns[:3]
    
    # 确定治疗优先级
    if len(patterns) > 2:
        diagnosis["treatment_priority"] = "高"
    elif len(patterns) > 0:
        diagnosis["treatment_priority"] = "中"
    
    # 计算证候一致性
    diagnosis["pattern_consistency"] = min(1.0, len(patterns) / 3)
    
    # 生成综合建议
    if patterns:
        diagnosis["recommendations"].extend([
            "综合调理脏腑功能",
            "疏通经络气血",
            "平衡阴阳"
        ])
    
    # 制定治疗计划
    diagnosis["treatment_plan"] = {
        "治疗原则": "整体调理，标本兼治",
        "治疗方法": ["针灸", "推拿", "中药"],
        "疗程安排": "4-8周为一疗程",
        "随访计划": "每周评估一次"
    }
    
    return diagnosis

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "palpation-service",
        "version": "1.0.0",
        "analyzer_status": "ready"
    } 