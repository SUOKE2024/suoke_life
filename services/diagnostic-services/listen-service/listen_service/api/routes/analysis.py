"""
闻诊分析API路由

提供语音分析、呼吸音分析、咳嗽分析的智能接口
"""

import asyncio
import logging
import io
import wave
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import librosa
import soundfile as sf

from ...core.audio_analyzer import (
    AudioAnalyzer,
    VoiceAnalysisResult,
    BreathingAnalysisResult,
    CoughAnalysisResult,
    AudioType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["闻诊分析"])

# 全局音频分析器实例
audio_analyzer = AudioAnalyzer()

async def process_uploaded_audio(file: UploadFile) -> tuple[np.ndarray, int]:
    """处理上传的音频文件"""
    try:
        # 验证文件类型
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="文件必须是音频格式")
        
        # 读取音频数据
        contents = await file.read()
        
        # 使用librosa加载音频
        audio_data, sample_rate = librosa.load(io.BytesIO(contents), sr=None)
        
        # 验证音频长度
        duration = len(audio_data) / sample_rate
        if duration > 300:  # 最大5分钟
            raise HTTPException(status_code=400, detail="音频文件过长，最大支持5分钟")
        
        if duration < 1:  # 最小1秒
            raise HTTPException(status_code=400, detail="音频文件过短，最少需要1秒")
        
        return audio_data, sample_rate
        
    except Exception as e:
        logger.error(f"音频处理失败: {e}")
        raise HTTPException(status_code=400, detail=f"音频处理失败: {str(e)}")

@router.post("/voice", response_model=Dict[str, Any])
async def analyze_voice(
    file: UploadFile = File(...),
    analysis_type: str = Form("comprehensive")
):
    """
    语音分析接口
    
    上传语音文件，返回声音质量、情绪状态、中医诊断等分析结果
    """
    try:
        logger.info(f"开始语音分析，文件: {file.filename}, 类型: {analysis_type}")
        
        # 处理上传的音频
        audio_data, sample_rate = await process_uploaded_audio(file)
        
        # 执行语音分析
        result = await audio_analyzer.analyze_voice(audio_data, sample_rate)
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": AudioType.VOICE.value,
            "audio_metadata": {
                "duration": len(audio_data) / sample_rate,
                "sample_rate": sample_rate,
                "channels": 1,
                "quality": "良好" if result.confidence > 0.7 else "一般"
            },
            "voice_characteristics": {
                "pitch": result.pitch_analysis,
                "volume": result.volume_analysis,
                "tone_quality": result.tone_quality,
                "speech_rate": result.speech_rate,
                "voice_stability": result.voice_stability
            },
            "tcm_analysis": {
                "voice_quality": result.voice_quality,
                "qi_state": result.qi_state,
                "organ_correlation": result.organ_correlation,
                "syndrome_pattern": result.syndrome_pattern,
                "confidence": result.confidence
            },
            "health_indicators": {
                "respiratory_health": _assess_respiratory_health(result),
                "emotional_state": result.emotional_state,
                "energy_level": result.energy_level,
                "stress_indicators": result.stress_indicators
            },
            "recommendations": _generate_voice_recommendations(result),
            "detailed_analysis": {
                "frequency_analysis": result.frequency_features,
                "temporal_features": result.temporal_features,
                "spectral_features": result.spectral_features
            }
        }
        
        logger.info(f"语音分析完成，声音质量: {result.voice_quality}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"语音分析失败: {str(e)}")

@router.post("/breathing", response_model=Dict[str, Any])
async def analyze_breathing(
    file: UploadFile = File(...),
    breathing_type: str = Form("normal")
):
    """
    呼吸音分析接口
    
    上传呼吸音文件，返回呼吸模式、肺部健康状态等分析结果
    """
    try:
        logger.info(f"开始呼吸音分析，文件: {file.filename}, 类型: {breathing_type}")
        
        # 处理上传的音频
        audio_data, sample_rate = await process_uploaded_audio(file)
        
        # 执行呼吸音分析
        result = await audio_analyzer.analyze_breathing(audio_data, sample_rate)
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": AudioType.BREATHING.value,
            "breathing_pattern": {
                "rhythm": result.breathing_rhythm,
                "depth": result.breathing_depth,
                "rate": result.breathing_rate,
                "regularity": result.breathing_regularity,
                "effort": result.breathing_effort
            },
            "lung_sounds": {
                "normal_sounds": result.normal_sounds,
                "abnormal_sounds": result.abnormal_sounds,
                "wheeze_detection": result.wheeze_detection,
                "crackle_detection": result.crackle_detection
            },
            "tcm_diagnosis": {
                "lung_qi_state": result.lung_qi_state,
                "breathing_quality": result.breathing_quality,
                "syndrome_pattern": result.syndrome_pattern,
                "organ_function": result.organ_function,
                "confidence": result.confidence
            },
            "health_assessment": {
                "respiratory_efficiency": result.respiratory_efficiency,
                "lung_capacity_estimate": result.lung_capacity_estimate,
                "airway_condition": result.airway_condition,
                "overall_health": _assess_breathing_health(result)
            },
            "recommendations": _generate_breathing_recommendations(result),
            "clinical_notes": {
                "significant_findings": result.significant_findings,
                "follow_up_needed": result.follow_up_needed,
                "urgency_level": result.urgency_level
            }
        }
        
        logger.info(f"呼吸音分析完成，呼吸质量: {result.breathing_quality}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"呼吸音分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"呼吸音分析失败: {str(e)}")

