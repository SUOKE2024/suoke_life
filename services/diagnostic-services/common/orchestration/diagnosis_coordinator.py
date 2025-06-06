"""
diagnosis_coordinator - 索克生活项目模块
"""

from ..communication.service_client import get_diagnosis_client
from ..config.settings import get_settings
from ..database.manager import get_data_access
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import logging
import numpy as np
import time

"""
综合诊断协调器

统一协调五诊服务，提供完整的中医诊断流程和结果整合，
支持并行分析、结果融合、置信度评估等功能。
"""



logger = logging.getLogger(__name__)

class DiagnosisStage(Enum):
    """诊断阶段"""
    INITIALIZATION = "initialization"
    DATA_COLLECTION = "data_collection"
    PARALLEL_ANALYSIS = "parallel_analysis"
    RESULT_INTEGRATION = "result_integration"
    CONFIDENCE_EVALUATION = "confidence_evaluation"
    FINAL_DIAGNOSIS = "final_diagnosis"
    COMPLETED = "completed"

class DiagnosisType(Enum):
    """诊断类型"""
    LOOK = "look"
    LISTEN = "listen"
    INQUIRY = "inquiry"
    PALPATION = "palpation"
    CALCULATION = "calculation"

@dataclass
class DiagnosisInput:
    """诊断输入数据"""
    patient_id: str
    session_id: str
    
    # 五诊数据
    look_data: Optional[Dict[str, Any]] = None
    listen_data: Optional[Dict[str, Any]] = None
    inquiry_data: Optional[Dict[str, Any]] = None
    palpation_data: Optional[Dict[str, Any]] = None
    calculation_data: Optional[Dict[str, Any]] = None
    
    # 配置
    enable_parallel: bool = True
    timeout: int = 300  # 秒
    min_confidence: float = 0.6

@dataclass
class DiagnosisResult:
    """单项诊断结果"""
    diagnosis_type: DiagnosisType
    tcm_diagnosis: str
    syndrome_pattern: str
    confidence_score: float
    analysis_result: Dict[str, Any]
    processing_time: float
    error_message: Optional[str] = None

@dataclass
class ComprehensiveDiagnosisResult:
    """综合诊断结果"""
    session_id: str
    patient_id: str
    
    # 单项结果
    individual_results: Dict[DiagnosisType, DiagnosisResult] = field(default_factory=dict)
    
    # 综合结果
    final_diagnosis: str = ""
    primary_syndrome: str = ""
    secondary_syndromes: List[str] = field(default_factory=list)
    overall_confidence: float = 0.0
    
    # 治疗建议
    treatment_principles: List[str] = field(default_factory=list)
    herbal_formula: Optional[str] = None
    acupoint_prescription: List[str] = field(default_factory=list)
    lifestyle_advice: List[str] = field(default_factory=list)
    
    # 元数据
    diagnosis_date: datetime = field(default_factory=datetime.utcnow)
    total_processing_time: float = 0.0
    completed_stages: List[DiagnosisStage] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "patient_id": self.patient_id,
            "individual_results": {
                k.value: {
                    "tcm_diagnosis": v.tcm_diagnosis,
                    "syndrome_pattern": v.syndrome_pattern,
                    "confidence_score": v.confidence_score,
                    "processing_time": v.processing_time,
                    "error_message": v.error_message
                }
                for k, v in self.individual_results.items()
            },
            "final_diagnosis": self.final_diagnosis,
            "primary_syndrome": self.primary_syndrome,
            "secondary_syndromes": self.secondary_syndromes,
            "overall_confidence": self.overall_confidence,
            "treatment_principles": self.treatment_principles,
            "herbal_formula": self.herbal_formula,
            "acupoint_prescription": self.acupoint_prescription,
            "lifestyle_advice": self.lifestyle_advice,
            "diagnosis_date": self.diagnosis_date.isoformat(),
            "total_processing_time": self.total_processing_time,
            "completed_stages": [stage.value for stage in self.completed_stages]
        }

