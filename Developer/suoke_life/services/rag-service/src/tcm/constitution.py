#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
体质辨别模块

该模块实现了基于中医理论的体质辨别系统，包括九种基本体质类型的辨别方法、
问卷设计、评分系统以及个性化调理方案生成。

Author: AI Team
Date: 2023
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import numpy as np
from loguru import logger

# 导入四诊相关模块，用于结合四诊数据进行综合分析
try:
    from .four_diagnosis import DiagnosisData, TongueData, PulseData, FaceData
except ImportError:
    logger.warning("无法导入四诊模块，将只使用问卷数据进行体质辨别")


class ConstitutionType(str, Enum):
    """体质类型枚举"""
    BALANCED = "平和质"
    QI_DEFICIENCY = "气虚质"
    YANG_DEFICIENCY = "阳虚质"
    YIN_DEFICIENCY = "阴虚质"
    PHLEGM_DAMPNESS = "痰湿质"
    DAMP_HEAT = "湿热质"
    BLOOD_STASIS = "血瘀质"
    QI_STAGNATION = "气郁质"
    SPECIAL = "特禀质"


@dataclass
class ConstitutionQuestion:
    """体质辨别问卷问题结构"""
    id: str
    question: str
    related_types: List[Tuple[ConstitutionType, float]]  # 相关体质类型及其权重
    category: str  # 问题分类，如"症状体征"，"生活习惯"等
    options: List[Dict[str, Any]]  # 选项列表，包含选项文本和对应分值


@dataclass
class ConstitutionResult:
    """体质辨别结果结构"""
    primary_type: Optional[ConstitutionType]  # 主要体质类型
    secondary_types: List[ConstitutionType]  # 次要体质类型
    scores: Dict[ConstitutionType, float]  # 各体质得分
    timestamp: datetime  # 辨别时间
    recommendations: Dict[ConstitutionType, Dict[str, Any]]  # 调理推荐方案
    features: Dict[ConstitutionType, Dict[str, Any]]  # 体质特征描述


