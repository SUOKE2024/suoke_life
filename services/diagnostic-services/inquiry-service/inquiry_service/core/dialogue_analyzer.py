"""
dialogue_analyzer - 索克生活项目模块
"""

from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any, Set
import asyncio
import jieba
import jieba.posseg as pseg
import logging
import re

"""
问诊智能对话分析器

基于自然语言处理和中医知识图谱，实现智能问诊对话分析功能。
包括症状提取、病情分析、证候辨识等核心功能。
"""


logger = logging.getLogger(__name__)

class SymptomCategory(str, Enum):
    """症状分类"""
    PAIN = "疼痛"
    DIGESTIVE = "消化"
    RESPIRATORY = "呼吸"
    CARDIOVASCULAR = "心血管"
    NEUROLOGICAL = "神经"
    GYNECOLOGICAL = "妇科"
    UROLOGICAL = "泌尿"
    DERMATOLOGICAL = "皮肤"
    EMOTIONAL = "情志"
    SLEEP = "睡眠"
    APPETITE = "食欲"
    TEMPERATURE = "寒热"

@dataclass
class SymptomInfo:
    """症状信息"""
    name: str              # 症状名称
    category: SymptomCategory  # 症状分类
    severity: str          # 严重程度
    duration: str          # 持续时间
    frequency: str         # 发作频率
    triggers: List[str]    # 诱发因素
    relievers: List[str]   # 缓解因素
    associated_symptoms: List[str]  # 伴随症状
    confidence: float      # 识别置信度

@dataclass
class PatientProfile:
    """患者档案"""
    age: Optional[int] = None
    gender: Optional[str] = None
    constitution: Optional[str] = None  # 体质
    medical_history: List[str] = None
    current_medications: List[str] = None
    lifestyle: Dict[str, str] = None

@dataclass
class DialogueAnalysisResult:
    """对话分析结果"""
    extracted_symptoms: List[SymptomInfo]
    patient_profile: PatientProfile
    syndrome_patterns: List[str]  # 证候模式
    tcm_diagnosis: str           # 中医诊断
    severity_assessment: str     # 严重程度评估
    recommendations: List[str]   # 建议
    confidence: float

