"""
data_enhancement_pipeline - 索克生活项目模块
"""

    import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from transformers import AutoTokenizer, AutoModel
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import cv2
import jieba
import json
import librosa
import logging
import numpy as np
import pandas as pd
import re
import torch
import torch.nn as nn

"""
数据质量提升管道 - 五诊系统数据增强
包含数据清洗、增强、验证和知识库优化
"""


logger = logging.getLogger(__name__)

@dataclass
class DataQualityMetrics:
    """数据质量指标"""
    completeness: float  # 完整性
    accuracy: float      # 准确性
    consistency: float   # 一致性
    validity: float      # 有效性
    uniqueness: float    # 唯一性
    overall_score: float # 总体评分

@dataclass
class EnhancementResult:
    """数据增强结果"""
    original_size: int
    enhanced_size: int
    quality_improvement: float
    processing_time: float
    success: bool

class TCMKnowledgeBase:
    """中医知识库"""
    
    def __init__(self):
        self.symptoms_dict = self._load_symptoms_dictionary()
        self.syndrome_patterns = self._load_syndrome_patterns()
        self.constitution_types = self._load_constitution_types()
        self.pulse_types = self._load_pulse_types()
        self.tongue_features = self._load_tongue_features()
    
    def _load_symptoms_dictionary(self) -> Dict[str, Any]:
        """加载症状词典"""
        return {
            "头痛": {
                "category": "头部症状",
                "severity_levels": ["轻微", "中等", "严重"],
                "related_organs": ["肝", "肾", "心"],
                "common_syndromes": ["肝阳上亢", "肾虚", "血瘀"]
            },
            "咳嗽": {
                "category": "呼吸系统",
                "severity_levels": ["偶发", "频繁", "持续"],
                "related_organs": ["肺", "脾", "肾"],
                "common_syndromes": ["肺热", "肺燥", "肺虚"]
            },
            "失眠": {
                "category": "神志症状",
                "severity_levels": ["入睡困难", "易醒", "彻夜不眠"],
                "related_organs": ["心", "肝", "肾"],
                "common_syndromes": ["心肾不交", "肝郁化火", "心脾两虚"]
            }
        }
    
    def _load_syndrome_patterns(self) -> Dict[str, Any]:
        """加载证候模式"""
        return {
            "肝阳上亢": {
                "main_symptoms": ["头痛", "眩晕", "急躁易怒"],
                "tongue": "红舌",
                "pulse": "弦脉",
                "treatment_principle": "平肝潜阳"
            },
            "肾阴虚": {
                "main_symptoms": ["腰膝酸软", "五心烦热", "盗汗"],
                "tongue": "红舌少苔",
                "pulse": "细数脉",
                "treatment_principle": "滋阴补肾"
            }
        }
    
    def _load_constitution_types(self) -> Dict[str, Any]:
        """加载体质类型"""
        return {
            "平和质": {"characteristics": ["精力充沛", "睡眠良好", "性格开朗"]},
            "气虚质": {"characteristics": ["疲乏无力", "气短懒言", "易感冒"]},
            "阳虚质": {"characteristics": ["畏寒怕冷", "手足不温", "精神不振"]},
            "阴虚质": {"characteristics": ["手足心热", "口燥咽干", "喜冷饮"]},
            "痰湿质": {"characteristics": ["形体肥胖", "腹部肥满", "口黏腻"]},
            "湿热质": {"characteristics": ["面垢油腻", "口苦", "身重困倦"]},
            "血瘀质": {"characteristics": ["肤色晦暗", "色素沉着", "易出血"]},
            "气郁质": {"characteristics": ["神情抑郁", "情绪不稳", "胸胁胀满"]},
            "特禀质": {"characteristics": ["过敏体质", "遗传缺陷", "胎传异常"]}
        }
    
    def _load_pulse_types(self) -> Dict[str, Any]:
        """加载脉象类型"""
        return {
            "浮脉": {"position": "浮", "rate": "正常", "strength": "有力", "meaning": "表证"},
            "沉脉": {"position": "沉", "rate": "正常", "strength": "有力", "meaning": "里证"},
            "迟脉": {"position": "正常", "rate": "缓慢", "strength": "正常", "meaning": "寒证"},
            "数脉": {"position": "正常", "rate": "快速", "strength": "正常", "meaning": "热证"},
            "弦脉": {"position": "正常", "rate": "正常", "strength": "紧张", "meaning": "肝胆病"},
            "滑脉": {"position": "正常", "rate": "正常", "strength": "流利", "meaning": "痰湿"},
            "细脉": {"position": "正常", "rate": "正常", "strength": "微弱", "meaning": "血虚"},
            "洪脉": {"position": "浮", "rate": "正常", "strength": "强盛", "meaning": "热盛"}
        }
    
    def _load_tongue_features(self) -> Dict[str, Any]:
        """加载舌象特征"""
        return {
            "舌质": {
                "淡红": "正常",
                "红": "热证",
                "绛": "热入营血",
                "淡白": "虚寒",
                "紫": "血瘀"
            },
            "舌苔": {
                "薄白": "正常",
                "厚白": "痰湿",
                "黄": "热证",
                "黑": "热极",
                "无苔": "阴虚"
            }
        }