class ConstitutionIdentifier:
    """体质辨别器"""
    
    def __init__(self):
        """初始化体质辨别器"""
        # 初始化问卷
        self.questionnaire = self._init_questionnaire()
        
        # 初始化各体质类型特征
        self.features = self._init_features()
        
        # 初始化各体质类型的推荐方案
        self.recommendations = self._init_recommendations()
        
        logger.info("体质辨别器初始化完成")
        
        # 体质特征映射
        self.constitution_features = self._init_features()
        
        # 体质调理建议
        self.constitution_recommendations = self._init_recommendations()
        
    def _init_questionnaire(self) -> List[ConstitutionQuestion]:
        """初始化体质辨别问卷"""
        questionnaire = []
        
        # 平和质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="B001",
            question="您的面色红润有光泽吗？",
            related_types=[(ConstitutionType.BALANCED, 1.0)],
            category="外在表现",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="B002",
            question="您的精力充沛，耐受力强吗？",
            related_types=[(ConstitutionType.BALANCED, 1.0)],
            category="精神状态",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        # 气虚质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="Q001",
            question="您是否容易感到疲乏无力？",
            related_types=[(ConstitutionType.QI_DEFICIENCY, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="Q002",
            question="您说话时声音低弱无力吗？",
            related_types=[(ConstitutionType.QI_DEFICIENCY, 1.0)],
            category="症状体征",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="Q003",
            question="您容易出汗，即使不活动也会出汗吗？",
            related_types=[(ConstitutionType.QI_DEFICIENCY, 1.0)],
            category="症状体征",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        # 阳虚质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="Y001",
            question="您手脚发凉，尤其是在冬天吗？",
            related_types=[(ConstitutionType.YANG_DEFICIENCY, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="Y002",
            question="您怕冷，特别喜欢温暖的环境吗？",
            related_types=[(ConstitutionType.YANG_DEFICIENCY, 1.0)],
            category="生活习惯",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        # 阴虚质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="YY001",
            question="您是否感到手心发热、口干？",
            related_types=[(ConstitutionType.YIN_DEFICIENCY, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="YY002",
            question="您是否容易感到烦躁、口干舌燥？",
            related_types=[(ConstitutionType.YIN_DEFICIENCY, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="YY003",
            question="您是否在睡眠中容易出汗？",
            related_types=[(ConstitutionType.YIN_DEFICIENCY, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        # 痰湿质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="T001",
            question="您是否感到胸闷或腹部胀满？",
            related_types=[(ConstitutionType.PHLEGM_DAMPNESS, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="T002",
            question="您的身体或面部是否感到发胖或浮肿？",
            related_types=[(ConstitutionType.PHLEGM_DAMPNESS, 1.0)],
            category="体型特征",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="T003",
            question="您的舌头上是否常有厚厚的白苔？",
            related_types=[(ConstitutionType.PHLEGM_DAMPNESS, 1.0)],
            category="舌象",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        # 湿热质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="S001",
            question="您是否感到口苦或嘴里有异味？",
            related_types=[(ConstitutionType.DAMP_HEAT, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="S002",
            question="您的大便黏腻不爽、有灼热感吗？",
            related_types=[(ConstitutionType.DAMP_HEAT, 1.0)],
            category="排泄特征",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        # 血瘀质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="X001",
            question="您的嘴唇颜色偏暗紫吗？",
            related_types=[(ConstitutionType.BLOOD_STASIS, 1.0)],
            category="外在表现",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="X002",
            question="您容易出现皮肤淤青吗？",
            related_types=[(ConstitutionType.BLOOD_STASIS, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="X003",
            question="您的面色晦暗或容易出现褐斑吗？",
            related_types=[(ConstitutionType.BLOOD_STASIS, 1.0)],
            category="外在表现",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        # 气郁质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="QY001",
            question="您容易感到情绪低落或郁闷吗？",
            related_types=[(ConstitutionType.QI_STAGNATION, 1.0)],
            category="心理状态",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="QY002",
            question="您容易感到焦虑、担心或烦躁吗？",
            related_types=[(ConstitutionType.QI_STAGNATION, 1.0)],
            category="心理状态",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="QY003",
            question="您容易叹气吗？",
            related_types=[(ConstitutionType.QI_STAGNATION, 1.0)],
            category="症状体征",
            options=[
                {"text": "经常", "value": 1},
                {"text": "偶尔", "value": 0.5},
                {"text": "很少", "value": 0}
            ]
        ))
        
        # 特禀质相关问题
        questionnaire.append(ConstitutionQuestion(
            id="TB001",
            question="您对某些食物或药物容易过敏吗？",
            related_types=[(ConstitutionType.SPECIAL, 1.0)],
            category="过敏史",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="TB002",
            question="您的家族中有人有过敏体质吗？",
            related_types=[(ConstitutionType.SPECIAL, 1.0)],
            category="家族史",
            options=[
                {"text": "是", "value": 1},
                {"text": "否", "value": 0},
                {"text": "不确定", "value": 0.5}
            ]
        ))
        
        # 混合类问题
        questionnaire.append(ConstitutionQuestion(
            id="M001",
            question="您对气候变化的适应能力如何？",
            related_types=[
                (ConstitutionType.BALANCED, 1.0),
                (ConstitutionType.QI_DEFICIENCY, -0.5),
                (ConstitutionType.YANG_DEFICIENCY, -0.5)
            ],
            category="环境适应",
            options=[
                {"text": "良好", "value": 1},
                {"text": "一般", "value": 0.5},
                {"text": "较差", "value": 0}
            ]
        ))
        
        questionnaire.append(ConstitutionQuestion(
            id="M002",
            question="您的睡眠质量如何？",
            related_types=[
                (ConstitutionType.BALANCED, 1.0),
                (ConstitutionType.QI_STAGNATION, -0.5),
                (ConstitutionType.YIN_DEFICIENCY, -0.5)
            ],
            category="睡眠",
            options=[
                {"text": "良好", "value": 1},
                {"text": "一般", "value": 0.5},
                {"text": "较差", "value": 0}
            ]
        ))
        
        return questionnaire
        
    def _init_features(self) -> Dict[ConstitutionType, Dict[str, Any]]:
        """初始化各体质类型的特征描述"""
        features = {}
        
        features[ConstitutionType.BALANCED] = {
            "name": "平和质",
            "description": "平和质是九种体质中最为理想的状态，表现为阴阳气血调和，形体适中，面色红润，精力充沛。",
            "characteristics": [
                "面色红润有光泽",
                "精力充沛，耐受力强",
                "体形匀称，肌肉结实有弹性",
                "胃口良好，大小便正常",
                "睡眠良好，情绪稳定",
                "对外界环境适应能力强"
            ],
            "traditional_description": "阴阳协调，气血和顺",
            "disease_tendency": [
                "平和体质发病率低",
                "患病后一般为实证",
                "病情较轻，恢复快"
            ],
            "score_threshold": 0.8
        }
        
        features[ConstitutionType.QI_DEFICIENCY] = {
            "name": "气虚质",
            "description": "气虚质表现为元气不足，体质虚弱，易疲劳，声音低弱，容易感冒等。",
            "characteristics": [
                "平素语音低弱，气短懒言",
                "容易疲乏，精神不振",
                "易出汗，活动后汗出较多",
                "舌淡红，舌边有齿痕",
                "面色淡白或萎黄",
                "容易感冒，恢复较慢"
            ],
            "traditional_description": "肺脾气虚，卫外不固",
            "disease_tendency": [
                "慢性疲劳综合征",
                "呼吸系统疾病",
                "消化系统功能减弱",
                "易感染"
            ],
            "score_threshold": 0.6
        }
        
        features[ConstitutionType.YANG_DEFICIENCY] = {
            "name": "阳虚质",
            "description": "阳虚质表现为畏寒怕冷，手脚发凉，喜温喜热，精神不振等。",
            "characteristics": [
                "怕冷，手脚发凉",
                "喜热饮食，不喜冷饮",
                "面色苍白，光泽少",
                "舌淡胖嫩，苔白滑",
                "大便溏薄，小便清长",
                "腰膝酸软，精神不足"
            ],
            "traditional_description": "阳气虚衰，温煦不足",
            "disease_tendency": [
                "心血管疾病",
                "肾功能减退",
                "代谢性疾病",
                "免疫力低下"
            ],
            "score_threshold": 0.6
        }
        
        features[ConstitutionType.YIN_DEFICIENCY] = {
            "name": "阴虚质",
            "description": "阴虚质表现为口干舌燥，手足心热，干咳少痰，失眠多梦等。",
            "characteristics": [
                "手心脚心发热",
                "口干咽干，喜冷饮",
                "面色潮红或偏红",
                "舌红少苔，或舌光剥",
                "大便干燥，小便短黄",
                "睡眠不实，容易失眠"
            ],
            "traditional_description": "阴液亏损，内热明显",
            "disease_tendency": [
                "内分泌失调",
                "糖尿病",
                "消化系统疾病",
                "皮肤干燥相关疾病"
            ],
            "score_threshold": 0.6
        }
        
        features[ConstitutionType.PHLEGM_DAMPNESS] = {
            "name": "痰湿质",
            "description": "痰湿质表现为体形肥胖，腹部松软，容易疲倦，舌苔厚腻等。",
            "characteristics": [
                "体形肥胖，腹部松软肥满",
                "面部皮肤油脂多，易生痤疮",
                "口黏腻或甜，口中痰多",
                "舌淡胖，苔白腻",
                "睡眠打鼾，容易疲倦",
                "大便黏滞不爽"
            ],
            "traditional_description": "痰湿内蕴，运化不利",
            "disease_tendency": [
                "肥胖症",
                "高脂血症",
                "脑血管疾病",
                "代谢综合征"
            ],
            "score_threshold": 0.6
        }
        
        features[ConstitutionType.DAMP_HEAT] = {
            "name": "湿热质",
            "description": "湿热质表现为面垢油光，易生痤疮，口苦口臭，大便粘滞等。",
            "characteristics": [
                "面垢油光，易生痤疮",
                "口苦口臭，口干不欲饮",
                "大便粘滞不畅或燥结",
                "小便短黄，尿道有热感",
                "易生疮疖，皮肤瘙痒",
                "舌红，苔黄腻"
            ],
            "traditional_description": "湿热内蕴，外达肌肤",
            "disease_tendency": [
                "皮肤炎症性疾病",
                "尿路感染",
                "肝胆疾病",
                "消化系统疾病"
            ],
            "score_threshold": 0.6
        }
        
        features[ConstitutionType.BLOOD_STASIS] = {
            "name": "血瘀质",
            "description": "血瘀质表现为面色晦暗，皮肤紫斑，口唇黯淡，舌有瘀点等。",
            "characteristics": [
                "面色晦暗或黯淡，甚则有褐斑",
                "口唇黯淡或紫暗",
                "肌肤易见瘀斑",
                "舌质紫暗或有瘀点",
                "女性月经有血块",
                "皮肤干燥，毛发不荣",
                "肢体某处疼痛固定不移"
            ],
            "traditional_description": "血行不畅，瘀滞于内",
            "disease_tendency": [
                "心脑血管疾病",
                "妇科疾病",
                "疼痛性疾病",
                "静脉曲张"
            ],
            "score_threshold": 0.6
        }
        
        features[ConstitutionType.QI_STAGNATION] = {
            "name": "气郁质",
            "description": "气郁质表现为情绪抑郁或烦躁，胸胁胀闷，舌苔薄白等。",
            "characteristics": [
                "情绪波动大，易烦躁或抑郁",
                "胸胁部胀满，喜欢叹气",
                "常感到咽部异物感",
                "女性月经前乳房胀痛明显",
                "舌淡红，苔薄白",
                "焦虑不安，易惊醒"
            ],
            "traditional_description": "气机郁滞，情志不舒",
            "disease_tendency": [
                "抑郁症",
                "焦虑症",
                "功能性消化不良",
                "乳腺疾病"
            ],
            "score_threshold": 0.6
        }
        
        features[ConstitutionType.SPECIAL] = {
            "name": "特禀质",
            "description": "特禀质表现为过敏体质，容易对药物、食物或环境过敏，有家族遗传倾向等。",
            "characteristics": [
                "容易过敏，如过敏性鼻炎、哮喘、荨麻疹等",
                "对某些药物、食物或接触物过敏",
                "过敏症状反复发作",
                "多有家族过敏史",
                "可伴有其他体质特点"
            ],
            "traditional_description": "禀赋异常，易感特异",
            "disease_tendency": [
                "过敏性疾病",
                "自身免疫性疾病",
                "皮肤过敏",
                "药物不良反应"
            ],
            "score_threshold": 0.6
        }
        
        return features
        
    def _init_recommendations(self) -> Dict[ConstitutionType, Dict[str, Any]]:
        """初始化各体质类型的调理推荐方案"""
        recommendations = {}
        
        recommendations[ConstitutionType.BALANCED] = {
            "diet": [
                "饮食应以清淡、均衡为主",
                "粗细搭配，荤素结合",
                "少食辛辣刺激性食物",
                "定时定量，不暴饮暴食"
            ],
            "exercise": [
                "保持适量运动，如散步、慢跑、太极等",
                "避免过度疲劳",
                "保持规律的作息时间"
            ],
            "acupoints": [
                "百会穴：宁心安神",
                "足三里：增强体质",
                "关元穴：培元固本"
            ],
            "herbs": [
                "人参：适量服用可增强体质",
                "太子参：温和补气",
                "枸杞子：滋阴明目"
            ],
            "lifestyle": [
                "保持心情舒畅，避免大悲大喜",
                "作息规律，早睡早起",
                "适当参加社交活动，保持良好心态"
            ],
            "seasonal_advice": {
                "spring": "春季注意保暖，适量增加户外活动",
                "summer": "夏季注意防暑降温，饮食宜清淡",
                "autumn": "秋季注意防燥，可适量食用滋阴润燥食物",
                "winter": "冬季注意保暖，可适当进补"
            }
        }
        
        recommendations[ConstitutionType.QI_DEFICIENCY] = {
            "diet": [
                "宜食易消化、富含蛋白质的食物",
                "可适量食用山药、大枣、粳米等",
                "饮食宜温热，少食生冷",
                "少量多餐，避免过度饥饿"
            ],
            "exercise": [
                "宜进行缓和、舒缓的运动，如太极、气功",
                "避免剧烈运动和过度劳累",
                "保证充足休息，午间小憩"
            ],
            "acupoints": [
                "足三里：补中益气",
                "气海穴：补气培元",
                "关元穴：固本培元"
            ],
            "herbs": [
                "西洋参：补气养阴",
                "黄芪：补气固表",
                "白术：健脾益气"
            ],
            "lifestyle": [
                "保持乐观情绪，减少忧思",
                "避免过度劳累，适当午休",
                "保暖防寒，避免受凉"
            ],
            "seasonal_advice": {
                "spring": "春季注意养肺护脾，可服用玉屏风散等增强抵抗力",
                "summer": "夏季注意防暑，避免过度出汗耗气",
                "autumn": "秋季注意防燥养肺，可适量食用百合、沙参等",
                "winter": "冬季注意保暖，可适当服用参芪等温补药膳"
            }
        }
        
        recommendations[ConstitutionType.YANG_DEFICIENCY] = {
            "diet": [
                "宜食温热食物，如羊肉、牛肉、韭菜等",
                "可适量食用桂圆、核桃等温补食物",
                "忌食生冷瓜果和寒凉食物",
                "饮食宜温不宜凉，少食冷饮"
            ],
            "exercise": [
                "宜进行温和运动，如散步、慢跑",
                "练习八段锦、五禽戏等养生功法",
                "避免在寒冷环境中长时间活动"
            ],
            "acupoints": [
                "关元穴：温补元阳",
                "命门穴：温补肾阳",
                "足三里：健脾胃，补中气"
            ],
            "herbs": [
                "肉桂：温肾阳",
                "附子：回阳救逆（需在医师指导下使用）",
                "干姜：温中散寒"
            ],
            "lifestyle": [
                "保暖防寒，尤其注意腰腹部和足部保暖",
                "避免长时间处于寒冷潮湿环境",
                "作息规律，保证充足睡眠"
            ],
            "seasonal_advice": {
                "spring": "春季注意防风寒，逐渐增加户外活动",
                "summer": "夏季避免长时间呆在空调房，防止寒邪侵袭",
                "autumn": "秋季及时添加衣物，防寒保暖",
                "winter": "冬季是温补阳气的最佳季节，可适当服用温阳药膳"
            }
        }
        
        recommendations[ConstitutionType.YIN_DEFICIENCY] = {
            "diet": [
                "宜食滋阴润燥食物，如银耳、百合、梨等",
                "多喝水，少食辛辣刺激性食物",
                "适量食用豆类、乳制品等",
                "忌烟酒、浓茶、咖啡等刺激性饮料"
            ],
            "exercise": [
                "宜进行舒缓运动，如太极拳、气功",
                "避免剧烈运动和过度出汗",
                "保持规律作息，防止熬夜"
            ],
            "acupoints": [
                "太溪穴：滋补肾阴",
                "三阴交：调理肝脾肾三阴",
                "涌泉穴：滋阴降火"
            ],
            "herbs": [
                "沙参：养阴润肺",
                "麦冬：滋阴润肺",
                "玄参：滋阴降火"
            ],
            "lifestyle": [
                "避免情绪过度激动",
                "保持心情舒畅，避免暴怒",
                "不宜长时间处于干燥、高温环境"
            ],
            "seasonal_advice": {
                "spring": "春季注意防燥，多饮水",
                "summer": "夏季注意防暑，但避免过度贪凉",
                "autumn": "秋季是阴虚体质最需要调理的季节，多食滋阴润燥食物",
                "winter": "冬季注意保暖同时滋阴，避免燥热"
            }
        }
        
        recommendations[ConstitutionType.PHLEGM_DAMPNESS] = {
            "diet": [
                "宜食清淡、易消化食物",
                "多食用薏米、赤小豆、冬瓜等利水渗湿食物",
                "少食肥甘厚腻和生冷食物",
                "控制总热量摄入，保持合理体重"
            ],
            "exercise": [
                "增加有氧运动，如慢跑、快走",
                "坚持运动，帮助代谢水湿",
                "保持规律运动，控制体重"
            ],
            "acupoints": [
                "丰隆穴：化痰理气",
                "脾俞穴：健脾化湿",
                "足三里：健脾胃"
            ],
            "herbs": [
                "茯苓：利水渗湿",
                "陈皮：理气化痰",
                "半夏：燥湿化痰（需在医师指导下使用）"
            ],
            "lifestyle": [
                "避免久坐不动，保持活动",
                "居住环境保持通风干燥",
                "避免长时间处于潮湿环境"
            ],
            "seasonal_advice": {
                "spring": "春季注意祛湿，可服用藿香正气类药物",
                "summer": "夏季注意防暑祛湿，避免贪食生冷",
                "autumn": "秋季注意健脾祛湿，是调理痰湿体质的好时机",
                "winter": "冬季避免过度进补，防止痰湿内生"
            }
        }
        
        recommendations[ConstitutionType.DAMP_HEAT] = {
            "diet": [
                "宜食清淡、利湿清热食物，如冬瓜、绿豆、苦瓜等",
                "多喝水，促进代谢",
                "少食辛辣、油腻、煎炸食物",
                "忌酒及刺激性食物"
            ],
            "exercise": [
                "坚持适量运动，促进汗液排出",
                "晨练或傍晚运动较为适宜",
                "避免在湿热环境中长时间运动"
            ],
            "acupoints": [
                "阴陵泉：利湿清热",
                "三阴交：健脾利湿",
                "曲池穴：清热解毒"
            ],
            "herbs": [
                "黄连：清热燥湿",
                "黄芩：清热燥湿",
                "薏米：利水渗湿"
            ],
            "lifestyle": [
                "保持居住环境通风干燥",
                "避免长时间处于高温潮湿环境",
                "保持心情舒畅，避免情绪郁结"
            ],
            "seasonal_advice": {
                "spring": "春季适当使用祛湿药膳，如薏米粥",
                "summer": "夏季是湿热体质最易加重的季节，注意清热祛湿",
                "autumn": "秋季继续调理余热，食用些清热祛湿食物",
                "winter": "冬季可适当进补，但应避免温热太过"
            }
        }
        
        recommendations[ConstitutionType.BLOOD_STASIS] = {
            "diet": [
                "宜食活血化瘀食物，如黑木耳、山楂、桃仁等",
                "少食油腻、煎炸、过咸食物",
                "忌食寒凉，避免生冷刺激",
                "适量饮水，保持血液循环"
            ],
            "exercise": [
                "坚持有氧运动，如慢跑、游泳、太极拳等",
                "避免久坐不动，定时起身活动",
                "适当增加活动量，促进血液循环"
            ],
            "acupoints": [
                "血海穴：活血化瘀",
                "膈俞穴：活血行气",
                "三阴交：调理气血"
            ],
            "herbs": [
                "当归：补血活血",
                "川芎：活血行气",
                "红花：活血通经"
            ],
            "lifestyle": [
                "保持情绪稳定，避免大喜大悲",
                "保暖防寒，特别是手脚",
                "作息规律，避免熬夜"
            ],
            "seasonal_advice": {
                "spring": "春季可适当食用活血化瘀的食物，如春笋、荠菜等",
                "summer": "夏季注意防暑，保持血液循环通畅",
                "autumn": "秋季注意润燥，避免血液黏稠",
                "winter": "冬季注意保暖，防止寒邪凝滞血脉"
            }
        }
        
        recommendations[ConstitutionType.QI_STAGNATION] = {
            "diet": [
                "宜食理气解郁食物，如柑橘、香菜、玫瑰花等",
                "少食生冷、油腻食物",
                "适量饮茶，如玫瑰花茶、菊花茶等",
                "保持饮食规律，避免暴饮暴食"
            ],
            "exercise": [
                "适合进行舒展性运动，如瑜伽、太极",
                "深呼吸、冥想等放松练习",
                "增加户外活动，亲近自然"
            ],
            "acupoints": [
                "太冲穴：疏肝解郁",
                "内关穴：理气解郁",
                "膻中穴：宽胸理气"
            ],
            "herbs": [
                "柴胡：疏肝解郁",
                "香附：理气解郁",
                "玫瑰花：理气解郁"
            ],
            "lifestyle": [
                "培养兴趣爱好，转移注意力",
                "学习情绪管理技巧，如认知调节",
                "保持社交活动，避免孤独"
            ],
            "seasonal_advice": {
                "spring": "春季是肝气最易郁结的季节，多参与户外活动",
                "summer": "夏季注意防暑，保持情绪舒畅",
                "autumn": "秋季注意调畅情志，防止肃杀之气影响情绪",
                "winter": "冬季注意保暖，多参与愉悦身心的活动"
            }
        }
        
        recommendations[ConstitutionType.SPECIAL] = {
            "diet": [
                "避免已知过敏食物",
                "记录饮食日记，找出潜在过敏原",
                "多食用新鲜蔬果，增强免疫力",
                "避免添加剂和防腐剂"
            ],
            "exercise": [
                "适量运动，增强体质",
                "避免在花粉高发季节户外运动",
                "室内运动选择通风良好环境"
            ],
            "acupoints": [
                "肺俞穴：增强肺功能",
                "脾俞穴：调节免疫功能",
                "足三里：增强体质"
            ],
            "herbs": [
                "黄芪：增强免疫力",
                "荆芥：防风散邪",
                "防风：祛风解表"
            ],
            "lifestyle": [
                "保持环境清洁，减少过敏原",
                "注意气候变化，及时增减衣物",
                "定期体检，了解自身过敏状况"
            ],
            "seasonal_advice": {
                "spring": "春季是过敏高发季节，注意防护，可服用防过敏药物",
                "summer": "夏季注意防暑，避免剧烈温差变化",
                "autumn": "秋季注意防风邪，过敏体质者应减少户外活动",
                "winter": "冬季注意保暖，防止寒邪侵袭诱发过敏"
            }
        }
        
        return recommendations
        
    def identify_constitution(self, 
                           diagnostic_data: Optional[Dict[str, Any]] = None, 
                           questionnaire_answers: Optional[Dict[str, Any]] = None) -> ConstitutionResult:
        """
        根据四诊数据或问卷回答识别体质
        
        Args:
            diagnostic_data: 四诊合参数据，包含望闻问切的结果
            questionnaire_answers: 问卷回答，格式为 {问题ID: 选项值}
            
        Returns:
            ConstitutionResult: 体质辨别结果
        """
        # 初始化各体质的得分
        scores = {constitution_type: 0.0 for constitution_type in ConstitutionType}
        
        # 如果有问卷回答，则基于问卷进行评分
        if questionnaire_answers:
            scores = self._score_from_questionnaire(questionnaire_answers, scores)
        
        # 如果有四诊数据，则基于四诊数据进行评分
        if diagnostic_data:
            scores = self._score_from_diagnostic_data(diagnostic_data, scores)
        
        # 如果既没有问卷回答也没有四诊数据，则返回空结果
        if not diagnostic_data and not questionnaire_answers:
            logger.warning("无法进行体质辨别：缺少问卷回答和四诊数据")
            return ConstitutionResult(
                primary_type=None,
                secondary_types=[],
                scores={},
                timestamp=datetime.now(),
                recommendations={},
                features={}
            )
        
        # 标准化得分
        normalized_scores = self._normalize_scores(scores)
        
        # 确定主要体质和次要体质
        primary_type, secondary_types = self._determine_constitution_types(normalized_scores)
        
        # 获取主要体质的特征和推荐方案
        features = {}
        recommendations = {}
        
        if primary_type:
            features[primary_type] = self.constitution_features.get(primary_type, {})
            recommendations[primary_type] = self.constitution_recommendations.get(primary_type, {})
        
        # 获取次要体质的特征和推荐方案
        for constitution_type in secondary_types:
            features[constitution_type] = self.constitution_features.get(constitution_type, {})
            recommendations[constitution_type] = self.constitution_recommendations.get(constitution_type, {})
        
        # 返回结果
        result = ConstitutionResult(
            primary_type=primary_type,
            secondary_types=secondary_types,
            scores=normalized_scores,
            timestamp=datetime.now(),
            recommendations=recommendations,
            features=features
        )
        
        logger.info(f"体质辨别结果：主要体质：{primary_type.value if primary_type else 'None'}, " + 
                   f"次要体质：{[t.value for t in secondary_types]}")
        
        return result
    
    def _score_from_questionnaire(self, 
                                 answers: Dict[str, Any], 
                                 initial_scores: Dict[ConstitutionType, float]) -> Dict[ConstitutionType, float]:
        """基于问卷回答计算体质得分"""
        scores = initial_scores.copy()
        
        for question in self.questionnaire:
            if question.id in answers:
                answer_value = answers[question.id]
                
                # 找到对应选项的值
                option_value = 0.0
                for option in question.options:
                    if isinstance(answer_value, str) and option["text"] == answer_value:
                        option_value = option["value"]
                        break
                    elif isinstance(answer_value, (int, float)):
                        option_value = float(answer_value)
                        break
                
                # 为相关体质类型加分
                for constitution_type, weight in question.related_types:
                    scores[constitution_type] += option_value * weight
        
        return scores
    
    def _score_from_diagnostic_data(self, 
                                   diagnostic_data: Dict[str, Any], 
                                   initial_scores: Dict[ConstitutionType, float]) -> Dict[ConstitutionType, float]:
        """基于四诊数据计算体质得分"""
        scores = initial_scores.copy()
        
        # 舌诊数据分析
        if "tongue_data" in diagnostic_data:
            tongue_data = diagnostic_data["tongue_data"]
            scores = self._analyze_tongue_data(tongue_data, scores)
        
        # 脉诊数据分析
        if "pulse_data" in diagnostic_data:
            pulse_data = diagnostic_data["pulse_data"]
            scores = self._analyze_pulse_data(pulse_data, scores)
        
        # 面诊数据分析
        if "face_data" in diagnostic_data:
            face_data = diagnostic_data["face_data"]
            scores = self._analyze_face_data(face_data, scores)
        
        # 问诊数据分析
        if "inquiry_data" in diagnostic_data:
            inquiry_data = diagnostic_data["inquiry_data"]
            scores = self._analyze_inquiry_data(inquiry_data, scores)
        
        return scores
    
    def _analyze_tongue_data(self, 
                            tongue_data: Dict[str, Any], 
                            scores: Dict[ConstitutionType, float]) -> Dict[ConstitutionType, float]:
        """分析舌诊数据，更新体质得分"""
        # 舌质颜色分析
        if "tongue_color" in tongue_data:
            color = tongue_data["tongue_color"]
            if color == "pale":  # 淡白舌
                scores[ConstitutionType.QI_DEFICIENCY] += 1.0
                scores[ConstitutionType.YANG_DEFICIENCY] += 0.8
            elif color == "red":  # 红舌
                scores[ConstitutionType.YIN_DEFICIENCY] += 1.0
                scores[ConstitutionType.DAMP_HEAT] += 0.5
            elif color == "dark_red" or color == "purple":  # 深红舌或紫舌
                scores[ConstitutionType.BLOOD_STASIS] += 1.0
            elif color == "normal":  # 淡红舌
                scores[ConstitutionType.BALANCED] += 1.0
        
        # 舌苔分析
        if "coating_color" in tongue_data:
            coating = tongue_data["coating_color"]
            if coating == "white_thick":  # 厚白苔
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 1.0
                scores[ConstitutionType.YANG_DEFICIENCY] += 0.5
            elif coating == "yellow" or coating == "yellow_thick":  # 黄苔或厚黄苔
                scores[ConstitutionType.DAMP_HEAT] += 1.0
            elif coating == "no_coating" or coating == "little_coating":  # 少苔或无苔
                scores[ConstitutionType.YIN_DEFICIENCY] += 1.0
            elif coating == "white_thin":  # 薄白苔
                scores[ConstitutionType.BALANCED] += 0.8
        
        # 舌体形态分析
        if "shape" in tongue_data:
            shape = tongue_data["shape"]
            if shape == "swollen":  # 胖大舌
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.8
                scores[ConstitutionType.QI_DEFICIENCY] += 0.5
            elif shape == "thin":  # 瘦薄舌
                scores[ConstitutionType.YIN_DEFICIENCY] += 0.8
            elif shape == "cracked":  # 裂纹舌
                scores[ConstitutionType.YIN_DEFICIENCY] += 1.0
            elif shape == "tooth_marked":  # 齿痕舌
                scores[ConstitutionType.QI_DEFICIENCY] += 0.8
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.5
        
        # 舌苔湿度分析
        if "moisture" in tongue_data:
            moisture = tongue_data["moisture"]
            if moisture == "dry":  # 干燥
                scores[ConstitutionType.YIN_DEFICIENCY] += 1.0
            elif moisture == "very_wet":  # 很湿润
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.8
            elif moisture == "normal":  # 正常湿润
                scores[ConstitutionType.BALANCED] += 0.8
        
        return scores
    
    def _analyze_pulse_data(self, 
                           pulse_data: Dict[str, Any], 
                           scores: Dict[ConstitutionType, float]) -> Dict[ConstitutionType, float]:
        """分析脉诊数据，更新体质得分"""
        # 脉象分析
        if "pulse_type" in pulse_data:
            pulse_type = pulse_data["pulse_type"]
            
            if pulse_type == "weak" or pulse_type == "thin":  # 弱脉或细脉
                scores[ConstitutionType.QI_DEFICIENCY] += 1.0
            elif pulse_type == "slow" or pulse_type == "deep_weak":  # 迟脉或沉弱脉
                scores[ConstitutionType.YANG_DEFICIENCY] += 1.0
            elif pulse_type == "rapid" or pulse_type == "thin_rapid":  # 数脉或细数脉
                scores[ConstitutionType.YIN_DEFICIENCY] += 1.0
            elif pulse_type == "slippery":  # 滑脉
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.8
                scores[ConstitutionType.DAMP_HEAT] += 0.5
            elif pulse_type == "wiry":  # 弦脉
                scores[ConstitutionType.QI_STAGNATION] += 1.0
                scores[ConstitutionType.DAMP_HEAT] += 0.3
            elif pulse_type == "hesitant" or pulse_type == "choppy":  # 涩脉
                scores[ConstitutionType.BLOOD_STASIS] += 1.0
            elif pulse_type == "normal":  # 正常脉
                scores[ConstitutionType.BALANCED] += 1.0
        
        # 脉搏强度分析
        if "strength" in pulse_data:
            strength = pulse_data["strength"]
            if strength == "weak":  # 脉搏力弱
                scores[ConstitutionType.QI_DEFICIENCY] += 0.8
                scores[ConstitutionType.YANG_DEFICIENCY] += 0.5
            elif strength == "strong":  # 脉搏力强
                scores[ConstitutionType.DAMP_HEAT] += 0.5
            elif strength == "normal":  # 脉搏力适中
                scores[ConstitutionType.BALANCED] += 0.8
        
        # 脉搏规律性分析
        if "regularity" in pulse_data:
            regularity = pulse_data["regularity"]
            if regularity == "irregular":  # 脉搏不规则
                scores[ConstitutionType.QI_STAGNATION] += 0.5
                scores[ConstitutionType.BLOOD_STASIS] += 0.8
            elif regularity == "regular":  # 脉搏规则
                scores[ConstitutionType.BALANCED] += 0.5
        
        return scores
    
    def _analyze_face_data(self, 
                          face_data: Dict[str, Any], 
                          scores: Dict[ConstitutionType, float]) -> Dict[ConstitutionType, float]:
        """分析面诊数据，更新体质得分"""
        # 面色分析
        if "face_color" in face_data:
            color = face_data["face_color"]
            if color == "pale" or color == "white":  # 面色苍白
                scores[ConstitutionType.QI_DEFICIENCY] += 1.0
                scores[ConstitutionType.YANG_DEFICIENCY] += 0.8
            elif color == "red":  # 面色红赤
                scores[ConstitutionType.YIN_DEFICIENCY] += 0.8
                scores[ConstitutionType.DAMP_HEAT] += 0.5
            elif color == "yellow":  # 面色萎黄
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.8
                scores[ConstitutionType.QI_DEFICIENCY] += 0.5
            elif color == "dark" or color == "bluish":  # 面色晦暗或青紫
                scores[ConstitutionType.BLOOD_STASIS] += 1.0
            elif color == "normal":  # 面色红润
                scores[ConstitutionType.BALANCED] += 1.0
        
        # 面部特征分析
        if "features" in face_data:
            features = face_data["features"]
            if "facial_swelling" in features and features["facial_swelling"]:  # 面部浮肿
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.8
                scores[ConstitutionType.YANG_DEFICIENCY] += 0.5
            if "facial_acne" in features and features["facial_acne"]:  # 面部痤疮
                scores[ConstitutionType.DAMP_HEAT] += 0.8
            if "facial_spots" in features and features["facial_spots"]:  # 面部斑点
                scores[ConstitutionType.BLOOD_STASIS] += 0.5
                scores[ConstitutionType.YIN_DEFICIENCY] += 0.3
            if "facial_oily" in features and features["facial_oily"]:  # 面部油脂多
                scores[ConstitutionType.DAMP_HEAT] += 0.5
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.3
        
        # 面部表情分析
        if "expression" in face_data:
            expression = face_data["expression"]
            if expression == "tired":  # 表情疲惫
                scores[ConstitutionType.QI_DEFICIENCY] += 0.8
            elif expression == "anxious" or expression == "depressed":  # 表情焦虑或抑郁
                scores[ConstitutionType.QI_STAGNATION] += 1.0
            elif expression == "lively":  # 表情生动活泼
                scores[ConstitutionType.BALANCED] += 0.8
        
        return scores
    
    def _analyze_inquiry_data(self, 
                             inquiry_data: Dict[str, Any], 
                             scores: Dict[ConstitutionType, float]) -> Dict[ConstitutionType, float]:
        """分析问诊数据，更新体质得分"""
        # 体温感觉分析
        if "temperature_feel" in inquiry_data:
            temp_feel = inquiry_data["temperature_feel"]
            if temp_feel == "cold" or temp_feel == "fear_cold":  # 怕冷，手脚冰凉
                scores[ConstitutionType.YANG_DEFICIENCY] += 1.0
            elif temp_feel == "hot" or temp_feel == "heat_in_palms":  # 怕热，手心发热
                scores[ConstitutionType.YIN_DEFICIENCY] += 1.0
                scores[ConstitutionType.DAMP_HEAT] += 0.5
        
        # 消化系统分析
        if "digestion" in inquiry_data:
            digestion = inquiry_data["digestion"]
            if digestion == "poor":  # 消化不良
                scores[ConstitutionType.QI_DEFICIENCY] += 0.8
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.5
            elif digestion == "bloating":  # 腹胀
                scores[ConstitutionType.QI_STAGNATION] += 0.8
            elif digestion == "good":  # 消化良好
                scores[ConstitutionType.BALANCED] += 0.8
        
        # 大便状况分析
        if "stool" in inquiry_data:
            stool = inquiry_data["stool"]
            if stool == "loose" or stool == "watery":  # 大便稀溏
                scores[ConstitutionType.YANG_DEFICIENCY] += 0.8
                scores[ConstitutionType.QI_DEFICIENCY] += 0.5
            elif stool == "dry" or stool == "constipation":  # 大便干结
                scores[ConstitutionType.YIN_DEFICIENCY] += 0.8
            elif stool == "sticky":  # 大便黏腻
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 1.0
                scores[ConstitutionType.DAMP_HEAT] += 0.5
            elif stool == "normal":  # 大便正常
                scores[ConstitutionType.BALANCED] += 0.8
        
        # 睡眠状况分析
        if "sleep" in inquiry_data:
            sleep = inquiry_data["sleep"]
            if sleep == "insomnia" or sleep == "dream_disturbed":  # 失眠多梦
                scores[ConstitutionType.YIN_DEFICIENCY] += 0.8
                scores[ConstitutionType.QI_STAGNATION] += 0.5
            elif sleep == "excessive":  # 嗜睡
                scores[ConstitutionType.PHLEGM_DAMPNESS] += 0.8
                scores[ConstitutionType.YANG_DEFICIENCY] += 0.5
            elif sleep == "normal":  # 睡眠正常
                scores[ConstitutionType.BALANCED] += 0.8
        
        # 精神状态分析
        if "mental_state" in inquiry_data:
            mental = inquiry_data["mental_state"]
            if mental == "tired" or mental == "fatigue":  # 疲倦乏力
                scores[ConstitutionType.QI_DEFICIENCY] += 1.0
            elif mental == "anxious" or mental == "depressed":  # 焦虑抑郁
                scores[ConstitutionType.QI_STAGNATION] += 1.0
            elif mental == "good":  # 精神状态良好
                scores[ConstitutionType.BALANCED] += 1.0
        
        # 过敏史分析
        if "allergy_history" in inquiry_data and inquiry_data["allergy_history"]:
            scores[ConstitutionType.SPECIAL] += 1.5
        
        return scores
    
    def _normalize_scores(self, scores: Dict[ConstitutionType, float]) -> Dict[ConstitutionType, float]:
        """标准化各体质得分，使总分为1"""
        total_score = sum(scores.values())
        if total_score == 0:
            # 如果总分为0，则平均分配
            normalized = {t: 1.0/len(ConstitutionType) for t in ConstitutionType}
        else:
            normalized = {t: score/total_score for t, score in scores.items()}
        return normalized
    
    def _determine_constitution_types(self, scores: Dict[ConstitutionType, float]) -> Tuple[Optional[ConstitutionType], List[ConstitutionType]]:
        """确定主要体质和次要体质"""
        # 按得分降序排序
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 获取主要体质
        primary_type = None
        for constitution_type, score in sorted_types:
            threshold = self.constitution_features[constitution_type].get("score_threshold", 0.6)
            if score >= threshold:
                primary_type = constitution_type
                break
        
        # 如果没有体质得分超过阈值，则取得分最高的
        if primary_type is None and sorted_types:
            primary_type = sorted_types[0][0]
        
        # 获取次要体质（得分超过25%的）
        secondary_types = []
        for constitution_type, score in sorted_types:
            if constitution_type != primary_type and score >= 0.25:
                secondary_types.append(constitution_type)
        
        # 最多返回3个次要体质
        return primary_type, secondary_types[:3]
    
    def get_questionnaire(self) -> List[Dict[str, Any]]:
        """获取体质辨别问卷"""
        questionnaire_dict = []
        for question in self.questionnaire:
            questionnaire_dict.append({
                "id": question.id,
                "question": question.question,
                "category": question.category,
                "options": question.options
            })
        return questionnaire_dict
    
    def get_constitution_features(self, constitution_type: ConstitutionType) -> Dict[str, Any]:
        """获取指定体质类型的特征描述"""
        return self.constitution_features.get(constitution_type, {})
    
    def get_constitution_recommendations(self, constitution_type: ConstitutionType) -> Dict[str, Any]:
        """获取指定体质类型的调理推荐方案"""
        return self.constitution_recommendations.get(constitution_type, {})
    
    def analyze_with_four_diagnosis(self, diagnosis_data: 'DiagnosisData') -> ConstitutionResult:
        """
        结合四诊合参数据进行体质辨别
        
        Args:
            diagnosis_data: 四诊合参数据对象
            
        Returns:
            ConstitutionResult: 体质辨别结果
        """
        # 构建诊断数据字典
        diagnostic_data = {}
        
        # 添加舌诊数据
        if hasattr(diagnosis_data, 'tongue_data') and diagnosis_data.tongue_data:
            diagnostic_data["tongue_data"] = diagnosis_data.tongue_data.__dict__
        
        # 添加脉诊数据
        if hasattr(diagnosis_data, 'pulse_data') and diagnosis_data.pulse_data:
            diagnostic_data["pulse_data"] = diagnosis_data.pulse_data.__dict__
        
        # 添加面诊数据
        if hasattr(diagnosis_data, 'face_data') and diagnosis_data.face_data:
            diagnostic_data["face_data"] = diagnosis_data.face_data.__dict__
        
        # 添加问诊数据
        if hasattr(diagnosis_data, 'inquiry_data') and diagnosis_data.inquiry_data:
            inquiry_dict = {}
            for key, value in diagnosis_data.inquiry_data.__dict__.items():
                if not key.startswith('_'):
                    inquiry_dict[key] = value
            diagnostic_data["inquiry_data"] = inquiry_dict
        
        # 使用诊断数据进行体质辨别
        return self.identify_constitution(diagnostic_data=diagnostic_data)
    
    def generate_comprehensive_report(self, result: ConstitutionResult) -> Dict[str, Any]:
        """
        生成全面的体质报告
        
        Args:
            result: 体质辨别结果
            
        Returns:
            Dict[str, Any]: 全面的体质报告
        """
        # 创建报告
        report = {
            "timestamp": result.timestamp.isoformat(),
            "constitution_profile": {
                "primary_type": result.primary_type.value if result.primary_type else None,
                "primary_score": result.scores.get(result.primary_type, 0) if result.primary_type else 0,
                "secondary_types": [t.value for t in result.secondary_types],
                "all_scores": {t.value: score for t, score in result.scores.items()}
            },
            "features": {},
            "recommendations": {}
        }
        
        # 添加主要体质特征和推荐
        if result.primary_type:
            primary_features = result.features.get(result.primary_type, {})
            primary_recommendations = result.recommendations.get(result.primary_type, {})
            
            report["features"]["primary"] = {
                "type": result.primary_type.value,
                "description": primary_features.get("description", ""),
                "characteristics": primary_features.get("characteristics", []),
                "traditional_description": primary_features.get("traditional_description", ""),
                "disease_tendency": primary_features.get("disease_tendency", [])
            }
            
            report["recommendations"]["primary"] = {
                "type": result.primary_type.value,
                "diet": primary_recommendations.get("diet", []),
                "exercise": primary_recommendations.get("exercise", []),
                "acupoints": primary_recommendations.get("acupoints", []),
                "herbs": primary_recommendations.get("herbs", []),
                "lifestyle": primary_recommendations.get("lifestyle", []),
                "seasonal_advice": primary_recommendations.get("seasonal_advice", {})
            }
        
        # 添加次要体质特征和推荐
        report["features"]["secondary"] = []
        report["recommendations"]["secondary"] = []
        
        for constitution_type in result.secondary_types:
            features = result.features.get(constitution_type, {})
            recommendations = result.recommendations.get(constitution_type, {})
            
            report["features"]["secondary"].append({
                "type": constitution_type.value,
                "description": features.get("description", ""),
                "characteristics": features.get("characteristics", []),
                "traditional_description": features.get("traditional_description", ""),
                "disease_tendency": features.get("disease_tendency", [])
            })
            
            report["recommendations"]["secondary"].append({
                "type": constitution_type.value,
                "diet": recommendations.get("diet", []),
                "exercise": recommendations.get("exercise", []),
                "acupoints": recommendations.get("acupoints", []),
                "herbs": recommendations.get("herbs", []),
                "lifestyle": recommendations.get("lifestyle", []),
                "seasonal_advice": recommendations.get("seasonal_advice", {})
            })
        
        # 添加定制的综合推荐
        report["integrated_recommendations"] = self._generate_integrated_recommendations(result)
        
        return report
    
    def _generate_integrated_recommendations(self, result: ConstitutionResult) -> Dict[str, Any]:
        """生成综合的调理推荐方案"""
        integrated = {
            "overview": "",
            "diet": [],
            "exercise": [],
            "lifestyle": [],
            "seasonal_focus": {}
        }
        
        # 如果没有主要体质，则返回空推荐
        if not result.primary_type:
            integrated["overview"] = "无法确定明确的体质类型，建议咨询专业中医师进行详细辨识。"
            return integrated
        
        # 添加概述
        primary_name = result.primary_type.value
        secondary_names = [t.value for t in result.secondary_types]
        
        if secondary_names:
            integrated["overview"] = f"您的体质主要为{primary_name}，兼有{', '.join(secondary_names)}特征。"
        else:
            integrated["overview"] = f"您的体质主要为{primary_name}。"
        
        # 合并主要和次要体质的推荐
        all_types = [result.primary_type] + result.secondary_types
        
        # 汇总饮食建议（去重）
        diet_recommendations = set()
        for t in all_types:
            recs = result.recommendations.get(t, {}).get("diet", [])
            for rec in recs:
                diet_recommendations.add(rec)
        
        # 汇总运动建议（去重）
        exercise_recommendations = set()
        for t in all_types:
            recs = result.recommendations.get(t, {}).get("exercise", [])
            for rec in recs:
                exercise_recommendations.add(rec)
        
        # 汇总生活方式建议（去重）
        lifestyle_recommendations = set()
        for t in all_types:
            recs = result.recommendations.get(t, {}).get("lifestyle", [])
            for rec in recs:
                lifestyle_recommendations.add(rec)
        
        # 季节性建议（以主要体质为主）
        seasonal_advice = {}
        if result.primary_type:
            seasonal_advice = result.recommendations.get(result.primary_type, {}).get("seasonal_advice", {})
        
        # 组装综合推荐
        integrated["diet"] = list(diet_recommendations)
        integrated["exercise"] = list(exercise_recommendations)
        integrated["lifestyle"] = list(lifestyle_recommendations)
        integrated["seasonal_focus"] = seasonal_advice
        
        return integrated


# 示例用法
if __name__ == "__main__":
    # 创建体质辨别器实例
    identifier = ConstitutionIdentifier()
    
    # 示例问卷回答
    sample_answers = {
        "B001": "是",
        "B002": "是",
        "Q001": "偶尔",
        "Y001": "很少",
        "YY001": "很少",
        "T001": "偶尔",
        "S001": "很少",
        "X001": "否",
        "QY001": "偶尔",
        "TB001": "否"
    }
    
    # 进行体质辨别
    result = identifier.identify_constitution(questionnaire_answers=sample_answers)
    
    # 生成体质报告
    report = identifier.generate_comprehensive_report(result)
    
    # 打印报告
    print(json.dumps(report, ensure_ascii=False, indent=2))
    
    # 获取问卷
    questionnaire = identifier.get_questionnaire()
    print(f"问卷题目数量: {len(questionnaire)}")