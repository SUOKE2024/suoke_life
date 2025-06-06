"""
analysis - 索克生活项目模块
"""

from ...core.vision_analyzer import (
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio
import cv2
import io
import logging
import numpy as np

"""
望诊分析API路由

提供面诊、舌诊、眼诊的智能分析接口
"""


    VisionAnalyzer, 
    FaceAnalysisResult, 
    TongueAnalysisResult, 
    EyeAnalysisResult,
    DiagnosisType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["望诊分析"])

# 全局视觉分析器实例
vision_analyzer = VisionAnalyzer()

async def process_uploaded_image(file: UploadFile) -> np.ndarray:
    """处理上传的图像文件"""
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必须是图像格式")
        
        # 读取图像数据
        contents = await file.read()
        
        # 转换为PIL图像
        pil_image = Image.open(io.BytesIO(contents))
        
        # 转换为RGB格式（如果是RGBA）
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        
        # 转换为numpy数组
        image_array = np.array(pil_image)
        
        # 转换为BGR格式（OpenCV格式）
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return image_array
        
    except Exception as e:
        logger.error(f"图像处理失败: {e}")
        raise HTTPException(status_code=400, detail=f"图像处理失败: {str(e)}")

@router.post("/face", response_model=Dict[str, Any])
async def analyze_face(file: UploadFile = File(...)):
    """
    面诊分析接口
    
    上传面部图像，返回面色、光泽、面部特征等分析结果
    """
    try:
        logger.info(f"开始面诊分析，文件: {file.filename}")
        
        # 处理上传的图像
        image = await process_uploaded_image(file)
        
        # 执行面诊分析
        result = await vision_analyzer.analyze_face(image)
        
        # 构建响应数据
        response_data = {
            "success": True,
            "diagnosis_type": DiagnosisType.FACE.value,
            "analysis_result": {
                "complexion": result.complexion,
                "luster": result.luster,
                "facial_features": result.facial_features,
                "emotion_state": result.emotion_state,
                "health_indicators": result.health_indicators,
                "confidence": result.confidence
            },
            "tcm_interpretation": {
                "primary_finding": result.complexion,
                "health_status": "正常" if result.complexion == "红润" else "需要关注",
                "recommendations": _generate_face_recommendations(result)
            },
            "metadata": {
                "analysis_time": "实时",
                "image_quality": "良好" if result.confidence > 0.7 else "一般",
                "processing_method": "计算机视觉分析"
            }
        }
        
        logger.info(f"面诊分析完成，面色: {result.complexion}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"面诊分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"面诊分析失败: {str(e)}")

@router.post("/tongue", response_model=Dict[str, Any])
async def analyze_tongue(file: UploadFile = File(...)):
    """
    舌诊分析接口
    
    上传舌部图像，返回舌质、舌苔、中医诊断等分析结果
    """
    try:
        logger.info(f"开始舌诊分析，文件: {file.filename}")
        
        # 处理上传的图像
        image = await process_uploaded_image(file)
        
        # 执行舌诊分析
        result = await vision_analyzer.analyze_tongue(image)
        
        # 构建响应数据
        response_data = {
            "success": True,
            "diagnosis_type": DiagnosisType.TONGUE.value,
            "analysis_result": {
                "tongue_body": result.tongue_body,
                "tongue_coating": result.tongue_coating,
                "tongue_texture": result.tongue_texture,
                "moisture_level": result.moisture_level,
                "confidence": result.confidence
            },
            "tcm_diagnosis": {
                "primary_diagnosis": result.tcm_diagnosis,
                "syndrome_pattern": _get_syndrome_pattern(result),
                "severity": _assess_severity(result),
                "recommendations": _generate_tongue_recommendations(result)
            },
            "detailed_analysis": {
                "tongue_color_significance": _explain_tongue_color(result.tongue_body["color"]),
                "coating_significance": _explain_coating(result.tongue_coating),
                "clinical_implications": _get_clinical_implications(result)
            },
            "metadata": {
                "analysis_time": "实时",
                "image_quality": "良好" if result.confidence > 0.7 else "一般",
                "processing_method": "中医舌诊AI分析"
            }
        }
        
        logger.info(f"舌诊分析完成，诊断: {result.tcm_diagnosis}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"舌诊分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"舌诊分析失败: {str(e)}")