class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        self.tcm_kb = TCMKnowledgeBase()
    
    async def clean_text_data(self, texts: List[str]) -> List[str]:
        """清洗文本数据"""
        cleaned_texts = []
        
        for text in texts:
            if not text or not isinstance(text, str):
                continue
            
            # 去除特殊字符
            cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？；：]', '', text)
            
            # 去除过短或过长的文本
            if 2 <= len(cleaned) <= 1000:
                cleaned_texts.append(cleaned)
        
        logger.info(f"文本清洗完成: {len(texts)} -> {len(cleaned_texts)}")
        return cleaned_texts
    
    async def clean_image_data(self, image_paths: List[str]) -> List[str]:
        """清洗图像数据"""
        valid_images = []
        
        for path in image_paths:
            try:
                image = cv2.imread(path)
                if image is not None:
                    height, width = image.shape[:2]
                    
                    # 检查图像尺寸
                    if height >= 64 and width >= 64:
                        # 检查图像质量
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                        
                        # 过滤模糊图像
                        if laplacian_var > 100:
                            valid_images.append(path)
                            
            except Exception as e:
                logger.warning(f"图像处理失败 {path}: {e}")
        
        logger.info(f"图像清洗完成: {len(image_paths)} -> {len(valid_images)}")
        return valid_images
    
    async def clean_audio_data(self, audio_paths: List[str]) -> List[str]:
        """清洗音频数据"""
        valid_audios = []
        
        for path in audio_paths:
            try:
                y, sr = librosa.load(path, duration=30)
                
                # 检查音频长度
                if len(y) > sr * 0.5:  # 至少0.5秒
                    # 检查音频质量
                    rms = librosa.feature.rms(y=y)[0]
                    if np.mean(rms) > 0.01:  # 过滤静音
                        valid_audios.append(path)
                        
            except Exception as e:
                logger.warning(f"音频处理失败 {path}: {e}")
        
        logger.info(f"音频清洗完成: {len(audio_paths)} -> {len(valid_audios)}")
        return valid_audios
    
    async def clean_sensor_data(self, sensor_data: np.ndarray) -> np.ndarray:
        """清洗传感器数据"""
        if len(sensor_data) == 0:
            return sensor_data
        
        # 去除异常值
        Q1 = np.percentile(sensor_data, 25)
        Q3 = np.percentile(sensor_data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 过滤异常值
        mask = (sensor_data >= lower_bound) & (sensor_data <= upper_bound)
        cleaned_data = sensor_data[mask]
        
        logger.info(f"传感器数据清洗完成: {len(sensor_data)} -> {len(cleaned_data)}")
        return cleaned_data

class DataAugmentor:
    """数据增强器"""
    
    def __init__(self):
        self.tcm_kb = TCMKnowledgeBase()
    
    async def augment_text_data(self, texts: List[str], labels: List[str]) -> Tuple[List[str], List[str]]:
        """增强文本数据"""
        augmented_texts = texts.copy()
        augmented_labels = labels.copy()
        
        for text, label in zip(texts, labels):
            # 同义词替换
            augmented_text = await self._synonym_replacement(text)
            if augmented_text != text:
                augmented_texts.append(augmented_text)
                augmented_labels.append(label)
            
            # 句式变换
            transformed_text = await self._sentence_transformation(text)
            if transformed_text != text:
                augmented_texts.append(transformed_text)
                augmented_labels.append(label)
        
        logger.info(f"文本增强完成: {len(texts)} -> {len(augmented_texts)}")
        return augmented_texts, augmented_labels
    
    async def _synonym_replacement(self, text: str) -> str:
        """同义词替换"""
        # 中医术语同义词映射
        synonyms = {
            "头疼": "头痛",
            "肚子疼": "腹痛",
            "睡不着": "失眠",
            "没力气": "乏力",
            "心慌": "心悸"
        }
        
        for original, synonym in synonyms.items():
            if original in text:
                return text.replace(original, synonym)
        
        return text
    
    async def _sentence_transformation(self, text: str) -> str:
        """句式变换"""
        # 简单的句式变换
        if "我" in text and "感觉" in text:
            return text.replace("我感觉", "患者自述")
        elif "有点" in text:
            return text.replace("有点", "轻微")
        
        return text
    
    async def augment_image_data(self, image_paths: List[str]) -> List[str]:
        """增强图像数据"""
        augmented_paths = []
        
        for i, path in enumerate(image_paths):
            try:
                image = cv2.imread(path)
                if image is None:
                    continue
                
                # 旋转
                rotated = self._rotate_image(image, 15)
                rotated_path = f"augmented_rotated_{i}.jpg"
                cv2.imwrite(rotated_path, rotated)
                augmented_paths.append(rotated_path)
                
                # 亮度调整
                brightened = self._adjust_brightness(image, 1.2)
                bright_path = f"augmented_bright_{i}.jpg"
                cv2.imwrite(bright_path, brightened)
                augmented_paths.append(bright_path)
                
                # 对比度调整
                contrasted = self._adjust_contrast(image, 1.1)
                contrast_path = f"augmented_contrast_{i}.jpg"
                cv2.imwrite(contrast_path, contrasted)
                augmented_paths.append(contrast_path)
                
            except Exception as e:
                logger.warning(f"图像增强失败 {path}: {e}")
        
        logger.info(f"图像增强完成: {len(image_paths)} -> {len(augmented_paths)}")
        return image_paths + augmented_paths
    
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """旋转图像"""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (width, height))
    
    def _adjust_brightness(self, image: np.ndarray, factor: float) -> np.ndarray:
        """调整亮度"""
        return cv2.convertScaleAbs(image, alpha=factor, beta=0)
    
    def _adjust_contrast(self, image: np.ndarray, factor: float) -> np.ndarray:
        """调整对比度"""
        return cv2.convertScaleAbs(image, alpha=factor, beta=0)