@router.post("/cough", response_model=Dict[str, Any])
async def analyze_cough(
    file: UploadFile = File(...),
    cough_context: str = Form("unknown")
):
    """
    咳嗽分析接口
    
    上传咳嗽音频，返回咳嗽类型、病因分析等结果
    """
    try:
        logger.info(f"开始咳嗽分析，文件: {file.filename}, 背景: {cough_context}")
        
        # 处理上传的音频
        audio_data, sample_rate = await process_uploaded_audio(file)
        
        # 执行咳嗽分析
        result = await audio_analyzer.analyze_cough(audio_data, sample_rate)
        
        # 构建响应数据
        response_data = {
            "success": True,
            "analysis_type": AudioType.COUGH.value,
            "cough_characteristics": {
                "cough_type": result.cough_type,
                "intensity": result.cough_intensity,
                "frequency": result.cough_frequency,
                "duration": result.cough_duration,
                "wetness": result.cough_wetness,
                "pitch": result.cough_pitch
            },
            "tcm_classification": {
                "cough_nature": result.cough_nature,
                "pathogen_type": result.pathogen_type,
                "organ_involvement": result.organ_involvement,
                "syndrome_pattern": result.syndrome_pattern,
                "severity": result.severity
            },
            "pathological_indicators": {
                "inflammation_signs": result.inflammation_signs,
                "obstruction_signs": result.obstruction_signs,
                "infection_probability": result.infection_probability,
                "chronic_indicators": result.chronic_indicators
            },
            "differential_diagnosis": {
                "possible_causes": result.possible_causes,
                "probability_scores": result.probability_scores,
                "key_distinguishing_features": result.distinguishing_features
            },
            "treatment_suggestions": _generate_cough_treatment_suggestions(result),
            "monitoring_advice": {
                "follow_up_timeline": result.follow_up_timeline,
                "warning_signs": result.warning_signs,
                "improvement_indicators": result.improvement_indicators
            },
            "confidence": result.confidence
        }
        
        logger.info(f"咳嗽分析完成，咳嗽类型: {result.cough_type}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"咳嗽分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"咳嗽分析失败: {str(e)}")