@router.post("/eyes", response_model=Dict[str, Any])
async def analyze_eyes(file: UploadFile = File(...)):
    """
    眼诊分析接口
    
    上传眼部图像，返回巩膜、瞳孔、眼神等分析结果
    """
    try:
        logger.info(f"开始眼诊分析，文件: {file.filename}")
        
        # 处理上传的图像
        image = await process_uploaded_image(file)
        
        # 执行眼诊分析
        result = await vision_analyzer.analyze_eyes(image)
        
        # 构建响应数据
        response_data = {
            "success": True,
            "diagnosis_type": DiagnosisType.EYE.value,
            "analysis_result": {
                "sclera_color": result.sclera_color,
                "pupil_response": result.pupil_response,
                "eye_luster": result.eye_luster,
                "blood_vessels": result.blood_vessels,
                "eyelid_condition": result.eyelid_condition,
                "confidence": result.confidence
            },
            "tcm_interpretation": {
                "eye_spirit": result.eye_luster,
                "health_indicators": _generate_eye_health_indicators(result),
                "organ_correlation": _get_organ_correlation(result),
                "recommendations": _generate_eye_recommendations(result)
            },
            "clinical_significance": {
                "sclera_meaning": _explain_sclera_color(result.sclera_color),
                "luster_meaning": _explain_eye_luster(result.eye_luster),
                "vessel_meaning": _explain_blood_vessels(result.blood_vessels)
            },
            "metadata": {
                "analysis_time": "实时",
                "image_quality": "良好" if result.confidence > 0.7 else "一般",
                "processing_method": "眼诊AI分析"
            }
        }
        
        logger.info(f"眼诊分析完成，眼神: {result.eye_luster}, 置信度: {result.confidence:.2f}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"眼诊分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"眼诊分析失败: {str(e)}")

@router.post("/comprehensive", response_model=Dict[str, Any])
async def comprehensive_analysis(
    face_file: Optional[UploadFile] = File(None),
    tongue_file: Optional[UploadFile] = File(None),
    eye_file: Optional[UploadFile] = File(None)
):
    """
    综合望诊分析接口
    
    可同时上传面部、舌部、眼部图像，进行综合分析
    """
    try:
        logger.info("开始综合望诊分析")
        
        results = {}
        
        # 面诊分析
        if face_file:
            face_image = await process_uploaded_image(face_file)
            face_result = await vision_analyzer.analyze_face(face_image)
            results["face_analysis"] = face_result
        
        # 舌诊分析
        if tongue_file:
            tongue_image = await process_uploaded_image(tongue_file)
            tongue_result = await vision_analyzer.analyze_tongue(tongue_image)
            results["tongue_analysis"] = tongue_result
        
        # 眼诊分析
        if eye_file:
            eye_image = await process_uploaded_image(eye_file)
            eye_result = await vision_analyzer.analyze_eyes(eye_image)
            results["eye_analysis"] = eye_result
        
        if not results:
            raise HTTPException(status_code=400, detail="至少需要上传一个图像文件")
        
        # 生成综合诊断
        comprehensive_diagnosis = _generate_comprehensive_diagnosis(results)
        
        response_data = {
            "success": True,
            "diagnosis_type": "comprehensive",
            "individual_results": results,
            "comprehensive_diagnosis": comprehensive_diagnosis,
            "metadata": {
                "analysis_time": "实时",
                "analyzed_components": list(results.keys()),
                "processing_method": "多模态望诊AI分析"
            }
        }
        
        logger.info(f"综合望诊分析完成，分析组件: {list(results.keys())}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"综合望诊分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"综合望诊分析失败: {str(e)}")

# 辅助函数

def _generate_face_recommendations(result: FaceAnalysisResult) -> list:
    """生成面诊建议"""
    recommendations = []
    
    if result.complexion == "苍白":
        recommendations.extend([
            "建议增加营养摄入，特别是铁质丰富的食物",
            "适当运动，促进血液循环",
            "保证充足睡眠"
        ])
    elif result.complexion == "萎黄":
        recommendations.extend([
            "调理脾胃，注意饮食规律",
            "避免生冷食物",
            "可适当食用健脾食材"
        ])
    elif result.complexion == "潮红":
        recommendations.extend([
            "清热降火，避免辛辣食物",
            "保持情绪平和",
            "适当清淡饮食"
        ])
    else:
        recommendations.append("保持当前良好状态")
    
    return recommendations

def _generate_tongue_recommendations(result: TongueAnalysisResult) -> list:
    """生成舌诊建议"""
    recommendations = []
    
    if result.tcm_diagnosis == "热证":
        recommendations.extend([
            "清热解毒，多饮水",
            "避免辛辣燥热食物",
            "可食用清热食材如绿豆、莲子"
        ])
    elif result.tcm_diagnosis == "虚寒证":
        recommendations.extend([
            "温阳补虚，避免生冷",
            "适当食用温补食材",
            "注意保暖"
        ])
    elif result.tcm_diagnosis == "血瘀证":
        recommendations.extend([
            "活血化瘀，适当运动",
            "避免久坐不动",
            "可食用活血食材"
        ])
    else:
        recommendations.append("保持良好生活习惯")
    
    return recommendations

def _generate_eye_recommendations(result: EyeAnalysisResult) -> list:
    """生成眼诊建议"""
    recommendations = []
    
    if result.blood_vessels == "充血明显":
        recommendations.extend([
            "注意用眼卫生，避免过度用眼",
            "保证充足睡眠",
            "可适当使用护眼产品"
        ])
    elif result.eye_luster == "无神":
        recommendations.extend([
            "加强营养，特别是维生素A",
            "规律作息，避免熬夜",
            "适当眼部按摩"
        ])
    else:
        recommendations.append("保持良好用眼习惯")
    
    return recommendations

