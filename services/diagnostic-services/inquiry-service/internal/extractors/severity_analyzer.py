#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
严重程度分析器
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from ..common.base import BaseService
from ..common.logging import get_logger
from ..common.utils import sanitize_text, calculate_confidence


class SeverityAnalyzer(BaseService):
    """严重程度分析器"""
    
    async def _do_initialize(self) -> None:
        """初始化严重程度分析器"""
        # 严重程度关键词
        self.severity_keywords = {
            'mild': {
                'keywords': [
                    "轻微", "轻度", "一点", "有点", "稍微", "略微", "偶尔",
                    "不太", "不是很", "还好", "可以忍受", "不严重"
                ],
                'score': 0.3
            },
            'moderate': {
                'keywords': [
                    "中等", "一般", "明显", "比较", "较为", "有些", "还是",
                    "挺", "蛮", "相当", "不轻", "不算轻"
                ],
                'score': 0.6
            },
            'severe': {
                'keywords': [
                    "严重", "剧烈", "强烈", "厉害", "很", "非常", "特别",
                    "极其", "十分", "相当", "异常", "难以忍受", "痛苦",
                    "要命", "受不了", "折磨"
                ],
                'score': 0.9
            }
        }
        
        # 程度修饰词
        self.intensity_modifiers = {
            'very_high': ["极其", "异常", "特别", "非常", "十分", "相当"],
            'high': ["很", "挺", "蛮", "比较", "较为"],
            'medium': ["有些", "有点", "一些", "还是"],
            'low': ["稍微", "略微", "一点", "不太"]
        }
        
        # 频率词汇
        self.frequency_words = {
            'always': ["总是", "一直", "持续", "不断", "经常"],
            'often': ["经常", "常常", "频繁", "反复"],
            'sometimes': ["有时", "偶尔", "间歇", "时而"],
            'rarely': ["很少", "偶尔", "极少"]
        }
        
        # 影响程度词汇
        self.impact_words = {
            'high_impact': [
                "无法", "不能", "难以", "影响", "干扰", "妨碍",
                "阻碍", "限制", "困难", "痛苦", "折磨"
            ],
            'medium_impact': [
                "有些影响", "稍有影响", "轻微影响", "不太方便"
            ],
            'low_impact': [
                "基本不影响", "影响不大", "还能", "勉强可以"
            ]
        }
        
        self.logger.info("严重程度分析器初始化完成")
    
    async def _do_health_check(self) -> bool:
        """健康检查"""
        try:
            # 测试严重程度分析
            test_result = await self.analyze_severity("我头很痛", "头痛")
            return test_result == "severe"
        except Exception:
            return False
    
    async def analyze_severity(self, text: str, symptom: str) -> str:
        """分析症状的严重程度"""
        try:
            cleaned_text = sanitize_text(text)
            
            # 获取症状周围的上下文
            context = self._extract_symptom_context(cleaned_text, symptom)
            
            # 计算各个严重程度的得分
            severity_scores = {}
            for severity, data in self.severity_keywords.items():
                score = self._calculate_severity_score(context, data['keywords'], data['score'])
                severity_scores[severity] = score
            
            # 应用修饰词加权
            severity_scores = self._apply_modifier_weights(context, severity_scores)
            
            # 应用频率加权
            severity_scores = self._apply_frequency_weights(context, severity_scores)
            
            # 应用影响程度加权
            severity_scores = self._apply_impact_weights(context, severity_scores)
            
            # 选择得分最高的严重程度
            if not severity_scores or all(score == 0 for score in severity_scores.values()):
                return "unknown"
            
            best_severity = max(severity_scores.items(), key=lambda x: x[1])
            
            # 如果得分太低，返回unknown
            if best_severity[1] < 0.3:
                return "unknown"
            
            return best_severity[0]
            
        except Exception as e:
            self.logger.error(f"严重程度分析失败: {str(e)}")
            return "unknown"
    
    async def analyze_detailed_severity(self, text: str, symptom: str) -> Dict[str, Any]:
        """详细的严重程度分析"""
        try:
            cleaned_text = sanitize_text(text)
            context = self._extract_symptom_context(cleaned_text, symptom)
            
            # 基础严重程度分析
            severity = await self.analyze_severity(text, symptom)
            
            # 详细分析
            analysis = {
                'severity': severity,
                'confidence': 0.0,
                'factors': {},
                'context': context,
                'modifiers': [],
                'frequency': None,
                'impact': None
            }
            
            # 分析修饰词
            modifiers = self._find_modifiers(context)
            analysis['modifiers'] = modifiers
            
            # 分析频率
            frequency = self._analyze_frequency(context)
            analysis['frequency'] = frequency
            
            # 分析影响程度
            impact = self._analyze_impact(context)
            analysis['impact'] = impact
            
            # 计算置信度
            confidence_factors = []
            if modifiers:
                confidence_factors.append(0.8)
            if frequency:
                confidence_factors.append(0.7)
            if impact:
                confidence_factors.append(0.9)
            if severity != "unknown":
                confidence_factors.append(0.6)
            
            analysis['confidence'] = calculate_confidence(confidence_factors) if confidence_factors else 0.0
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"详细严重程度分析失败: {str(e)}")
            return {'severity': 'unknown', 'confidence': 0.0}
    
    def _extract_symptom_context(self, text: str, symptom: str) -> str:
        """提取症状周围的上下文"""
        symptom_pos = text.find(symptom)
        if symptom_pos == -1:
            return text
        
        # 提取症状前后各20个字符的上下文
        start = max(0, symptom_pos - 20)
        end = min(len(text), symptom_pos + len(symptom) + 20)
        
        return text[start:end]
    
    def _calculate_severity_score(self, context: str, keywords: List[str], base_score: float) -> float:
        """计算严重程度得分"""
        score = 0.0
        matched_keywords = 0
        
        for keyword in keywords:
            if keyword in context:
                matched_keywords += 1
                # 关键词长度加权
                keyword_weight = len(keyword) / 10.0
                score += base_score * (1 + keyword_weight)
        
        # 多个关键词匹配加权
        if matched_keywords > 1:
            score *= (1 + matched_keywords * 0.1)
        
        return min(score, 1.0)
    
    def _apply_modifier_weights(self, context: str, severity_scores: Dict[str, float]) -> Dict[str, float]:
        """应用修饰词加权"""
        for intensity, modifiers in self.intensity_modifiers.items():
            for modifier in modifiers:
                if modifier in context:
                    if intensity == 'very_high':
                        severity_scores['severe'] *= 1.3
                        severity_scores['moderate'] *= 0.8
                        severity_scores['mild'] *= 0.5
                    elif intensity == 'high':
                        severity_scores['severe'] *= 1.2
                        severity_scores['moderate'] *= 1.1
                        severity_scores['mild'] *= 0.7
                    elif intensity == 'medium':
                        severity_scores['moderate'] *= 1.2
                        severity_scores['severe'] *= 0.9
                        severity_scores['mild'] *= 0.9
                    elif intensity == 'low':
                        severity_scores['mild'] *= 1.3
                        severity_scores['moderate'] *= 0.8
                        severity_scores['severe'] *= 0.5
                    break
        
        return severity_scores
    
    def _apply_frequency_weights(self, context: str, severity_scores: Dict[str, float]) -> Dict[str, float]:
        """应用频率加权"""
        for freq_level, freq_words in self.frequency_words.items():
            for word in freq_words:
                if word in context:
                    if freq_level in ['always', 'often']:
                        # 高频率增加严重程度
                        severity_scores['severe'] *= 1.2
                        severity_scores['moderate'] *= 1.1
                    elif freq_level == 'rarely':
                        # 低频率降低严重程度
                        severity_scores['severe'] *= 0.8
                        severity_scores['moderate'] *= 0.9
                        severity_scores['mild'] *= 1.1
                    break
        
        return severity_scores
    
    def _apply_impact_weights(self, context: str, severity_scores: Dict[str, float]) -> Dict[str, float]:
        """应用影响程度加权"""
        for impact_level, impact_words in self.impact_words.items():
            for word in impact_words:
                if word in context:
                    if impact_level == 'high_impact':
                        severity_scores['severe'] *= 1.4
                        severity_scores['moderate'] *= 1.1
                        severity_scores['mild'] *= 0.6
                    elif impact_level == 'medium_impact':
                        severity_scores['moderate'] *= 1.2
                        severity_scores['severe'] *= 0.9
                        severity_scores['mild'] *= 0.8
                    elif impact_level == 'low_impact':
                        severity_scores['mild'] *= 1.3
                        severity_scores['moderate'] *= 0.8
                        severity_scores['severe'] *= 0.5
                    break
        
        return severity_scores
    
    def _find_modifiers(self, context: str) -> List[Dict[str, Any]]:
        """查找修饰词"""
        modifiers = []
        
        for intensity, modifier_list in self.intensity_modifiers.items():
            for modifier in modifier_list:
                if modifier in context:
                    modifiers.append({
                        'word': modifier,
                        'intensity': intensity,
                        'position': context.find(modifier)
                    })
        
        return modifiers
    
    def _analyze_frequency(self, context: str) -> Optional[Dict[str, Any]]:
        """分析频率"""
        for freq_level, freq_words in self.frequency_words.items():
            for word in freq_words:
                if word in context:
                    return {
                        'level': freq_level,
                        'word': word,
                        'position': context.find(word)
                    }
        return None
    
    def _analyze_impact(self, context: str) -> Optional[Dict[str, Any]]:
        """分析影响程度"""
        for impact_level, impact_words in self.impact_words.items():
            for word in impact_words:
                if word in context:
                    return {
                        'level': impact_level,
                        'word': word,
                        'position': context.find(word)
                    }
        return None
    
    async def compare_severities(self, text1: str, symptom1: str, text2: str, symptom2: str) -> Dict[str, Any]:
        """比较两个症状的严重程度"""
        try:
            analysis1 = await self.analyze_detailed_severity(text1, symptom1)
            analysis2 = await self.analyze_detailed_severity(text2, symptom2)
            
            severity_order = {'mild': 1, 'moderate': 2, 'severe': 3, 'unknown': 0}
            
            score1 = severity_order.get(analysis1['severity'], 0)
            score2 = severity_order.get(analysis2['severity'], 0)
            
            if score1 > score2:
                result = "first_more_severe"
            elif score2 > score1:
                result = "second_more_severe"
            else:
                result = "equal_severity"
            
            return {
                'comparison_result': result,
                'first_analysis': analysis1,
                'second_analysis': analysis2,
                'confidence': min(analysis1['confidence'], analysis2['confidence'])
            }
            
        except Exception as e:
            self.logger.error(f"严重程度比较失败: {str(e)}")
            return {'comparison_result': 'unknown', 'confidence': 0.0} 