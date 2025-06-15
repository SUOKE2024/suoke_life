"""
AI文本分析器

使用机器学习模型对文本内容进行智能分析，包括：
- 内容质量评估
- 风险等级判断
- 情感分析
- 关键词提取
- 合规性检查
"""
import asyncio
import logging
import re
from typing import Any, Dict, List, Optional

import jieba
import numpy as np
from textblob import TextBlob

from internal.config.settings import get_settings
from internal.models.review_models import RiskLevel

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """文本分析器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.risk_keywords = self._load_risk_keywords()
        self.medical_terms = self._load_medical_terms()
        self.compliance_patterns = self._load_compliance_patterns()
        
    def _load_risk_keywords(self) -> Dict[str, List[str]]:
        """加载风险关键词"""
        return {
            "high_risk": [
                "毒性", "副作用", "禁忌", "过敏", "中毒", "致命", "危险",
                "不良反应", "严重", "急性", "慢性", "并发症", "感染"
            ],
            "medium_risk": [
                "注意", "谨慎", "小心", "可能", "风险", "建议", "咨询",
                "医生", "专业", "诊断", "治疗", "用药", "剂量"
            ],
            "medical_claims": [
                "治愈", "根治", "特效", "神药", "包治", "立即见效",
                "100%有效", "无副作用", "纯天然", "祖传秘方"
            ]
        }
    
    def _load_medical_terms(self) -> List[str]:
        """加载医学术语"""
        return [
            "症状", "诊断", "治疗", "药物", "疾病", "病理", "生理",
            "解剖", "病因", "预后", "康复", "护理", "检查", "化验",
            "手术", "麻醉", "急救", "预防", "保健", "营养", "运动"
        ]
    
    def _load_compliance_patterns(self) -> List[str]:
        """加载合规性检查模式"""
        return [
            r"包治.*病",
            r"立即.*效",
            r"100%.*效",
            r"无.*副作用",
            r"祖传.*方",
            r"神.*药",
            r"特.*效",
            r"根.*治"
        ]
    
    async def analyze_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析文本内容
        
        Args:
            text: 待分析的文本
            context: 上下文信息
            
        Returns:
            分析结果字典
        """
        try:
            # 基础文本处理
            cleaned_text = self._preprocess_text(text)
            
            # 并行执行各种分析
            results = await asyncio.gather(
                self._analyze_quality(cleaned_text),
                self._analyze_risk(cleaned_text),
                self._analyze_sentiment(cleaned_text),
                self._extract_keywords(cleaned_text),
                self._check_compliance(cleaned_text),
                self._analyze_medical_content(cleaned_text),
                return_exceptions=True
            )
            
            # 整合分析结果
            quality_result, risk_result, sentiment_result, keywords_result, \
            compliance_result, medical_result = results
            
            # 计算综合评分
            overall_score = self._calculate_overall_score(
                quality_result.get('score', 0.5) if isinstance(quality_result, dict) else 0.5,
                risk_result.get('score', 0.5) if isinstance(risk_result, dict) else 0.5,
                compliance_result.get('score', 0.5) if isinstance(compliance_result, dict) else 0.5
            )
            
            # 确定风险等级
            risk_level = self._determine_risk_level(
                risk_result.get('level', 'medium') if isinstance(risk_result, dict) else 'medium',
                compliance_result.get('violations', []) if isinstance(compliance_result, dict) else []
            )
            
            return {
                'overall_score': overall_score,
                'risk_level': risk_level,
                'confidence': min(0.9, overall_score + 0.1),
                'quality': quality_result if isinstance(quality_result, dict) else {'error': str(quality_result)},
                'risk': risk_result if isinstance(risk_result, dict) else {'error': str(risk_result)},
                'sentiment': sentiment_result if isinstance(sentiment_result, dict) else {'error': str(sentiment_result)},
                'keywords': keywords_result if isinstance(keywords_result, dict) else {'error': str(keywords_result)},
                'compliance': compliance_result if isinstance(compliance_result, dict) else {'error': str(compliance_result)},
                'medical': medical_result if isinstance(medical_result, dict) else {'error': str(medical_result)},
                'metadata': {
                    'text_length': len(text),
                    'cleaned_length': len(cleaned_text),
                    'language': self._detect_language(text),
                    'processing_time': 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"文本分析失败: {e}")
            return {
                'overall_score': 0.5,
                'risk_level': RiskLevel.MEDIUM,
                'confidence': 0.1,
                'error': str(e)
            }
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符（保留中文、英文、数字、基本标点）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,!?;:()（）。，！？；：]', '', text)
        
        return text
    
    async def _analyze_quality(self, text: str) -> Dict[str, Any]:
        """分析文本质量"""
        try:
            # 长度评分
            length_score = min(1.0, len(text) / 100)
            
            # 结构评分
            sentences = re.split(r'[。！？.!?]', text)
            structure_score = min(1.0, len([s for s in sentences if s.strip()]) / 5)
            
            # 词汇丰富度
            words = list(jieba.cut(text))
            unique_words = set(words)
            vocabulary_score = min(1.0, len(unique_words) / max(1, len(words)))
            
            # 可读性评分
            avg_sentence_length = len(text) / max(1, len(sentences))
            readability_score = max(0, 1.0 - (avg_sentence_length - 20) / 50)
            
            overall_quality = (length_score + structure_score + vocabulary_score + readability_score) / 4
            
            return {
                'score': overall_quality,
                'details': {
                    'length_score': length_score,
                    'structure_score': structure_score,
                    'vocabulary_score': vocabulary_score,
                    'readability_score': readability_score
                }
            }
            
        except Exception as e:
            logger.error(f"质量分析失败: {e}")
            return {'score': 0.5, 'error': str(e)}
    
    async def _analyze_risk(self, text: str) -> Dict[str, Any]:
        """分析风险等级"""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # 检查高风险关键词
            high_risk_count = sum(1 for keyword in self.risk_keywords['high_risk'] if keyword in text)
            if high_risk_count > 0:
                risk_score += high_risk_count * 0.3
                risk_factors.append(f"包含高风险关键词: {high_risk_count}个")
            
            # 检查中风险关键词
            medium_risk_count = sum(1 for keyword in self.risk_keywords['medium_risk'] if keyword in text)
            if medium_risk_count > 0:
                risk_score += medium_risk_count * 0.1
                risk_factors.append(f"包含中风险关键词: {medium_risk_count}个")
            
            # 检查医疗声明
            medical_claims_count = sum(1 for keyword in self.risk_keywords['medical_claims'] if keyword in text)
            if medical_claims_count > 0:
                risk_score += medical_claims_count * 0.4
                risk_factors.append(f"包含医疗声明: {medical_claims_count}个")
            
            # 确定风险等级
            if risk_score >= self.settings.ai.risk_threshold_high:
                level = RiskLevel.HIGH
            elif risk_score >= self.settings.ai.risk_threshold_medium:
                level = RiskLevel.MEDIUM
            elif risk_score >= self.settings.ai.risk_threshold_low:
                level = RiskLevel.LOW
            else:
                level = RiskLevel.VERY_LOW
            
            return {
                'score': min(1.0, risk_score),
                'level': level,
                'factors': risk_factors
            }
            
        except Exception as e:
            logger.error(f"风险分析失败: {e}")
            return {'score': 0.5, 'level': RiskLevel.MEDIUM, 'error': str(e)}
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析情感倾向"""
        try:
            # 使用TextBlob进行情感分析
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # 转换为更直观的分类
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity)
            }
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {'sentiment': 'neutral', 'error': str(e)}
    
    async def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """提取关键词"""
        try:
            # 使用jieba分词
            words = list(jieba.cut(text))
            
            # 过滤停用词和短词
            filtered_words = [word for word in words if len(word) > 1 and word not in ['的', '了', '在', '是', '有', '和', '与']]
            
            # 计算词频
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 排序并取前10个关键词
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # 识别医学术语
            medical_keywords = [word for word, _ in keywords if word in self.medical_terms]
            
            return {
                'keywords': [{'word': word, 'frequency': freq} for word, freq in keywords],
                'medical_terms': medical_keywords,
                'total_words': len(words),
                'unique_words': len(set(words))
            }
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return {'keywords': [], 'error': str(e)}
    
    async def _check_compliance(self, text: str) -> Dict[str, Any]:
        """检查合规性"""
        try:
            violations = []
            compliance_score = 1.0
            
            # 检查违规模式
            for pattern in self.compliance_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    violations.append({
                        'pattern': pattern,
                        'matches': matches,
                        'severity': 'high'
                    })
                    compliance_score -= 0.2
            
            # 检查过度医疗声明
            medical_claims = [claim for claim in self.risk_keywords['medical_claims'] if claim in text]
            if medical_claims:
                violations.append({
                    'type': 'medical_claims',
                    'claims': medical_claims,
                    'severity': 'high'
                })
                compliance_score -= len(medical_claims) * 0.1
            
            compliance_score = max(0.0, compliance_score)
            
            return {
                'score': compliance_score,
                'violations': violations,
                'is_compliant': len(violations) == 0
            }
            
        except Exception as e:
            logger.error(f"合规性检查失败: {e}")
            return {'score': 0.5, 'violations': [], 'error': str(e)}
    
    async def _analyze_medical_content(self, text: str) -> Dict[str, Any]:
        """分析医学内容"""
        try:
            medical_score = 0.0
            medical_indicators = []
            
            # 检查医学术语密度
            words = list(jieba.cut(text))
            medical_word_count = sum(1 for word in words if word in self.medical_terms)
            medical_density = medical_word_count / max(1, len(words))
            
            if medical_density > 0.1:
                medical_score += 0.5
                medical_indicators.append(f"医学术语密度: {medical_density:.2%}")
            
            # 检查症状描述
            symptom_patterns = [r'症状', r'疼痛', r'不适', r'异常', r'发热', r'咳嗽']
            symptom_count = sum(1 for pattern in symptom_patterns if re.search(pattern, text))
            if symptom_count > 0:
                medical_score += 0.3
                medical_indicators.append(f"症状描述: {symptom_count}个")
            
            # 检查治疗建议
            treatment_patterns = [r'治疗', r'用药', r'服用', r'建议', r'方案']
            treatment_count = sum(1 for pattern in treatment_patterns if re.search(pattern, text))
            if treatment_count > 0:
                medical_score += 0.2
                medical_indicators.append(f"治疗建议: {treatment_count}个")
            
            return {
                'score': min(1.0, medical_score),
                'is_medical_content': medical_score > 0.3,
                'medical_density': medical_density,
                'indicators': medical_indicators
            }
            
        except Exception as e:
            logger.error(f"医学内容分析失败: {e}")
            return {'score': 0.0, 'is_medical_content': False, 'error': str(e)}
    
    def _calculate_overall_score(self, quality_score: float, risk_score: float, compliance_score: float) -> float:
        """计算综合评分"""
        # 权重分配：质量40%，风险30%，合规30%
        overall = (quality_score * 0.4 + (1 - risk_score) * 0.3 + compliance_score * 0.3)
        return max(0.0, min(1.0, overall))
    
    def _determine_risk_level(self, risk_level: str, violations: List[Dict]) -> RiskLevel:
        """确定最终风险等级"""
        if violations and any(v.get('severity') == 'high' for v in violations):
            return RiskLevel.HIGH
        
        if risk_level == 'high':
            return RiskLevel.HIGH
        elif risk_level == 'medium':
            return RiskLevel.MEDIUM
        elif risk_level == 'low':
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def _detect_language(self, text: str) -> str:
        """检测文本语言"""
        # 简单的语言检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > english_chars:
            return 'zh'
        elif english_chars > 0:
            return 'en'
        else:
            return 'unknown'
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试分析功能
            test_text = "这是一个测试文本"
            result = await self.analyze_text(test_text)
            
            return {
                'status': 'healthy',
                'test_result': result.get('overall_score', 0) > 0
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            } 