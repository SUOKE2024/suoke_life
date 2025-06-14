"""
context_analyzer - 索克生活项目模块
"""

from ..common.base import BaseService
from ..common.utils import calculate_confidence, sanitize_text
from typing import Any
import re

#! / usr / bin / env python

"""
症状上下文分析器
"""




class SymptomContextAnalyzer(BaseService):
    """症状上下文分析器"""

    async def _do_initialize(self)-> None:
        """初始化上下文分析器"""
        # 诱发因素关键词
        self.trigger_keywords = {
            "stress": ["压力", "紧张", "焦虑", "担心", "烦恼", "着急"],
            "weather": ["天气", "气候", "下雨", "阴天", "潮湿", "干燥", "寒冷", "炎热"],
            "food": ["吃", "饮食", "食物", "辛辣", "油腻", "生冷", "甜食", "酒"],
            "activity": ["运动", "劳累", "疲劳", "熬夜", "久坐", "久站", "弯腰"],
            "environment": ["噪音", "光线", "空气", "污染", "灰尘", "花粉", "异味"],
            "sleep": ["睡眠", "失眠", "熬夜", "睡不好", "睡得晚", "起得早"],
            "emotion": ["生气", "愤怒", "悲伤", "抑郁", "兴奋", "激动", "情绪"],
            "menstrual": ["月经", "生理期", "经期", "例假", "大姨妈"],
            "medication": ["药物", "吃药", "服药", "停药", "换药"],
        }

        # 缓解因素关键词
        self.relief_keywords = {
            "rest": ["休息", "睡觉", "躺下", "坐下", "放松"],
            "medication": ["吃药", "服药", "药物", "止痛药", "中药"],
            "physical": ["按摩", "热敷", "冷敷", "针灸", "理疗", "拉伸"],
            "environment": ["安静", "黑暗", "通风", "新鲜空气", "温暖"],
            "food": ["喝水", "热水", "温水", "清淡饮食", "不吃"],
            "activity": ["散步", "轻微运动", "深呼吸", "冥想"],
            "position": ["平躺", "侧躺", "抬高", "低头", "仰头"],
        }

        # 加重因素关键词
        self.aggravating_keywords = {
            "activity": ["运动", "活动", "走路", "跑步", "弯腰", "低头", "咳嗽"],
            "position": ["站立", "坐着", "躺着", "转头", "仰头"],
            "environment": ["噪音", "强光", "寒冷", "炎热", "风吹"],
            "food": ["吃东西", "喝水", "辛辣", "油腻", "冷饮"],
            "emotion": ["紧张", "激动", "生气", "着急", "压力"],
            "time": ["早上", "晚上", "夜里", "饭后", "空腹"],
            "touch": ["触摸", "按压", "碰到", "摸到"],
        }

        # 伴随症状关键词
        self.accompanying_keywords = {
            "neurological": ["头晕", "恶心", "呕吐", "视力模糊", "耳鸣", "麻木"],
            "cardiovascular": ["心悸", "胸闷", "气短", "出汗", "面色苍白"],
            "digestive": ["腹痛", "腹胀", "腹泻", "便秘", "食欲不振", "反酸"],
            "respiratory": ["咳嗽", "咳痰", "气喘", "呼吸困难", "胸痛"],
            "musculoskeletal": ["关节痛", "肌肉酸痛", "僵硬", "无力", "疲劳"],
            "psychological": ["焦虑", "抑郁", "烦躁", "失眠", "注意力不集中"],
        }

        # 上下文模式
        self.context_patterns = {
            "trigger": [
                r"(因为|由于|当|在|每当|一旦). * ?([^，。！？；：\s]{2,10}). * ?(就|便|会|开始|出现)",
                r"([^，。！？；：\s]{2,10})(后|时|的时候|之后). * ?(出现|开始|发作)",
                r"(遇到|碰到|接触). * ?([^，。！？；：\s]{2,10}). * ?(就|便|会)",
            ],
            "relief": [
                r"(通过|经过|用|吃|服). * ?([^，。！？；：\s]{2,10}). * ?(缓解|减轻|好转|消失)",
                r"([^，。！？；：\s]{2,10})(后|时|之后). * ?(缓解|减轻|好转|消失)",
                r"(休息|睡觉|躺下). * ?(后|时|之后). * ?(缓解|减轻|好转)",
            ],
            "aggravating": [
                r"(当|在|每当|一旦). * ?([^，。！？；：\s]{2,10}). * ?(加重|严重|厉害)",
                r"([^，。！？；：\s]{2,10})(后|时|的时候|之后). * ?(加重|严重|厉害)",
                r"(遇到|碰到|接触). * ?([^，。！？；：\s]{2,10}). * ?(加重|严重)",
            ],
        }

        self.logger.info("症状上下文分析器初始化完成")

    async def _do_health_check(self)-> bool:
        """健康检查"""
        try:
            # 测试上下文分析
            test_result = await self.analyze_context("我在紧张的时候头痛", "头痛")
            return "triggers" in test_result and len(test_result["triggers"]) > 0
        except Exception:
            return False

    async def analyze_context(self, text: str, symptom: str)-> dict[str, Any]:
        """分析症状的上下文信息"""
        try:
            cleaned_text = sanitize_text(text)

            # 获取症状周围的上下文
            context = self._extract_symptom_context(cleaned_text, symptom)

            analysis = {
                "triggers": [],  # 诱发因素
                "relievers": [],  # 缓解因素
                "aggravators": [],  # 加重因素
                "accompanying": [],  # 伴随症状
                "temporal": {},  # 时间相关
                "environmental": {},  # 环境相关
                "confidence": 0.0,
            }

            # 分析诱发因素
            triggers = await self._analyze_triggers(context)
            analysis["triggers"] = triggers

            # 分析缓解因素
            relievers = await self._analyze_relievers(context)
            analysis["relievers"] = relievers

            # 分析加重因素
            aggravators = await self._analyze_aggravators(context)
            analysis["aggravators"] = aggravators

            # 分析伴随症状
            accompanying = await self._analyze_accompanying_symptoms(context)
            analysis["accompanying"] = accompanying

            # 分析时间相关因素
            temporal = await self._analyze_temporal_context(context)
            analysis["temporal"] = temporal

            # 分析环境相关因素
            environmental = await self._analyze_environmental_context(context)
            analysis["environmental"] = environmental

            # 计算置信度
            confidence_factors = []
            if triggers:
                confidence_factors.append(0.8)
            if relievers:
                confidence_factors.append(0.8)
            if aggravators:
                confidence_factors.append(0.7)
            if accompanying:
                confidence_factors.append(0.9)
            if temporal:
                confidence_factors.append(0.6)
            if environmental:
                confidence_factors.append(0.6)

            analysis["confidence"] = (
                calculate_confidence(confidence_factors) if confidence_factors else 0.0
            )

            return analysis

        except Exception as e:
            self.logger.error(f"上下文分析失败: {e!s}")
            return {
                "triggers": [],
                "relievers": [],
                "aggravators": [],
                "accompanying": [],
                "confidence": 0.0,
            }

    def _extract_symptom_context(self, text: str, symptom: str)-> str:
        """提取症状周围的上下文"""
        symptom_pos = text.find(symptom)
        if symptom_pos == - 1:
            return text

        # 提取症状前后各50个字符的上下文
        start = max(0, symptom_pos - 50)
        end = min(len(text), symptom_pos + len(symptom) + 50)

        return text[start:end]

    async def _analyze_triggers(self, context: str)-> list[dict[str, Any]]:
        """分析诱发因素"""
        triggers = []

        # 关键词匹配
        for category, keywords in self.trigger_keywords.items():
            for keyword in keywords:
                if keyword in context:
                    # 检查是否在诱发模式中
                    confidence = self._calculate_trigger_confidence(context, keyword)
                    if confidence > 0.3:
                        triggers.append(
                            {
                                "factor": keyword,
                                "category": category,
                                "confidence": confidence,
                                "context_snippet": self._extract_snippet(
                                    context, keyword
                                ),
                            }
                        )

        # 模式匹配
        pattern_triggers = self._extract_pattern_triggers(context)
        triggers.extend(pattern_triggers)

        # 去重和排序
        triggers = self._deduplicate_factors(triggers)
        triggers.sort(key = lambda x: x["confidence"], reverse = True)

        return triggers[:5]  # 最多返回5个诱发因素

    async def _analyze_relievers(self, context: str)-> list[dict[str, Any]]:
        """分析缓解因素"""
        relievers = []

        # 关键词匹配
        for category, keywords in self.relief_keywords.items():
            for keyword in keywords:
                if keyword in context:
                    confidence = self._calculate_relief_confidence(context, keyword)
                    if confidence > 0.3:
                        relievers.append(
                            {
                                "factor": keyword,
                                "category": category,
                                "confidence": confidence,
                                "context_snippet": self._extract_snippet(
                                    context, keyword
                                ),
                            }
                        )

        # 模式匹配
        pattern_relievers = self._extract_pattern_relievers(context)
        relievers.extend(pattern_relievers)

        # 去重和排序
        relievers = self._deduplicate_factors(relievers)
        relievers.sort(key = lambda x: x["confidence"], reverse = True)

        return relievers[:5]

    async def _analyze_aggravators(self, context: str)-> list[dict[str, Any]]:
        """分析加重因素"""
        aggravators = []

        # 关键词匹配
        for category, keywords in self.aggravating_keywords.items():
            for keyword in keywords:
                if keyword in context:
                    confidence = self._calculate_aggravating_confidence(
                        context, keyword
                    )
                    if confidence > 0.3:
                        aggravators.append(
                            {
                                "factor": keyword,
                                "category": category,
                                "confidence": confidence,
                                "context_snippet": self._extract_snippet(
                                    context, keyword
                                ),
                            }
                        )

        # 模式匹配
        pattern_aggravators = self._extract_pattern_aggravators(context)
        aggravators.extend(pattern_aggravators)

        # 去重和排序
        aggravators = self._deduplicate_factors(aggravators)
        aggravators.sort(key = lambda x: x["confidence"], reverse = True)

        return aggravators[:5]

    async def _analyze_accompanying_symptoms(
        self, context: str
    )-> list[dict[str, Any]]:
        """分析伴随症状"""
        accompanying = []

        for category, keywords in self.accompanying_keywords.items():
            for keyword in keywords:
                if keyword in context:
                    confidence = self._calculate_accompanying_confidence(
                        context, keyword
                    )
                    if confidence > 0.4:
                        accompanying.append(
                            {
                                "symptom": keyword,
                                "category": category,
                                "confidence": confidence,
                                "context_snippet": self._extract_snippet(
                                    context, keyword
                                ),
                            }
                        )

        # 去重和排序
        accompanying = self._deduplicate_factors(accompanying, key = "symptom")
        accompanying.sort(key = lambda x: x["confidence"], reverse = True)

        return accompanying[:8]  # 最多返回8个伴随症状

    async def _analyze_temporal_context(self, context: str)-> dict[str, Any]:
        """分析时间相关上下文"""
        temporal = {}

        # 时间模式
        time_patterns = {
            "morning": r"(早上|上午|清晨|晨起)",
            "afternoon": r"(下午|午后)",
            "evening": r"(晚上|傍晚|黄昏)",
            "night": r"(夜里|夜间|深夜|半夜)",
            "meal_related": r"(饭前|饭后|空腹|饱餐)",
            "sleep_related": r"(睡前|睡后|醒来|起床)",
            "seasonal": r"(春天|夏天|秋天|冬天|换季)",
            "weather": r"(下雨|阴天|晴天|刮风|潮湿|干燥)",
        }

        for time_type, pattern in time_patterns.items():
            match = re.search(pattern, context)
            if match:
                temporal[time_type] = {
                    "text": match.group(0),
                    "position": match.start(),
                    "confidence": 0.7,
                }

        return temporal

    async def _analyze_environmental_context(self, context: str)-> dict[str, Any]:
        """分析环境相关上下文"""
        environmental = {}

        # 环境模式
        env_patterns = {
            "location": r"(在|到|去). * ?(家|办公室|学校|医院|户外|室内)",
            "noise": r"(噪音|吵闹|安静|嘈杂)",
            "light": r"(强光|刺眼|黑暗|昏暗|明亮)",
            "temperature": r"(热|冷|温暖|凉爽|闷热)",
            "air_quality": r"(空气|通风|闷|新鲜|污染|灰尘)",
            "crowd": r"(人多|拥挤|安静|独处)",
        }

        for env_type, pattern in env_patterns.items():
            match = re.search(pattern, context)
            if match:
                environmental[env_type] = {
                    "text": match.group(0),
                    "position": match.start(),
                    "confidence": 0.6,
                }

        return environmental

    def _calculate_trigger_confidence(self, context: str, keyword: str)-> float:
        """计算诱发因素的置信度"""
        confidence = 0.5  # 基础置信度

        # 检查诱发模式
        trigger_indicators = [
            "因为",
            "由于",
            "当",
            "在",
            "每当",
            "一旦",
            "遇到",
            "碰到",
        ]
        for indicator in trigger_indicators:
            if indicator in context:
                confidence += 0.2
                break

        # 检查结果词
        result_words = ["就", "便", "会", "开始", "出现", "发作"]
        for word in result_words:
            if word in context:
                confidence += 0.1
                break

        return min(confidence, 1.0)

    def _calculate_relief_confidence(self, context: str, keyword: str)-> float:
        """计算缓解因素的置信度"""
        confidence = 0.5

        # 检查缓解模式
        relief_indicators = ["通过", "经过", "用", "吃", "服", "后", "之后"]
        for indicator in relief_indicators:
            if indicator in context:
                confidence += 0.2
                break

        # 检查缓解词
        relief_words = ["缓解", "减轻", "好转", "消失", "改善"]
        for word in relief_words:
            if word in context:
                confidence += 0.2
                break

        return min(confidence, 1.0)

    def _calculate_aggravating_confidence(self, context: str, keyword: str)-> float:
        """计算加重因素的置信度"""
        confidence = 0.5

        # 检查加重模式
        aggravating_indicators = ["当", "在", "每当", "一旦", "遇到", "碰到"]
        for indicator in aggravating_indicators:
            if indicator in context:
                confidence += 0.2
                break

        # 检查加重词
        aggravating_words = ["加重", "严重", "厉害", "恶化", "更痛"]
        for word in aggravating_words:
            if word in context:
                confidence += 0.2
                break

        return min(confidence, 1.0)

    def _calculate_accompanying_confidence(self, context: str, keyword: str)-> float:
        """计算伴随症状的置信度"""
        confidence = 0.6

        # 检查伴随模式
        accompanying_indicators = ["同时", "还有", "伴有", "并且", "以及", "另外"]
        for indicator in accompanying_indicators:
            if indicator in context:
                confidence += 0.2
                break

        return min(confidence, 1.0)

    def _extract_snippet(self, context: str, keyword: str)-> str:
        """提取关键词周围的文本片段"""
        pos = context.find(keyword)
        if pos == - 1:
            return ""

        start = max(0, pos - 15)
        end = min(len(context), pos + len(keyword) + 15)

        return context[start:end]

    def _extract_pattern_triggers(self, context: str)-> list[dict[str, Any]]:
        """使用模式提取诱发因素"""
        triggers = []

        for pattern in self.context_patterns["trigger"]:
            matches = re.finditer(pattern, context)
            for match in matches:
                if len(match.groups()) >= 2:
                    factor = match.group(2)
                    triggers.append(
                        {
                            "factor": factor,
                            "category": "pattern_detected",
                            "confidence": 0.7,
                            "context_snippet": match.group(0),
                        }
                    )

        return triggers

    def _extract_pattern_relievers(self, context: str)-> list[dict[str, Any]]:
        """使用模式提取缓解因素"""
        relievers = []

        for pattern in self.context_patterns["relief"]:
            matches = re.finditer(pattern, context)
            for match in matches:
                if len(match.groups()) >= 2:
                    factor = (
                        match.group(2) if len(match.groups()) > 1 else match.group(1)
                    )
                    relievers.append(
                        {
                            "factor": factor,
                            "category": "pattern_detected",
                            "confidence": 0.7,
                            "context_snippet": match.group(0),
                        }
                    )

        return relievers

    def _extract_pattern_aggravators(self, context: str)-> list[dict[str, Any]]:
        """使用模式提取加重因素"""
        aggravators = []

        for pattern in self.context_patterns["aggravating"]:
            matches = re.finditer(pattern, context)
            for match in matches:
                if len(match.groups()) >= 2:
                    factor = match.group(2)
                    aggravators.append(
                        {
                            "factor": factor,
                            "category": "pattern_detected",
                            "confidence": 0.7,
                            "context_snippet": match.group(0),
                        }
                    )

        return aggravators

    def _deduplicate_factors(
        self, factors: list[dict[str, Any]], key: str = "factor"
    )-> list[dict[str, Any]]:
        """去除重复的因素"""
        seen = set()
        unique_factors = []

        for factor in factors:
            factor_key = factor[key]
            if factor_key not in seen:
                seen.add(factor_key)
                unique_factors.append(factor)

        return unique_factors
