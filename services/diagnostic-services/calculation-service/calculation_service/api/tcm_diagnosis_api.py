"""
中医诊断API接口
整合舌脉象分析和知识图谱推理功能
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import numpy as np
import cv2
import json
import logging
from datetime import datetime
import asyncio
from io import BytesIO

from ..core.algorithms.tongue_pulse_analysis import (
    TonguePulseCalculationEngine,
    TongueImageAnalyzer,
    PulseWaveformAnalyzer
)

logger = logging.getLogger(__name__)

# Pydantic模型定义
class SymptomInput(BaseModel):
    """症状输入模型"""
    symptoms: List[str] = Field(..., description="症状列表")
    severity: Optional[Dict[str, int]] = Field(None, description="症状严重程度(1-10)")

class TongueAnalysisInput(BaseModel):
    """舌诊输入模型"""
    image_base64: Optional[str] = Field(None, description="舌象图片的base64编码")
    manual_observation: Optional[Dict[str, Any]] = Field(None, description="人工观察结果")

class PulseAnalysisInput(BaseModel):
    """脉诊输入模型"""
    waveform_data: Optional[List[float]] = Field(None, description="脉搏波形数据")
    duration: float = Field(30.0, description="采集时长(秒)")
    sampling_rate: int = Field(1000, description="采样率")
    manual_observation: Optional[Dict[str, Any]] = Field(None, description="人工观察结果")

class PatientInfo(BaseModel):
    """患者信息模型"""
    age: int = Field(..., description="年龄")
    gender: str = Field(..., description="性别")
    height: Optional[float] = Field(None, description="身高(cm)")
    weight: Optional[float] = Field(None, description="体重(kg)")
    medical_history: Optional[List[str]] = Field(None, description="病史")
    current_medications: Optional[List[str]] = Field(None, description="当前用药")

class DiagnosisRequest(BaseModel):
    """诊断请求模型"""
    patient_info: PatientInfo
    symptoms: SymptomInput
    tongue_analysis: Optional[TongueAnalysisInput] = None
    pulse_analysis: Optional[PulseAnalysisInput] = None
    additional_info: Optional[Dict[str, Any]] = None

class DiagnosisResponse(BaseModel):
    """诊断响应模型"""
    diagnosis_id: str
    timestamp: datetime
    patient_info: PatientInfo
    tongue_analysis_result: Optional[Dict[str, Any]] = None
    pulse_analysis_result: Optional[Dict[str, Any]] = None
    syndrome_classification: Dict[str, Any]
    treatment_recommendations: List[Dict[str, Any]]
    confidence_score: float
    reasoning_explanation: str
    differential_diagnosis: List[Dict[str, Any]]

class AnalysisStatus(BaseModel):
    """分析状态模型"""
    diagnosis_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    estimated_completion: Optional[datetime] = None

# 创建FastAPI应用
app = FastAPI(
    title="中医诊断API",
    description="基于舌脉象分析和知识图谱推理的中医诊断系统",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
calculation_engine = TonguePulseCalculationEngine()
analysis_tasks: Dict[str, Dict[str, Any]] = {}

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("中医诊断API服务启动")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("中医诊断API服务关闭")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "tcm-diagnosis-api",
        "version": "1.0.0"
    }

@app.post("/api/v1/diagnosis", response_model=DiagnosisResponse)
async def create_diagnosis(
    request: DiagnosisRequest,
    background_tasks: BackgroundTasks
):
    """
    创建中医诊断
    """
    try:
        diagnosis_id = f"diag_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(request)) % 10000:04d}"
        
        # 初始化分析状态
        analysis_tasks[diagnosis_id] = {
            "status": "processing",
            "progress": 0,
            "message": "开始分析",
            "start_time": datetime.now()
        }
        
        # 启动后台分析任务
        background_tasks.add_task(
            process_diagnosis_async,
            diagnosis_id,
            request
        )
        
        return {
            "diagnosis_id": diagnosis_id,
            "timestamp": datetime.now(),
            "patient_info": request.patient_info,
            "syndrome_classification": {"status": "processing"},
            "treatment_recommendations": [],
            "confidence_score": 0.0,
            "reasoning_explanation": "诊断分析进行中...",
            "differential_diagnosis": []
        }
        
    except Exception as e:
        logger.error(f"创建诊断失败: {e}")
        raise HTTPException(status_code=500, detail=f"诊断创建失败: {str(e)}")

@app.get("/api/v1/diagnosis/{diagnosis_id}/status", response_model=AnalysisStatus)
async def get_diagnosis_status(diagnosis_id: str):
    """
    获取诊断状态
    """
    if diagnosis_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="诊断ID不存在")
    
    task_info = analysis_tasks[diagnosis_id]
    
    return AnalysisStatus(
        diagnosis_id=diagnosis_id,
        status=task_info["status"],
        progress=task_info["progress"],
        message=task_info["message"],
        estimated_completion=task_info.get("estimated_completion")
    )

@app.get("/api/v1/diagnosis/{diagnosis_id}/result")
async def get_diagnosis_result(diagnosis_id: str):
    """
    获取诊断结果
    """
    if diagnosis_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="诊断ID不存在")
    
    task_info = analysis_tasks[diagnosis_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(status_code=202, detail="诊断尚未完成")
    
    return task_info.get("result", {})

@app.post("/api/v1/tongue-analysis")
async def analyze_tongue_image(
    file: UploadFile = File(...),
    manual_observation: Optional[str] = None
):
    """
    舌象图像分析
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必须是图像格式")
        
        # 读取图像数据
        image_data = await file.read()
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="无法解析图像文件")
        
        # 分析舌象
        tongue_analyzer = TongueImageAnalyzer()
        result = tongue_analyzer.analyze_tongue_image(image)
        
        # 转换结果为字典格式
        analysis_result = {
            "color": result.color.value,
            "coating": result.coating.value,
            "texture": result.texture,
            "moisture": result.moisture,
            "thickness": result.thickness,
            "color_confidence": result.color_confidence,
            "coating_confidence": result.coating_confidence,
            "abnormal_areas": result.abnormal_areas,
            "timestamp": result.timestamp.isoformat()
        }
        
        # 如果有人工观察结果，进行融合
        if manual_observation:
            manual_data = json.loads(manual_observation)
            analysis_result["manual_observation"] = manual_data
            analysis_result["fusion_result"] = fuse_tongue_observations(analysis_result, manual_data)
        
        return {
            "status": "success",
            "analysis_result": analysis_result,
            "processing_time": "实时分析完成"
        }
        
    except Exception as e:
        logger.error(f"舌象分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"舌象分析失败: {str(e)}")

@app.post("/api/v1/pulse-analysis")
async def analyze_pulse_waveform(request: PulseAnalysisInput):
    """
    脉象波形分析
    """
    try:
        if not request.waveform_data:
            raise HTTPException(status_code=400, detail="缺少脉搏波形数据")
        
        # 转换为numpy数组
        waveform = np.array(request.waveform_data)
        
        # 分析脉象
        pulse_analyzer = PulseWaveformAnalyzer(sampling_rate=request.sampling_rate)
        result = pulse_analyzer.analyze_pulse_waveform(waveform, request.duration)
        
        # 转换结果为字典格式
        analysis_result = {
            "pulse_type": result.pulse_type.value,
            "rate": result.rate,
            "rhythm": result.rhythm,
            "strength": result.strength,
            "depth": result.depth,
            "width": result.width,
            "confidence": result.confidence,
            "waveform_features": result.waveform_features,
            "timestamp": result.timestamp.isoformat()
        }
        
        # 如果有人工观察结果，进行融合
        if request.manual_observation:
            analysis_result["manual_observation"] = request.manual_observation
            analysis_result["fusion_result"] = fuse_pulse_observations(analysis_result, request.manual_observation)
        
        return {
            "status": "success",
            "analysis_result": analysis_result,
            "processing_time": "实时分析完成"
        }
        
    except Exception as e:
        logger.error(f"脉象分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"脉象分析失败: {str(e)}")

@app.post("/api/v1/comprehensive-analysis")
async def comprehensive_tcm_analysis(
    tongue_image: Optional[UploadFile] = File(None),
    pulse_data: Optional[str] = None,
    symptoms: str = "[]",
    patient_info: str = "{}"
):
    """
    综合中医分析（支持文件上传）
    """
    try:
        # 解析输入参数
        symptoms_list = json.loads(symptoms)
        patient_data = json.loads(patient_info)
        
        analysis_results = {}
        
        # 舌象分析
        if tongue_image:
            image_data = await tongue_image.read()
            image_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is not None:
                tongue_result = calculation_engine.tongue_analyzer.analyze_tongue_image(image)
                analysis_results["tongue_analysis"] = {
                    "color": tongue_result.color.value,
                    "coating": tongue_result.coating.value,
                    "texture": tongue_result.texture,
                    "moisture": tongue_result.moisture,
                    "thickness": tongue_result.thickness,
                    "confidence": tongue_result.color_confidence
                }
        
        # 脉象分析
        if pulse_data:
            pulse_info = json.loads(pulse_data)
            if "waveform" in pulse_info:
                waveform = np.array(pulse_info["waveform"])
                duration = pulse_info.get("duration", 30.0)
                
                pulse_result = calculation_engine.pulse_analyzer.analyze_pulse_waveform(waveform, duration)
                analysis_results["pulse_analysis"] = {
                    "pulse_type": pulse_result.pulse_type.value,
                    "rate": pulse_result.rate,
                    "rhythm": pulse_result.rhythm,
                    "strength": pulse_result.strength,
                    "confidence": pulse_result.confidence
                }
        
        # 综合分析
        comprehensive_result = calculation_engine.comprehensive_analysis(
            tongue_image=image if tongue_image else None,
            pulse_waveform=waveform if pulse_data else None
        )
        
        # 添加症状和患者信息到结果中
        comprehensive_result["symptoms"] = symptoms_list
        comprehensive_result["patient_info"] = patient_data
        
        return {
            "status": "success",
            "comprehensive_result": comprehensive_result,
            "individual_analyses": analysis_results
        }
        
    except Exception as e:
        logger.error(f"综合分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"综合分析失败: {str(e)}")

async def process_diagnosis_async(diagnosis_id: str, request: DiagnosisRequest):
    """
    异步处理诊断请求
    """
    try:
        # 更新状态：开始舌象分析
        analysis_tasks[diagnosis_id].update({
            "status": "processing",
            "progress": 10,
            "message": "正在分析舌象..."
        })
        
        tongue_result = None
        if request.tongue_analysis and request.tongue_analysis.image_base64:
            # 解码base64图像
            import base64
            image_data = base64.b64decode(request.tongue_analysis.image_base64)
            image_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is not None:
                tongue_result = calculation_engine.tongue_analyzer.analyze_tongue_image(image)
        
        # 更新状态：开始脉象分析
        analysis_tasks[diagnosis_id].update({
            "progress": 30,
            "message": "正在分析脉象..."
        })
        
        pulse_result = None
        if request.pulse_analysis and request.pulse_analysis.waveform_data:
            waveform = np.array(request.pulse_analysis.waveform_data)
            pulse_result = calculation_engine.pulse_analyzer.analyze_pulse_waveform(
                waveform, request.pulse_analysis.duration
            )
        
        # 更新状态：综合分析
        analysis_tasks[diagnosis_id].update({
            "progress": 60,
            "message": "正在进行综合分析..."
        })
        
        # 执行综合分析
        comprehensive_result = calculation_engine.comprehensive_analysis(
            tongue_image=image if tongue_result else None,
            pulse_waveform=waveform if pulse_result else None
        )
        
        # 更新状态：生成报告
        analysis_tasks[diagnosis_id].update({
            "progress": 90,
            "message": "正在生成诊断报告..."
        })
        
        # 构建最终结果
        final_result = {
            "diagnosis_id": diagnosis_id,
            "timestamp": datetime.now(),
            "patient_info": request.patient_info,
            "tongue_analysis_result": format_tongue_result(tongue_result) if tongue_result else None,
            "pulse_analysis_result": format_pulse_result(pulse_result) if pulse_result else None,
            "syndrome_classification": comprehensive_result.get("syndrome_classification", {}),
            "treatment_recommendations": comprehensive_result.get("recommendations", []),
            "confidence_score": calculate_overall_confidence(comprehensive_result),
            "reasoning_explanation": generate_reasoning_explanation(comprehensive_result),
            "differential_diagnosis": generate_differential_diagnosis(comprehensive_result)
        }
        
        # 更新状态：完成
        analysis_tasks[diagnosis_id].update({
            "status": "completed",
            "progress": 100,
            "message": "诊断分析完成",
            "result": final_result,
            "completion_time": datetime.now()
        })
        
    except Exception as e:
        logger.error(f"诊断处理失败 {diagnosis_id}: {e}")
        analysis_tasks[diagnosis_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"诊断失败: {str(e)}",
            "error": str(e)
        })

def fuse_tongue_observations(auto_result: Dict, manual_result: Dict) -> Dict:
    """融合自动分析和人工观察的舌诊结果"""
    fusion_result = auto_result.copy()
    
    # 如果人工观察置信度更高，使用人工结果
    if manual_result.get("confidence", 0) > auto_result.get("color_confidence", 0):
        fusion_result["color"] = manual_result.get("color", auto_result["color"])
        fusion_result["coating"] = manual_result.get("coating", auto_result["coating"])
    
    # 融合置信度
    fusion_result["fusion_confidence"] = (
        auto_result.get("color_confidence", 0) * 0.6 + 
        manual_result.get("confidence", 0) * 0.4
    )
    
    return fusion_result

def fuse_pulse_observations(auto_result: Dict, manual_result: Dict) -> Dict:
    """融合自动分析和人工观察的脉诊结果"""
    fusion_result = auto_result.copy()
    
    # 如果人工观察置信度更高，使用人工结果
    if manual_result.get("confidence", 0) > auto_result.get("confidence", 0):
        fusion_result["pulse_type"] = manual_result.get("pulse_type", auto_result["pulse_type"])
        fusion_result["rhythm"] = manual_result.get("rhythm", auto_result["rhythm"])
    
    # 融合置信度
    fusion_result["fusion_confidence"] = (
        auto_result.get("confidence", 0) * 0.7 + 
        manual_result.get("confidence", 0) * 0.3
    )
    
    return fusion_result

def format_tongue_result(result) -> Dict:
    """格式化舌诊结果"""
    return {
        "color": result.color.value,
        "coating": result.coating.value,
        "texture": result.texture,
        "moisture": result.moisture,
        "thickness": result.thickness,
        "confidence": result.color_confidence,
        "abnormal_areas": result.abnormal_areas,
        "timestamp": result.timestamp.isoformat()
    }

def format_pulse_result(result) -> Dict:
    """格式化脉诊结果"""
    return {
        "pulse_type": result.pulse_type.value,
        "rate": result.rate,
        "rhythm": result.rhythm,
        "strength": result.strength,
        "depth": result.depth,
        "width": result.width,
        "confidence": result.confidence,
        "features": result.waveform_features,
        "timestamp": result.timestamp.isoformat()
    }

def calculate_overall_confidence(result: Dict) -> float:
    """计算总体置信度"""
    confidences = []
    
    if "tongue_analysis" in result and result["tongue_analysis"]:
        confidences.append(result["tongue_analysis"].get("color_confidence", 0))
    
    if "pulse_analysis" in result and result["pulse_analysis"]:
        confidences.append(result["pulse_analysis"].get("confidence", 0))
    
    if "syndrome_classification" in result:
        confidences.append(result["syndrome_classification"].get("primary_score", 0))
    
    return sum(confidences) / len(confidences) if confidences else 0.0

def generate_reasoning_explanation(result: Dict) -> str:
    """生成推理解释"""
    explanations = []
    
    # 舌诊解释
    if "tongue_analysis" in result and result["tongue_analysis"]:
        tongue = result["tongue_analysis"]
        explanations.append(f"舌象表现为{tongue['color']}舌{tongue['coating']}苔")
    
    # 脉诊解释
    if "pulse_analysis" in result and result["pulse_analysis"]:
        pulse = result["pulse_analysis"]
        explanations.append(f"脉象为{pulse['pulse_type']}，脉率{pulse['rate']:.0f}次/分")
    
    # 证候解释
    if "syndrome_classification" in result:
        syndrome = result["syndrome_classification"]
        if syndrome.get("primary_syndrome"):
            explanations.append(f"综合分析提示{syndrome['primary_syndrome']}可能性较大")
    
    return "；".join(explanations) if explanations else "基于现有信息进行综合分析"

def generate_differential_diagnosis(result: Dict) -> List[Dict]:
    """生成鉴别诊断"""
    differential = []
    
    if "syndrome_classification" in result:
        all_syndromes = result["syndrome_classification"].get("all_syndromes", {})
        
        for syndrome, info in list(all_syndromes.items())[:3]:  # 取前3个
            differential.append({
                "syndrome": syndrome,
                "probability": info.get("score", 0),
                "supporting_evidence": info.get("matched_features", []),
                "confidence": info.get("confidence", False)
            })
    
    return differential

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 