class SyndromePatternMatcher:
    """证候模式匹配器"""
    
    def __init__(self):
        # 中医证候模式知识库
        self.syndrome_patterns = {
            "气虚证": {
                "keywords": ["气短", "乏力", "懒言", "自汗", "脉弱"],
                "look_signs": ["面色萎黄", "神疲"],
                "listen_signs": ["声音低微", "气息微弱"],
                "inquiry_signs": ["疲倦", "食欲不振"],
                "palpation_signs": ["脉虚弱"],
                "weight": 1.0
            },
            "血虚证": {
                "keywords": ["面色苍白", "头晕", "心悸", "失眠"],
                "look_signs": ["面色无华", "唇甲色淡"],
                "listen_signs": ["心悸"],
                "inquiry_signs": ["头晕", "失眠", "健忘"],
                "palpation_signs": ["脉细弱"],
                "weight": 1.0
            },
            "阴虚证": {
                "keywords": ["潮热", "盗汗", "五心烦热", "口干"],
                "look_signs": ["颧红", "舌红少苔"],
                "listen_signs": ["声音嘶哑"],
                "inquiry_signs": ["潮热", "盗汗", "口干"],
                "palpation_signs": ["脉细数"],
                "weight": 1.0
            },
            "阳虚证": {
                "keywords": ["畏寒", "肢冷", "精神萎靡", "腰膝酸软"],
                "look_signs": ["面色㿠白", "舌淡胖"],
                "listen_signs": ["声音低沉"],
                "inquiry_signs": ["畏寒", "肢冷", "腰膝酸软"],
                "palpation_signs": ["脉沉迟"],
                "weight": 1.0
            },
            "气滞证": {
                "keywords": ["胸闷", "胁痛", "情志不舒", "善太息"],
                "look_signs": ["面色晦暗"],
                "listen_signs": ["善太息"],
                "inquiry_signs": ["胸闷", "胁痛", "情绪不稳"],
                "palpation_signs": ["脉弦"],
                "weight": 1.0
            },
            "血瘀证": {
                "keywords": ["刺痛", "痛处固定", "面色晦暗", "肌肤甲错"],
                "look_signs": ["面色晦暗", "舌质紫暗"],
                "listen_signs": [],
                "inquiry_signs": ["刺痛", "痛处固定"],
                "palpation_signs": ["脉涩"],
                "weight": 1.0
            },
            "痰湿证": {
                "keywords": ["身重", "胸闷", "痰多", "食欲不振"],
                "look_signs": ["形体肥胖", "舌苔厚腻"],
                "listen_signs": ["痰鸣"],
                "inquiry_signs": ["身重", "胸闷", "痰多"],
                "palpation_signs": ["脉滑"],
                "weight": 1.0
            }
        }
    
    def match_syndrome_patterns(self, results: Dict[DiagnosisType, DiagnosisResult]) -> List[Tuple[str, float]]:
        """匹配证候模式"""
        pattern_scores = {}
        
        for pattern_name, pattern_data in self.syndrome_patterns.items():
            score = self._calculate_pattern_score(pattern_data, results)
            if score > 0:
                pattern_scores[pattern_name] = score
        
        # 按分数排序
        sorted_patterns = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_patterns
    
    def _calculate_pattern_score(self, pattern_data: Dict[str, Any], results: Dict[DiagnosisType, DiagnosisResult]) -> float:
        """计算证候模式分数"""
        total_score = 0.0
        total_weight = 0.0
        
        # 检查各诊断类型的匹配度
        for diagnosis_type, result in results.items():
            if result.error_message:
                continue
            
            type_score = 0.0
            type_weight = result.confidence_score
            
            if diagnosis_type == DiagnosisType.LOOK:
                type_score = self._match_signs(pattern_data.get("look_signs", []), result.analysis_result)
            elif diagnosis_type == DiagnosisType.LISTEN:
                type_score = self._match_signs(pattern_data.get("listen_signs", []), result.analysis_result)
            elif diagnosis_type == DiagnosisType.INQUIRY:
                type_score = self._match_signs(pattern_data.get("inquiry_signs", []), result.analysis_result)
            elif diagnosis_type == DiagnosisType.PALPATION:
                type_score = self._match_signs(pattern_data.get("palpation_signs", []), result.analysis_result)
            
            total_score += type_score * type_weight
            total_weight += type_weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _match_signs(self, pattern_signs: List[str], analysis_result: Dict[str, Any]) -> float:
        """匹配症状体征"""
        if not pattern_signs:
            return 0.0
        
        matched_count = 0
        total_count = len(pattern_signs)
        
        # 简化的匹配逻辑，实际应该使用更复杂的NLP匹配
        result_text = str(analysis_result).lower()
        
        for sign in pattern_signs:
            if sign.lower() in result_text:
                matched_count += 1
        
        return matched_count / total_count

