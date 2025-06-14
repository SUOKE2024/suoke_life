"""
negation_detector - 索克生活项目模块
"""

from ..common.base import BaseService
from ..common.utils import sanitize_text
from typing import Any
import re

#! / usr / bin / env python

"""
否定词检测器
"""




class NegationDetector(BaseService):
    """否定词检测器"""

    async def _do_initialize(self)-> None:
        """初始化否定词检测器"""
        # 否定词列表
        self.negation_words = [
            # 直接否定
            "不",
            "没",
            "没有",
            "无",
            "未",
            "非",
            "否",
            "别",
            "勿",
            # 程度否定
            "不太",
            "不很",
            "不怎么",
            "不是很",
            "不算",
            # 时间否定
            "不再",
            "不会",
            "不曾",
            "从不",
            "从未",
            "绝不",
            # 复合否定
            "并不",
            "并非",
            "并无",
            "根本不",
            "完全不",
            "绝对不",
            # 疑问否定
            "难道不",
            "岂不",
            "何不",
            "为何不",
            # 条件否定
            "除非",
            "要不是",
            "如果不是",
        ]

        # 否定范围词
        self.scope_words = [
            "但是",
            "不过",
            "然而",
            "可是",
            "只是",
            "就是",
            "而是",
            "除了",
            "除非",
            "要不然",
            "否则",
        ]

        # 否定模式
        self.negation_patterns = [
            r"(不|没|没有|无|未|非)\s * ([^，。！？；：\s]{1,10})",
            r"(从不|从未|绝不|根本不|完全不)\s * ([^，。！？；：\s]{1,10})",
            r"(并不|并非|并无)\s * ([^，。！？；：\s]{1,10})",
            r"(难道不|岂不|何不)\s * ([^，。！？；：\s]{1,10})",
        ]

        self.logger.info("否定词检测器初始化完成")

    async def _do_health_check(self)-> bool:
        """健康检查"""
        try:
            # 测试否定检测
            test_result = await self.is_negated("我不头痛", "头痛")
            return test_result is True
        except Exception:
            return False

    async def is_negated(self, text: str, target_word: str)-> bool:
        """检查目标词是否被否定"""
        try:
            cleaned_text = sanitize_text(text)

            # 查找目标词的位置
            target_positions = self._find_word_positions(cleaned_text, target_word)
            if not target_positions:
                return False

            # 检查每个目标词位置的否定情况
            for pos in target_positions:
                if await self._is_position_negated(cleaned_text, pos, target_word):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"否定检测失败: {e!s}")
            return False

    async def detect_negations(self, text: str)-> list[dict[str, Any]]:
        """检测文本中的所有否定表达"""
        try:
            cleaned_text = sanitize_text(text)
            negations = []

            # 使用正则模式检测
            for pattern in self.negation_patterns:
                matches = re.finditer(pattern, cleaned_text)
                for match in matches:
                    negation_word = match.group(1)
                    target_word = match.group(2)

                    negations.append(
                        {
                            "negation_word": negation_word,
                            "target_word": target_word,
                            "position": match.start(),
                            "full_match": match.group(0),
                            "confidence": self._calculate_negation_confidence(
                                negation_word, target_word, cleaned_text
                            ),
                        }
                    )

            # 去重和排序
            negations = self._deduplicate_negations(negations)
            negations.sort(key=lambda x: x["confidence"], reverse = True)

            return negations

        except Exception as e:
            self.logger.error(f"否定检测失败: {e!s}")
            return []

    async def get_negation_scope(self, text: str, negation_pos: int)-> tuple[int, int]:
        """获取否定词的作用范围"""
        try:
            # 向前查找范围开始
            start_pos = max(0, negation_pos - 20)

            # 向后查找范围结束
            end_pos = negation_pos + 20

            # 查找句子边界
            sentence_boundaries = [".", "。", "!", "！", "?", "？", ";", "；", "\n"]

            # 向前查找句子开始
            for i in range(negation_pos - 1, start_pos - 1, - 1):
                if i < len(text) and text[i] in sentence_boundaries:
                    start_pos = i + 1
                    break

            # 向后查找句子结束
            for i in range(negation_pos, min(len(text), end_pos)):
                if text[i] in sentence_boundaries:
                    end_pos = i
                    break

            return start_pos, end_pos

        except Exception as e:
            self.logger.error(f"否定范围计算失败: {e!s}")
            return negation_pos, negation_pos + 10

    def _find_word_positions(self, text: str, word: str)-> list[int]:
        """查找词语在文本中的所有位置"""
        positions = []
        start = 0

        while True:
            pos = text.find(word, start)
            if pos == - 1:
                break
            positions.append(pos)
            start = pos + 1

        return positions

    async def _is_position_negated(
        self, text: str, position: int, target_word: str
    )-> bool:
        """检查特定位置的词是否被否定"""
        # 获取否定检查范围
        check_start = max(0, position - 15)
        check_end = min(len(text), position + len(target_word) + 5)
        context = text[check_start:check_end]

        # 检查直接否定
        for neg_word in self.negation_words:
            neg_pos = context.find(neg_word)
            if neg_pos != -1:
                # 计算否定词到目标词的距离
                target_pos_in_context = position - check_start
                distance = abs(target_pos_in_context - neg_pos)

                # 距离越近，否定可能性越大
                if distance <= 8:  # 8个字符内认为有否定关系
                    return True

        # 检查否定模式
        for pattern in self.negation_patterns:
            if re.search(pattern, context):
                return True

        return False

    def _calculate_negation_confidence(
        self, negation_word: str, target_word: str, text: str
    )-> float:
        """计算否定的置信度"""
        confidence = 0.7  # 基础置信度

        # 否定词强度加权
        strong_negations = ["绝不", "从不", "从未", "根本不", "完全不", "绝对不"]
        if negation_word in strong_negations:
            confidence += 0.2

        # 距离加权
        neg_pos = text.find(negation_word)
        target_pos = text.find(target_word)
        if neg_pos != -1 and target_pos != -1:
            distance = abs(target_pos - neg_pos)
            if distance <= 3:
                confidence += 0.1
            elif distance <= 6:
                confidence += 0.05

        # 上下文加权
        context_indicators = ["但是", "不过", "然而", "可是"]
        for indicator in context_indicators:
            if indicator in text:
                confidence -= 0.1  # 转折词可能削弱否定

        return max(0.0, min(1.0, confidence))

    def _deduplicate_negations(
        self, negations: list[dict[str, Any]]
    )-> list[dict[str, Any]]:
        """去除重复的否定检测结果"""
        seen = set()
        unique_negations = []

        for negation in negations:
            key = (negation["negation_word"], negation["target_word"])
            if key not in seen:
                seen.add(key)
                unique_negations.append(negation)

        return unique_negations

    async def analyze_negation_context(
        self, text: str, negation_word: str, target_word: str
    )-> dict[str, Any]:
        """分析否定的上下文信息"""
        try:
            # 查找否定词和目标词的位置
            neg_pos = text.find(negation_word)
            target_pos = text.find(target_word)

            if neg_pos == - 1 or target_pos == - 1:
                return {}

            # 获取上下文
            context_start = max(0, min(neg_pos, target_pos) - 20)
            context_end = min(len(text), max(neg_pos, target_pos) + 20)
            context = text[context_start:context_end]

            # 分析否定类型
            negation_type = self._classify_negation_type(negation_word)

            # 分析否定强度
            strength = self._analyze_negation_strength(context, negation_word)

            # 检查是否有转折
            has_contrast = any(word in context for word in self.scope_words)

            return {
                "context": context,
                "negation_type": negation_type,
                "strength": strength,
                "has_contrast": has_contrast,
                "distance": abs(target_pos - neg_pos),
            }

        except Exception as e:
            self.logger.error(f"否定上下文分析失败: {e!s}")
            return {}

    def _classify_negation_type(self, negation_word: str)-> str:
        """分类否定类型"""
        if negation_word in ["不", "没", "没有", "无", "未"]:
            return "direct"  # 直接否定
        elif negation_word in ["从不", "从未", "绝不"]:
            return "absolute"  # 绝对否定
        elif negation_word in ["不太", "不很", "不怎么"]:
            return "partial"  # 部分否定
        elif negation_word in ["难道不", "岂不"]:
            return "rhetorical"  # 反问否定
        else:
            return "general"  # 一般否定

    def _analyze_negation_strength(self, context: str, negation_word: str)-> str:
        """分析否定强度"""
        # 强否定词
        if negation_word in ["绝不", "从不", "从未", "根本不", "完全不", "绝对不"]:
            return "strong"

        # 弱否定词
        elif negation_word in ["不太", "不很", "不怎么", "不是很"]:
            return "weak"

        # 检查强化词
        intensifiers = ["很", "非常", "特别", "极其", "十分"]
        if any(word in context for word in intensifiers):
            return "strong"

        return "medium"