@router.post("/comprehensive", response_model=Dict[str, Any])
async def comprehensive_audio_analysis(
    voice_file: Optional[UploadFile] = File(None),
    breathing_file: Optional[UploadFile] = File(None),
    cough_file: Optional[UploadFile] = File(None)
):
    """
    综合音频分析接口
    
    同时分析多种音频类型，提供综合诊断结果
    """
    try:
        logger.info("开始综合音频分析")
        
        if not any([voice_file, breathing_file, cough_file]):
            raise HTTPException(status_code=400, detail="至少需要提供一个音频文件")
        
        results = {}
        
        # 并行处理多个音频文件
        tasks = []
        
        if voice_file:
            tasks.append(_process_voice_file(voice_file))
        
        if breathing_file:
            tasks.append(_process_breathing_file(breathing_file))
        
        if cough_file:
            tasks.append(_process_cough_file(cough_file))
        
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
        comprehensive_diagnosis = _generate_comprehensive_audio_diagnosis(results)
        
        response_data = {
            "success": True,
            "analysis_type": "comprehensive_audio",
            "individual_results": results,
            "comprehensive_diagnosis": comprehensive_diagnosis,
            "overall_assessment": {
                "respiratory_health": comprehensive_diagnosis.get("respiratory_health", "未知"),
                "vocal_health": comprehensive_diagnosis.get("vocal_health", "未知"),
                "overall_confidence": comprehensive_diagnosis.get("overall_confidence", 0.0)
            },
            "integrated_recommendations": comprehensive_diagnosis.get("recommendations", []),
            "follow_up_plan": comprehensive_diagnosis.get("follow_up_plan", {})
        }
        
        logger.info("综合音频分析完成")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"综合音频分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"综合音频分析失败: {str(e)}")

# 辅助函数

async def _process_voice_file(file: UploadFile) -> Dict[str, Any]:
    """处理语音文件"""
    try:
        audio_data, sample_rate = await process_uploaded_audio(file)
        result = await audio_analyzer.analyze_voice(audio_data, sample_rate)
        return {"voice_analysis": result}
    except Exception as e:
        logger.error(f"语音文件处理失败: {e}")
        return {}

async def _process_breathing_file(file: UploadFile) -> Dict[str, Any]:
    """处理呼吸音文件"""
    try:
        audio_data, sample_rate = await process_uploaded_audio(file)
        result = await audio_analyzer.analyze_breathing(audio_data, sample_rate)
        return {"breathing_analysis": result}
    except Exception as e:
        logger.error(f"呼吸音文件处理失败: {e}")
        return {}

async def _process_cough_file(file: UploadFile) -> Dict[str, Any]:
    """处理咳嗽文件"""
    try:
        audio_data, sample_rate = await process_uploaded_audio(file)
        result = await audio_analyzer.analyze_cough(audio_data, sample_rate)
        return {"cough_analysis": result}
    except Exception as e:
        logger.error(f"咳嗽文件处理失败: {e}")
        return {}

def _assess_respiratory_health(result: VoiceAnalysisResult) -> str:
    """评估呼吸健康状态"""
    if result.confidence < 0.5:
        return "无法评估"
    
    if result.voice_quality in ["清亮", "洪亮"]:
        return "良好"
    elif result.voice_quality in ["低沉", "嘶哑"]:
        return "需要关注"
    else:
        return "一般"

def _assess_breathing_health(result: BreathingAnalysisResult) -> str:
    """评估呼吸健康状态"""
    if result.confidence < 0.5:
        return "无法评估"
    
    if result.breathing_quality == "正常" and not result.abnormal_sounds:
        return "健康"
    elif result.abnormal_sounds:
        return "异常"
    else:
        return "需要观察"

def _generate_voice_recommendations(result: VoiceAnalysisResult) -> List[str]:
    """生成语音分析建议"""
    recommendations = []
    
    if result.voice_quality == "嘶哑":
        recommendations.extend([
            "避免大声说话",
            "多喝温水润喉",
            "避免辛辣刺激食物"
        ])
    
    if result.qi_state == "气虚":
        recommendations.extend([
            "适当休息，避免过度用声",
            "进行呼吸训练",
            "补充营养，增强体质"
        ])
    
    if result.emotional_state == "紧张":
        recommendations.extend([
            "进行放松训练",
            "保持心情舒畅",
            "适当运动缓解压力"
        ])
    
    return recommendations