class TreatmentRecommendationEngine:
    """治疗建议引擎"""
    
    def __init__(self):
        # 治疗原则知识库
        self.treatment_principles = {
            "气虚证": ["补气", "健脾", "益肺"],
            "血虚证": ["补血", "养心", "安神"],
            "阴虚证": ["滋阴", "润燥", "清热"],
            "阳虚证": ["温阳", "补肾", "健脾"],
            "气滞证": ["理气", "疏肝", "解郁"],
            "血瘀证": ["活血", "化瘀", "通络"],
            "痰湿证": ["化痰", "燥湿", "健脾"]
        }
        
        # 方剂知识库
        self.herbal_formulas = {
            "气虚证": "四君子汤",
            "血虚证": "四物汤",
            "阴虚证": "六味地黄丸",
            "阳虚证": "金匮肾气丸",
            "气滞证": "逍遥散",
            "血瘀证": "血府逐瘀汤",
            "痰湿证": "二陈汤"
        }
        
        # 穴位处方知识库
        self.acupoint_prescriptions = {
            "气虚证": ["气海", "关元", "足三里", "脾俞"],
            "血虚证": ["血海", "三阴交", "心俞", "肝俞"],
            "阴虚证": ["太溪", "照海", "肾俞", "太冲"],
            "阳虚证": ["命门", "肾俞", "关元", "神阙"],
            "气滞证": ["太冲", "期门", "膻中", "内关"],
            "血瘀证": ["血海", "膈俞", "三阴交", "合谷"],
            "痰湿证": ["丰隆", "阴陵泉", "脾俞", "中脘"]
        }
        
        # 生活建议知识库
        self.lifestyle_advice = {
            "气虚证": ["适当运动", "规律作息", "避免过劳", "饮食清淡"],
            "血虚证": ["充足睡眠", "营养均衡", "避免熬夜", "适量运动"],
            "阴虚证": ["避免辛辣", "多饮水", "保持心情舒畅", "避免过度劳累"],
            "阳虚证": ["保暖防寒", "温热饮食", "适度运动", "早睡早起"],
            "气滞证": ["保持心情舒畅", "适当运动", "避免情绪激动", "规律作息"],
            "血瘀证": ["适当运动", "避免久坐", "保持心情愉快", "饮食清淡"],
            "痰湿证": ["控制体重", "清淡饮食", "适量运动", "避免油腻"]
        }
    
    def generate_recommendations(self, primary_syndrome: str, secondary_syndromes: List[str]) -> Dict[str, Any]:
        """生成治疗建议"""
        recommendations = {
            "treatment_principles": [],
            "herbal_formula": None,
            "acupoint_prescription": [],
            "lifestyle_advice": []
        }
        
        # 主要证候的治疗建议
        if primary_syndrome in self.treatment_principles:
            recommendations["treatment_principles"].extend(self.treatment_principles[primary_syndrome])
            recommendations["herbal_formula"] = self.herbal_formulas.get(primary_syndrome)
            recommendations["acupoint_prescription"].extend(self.acupoint_prescriptions.get(primary_syndrome, []))
            recommendations["lifestyle_advice"].extend(self.lifestyle_advice.get(primary_syndrome, []))
        
        # 次要证候的治疗建议
        for syndrome in secondary_syndromes:
            if syndrome in self.treatment_principles:
                # 添加部分治疗原则
                additional_principles = self.treatment_principles[syndrome][:2]
                recommendations["treatment_principles"].extend(additional_principles)
                
                # 添加部分穴位
                additional_acupoints = self.acupoint_prescriptions.get(syndrome, [])[:2]
                recommendations["acupoint_prescription"].extend(additional_acupoints)
        
        # 去重
        recommendations["treatment_principles"] = list(set(recommendations["treatment_principles"]))
        recommendations["acupoint_prescription"] = list(set(recommendations["acupoint_prescription"]))
        recommendations["lifestyle_advice"] = list(set(recommendations["lifestyle_advice"]))
        
        return recommendations