class SymptomExtractor:
    """症状提取器"""
    
    def __init__(self):
        # 症状词典
        self.symptom_dict = {
            "疼痛": ["疼", "痛", "酸痛", "胀痛", "刺痛", "隐痛", "绞痛", "钝痛", "剧痛"],
            "头痛": ["头疼", "头痛", "偏头痛", "头胀", "头晕"],
            "胸痛": ["胸疼", "胸痛", "胸闷", "心痛", "胸部不适"],
            "腹痛": ["肚子疼", "腹痛", "胃痛", "肚痛", "腹部疼痛"],
            "咳嗽": ["咳嗽", "咳", "干咳", "咳痰", "咳血"],
            "发热": ["发烧", "发热", "高烧", "低烧", "体温高"],
            "乏力": ["乏力", "疲劳", "无力", "疲倦", "精神不振"],
            "失眠": ["失眠", "睡不着", "入睡困难", "早醒", "多梦"],
            "食欲不振": ["不想吃", "没胃口", "食欲差", "不思饮食"],
            "恶心": ["恶心", "想吐", "反胃", "呕吐"],
            "腹泻": ["拉肚子", "腹泻", "大便稀", "水样便"],
            "便秘": ["便秘", "大便干", "排便困难", "几天不大便"],
            "心悸": ["心慌", "心跳快", "心悸", "心律不齐"],
            "气短": ["气短", "呼吸困难", "喘气", "气促"],
            "眩晕": ["头晕", "眩晕", "天旋地转", "站不稳"]
        }
        
        # 程度词典
        self.severity_dict = {
            "轻微": ["轻微", "稍微", "一点", "有点", "略微"],
            "中等": ["中等", "一般", "还可以", "不算严重"],
            "严重": ["严重", "厉害", "很", "非常", "剧烈", "难受"]
        }
        
        # 时间词典
        self.duration_dict = {
            "急性": ["刚才", "刚刚", "突然", "今天", "昨天"],
            "亚急性": ["几天", "一周", "这周", "最近"],
            "慢性": ["很久", "长期", "一直", "好几个月", "半年", "一年"]
        }
        
        # 频率词典
        self.frequency_dict = {
            "偶尔": ["偶尔", "有时", "偶然", "不常"],
            "经常": ["经常", "常常", "总是", "老是"],
            "持续": ["一直", "持续", "不停", "连续"]
        }
    
    def extract_symptoms(self, text: str) -> List[SymptomInfo]:
        """从文本中提取症状信息"""
        symptoms = []
        
        # 分词和词性标注
        words = pseg.cut(text)
        word_list = [(word, flag) for word, flag in words]
        
        # 提取症状
        for symptom_name, keywords in self.symptom_dict.items():
            for keyword in keywords:
                if keyword in text:
                    symptom_info = self._analyze_symptom_context(
                        text, keyword, symptom_name, word_list
                    )
                    if symptom_info:
                        symptoms.append(symptom_info)
                        break  # 避免重复提取同一症状
        
        return symptoms
    
    def _analyze_symptom_context(self, text: str, keyword: str, symptom_name: str, 
                               word_list: List[Tuple[str, str]]) -> Optional[SymptomInfo]:
        """分析症状上下文"""
        # 找到关键词位置
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return None
        
        # 提取上下文
        context_start = max(0, keyword_pos - 20)
        context_end = min(len(text), keyword_pos + len(keyword) + 20)
        context = text[context_start:context_end]
        
        # 分析严重程度
        severity = self._extract_severity(context)
        
        # 分析持续时间
        duration = self._extract_duration(context)
        
        # 分析频率
        frequency = self._extract_frequency(context)
        
        # 确定症状分类
        category = self._categorize_symptom(symptom_name)
        
        return SymptomInfo(
            name=symptom_name,
            category=category,
            severity=severity,
            duration=duration,
            frequency=frequency,
            triggers=[],
            relievers=[],
            associated_symptoms=[],
            confidence=0.8
        )
    
    def _extract_severity(self, context: str) -> str:
        """提取严重程度"""
        for severity, keywords in self.severity_dict.items():
            for keyword in keywords:
                if keyword in context:
                    return severity
        return "中等"
    
    def _extract_duration(self, context: str) -> str:
        """提取持续时间"""
        for duration, keywords in self.duration_dict.items():
            for keyword in keywords:
                if keyword in context:
                    return duration
        return "未知"
    
    def _extract_frequency(self, context: str) -> str:
        """提取频率"""
        for frequency, keywords in self.frequency_dict.items():
            for keyword in keywords:
                if keyword in context:
                    return frequency
        return "未知"
    
    def _categorize_symptom(self, symptom_name: str) -> SymptomCategory:
        """症状分类"""
        category_mapping = {
            "疼痛": SymptomCategory.PAIN,
            "头痛": SymptomCategory.NEUROLOGICAL,
            "胸痛": SymptomCategory.CARDIOVASCULAR,
            "腹痛": SymptomCategory.DIGESTIVE,
            "咳嗽": SymptomCategory.RESPIRATORY,
            "发热": SymptomCategory.TEMPERATURE,
            "乏力": SymptomCategory.NEUROLOGICAL,
            "失眠": SymptomCategory.SLEEP,
            "食欲不振": SymptomCategory.APPETITE,
            "恶心": SymptomCategory.DIGESTIVE,
            "腹泻": SymptomCategory.DIGESTIVE,
            "便秘": SymptomCategory.DIGESTIVE,
            "心悸": SymptomCategory.CARDIOVASCULAR,
            "气短": SymptomCategory.RESPIRATORY,
            "眩晕": SymptomCategory.NEUROLOGICAL
        }
        
        return category_mapping.get(symptom_name, SymptomCategory.PAIN)