def _get_syndrome_pattern(result: TongueAnalysisResult) -> str:
    """获取证候模式"""
    patterns = {
        "热证": "实热证",
        "虚寒证": "虚寒证",
        "血瘀证": "血瘀证",
        "正常": "平和质"
    }
    return patterns.get(result.tcm_diagnosis, "待进一步辨证")

def _assess_severity(result: TongueAnalysisResult) -> str:
    """评估严重程度"""
    if result.confidence < 0.5:
        return "不确定"
    elif result.tcm_diagnosis == "正常":
        return "正常"
    elif result.tcm_diagnosis in ["热证", "虚寒证"]:
        return "轻度"
    else:
        return "中度"

def _explain_tongue_color(color: str) -> str:
    """解释舌色意义"""
    explanations = {
        "淡红": "正常舌色，气血调和",
        "红": "热证表现，体内有热",
        "绛红": "热盛或阴虚，需要清热",
        "淡白": "气血不足，阳虚表现",
        "青紫": "血瘀或寒证，循环不畅"
    }
    return explanations.get(color, "需要进一步观察")

def _explain_coating(coating: Dict[str, str]) -> str:
    """解释舌苔意义"""
    color = coating.get("color", "")
    thickness = coating.get("thickness", "")
    
    if color == "白苔" and thickness == "薄苔":
        return "正常舌苔，脾胃功能良好"
    elif color == "黄苔":
        return "热证表现，体内有热邪"
    elif color == "黑苔":
        return "热极或寒极，病情较重"
    else:
        return "舌苔异常，需要调理"

def _get_clinical_implications(result: TongueAnalysisResult) -> list:
    """获取临床意义"""
    implications = []
    
    if result.tcm_diagnosis != "正常":
        implications.append(f"提示{result.tcm_diagnosis}，需要相应调理")
    
    if result.confidence < 0.7:
        implications.append("建议结合其他诊断方法确认")
    
    implications.append("舌诊结果仅供参考，不能替代专业医疗诊断")
    
    return implications

def _generate_eye_health_indicators(result: EyeAnalysisResult) -> list:
    """生成眼部健康指标"""
    indicators = []
    
    if result.eye_luster == "有神":
        indicators.append("精神状态良好")
    elif result.eye_luster == "无神":
        indicators.append("可能存在疲劳或营养不足")
    
    if result.blood_vessels == "正常":
        indicators.append("眼部血液循环良好")
    elif result.blood_vessels == "充血明显":
        indicators.append("眼部疲劳或炎症")
    
    return indicators

def _get_organ_correlation(result: EyeAnalysisResult) -> Dict[str, str]:
    """获取脏腑关联"""
    return {
        "肝": "肝开窍于目，眼神反映肝的功能状态",
        "肾": "肾精充足则目光有神",
        "心": "心主神明，眼神体现心神状态"
    }

def _explain_sclera_color(color: str) -> str:
    """解释巩膜颜色意义"""
    explanations = {
        "正常白色": "眼部健康，无明显异常",
        "充血": "可能存在炎症或疲劳",
        "发黄": "可能提示肝胆功能异常"
    }
    return explanations.get(color, "需要进一步观察")

def _explain_eye_luster(luster: str) -> str:
    """解释眼神意义"""
    explanations = {
        "有神": "精神饱满，脏腑功能良好",
        "无神": "精神不振，可能存在虚证",
        "一般": "精神状态一般，需要调养"
    }
    return explanations.get(luster, "需要进一步观察")

def _explain_blood_vessels(vessels: str) -> str:
    """解释血管状态意义"""
    explanations = {
        "正常": "眼部血液循环良好",
        "充血明显": "眼部疲劳或有炎症",
        "轻微充血": "轻度疲劳，注意休息"
    }
    return explanations.get(vessels, "需要进一步观察")

def _generate_comprehensive_diagnosis(results: Dict[str, Any]) -> Dict[str, Any]:
    """生成综合诊断"""
    diagnosis = {
        "overall_assessment": "综合评估",
        "primary_findings": [],
        "syndrome_differentiation": "待综合分析",
        "health_status": "良好",
        "recommendations": []
    }
    
    # 收集主要发现
    if "face_analysis" in results:
        face = results["face_analysis"]
        diagnosis["primary_findings"].append(f"面色: {face.complexion}")
    
    if "tongue_analysis" in results:
        tongue = results["tongue_analysis"]
        diagnosis["primary_findings"].append(f"舌诊: {tongue.tcm_diagnosis}")
    
    if "eye_analysis" in results:
        eye = results["eye_analysis"]
        diagnosis["primary_findings"].append(f"眼神: {eye.eye_luster}")
    
    # 综合建议
    diagnosis["recommendations"] = [
        "建议结合多种诊断方法",
        "保持良好生活习惯",
        "如有不适及时就医"
    ]
    
    return diagnosis