class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.tcm_kb = TCMKnowledgeBase()
    
    async def validate_dataset(self, data: Dict[str, Any]) -> DataQualityMetrics:
        """验证数据集质量"""
        completeness = await self._check_completeness(data)
        accuracy = await self._check_accuracy(data)
        consistency = await self._check_consistency(data)
        validity = await self._check_validity(data)
        uniqueness = await self._check_uniqueness(data)
        
        overall_score = (completeness + accuracy + consistency + validity + uniqueness) / 5
        
        return DataQualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            validity=validity,
            uniqueness=uniqueness,
            overall_score=overall_score
        )
    
    async def _check_completeness(self, data: Dict[str, Any]) -> float:
        """检查完整性"""
        total_fields = 0
        complete_fields = 0
        
        for key, values in data.items():
            if isinstance(values, list):
                total_fields += len(values)
                complete_fields += sum(1 for v in values if v is not None and v != "")
        
        return complete_fields / total_fields if total_fields > 0 else 0.0
    
    async def _check_accuracy(self, data: Dict[str, Any]) -> float:
        """检查准确性"""
        # 基于中医知识库验证
        accurate_count = 0
        total_count = 0
        
        if "symptoms" in data:
            for symptom in data["symptoms"]:
                total_count += 1
                if symptom in self.tcm_kb.symptoms_dict:
                    accurate_count += 1
        
        return accurate_count / total_count if total_count > 0 else 1.0
    
    async def _check_consistency(self, data: Dict[str, Any]) -> float:
        """检查一致性"""
        # 检查数据格式一致性
        consistency_score = 1.0
        
        # 检查症状描述的一致性
        if "symptoms" in data:
            symptoms = data["symptoms"]
            if len(set(type(s).__name__ for s in symptoms)) > 1:
                consistency_score -= 0.2
        
        return max(0.0, consistency_score)
    
    async def _check_validity(self, data: Dict[str, Any]) -> float:
        """检查有效性"""
        valid_count = 0
        total_count = 0
        
        for key, values in data.items():
            if isinstance(values, list):
                for value in values:
                    total_count += 1
                    if await self._is_valid_value(key, value):
                        valid_count += 1
        
        return valid_count / total_count if total_count > 0 else 1.0
    
    async def _is_valid_value(self, field: str, value: Any) -> bool:
        """检查值是否有效"""
        if value is None or value == "":
            return False
        
        if field == "age" and isinstance(value, (int, float)):
            return 0 <= value <= 120
        elif field == "pulse_rate" and isinstance(value, (int, float)):
            return 40 <= value <= 200
        elif field == "temperature" and isinstance(value, (int, float)):
            return 35.0 <= value <= 42.0
        
        return True
    
    async def _check_uniqueness(self, data: Dict[str, Any]) -> float:
        """检查唯一性"""
        unique_score = 1.0
        
        for key, values in data.items():
            if isinstance(values, list) and len(values) > 0:
                unique_count = len(set(str(v) for v in values))
                total_count = len(values)
                field_uniqueness = unique_count / total_count
                unique_score = min(unique_score, field_uniqueness)
        
        return unique_score