class PatientProfileExtractor:
    """患者档案提取器"""
    
    def __init__(self):
        # 年龄模式
        self.age_pattern = re.compile(r'(\d+)[岁年]')
        
        # 性别词典
        self.gender_dict = {
            "男": ["男", "男性", "先生", "男士"],
            "女": ["女", "女性", "女士", "小姐", "太太"]
        }
        
        # 体质词典
        self.constitution_dict = {
            "平和质": ["身体好", "很健康", "没什么毛病"],
            "气虚质": ["容易累", "气短", "声音小", "容易感冒"],
            "阳虚质": ["怕冷", "手脚冰凉", "精神不振"],
            "阴虚质": ["怕热", "口干", "失眠", "心烦"],
            "痰湿质": ["肥胖", "容易困倦", "胸闷", "痰多"],
            "湿热质": ["面部油腻", "口苦", "大便黏腻"],
            "血瘀质": ["面色晦暗", "容易健忘", "皮肤粗糙"],
            "气郁质": ["情绪低落", "容易紧张", "胸闷不舒"],
            "特禀质": ["过敏", "哮喘", "荨麻疹"]
        }
    
    def extract_profile(self, dialogue_history: List[str]) -> PatientProfile:
        """从对话历史中提取患者档案"""
        full_text = " ".join(dialogue_history)
        
        # 提取年龄
        age = self._extract_age(full_text)
        
        # 提取性别
        gender = self._extract_gender(full_text)
        
        # 提取体质
        constitution = self._extract_constitution(full_text)
        
        # 提取病史
        medical_history = self._extract_medical_history(full_text)
        
        # 提取用药情况
        medications = self._extract_medications(full_text)
        
        # 提取生活方式
        lifestyle = self._extract_lifestyle(full_text)
        
        return PatientProfile(
            age=age,
            gender=gender,
            constitution=constitution,
            medical_history=medical_history,
            current_medications=medications,
            lifestyle=lifestyle
        )
    
    def _extract_age(self, text: str) -> Optional[int]:
        """提取年龄"""
        match = self.age_pattern.search(text)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_gender(self, text: str) -> Optional[str]:
        """提取性别"""
        for gender, keywords in self.gender_dict.items():
            for keyword in keywords:
                if keyword in text:
                    return gender
        return None
    
    def _extract_constitution(self, text: str) -> Optional[str]:
        """提取体质"""
        constitution_scores = defaultdict(int)
        
        for constitution, keywords in self.constitution_dict.items():
            for keyword in keywords:
                if keyword in text:
                    constitution_scores[constitution] += 1
        
        if constitution_scores:
            return max(constitution_scores, key=constitution_scores.get)
        return None
    
    def _extract_medical_history(self, text: str) -> List[str]:
        """提取病史"""
        history_keywords = ["以前", "之前", "曾经", "历史", "得过", "患过"]
        disease_keywords = ["高血压", "糖尿病", "心脏病", "肝病", "肾病", "癌症", "手术"]
        
        medical_history = []
        for keyword in history_keywords:
            if keyword in text:
                # 在关键词附近查找疾病名称
                keyword_pos = text.find(keyword)
                context = text[keyword_pos:keyword_pos+50]
                
                for disease in disease_keywords:
                    if disease in context:
                        medical_history.append(disease)
        
        return list(set(medical_history))
    
    def _extract_medications(self, text: str) -> List[str]:
        """提取用药情况"""
        med_keywords = ["吃药", "服药", "用药", "药物", "治疗"]
        medications = []
        
        for keyword in med_keywords:
            if keyword in text:
                medications.append("正在用药")
                break
        
        return medications
    
    def _extract_lifestyle(self, text: str) -> Dict[str, str]:
        """提取生活方式"""
        lifestyle = {}
        
        # 睡眠
        if any(word in text for word in ["熬夜", "晚睡", "失眠"]):
            lifestyle["睡眠"] = "不规律"
        elif any(word in text for word in ["早睡", "睡眠好"]):
            lifestyle["睡眠"] = "规律"
        
        # 饮食
        if any(word in text for word in ["不规律", "暴饮暴食", "节食"]):
            lifestyle["饮食"] = "不规律"
        elif any(word in text for word in ["规律", "健康饮食"]):
            lifestyle["饮食"] = "规律"
        
        # 运动
        if any(word in text for word in ["不运动", "久坐", "缺乏运动"]):
            lifestyle["运动"] = "缺乏"
        elif any(word in text for word in ["运动", "锻炼", "健身"]):
            lifestyle["运动"] = "规律"
        
        return lifestyle

