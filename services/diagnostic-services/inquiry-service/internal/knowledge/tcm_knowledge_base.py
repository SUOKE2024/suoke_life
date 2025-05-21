#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医知识库模块，提供中医症状与证型的映射关系
"""

import logging
import json
import os
import yaml
from typing import Dict, List, Any, Tuple, Set, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TCMKnowledgeBase:
    """中医知识库类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化中医知识库
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.knowledge_config = config.get("tcm_knowledge", {})
        
        # 知识库加载路径
        self.data_dir = self.knowledge_config.get("data_dir", "data/tcm_knowledge")
        
        # 加载标志
        self._initialized = False
        self._loading_error = None
        
        # 数据存储
        self.patterns = {}  # 证型数据
        self.symptoms = {}  # 症状数据
        self.symptom_pattern_mapping = {}  # 症状到证型的映射
        self.pattern_categories = {}  # 证型分类
        self.body_locations = {}  # 身体部位
        
        # 加载知识库
        self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> None:
        """加载中医知识库数据"""
        try:
            # 获取知识库路径
            base_path = Path(self.data_dir)
            
            # 检查目录是否存在
            if not base_path.exists():
                logger.warning(f"中医知识库目录不存在: {base_path}，尝试创建")
                os.makedirs(base_path, exist_ok=True)
            
            # 加载证型数据
            patterns_file = base_path / "patterns.yaml"
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    self.patterns = yaml.safe_load(f)
                logger.info(f"已加载 {len(self.patterns)} 个证型")
            else:
                logger.warning(f"证型文件不存在: {patterns_file}")
                # 创建初始数据文件
                self._create_sample_data_files(base_path)
                
            # 加载症状数据
            symptoms_file = base_path / "symptoms.yaml"
            if symptoms_file.exists():
                with open(symptoms_file, 'r', encoding='utf-8') as f:
                    self.symptoms = yaml.safe_load(f)
                logger.info(f"已加载 {len(self.symptoms)} 个症状")
            else:
                logger.warning(f"症状文件不存在: {symptoms_file}")
            
            # 加载症状-证型映射
            mapping_file = base_path / "symptom_pattern_mapping.yaml"
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self.symptom_pattern_mapping = yaml.safe_load(f)
                logger.info(f"已加载 {len(self.symptom_pattern_mapping)} 个症状-证型映射")
            else:
                logger.warning(f"症状-证型映射文件不存在: {mapping_file}")
            
            # 加载证型分类
            categories_file = base_path / "pattern_categories.yaml"
            if categories_file.exists():
                with open(categories_file, 'r', encoding='utf-8') as f:
                    self.pattern_categories = yaml.safe_load(f)
                logger.info(f"已加载 {len(self.pattern_categories)} 个证型分类")
            else:
                logger.warning(f"证型分类文件不存在: {categories_file}")
            
            # 加载身体部位
            body_locations_file = base_path / "body_locations.yaml"
            if body_locations_file.exists():
                with open(body_locations_file, 'r', encoding='utf-8') as f:
                    self.body_locations = yaml.safe_load(f)
                logger.info(f"已加载 {len(self.body_locations)} 个身体部位")
            else:
                logger.warning(f"身体部位文件不存在: {body_locations_file}")
            
            # 设置初始化标志
            self._initialized = True
            logger.info("中医知识库加载完成")
            
        except Exception as e:
            logger.error(f"加载中医知识库失败: {str(e)}", exc_info=True)
            self._loading_error = str(e)
            self._initialized = False
    
    def _create_sample_data_files(self, base_path: Path) -> None:
        """
        创建示例数据文件
        
        Args:
            base_path: 数据目录路径
        """
        logger.info("创建示例中医知识库数据文件")
        
        # 确保目录存在
        os.makedirs(base_path, exist_ok=True)
        
        # 创建示例证型数据
        sample_patterns = {
            "qi_deficiency": {
                "name": "气虚证",
                "category": "虚证",
                "description": "气虚证是指人体内气的不足所导致的一系列症状，常见表现为疲乏无力、气短懒言、面色苍白、自汗等。",
                "common_symptoms": ["疲乏无力", "气短懒言", "面色苍白", "自汗", "食欲不振", "大便溏薄", "舌淡胖", "脉弱"]
            },
            "yang_deficiency": {
                "name": "阳虚证",
                "category": "虚证",
                "description": "阳虚证是指人体阳气不足所导致的一系列症状，常见表现为畏寒肢冷、面色苍白、精神萎靡、小便清长等。",
                "common_symptoms": ["畏寒肢冷", "面色苍白", "精神萎靡", "小便清长", "腰膝酸软", "舌淡胖", "脉沉细"]
            },
            "yin_deficiency": {
                "name": "阴虚证",
                "category": "虚证",
                "description": "阴虚证是指人体阴液不足所导致的一系列症状，常见表现为口燥咽干、五心烦热、盗汗、舌红少苔等。",
                "common_symptoms": ["口燥咽干", "五心烦热", "盗汗", "颧红", "手足心热", "舌红少苔", "脉细数"]
            },
            "blood_stasis": {
                "name": "血瘀证",
                "category": "实证",
                "description": "血瘀证是指血液运行不畅、停滞所导致的一系列症状，常见表现为疼痛固定、舌质紫暗、瘀斑瘀点等。",
                "common_symptoms": ["疼痛固定", "刺痛", "皮肤紫暗", "唇甲紫暗", "舌质紫暗", "瘀斑瘀点", "脉涩"]
            },
            "phlegm_dampness": {
                "name": "痰湿证",
                "category": "实证",
                "description": "痰湿证是指体内水液代谢异常，聚湿成痰所导致的一系列症状，常见表现为胸闷、痰多、恶心、舌苔厚腻等。",
                "common_symptoms": ["胸闷", "痰多", "恶心", "头重", "肢体困重", "舌苔厚腻", "脉滑"]
            },
            "damp_heat": {
                "name": "湿热证",
                "category": "实证",
                "description": "湿热证是指湿邪与热邪同时侵犯人体所导致的一系列症状，常见表现为发热、口苦、小便短赤、舌红苔黄腻等。",
                "common_symptoms": ["发热", "口苦", "小便短赤", "苔黄腻", "脉濡数"]
            },
            "qi_stagnation": {
                "name": "气滞证",
                "category": "实证",
                "description": "气滞证是指气机郁滞不畅所导致的一系列症状，常见表现为胸胁胀痛、情绪波动、叹息、脉弦等。",
                "common_symptoms": ["胸胁胀痛", "情绪波动", "叹息", "嗳气", "脉弦"]
            },
            "liver_yang_hyperactivity": {
                "name": "肝阳上亢证",
                "category": "实证",
                "description": "肝阳上亢证是指肝阳上亢所导致的一系列症状，常见表现为头痛、头晕、面红、易怒、舌红脉弦等。",
                "common_symptoms": ["头痛", "头晕", "面红", "易怒", "耳鸣", "舌红", "脉弦"]
            },
            "spleen_deficiency": {
                "name": "脾虚证",
                "category": "虚证",
                "description": "脾虚证是指脾的功能减弱所导致的一系列症状，常见表现为食欲不振、腹胀、大便溏薄、倦怠乏力等。",
                "common_symptoms": ["食欲不振", "腹胀", "大便溏薄", "倦怠乏力", "面色萎黄", "舌淡胖", "脉缓弱"]
            },
            "lung_heat": {
                "name": "肺热证",
                "category": "实证",
                "description": "肺热证是指热邪侵犯肺部所导致的一系列症状，常见表现为发热、咳嗽、痰黄、鼻塞、咽痛等。",
                "common_symptoms": ["发热", "咳嗽", "痰黄", "鼻塞", "咽痛", "舌红", "脉浮数"]
            }
        }
        
        with open(base_path / "patterns.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(sample_patterns, f, allow_unicode=True, default_flow_style=False)
        
        # 创建示例症状数据
        sample_symptoms = {
            "fatigue": {
                "name": "疲乏无力",
                "description": "身体乏力，精神不振，容易疲劳",
                "body_locations": ["全身"],
                "common_patterns": ["气虚证", "脾虚证", "肾虚证"]
            },
            "shortness_of_breath": {
                "name": "气短懒言",
                "description": "说话无力，呼吸急促，不愿意多讲话",
                "body_locations": ["胸部", "肺"],
                "common_patterns": ["气虚证", "肺虚证"]
            },
            "pale_face": {
                "name": "面色苍白",
                "description": "面部颜色苍白，缺乏血色",
                "body_locations": ["面部"],
                "common_patterns": ["气虚证", "血虚证", "阳虚证"]
            },
            "spontaneous_sweating": {
                "name": "自汗",
                "description": "不因运动、热等外因而自行出汗",
                "body_locations": ["全身"],
                "common_patterns": ["气虚证", "阳虚证"]
            },
            "chills": {
                "name": "畏寒肢冷",
                "description": "怕冷，手脚发凉",
                "body_locations": ["四肢", "全身"],
                "common_patterns": ["阳虚证", "寒证"]
            },
            "listlessness": {
                "name": "精神萎靡",
                "description": "精神状态不佳，提不起精神",
                "body_locations": ["全身"],
                "common_patterns": ["气虚证", "阳虚证", "脾虚证"]
            },
            "clear_urination": {
                "name": "小便清长",
                "description": "尿量多，颜色清淡",
                "body_locations": ["泌尿系统"],
                "common_patterns": ["阳虚证", "肾虚证"]
            },
            "dry_mouth": {
                "name": "口燥咽干",
                "description": "口腔和咽喉干燥",
                "body_locations": ["口腔", "咽喉"],
                "common_patterns": ["阴虚证", "热证"]
            },
            "hot_sensation": {
                "name": "五心烦热",
                "description": "手心、足心、胸部感到烦热",
                "body_locations": ["手掌", "足底", "胸部"],
                "common_patterns": ["阴虚证", "心火旺"]
            },
            "night_sweats": {
                "name": "盗汗",
                "description": "睡眠中出汗，醒后汗止",
                "body_locations": ["全身"],
                "common_patterns": ["阴虚证", "血虚证"]
            },
            "fixed_pain": {
                "name": "疼痛固定",
                "description": "疼痛位置固定不移",
                "body_locations": ["全身"],
                "common_patterns": ["血瘀证"]
            },
            "chest_stuffiness": {
                "name": "胸闷",
                "description": "胸部闷胀不适",
                "body_locations": ["胸部"],
                "common_patterns": ["痰湿证", "气滞证"]
            },
            "phlegm": {
                "name": "痰多",
                "description": "痰液分泌过多",
                "body_locations": ["肺", "咽喉"],
                "common_patterns": ["痰湿证", "肺热证"]
            },
            "nausea": {
                "name": "恶心",
                "description": "胃部不适，欲吐不吐",
                "body_locations": ["胃部"],
                "common_patterns": ["痰湿证", "脾胃不和"]
            },
            "fever": {
                "name": "发热",
                "description": "体温升高",
                "body_locations": ["全身"],
                "common_patterns": ["湿热证", "肺热证", "热证"]
            },
            "bitter_taste": {
                "name": "口苦",
                "description": "口中有苦味",
                "body_locations": ["口腔"],
                "common_patterns": ["湿热证", "肝胆湿热"]
            },
            "chest_pain": {
                "name": "胸胁胀痛",
                "description": "胸部和侧腹部胀痛",
                "body_locations": ["胸部", "侧腹部"],
                "common_patterns": ["气滞证", "肝气郁结"]
            },
            "mood_swings": {
                "name": "情绪波动",
                "description": "情绪不稳定，易喜易怒",
                "body_locations": ["心"],
                "common_patterns": ["气滞证", "肝气郁结"]
            },
            "headache": {
                "name": "头痛",
                "description": "头部疼痛",
                "body_locations": ["头部"],
                "common_patterns": ["肝阳上亢证", "风寒证", "风热证"]
            },
            "dizziness": {
                "name": "头晕",
                "description": "头晕目眩",
                "body_locations": ["头部"],
                "common_patterns": ["肝阳上亢证", "气虚证", "血虚证"]
            },
            "irritability": {
                "name": "易怒",
                "description": "容易发怒",
                "body_locations": ["肝"],
                "common_patterns": ["肝阳上亢证", "肝火旺"]
            },
            "poor_appetite": {
                "name": "食欲不振",
                "description": "胃口不好，不想吃东西",
                "body_locations": ["胃部"],
                "common_patterns": ["脾虚证", "气虚证"]
            },
            "abdominal_distension": {
                "name": "腹胀",
                "description": "腹部胀满不适",
                "body_locations": ["腹部"],
                "common_patterns": ["脾虚证", "气滞证"]
            },
            "loose_stool": {
                "name": "大便溏薄",
                "description": "大便稀溏不成形",
                "body_locations": ["肠道"],
                "common_patterns": ["脾虚证", "湿证"]
            },
            "cough": {
                "name": "咳嗽",
                "description": "咳嗽",
                "body_locations": ["肺", "咽喉"],
                "common_patterns": ["肺热证", "风寒咳嗽", "风热咳嗽"]
            },
            "yellow_phlegm": {
                "name": "痰黄",
                "description": "痰液呈黄色",
                "body_locations": ["肺", "咽喉"],
                "common_patterns": ["肺热证", "湿热证"]
            },
            "sore_throat": {
                "name": "咽痛",
                "description": "咽喉疼痛",
                "body_locations": ["咽喉"],
                "common_patterns": ["肺热证", "风热证"]
            }
        }
        
        with open(base_path / "symptoms.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(sample_symptoms, f, allow_unicode=True, default_flow_style=False)
        
        # 创建示例症状-证型映射
        sample_mapping = {
            "疲乏无力": ["气虚证", "脾虚证", "肾虚证"],
            "气短懒言": ["气虚证", "肺虚证"],
            "面色苍白": ["气虚证", "血虚证", "阳虚证"],
            "自汗": ["气虚证", "阳虚证"],
            "畏寒肢冷": ["阳虚证", "寒证"],
            "精神萎靡": ["气虚证", "阳虚证", "脾虚证"],
            "小便清长": ["阳虚证", "肾虚证"],
            "口燥咽干": ["阴虚证", "热证"],
            "五心烦热": ["阴虚证", "心火旺"],
            "盗汗": ["阴虚证", "血虚证"],
            "疼痛固定": ["血瘀证"],
            "胸闷": ["痰湿证", "气滞证"],
            "痰多": ["痰湿证", "肺热证"],
            "恶心": ["痰湿证", "脾胃不和"],
            "发热": ["湿热证", "肺热证", "热证"],
            "口苦": ["湿热证", "肝胆湿热"],
            "胸胁胀痛": ["气滞证", "肝气郁结"],
            "情绪波动": ["气滞证", "肝气郁结"],
            "头痛": ["肝阳上亢证", "风寒证", "风热证"],
            "头晕": ["肝阳上亢证", "气虚证", "血虚证"],
            "易怒": ["肝阳上亢证", "肝火旺"],
            "食欲不振": ["脾虚证", "气虚证"],
            "腹胀": ["脾虚证", "气滞证"],
            "大便溏薄": ["脾虚证", "湿证"],
            "咳嗽": ["肺热证", "风寒咳嗽", "风热咳嗽"],
            "痰黄": ["肺热证", "湿热证"],
            "咽痛": ["肺热证", "风热证"]
        }
        
        with open(base_path / "symptom_pattern_mapping.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(sample_mapping, f, allow_unicode=True, default_flow_style=False)
        
        # 创建示例证型分类
        sample_categories = {
            "虚实": ["虚证", "实证"],
            "寒热": ["寒证", "热证"],
            "气血津液": ["气虚证", "气滞证", "血虚证", "血瘀证", "津液不足", "痰湿证"],
            "脏腑": ["肝证", "心证", "脾证", "肺证", "肾证"]
        }
        
        with open(base_path / "pattern_categories.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(sample_categories, f, allow_unicode=True, default_flow_style=False)
        
        # 创建示例身体部位
        sample_body_locations = {
            "头部": {
                "associated_organs": ["脑", "肝"],
                "common_symptoms": ["头痛", "头晕", "头重"]
            },
            "面部": {
                "associated_organs": ["脾", "肺"],
                "common_symptoms": ["面色苍白", "面红", "面浮肿"]
            },
            "眼部": {
                "associated_organs": ["肝"],
                "common_symptoms": ["目赤", "视物模糊", "干涩"]
            },
            "口腔": {
                "associated_organs": ["脾", "胃"],
                "common_symptoms": ["口燥", "口苦", "口臭"]
            },
            "咽喉": {
                "associated_organs": ["肺"],
                "common_symptoms": ["咽干", "咽痛", "咳嗽"]
            },
            "胸部": {
                "associated_organs": ["心", "肺"],
                "common_symptoms": ["胸闷", "胸痛", "心悸"]
            },
            "腹部": {
                "associated_organs": ["脾", "胃", "肝", "肾"],
                "common_symptoms": ["腹痛", "腹胀", "腹泻"]
            },
            "腰部": {
                "associated_organs": ["肾"],
                "common_symptoms": ["腰酸", "腰痛", "腰膝酸软"]
            },
            "四肢": {
                "associated_organs": ["肝", "脾"],
                "common_symptoms": ["肢体酸痛", "肢体麻木", "肢体沉重"]
            }
        }
        
        with open(base_path / "body_locations.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(sample_body_locations, f, allow_unicode=True, default_flow_style=False)
        
        logger.info("已创建示例中医知识库数据文件")
    
    def get_pattern_by_name(self, pattern_name: str) -> Optional[Dict]:
        """
        根据证型名称获取证型信息
        
        Args:
            pattern_name: 证型名称
            
        Returns:
            证型信息字典
        """
        if not self._initialized:
            logger.warning("中医知识库未初始化")
            return None
            
        # 直接匹配
        for pattern_id, pattern_info in self.patterns.items():
            if pattern_info["name"] == pattern_name:
                result = pattern_info.copy()
                result["id"] = pattern_id
                return result
                
        # 模糊匹配
        for pattern_id, pattern_info in self.patterns.items():
            if pattern_name in pattern_info["name"]:
                result = pattern_info.copy()
                result["id"] = pattern_id
                return result
                
        logger.debug(f"未找到证型: {pattern_name}")
        return None
    
    def get_symptom_by_name(self, symptom_name: str) -> Optional[Dict]:
        """
        根据症状名称获取症状信息
        
        Args:
            symptom_name: 症状名称
            
        Returns:
            症状信息字典
        """
        if not self._initialized:
            logger.warning("中医知识库未初始化")
            return None
            
        # 直接匹配
        for symptom_id, symptom_info in self.symptoms.items():
            if symptom_info["name"] == symptom_name:
                result = symptom_info.copy()
                result["id"] = symptom_id
                return result
                
        # 模糊匹配
        for symptom_id, symptom_info in self.symptoms.items():
            if symptom_name in symptom_info["name"]:
                result = symptom_info.copy()
                result["id"] = symptom_id
                return result
                
        logger.debug(f"未找到症状: {symptom_name}")
        return None
    
    def get_related_patterns(self, symptom_name: str) -> List[Dict]:
        """
        根据症状获取相关证型
        
        Args:
            symptom_name: 症状名称
            
        Returns:
            相关证型列表
        """
        if not self._initialized:
            logger.warning("中医知识库未初始化")
            return []
            
        related_patterns = []
        
        # 从映射中查找
        if symptom_name in self.symptom_pattern_mapping:
            pattern_names = self.symptom_pattern_mapping[symptom_name]
            for pattern_name in pattern_names:
                pattern = self.get_pattern_by_name(pattern_name)
                if pattern:
                    related_patterns.append(pattern)
        else:
            # 在症状信息中查找
            symptom = self.get_symptom_by_name(symptom_name)
            if symptom and "common_patterns" in symptom:
                for pattern_name in symptom["common_patterns"]:
                    pattern = self.get_pattern_by_name(pattern_name)
                    if pattern:
                        related_patterns.append(pattern)
        
        return related_patterns
    
    def get_patterns_by_category(self, category: str) -> List[Dict]:
        """
        根据分类获取证型
        
        Args:
            category: 证型分类
            
        Returns:
            证型列表
        """
        if not self._initialized:
            logger.warning("中医知识库未初始化")
            return []
            
        result = []
        
        for pattern_id, pattern_info in self.patterns.items():
            if pattern_info.get("category") == category:
                pattern_copy = pattern_info.copy()
                pattern_copy["id"] = pattern_id
                result.append(pattern_copy)
                
        return result
    
    def get_body_location(self, location_name: str) -> Optional[Dict]:
        """
        获取身体部位信息
        
        Args:
            location_name: 部位名称
            
        Returns:
            部位信息字典
        """
        if not self._initialized:
            logger.warning("中医知识库未初始化")
            return None
            
        # 直接匹配
        if location_name in self.body_locations:
            result = self.body_locations[location_name].copy()
            result["name"] = location_name
            return result
            
        # 模糊匹配
        for loc_name, loc_info in self.body_locations.items():
            if location_name in loc_name or loc_name in location_name:
                result = loc_info.copy()
                result["name"] = loc_name
                return result
                
        logger.debug(f"未找到身体部位: {location_name}")
        return None
    
    def get_symptoms_by_body_location(self, location_name: str) -> List[Dict]:
        """
        根据身体部位获取相关症状
        
        Args:
            location_name: 部位名称
            
        Returns:
            症状列表
        """
        if not self._initialized:
            logger.warning("中医知识库未初始化")
            return []
            
        result = []
        location = self.get_body_location(location_name)
        
        if location and "common_symptoms" in location:
            for symptom_name in location["common_symptoms"]:
                symptom = self.get_symptom_by_name(symptom_name)
                if symptom:
                    result.append(symptom)
        else:
            # 在所有症状中查找与该部位相关的
            for symptom_id, symptom_info in self.symptoms.items():
                if "body_locations" in symptom_info and location_name in symptom_info["body_locations"]:
                    symptom_copy = symptom_info.copy()
                    symptom_copy["id"] = symptom_id
                    result.append(symptom_copy)
        
        return result
    
    def get_status(self) -> Dict:
        """
        获取知识库状态
        
        Returns:
            状态信息字典
        """
        return {
            "initialized": self._initialized,
            "loading_error": self._loading_error,
            "patterns_count": len(self.patterns),
            "symptoms_count": len(self.symptoms),
            "mappings_count": len(self.symptom_pattern_mapping),
            "categories_count": len(self.pattern_categories),
            "body_locations_count": len(self.body_locations)
        } 