#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
持续时间提取器
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import timedelta
from ..common.base import BaseService
from ..common.logging import get_logger
from ..common.utils import sanitize_text, parse_time_expression


class DurationExtractor(BaseService):
    """持续时间提取器"""
    
    async def _do_initialize(self) -> None:
        """初始化持续时间提取器"""
        # 时间单位映射（转换为天数）
        self.time_units = {
            '秒': 1 / (24 * 3600),
            '分钟': 1 / (24 * 60),
            '小时': 1 / 24,
            '天': 1,
            '日': 1,
            '周': 7,
            '星期': 7,
            '月': 30,
            '年': 365
        }
        
        # 时间表达式模式
        self.duration_patterns = [
            # 数字+单位
            r'(\d+)\s*(秒|分钟|小时|天|日|周|星期|月|年)',
            # 中文数字+单位
            r'(一|二|三|四|五|六|七|八|九|十|几|半)\s*(秒|分钟|小时|天|日|周|星期|月|年)',
            # 复合表达式
            r'(\d+)\s*到\s*(\d+)\s*(天|日|周|星期|月|年)',
            r'(\d+)\s*-\s*(\d+)\s*(天|日|周|星期|月|年)',
            # 模糊时间
            r'(最近|近期|这几天|这周|这个月|长期|一直|总是)',
            # 相对时间
            r'(昨天|前天|今天|明天|后天)',
            r'(上周|本周|下周|上个月|这个月|下个月)',
        ]
        
        # 中文数字映射
        self.chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '几': 3, '半': 0.5  # 几天按3天估算，半天按0.5天
        }
        
        # 模糊时间映射
        self.fuzzy_durations = {
            '最近': 7,
            '近期': 14,
            '这几天': 3,
            '这周': 7,
            '这个月': 30,
            '长期': 365,
            '一直': 365,
            '总是': 365,
            '昨天': 1,
            '前天': 2,
            '今天': 0,
            '明天': -1,  # 负数表示未来
            '后天': -2,
            '上周': 7,
            '本周': 3,
            '下周': -7,
            '上个月': 30,
            '这个月': 15,
            '下个月': -30
        }
        
        # 持续性关键词
        self.duration_keywords = [
            '持续', '连续', '不断', '一直', '总是', '经常',
            '反复', '间歇', '偶尔', '时而', '有时'
        ]
        
        self.logger.info("持续时间提取器初始化完成")
    
    async def _do_health_check(self) -> bool:
        """健康检查"""
        try:
            # 测试持续时间提取
            test_result = await self.extract_duration("我头痛了三天", "头痛")
            return test_result > 0
        except Exception:
            return False
    
    async def extract_duration(self, text: str, symptom: str) -> int:
        """提取症状的持续时间（天数）"""
        try:
            cleaned_text = sanitize_text(text)
            
            # 获取症状周围的上下文
            context = self._extract_symptom_context(cleaned_text, symptom)
            
            # 尝试各种提取方法
            durations = []
            
            # 1. 精确数字提取
            exact_duration = self._extract_exact_duration(context)
            if exact_duration is not None:
                durations.append(exact_duration)
            
            # 2. 中文数字提取
            chinese_duration = self._extract_chinese_duration(context)
            if chinese_duration is not None:
                durations.append(chinese_duration)
            
            # 3. 模糊时间提取
            fuzzy_duration = self._extract_fuzzy_duration(context)
            if fuzzy_duration is not None:
                durations.append(fuzzy_duration)
            
            # 4. 范围时间提取
            range_duration = self._extract_range_duration(context)
            if range_duration is not None:
                durations.append(range_duration)
            
            # 选择最可信的持续时间
            if durations:
                # 过滤负数（未来时间）
                valid_durations = [d for d in durations if d >= 0]
                if valid_durations:
                    return int(max(valid_durations))  # 选择最长的持续时间
            
            return 0
            
        except Exception as e:
            self.logger.error(f"持续时间提取失败: {str(e)}")
            return 0
    
    async def extract_detailed_duration(self, text: str, symptom: str) -> Dict[str, Any]:
        """详细的持续时间提取"""
        try:
            cleaned_text = sanitize_text(text)
            context = self._extract_symptom_context(cleaned_text, symptom)
            
            # 基础持续时间
            duration_days = await self.extract_duration(text, symptom)
            
            # 详细分析
            analysis = {
                'duration_days': duration_days,
                'duration_category': self._categorize_duration(duration_days),
                'extracted_expressions': [],
                'confidence': 0.0,
                'context': context,
                'pattern_type': None,
                'is_ongoing': False,
                'is_intermittent': False
            }
            
            # 提取所有时间表达式
            expressions = self._extract_all_time_expressions(context)
            analysis['extracted_expressions'] = expressions
            
            # 分析持续性
            analysis['is_ongoing'] = self._is_ongoing_symptom(context)
            analysis['is_intermittent'] = self._is_intermittent_symptom(context)
            
            # 确定模式类型
            if expressions:
                analysis['pattern_type'] = expressions[0].get('type', 'unknown')
            
            # 计算置信度
            confidence_factors = []
            if duration_days > 0:
                confidence_factors.append(0.7)
            if expressions:
                confidence_factors.append(0.8)
            if analysis['is_ongoing'] or analysis['is_intermittent']:
                confidence_factors.append(0.6)
            
            from ..common.utils import calculate_confidence
            analysis['confidence'] = calculate_confidence(confidence_factors) if confidence_factors else 0.0
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"详细持续时间提取失败: {str(e)}")
            return {'duration_days': 0, 'confidence': 0.0}
    
    def _extract_symptom_context(self, text: str, symptom: str) -> str:
        """提取症状周围的上下文"""
        symptom_pos = text.find(symptom)
        if symptom_pos == -1:
            return text
        
        # 提取症状前后各30个字符的上下文
        start = max(0, symptom_pos - 30)
        end = min(len(text), symptom_pos + len(symptom) + 30)
        
        return text[start:end]
    
    def _extract_exact_duration(self, context: str) -> Optional[float]:
        """提取精确的数字时间"""
        pattern = r'(\d+(?:\.\d+)?)\s*(秒|分钟|小时|天|日|周|星期|月|年)'
        matches = re.findall(pattern, context)
        
        if matches:
            number, unit = matches[0]
            days = float(number) * self.time_units.get(unit, 1)
            return days
        
        return None
    
    def _extract_chinese_duration(self, context: str) -> Optional[float]:
        """提取中文数字时间"""
        pattern = r'(一|二|三|四|五|六|七|八|九|十|几|半)\s*(秒|分钟|小时|天|日|周|星期|月|年)'
        matches = re.findall(pattern, context)
        
        if matches:
            chinese_num, unit = matches[0]
            number = self.chinese_numbers.get(chinese_num, 1)
            days = number * self.time_units.get(unit, 1)
            return days
        
        return None
    
    def _extract_fuzzy_duration(self, context: str) -> Optional[float]:
        """提取模糊时间"""
        for fuzzy_term, days in self.fuzzy_durations.items():
            if fuzzy_term in context:
                return float(days)
        
        return None
    
    def _extract_range_duration(self, context: str) -> Optional[float]:
        """提取范围时间"""
        # 匹配 "3到5天" 或 "3-5天" 格式
        patterns = [
            r'(\d+)\s*到\s*(\d+)\s*(天|日|周|星期|月|年)',
            r'(\d+)\s*-\s*(\d+)\s*(天|日|周|星期|月|年)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, context)
            if matches:
                start_num, end_num, unit = matches[0]
                # 取平均值
                avg_num = (int(start_num) + int(end_num)) / 2
                days = avg_num * self.time_units.get(unit, 1)
                return days
        
        return None
    
    def _extract_all_time_expressions(self, context: str) -> List[Dict[str, Any]]:
        """提取所有时间表达式"""
        expressions = []
        
        # 精确数字表达式
        pattern = r'(\d+(?:\.\d+)?)\s*(秒|分钟|小时|天|日|周|星期|月|年)'
        for match in re.finditer(pattern, context):
            number, unit = match.groups()
            days = float(number) * self.time_units.get(unit, 1)
            expressions.append({
                'type': 'exact',
                'text': match.group(0),
                'number': float(number),
                'unit': unit,
                'days': days,
                'position': match.start()
            })
        
        # 中文数字表达式
        pattern = r'(一|二|三|四|五|六|七|八|九|十|几|半)\s*(秒|分钟|小时|天|日|周|星期|月|年)'
        for match in re.finditer(pattern, context):
            chinese_num, unit = match.groups()
            number = self.chinese_numbers.get(chinese_num, 1)
            days = number * self.time_units.get(unit, 1)
            expressions.append({
                'type': 'chinese',
                'text': match.group(0),
                'chinese_number': chinese_num,
                'number': number,
                'unit': unit,
                'days': days,
                'position': match.start()
            })
        
        # 模糊时间表达式
        for fuzzy_term, days in self.fuzzy_durations.items():
            if fuzzy_term in context:
                pos = context.find(fuzzy_term)
                expressions.append({
                    'type': 'fuzzy',
                    'text': fuzzy_term,
                    'days': float(days),
                    'position': pos
                })
        
        return expressions
    
    def _categorize_duration(self, duration_days: int) -> str:
        """分类持续时间"""
        if duration_days == 0:
            return "unknown"
        elif duration_days < 1:
            return "acute"  # 急性（小于1天）
        elif duration_days <= 7:
            return "short_term"  # 短期（1-7天）
        elif duration_days <= 30:
            return "medium_term"  # 中期（1周-1月）
        elif duration_days <= 90:
            return "long_term"  # 长期（1-3月）
        else:
            return "chronic"  # 慢性（超过3月）
    
    def _is_ongoing_symptom(self, context: str) -> bool:
        """判断是否是持续性症状"""
        ongoing_keywords = [
            '持续', '连续', '不断', '一直', '总是', '始终',
            '从未停止', '没有缓解', '持续不断'
        ]
        
        return any(keyword in context for keyword in ongoing_keywords)
    
    def _is_intermittent_symptom(self, context: str) -> bool:
        """判断是否是间歇性症状"""
        intermittent_keywords = [
            '间歇', '偶尔', '时而', '有时', '反复', '时好时坏',
            '发作', '阵发', '一阵一阵', '来来去去'
        ]
        
        return any(keyword in context for keyword in intermittent_keywords)
    
    async def compare_durations(self, text1: str, symptom1: str, text2: str, symptom2: str) -> Dict[str, Any]:
        """比较两个症状的持续时间"""
        try:
            analysis1 = await self.extract_detailed_duration(text1, symptom1)
            analysis2 = await self.extract_detailed_duration(text2, symptom2)
            
            duration1 = analysis1['duration_days']
            duration2 = analysis2['duration_days']
            
            if duration1 > duration2:
                result = "first_longer"
            elif duration2 > duration1:
                result = "second_longer"
            else:
                result = "equal_duration"
            
            return {
                'comparison_result': result,
                'first_analysis': analysis1,
                'second_analysis': analysis2,
                'duration_difference': abs(duration1 - duration2),
                'confidence': min(analysis1['confidence'], analysis2['confidence'])
            }
            
        except Exception as e:
            self.logger.error(f"持续时间比较失败: {str(e)}")
            return {'comparison_result': 'unknown', 'confidence': 0.0}
    
    async def extract_temporal_patterns(self, text: str) -> Dict[str, Any]:
        """提取时间模式"""
        try:
            cleaned_text = sanitize_text(text)
            
            patterns = {
                'onset_time': None,  # 发作时间
                'duration': None,    # 持续时间
                'frequency': None,   # 频率
                'timing': None,      # 时机（早上、晚上等）
                'triggers': [],      # 触发因素
                'relievers': []      # 缓解因素
            }
            
            # 发作时间模式
            onset_patterns = [
                r'(突然|忽然|瞬间|立即|马上)',
                r'(逐渐|慢慢|渐渐|缓慢)',
                r'(昨天|前天|今天|上周|上个月).*?(开始|发作|出现)'
            ]
            
            for pattern in onset_patterns:
                match = re.search(pattern, cleaned_text)
                if match:
                    patterns['onset_time'] = match.group(0)
                    break
            
            # 时机模式
            timing_patterns = {
                'morning': r'(早上|上午|清晨|晨起)',
                'afternoon': r'(下午|午后)',
                'evening': r'(晚上|傍晚|黄昏)',
                'night': r'(夜里|夜间|深夜|半夜)',
                'meal_related': r'(饭前|饭后|空腹|饱餐)',
                'activity_related': r'(运动后|劳累后|休息时|睡觉时)'
            }
            
            for timing_type, pattern in timing_patterns.items():
                if re.search(pattern, cleaned_text):
                    patterns['timing'] = timing_type
                    break
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"时间模式提取失败: {str(e)}")
            return {} 