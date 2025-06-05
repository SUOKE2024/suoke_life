#!/usr/bin/env python

"""
症状提取器模块，用于从用户文本中提取症状信息
"""

import json
import logging
import os
import re
from typing import Any

from internal.llm.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SymptomExtractor:
    """症状提取器类，负责从文本中提取症状信息"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化症状提取器

        Args:
            config: 配置信息
        """
        self.config = config
        self.extractor_config = config.get("symptom_extraction", {})

        # 症状提取配置
        self.model_path = self.extractor_config.get("model_path", "")
        self.min_confidence = self.extractor_config.get("min_confidence", 0.6)
        self.batch_size = self.extractor_config.get("batch_size", 16)
        self.enable_negation_detection = self.extractor_config.get(
            "enable_negation_detection", True
        )
        self.max_symptoms_per_text = self.extractor_config.get(
            "max_symptoms_per_text", 30
        )

        # 症状映射与分类
        self.symptoms_mapping_path = config.get("tcm_knowledge", {}).get(
            "symptoms_mapping_path", ""
        )
        self.symptoms_map = self._load_symptoms_map()

        # 症状关键词
        self.symptom_keywords = self._load_symptom_keywords()

        # 否定词
        self.negation_words = [
            "没有",
            "不",
            "不存在",
            "不会",
            "不曾",
            "不再",
            "无",
            "未",
            "否认",
            "拒绝",
            "排除",
            "不太",
            "不怎么",
            "从不",
            "从来不",
            "不敢说",
            "不确定",
            "不一定",
            "尚未",
            "不能确定",
            "并非",
        ]

        # 模型加载（如果使用NER模型）
        self.model = None
        self.tokenizer = None
        if self.model_path and os.path.exists(self.model_path):
            self._load_model()

        # LLM客户端（用于高级症状提取）
        self.llm_client = None
        llm_config = config.get("llm", {})
        if llm_config.get("use_llm_extraction", False) or llm_config.get("use_mock_mode", False):
            self.llm_client = LLMClient(llm_config)

        logger.info("症状提取器初始化完成")

    def _load_symptoms_map(self) -> dict:
        """加载症状映射表"""
        try:
            if self.symptoms_mapping_path and os.path.exists(
                self.symptoms_mapping_path
            ):
                with open(self.symptoms_mapping_path, encoding="utf-8") as file:
                    data = json.load(file)

                    # 验证加载的数据格式
                    if isinstance(data, list):
                        # 如果是列表格式，转换为字典格式
                        logger.warning("症状映射文件是列表格式，转换为字典格式")
                        return self._get_default_symptoms_map()
                    elif isinstance(data, dict):
                        return data
                    else:
                        logger.error("症状映射文件格式不正确，使用默认映射")
                        return self._get_default_symptoms_map()
            else:
                logger.warning("症状映射文件不存在，将使用内置的基本症状映射")
                return self._get_default_symptoms_map()
        except Exception as e:
            logger.error(f"加载症状映射失败: {e!s}")
            return self._get_default_symptoms_map()

    def _get_default_symptoms_map(self) -> dict:
        """获取默认的症状映射"""
        # 简单版本的中西医症状映射，实际应用中应该更完整
        return {
            "symptom_categories": {
                "head": ["头痛", "头晕", "头胀", "偏头痛", "头重", "颈痛"],
                "chest": ["胸闷", "胸痛", "心悸", "气短", "憋气", "咳嗽", "咳痰"],
                "abdomen": [
                    "腹痛",
                    "腹胀",
                    "恶心",
                    "呕吐",
                    "腹泻",
                    "便秘",
                    "消化不良",
                    "嗳气",
                ],
                "limbs": ["关节痛", "肌肉酸痛", "肢体麻木", "腿软", "手脚冰凉", "抽筋"],
                "senses": ["视力下降", "听力下降", "耳鸣", "嗅觉减退", "味觉改变"],
                "sleep": ["失眠", "多梦", "易醒", "嗜睡", "睡眠不深", "睡眠", "醒来", "睡不好"],
                "mental": ["焦虑", "抑郁", "烦躁", "易怒", "情绪波动", "记忆力下降"],
                "energy": ["疲劳", "乏力", "精神不振", "体力下降", "懒言"],
            },
            "tcm_mapping": {
                "气虚症状": [
                    "疲劳",
                    "乏力",
                    "气短",
                    "懒言",
                    "自汗",
                    "动则汗出",
                    "语声低弱",
                    "气短懒言",
                ],
                "血虚症状": [
                    "面色苍白",
                    "唇甲色淡",
                    "头晕",
                    "眼花",
                    "失眠",
                    "心悸",
                    "月经量少",
                ],
                "阴虚症状": [
                    "口干",
                    "咽干",
                    "五心烦热",
                    "潮热",
                    "盗汗",
                    "失眠",
                    "颧红",
                    "手足心热",
                ],
                "阳虚症状": [
                    "怕冷",
                    "手脚冰凉",
                    "面色苍白",
                    "喜温",
                    "腰膝酸软",
                    "神疲",
                ],
                "痰湿症状": [
                    "痰多",
                    "胸闷",
                    "恶心",
                    "呕吐",
                    "腹胀",
                    "苔腻",
                    "头重",
                    "肢体沉重",
                ],
                "湿热症状": [
                    "口苦",
                    "口臭",
                    "小便黄",
                    "大便粘滞不爽",
                    "苔黄腻",
                    "身重",
                ],
                "气滞症状": [
                    "胸胁胀痛",
                    "情志不畅",
                    "嗳气",
                    "打嗝",
                    "痛处不固定",
                    "善太息",
                ],
                "血瘀症状": [
                    "疼痛固定",
                    "刺痛",
                    "肌肤甲错",
                    "舌质紫暗",
                    "口唇紫暗",
                    "瘀斑",
                ],
            },
            "severity": {
                "mild": ["有点", "轻微", "些许", "一点点", "偶尔", "不太", "有时"],
                "moderate": ["明显", "较为", "比较", "常常", "时常", "经常"],
                "severe": [
                    "严重",
                    "剧烈",
                    "难以忍受",
                    "极度",
                    "非常",
                    "特别",
                    "很",
                    "十分",
                ],
            },
            "duration": {
                "acute": ["突然", "刚刚", "今天", "昨天", "近日", "最近几天"],
                "subacute": ["最近", "这周", "这个月", "近期", "前段时间"],
                "chronic": ["长期", "一直", "总是", "很久", "几个月", "几年", "长达"],
            },
        }

    def _load_symptom_keywords(self) -> list[str]:
        """加载症状关键词列表"""
        # 从症状映射中提取所有症状关键词
        keywords = []

        # 从分类中提取
        for category, symptoms in self.symptoms_map.get(
            "symptom_categories", {}
        ).items():
            keywords.extend(symptoms)

        # 从中医映射中提取
        for pattern, symptoms in self.symptoms_map.get("tcm_mapping", {}).items():
            keywords.extend(symptoms)

        # 去重
        keywords = list(set(keywords))

        # 按长度排序，优先匹配较长的症状描述
        keywords.sort(key=len, reverse=True)

        return keywords

    def _load_model(self):
        """加载NER模型（如果配置）"""
        try:
            # 尝试加载配置的NER模型
            # 这里应该根据实际使用的模型类型进行加载
            # 例如使用基于HuggingFace transformers库的NER模型
            try:
                from transformers import AutoModelForTokenClassification, AutoTokenizer

                logger.info(f"正在加载症状提取模型: {self.model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForTokenClassification.from_pretrained(
                    self.model_path
                )
                logger.info("症状提取模型加载成功")
            except ImportError:
                logger.error("未安装transformers库，无法加载NER模型")
                self.model = None
            except Exception as e:
                logger.error(f"加载NER模型失败: {e!s}")
                self.model = None
        except Exception as e:
            logger.error(f"加载症状提取模型失败: {e!s}")
            self.model = None

    async def extract_symptoms(self, text: str) -> dict:
        """
        从文本中提取症状信息

        Args:
            text: 需要分析的文本

        Returns:
            Dict: 包含提取的症状、身体部位、时间因素和置信度
        """
        try:
            # 如果有LLM客户端，使用LLM提取
            if self.llm_client is not None:
                (
                    symptoms,
                    body_locations,
                    temporal_factors,
                    confidence,
                ) = await self._extract_with_llm(text)
            # 如果有NER模型，使用模型提取
            elif self.model is not None:
                (
                    symptoms,
                    body_locations,
                    temporal_factors,
                    confidence,
                ) = await self._extract_with_model(text)
            else:
                # 否则使用规则和关键词匹配
                symptoms, body_locations, temporal_factors, confidence = (
                    self._extract_with_rules(text)
                )

            # 限制症状数量
            if len(symptoms) > self.max_symptoms_per_text:
                # 按照置信度排序，保留置信度最高的
                symptoms.sort(key=lambda x: x["confidence"], reverse=True)
                symptoms = symptoms[: self.max_symptoms_per_text]

            result = {
                "symptoms": symptoms,
                "body_locations": body_locations,
                "temporal_factors": temporal_factors,
                "confidence_score": confidence,
            }

            logger.info(f"从文本中提取到 {len(symptoms)} 个症状")

            return result

        except Exception as e:
            logger.error(f"提取症状失败: {e!s}")
            # 如果是LLM相关错误，重新抛出异常
            if "LLM" in str(e) or "generate" in str(e):
                raise e
            # 其他错误返回默认结果
            return {
                "symptoms": [],
                "body_locations": [],
                "temporal_factors": [],
                "confidence_score": 0.0,
            }

    async def _extract_with_llm(
        self, text: str
    ) -> tuple[list[dict], list[dict], list[dict], float]:
        """使用LLM提取症状"""
        try:
            # 构建提示词
            prompt = f"""
请从以下文本中提取症状信息，并以JSON格式返回：

文本：{text}

请返回以下格式的JSON：
{{
    "symptoms": [
        {{
            "symptom_name": "症状名称",
            "severity": "MILD/MODERATE/SEVERE",
            "onset_time": 时间戳,
            "duration": 持续时间(秒),
            "description": "详细描述",
            "confidence": 置信度(0-1)
        }}
    ],
    "body_locations": [
        {{
            "location_name": "身体部位",
            "associated_symptoms": ["相关症状"],
            "side": "left/right/bilateral/central"
        }}
    ],
    "temporal_factors": [
        {{
            "factor_type": "时间类型",
            "description": "时间描述",
            "symptoms_affected": ["受影响的症状"]
        }}
    ],
    "confidence_score": 总体置信度
}}
"""

            # 调用LLM
            response = await self.llm_client.generate(prompt)
            
            # 解析JSON响应
            result = json.loads(response)
            
            return (
                result.get("symptoms", []),
                result.get("body_locations", []),
                result.get("temporal_factors", []),
                result.get("confidence_score", 0.0)
            )
            
        except Exception as e:
            logger.error(f"LLM症状提取失败: {e}")
            raise e

    async def _extract_with_model(
        self, text: str
    ) -> tuple[list[dict], list[dict], list[dict], float]:
        """使用NER模型提取症状"""
        try:
            import torch

            # 对文本进行编码
            inputs = self.tokenizer(
                text, return_tensors="pt", truncation=True, padding=True
            )

            # 推理
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.argmax(outputs.logits, dim=2)

            # 解码标签
            tokens = self.tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
            token_predictions = [
                self.model.config.id2label[p.item()] for p in predictions[0]
            ]

            # 提取实体
            symptoms = []
            body_locations = []
            temporal_factors = []

            # 实现NER结果的后处理
            # 这里需要根据具体的NER模型输出格式进行解析
            # 以下为示例代码，实际需要根据模型输出调整
            current_entity = None
            current_tokens = []

            for token, label in zip(tokens, token_predictions, strict=False):
                if label.startswith("B-SYMPTOM"):
                    if current_entity == "SYMPTOM":
                        # 添加之前的症状
                        symptom_text = self.tokenizer.convert_tokens_to_string(
                            current_tokens
                        )
                        symptoms.append(
                            {
                                "symptom_name": symptom_text,
                                "severity": "MODERATE",  # 默认严重程度
                                "confidence": 0.85,  # 默认置信度
                            }
                        )
                    current_entity = "SYMPTOM"
                    current_tokens = [token]
                elif label.startswith("B-BODY"):
                    if current_entity == "BODY":
                        # 添加之前的身体部位
                        body_text = self.tokenizer.convert_tokens_to_string(
                            current_tokens
                        )
                        body_locations.append(
                            {
                                "location_name": body_text,
                                "associated_symptoms": [],
                                "side": "central",  # 默认位置
                            }
                        )
                    current_entity = "BODY"
                    current_tokens = [token]
                elif label.startswith("B-TIME"):
                    if current_entity == "TIME":
                        # 添加之前的时间因素
                        time_text = self.tokenizer.convert_tokens_to_string(
                            current_tokens
                        )
                        temporal_factors.append(
                            {
                                "factor_type": "temporal",
                                "description": time_text,
                                "symptoms_affected": [],
                            }
                        )
                    current_entity = "TIME"
                    current_tokens = [token]
                elif label.startswith("I-") and current_entity:
                    # 继续当前实体
                    current_tokens.append(token)
                elif label == "O":
                    # 结束当前实体
                    if current_entity == "SYMPTOM" and current_tokens:
                        symptom_text = self.tokenizer.convert_tokens_to_string(
                            current_tokens
                        )
                        symptoms.append(
                            {
                                "symptom_name": symptom_text,
                                "severity": "MODERATE",
                                "confidence": 0.85,
                            }
                        )
                    elif current_entity == "BODY" and current_tokens:
                        body_text = self.tokenizer.convert_tokens_to_string(
                            current_tokens
                        )
                        body_locations.append(
                            {
                                "location_name": body_text,
                                "associated_symptoms": [],
                                "side": "central",
                            }
                        )
                    elif current_entity == "TIME" and current_tokens:
                        time_text = self.tokenizer.convert_tokens_to_string(
                            current_tokens
                        )
                        temporal_factors.append(
                            {
                                "factor_type": "temporal",
                                "description": time_text,
                                "symptoms_affected": [],
                            }
                        )
                    current_entity = None
                    current_tokens = []

            # 处理最后一个实体
            if current_entity == "SYMPTOM" and current_tokens:
                symptom_text = self.tokenizer.convert_tokens_to_string(current_tokens)
                symptoms.append(
                    {
                        "symptom_name": symptom_text,
                        "severity": "MODERATE",
                        "confidence": 0.85,
                    }
                )
            elif current_entity == "BODY" and current_tokens:
                body_text = self.tokenizer.convert_tokens_to_string(current_tokens)
                body_locations.append(
                    {
                        "location_name": body_text,
                        "associated_symptoms": [],
                        "side": "central",
                    }
                )
            elif current_entity == "TIME" and current_tokens:
                time_text = self.tokenizer.convert_tokens_to_string(current_tokens)
                temporal_factors.append(
                    {
                        "factor_type": "temporal",
                        "description": time_text,
                        "symptoms_affected": [],
                    }
                )

            # 关联症状和身体部位
            self._associate_symptoms_with_locations(symptoms, body_locations)

            # 根据症状、身体部位和时间因素的提取数量计算总体置信度
            total_entities = len(symptoms) + len(body_locations) + len(temporal_factors)
            if total_entities > 0:
                confidence = min(0.95, 0.7 + (total_entities / 20.0) * 0.25)
            else:
                confidence = 0.5

            return symptoms, body_locations, temporal_factors, confidence

        except Exception as e:
            logger.error(f"使用模型提取症状失败: {e!s}")
            # 回退到规则匹配
            return self._extract_with_rules(text)

    def _extract_with_rules(
        self, text: str
    ) -> tuple[list[dict], list[dict], list[dict], float]:
        """使用规则和关键词匹配提取症状"""
        symptoms = []
        body_locations = []
        temporal_factors = []

        # 1. 提取症状
        for keyword in self.symptom_keywords:
            if keyword in text:
                # 检查否定词
                if self.enable_negation_detection and self._is_negated(text, keyword):
                    continue

                # 提取症状严重程度
                severity = self._extract_severity(text, keyword)

                # 提取持续时间
                duration = self._extract_duration(text, keyword)

                symptoms.append(
                    {
                        "symptom_name": keyword,
                        "severity": severity,
                        "onset_time": 0,  # 未知开始时间
                        "duration": duration,
                        "description": f"从文本中提取的症状: {keyword}",
                        "confidence": 0.8,  # 默认置信度
                    }
                )

        # 2. 提取身体部位
        body_parts = {
            "头": ["头部", "脑袋", "头顶", "额头", "太阳穴"],
            "胸": ["胸部", "胸口", "胸腔"],
            "腹": ["腹部", "肚子", "腹腔", "胃部"],
            "背": ["背部", "脊椎", "后背"],
            "腰": ["腰部", "腰间"],
            "手": ["手部", "手腕", "手指", "手掌"],
            "脚": ["脚部", "脚踝", "脚趾", "脚掌"],
            "颈": ["颈部", "脖子"],
            "肩": ["肩部", "肩膀"],
            "腿": ["腿部", "大腿", "小腿", "膝盖"],
            "眼": ["眼睛", "眼球", "眼皮"],
            "耳": ["耳朵", "耳廓"],
            "鼻": ["鼻子", "鼻腔"],
            "口": ["嘴巴", "嘴唇", "口腔"],
            "皮肤": ["皮肤", "肌肤"],
        }

        for main_part, synonyms in body_parts.items():
            for term in [main_part] + synonyms:
                if term in text:
                    # 检查是否已经添加过这个部位
                    location_exists = False
                    for loc in body_locations:
                        if loc["location_name"] == main_part:
                            location_exists = True
                            break

                    if not location_exists:
                        # 确定方位 (左/右/双侧)
                        side = "central"
                        if f"左{term}" in text or f"{term}左" in text:
                            side = "left"
                        elif f"右{term}" in text or f"{term}右" in text:
                            side = "right"
                        elif f"两{term}" in text or f"双{term}" in text:
                            side = "bilateral"

                        body_locations.append(
                            {
                                "location_name": main_part,
                                "associated_symptoms": [],
                                "side": side,
                            }
                        )

        # 3. 提取时间因素
        time_patterns = {
            "diurnal": ["早上", "上午", "中午", "下午", "晚上", "夜间", "凌晨"],
            "seasonal": [
                "春天",
                "夏天",
                "秋天",
                "冬天",
                "春季",
                "夏季",
                "秋季",
                "冬季",
            ],
            "durational": [
                "持续",
                "一直",
                "长期",
                "短期",
                "几天",
                "几周",
                "几个月",
                "几年",
            ],
            "frequency": [
                "经常",
                "偶尔",
                "有时",
                "时常",
                "总是",
                "频繁",
                "很少",
                "从不",
            ],
            "triggers": [
                "吃完",
                "吃后",
                "饭后",
                "运动后",
                "劳累",
                "熬夜",
                "情绪",
                "受凉",
            ],
        }

        for factor_type, keywords in time_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    # 提取关联的症状
                    related_symptoms = []
                    for symptom in symptoms:
                        # 简单判断：如果症状和时间因素在同一句话中出现
                        sentences = re.split(r"[。！？.!?]", text)
                        for sentence in sentences:
                            if (
                                keyword in sentence
                                and symptom["symptom_name"] in sentence
                            ):
                                related_symptoms.append(symptom["symptom_name"])

                    # 构建上下文描述
                    context = ""
                    for sentence in re.split(r"[。！？.!?]", text):
                        if keyword in sentence:
                            context = sentence.strip()
                            break

                    if not context:
                        context = f"文本中提到: {keyword}"

                    temporal_factors.append(
                        {
                            "factor_type": factor_type,
                            "description": context,
                            "symptoms_affected": related_symptoms,
                        }
                    )

        # 关联症状和身体部位
        self._associate_symptoms_with_locations(symptoms, body_locations)

        # 根据提取到的信息计算置信度
        total_items = len(symptoms) + len(body_locations) + len(temporal_factors)
        if total_items > 0:
            confidence = min(0.9, 0.6 + (total_items / 15.0) * 0.3)
        else:
            # 如果没有提取到任何信息，置信度为0
            confidence = 0.0

        return symptoms, body_locations, temporal_factors, confidence

    def _is_negated(self, text: str, symptom: str) -> bool:
        """检查症状是否被否定词修饰"""
        # 分析文本上下文
        sentences = re.split(r"[。！？.!?]", text)
        for sentence in sentences:
            if symptom in sentence:
                # 检查句子中是否包含否定词
                for neg_word in self.negation_words:
                    # 检查否定词是否在症状之前的合理距离内
                    neg_pos = sentence.find(neg_word)
                    symptom_pos = sentence.find(symptom)
                    if (
                        neg_pos != -1
                        and neg_pos < symptom_pos
                        and symptom_pos - neg_pos < 15
                    ):
                        return True
        return False

    def _extract_severity(self, text: str, symptom: str) -> str:
        """提取症状的严重程度"""
        severity_indicators = self.symptoms_map.get("severity", {})

        # 获取包含症状的句子
        sentences = re.split(r"[。！？.!?]", text)
        for sentence in sentences:
            if symptom in sentence:
                # 检查各级严重程度指示词
                for level, indicators in severity_indicators.items():
                    for indicator in indicators:
                        # 检查指示词是否修饰这个症状
                        ind_pos = sentence.find(indicator)
                        symptom_pos = sentence.find(symptom)
                        if ind_pos != -1 and abs(ind_pos - symptom_pos) < 10:
                            if level == "mild":
                                return "MILD"
                            elif level == "moderate":
                                return "MODERATE"
                            elif level == "severe":
                                return "SEVERE"

        # 默认为中度
        return "MODERATE"

    def _extract_duration(self, text: str, symptom: str) -> int:
        """提取症状的持续时间(秒)"""
        duration_indicators = self.symptoms_map.get("duration", {})

        # 获取包含症状的句子
        sentences = re.split(r"[。！？.!?]", text)
        for sentence in sentences:
            if symptom in sentence:
                # 提取具体的时间段
                time_patterns = [
                    (r"(\d+)\s*年", lambda x: int(x) * 365 * 24 * 3600),
                    (r"(\d+)\s*个月", lambda x: int(x) * 30 * 24 * 3600),
                    (r"(\d+)\s*周", lambda x: int(x) * 7 * 24 * 3600),
                    (r"(\d+)\s*天", lambda x: int(x) * 24 * 3600),
                    (r"(\d+)\s*小时", lambda x: int(x) * 3600),
                    (r"(\d+)\s*分钟", lambda x: int(x) * 60),
                ]

                for pattern, converter in time_patterns:
                    match = re.search(pattern, sentence)
                    if match:
                        return converter(match.group(1))

                # 检查持续时间指示词
                for duration_type, indicators in duration_indicators.items():
                    for indicator in indicators:
                        if indicator in sentence:
                            if duration_type == "acute":
                                return 1 * 24 * 3600  # 1天
                            elif duration_type == "subacute":
                                return 14 * 24 * 3600  # 2周
                            elif duration_type == "chronic":
                                return 90 * 24 * 3600  # 3个月

        # 默认返回0表示未知
        return 0

    def _associate_symptoms_with_locations(
        self, symptoms: list[dict], body_locations: list[dict]
    ):
        """关联症状和身体部位"""
        # 简单关联：基于同一句话中出现
        # 这部分可以根据实际需求优化
        for location in body_locations:
            for symptom in symptoms:
                symp_name = symptom["symptom_name"]
                loc_name = location["location_name"]

                # 如果症状名称中包含身体部位，直接关联
                if loc_name in symp_name:
                    if symp_name not in location["associated_symptoms"]:
                        location["associated_symptoms"].append(symp_name)

        # 特定症状和身体部位的关联规则
        symptom_to_location = {
            "头痛": "头",
            "头晕": "头",
            "胸闷": "胸",
            "胸痛": "胸",
            "腹痛": "腹",
            "腹胀": "腹",
            "咳嗽": "胸",
            "背痛": "背",
            "腰痛": "腰",
            "肩痛": "肩",
            "颈痛": "颈",
            "手麻": "手",
            "脚麻": "脚",
            "膝盖痛": "腿",
        }

        for symptom in symptoms:
            symp_name = symptom["symptom_name"]
            if symp_name in symptom_to_location:
                loc_name = symptom_to_location[symp_name]

                # 寻找对应的身体部位
                for location in body_locations:
                    if location["location_name"] == loc_name:
                        if symp_name not in location["associated_symptoms"]:
                            location["associated_symptoms"].append(symp_name)
                        break
                else:
                    # 如果找不到对应的身体部位，创建一个新的
                    body_locations.append(
                        {
                            "location_name": loc_name,
                            "associated_symptoms": [symp_name],
                            "side": "central",
                        }
                    )

    async def extract_symptoms_with_knowledge(self, text: str, knowledge_base) -> dict:
        """
        使用知识库增强的症状提取

        Args:
            text: 需要分析的文本
            knowledge_base: 中医知识库实例

        Returns:
            Dict: 增强的症状提取结果
        """
        try:
            # 先进行基础症状提取
            base_result = await self.extract_symptoms(text)

            # 使用知识库验证和增强症状
            enhanced_symptoms = []
            for symptom in base_result["symptoms"]:
                symptom_name = symptom["symptom_name"]

                # 从知识库获取症状信息
                symptom_info = knowledge_base.get_symptom_info(symptom_name)

                if symptom_info:
                    # 更新症状描述和相关信息
                    symptom["description"] = symptom_info.get(
                        "description", symptom["description"]
                    )
                    symptom["related_patterns"] = symptom_info.get(
                        "related_patterns", []
                    )
                    symptom["validated"] = True
                    symptom["confidence"] = min(
                        symptom["confidence"] * 1.2, 0.95
                    )  # 提高置信度
                else:
                    # 尝试模糊匹配
                    similar_symptoms = knowledge_base.search_symptoms(symptom_name)
                    if similar_symptoms:
                        # 使用最相似的症状
                        symptom["symptom_name"] = similar_symptoms[0]
                        symptom["original_name"] = symptom_name
                        symptom["validated"] = True
                        symptom["confidence"] = symptom["confidence"] * 0.9
                    else:
                        symptom["validated"] = False

                enhanced_symptoms.append(symptom)

            # 根据症状推断可能的证型
            symptom_names = [
                s["symptom_name"]
                for s in enhanced_symptoms
                if s.get("validated", False)
            ]
            if symptom_names:
                possible_patterns = knowledge_base.get_patterns_by_symptoms(
                    symptom_names
                )

                # 添加证型信息到结果中
                base_result["possible_tcm_patterns"] = [
                    {
                        "pattern_name": p["pattern_name"],
                        "match_score": p["match_score"],
                        "category": p["pattern_info"].get("category", ""),
                        "description": p["pattern_info"].get("description", ""),
                    }
                    for p in possible_patterns[:5]  # 返回前5个最可能的证型
                ]
            else:
                base_result["possible_tcm_patterns"] = []

            # 更新增强后的症状列表
            base_result["symptoms"] = enhanced_symptoms

            # 增强身体部位信息
            for location in base_result["body_locations"]:
                loc_name = location["location_name"]
                # 从知识库获取该部位的常见症状
                common_symptoms = knowledge_base.get_symptoms_by_body_location(loc_name)

                # 检查这些常见症状是否在文本中出现
                location["potential_symptoms"] = []
                for common_symptom in common_symptoms:
                    if common_symptom in text:
                        location["potential_symptoms"].append(common_symptom)

            return base_result

        except Exception as e:
            logger.error(f"使用知识库增强症状提取失败: {e!s}")
            return base_result  # 返回基础结果

    def analyze_symptom_context(self, text: str, symptom: str) -> dict:
        """
        分析症状的上下文信息

        Args:
            text: 完整文本
            symptom: 症状名称

        Returns:
            Dict: 症状的上下文分析结果
        """
        context = {
            "triggers": [],  # 诱发因素
            "relieving_factors": [],  # 缓解因素
            "aggravating_factors": [],  # 加重因素
            "accompanying_symptoms": [],  # 伴随症状
            "timing": {},  # 时间特征
            "quality": [],  # 性质描述
        }

        # 获取包含症状的句子及其前后句
        sentences = re.split(r"[。！？.!?]", text)
        for i, sentence in enumerate(sentences):
            if symptom in sentence:
                # 当前句子和前后句组成上下文
                context_sentences = []
                if i > 0:
                    context_sentences.append(sentences[i - 1])
                context_sentences.append(sentence)
                if i < len(sentences) - 1:
                    context_sentences.append(sentences[i + 1])

                context_text = "。".join(context_sentences)

                # 分析诱发因素
                trigger_patterns = [
                    "吃.*后",
                    "饮.*后",
                    "运动后",
                    "劳累后",
                    "受凉后",
                    "生气后",
                    "着急后",
                    "熬夜后",
                    "喝酒后",
                    "吹风后",
                    "淋雨后",
                ]
                for pattern in trigger_patterns:
                    if re.search(pattern, context_text):
                        context["triggers"].append(pattern)

                # 分析缓解因素
                relief_patterns = [
                    "休息.*好转",
                    "吃.*缓解",
                    "按摩.*舒服",
                    "热敷.*减轻",
                    "服药.*好转",
                    "睡.*缓解",
                ]
                for pattern in relief_patterns:
                    if re.search(pattern, context_text):
                        context["relieving_factors"].append(pattern)

                # 分析加重因素
                aggravate_patterns = [
                    "活动.*加重",
                    "劳累.*严重",
                    "夜间.*明显",
                    "饭后.*加重",
                    "情绪.*严重",
                    "天冷.*加重",
                ]
                for pattern in aggravate_patterns:
                    if re.search(pattern, context_text):
                        context["aggravating_factors"].append(pattern)

                # 分析伴随症状
                # 在同一句中查找其他症状
                for other_symptom in self.symptom_keywords:
                    if other_symptom != symptom and other_symptom in sentence:
                        context["accompanying_symptoms"].append(other_symptom)

                # 分析时间特征
                time_features = {
                    "morning": ["早上", "早晨", "清晨", "凌晨"],
                    "afternoon": ["下午", "午后"],
                    "evening": ["晚上", "傍晚", "夜间", "深夜"],
                    "meal_related": ["饭前", "饭后", "空腹", "餐后"],
                }

                for feature, keywords in time_features.items():
                    for keyword in keywords:
                        if keyword in context_text:
                            context["timing"][feature] = True

                # 分析性质描述
                quality_patterns = {
                    "pain_quality": [
                        "刺痛",
                        "胀痛",
                        "隐痛",
                        "剧痛",
                        "钝痛",
                        "绞痛",
                        "灼痛",
                    ],
                    "sensation": ["麻木", "发凉", "发热", "沉重", "紧绷"],
                    "characteristics": ["持续", "间歇", "阵发", "游走", "固定"],
                }

                for quality_type, patterns in quality_patterns.items():
                    for pattern in patterns:
                        if pattern in context_text:
                            context["quality"].append(
                                {"type": quality_type, "description": pattern}
                            )

        return context

    def classify_symptom_by_tcm(self, symptom_name: str) -> dict:
        """
        根据中医理论对症状进行分类

        Args:
            symptom_name: 症状名称

        Returns:
            Dict: 中医分类信息
        """
        classification = {
            "pattern_associations": [],  # 关联的证型
            "organ_systems": [],  # 涉及的脏腑
            "pathogenic_factors": [],  # 病理因素
            "nature": "",  # 性质（寒热虚实）
        }

        # 查找症状在TCM映射中的位置
        for pattern_type, symptoms in self.symptoms_map.get("tcm_mapping", {}).items():
            if symptom_name in symptoms:
                classification["pattern_associations"].append(pattern_type)

                # 推断脏腑系统
                if "气虚" in pattern_type or "血虚" in pattern_type:
                    classification["organ_systems"].extend(["脾", "肺"])
                    classification["nature"] = "虚"
                elif "阴虚" in pattern_type:
                    classification["organ_systems"].extend(["肾", "肝"])
                    classification["nature"] = "虚热"
                elif "阳虚" in pattern_type:
                    classification["organ_systems"].extend(["肾", "脾"])
                    classification["nature"] = "虚寒"
                elif "痰湿" in pattern_type:
                    classification["organ_systems"].extend(["脾", "肺"])
                    classification["nature"] = "实"
                    classification["pathogenic_factors"].append("痰湿")
                elif "湿热" in pattern_type:
                    classification["organ_systems"].extend(["脾", "肝胆"])
                    classification["nature"] = "实热"
                    classification["pathogenic_factors"].extend(["湿", "热"])
                elif "气滞" in pattern_type:
                    classification["organ_systems"].extend(["肝", "脾"])
                    classification["nature"] = "实"
                    classification["pathogenic_factors"].append("气滞")
                elif "血瘀" in pattern_type:
                    classification["organ_systems"].extend(["肝", "心"])
                    classification["nature"] = "实"
                    classification["pathogenic_factors"].append("血瘀")

        # 根据症状特征推断
        symptom_characteristics = {
            "痛": {"organs": ["肝"], "factors": ["气滞", "血瘀"], "nature": "实"},
            "胀": {"organs": ["脾", "肝"], "factors": ["气滞"], "nature": "实"},
            "痒": {"organs": ["肺", "肝"], "factors": ["风", "血虚"], "nature": "虚"},
            "麻": {"organs": ["肝", "肾"], "factors": ["血虚", "痰湿"], "nature": "虚"},
            "热": {"organs": ["心", "肺"], "factors": ["热", "火"], "nature": "热"},
            "冷": {"organs": ["肾", "脾"], "factors": ["阳虚", "寒"], "nature": "寒"},
        }

        # 检查症状名称中的特征词
        for char, info in symptom_characteristics.items():
            if char in symptom_name:
                classification["organ_systems"].extend(info["organs"])
                classification["pathogenic_factors"].extend(info["factors"])
                if not classification["nature"]:
                    classification["nature"] = info["nature"]

        # 去重
        classification["organ_systems"] = list(set(classification["organ_systems"]))
        classification["pathogenic_factors"] = list(
            set(classification["pathogenic_factors"])
        )

        return classification

    async def check_health(self) -> bool:
        """健康检查"""
        try:
            # 检查是否加载了必要的数据
            return bool(self.symptom_keywords) and bool(self.symptoms_map)
        except Exception:
            return False
