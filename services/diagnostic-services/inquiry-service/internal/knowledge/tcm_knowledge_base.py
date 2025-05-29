#!/usr/bin/env python

"""
中医知识库模块，管理和查询中医相关知识数据
"""

import logging
import os
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class TCMKnowledgeBase:
    """中医知识库管理类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化中医知识库

        Args:
            config: 配置信息
        """
        self.config = config
        self.tcm_config = config.get("tcm_knowledge", {})

        # 数据目录
        self.data_dir = self.tcm_config.get("data_dir", "./data/tcm_knowledge")

        # 配置选项
        self.enable_traditional_terms = self.tcm_config.get(
            "enable_traditional_terms", True
        )
        self.enable_simplified_terms = self.tcm_config.get(
            "enable_simplified_terms", True
        )
        self.confidence_threshold = self.tcm_config.get("confidence_threshold", 0.7)
        self.auto_create_sample_data = self.tcm_config.get(
            "auto_create_sample_data", True
        )

        # 知识库数据
        self.patterns = {}  # 证型数据
        self.symptoms = {}  # 症状数据
        self.symptom_pattern_mapping = {}  # 症状-证型映射
        self.pattern_categories = {}  # 证型分类
        self.body_locations = {}  # 身体部位

        # 索引数据
        self.symptom_aliases = {}  # 症状别名索引
        self.pattern_aliases = {}  # 证型别名索引

        # 加载知识库
        self._load_knowledge_base()

        logger.info("中医知识库初始化完成")

    def _load_knowledge_base(self):
        """加载知识库数据"""
        try:
            # 确保数据目录存在
            os.makedirs(self.data_dir, exist_ok=True)

            # 检查数据文件是否存在
            data_files = {
                "patterns.yaml": self._load_patterns,
                "symptoms.yaml": self._load_symptoms,
                "symptom_pattern_mapping.yaml": self._load_symptom_pattern_mapping,
                "pattern_categories.yaml": self._load_pattern_categories,
                "body_locations.yaml": self._load_body_locations,
            }

            # 如果任何文件不存在且启用自动创建，则创建示例数据
            missing_files = [
                f
                for f in data_files
                if not os.path.exists(os.path.join(self.data_dir, f))
            ]

            if missing_files and self.auto_create_sample_data:
                logger.info(f"缺少数据文件: {missing_files}，创建示例数据...")
                self._create_sample_data()

            # 加载各类数据
            for filename, loader_func in data_files.items():
                filepath = os.path.join(self.data_dir, filename)
                if os.path.exists(filepath):
                    loader_func(filepath)
                else:
                    logger.warning(f"数据文件不存在: {filepath}")

            # 构建索引
            self._build_indexes()

            logger.info(
                f"知识库加载完成: {len(self.patterns)}个证型, "
                f"{len(self.symptoms)}个症状, "
                f"{len(self.symptom_pattern_mapping)}个映射关系"
            )

        except Exception as e:
            logger.error(f"加载知识库失败: {e!s}")

    def _create_sample_data(self):
        """创建示例数据"""
        try:
            # 创建证型数据
            patterns_data = {
                "气虚证": {
                    "id": "qi_deficiency",
                    "name": "气虚证",
                    "aliases": ["气不足", "元气虚弱"],
                    "category": "虚证",
                    "description": "气虚证是指人体内气的不足所导致的一系列症状，表现为疲劳、气短、自汗等",
                    "common_symptoms": ["疲劳", "气短", "自汗", "声音低弱", "面色萎黄"],
                    "pathogenesis": "过度劳累、久病耗气、饮食失调等导致气的生成不足或消耗过度",
                    "treatment_principle": "补气健脾",
                    "common_herbs": ["人参", "黄芪", "白术", "山药"],
                    "dietary_advice": ["多吃补气食物如山药、大枣", "避免生冷寒凉食物"],
                    "lifestyle_advice": ["适量运动，避免过度劳累", "保证充足睡眠"],
                },
                "阳虚证": {
                    "id": "yang_deficiency",
                    "name": "阳虚证",
                    "aliases": ["阳气不足", "虚寒证"],
                    "category": "虚证",
                    "description": "阳虚证是指机体阳气不足，温煦功能减退所表现的证候",
                    "common_symptoms": ["畏寒", "肢冷", "腰膝酸软", "夜尿频多", "便溏"],
                    "pathogenesis": "先天不足、久病耗阳、年老体衰等导致阳气虚损",
                    "treatment_principle": "温补阳气",
                    "common_herbs": ["附子", "肉桂", "干姜", "巴戟天"],
                    "dietary_advice": ["多吃温热食物如羊肉、生姜", "避免寒凉食物"],
                    "lifestyle_advice": ["注意保暖", "适当晒太阳", "避免过度房劳"],
                },
                "阴虚证": {
                    "id": "yin_deficiency",
                    "name": "阴虚证",
                    "aliases": ["阴液不足", "虚热证"],
                    "category": "虚证",
                    "description": "阴虚证是指机体阴液不足，滋润、宁静功能减退所表现的证候",
                    "common_symptoms": ["口干", "潮热", "盗汗", "五心烦热", "便秘"],
                    "pathogenesis": "热病伤阴、久病耗阴、情志内伤等导致阴液亏损",
                    "treatment_principle": "滋阴降火",
                    "common_herbs": ["生地黄", "麦冬", "玄参", "百合"],
                    "dietary_advice": ["多吃滋阴食物如银耳、百合", "避免辛辣刺激食物"],
                    "lifestyle_advice": ["避免熬夜", "保持心情平和", "适量饮水"],
                },
                "湿热证": {
                    "id": "damp_heat",
                    "name": "湿热证",
                    "aliases": ["湿热内蕴", "湿热困脾"],
                    "category": "实证",
                    "description": "湿热证是指湿邪与热邪相合，蕴结体内所表现的证候",
                    "common_symptoms": [
                        "口苦",
                        "身重",
                        "小便黄赤",
                        "大便黏滞",
                        "舌苔黄腻",
                    ],
                    "pathogenesis": "饮食不节、环境潮湿、情志不畅等导致湿热内生",
                    "treatment_principle": "清热利湿",
                    "common_herbs": ["黄连", "黄芩", "茵陈", "滑石"],
                    "dietary_advice": ["清淡饮食", "多吃清热利湿食物如冬瓜、薏米"],
                    "lifestyle_advice": ["保持环境干燥", "规律作息", "适量运动"],
                },
            }

            # 创建症状数据
            symptoms_data = {
                "疲劳": {
                    "id": "fatigue",
                    "name": "疲劳",
                    "aliases": ["乏力", "倦怠", "无力"],
                    "description": "全身或局部感到疲乏无力，精神不振",
                    "body_locations": ["全身"],
                    "related_patterns": ["气虚证", "阳虚证", "血虚证"],
                    "severity_indicators": {
                        "mild": "轻度疲劳，休息后可缓解",
                        "moderate": "中度疲劳，影响日常活动",
                        "severe": "重度疲劳，严重影响生活质量",
                    },
                },
                "头痛": {
                    "id": "headache",
                    "name": "头痛",
                    "aliases": ["头疼", "偏头痛"],
                    "description": "头部疼痛不适",
                    "body_locations": ["头部"],
                    "related_patterns": ["肝阳上亢", "风寒犯表", "血瘀证"],
                    "severity_indicators": {
                        "mild": "轻微头痛，不影响活动",
                        "moderate": "中度头痛，影响注意力",
                        "severe": "剧烈头痛，需要卧床休息",
                    },
                },
                "失眠": {
                    "id": "insomnia",
                    "name": "失眠",
                    "aliases": ["不寐", "睡眠障碍"],
                    "description": "入睡困难或睡眠质量差",
                    "body_locations": ["神志"],
                    "related_patterns": ["心肾不交", "肝火上炎", "心脾两虚"],
                    "severity_indicators": {
                        "mild": "偶尔失眠",
                        "moderate": "经常失眠，影响白天精神",
                        "severe": "严重失眠，彻夜难眠",
                    },
                },
            }

            # 创建映射数据
            mapping_data = {
                "mappings": [
                    {
                        "symptom": "疲劳",
                        "pattern": "气虚证",
                        "weight": 0.8,
                        "notes": "疲劳是气虚证的主要症状之一",
                    },
                    {
                        "symptom": "疲劳",
                        "pattern": "阳虚证",
                        "weight": 0.6,
                        "notes": "阳虚也可导致疲劳，常伴有畏寒",
                    },
                    {
                        "symptom": "畏寒",
                        "pattern": "阳虚证",
                        "weight": 0.9,
                        "notes": "畏寒是阳虚证的典型表现",
                    },
                    {
                        "symptom": "口干",
                        "pattern": "阴虚证",
                        "weight": 0.8,
                        "notes": "口干是阴虚证的常见症状",
                    },
                ]
            }

            # 创建分类数据
            categories_data = {
                "虚实": {
                    "虚证": ["气虚证", "血虚证", "阴虚证", "阳虚证"],
                    "实证": ["气滞证", "血瘀证", "痰湿证", "湿热证"],
                },
                "寒热": {
                    "寒证": ["寒湿证", "阳虚证"],
                    "热证": ["实热证", "阴虚内热证", "湿热证"],
                },
                "表里": {
                    "表证": ["风寒表证", "风热表证"],
                    "里证": ["里实证", "里虚证"],
                },
            }

            # 创建身体部位数据
            body_locations_data = {
                "头部": {
                    "id": "head",
                    "name": "头部",
                    "sub_locations": ["前额", "头顶", "后脑", "太阳穴"],
                    "related_organs": ["脑", "眼", "耳", "鼻"],
                    "common_symptoms": ["头痛", "眩晕", "耳鸣", "鼻塞"],
                },
                "胸部": {
                    "id": "chest",
                    "name": "胸部",
                    "sub_locations": ["心前区", "胸骨后", "两胁"],
                    "related_organs": ["心", "肺"],
                    "common_symptoms": ["胸痛", "胸闷", "心悸", "咳嗽"],
                },
                "腹部": {
                    "id": "abdomen",
                    "name": "腹部",
                    "sub_locations": ["上腹", "中腹", "下腹", "两胁"],
                    "related_organs": ["胃", "肠", "肝", "脾"],
                    "common_symptoms": ["腹痛", "腹胀", "恶心", "便秘"],
                },
            }

            # 保存数据文件
            files_to_create = {
                "patterns.yaml": patterns_data,
                "symptoms.yaml": symptoms_data,
                "symptom_pattern_mapping.yaml": mapping_data,
                "pattern_categories.yaml": categories_data,
                "body_locations.yaml": body_locations_data,
            }

            for filename, data in files_to_create.items():
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
                logger.info(f"创建示例数据文件: {filepath}")

        except Exception as e:
            logger.error(f"创建示例数据失败: {e!s}")

    def _load_patterns(self, filepath: str):
        """加载证型数据"""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.patterns = data if data else {}
                logger.info(f"加载了 {len(self.patterns)} 个证型")
        except Exception as e:
            logger.error(f"加载证型数据失败: {e!s}")

    def _load_symptoms(self, filepath: str):
        """加载症状数据"""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.symptoms = data if data else {}
                logger.info(f"加载了 {len(self.symptoms)} 个症状")
        except Exception as e:
            logger.error(f"加载症状数据失败: {e!s}")

    def _load_symptom_pattern_mapping(self, filepath: str):
        """加载症状-证型映射"""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "mappings" in data:
                    # 转换为便于查询的格式
                    for mapping in data["mappings"]:
                        symptom = mapping["symptom"]
                        pattern = mapping["pattern"]
                        weight = mapping.get("weight", 0.5)

                        if symptom not in self.symptom_pattern_mapping:
                            self.symptom_pattern_mapping[symptom] = []

                        self.symptom_pattern_mapping[symptom].append(
                            {
                                "pattern": pattern,
                                "weight": weight,
                                "notes": mapping.get("notes", ""),
                            }
                        )

                logger.info(
                    f"加载了 {len(self.symptom_pattern_mapping)} 个症状映射关系"
                )
        except Exception as e:
            logger.error(f"加载症状-证型映射失败: {e!s}")

    def _load_pattern_categories(self, filepath: str):
        """加载证型分类"""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.pattern_categories = data if data else {}
                logger.info(f"加载了 {len(self.pattern_categories)} 个证型分类")
        except Exception as e:
            logger.error(f"加载证型分类失败: {e!s}")

    def _load_body_locations(self, filepath: str):
        """加载身体部位数据"""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.body_locations = data if data else {}
                logger.info(f"加载了 {len(self.body_locations)} 个身体部位")
        except Exception as e:
            logger.error(f"加载身体部位数据失败: {e!s}")

    def _build_indexes(self):
        """构建索引以提高查询效率"""
        try:
            # 构建症状别名索引
            for symptom_name, symptom_data in self.symptoms.items():
                if isinstance(symptom_data, dict):
                    # 添加主名称
                    self.symptom_aliases[symptom_name.lower()] = symptom_name

                    # 添加别名
                    aliases = symptom_data.get("aliases", [])
                    for alias in aliases:
                        self.symptom_aliases[alias.lower()] = symptom_name

            # 构建证型别名索引
            for pattern_name, pattern_data in self.patterns.items():
                if isinstance(pattern_data, dict):
                    # 添加主名称
                    self.pattern_aliases[pattern_name.lower()] = pattern_name

                    # 添加别名
                    aliases = pattern_data.get("aliases", [])
                    for alias in aliases:
                        self.pattern_aliases[alias.lower()] = pattern_name

            logger.info(
                f"构建索引完成: {len(self.symptom_aliases)}个症状别名, "
                f"{len(self.pattern_aliases)}个证型别名"
            )

        except Exception as e:
            logger.error(f"构建索引失败: {e!s}")

    def get_symptom_info(self, symptom_name: str) -> dict | None:
        """
        获取症状信息

        Args:
            symptom_name: 症状名称

        Returns:
            症状信息字典，如果不存在则返回None
        """
        # 先尝试直接匹配
        if symptom_name in self.symptoms:
            return self.symptoms[symptom_name]

        # 尝试别名匹配
        normalized_name = symptom_name.lower()
        if normalized_name in self.symptom_aliases:
            actual_name = self.symptom_aliases[normalized_name]
            return self.symptoms.get(actual_name)

        return None

    def get_pattern_info(self, pattern_name: str) -> dict | None:
        """
        获取证型信息

        Args:
            pattern_name: 证型名称

        Returns:
            证型信息字典，如果不存在则返回None
        """
        # 先尝试直接匹配
        if pattern_name in self.patterns:
            return self.patterns[pattern_name]

        # 尝试别名匹配
        normalized_name = pattern_name.lower()
        if normalized_name in self.pattern_aliases:
            actual_name = self.pattern_aliases[normalized_name]
            return self.patterns.get(actual_name)

        return None

    def get_patterns_by_symptoms(self, symptoms: list[str]) -> list[dict]:
        """
        根据症状列表获取可能的证型

        Args:
            symptoms: 症状名称列表

        Returns:
            证型列表，按匹配度排序
        """
        pattern_scores = {}

        for symptom in symptoms:
            # 获取症状对应的证型
            mappings = self.symptom_pattern_mapping.get(symptom, [])

            # 如果直接匹配失败，尝试别名匹配
            if not mappings:
                normalized = symptom.lower()
                if normalized in self.symptom_aliases:
                    actual_symptom = self.symptom_aliases[normalized]
                    mappings = self.symptom_pattern_mapping.get(actual_symptom, [])

            # 累计证型得分
            for mapping in mappings:
                pattern = mapping["pattern"]
                weight = mapping["weight"]

                if pattern not in pattern_scores:
                    pattern_scores[pattern] = 0

                pattern_scores[pattern] += weight

        # 转换为列表并排序
        results = []
        for pattern, score in pattern_scores.items():
            pattern_info = self.get_pattern_info(pattern)
            if pattern_info:
                results.append(
                    {
                        "pattern_name": pattern,
                        "match_score": score / len(symptoms),  # 归一化得分
                        "matched_symptoms": symptoms,
                        "pattern_info": pattern_info,
                    }
                )

        # 按匹配度排序
        results.sort(key=lambda x: x["match_score"], reverse=True)

        # 只返回置信度超过阈值的结果
        return [r for r in results if r["match_score"] >= self.confidence_threshold]

    def get_symptoms_by_body_location(self, location: str) -> list[str]:
        """
        根据身体部位获取常见症状

        Args:
            location: 身体部位名称

        Returns:
            症状列表
        """
        location_info = self.body_locations.get(location)
        if location_info and isinstance(location_info, dict):
            return location_info.get("common_symptoms", [])

        # 搜索子部位
        for loc_name, loc_data in self.body_locations.items():
            if isinstance(loc_data, dict):
                sub_locations = loc_data.get("sub_locations", [])
                if location in sub_locations:
                    return loc_data.get("common_symptoms", [])

        return []

    def get_pattern_category(self, pattern_name: str) -> dict[str, str]:
        """
        获取证型的分类信息

        Args:
            pattern_name: 证型名称

        Returns:
            分类信息字典
        """
        categories = {}

        for category_type, category_data in self.pattern_categories.items():
            for category_name, patterns in category_data.items():
                if pattern_name in patterns:
                    categories[category_type] = category_name

        return categories

    def search_symptoms(self, keyword: str) -> list[str]:
        """
        搜索包含关键词的症状

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的症状列表
        """
        keyword_lower = keyword.lower()
        matched_symptoms = set()

        # 搜索症状名称
        for symptom_name in self.symptoms.keys():
            if keyword_lower in symptom_name.lower():
                matched_symptoms.add(symptom_name)

        # 搜索症状别名
        for alias, actual_name in self.symptom_aliases.items():
            if keyword_lower in alias:
                matched_symptoms.add(actual_name)

        # 搜索症状描述
        for symptom_name, symptom_data in self.symptoms.items():
            if isinstance(symptom_data, dict):
                description = symptom_data.get("description", "")
                if keyword_lower in description.lower():
                    matched_symptoms.add(symptom_name)

        return list(matched_symptoms)

    def get_treatment_suggestions(self, pattern_name: str) -> dict[str, Any]:
        """
        获取证型的治疗建议

        Args:
            pattern_name: 证型名称

        Returns:
            治疗建议字典
        """
        pattern_info = self.get_pattern_info(pattern_name)

        if not pattern_info:
            return {}

        return {
            "treatment_principle": pattern_info.get("treatment_principle", ""),
            "common_herbs": pattern_info.get("common_herbs", []),
            "dietary_advice": pattern_info.get("dietary_advice", []),
            "lifestyle_advice": pattern_info.get("lifestyle_advice", []),
        }

    def validate_symptom(self, symptom: str) -> bool:
        """
        验证症状是否在知识库中

        Args:
            symptom: 症状名称

        Returns:
            是否存在
        """
        return symptom in self.symptoms or symptom.lower() in self.symptom_aliases

    def validate_pattern(self, pattern: str) -> bool:
        """
        验证证型是否在知识库中

        Args:
            pattern: 证型名称

        Returns:
            是否存在
        """
        return pattern in self.patterns or pattern.lower() in self.pattern_aliases

    async def check_health(self) -> bool:
        """健康检查"""
        try:
            # 检查是否加载了基本数据
            return (
                len(self.patterns) > 0
                and len(self.symptoms) > 0
                and len(self.symptom_pattern_mapping) > 0
            )
        except Exception:
            return False