def _generate_breathing_recommendations(result: BreathingAnalysisResult) -> List[str]:
    """生成呼吸分析建议"""
    recommendations = []
    
    if result.breathing_quality != "正常":
        recommendations.extend([
            "进行呼吸训练",
            "保持室内空气清新",
            "避免吸烟和二手烟"
        ])
    
    if result.abnormal_sounds:
        recommendations.extend([
            "及时就医检查",
            "避免剧烈运动",
            "注意保暖"
        ])
    
    if result.lung_qi_state == "肺气虚":
        recommendations.extend([
            "适当进行有氧运动",
            "食用润肺食物",
            "避免过度劳累"
        ])
    
    return recommendations

def _generate_cough_treatment_suggestions(result: CoughAnalysisResult) -> List[str]:
    """生成咳嗽治疗建议"""
    suggestions = []
    
    if result.cough_nature == "热咳":
        suggestions.extend([
            "清热化痰",
            "避免辛辣食物",
            "多饮清热茶水"
        ])
    elif result.cough_nature == "寒咳":
        suggestions.extend([
            "温肺散寒",
            "注意保暖",
            "饮用温热汤水"
        ])
    
    if result.cough_wetness == "湿咳":
        suggestions.extend([
            "化痰止咳",
            "避免甜腻食物",
            "保持室内干燥"
        ])
    elif result.cough_wetness == "干咳":
        suggestions.extend([
            "润肺止咳",
            "多饮水润燥",
            "避免干燥环境"
        ])
    
    return suggestions

def _generate_comprehensive_audio_diagnosis(results: Dict[str, Any]) -> Dict[str, Any]:
    """生成综合音频诊断"""
    diagnosis = {
        "respiratory_health": "正常",
        "vocal_health": "正常",
        "overall_confidence": 0.0,
        "recommendations": [],
        "follow_up_plan": {}
    }
    
    confidences = []
    
    # 分析语音结果
    if "voice_analysis" in results:
        voice_result = results["voice_analysis"]
        confidences.append(voice_result.confidence)
        
        if voice_result.voice_quality in ["嘶哑", "低沉"]:
            diagnosis["vocal_health"] = "需要关注"
        
        diagnosis["recommendations"].extend(_generate_voice_recommendations(voice_result))
    
    # 分析呼吸结果
    if "breathing_analysis" in results:
        breathing_result = results["breathing_analysis"]
        confidences.append(breathing_result.confidence)
        
        if breathing_result.abnormal_sounds:
            diagnosis["respiratory_health"] = "异常"
        elif breathing_result.breathing_quality != "正常":
            diagnosis["respiratory_health"] = "需要观察"
        
        diagnosis["recommendations"].extend(_generate_breathing_recommendations(breathing_result))
    
    # 分析咳嗽结果
    if "cough_analysis" in results:
        cough_result = results["cough_analysis"]
        confidences.append(cough_result.confidence)
        
        if cough_result.severity in ["重度", "严重"]:
            diagnosis["respiratory_health"] = "异常"
        
        diagnosis["recommendations"].extend(_generate_cough_treatment_suggestions(cough_result))
    
    # 计算整体置信度
    if confidences:
        diagnosis["overall_confidence"] = sum(confidences) / len(confidences)
    
    # 去重建议
    diagnosis["recommendations"] = list(set(diagnosis["recommendations"]))
    
    # 制定随访计划
    if diagnosis["respiratory_health"] == "异常":
        diagnosis["follow_up_plan"] = {
            "timeline": "1-2周内复查",
            "focus": "呼吸系统检查",
            "urgency": "高"
        }
    elif diagnosis["vocal_health"] == "需要关注":
        diagnosis["follow_up_plan"] = {
            "timeline": "2-4周内观察",
            "focus": "声带健康",
            "urgency": "中"
        }
    
    return diagnosis

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "listen-service",
        "version": "1.0.0",
        "analyzer_status": "ready"
    } 