class TCMDiagnosisEngine:
    """中医诊断引擎"""
    
    def __init__(self):
        # 证候模式库
        self.syndrome_patterns = {
            "气虚证": {
                "symptoms": ["乏力", "气短", "声音小", "容易感冒"],
                "severity": ["轻微", "中等"],
                "constitution": "气虚质"
            },
            "阳虚证": {
                "symptoms": ["怕冷", "乏力", "腹泻", "夜尿多"],
                "severity": ["中等", "严重"],
                "constitution": "阳虚质"
            },
            "阴虚证": {
                "symptoms": ["怕热", "口干", "失眠", "心烦"],
                "severity": ["中等", "严重"],
                "constitution": "阴虚质"
            },
            "血瘀证": {
                "symptoms": ["疼痛", "面色晦暗", "健忘"],
                "severity": ["中等", "严重"],
                "constitution": "血瘀质"
            },
            "痰湿证": {
                "symptoms": ["胸闷", "痰多", "困倦", "食欲不振"],
                "severity": ["轻微", "中等"],
                "constitution": "痰湿质"
            },
            "湿热证": {
                "symptoms": ["口苦", "大便黏腻", "小便黄", "烦躁"],
                "severity": ["中等", "严重"],
                "constitution": "湿热质"
            },
            "肝郁证": {
                "symptoms": ["胸闷", "情绪低落", "易怒", "失眠"],
                "severity": ["轻微", "中等"],
                "constitution": "气郁质"
            }
        }
        
        # 脏腑辨证
        self.organ_patterns = {
            "心": ["心悸", "失眠", "健忘", "胸痛"],
            "肝": ["胸闷", "易怒", "头痛", "眩晕"],
            "脾": ["食欲不振", "腹胀", "乏力", "腹泻"],
            "肺": ["咳嗽", "气短", "容易感冒"],
            "肾": ["腰痛", "夜尿多", "耳鸣", "怕冷"]
        }
    
    def analyze_syndrome(self, symptoms: List[SymptomInfo], 
                        patient_profile: PatientProfile) -> Tuple[List[str], str]:
        """分析证候模式"""
        syndrome_scores = defaultdict(float)
        
        # 基于症状匹配
        for symptom in symptoms:
            for syndrome, pattern in self.syndrome_patterns.items():
                if symptom.name in pattern["symptoms"]:
                    score = 1.0
                    
                    # 严重程度加权
                    if symptom.severity in pattern.get("severity", []):
                        score *= 1.5
                    
                    # 体质匹配加权
                    if (patient_profile.constitution and 
                        patient_profile.constitution == pattern.get("constitution")):
                        score *= 2.0
                    
                    syndrome_scores[syndrome] += score * symptom.confidence
        
        # 排序并选择最可能的证候
        sorted_syndromes = sorted(syndrome_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 选择得分最高的证候作为主要诊断
        primary_syndrome = sorted_syndromes[0][0] if sorted_syndromes else "待进一步辨证"
        
        # 返回所有可能的证候模式
        syndrome_patterns = [syndrome for syndrome, score in sorted_syndromes if score > 0.5]
        
        return syndrome_patterns, primary_syndrome
    
    def generate_recommendations(self, syndrome: str, symptoms: List[SymptomInfo]) -> List[str]:
        """生成治疗建议"""
        recommendations = []
        
        # 基于证候的通用建议
        syndrome_recommendations = {
            "气虚证": [
                "建议补气养血，可适当食用人参、黄芪等",
                "避免过度劳累，保证充足休息",
                "适当进行缓和运动，如太极拳、八段锦"
            ],
            "阳虚证": [
                "建议温阳补肾，避免生冷食物",
                "注意保暖，特别是腰腹部",
                "可适当食用温补食材如羊肉、韭菜"
            ],
            "阴虚证": [
                "建议滋阴润燥，多食用银耳、百合等",
                "避免辛辣燥热食物",
                "保持情绪平和，避免熬夜"
            ],
            "血瘀证": [
                "建议活血化瘀，适当运动促进血液循环",
                "可食用山楂、红花等活血食材",
                "避免久坐不动"
            ],
            "痰湿证": [
                "建议健脾化湿，饮食清淡",
                "避免油腻甜食，多食用薏米、冬瓜等",
                "适当运动，促进新陈代谢"
            ],
            "湿热证": [
                "建议清热利湿，避免辛辣油腻",
                "多饮水，保持大便通畅",
                "可食用绿豆、苦瓜等清热食材"
            ],
            "肝郁证": [
                "建议疏肝解郁，保持心情舒畅",
                "适当运动，如散步、瑜伽",
                "可饮用玫瑰花茶、柠檬茶"
            ]
        }
        
        recommendations.extend(syndrome_recommendations.get(syndrome, []))
        
        # 基于症状的特殊建议
        for symptom in symptoms:
            if symptom.name == "失眠":
                recommendations.append("建议睡前避免使用电子设备，创造良好睡眠环境")
            elif symptom.name == "头痛":
                recommendations.append("注意休息，避免精神紧张，可适当按摩太阳穴")
            elif symptom.name == "咳嗽":
                recommendations.append("多饮温水，避免吸烟和二手烟")
        
        return list(set(recommendations))  # 去重

class DialogueAnalyzer:
    """对话分析器主类"""
    
    def __init__(self):
        self.symptom_extractor = SymptomExtractor()
        self.profile_extractor = PatientProfileExtractor()
        self.diagnosis_engine = TCMDiagnosisEngine()
        
        logger.info("问诊对话分析器初始化完成")
    
    async def analyze_dialogue(self, dialogue_history: List[str]) -> DialogueAnalysisResult:
        """分析对话历史"""
        try:
            # 合并所有对话文本
            full_text = " ".join(dialogue_history)
            
            # 提取症状信息
            symptoms = self.symptom_extractor.extract_symptoms(full_text)
            
            # 提取患者档案
            patient_profile = self.profile_extractor.extract_profile(dialogue_history)
            
            # 证候分析
            syndrome_patterns, primary_syndrome = self.diagnosis_engine.analyze_syndrome(
                symptoms, patient_profile
            )
            
            # 严重程度评估
            severity_assessment = self._assess_severity(symptoms)
            
            # 生成建议
            recommendations = self.diagnosis_engine.generate_recommendations(
                primary_syndrome, symptoms
            )
            
            # 计算整体置信度
            confidence = self._calculate_confidence(symptoms, patient_profile)
            
            result = DialogueAnalysisResult(
                extracted_symptoms=symptoms,
                patient_profile=patient_profile,
                syndrome_patterns=syndrome_patterns,
                tcm_diagnosis=primary_syndrome,
                severity_assessment=severity_assessment,
                recommendations=recommendations,
                confidence=confidence
            )
            
            logger.info(f"对话分析完成，诊断: {primary_syndrome}, 症状数: {len(symptoms)}")
            return result
            
        except Exception as e:
            logger.error(f"对话分析失败: {e}")
            raise
    
    def _assess_severity(self, symptoms: List[SymptomInfo]) -> str:
        """评估病情严重程度"""
        if not symptoms:
            return "无明显症状"
        
        severity_scores = {"轻微": 1, "中等": 2, "严重": 3}
        total_score = sum(severity_scores.get(symptom.severity, 2) for symptom in symptoms)
        avg_score = total_score / len(symptoms)
        
        if avg_score >= 2.5:
            return "较严重"
        elif avg_score >= 1.5:
            return "中等"
        else:
            return "轻微"
    
    def _calculate_confidence(self, symptoms: List[SymptomInfo], 
                            patient_profile: PatientProfile) -> float:
        """计算分析置信度"""
        if not symptoms:
            return 0.3
        
        # 基于症状数量和质量
        symptom_confidence = sum(symptom.confidence for symptom in symptoms) / len(symptoms)
        
        # 基于患者信息完整性
        profile_completeness = 0.0
        if patient_profile.age:
            profile_completeness += 0.2
        if patient_profile.gender:
            profile_completeness += 0.2
        if patient_profile.constitution:
            profile_completeness += 0.3
        if patient_profile.medical_history:
            profile_completeness += 0.2
        if patient_profile.lifestyle:
            profile_completeness += 0.1
        
        # 综合置信度
        confidence = (symptom_confidence * 0.7 + profile_completeness * 0.3)
        return max(0.4, min(0.95, confidence)) 