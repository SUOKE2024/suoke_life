#!/usr/bin/env python3
"""
小艾智能体管理器 - 索克生活项目
负责中医诊断智能体的核心功能实现
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
import aiohttp
import json

# 智能体状态枚举
class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    LEARNING = "learning"
    ERROR = "error"
    OFFLINE = "offline"

# 诊断类型枚举
class DiagnosisType(Enum):
    LOOKING = "looking"  # 望诊
    LISTENING = "listening"  # 闻诊
    INQUIRY = "inquiry"  # 问诊
    PALPATION = "palpation"  # 切诊
    CALCULATION = "calculation"  # 算诊

# 智能体配置
@dataclass
class AgentConfig:
    """智能体配置类"""
    agent_id: str = "xiaoai"
    name: str = "小艾"
    description: str = "中医诊断智能体"
    version: str = "1.0.0"
    max_concurrent_sessions: int = 100
    session_timeout: int = 3600  # 1小时
    context_window_size: int = 4096
    confidence_threshold: float = 0.7
    enable_learning: bool = True
    enable_metrics: bool = True

# 会话数据
@dataclass
class SessionData:
    """会话数据类"""
    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    context: Dict[str, Any] = field(default_factory=dict)
    diagnosis_history: List[Dict[str, Any]] = field(default_factory=list)
    patient_info: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"

# 诊断请求
@dataclass
class DiagnosisRequest:
    """诊断请求类"""
    user_id: str
    session_id: str
    diagnosis_type: DiagnosisType
    data: Dict[str, Any]
    patient_info: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

# 诊断响应
@dataclass
class DiagnosisResponse:
    """诊断响应类"""
    message_id: str
    diagnosis_type: DiagnosisType
    result: Dict[str, Any]
    confidence: float
    suggestions: List[str]
    metadata: Dict[str, Any]
    timestamp: float

class XiaoaiAgentManager:
    """小艾智能体管理器"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """初始化智能体管理器"""
        self.config = config or AgentConfig()
        self.status = AgentStatus.OFFLINE
        self.active_sessions: Dict[str, SessionData] = {}
        self.metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_diagnoses": 0,
            "successful_diagnoses": 0,
            "failed_diagnoses": 0,
            "average_response_time": 0.0,
            "uptime": 0.0
        }
        self.start_time = time.time()
        
        # 设置日志
        self.logger = logging.getLogger(f"xiaoai.{self.config.agent_id}")
        self.logger.setLevel(logging.INFO)
        
        # 中医知识库
        self.tcm_knowledge = self._initialize_tcm_knowledge()
        
        # 诊断模型配置
        self.diagnosis_models = {
            DiagnosisType.LOOKING: self._initialize_looking_model(),
            DiagnosisType.LISTENING: self._initialize_listening_model(),
            DiagnosisType.INQUIRY: self._initialize_inquiry_model(),
            DiagnosisType.PALPATION: self._initialize_palpation_model(),
            DiagnosisType.CALCULATION: self._initialize_calculation_model()
        }
        
        logger.info(f"小艾智能体管理器初始化完成: {self.config.agent_id}")

    def _initialize_tcm_knowledge(self) -> Dict[str, Any]:
        """初始化中医知识库"""
        return {
            "syndromes": {
                "qi_deficiency": {
                    "name": "气虚证",
                    "symptoms": ["乏力", "气短", "声音低微", "面色萎黄"],
                    "tongue": "舌质淡",
                    "pulse": "脉细弱",
                    "treatment": "补中益气"
                },
                "blood_stasis": {
                    "name": "血瘀证", 
                    "symptoms": ["胸痛", "刺痛", "面色晦暗"],
                    "tongue": "舌质紫暗",
                    "pulse": "脉涩",
                    "treatment": "活血化瘀"
                },
                "phlegm_dampness": {
                    "name": "痰湿证",
                    "symptoms": ["胸闷", "痰多", "身重困倦"],
                    "tongue": "舌苔厚腻",
                    "pulse": "脉滑",
                    "treatment": "化痰除湿"
                }
            },
            "constitutions": {
                "qi_deficiency": "气虚质",
                "yang_deficiency": "阳虚质",
                "yin_deficiency": "阴虚质",
                "phlegm_dampness": "痰湿质",
                "damp_heat": "湿热质",
                "blood_stasis": "血瘀质",
                "qi_stagnation": "气郁质",
                "special_diathesis": "特禀质",
                "balanced": "平和质"
            },
            "formulas": {
                "si_jun_zi_tang": {
                    "name": "四君子汤",
                    "composition": ["人参", "白术", "茯苓", "甘草"],
                    "function": "益气健脾",
                    "indication": "脾胃气虚证"
                },
                "bu_zhong_yi_qi_tang": {
                    "name": "补中益气汤",
                    "composition": ["黄芪", "人参", "白术", "甘草", "当归", "陈皮", "升麻", "柴胡"],
                    "function": "补中益气，升阳举陷",
                    "indication": "脾胃虚弱，中气下陷证"
                }
            }
        }

    def _initialize_looking_model(self) -> Dict[str, Any]:
        """初始化望诊模型"""
        return {
            "face_analysis": {
                "color_mapping": {
                    "red": "热证",
                    "yellow": "脾胃虚弱",
                    "white": "气血不足",
                    "black": "肾虚",
                    "blue": "寒证"
                }
            },
            "tongue_analysis": {
                "tongue_body": {
                    "pale": "气血不足",
                    "red": "热证",
                    "purple": "血瘀",
                    "dark_red": "热盛"
                },
                "tongue_coating": {
                    "white_thin": "正常",
                    "white_thick": "寒湿",
                    "yellow_thin": "热证",
                    "yellow_thick": "湿热"
                }
            }
        }

    def _initialize_listening_model(self) -> Dict[str, Any]:
        """初始化闻诊模型"""
        return {
            "voice_analysis": {
                "volume": {
                    "low": "气虚",
                    "high": "实证",
                    "normal": "正常"
                },
                "tone": {
                    "hoarse": "肺燥",
                    "weak": "气虚",
                    "sharp": "肝火"
                }
            },
            "breathing_analysis": {
                "shallow": "气虚",
                "rapid": "热证",
                "slow": "寒证"
            }
        }

    def _initialize_inquiry_model(self) -> Dict[str, Any]:
        """初始化问诊模型"""
        return {
            "symptom_mapping": {
                "fatigue": "气虚",
                "insomnia": "心肾不交",
                "poor_appetite": "脾胃虚弱",
                "cold_limbs": "阳虚",
                "night_sweats": "阴虚"
            },
            "question_templates": [
                "请描述您的主要不适症状？",
                "症状持续多长时间了？",
                "什么情况下症状会加重或减轻？",
                "您的睡眠质量如何？",
                "您的饮食和排便情况怎样？"
            ]
        }

    def _initialize_palpation_model(self) -> Dict[str, Any]:
        """初始化切诊模型"""
        return {
            "pulse_analysis": {
                "rate": {
                    "slow": "寒证",
                    "fast": "热证",
                    "normal": "正常"
                },
                "strength": {
                    "weak": "虚证",
                    "strong": "实证",
                    "normal": "正常"
                },
                "rhythm": {
                    "irregular": "心律不齐",
                    "regular": "正常"
                }
            },
            "acupoint_sensitivity": {
                "shenmen": "心神不宁",
                "taichong": "肝气郁结",
                "zusanli": "脾胃虚弱"
            }
        }

    def _initialize_calculation_model(self) -> Dict[str, Any]:
        """初始化算诊模型"""
        return {
            "syndrome_weights": {
                "qi_deficiency": 0.3,
                "blood_stasis": 0.25,
                "phlegm_dampness": 0.2,
                "yin_deficiency": 0.15,
                "yang_deficiency": 0.1
            },
            "confidence_thresholds": {
                "high": 0.8,
                "medium": 0.6,
                "low": 0.4
            }
        }

    async def start(self) -> None:
        """启动智能体"""
        try:
            self.status = AgentStatus.IDLE
            self.start_time = time.time()
            
            # 启动后台任务
            asyncio.create_task(self._session_cleanup_task())
            asyncio.create_task(self._metrics_update_task())
            
            logger.info(f"小艾智能体 {self.config.agent_id} 启动成功")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"智能体启动失败: {e}")
            raise

    async def stop(self) -> None:
        """停止智能体"""
        try:
            self.status = AgentStatus.OFFLINE
            
            # 清理活跃会话
            for session_id in list(self.active_sessions.keys()):
                await self.end_session(session_id)
            
            logger.info(f"小艾智能体 {self.config.agent_id} 已停止")
            
        except Exception as e:
            logger.error(f"智能体停止失败: {e}")
            raise

    async def create_session(self, user_id: str, patient_info: Optional[Dict[str, Any]] = None) -> str:
        """创建新会话"""
        try:
            session_id = str(uuid4())
            current_time = time.time()
            
            session_data = SessionData(
                session_id=session_id,
                user_id=user_id,
                created_at=current_time,
                last_activity=current_time,
                patient_info=patient_info or {}
            )
            
            self.active_sessions[session_id] = session_data
            self.metrics["total_sessions"] += 1
            self.metrics["active_sessions"] = len(self.active_sessions)
            
            logger.info(f"创建新会话: {session_id}, 用户: {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise

    async def end_session(self, session_id: str) -> None:
        """结束会话"""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                session_data.status = "ended"
                del self.active_sessions[session_id]
                
                self.metrics["active_sessions"] = len(self.active_sessions)
                logger.info(f"会话结束: {session_id}")
            
        except Exception as e:
            logger.error(f"结束会话失败: {e}")

    async def process_diagnosis(self, request: DiagnosisRequest) -> DiagnosisResponse:
        """处理诊断请求"""
        start_time = time.time()
        
        try:
            self.status = AgentStatus.PROCESSING
            
            # 验证会话
            if request.session_id not in self.active_sessions:
                raise ValueError(f"无效的会话ID: {request.session_id}")
            
            session_data = self.active_sessions[request.session_id]
            session_data.last_activity = time.time()
            
            # 根据诊断类型处理
            if request.diagnosis_type == DiagnosisType.LOOKING:
                result = await self._process_looking_diagnosis(request)
            elif request.diagnosis_type == DiagnosisType.LISTENING:
                result = await self._process_listening_diagnosis(request)
            elif request.diagnosis_type == DiagnosisType.INQUIRY:
                result = await self._process_inquiry_diagnosis(request)
            elif request.diagnosis_type == DiagnosisType.PALPATION:
                result = await self._process_palpation_diagnosis(request)
            elif request.diagnosis_type == DiagnosisType.CALCULATION:
                result = await self._process_calculation_diagnosis(request)
            else:
                raise ValueError(f"不支持的诊断类型: {request.diagnosis_type}")
            
            # 更新会话历史
            diagnosis_record = {
                "timestamp": time.time(),
                "diagnosis_type": request.diagnosis_type.value,
                "data": request.data,
                "result": result
            }
            session_data.diagnosis_history.append(diagnosis_record)
            
            # 创建响应
            response = DiagnosisResponse(
                message_id=str(uuid4()),
                diagnosis_type=request.diagnosis_type,
                result=result["analysis"],
                confidence=result["confidence"],
                suggestions=result["suggestions"],
                metadata={
                    "session_id": request.session_id,
                    "processing_time": time.time() - start_time,
                    "model_version": self.config.version
                },
                timestamp=time.time()
            )
            
            # 更新指标
            self.metrics["total_diagnoses"] += 1
            self.metrics["successful_diagnoses"] += 1
            
            processing_time = time.time() - start_time
            self._update_average_response_time(processing_time)
            
            self.status = AgentStatus.IDLE
            logger.info(f"诊断完成: {request.diagnosis_type.value}, 耗时: {processing_time:.2f}s")
            
            return response
            
        except Exception as e:
            self.metrics["failed_diagnoses"] += 1
            self.status = AgentStatus.ERROR
            logger.error(f"诊断处理失败: {e}")
            
            # 返回错误响应
            return DiagnosisResponse(
                message_id=str(uuid4()),
                diagnosis_type=request.diagnosis_type,
                result={"error": str(e)},
                confidence=0.0,
                suggestions=["请重试或联系技术支持"],
                metadata={
                    "session_id": request.session_id,
                    "error": True,
                    "processing_time": time.time() - start_time
                },
                timestamp=time.time()
            )

    async def _process_looking_diagnosis(self, request: DiagnosisRequest) -> Dict[str, Any]:
        """处理望诊"""
        data = request.data
        model = self.diagnosis_models[DiagnosisType.LOOKING]
        
        analysis = {
            "face_analysis": {},
            "tongue_analysis": {},
            "spirit_analysis": {}
        }
        
        # 面色分析
        if "face_color" in data:
            face_color = data["face_color"]
            color_mapping = model["face_analysis"]["color_mapping"]
            analysis["face_analysis"]["color_indication"] = color_mapping.get(face_color, "需要进一步观察")
        
        # 舌象分析
        if "tongue_color" in data:
            tongue_color = data["tongue_color"]
            tongue_mapping = model["tongue_analysis"]["tongue_body"]
            analysis["tongue_analysis"]["body_indication"] = tongue_mapping.get(tongue_color, "正常范围")
        
        if "tongue_coating" in data:
            coating = data["tongue_coating"]
            coating_mapping = model["tongue_analysis"]["tongue_coating"]
            analysis["tongue_analysis"]["coating_indication"] = coating_mapping.get(coating, "正常")
        
        # 计算置信度
        confidence = self._calculate_confidence(analysis, "looking")
        
        # 生成建议
        suggestions = self._generate_looking_suggestions(analysis)
        
        return {
            "analysis": analysis,
            "confidence": confidence,
            "suggestions": suggestions
        }

    async def _process_listening_diagnosis(self, request: DiagnosisRequest) -> Dict[str, Any]:
        """处理闻诊"""
        data = request.data
        
        analysis = {
            "voice_analysis": {},
            "breathing_analysis": {},
            "sound_analysis": {}
        }
        
        # 声音分析
        if "voice_quality" in data:
            voice = data["voice_quality"]
            if "低微" in voice:
                analysis["voice_analysis"]["indication"] = "气虚"
            elif "洪亮" in voice:
                analysis["voice_analysis"]["indication"] = "实证"
        
        # 呼吸分析
        if "breathing" in data:
            breathing = data["breathing"]
            if "气短" in breathing:
                analysis["breathing_analysis"]["indication"] = "气虚"
            elif "喘促" in breathing:
                analysis["breathing_analysis"]["indication"] = "肺热"
        
        confidence = self._calculate_confidence(analysis, "listening")
        suggestions = self._generate_listening_suggestions(analysis)
        
        return {
            "analysis": analysis,
            "confidence": confidence,
            "suggestions": suggestions
        }

    async def _process_inquiry_diagnosis(self, request: DiagnosisRequest) -> Dict[str, Any]:
        """处理问诊"""
        data = request.data
        
        analysis = {
            "symptom_analysis": {},
            "duration_analysis": {},
            "trigger_analysis": {}
        }
        
        # 症状分析
        if "symptoms" in data:
            symptoms = data["symptoms"]
            symptom_indications = []
            for symptom in symptoms:
                if "乏力" in symptom:
                    symptom_indications.append("气虚")
                elif "失眠" in symptom:
                    symptom_indications.append("心肾不交")
                elif "食欲不振" in symptom:
                    symptom_indications.append("脾胃虚弱")
            
            analysis["symptom_analysis"]["indications"] = symptom_indications
        
        # 持续时间分析
        if "duration" in data:
            duration = data["duration"]
            if "慢性" in duration or "月" in duration:
                analysis["duration_analysis"]["type"] = "慢性病程"
            else:
                analysis["duration_analysis"]["type"] = "急性病程"
        
        confidence = self._calculate_confidence(analysis, "inquiry")
        suggestions = self._generate_inquiry_suggestions(analysis)
        
        return {
            "analysis": analysis,
            "confidence": confidence,
            "suggestions": suggestions
        }

    async def _process_palpation_diagnosis(self, request: DiagnosisRequest) -> Dict[str, Any]:
        """处理切诊"""
        data = request.data
        
        analysis = {
            "pulse_analysis": {},
            "acupoint_analysis": {}
        }
        
        # 脉象分析
        if "pulse_quality" in data:
            pulse = data["pulse_quality"]
            if "细弱" in pulse:
                analysis["pulse_analysis"]["indication"] = "气血不足"
            elif "洪大" in pulse:
                analysis["pulse_analysis"]["indication"] = "热盛"
            elif "弦" in pulse:
                analysis["pulse_analysis"]["indication"] = "肝郁"
        
        # 穴位敏感性分析
        if "acupoint_sensitivity" in data:
            sensitivity = data["acupoint_sensitivity"]
            if "神门穴" in sensitivity:
                analysis["acupoint_analysis"]["shenmen"] = "心神不宁"
        
        confidence = self._calculate_confidence(analysis, "palpation")
        suggestions = self._generate_palpation_suggestions(analysis)
        
        return {
            "analysis": analysis,
            "confidence": confidence,
            "suggestions": suggestions
        }

    async def _process_calculation_diagnosis(self, request: DiagnosisRequest) -> Dict[str, Any]:
        """处理算诊（综合分析）"""
        session_data = self.active_sessions[request.session_id]
        diagnosis_history = session_data.diagnosis_history
        
        # 综合分析所有诊断结果
        syndrome_scores = {}
        total_confidence = 0
        diagnosis_count = 0
        
        for record in diagnosis_history:
            if record["diagnosis_type"] != "calculation":
                analysis = record["result"]["analysis"]
                confidence = record["result"]["confidence"]
                
                # 根据不同诊法的结果计算证候得分
                if "气虚" in str(analysis):
                    syndrome_scores["qi_deficiency"] = syndrome_scores.get("qi_deficiency", 0) + confidence
                if "血瘀" in str(analysis):
                    syndrome_scores["blood_stasis"] = syndrome_scores.get("blood_stasis", 0) + confidence
                if "痰湿" in str(analysis):
                    syndrome_scores["phlegm_dampness"] = syndrome_scores.get("phlegm_dampness", 0) + confidence
                
                total_confidence += confidence
                diagnosis_count += 1
        
        # 确定主要证候
        if syndrome_scores:
            main_syndrome = max(syndrome_scores, key=syndrome_scores.get)
            syndrome_confidence = syndrome_scores[main_syndrome] / diagnosis_count if diagnosis_count > 0 else 0
        else:
            main_syndrome = "qi_deficiency"  # 默认
            syndrome_confidence = 0.5
        
        # 获取证候信息
        syndrome_info = self.tcm_knowledge["syndromes"].get(main_syndrome, {})
        
        analysis = {
            "tcm_syndrome": syndrome_info.get("name", "气虚证"),
            "constitution": self.tcm_knowledge["constitutions"].get(main_syndrome, "气虚质"),
            "treatment_principle": syndrome_info.get("treatment", "补中益气"),
            "recommended_formula": "四君子汤",
            "health_risk": self._assess_health_risk(syndrome_confidence),
            "syndrome_scores": syndrome_scores
        }
        
        confidence = min(syndrome_confidence, 0.95)  # 最高95%置信度
        suggestions = self._generate_calculation_suggestions(analysis, syndrome_info)
        
        return {
            "analysis": analysis,
            "confidence": confidence,
            "suggestions": suggestions
        }

    def _calculate_confidence(self, analysis: Dict[str, Any], diagnosis_type: str) -> float:
        """计算诊断置信度"""
        base_confidence = 0.7
        
        # 根据分析结果的完整性调整置信度
        non_empty_fields = sum(1 for value in analysis.values() if value)
        total_fields = len(analysis)
        
        completeness_factor = non_empty_fields / total_fields if total_fields > 0 else 0
        confidence = base_confidence * (0.5 + 0.5 * completeness_factor)
        
        return min(confidence, 0.95)

    def _assess_health_risk(self, confidence: float) -> str:
        """评估健康风险等级"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        else:
            return "low"

    def _generate_looking_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成望诊建议"""
        suggestions = []
        
        if "气虚" in str(analysis):
            suggestions.append("建议补气养血，可考虑四君子汤调理")
        if "血瘀" in str(analysis):
            suggestions.append("建议活血化瘀，注意情志调节")
        
        suggestions.append("建议结合其他诊法进行综合分析")
        return suggestions

    def _generate_listening_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成闻诊建议"""
        suggestions = []
        
        if "气虚" in str(analysis):
            suggestions.append("声音低微提示气虚，建议补气")
        
        suggestions.append("建议进行问诊了解详细症状")
        return suggestions

    def _generate_inquiry_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成问诊建议"""
        suggestions = []
        
        if "气虚" in str(analysis):
            suggestions.append("症状提示气虚证，建议补中益气")
        if "脾胃虚弱" in str(analysis):
            suggestions.append("脾胃功能需要调理，注意饮食规律")
        
        suggestions.append("建议进行切诊验证脉象")
        return suggestions

    def _generate_palpation_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成切诊建议"""
        suggestions = []
        
        if "气血不足" in str(analysis):
            suggestions.append("脉象提示气血不足，建议补气养血")
        
        suggestions.append("建议进行综合算诊分析")
        return suggestions

    def _generate_calculation_suggestions(self, analysis: Dict[str, Any], syndrome_info: Dict[str, Any]) -> List[str]:
        """生成算诊建议"""
        suggestions = []
        
        syndrome_name = analysis.get("tcm_syndrome", "")
        treatment = analysis.get("treatment_principle", "")
        
        suggestions.append(f"诊断为{syndrome_name}，治疗原则：{treatment}")
        suggestions.append(f"推荐方剂：{analysis.get('recommended_formula', '')}")
        suggestions.append("建议配合生活调理和适当运动")
        suggestions.append("定期复诊，观察疗效")
        
        return suggestions

    def _update_average_response_time(self, processing_time: float) -> None:
        """更新平均响应时间"""
        current_avg = self.metrics["average_response_time"]
        total_diagnoses = self.metrics["total_diagnoses"]
        
        if total_diagnoses == 1:
            self.metrics["average_response_time"] = processing_time
        else:
            self.metrics["average_response_time"] = (current_avg * (total_diagnoses - 1) + processing_time) / total_diagnoses

    async def _session_cleanup_task(self) -> None:
        """会话清理任务"""
        while self.status != AgentStatus.OFFLINE:
            try:
                current_time = time.time()
                expired_sessions = []
                
                for session_id, session_data in self.active_sessions.items():
                    if current_time - session_data.last_activity > self.config.session_timeout:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self.end_session(session_id)
                    logger.info(f"清理过期会话: {session_id}")
                
                await asyncio.sleep(300)  # 每5分钟检查一次
                
            except Exception as e:
                logger.error(f"会话清理任务错误: {e}")
                await asyncio.sleep(60)

    async def _metrics_update_task(self) -> None:
        """指标更新任务"""
        while self.status != AgentStatus.OFFLINE:
            try:
                self.metrics["uptime"] = time.time() - self.start_time
                await asyncio.sleep(60)  # 每分钟更新一次
                
            except Exception as e:
                logger.error(f"指标更新任务错误: {e}")
                await asyncio.sleep(60)

    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "agent_id": self.config.agent_id,
            "name": self.config.name,
            "status": self.status.value,
            "version": self.config.version,
            "uptime": time.time() - self.start_time,
            "active_sessions": len(self.active_sessions),
            "metrics": self.metrics.copy()
        }

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        if session_id not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[session_id]
        return {
            "session_id": session_data.session_id,
            "user_id": session_data.user_id,
            "created_at": session_data.created_at,
            "last_activity": session_data.last_activity,
            "status": session_data.status,
            "diagnosis_count": len(session_data.diagnosis_history),
            "patient_info": session_data.patient_info
        }

# 全局智能体实例
_agent_manager: Optional[XiaoaiAgentManager] = None

async def get_agent_manager() -> XiaoaiAgentManager:
    """获取智能体管理器实例"""
    global _agent_manager
    
    if _agent_manager is None:
        config = AgentConfig()
        _agent_manager = XiaoaiAgentManager(config)
        await _agent_manager.start()
    
    return _agent_manager

async def shutdown_agent_manager() -> None:
    """关闭智能体管理器"""
    global _agent_manager
    
    if _agent_manager is not None:
        await _agent_manager.stop()
        _agent_manager = None
