#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
多语言国际化模块 - 多语言支持和本地化
包含语言检测、翻译、文化适应、本地化配置等功能
"""

import logging
import time
import asyncio
import json
import re
import locale
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
# 可选的国际化库导入
try:
    import gettext
    import babel
    from babel import Locale, dates, numbers, units
    from babel.core import UnknownLocaleError
    from babel.support import Translations
    import langdetect
    from googletrans import Translator
    I18N_LOCALIZATION_AVAILABLE = True
except ImportError as e:
    # 如果没有安装国际化库，使用简化版本
    I18N_LOCALIZATION_AVAILABLE = False
    
    # 创建简化的替代类
    class langdetect:
        class LangDetectException(Exception):
            pass
        
        @staticmethod
        def detect(text):
            # 简化的语言检测
            if any(ord(char) >= 0x4e00 and ord(char) <= 0x9fff for char in text):
                return "zh"
            elif any(ord(char) >= 0x3040 and ord(char) <= 0x309f for char in text):
                return "ja"
            elif any(ord(char) >= 0xac00 and ord(char) <= 0xd7af for char in text):
                return "ko"
            else:
                return "en"
    
    class Translator:
        def translate(self, text, dest="en", src="auto"):
            class MockTranslation:
                def __init__(self, text, dest):
                    self.text = text
                    self.dest = dest
                    self.src = "auto"
            return MockTranslation(text, dest)
    
    class Locale:
        def __init__(self, language):
            self.language = language
        
        @staticmethod
        def parse(locale_str):
            return Locale(locale_str.split('-')[0])
    
    class UnknownLocaleError(Exception):
        pass

import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class LanguageCode(Enum):
    """语言代码枚举"""
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    ENGLISH = "en-US"
    JAPANESE = "ja-JP"
    KOREAN = "ko-KR"
    FRENCH = "fr-FR"
    GERMAN = "de-DE"
    SPANISH = "es-ES"
    ITALIAN = "it-IT"
    PORTUGUESE = "pt-BR"
    RUSSIAN = "ru-RU"
    ARABIC = "ar-SA"
    HINDI = "hi-IN"
    THAI = "th-TH"
    VIETNAMESE = "vi-VN"


class CulturalContext(Enum):
    """文化背景枚举"""
    EASTERN = "eastern"
    WESTERN = "western"
    MIDDLE_EASTERN = "middle_eastern"
    SOUTH_ASIAN = "south_asian"
    SOUTHEAST_ASIAN = "southeast_asian"
    AFRICAN = "african"
    LATIN_AMERICAN = "latin_american"


class TextDirection(Enum):
    """文本方向枚举"""
    LTR = "ltr"  # 从左到右
    RTL = "rtl"  # 从右到左
    TTB = "ttb"  # 从上到下


@dataclass
class LanguageProfile:
    """语言配置文件"""
    language_code: str
    language_name: str
    native_name: str
    cultural_context: CulturalContext
    text_direction: TextDirection
    date_format: str
    time_format: str
    number_format: str
    currency_symbol: str
    decimal_separator: str
    thousands_separator: str
    enabled: bool = True


@dataclass
class TranslationEntry:
    """翻译条目"""
    key: str
    source_text: str
    translated_text: str
    language_code: str
    context: Optional[str]
    translator: str
    confidence: float
    created_at: float
    updated_at: float


@dataclass
class LocalizationRule:
    """本地化规则"""
    rule_id: str
    language_code: str
    rule_type: str  # date, number, currency, address, name
    pattern: str
    replacement: str
    priority: int
    enabled: bool = True


@dataclass
class CulturalAdaptation:
    """文化适应"""
    adaptation_id: str
    cultural_context: CulturalContext
    category: str  # color, symbol, gesture, etiquette
    source_element: str
    adapted_element: str
    description: str
    sensitivity_level: str  # low, medium, high, critical
    enabled: bool = True


class LanguageDetector:
    """语言检测器"""
    
    def __init__(self):
        self.detection_stats = {
            "texts_detected": 0,
            "detection_errors": 0,
            "confidence_sum": 0.0
        }
        
        # 语言特征模式
        self.language_patterns = {
            "zh": [r'[\u4e00-\u9fff]', r'[\u3400-\u4dbf]'],  # 中文字符
            "ja": [r'[\u3040-\u309f]', r'[\u30a0-\u30ff]'],  # 日文假名
            "ko": [r'[\uac00-\ud7af]'],  # 韩文字符
            "ar": [r'[\u0600-\u06ff]'],  # 阿拉伯文字符
            "hi": [r'[\u0900-\u097f]'],  # 印地文字符
            "th": [r'[\u0e00-\u0e7f]'],  # 泰文字符
            "vi": [r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]'],  # 越南文特殊字符
        }
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """检测文本语言"""
        try:
            if not text or not text.strip():
                return {
                    "language": "unknown",
                    "confidence": 0.0,
                    "method": "empty_text"
                }
            
            # 使用模式匹配进行快速检测
            pattern_result = await self._detect_by_patterns(text)
            if pattern_result["confidence"] > 0.8:
                self.detection_stats["texts_detected"] += 1
                self.detection_stats["confidence_sum"] += pattern_result["confidence"]
                return pattern_result
            
            # 使用langdetect库进行检测
            try:
                detected_lang = langdetect.detect(text)
                confidence = await self._calculate_confidence(text, detected_lang)
                
                result = {
                    "language": detected_lang,
                    "confidence": confidence,
                    "method": "langdetect"
                }
                
                self.detection_stats["texts_detected"] += 1
                self.detection_stats["confidence_sum"] += confidence
                
                logger.debug(f"语言检测: {detected_lang}, 置信度: {confidence:.2f}")
                
                return result
                
            except langdetect.LangDetectException:
                # 回退到基础检测
                return await self._fallback_detection(text)
            
        except Exception as e:
            self.detection_stats["detection_errors"] += 1
            logger.error(f"语言检测失败: {str(e)}")
            return {
                "language": "unknown",
                "confidence": 0.0,
                "method": "error",
                "error": str(e)
            }
    
    async def detect_multiple_languages(self, text: str) -> List[Dict[str, Any]]:
        """检测文本中的多种语言"""
        try:
            # 分段检测
            segments = await self._segment_text(text)
            results = []
            
            for segment in segments:
                if segment.strip():
                    detection_result = await self.detect_language(segment)
                    detection_result["segment"] = segment
                    results.append(detection_result)
            
            # 合并相邻的相同语言段
            merged_results = await self._merge_language_segments(results)
            
            return merged_results
            
        except Exception as e:
            logger.error(f"多语言检测失败: {str(e)}")
            return []
    
    async def _detect_by_patterns(self, text: str) -> Dict[str, Any]:
        """基于模式的语言检测"""
        scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            total_chars = len(text)
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                score += len(matches) / total_chars if total_chars > 0 else 0
            
            if score > 0:
                scores[lang] = score
        
        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = min(scores[best_lang], 1.0)
            
            return {
                "language": best_lang,
                "confidence": confidence,
                "method": "pattern_matching",
                "scores": scores
            }
        
        return {
            "language": "unknown",
            "confidence": 0.0,
            "method": "pattern_matching"
        }
    
    async def _calculate_confidence(self, text: str, detected_lang: str) -> float:
        """计算检测置信度"""
        # 基于文本长度和特征计算置信度
        base_confidence = 0.7
        
        # 文本长度因子
        length_factor = min(len(text) / 100, 1.0)
        
        # 特殊字符因子
        special_char_factor = 0.0
        if detected_lang in self.language_patterns:
            for pattern in self.language_patterns[detected_lang]:
                matches = re.findall(pattern, text)
                special_char_factor += len(matches) / len(text) if len(text) > 0 else 0
        
        special_char_factor = min(special_char_factor, 0.3)
        
        confidence = base_confidence + length_factor * 0.2 + special_char_factor
        
        return min(confidence, 1.0)
    
    async def _fallback_detection(self, text: str) -> Dict[str, Any]:
        """回退检测方法"""
        # 基于ASCII字符比例判断
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        ascii_ratio = ascii_chars / len(text) if len(text) > 0 else 0
        
        if ascii_ratio > 0.8:
            return {
                "language": "en",
                "confidence": 0.6,
                "method": "ascii_fallback"
            }
        else:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "method": "fallback_failed"
            }
    
    async def _segment_text(self, text: str) -> List[str]:
        """文本分段"""
        # 简单的句子分割
        sentences = re.split(r'[.!?。！？\n]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    async def _merge_language_segments(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并相同语言的相邻段落"""
        if not results:
            return []
        
        merged = []
        current_group = [results[0]]
        
        for i in range(1, len(results)):
            if results[i]["language"] == current_group[-1]["language"]:
                current_group.append(results[i])
            else:
                # 合并当前组
                merged_segment = await self._merge_group(current_group)
                merged.append(merged_segment)
                current_group = [results[i]]
        
        # 处理最后一组
        if current_group:
            merged_segment = await self._merge_group(current_group)
            merged.append(merged_segment)
        
        return merged
    
    async def _merge_group(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并语言组"""
        if len(group) == 1:
            return group[0]
        
        merged_text = " ".join(item["segment"] for item in group)
        avg_confidence = sum(item["confidence"] for item in group) / len(group)
        
        return {
            "language": group[0]["language"],
            "confidence": avg_confidence,
            "method": "merged",
            "segment": merged_text,
            "segment_count": len(group)
        }


class TranslationEngine:
    """翻译引擎"""
    
    def __init__(self):
        self.translator = Translator()
        self.translation_cache = {}
        self.translation_stats = {
            "translations_requested": 0,
            "translations_cached": 0,
            "translation_errors": 0,
            "total_characters": 0
        }
        
        # 翻译质量评估
        self.quality_thresholds = {
            "high": 0.9,
            "medium": 0.7,
            "low": 0.5
        }
    
    async def translate_text(self, text: str, 
                           target_language: str,
                           source_language: Optional[str] = None,
                           context: Optional[str] = None) -> Dict[str, Any]:
        """翻译文本"""
        try:
            # 检查缓存
            cache_key = f"{text}:{source_language}:{target_language}"
            if cache_key in self.translation_cache:
                self.translation_stats["translations_cached"] += 1
                return self.translation_cache[cache_key]
            
            # 执行翻译
            if source_language:
                translation = self.translator.translate(
                    text, 
                    src=source_language, 
                    dest=target_language
                )
            else:
                translation = self.translator.translate(text, dest=target_language)
            
            # 评估翻译质量
            quality_score = await self._assess_translation_quality(
                text, translation.text, translation.src, target_language
            )
            
            result = {
                "source_text": text,
                "translated_text": translation.text,
                "source_language": translation.src,
                "target_language": target_language,
                "confidence": getattr(translation, 'confidence', 0.8),
                "quality_score": quality_score,
                "quality_level": await self._get_quality_level(quality_score),
                "context": context,
                "timestamp": time.time(),
                "method": "google_translate"
            }
            
            # 缓存结果
            self.translation_cache[cache_key] = result
            
            # 更新统计
            self.translation_stats["translations_requested"] += 1
            self.translation_stats["total_characters"] += len(text)
            
            logger.debug(f"翻译完成: {translation.src} -> {target_language}, 质量: {quality_score:.2f}")
            
            return result
            
        except Exception as e:
            self.translation_stats["translation_errors"] += 1
            logger.error(f"翻译失败: {str(e)}")
            return {
                "source_text": text,
                "translated_text": text,  # 返回原文
                "source_language": source_language or "unknown",
                "target_language": target_language,
                "confidence": 0.0,
                "quality_score": 0.0,
                "quality_level": "failed",
                "error": str(e),
                "timestamp": time.time(),
                "method": "error"
            }
    
    async def translate_batch(self, texts: List[str],
                            target_language: str,
                            source_language: Optional[str] = None) -> List[Dict[str, Any]]:
        """批量翻译"""
        results = []
        
        for text in texts:
            result = await self.translate_text(text, target_language, source_language)
            results.append(result)
            
            # 添加小延迟避免API限制
            await asyncio.sleep(0.1)
        
        return results
    
    async def translate_structured_data(self, data: Dict[str, Any],
                                      target_language: str,
                                      translatable_fields: List[str]) -> Dict[str, Any]:
        """翻译结构化数据"""
        translated_data = data.copy()
        
        for field in translatable_fields:
            if field in data and isinstance(data[field], str):
                translation_result = await self.translate_text(
                    data[field], target_language
                )
                translated_data[field] = translation_result["translated_text"]
                translated_data[f"{field}_translation_info"] = {
                    "quality_score": translation_result["quality_score"],
                    "confidence": translation_result["confidence"],
                    "source_language": translation_result["source_language"]
                }
        
        return translated_data
    
    async def _assess_translation_quality(self, source_text: str,
                                        translated_text: str,
                                        source_lang: str,
                                        target_lang: str) -> float:
        """评估翻译质量"""
        try:
            # 基础质量评估
            quality_score = 0.7  # 基础分数
            
            # 长度比例检查
            length_ratio = len(translated_text) / len(source_text) if len(source_text) > 0 else 0
            if 0.5 <= length_ratio <= 2.0:  # 合理的长度比例
                quality_score += 0.1
            
            # 特殊字符保留检查
            source_special = re.findall(r'[^\w\s]', source_text)
            translated_special = re.findall(r'[^\w\s]', translated_text)
            
            if len(source_special) > 0:
                special_retention = len(translated_special) / len(source_special)
                quality_score += min(special_retention, 0.1)
            
            # 数字保留检查
            source_numbers = re.findall(r'\d+', source_text)
            translated_numbers = re.findall(r'\d+', translated_text)
            
            if source_numbers == translated_numbers:
                quality_score += 0.1
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"翻译质量评估失败: {str(e)}")
            return 0.5
    
    async def _get_quality_level(self, quality_score: float) -> str:
        """获取质量等级"""
        if quality_score >= self.quality_thresholds["high"]:
            return "high"
        elif quality_score >= self.quality_thresholds["medium"]:
            return "medium"
        elif quality_score >= self.quality_thresholds["low"]:
            return "low"
        else:
            return "poor"


class LocalizationManager:
    """本地化管理器"""
    
    def __init__(self):
        self.language_profiles = {}
        self.localization_rules = {}
        self.cultural_adaptations = {}
        self.current_locale = "en-US"
        
        # 初始化默认语言配置
        self._initialize_default_languages()
        
        self.localization_stats = {
            "localizations_applied": 0,
            "cultural_adaptations": 0,
            "format_conversions": 0,
            "localization_errors": 0
        }
    
    def _initialize_default_languages(self):
        """初始化默认语言配置"""
        default_languages = [
            LanguageProfile(
                language_code="zh-CN",
                language_name="Chinese (Simplified)",
                native_name="简体中文",
                cultural_context=CulturalContext.EASTERN,
                text_direction=TextDirection.LTR,
                date_format="%Y年%m月%d日",
                time_format="%H:%M:%S",
                number_format="#,##0.##",
                currency_symbol="¥",
                decimal_separator=".",
                thousands_separator=","
            ),
            LanguageProfile(
                language_code="en-US",
                language_name="English (United States)",
                native_name="English",
                cultural_context=CulturalContext.WESTERN,
                text_direction=TextDirection.LTR,
                date_format="%m/%d/%Y",
                time_format="%I:%M:%S %p",
                number_format="#,##0.##",
                currency_symbol="$",
                decimal_separator=".",
                thousands_separator=","
            ),
            LanguageProfile(
                language_code="ja-JP",
                language_name="Japanese",
                native_name="日本語",
                cultural_context=CulturalContext.EASTERN,
                text_direction=TextDirection.LTR,
                date_format="%Y年%m月%d日",
                time_format="%H:%M:%S",
                number_format="#,##0.##",
                currency_symbol="¥",
                decimal_separator=".",
                thousands_separator=","
            ),
            LanguageProfile(
                language_code="ar-SA",
                language_name="Arabic (Saudi Arabia)",
                native_name="العربية",
                cultural_context=CulturalContext.MIDDLE_EASTERN,
                text_direction=TextDirection.RTL,
                date_format="%d/%m/%Y",
                time_format="%H:%M:%S",
                number_format="#,##0.##",
                currency_symbol="ر.س",
                decimal_separator=".",
                thousands_separator=","
            )
        ]
        
        for profile in default_languages:
            self.language_profiles[profile.language_code] = profile
    
    async def set_locale(self, language_code: str) -> bool:
        """设置当前语言环境"""
        try:
            if language_code not in self.language_profiles:
                logger.warning(f"不支持的语言代码: {language_code}")
                return False
            
            self.current_locale = language_code
            
            # 设置系统locale
            try:
                locale.setlocale(locale.LC_ALL, language_code.replace('-', '_'))
            except locale.Error:
                logger.warning(f"无法设置系统locale: {language_code}")
            
            logger.info(f"语言环境设置为: {language_code}")
            return True
            
        except Exception as e:
            logger.error(f"设置语言环境失败: {str(e)}")
            return False
    
    async def localize_data(self, data: Dict[str, Any],
                          target_language: str) -> Dict[str, Any]:
        """本地化数据"""
        try:
            if target_language not in self.language_profiles:
                logger.warning(f"不支持的目标语言: {target_language}")
                return data
            
            profile = self.language_profiles[target_language]
            localized_data = data.copy()
            
            # 本地化日期时间
            localized_data = await self._localize_datetime(localized_data, profile)
            
            # 本地化数字
            localized_data = await self._localize_numbers(localized_data, profile)
            
            # 本地化货币
            localized_data = await self._localize_currency(localized_data, profile)
            
            # 应用文化适应
            localized_data = await self._apply_cultural_adaptations(localized_data, profile)
            
            self.localization_stats["localizations_applied"] += 1
            
            logger.debug(f"数据本地化完成: {target_language}")
            
            return localized_data
            
        except Exception as e:
            self.localization_stats["localization_errors"] += 1
            logger.error(f"数据本地化失败: {str(e)}")
            return data
    
    async def format_date(self, date_obj: datetime, language_code: str) -> str:
        """格式化日期"""
        try:
            if language_code not in self.language_profiles:
                language_code = self.current_locale
            
            profile = self.language_profiles[language_code]
            
            # 使用babel进行本地化格式化
            try:
                locale_obj = Locale.parse(language_code.replace('-', '_'))
                formatted_date = dates.format_date(date_obj, locale=locale_obj)
                return formatted_date
            except (UnknownLocaleError, ValueError):
                # 回退到配置文件格式
                return date_obj.strftime(profile.date_format)
            
        except Exception as e:
            logger.error(f"日期格式化失败: {str(e)}")
            return str(date_obj)
    
    async def format_number(self, number: Union[int, float], 
                          language_code: str) -> str:
        """格式化数字"""
        try:
            if language_code not in self.language_profiles:
                language_code = self.current_locale
            
            profile = self.language_profiles[language_code]
            
            # 使用babel进行本地化格式化
            try:
                locale_obj = Locale.parse(language_code.replace('-', '_'))
                formatted_number = numbers.format_decimal(number, locale=locale_obj)
                return formatted_number
            except (UnknownLocaleError, ValueError):
                # 回退到简单格式化
                return f"{number:,.2f}".replace(',', profile.thousands_separator).replace('.', profile.decimal_separator)
            
        except Exception as e:
            logger.error(f"数字格式化失败: {str(e)}")
            return str(number)
    
    async def format_currency(self, amount: Union[int, float],
                            language_code: str,
                            currency_code: Optional[str] = None) -> str:
        """格式化货币"""
        try:
            if language_code not in self.language_profiles:
                language_code = self.current_locale
            
            profile = self.language_profiles[language_code]
            
            # 使用babel进行本地化格式化
            try:
                locale_obj = Locale.parse(language_code.replace('-', '_'))
                if currency_code:
                    formatted_currency = numbers.format_currency(
                        amount, currency_code, locale=locale_obj
                    )
                else:
                    formatted_currency = f"{profile.currency_symbol}{amount:,.2f}"
                return formatted_currency
            except (UnknownLocaleError, ValueError):
                # 回退到简单格式化
                return f"{profile.currency_symbol}{amount:,.2f}"
            
        except Exception as e:
            logger.error(f"货币格式化失败: {str(e)}")
            return f"{amount}"
    
    async def _localize_datetime(self, data: Dict[str, Any],
                               profile: LanguageProfile) -> Dict[str, Any]:
        """本地化日期时间字段"""
        datetime_fields = ["date", "time", "datetime", "created_at", "updated_at", "timestamp"]
        
        for field in datetime_fields:
            if field in data:
                value = data[field]
                if isinstance(value, (int, float)):
                    # 时间戳转换
                    dt = datetime.fromtimestamp(value)
                    data[field] = await self.format_date(dt, profile.language_code)
                elif isinstance(value, str):
                    # 尝试解析字符串日期
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        data[field] = await self.format_date(dt, profile.language_code)
                    except ValueError:
                        pass  # 保持原值
        
        return data
    
    async def _localize_numbers(self, data: Dict[str, Any],
                              profile: LanguageProfile) -> Dict[str, Any]:
        """本地化数字字段"""
        number_fields = ["count", "quantity", "amount", "value", "score", "rating"]
        
        for field in number_fields:
            if field in data and isinstance(data[field], (int, float)):
                data[field] = await self.format_number(data[field], profile.language_code)
        
        return data
    
    async def _localize_currency(self, data: Dict[str, Any],
                               profile: LanguageProfile) -> Dict[str, Any]:
        """本地化货币字段"""
        currency_fields = ["price", "cost", "fee", "salary", "income", "expense"]
        
        for field in currency_fields:
            if field in data and isinstance(data[field], (int, float)):
                data[field] = await self.format_currency(data[field], profile.language_code)
        
        return data
    
    async def _apply_cultural_adaptations(self, data: Dict[str, Any],
                                        profile: LanguageProfile) -> Dict[str, Any]:
        """应用文化适应"""
        # 获取相关的文化适应规则
        relevant_adaptations = [
            adaptation for adaptation in self.cultural_adaptations.values()
            if adaptation.cultural_context == profile.cultural_context and adaptation.enabled
        ]
        
        for adaptation in relevant_adaptations:
            if adaptation.source_element in str(data):
                # 应用文化适应
                data_str = json.dumps(data, ensure_ascii=False)
                adapted_str = data_str.replace(adaptation.source_element, adaptation.adapted_element)
                try:
                    data = json.loads(adapted_str)
                    self.localization_stats["cultural_adaptations"] += 1
                except json.JSONDecodeError:
                    pass  # 保持原数据
        
        return data
    
    async def add_cultural_adaptation(self, cultural_context: CulturalContext,
                                    category: str,
                                    source_element: str,
                                    adapted_element: str,
                                    description: str,
                                    sensitivity_level: str = "medium") -> str:
        """添加文化适应规则"""
        adaptation_id = f"adapt_{int(time.time())}_{len(self.cultural_adaptations)}"
        
        adaptation = CulturalAdaptation(
            adaptation_id=adaptation_id,
            cultural_context=cultural_context,
            category=category,
            source_element=source_element,
            adapted_element=adapted_element,
            description=description,
            sensitivity_level=sensitivity_level
        )
        
        self.cultural_adaptations[adaptation_id] = adaptation
        
        logger.info(f"添加文化适应规则: {adaptation_id}")
        
        return adaptation_id
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """获取支持的语言列表"""
        return [
            {
                "code": profile.language_code,
                "name": profile.language_name,
                "native_name": profile.native_name,
                "cultural_context": profile.cultural_context.value,
                "text_direction": profile.text_direction.value,
                "enabled": profile.enabled
            }
            for profile in self.language_profiles.values()
            if profile.enabled
        ]


class I18nLocalization:
    """多语言国际化主类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化多语言国际化系统
        
        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("i18n", {}).get("enabled", True) and I18N_LOCALIZATION_AVAILABLE
        self.default_language = config.get("i18n", {}).get("default_language", "en-US")
        
        # 核心组件
        if I18N_LOCALIZATION_AVAILABLE:
            self.language_detector = LanguageDetector()
            self.translation_engine = TranslationEngine()
            self.localization_manager = LocalizationManager()
        else:
            self.language_detector = None
            self.translation_engine = None
            self.localization_manager = None
        
        # 翻译缓存
        self.translation_entries = {}
        
        if I18N_LOCALIZATION_AVAILABLE:
            logger.info(f"多语言国际化系统初始化完成 - 启用: {self.enabled}, 默认语言: {self.default_language} (完整功能)")
        else:
            logger.info(f"多语言国际化系统初始化完成 - 启用: {self.enabled}, 默认语言: {self.default_language} (简化功能，缺少国际化库)")
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """检测文本语言"""
        if not self.enabled or not self.language_detector:
            return {"language": self.default_language, "confidence": 1.0, "method": "disabled"}
        
        return await self.language_detector.detect_language(text)
    
    async def translate_text(self, text: str,
                           target_language: str,
                           source_language: Optional[str] = None,
                           context: Optional[str] = None) -> Dict[str, Any]:
        """翻译文本"""
        if not self.enabled:
            return {
                "source_text": text,
                "translated_text": text,
                "source_language": source_language or self.default_language,
                "target_language": target_language,
                "method": "disabled"
            }
        
        # 如果目标语言与源语言相同，直接返回
        if source_language and source_language == target_language:
            return {
                "source_text": text,
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "method": "same_language"
            }
        
        # 自动检测源语言
        if not source_language:
            detection_result = await self.detect_language(text)
            source_language = detection_result["language"]
        
        if not self.translation_engine:
            return {
                "source_text": text,
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "method": "disabled"
            }
        
        return await self.translation_engine.translate_text(
            text, target_language, source_language, context
        )
    
    async def localize_content(self, content: Dict[str, Any],
                             target_language: str,
                             translatable_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """本地化内容"""
        if not self.enabled or not self.translation_engine or not self.localization_manager:
            return content
        
        try:
            localized_content = content.copy()
            
            # 翻译指定字段
            if translatable_fields:
                localized_content = await self.translation_engine.translate_structured_data(
                    localized_content, target_language, translatable_fields
                )
            
            # 应用本地化格式
            localized_content = await self.localization_manager.localize_data(
                localized_content, target_language
            )
            
            return localized_content
            
        except Exception as e:
            logger.error(f"内容本地化失败: {str(e)}")
            return content
    
    async def format_for_locale(self, data: Any, 
                              data_type: str,
                              language_code: str) -> str:
        """为特定语言环境格式化数据"""
        if not self.enabled:
            return str(data)
        
        try:
            if data_type == "date" and isinstance(data, datetime):
                return await self.localization_manager.format_date(data, language_code)
            elif data_type == "number" and isinstance(data, (int, float)):
                return await self.localization_manager.format_number(data, language_code)
            elif data_type == "currency" and isinstance(data, (int, float)):
                return await self.localization_manager.format_currency(data, language_code)
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"数据格式化失败: {str(e)}")
            return str(data)
    
    async def get_user_preferred_language(self, user_context: Dict[str, Any]) -> str:
        """获取用户首选语言"""
        # 优先级：用户设置 > 浏览器语言 > 地理位置 > 默认语言
        
        # 用户设置
        if "preferred_language" in user_context:
            return user_context["preferred_language"]
        
        # 浏览器语言
        if "accept_language" in user_context:
            accept_languages = user_context["accept_language"].split(',')
            for lang in accept_languages:
                lang_code = lang.split(';')[0].strip()
                if lang_code in self.localization_manager.language_profiles:
                    return lang_code
        
        # 地理位置推断
        if "country" in user_context:
            country_language_map = {
                "CN": "zh-CN",
                "TW": "zh-TW",
                "JP": "ja-JP",
                "KR": "ko-KR",
                "US": "en-US",
                "GB": "en-GB",
                "FR": "fr-FR",
                "DE": "de-DE",
                "ES": "es-ES",
                "IT": "it-IT",
                "BR": "pt-BR",
                "RU": "ru-RU",
                "SA": "ar-SA",
                "IN": "hi-IN",
                "TH": "th-TH",
                "VN": "vi-VN"
            }
            
            country = user_context["country"].upper()
            if country in country_language_map:
                return country_language_map[country]
        
        return self.default_language
    
    async def create_multilingual_response(self, content: Dict[str, Any],
                                         supported_languages: List[str],
                                         translatable_fields: List[str]) -> Dict[str, Dict[str, Any]]:
        """创建多语言响应"""
        multilingual_response = {}
        
        for language in supported_languages:
            try:
                localized_content = await self.localize_content(
                    content, language, translatable_fields
                )
                multilingual_response[language] = localized_content
            except Exception as e:
                logger.error(f"创建 {language} 语言响应失败: {str(e)}")
                multilingual_response[language] = content  # 回退到原内容
        
        return multilingual_response
    
    def get_localization_stats(self) -> Dict[str, Any]:
        """获取本地化统计信息"""
        stats = {
            "enabled": self.enabled,
            "default_language": self.default_language
        }
        
        # 在简化模式下，组件可能为None
        if self.localization_manager:
            stats["supported_languages"] = len(self.localization_manager.language_profiles)
            stats["localization_stats"] = self.localization_manager.localization_stats
            stats["cultural_adaptations"] = len(self.localization_manager.cultural_adaptations)
        else:
            stats["supported_languages"] = 0
            stats["localization_stats"] = {}
            stats["cultural_adaptations"] = 0
            
        if self.language_detector:
            stats["detection_stats"] = self.language_detector.detection_stats
        else:
            stats["detection_stats"] = {}
            
        if self.translation_engine:
            stats["translation_stats"] = self.translation_engine.translation_stats
            stats["cached_translations"] = len(self.translation_engine.translation_cache)
        else:
            stats["translation_stats"] = {}
            stats["cached_translations"] = 0
            
        return stats
    
    async def add_custom_translation(self, key: str,
                                   source_text: str,
                                   translated_text: str,
                                   language_code: str,
                                   context: Optional[str] = None) -> str:
        """添加自定义翻译"""
        entry_id = f"custom_{int(time.time())}_{len(self.translation_entries)}"
        
        entry = TranslationEntry(
            key=key,
            source_text=source_text,
            translated_text=translated_text,
            language_code=language_code,
            context=context,
            translator="custom",
            confidence=1.0,
            created_at=time.time(),
            updated_at=time.time()
        )
        
        self.translation_entries[entry_id] = entry
        
        # 更新翻译缓存
        cache_key = f"{source_text}:auto:{language_code}"
        self.translation_engine.translation_cache[cache_key] = {
            "source_text": source_text,
            "translated_text": translated_text,
            "source_language": "auto",
            "target_language": language_code,
            "confidence": 1.0,
            "quality_score": 1.0,
            "quality_level": "high",
            "context": context,
            "timestamp": time.time(),
            "method": "custom"
        }
        
        logger.info(f"添加自定义翻译: {entry_id}")
        
        return entry_id 