class KnowledgeBaseEnhancer:
    """知识库增强器"""
    
    def __init__(self):
        self.tcm_kb = TCMKnowledgeBase()
    
    async def enhance_knowledge_base(self) -> Dict[str, Any]:
        """增强知识库"""
        enhanced_kb = {
            "symptoms": await self._enhance_symptoms_knowledge(),
            "syndromes": await self._enhance_syndrome_knowledge(),
            "treatments": await self._enhance_treatment_knowledge(),
            "herbs": await self._enhance_herb_knowledge()
        }
        
        return enhanced_kb
    
    async def _enhance_symptoms_knowledge(self) -> Dict[str, Any]:
        """增强症状知识"""
        enhanced_symptoms = self.tcm_kb.symptoms_dict.copy()
        
        # 添加症状关联性
        for symptom, info in enhanced_symptoms.items():
            info["related_symptoms"] = await self._find_related_symptoms(symptom)
            info["severity_indicators"] = await self._get_severity_indicators(symptom)
            info["temporal_patterns"] = await self._get_temporal_patterns(symptom)
        
        return enhanced_symptoms
    
    async def _find_related_symptoms(self, symptom: str) -> List[str]:
        """查找相关症状"""
        # 基于中医理论的症状关联
        relations = {
            "头痛": ["眩晕", "恶心", "视物模糊"],
            "咳嗽": ["咳痰", "胸闷", "气短"],
            "失眠": ["多梦", "心悸", "健忘"]
        }
        
        return relations.get(symptom, [])
    
    async def _get_severity_indicators(self, symptom: str) -> Dict[str, str]:
        """获取严重程度指标"""
        indicators = {
            "头痛": {
                "轻微": "偶发性，不影响日常活动",
                "中等": "持续性，影响工作效率",
                "严重": "剧烈疼痛，无法正常活动"
            },
            "咳嗽": {
                "轻微": "偶尔干咳，无痰",
                "中等": "频繁咳嗽，有少量痰",
                "严重": "剧烈咳嗽，大量痰液"
            }
        }
        
        return indicators.get(symptom, {})
    
    async def _get_temporal_patterns(self, symptom: str) -> Dict[str, str]:
        """获取时间模式"""
        patterns = {
            "头痛": {
                "晨起": "可能与高血压相关",
                "午后": "可能与疲劳相关",
                "夜间": "可能与肝阳上亢相关"
            },
            "失眠": {
                "入睡困难": "多为肝郁气滞",
                "易醒": "多为心脾两虚",
                "早醒": "多为肝肾阴虚"
            }
        }
        
        return patterns.get(symptom, {})
    
    async def _enhance_syndrome_knowledge(self) -> Dict[str, Any]:
        """增强证候知识"""
        enhanced_syndromes = self.tcm_kb.syndrome_patterns.copy()
        
        for syndrome, info in enhanced_syndromes.items():
            info["diagnostic_criteria"] = await self._get_diagnostic_criteria(syndrome)
            info["differential_diagnosis"] = await self._get_differential_diagnosis(syndrome)
            info["prognosis"] = await self._get_prognosis(syndrome)
        
        return enhanced_syndromes
    
    async def _get_diagnostic_criteria(self, syndrome: str) -> Dict[str, Any]:
        """获取诊断标准"""
        criteria = {
            "肝阳上亢": {
                "主症": ["头痛眩晕", "急躁易怒"],
                "次症": ["面红目赤", "口苦咽干"],
                "舌脉": ["舌红苔黄", "脉弦数"]
            }
        }
        
        return criteria.get(syndrome, {})
    
    async def _get_differential_diagnosis(self, syndrome: str) -> List[str]:
        """获取鉴别诊断"""
        differentials = {
            "肝阳上亢": ["肝火上炎", "肝风内动", "痰火扰心"],
            "肾阴虚": ["肾阳虚", "心肾不交", "肝肾阴虚"]
        }
        
        return differentials.get(syndrome, [])
    
    async def _get_prognosis(self, syndrome: str) -> str:
        """获取预后"""
        prognosis = {
            "肝阳上亢": "及时治疗预后良好，需注意情志调节",
            "肾阴虚": "需长期调理，配合生活方式改善"
        }
        
        return prognosis.get(syndrome, "需要专业医师评估")
    
    async def _enhance_treatment_knowledge(self) -> Dict[str, Any]:
        """增强治疗知识"""
        return {
            "acupuncture_points": await self._get_acupuncture_knowledge(),
            "herbal_formulas": await self._get_herbal_formulas(),
            "lifestyle_advice": await self._get_lifestyle_advice()
        }
    
    async def _get_acupuncture_knowledge(self) -> Dict[str, Any]:
        """获取针灸知识"""
        return {
            "头痛": {
                "主穴": ["百会", "太阳", "风池"],
                "配穴": ["合谷", "太冲", "印堂"],
                "手法": "平补平泻"
            },
            "失眠": {
                "主穴": ["神门", "三阴交", "百会"],
                "配穴": ["心俞", "肾俞", "安眠"],
                "手法": "补法为主"
            }
        }
    
    async def _get_herbal_formulas(self) -> Dict[str, Any]:
        """获取方剂知识"""
        return {
            "肝阳上亢": {
                "主方": "天麻钩藤饮",
                "组成": ["天麻", "钩藤", "石决明", "栀子"],
                "功效": "平肝息风，清热安神"
            },
            "肾阴虚": {
                "主方": "六味地黄丸",
                "组成": ["熟地黄", "山茱萸", "山药", "泽泻"],
                "功效": "滋阴补肾"
            }
        }
    
    async def _get_lifestyle_advice(self) -> Dict[str, Any]:
        """获取生活方式建议"""
        return {
            "肝阳上亢": {
                "饮食": "清淡饮食，少食辛辣",
                "运动": "适量运动，避免剧烈运动",
                "情志": "保持心情平和，避免急躁"
            },
            "肾阴虚": {
                "饮食": "滋阴润燥，多食黑色食物",
                "运动": "太极拳、八段锦等柔和运动",
                "作息": "规律作息，避免熬夜"
            }
        }
    
    async def _enhance_herb_knowledge(self) -> Dict[str, Any]:
        """增强药物知识"""
        return {
            "天麻": {
                "性味": "甘，平",
                "归经": "肝经",
                "功效": "息风止痉，平抑肝阳",
                "主治": ["头痛眩晕", "肢体麻木", "小儿惊风"],
                "用量": "3-9g",
                "注意": "血虚无风者慎用"
            },
            "钩藤": {
                "性味": "甘，微寒",
                "归经": "肝、心包经",
                "功效": "息风止痉，清热平肝",
                "主治": ["头痛眩晕", "高血压", "小儿惊风"],
                "用量": "3-12g",
                "注意": "久煎降效"
            }
        }