class DiagnosisCoordinator:
    """诊断协调器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.syndrome_matcher = SyndromePatternMatcher()
        self.treatment_engine = TreatmentRecommendationEngine()
        self.diagnosis_client = None
        self.data_access = None
    
    async def initialize(self):
        """初始化协调器"""
        self.diagnosis_client = await get_diagnosis_client()
        self.data_access = await get_data_access()
        logger.info("诊断协调器初始化完成")
    
    async def comprehensive_diagnosis(self, diagnosis_input: DiagnosisInput) -> ComprehensiveDiagnosisResult:
        """综合诊断"""
        start_time = time.time()
        
        result = ComprehensiveDiagnosisResult(
            session_id=diagnosis_input.session_id,
            patient_id=diagnosis_input.patient_id
        )
        
        try:
            # 阶段1：初始化
            await self._stage_initialization(diagnosis_input, result)
            
            # 阶段2：数据收集验证
            await self._stage_data_collection(diagnosis_input, result)
            
            # 阶段3：并行分析
            await self._stage_parallel_analysis(diagnosis_input, result)
            
            # 阶段4：结果整合
            await self._stage_result_integration(diagnosis_input, result)
            
            # 阶段5：置信度评估
            await self._stage_confidence_evaluation(diagnosis_input, result)
            
            # 阶段6：最终诊断
            await self._stage_final_diagnosis(diagnosis_input, result)
            
            # 完成
            result.completed_stages.append(DiagnosisStage.COMPLETED)
            result.total_processing_time = time.time() - start_time
            
            # 保存结果
            await self._save_diagnosis_result(result)
            
            logger.info(f"综合诊断完成: {result.session_id}, 耗时: {result.total_processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"综合诊断失败: {e}")
            result.final_diagnosis = f"诊断过程出现错误: {str(e)}"
            result.total_processing_time = time.time() - start_time
        
        return result
    
    async def _stage_initialization(self, diagnosis_input: DiagnosisInput, result: ComprehensiveDiagnosisResult):
        """阶段1：初始化"""
        logger.info(f"开始初始化阶段: {diagnosis_input.session_id}")
        
        # 验证输入数据
        if not diagnosis_input.patient_id or not diagnosis_input.session_id:
            raise ValueError("患者ID和会话ID不能为空")
        
        # 检查至少有一种诊断数据
        has_data = any([
            diagnosis_input.look_data,
            diagnosis_input.listen_data,
            diagnosis_input.inquiry_data,
            diagnosis_input.palpation_data,
            diagnosis_input.calculation_data
        ])
        
        if not has_data:
            raise ValueError("至少需要提供一种诊断数据")
        
        result.completed_stages.append(DiagnosisStage.INITIALIZATION)
        logger.info(f"初始化阶段完成: {diagnosis_input.session_id}")
    
    async def _stage_data_collection(self, diagnosis_input: DiagnosisInput, result: ComprehensiveDiagnosisResult):
        """阶段2：数据收集验证"""
        logger.info(f"开始数据收集阶段: {diagnosis_input.session_id}")
        
        # 这里可以添加数据质量检查、预处理等逻辑
        # 例如：图像质量检查、音频降噪、文本清理等
        
        result.completed_stages.append(DiagnosisStage.DATA_COLLECTION)
        logger.info(f"数据收集阶段完成: {diagnosis_input.session_id}")
    
    async def _stage_parallel_analysis(self, diagnosis_input: DiagnosisInput, result: ComprehensiveDiagnosisResult):
        """阶段3：并行分析"""
        logger.info(f"开始并行分析阶段: {diagnosis_input.session_id}")
        
        # 创建分析任务
        tasks = []
        
        if diagnosis_input.look_data:
            tasks.append(self._analyze_look(diagnosis_input.look_data))
        
        if diagnosis_input.listen_data:
            tasks.append(self._analyze_listen(diagnosis_input.listen_data))
        
        if diagnosis_input.inquiry_data:
            tasks.append(self._analyze_inquiry(diagnosis_input.inquiry_data))
        
        if diagnosis_input.palpation_data:
            tasks.append(self._analyze_palpation(diagnosis_input.palpation_data))
        
        if diagnosis_input.calculation_data:
            tasks.append(self._analyze_calculation(diagnosis_input.calculation_data))
        
        # 并行执行分析
        if diagnosis_input.enable_parallel:
            analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            analysis_results = []
            for task in tasks:
                try:
                    result_item = await task
                    analysis_results.append(result_item)
                except Exception as e:
                    analysis_results.append(e)
        
        # 处理分析结果
        for analysis_result in analysis_results:
            if isinstance(analysis_result, Exception):
                logger.error(f"分析任务失败: {analysis_result}")
                continue
            
            if isinstance(analysis_result, DiagnosisResult):
                result.individual_results[analysis_result.diagnosis_type] = analysis_result
        
        result.completed_stages.append(DiagnosisStage.PARALLEL_ANALYSIS)
        logger.info(f"并行分析阶段完成: {diagnosis_input.session_id}, 完成 {len(result.individual_results)} 项分析")
    
    async def _stage_result_integration(self, diagnosis_input: DiagnosisInput, result: ComprehensiveDiagnosisResult):
        """阶段4：结果整合"""
        logger.info(f"开始结果整合阶段: {diagnosis_input.session_id}")
        
        if not result.individual_results:
            raise ValueError("没有可用的分析结果进行整合")
        
        # 证候模式匹配
        syndrome_patterns = self.syndrome_matcher.match_syndrome_patterns(result.individual_results)
        
        if syndrome_patterns:
            # 主要证候（得分最高）
            result.primary_syndrome = syndrome_patterns[0][0]
            
            # 次要证候（得分超过阈值的其他证候）
            threshold = 0.3
            result.secondary_syndromes = [
                pattern for pattern, score in syndrome_patterns[1:]
                if score > threshold
            ]
        
        result.completed_stages.append(DiagnosisStage.RESULT_INTEGRATION)
        logger.info(f"结果整合阶段完成: {diagnosis_input.session_id}")
    
    async def _stage_confidence_evaluation(self, diagnosis_input: DiagnosisInput, result: ComprehensiveDiagnosisResult):
        """阶段5：置信度评估"""
        logger.info(f"开始置信度评估阶段: {diagnosis_input.session_id}")
        
        # 计算整体置信度
        confidence_scores = [
            res.confidence_score for res in result.individual_results.values()
            if res.error_message is None
        ]
        
        if confidence_scores:
            # 使用加权平均计算整体置信度
            weights = [1.0] * len(confidence_scores)  # 可以根据诊断类型调整权重
            result.overall_confidence = np.average(confidence_scores, weights=weights)
        else:
            result.overall_confidence = 0.0
        
        result.completed_stages.append(DiagnosisStage.CONFIDENCE_EVALUATION)
        logger.info(f"置信度评估阶段完成: {diagnosis_input.session_id}, 整体置信度: {result.overall_confidence:.2f}")
    
    async def _stage_final_diagnosis(self, diagnosis_input: DiagnosisInput, result: ComprehensiveDiagnosisResult):
        """阶段6：最终诊断"""
        logger.info(f"开始最终诊断阶段: {diagnosis_input.session_id}")
        
        # 生成最终诊断
        if result.primary_syndrome:
            result.final_diagnosis = result.primary_syndrome
            
            if result.secondary_syndromes:
                result.final_diagnosis += f"，兼有{', '.join(result.secondary_syndromes)}"
        else:
            result.final_diagnosis = "证候不明，建议进一步检查"
        
        # 生成治疗建议
        if result.primary_syndrome:
            recommendations = self.treatment_engine.generate_recommendations(
                result.primary_syndrome,
                result.secondary_syndromes
            )
            
            result.treatment_principles = recommendations["treatment_principles"]
            result.herbal_formula = recommendations["herbal_formula"]
            result.acupoint_prescription = recommendations["acupoint_prescription"]
            result.lifestyle_advice = recommendations["lifestyle_advice"]
        
        result.completed_stages.append(DiagnosisStage.FINAL_DIAGNOSIS)
        logger.info(f"最终诊断阶段完成: {diagnosis_input.session_id}")
    
    async def _analyze_look(self, look_data: Dict[str, Any]) -> DiagnosisResult:
        """望诊分析"""
        start_time = time.time()
        
        try:
            # 调用望诊服务
            analysis_result = await self.diagnosis_client.analyze_look(
                image_data=look_data.get("image_data", b""),
                analysis_type=look_data.get("analysis_type", "face")
            )
            
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.LOOK,
                tcm_diagnosis=analysis_result.get("tcm_diagnosis", ""),
                syndrome_pattern=analysis_result.get("syndrome_pattern", ""),
                confidence_score=analysis_result.get("confidence_score", 0.0),
                analysis_result=analysis_result,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.LOOK,
                tcm_diagnosis="",
                syndrome_pattern="",
                confidence_score=0.0,
                analysis_result={},
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _analyze_listen(self, listen_data: Dict[str, Any]) -> DiagnosisResult:
        """闻诊分析"""
        start_time = time.time()
        
        try:
            analysis_result = await self.diagnosis_client.analyze_listen(
                audio_data=listen_data.get("audio_data", b""),
                analysis_type=listen_data.get("analysis_type", "voice")
            )
            
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.LISTEN,
                tcm_diagnosis=analysis_result.get("tcm_diagnosis", ""),
                syndrome_pattern=analysis_result.get("syndrome_pattern", ""),
                confidence_score=analysis_result.get("confidence_score", 0.0),
                analysis_result=analysis_result,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.LISTEN,
                tcm_diagnosis="",
                syndrome_pattern="",
                confidence_score=0.0,
                analysis_result={},
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _analyze_inquiry(self, inquiry_data: Dict[str, Any]) -> DiagnosisResult:
        """问诊分析"""
        start_time = time.time()
        
        try:
            analysis_result = await self.diagnosis_client.analyze_inquiry(
                dialogue_data=inquiry_data.get("dialogue_data", [])
            )
            
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.INQUIRY,
                tcm_diagnosis=analysis_result.get("tcm_diagnosis", ""),
                syndrome_pattern=analysis_result.get("syndrome_pattern", ""),
                confidence_score=analysis_result.get("confidence_score", 0.0),
                analysis_result=analysis_result,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.INQUIRY,
                tcm_diagnosis="",
                syndrome_pattern="",
                confidence_score=0.0,
                analysis_result={},
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _analyze_palpation(self, palpation_data: Dict[str, Any]) -> DiagnosisResult:
        """切诊分析"""
        start_time = time.time()
        
        try:
            analysis_result = await self.diagnosis_client.analyze_palpation(
                sensor_data=palpation_data
            )
            
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.PALPATION,
                tcm_diagnosis=analysis_result.get("tcm_diagnosis", ""),
                syndrome_pattern=analysis_result.get("syndrome_pattern", ""),
                confidence_score=analysis_result.get("confidence_score", 0.0),
                analysis_result=analysis_result,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.PALPATION,
                tcm_diagnosis="",
                syndrome_pattern="",
                confidence_score=0.0,
                analysis_result={},
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _analyze_calculation(self, calculation_data: Dict[str, Any]) -> DiagnosisResult:
        """算诊分析"""
        start_time = time.time()
        
        try:
            analysis_result = await self.diagnosis_client.analyze_calculation(
                birth_info=calculation_data
            )
            
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.CALCULATION,
                tcm_diagnosis=analysis_result.get("tcm_diagnosis", ""),
                syndrome_pattern=analysis_result.get("syndrome_pattern", ""),
                confidence_score=analysis_result.get("confidence_score", 0.0),
                analysis_result=analysis_result,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return DiagnosisResult(
                diagnosis_type=DiagnosisType.CALCULATION,
                tcm_diagnosis="",
                syndrome_pattern="",
                confidence_score=0.0,
                analysis_result={},
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _save_diagnosis_result(self, result: ComprehensiveDiagnosisResult):
        """保存诊断结果"""
        try:
            # 保存综合诊断结果
            await self.data_access.save_analysis_result("comprehensive", {
                "session_id": result.session_id,
                "analysis_result": result.to_dict(),
                "tcm_diagnosis": result.final_diagnosis,
                "confidence_score": result.overall_confidence,
                "processing_time": result.total_processing_time
            })
            
            # 保存各项单独结果
            for diagnosis_type, individual_result in result.individual_results.items():
                if individual_result.error_message is None:
                    await self.data_access.save_analysis_result(diagnosis_type.value, {
                        "session_id": result.session_id,
                        "analysis_result": individual_result.analysis_result,
                        "tcm_diagnosis": individual_result.tcm_diagnosis,
                        "confidence_score": individual_result.confidence_score,
                        "processing_time": individual_result.processing_time
                    })
            
            logger.info(f"诊断结果保存成功: {result.session_id}")
            
        except Exception as e:
            logger.error(f"保存诊断结果失败: {e}")

# 全局协调器实例
_coordinator = None

async def get_diagnosis_coordinator() -> DiagnosisCoordinator:
    """获取诊断协调器实例"""
    global _coordinator
    if _coordinator is None:
        _coordinator = DiagnosisCoordinator()
        await _coordinator.initialize()
    return _coordinator 