"""
切诊服务实现 - 索克生活项目
实现中医切诊的数字化，包括脉象分析、触诊数据处理等功能
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
from fastapi import HTTPException
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PulseType(str, Enum):
    """脉象类型枚举"""
    FLOATING = "浮脉"  # 浮脉
    DEEP = "沉脉"      # 沉脉
    SLOW = "迟脉"      # 迟脉
    RAPID = "数脉"     # 数脉
    SLIPPERY = "滑脉"  # 滑脉
    ROUGH = "涩脉"     # 涩脉
    WIRY = "弦脉"      # 弦脉
    TIGHT = "紧脉"     # 紧脉
    WEAK = "弱脉"      # 弱脉
    STRONG = "强脉"    # 强脉

class TouchType(str, Enum):
    """触诊类型枚举"""
    ABDOMEN = "腹诊"   # 腹部触诊
    LIMBS = "四肢"     # 四肢触诊
    ACUPOINTS = "穴位" # 穴位触诊
    SKIN = "皮肤"      # 皮肤触诊
    MUSCLE = "肌肉"    # 肌肉触诊

@dataclass
class PulseData:
    """脉象数据"""
    position: str  # 脉位：寸、关、尺
    rate: int      # 脉率（次/分钟）
    rhythm: str    # 脉律：规整、不规整
    strength: float # 脉力：0-1
    tension: float  # 脉张力：0-1
    width: float    # 脉宽：0-1
    depth: float    # 脉深度：0-1
    smoothness: float # 脉流利度：0-1

@dataclass
class TouchData:
    """触诊数据"""
    area: str           # 触诊部位
    temperature: float  # 温度
    moisture: float     # 湿润度
    elasticity: float   # 弹性
    tenderness: float   # 压痛
    hardness: float     # 硬度
    thickness: float    # 厚度

class PalpationRequest(BaseModel):
    """切诊请求"""
    patient_id: str = Field(..., description="患者ID")
    session_id: str = Field(..., description="会话ID")
    pulse_data: List[Dict[str, Any]] = Field(..., description="脉象数据")
    touch_data: List[Dict[str, Any]] = Field(..., description="触诊数据")
    symptoms: List[str] = Field(default=[], description="症状列表")
    constitution: Optional[str] = Field(None, description="体质类型")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class PalpationResult(BaseModel):
    """切诊结果"""
    analysis_id: str = Field(..., description="分析ID")
    pulse_analysis: Dict[str, Any] = Field(..., description="脉象分析")
    touch_analysis: Dict[str, Any] = Field(..., description="触诊分析")
    syndrome_differentiation: Dict[str, Any] = Field(..., description="辨证分析")
    recommendations: List[str] = Field(..., description="建议")
    confidence: float = Field(..., description="置信度")
    processing_time: float = Field(..., description="处理时间")
    timestamp: str = Field(..., description="时间戳")

class PalpationServiceImpl:
    """切诊服务实现类"""
    
    def __init__(self):
        """初始化切诊服务"""
        self.pulse_patterns = self._load_pulse_patterns()
        self.touch_patterns = self._load_touch_patterns()
        self.syndrome_rules = self._load_syndrome_rules()
        logger.info("切诊服务初始化完成")
    
    def _load_pulse_patterns(self) -> Dict[str, Any]:
        """加载脉象模式库"""
        return {
            "浮脉": {
                "characteristics": {"depth": 0.2, "strength": 0.7},
                "indications": ["表证", "虚阳外越"],
                "constitution": ["气虚", "阳虚"]
            },
            "沉脉": {
                "characteristics": {"depth": 0.8, "strength": 0.6},
                "indications": ["里证", "阳气不足"],
                "constitution": ["阳虚", "痰湿"]
            },
            "数脉": {
                "characteristics": {"rate": ">90", "rhythm": "规整"},
                "indications": ["热证", "阴虚"],
                "constitution": ["阴虚", "湿热"]
            },
            "迟脉": {
                "characteristics": {"rate": "<60", "rhythm": "规整"},
                "indications": ["寒证", "阳虚"],
                "constitution": ["阳虚", "痰湿"]
            },
            "滑脉": {
                "characteristics": {"smoothness": 0.9, "width": 0.7},
                "indications": ["痰湿", "食积", "妊娠"],
                "constitution": ["痰湿", "湿热"]
            },
            "涩脉": {
                "characteristics": {"smoothness": 0.3, "tension": 0.8},
                "indications": ["血瘀", "精亏", "血虚"],
                "constitution": ["血瘀", "阴虚"]
            },
            "弦脉": {
                "characteristics": {"tension": 0.9, "width": 0.4},
                "indications": ["肝胆病", "痛证", "痰饮"],
                "constitution": ["气郁", "痰湿"]
            },
            "紧脉": {
                "characteristics": {"tension": 0.8, "strength": 0.8},
                "indications": ["寒证", "痛证", "宿食"],
                "constitution": ["阳虚", "气滞"]
            }
        }
    
    def _load_touch_patterns(self) -> Dict[str, Any]:
        """加载触诊模式库"""
        return {
            "腹诊": {
                "正常": {"temperature": 0.5, "elasticity": 0.7, "tenderness": 0.1},
                "脾胃虚寒": {"temperature": 0.3, "elasticity": 0.5, "tenderness": 0.3},
                "肝气郁结": {"temperature": 0.6, "elasticity": 0.4, "tenderness": 0.7},
                "湿热内蕴": {"temperature": 0.8, "elasticity": 0.6, "tenderness": 0.5}
            },
            "穴位": {
                "正常": {"tenderness": 0.1, "elasticity": 0.7},
                "经络阻滞": {"tenderness": 0.8, "elasticity": 0.3},
                "气血不足": {"tenderness": 0.3, "elasticity": 0.4}
            },
            "皮肤": {
                "正常": {"temperature": 0.5, "moisture": 0.5, "elasticity": 0.7},
                "阳虚": {"temperature": 0.3, "moisture": 0.3, "elasticity": 0.5},
                "阴虚": {"temperature": 0.7, "moisture": 0.2, "elasticity": 0.4},
                "湿盛": {"temperature": 0.4, "moisture": 0.8, "elasticity": 0.6}
            }
        }
    
    def _load_syndrome_rules(self) -> Dict[str, Any]:
        """加载辨证规则"""
        return {
            "气虚证": {
                "pulse_indicators": ["弱脉", "虚脉"],
                "touch_indicators": ["肌肉松软", "按之无力"],
                "symptoms": ["乏力", "气短", "懒言"],
                "confidence_weight": 0.8
            },
            "血瘀证": {
                "pulse_indicators": ["涩脉", "结脉"],
                "touch_indicators": ["局部硬结", "压痛明显"],
                "symptoms": ["疼痛", "肿块", "紫斑"],
                "confidence_weight": 0.9
            },
            "痰湿证": {
                "pulse_indicators": ["滑脉", "濡脉"],
                "touch_indicators": ["肌肉松软", "水肿"],
                "symptoms": ["痰多", "胸闷", "肢体困重"],
                "confidence_weight": 0.85
            },
            "阴虚证": {
                "pulse_indicators": ["细脉", "数脉"],
                "touch_indicators": ["皮肤干燥", "肌肉瘦削"],
                "symptoms": ["潮热", "盗汗", "口干"],
                "confidence_weight": 0.8
            },
            "阳虚证": {
                "pulse_indicators": ["迟脉", "沉脉"],
                "touch_indicators": ["肢冷", "肌肉松软"],
                "symptoms": ["畏寒", "乏力", "腰膝酸软"],
                "confidence_weight": 0.8
            }
        }
    
    async def analyze_pulse(self, pulse_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析脉象"""
        try:
            pulse_results = []
            overall_patterns = []
            
            for pulse_data in pulse_data_list:
                pulse = PulseData(**pulse_data)
                
                # 分析脉象特征
                pattern_scores = {}
                for pattern_name, pattern_info in self.pulse_patterns.items():
                    score = self._calculate_pulse_pattern_score(pulse, pattern_info)
                    pattern_scores[pattern_name] = score
                
                # 找出最匹配的脉象
                best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
                
                pulse_result = {
                    "position": pulse.position,
                    "detected_pattern": best_pattern[0],
                    "confidence": best_pattern[1],
                    "characteristics": {
                        "rate": pulse.rate,
                        "rhythm": pulse.rhythm,
                        "strength": pulse.strength,
                        "tension": pulse.tension,
                        "depth": pulse.depth,
                        "smoothness": pulse.smoothness
                    },
                    "pattern_scores": pattern_scores
                }
                
                pulse_results.append(pulse_result)
                overall_patterns.append(best_pattern[0])
            
            # 综合分析
            pattern_frequency = {}
            for pattern in overall_patterns:
                pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
            
            dominant_pattern = max(pattern_frequency.items(), key=lambda x: x[1])[0]
            
            return {
                "individual_results": pulse_results,
                "dominant_pattern": dominant_pattern,
                "pattern_distribution": pattern_frequency,
                "clinical_significance": self.pulse_patterns[dominant_pattern]["indications"],
                "constitution_indication": self.pulse_patterns[dominant_pattern]["constitution"]
            }
            
        except Exception as e:
            logger.error(f"脉象分析失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"脉象分析失败: {str(e)}")
    
    def _calculate_pulse_pattern_score(self, pulse: PulseData, pattern_info: Dict[str, Any]) -> float:
        """计算脉象模式匹配分数"""
        score = 0.0
        total_weight = 0.0
        
        characteristics = pattern_info["characteristics"]
        
        # 检查脉率
        if "rate" in characteristics:
            rate_condition = characteristics["rate"]
            if isinstance(rate_condition, str):
                if rate_condition.startswith(">"):
                    target_rate = int(rate_condition[1:])
                    if pulse.rate > target_rate:
                        score +=1.0
                elif rate_condition.startswith("<"):
                    target_rate = int(rate_condition[1:])
                    if pulse.rate < target_rate:
                        score +=1.0
            total_weight +=1.0
        
        # 检查其他特征
        for char_name, target_value in characteristics.items():
            if char_name=="rate":
                continue
            
            if hasattr(pulse, char_name):
                actual_value = getattr(pulse, char_name)
                if isinstance(target_value, (int, float)):
                    # 计算相似度
                    similarity = 1.0 - abs(actual_value - target_value)
                    score +=max(0, similarity)
                    total_weight +=1.0
        
        return score / total_weight if total_weight > 0 else 0.0
    
    async def analyze_touch(self, touch_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析触诊"""
        try:
            touch_results = []
            
            for touch_data in touch_data_list:
                touch = TouchData(**touch_data)
                
                # 根据触诊部位选择相应的模式库
                area_patterns = self.touch_patterns.get(touch.area, {})
                
                pattern_scores = {}
                for pattern_name, pattern_info in area_patterns.items():
                    score = self._calculate_touch_pattern_score(touch, pattern_info)
                    pattern_scores[pattern_name] = score
                
                if pattern_scores:
                    best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
                    
                    touch_result = {
                        "area": touch.area,
                        "detected_pattern": best_pattern[0],
                        "confidence": best_pattern[1],
                        "measurements": {
                            "temperature": touch.temperature,
                            "moisture": touch.moisture,
                            "elasticity": touch.elasticity,
                            "tenderness": touch.tenderness,
                            "hardness": touch.hardness,
                            "thickness": touch.thickness
                        },
                        "pattern_scores": pattern_scores
                    }
                    
                    touch_results.append(touch_result)
            
            return {
                "individual_results": touch_results,
                "summary": self._summarize_touch_findings(touch_results)
            }
            
        except Exception as e:
            logger.error(f"触诊分析失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"触诊分析失败: {str(e)}")
    
    def _calculate_touch_pattern_score(self, touch: TouchData, pattern_info: Dict[str, Any]) -> float:
        """计算触诊模式匹配分数"""
        score = 0.0
        total_weight = 0.0
        
        for char_name, target_value in pattern_info.items():
            if hasattr(touch, char_name):
                actual_value = getattr(touch, char_name)
                similarity = 1.0 - abs(actual_value - target_value)
                score +=max(0, similarity)
                total_weight +=1.0
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _summarize_touch_findings(self, touch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """总结触诊发现"""
        abnormal_findings = []
        areas_examined = []
        
        for result in touch_results:
            areas_examined.append(result["area"])
            if result["detected_pattern"]!="正常":
                abnormal_findings.append({
                    "area": result["area"],
                    "finding": result["detected_pattern"],
                    "confidence": result["confidence"]
                })
        
        return {
            "areas_examined": areas_examined,
            "abnormal_findings": abnormal_findings,
            "overall_assessment": "正常" if not abnormal_findings else "异常"
        }
    
    async def perform_syndrome_differentiation(
        self, 
        pulse_analysis: Dict[str, Any], 
        touch_analysis: Dict[str, Any], 
        symptoms: List[str]
    ) -> Dict[str, Any]:
        """执行辨证分析"""
        try:
            syndrome_scores = {}
            
            for syndrome_name, syndrome_info in self.syndrome_rules.items():
                score = 0.0
                evidence = []
                
                # 检查脉象指标
                pulse_indicators = syndrome_info["pulse_indicators"]
                dominant_pulse = pulse_analysis.get("dominant_pattern", "")
                if dominant_pulse in pulse_indicators:
                    score +=0.4
                    evidence.append(f"脉象: {dominant_pulse}")
                
                # 检查触诊指标
                touch_indicators = syndrome_info["touch_indicators"]
                touch_findings = touch_analysis.get("summary", {}).get("abnormal_findings", [])
                for finding in touch_findings:
                    if any(indicator in finding["finding"] for indicator in touch_indicators):
                        score +=0.3
                        evidence.append(f"触诊: {finding['finding']}")
                
                # 检查症状
                syndrome_symptoms = syndrome_info["symptoms"]
                matching_symptoms = [s for s in symptoms if s in syndrome_symptoms]
                if matching_symptoms:
                    score +=0.3 * (len(matching_symptoms) / len(syndrome_symptoms))
                    evidence.extend([f"症状: {s}" for s in matching_symptoms])
                
                # 应用置信度权重
                final_score = score * syndrome_info["confidence_weight"]
                
                syndrome_scores[syndrome_name] = {
                    "score": final_score,
                    "evidence": evidence,
                    "confidence": syndrome_info["confidence_weight"]
                }
            
            # 排序并选择最可能的证候
            sorted_syndromes = sorted(
                syndrome_scores.items(), 
                key=lambda x: x[1]["score"], 
                reverse=True
            )
            
            primary_syndrome = sorted_syndromes[0] if sorted_syndromes else None
            
            return {
                "primary_syndrome": {
                    "name": primary_syndrome[0],
                    "score": primary_syndrome[1]["score"],
                    "evidence": primary_syndrome[1]["evidence"],
                    "confidence": primary_syndrome[1]["confidence"]
                } if primary_syndrome else None,
                "all_syndromes": dict(syndrome_scores),
                "differential_diagnosis": [
                    {"name": name, "score": info["score"]} 
                    for name, info in sorted_syndromes[:3]
                ]
            }
            
        except Exception as e:
            logger.error(f"辨证分析失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"辨证分析失败: {str(e)}")
    
    def _generate_recommendations(self, syndrome_analysis: Dict[str, Any]) -> List[str]:
        """生成治疗建议"""
        recommendations = []
        
        primary_syndrome = syndrome_analysis.get("primary_syndrome")
        if not primary_syndrome:
            return ["建议进一步检查以明确诊断"]
        
        syndrome_name = primary_syndrome["name"]
        
        # 基于证候的治疗建议
        treatment_recommendations = {
            "气虚证": [
                "建议补气健脾，可选用四君子汤加减",
                "适当运动，如太极拳、八段锦等",
                "饮食宜清淡易消化，多食山药、大枣等",
                "保证充足睡眠，避免过度劳累"
            ],
            "血瘀证": [
                "建议活血化瘀，可选用血府逐瘀汤加减",
                "适当按摩，促进血液循环",
                "饮食宜温热，可食用红花、当归等",
                "避免久坐久立，适当运动"
            ],
            "痰湿证": [
                "建议健脾化湿，可选用二陈汤加减",
                "控制饮食，少食肥甘厚腻",
                "适当运动，如快走、游泳等",
                "保持环境干燥，避免潮湿"
            ],
            "阴虚证": [
                "建议滋阴润燥，可选用六味地黄丸加减",
                "避免熬夜，保证充足睡眠",
                "饮食宜清淡，多食银耳、百合等",
                "避免辛辣刺激食物"
            ],
            "阳虚证": [
                "建议温阳补肾，可选用金匮肾气丸加减",
                "注意保暖，避免受寒",
                "饮食宜温热，可食用羊肉、生姜等",
                "适当运动，增强体质"
            ]
        }
        
        recommendations = treatment_recommendations.get(syndrome_name, [
            "建议咨询专业中医师进行个性化治疗",
            "定期复查，观察病情变化",
            "保持良好的生活习惯"
        ])
        
        return recommendations
    
    async def perform_comprehensive_palpation(self, request: PalpationRequest) -> PalpationResult:
        """执行综合切诊分析"""
        start_time = time.time()
        
        try:
            # 生成分析ID
            analysis_id = f"palpation_{int(time.time())}_{request.patient_id}"
            
            # 脉象分析
            pulse_analysis = await self.analyze_pulse(request.pulse_data)
            
            # 触诊分析
            touch_analysis = await self.analyze_touch(request.touch_data)
            
            # 辨证分析
            syndrome_analysis = await self.perform_syndrome_differentiation(
                pulse_analysis, touch_analysis, request.symptoms
            )
            
            # 生成建议
            recommendations = self._generate_recommendations(syndrome_analysis)
            
            # 计算总体置信度
            pulse_confidence = np.mean([
                result["confidence"] for result in pulse_analysis["individual_results"]
            ]) if pulse_analysis["individual_results"] else 0.0
            
            touch_confidence = np.mean([
                result["confidence"] for result in touch_analysis["individual_results"]
            ]) if touch_analysis["individual_results"] else 0.0
            
            syndrome_confidence = syndrome_analysis["primary_syndrome"]["confidence"] \
                if syndrome_analysis["primary_syndrome"] else 0.0
            
            overall_confidence = (pulse_confidence + touch_confidence + syndrome_confidence) / 3
            
            processing_time = time.time() - start_time
            
            result = PalpationResult(
                analysis_id=analysis_id,
                pulse_analysis=pulse_analysis,
                touch_analysis=touch_analysis,
                syndrome_differentiation=syndrome_analysis,
                recommendations=recommendations,
                confidence=overall_confidence,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"切诊分析完成: {analysis_id}, 耗时: {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"综合切诊分析失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"综合切诊分析失败: {str(e)}")

# 全局服务实例
palpation_service = PalpationServiceImpl()

async def process_palpation_request(request: PalpationRequest) -> PalpationResult:
    """处理切诊请求的主入口函数"""
    return await palpation_service.perform_comprehensive_palpation(request)

def main():
    """主函数"""
    logger.info("切诊服务启动")
    # 这里可以添加服务启动逻辑

if __name__=="__main__":
    main()