class DataEnhancementPipeline:
    """数据增强管道主类"""
    
    def __init__(self):
        self.cleaner = DataCleaner()
        self.augmentor = DataAugmentor()
        self.validator = DataValidator()
        self.kb_enhancer = KnowledgeBaseEnhancer()
    
    async def run_enhancement_pipeline(self, raw_data: Dict[str, Any]) -> EnhancementResult:
        """运行数据增强管道"""
        logger.info("开始数据质量提升管道...")
        start_time = time.time()
        
        try:
            original_size = self._calculate_data_size(raw_data)
            
            # 1. 数据清洗
            cleaned_data = await self._clean_all_data(raw_data)
            
            # 2. 数据增强
            enhanced_data = await self._augment_all_data(cleaned_data)
            
            # 3. 数据验证
            quality_metrics = await self.validator.validate_dataset(enhanced_data)
            
            # 4. 知识库增强
            enhanced_kb = await self.kb_enhancer.enhance_knowledge_base()
            
            # 5. 保存结果
            await self._save_enhanced_data(enhanced_data, enhanced_kb)
            
            enhanced_size = self._calculate_data_size(enhanced_data)
            processing_time = time.time() - start_time
            
            result = EnhancementResult(
                original_size=original_size,
                enhanced_size=enhanced_size,
                quality_improvement=quality_metrics.overall_score,
                processing_time=processing_time,
                success=True
            )
            
            logger.info(f"数据增强完成，质量评分: {quality_metrics.overall_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"数据增强失败: {e}")
            return EnhancementResult(
                original_size=0,
                enhanced_size=0,
                quality_improvement=0.0,
                processing_time=time.time() - start_time,
                success=False
            )
    
    async def _clean_all_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗所有数据"""
        cleaned_data = {}
        
        if "texts" in raw_data:
            cleaned_data["texts"] = await self.cleaner.clean_text_data(raw_data["texts"])
        
        if "images" in raw_data:
            cleaned_data["images"] = await self.cleaner.clean_image_data(raw_data["images"])
        
        if "audios" in raw_data:
            cleaned_data["audios"] = await self.cleaner.clean_audio_data(raw_data["audios"])
        
        if "sensors" in raw_data:
            cleaned_data["sensors"] = await self.cleaner.clean_sensor_data(raw_data["sensors"])
        
        return cleaned_data
    
    async def _augment_all_data(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """增强所有数据"""
        enhanced_data = cleaned_data.copy()
        
        if "texts" in cleaned_data and "labels" in cleaned_data:
            enhanced_texts, enhanced_labels = await self.augmentor.augment_text_data(
                cleaned_data["texts"], cleaned_data["labels"]
            )
            enhanced_data["texts"] = enhanced_texts
            enhanced_data["labels"] = enhanced_labels
        
        if "images" in cleaned_data:
            enhanced_data["images"] = await self.augmentor.augment_image_data(cleaned_data["images"])
        
        return enhanced_data
    
    def _calculate_data_size(self, data: Dict[str, Any]) -> int:
        """计算数据大小"""
        total_size = 0
        for key, values in data.items():
            if isinstance(values, list):
                total_size += len(values)
        return total_size
    
    async def _save_enhanced_data(self, enhanced_data: Dict[str, Any], enhanced_kb: Dict[str, Any]):
        """保存增强后的数据"""
        # 保存增强数据
        data_path = Path("enhanced_data")
        data_path.mkdir(exist_ok=True)
        
        with open(data_path / "enhanced_dataset.json", 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存增强知识库
        kb_path = Path("enhanced_knowledge_base")
        kb_path.mkdir(exist_ok=True)
        
        with open(kb_path / "enhanced_tcm_kb.json", 'w', encoding='utf-8') as f:
            json.dump(enhanced_kb, f, ensure_ascii=False, indent=2)
        
        logger.info("增强数据和知识库已保存")

async def run_data_enhancement():
    """运行数据增强"""
    # 模拟原始数据
    raw_data = {
        "texts": ["头疼", "睡不着觉", "肚子疼", "没力气"],
        "labels": ["头痛", "失眠", "腹痛", "乏力"],
        "images": ["face1.jpg", "tongue1.jpg", "eye1.jpg"],
        "audios": ["voice1.wav", "cough1.wav", "breath1.wav"],
        "sensors": np.random.randn(1000)
    }
    
    pipeline = DataEnhancementPipeline()
    result = await pipeline.run_enhancement_pipeline(raw_data)
    
    return result

if __name__ == "__main__":
    
    result = asyncio.run(run_data_enhancement())
    
    print(f"数据质量提升结果:")
    print(f"  成功: {result.success}")
    print(f"  原始数据量: {result.original_size}")
    print(f"  增强数据量: {result.enhanced_size}")
    print(f"  质量提升: {result.quality_improvement:.3f}")
    print(f"  处理时间: {result.processing_time:.2f}秒") 