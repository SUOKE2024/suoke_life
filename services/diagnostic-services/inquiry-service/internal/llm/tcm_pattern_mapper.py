#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TCM证型映射器模块，根据症状映射到中医证型
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class TCMPatternMapper:
    """TCM证型映射器类，负责将症状映射到中医证型"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化TCM证型映射器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.tcm_config = config.get('tcm_knowledge', {})
        
        # 配置
        self.patterns_db_path = self.tcm_config.get('patterns_db_path', '')
        self.constitution_types_path = self.tcm_config.get('constitution_types_path', '')
        self.enable_traditional_terms = self.tcm_config.get('enable_traditional_terms', True)
        self.enable_simplified_terms = self.tcm_config.get('enable_simplified_terms', True)
        self.confidence_threshold = self.tcm_config.get('confidence_threshold', 0.7)
        
        # 加载证型数据库
        self.patterns_db = self._load_patterns_db()
        
        # 加载体质类型数据
        self.constitution_types = self._load_constitution_types()
        
        logger.info("TCM证型映射器初始化完成")

    def _load_patterns_db(self) -> Dict:
        """加载证型数据库"""
        try:
            if self.patterns_db_path and os.path.exists(self.patterns_db_path):
                with open(self.patterns_db_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                logger.warning("证型数据库文件不存在，将使用内置的基本证型数据")
                return self._get_default_patterns_db()
        except Exception as e:
            logger.error(f"加载证型数据库失败: {str(e)}")
            return self._get_default_patterns_db()
            
    def _get_default_patterns_db(self) -> Dict:
        """获取默认的证型数据库"""
        # 简要版本的中医证型数据库，实际应用中应该更完整
        return {
            "patterns": [
                {
                    "name": "气虚证",
                    "category": "虚证",
                    "description": "气虚证是指人体内气的不足所导致的一系列症状",
                    "core_symptoms": ["疲劳", "乏力", "气短", "少气懒言", "自汗"],
                    "common_symptoms": ["声低", "气短", "动则汗出", "倦怠", "食欲不振"],
                    "tongue": ["舌淡", "舌胖", "齿痕", "舌苔薄白"],
                    "pulse": ["脉弱", "脉缓"]
                },
                {
                    "name": "血虚证",
                    "category": "虚证",
                    "description": "血虚证是指人体血液亏损不足所导致的一系列症状",
                    "core_symptoms": ["面色苍白", "唇甲色淡", "头晕", "眼花"],
                    "common_symptoms": ["失眠", "心悸", "月经量少", "肌肤干燥", "头发干枯", "指甲脆"],
                    "tongue": ["舌淡", "舌瘦", "少津", "舌苔少"],
                    "pulse": ["脉细", "脉弱"]
                },
                {
                    "name": "阴虚证",
                    "category": "虚证",
                    "description": "阴虚证是指人体阴液亏损所导致的一系列症状",
                    "core_symptoms": ["口干", "咽干", "五心烦热", "潮热", "盗汗"],
                    "common_symptoms": ["失眠", "颧红", "手足心热", "形体消瘦", "大便干燥"],
                    "tongue": ["舌红", "少津", "少苔", "舌苔薄或无苔"],
                    "pulse": ["脉细数", "脉弦细"]
                },
                {
                    "name": "阳虚证",
                    "category": "虚证",
                    "description": "阳虚证是指人体阳气不足所导致的一系列症状",
                    "core_symptoms": ["怕冷", "手脚冰凉", "面色苍白", "喜温"],
                    "common_symptoms": ["腰膝酸软", "神疲", "小便清长", "大便溏薄", "腹部冷痛"],
                    "tongue": ["舌淡胖", "舌体胖嫩", "舌苔白滑"],
                    "pulse": ["脉沉", "脉迟", "脉弱"]
                },
                {
                    "name": "痰湿证",
                    "category": "实证",
                    "description": "痰湿证是指体内水液代谢异常，聚湿成痰所导致的一系列症状",
                    "core_symptoms": ["痰多", "胸闷", "恶心", "呕吐", "腹胀"],
                    "common_symptoms": ["苔腻", "头重", "肢体沉重", "纳呆", "口黏"],
                    "tongue": ["舌体胖", "舌苔白腻", "舌苔厚腻"],
                    "pulse": ["脉滑", "脉濡", "脉弦滑"]
                },
                {
                    "name": "湿热证",
                    "category": "实证",
                    "description": "湿热证是指湿与热两种邪气互结所导致的一系列症状",
                    "core_symptoms": ["口苦", "口臭", "小便黄", "大便粘滞不爽"],
                    "common_symptoms": ["苔黄腻", "身重", "胸闷", "纳差", "头昏"],
                    "tongue": ["舌红", "舌苔黄腻"],
                    "pulse": ["脉滑数", "脉濡数"]
                },
                {
                    "name": "气滞证",
                    "category": "实证",
                    "description": "气滞证是指气机郁滞不畅所导致的一系列症状",
                    "core_symptoms": ["胸胁胀痛", "情志不畅", "嗳气", "打嗝"],
                    "common_symptoms": ["痛处不固定", "善太息", "脘腹胀满", "矢气多"],
                    "tongue": ["舌正常或淡红", "舌苔薄白"],
                    "pulse": ["脉弦", "脉结"]
                },
                {
                    "name": "血瘀证",
                    "category": "实证",
                    "description": "血瘀证是指血液运行不畅，瘀滞于体内所导致的一系列症状",
                    "core_symptoms": ["疼痛固定", "刺痛", "肌肤甲错"],
                    "common_symptoms": ["舌质紫暗", "口唇紫暗", "瘀斑", "瘀血", "肿块固定"],
                    "tongue": ["舌紫暗", "瘀斑", "瘀点", "舌下络脉怒张"],
                    "pulse": ["脉涩", "脉弦"]
                }
            ],
            "pattern_combinations": [
                {
                    "name": "气血两虚",
                    "patterns": ["气虚证", "血虚证"],
                    "description": "气血双重亏虚的证候",
                    "common_pattern": True
                },
                {
                    "name": "肝郁脾虚",
                    "patterns": ["气滞证", "气虚证"],
                    "description": "肝气郁结与脾气虚弱并存的证候",
                    "common_pattern": True
                },
                {
                    "name": "痰湿困脾",
                    "patterns": ["痰湿证", "气虚证"],
                    "description": "痰湿内蕴，脾气虚弱的证候",
                    "common_pattern": True
                },
                {
                    "name": "气阴两虚",
                    "patterns": ["气虚证", "阴虚证"],
                    "description": "气虚与阴虚同时存在的证候",
                    "common_pattern": True
                }
            ],
            "pattern_categories": {
                "虚实": ["虚证", "实证"],
                "寒热": ["寒证", "热证", "温证", "凉证"],
                "表里": ["表证", "里证", "半表半里"],
                "阴阳": ["阳证", "阴证", "阴阳两虚"]
            }
        }
        
    def _load_constitution_types(self) -> Dict:
        """加载体质类型数据"""
        try:
            if self.constitution_types_path and os.path.exists(self.constitution_types_path):
                with open(self.constitution_types_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                logger.warning("体质类型数据文件不存在，将使用内置的基本体质数据")
                return self._get_default_constitution_types()
        except Exception as e:
            logger.error(f"加载体质类型数据失败: {str(e)}")
            return self._get_default_constitution_types()
            
    def _get_default_constitution_types(self) -> Dict:
        """获取默认的体质类型数据"""
        # 简要版本的中医体质数据，实际应用中应该更完整
        return {
            "constitution_types": [
                {
                    "name": "平和质",
                    "code": "BALANCED",
                    "description": "平和体质是相对于偏颇体质而言的一种正常体质。",
                    "characteristics": [
                        "面色润泽",
                        "精力充沛",
                        "睡眠良好",
                        "适应能力强",
                        "体形适中"
                    ],
                    "common_patterns": []
                },
                {
                    "name": "气虚质",
                    "code": "QI_DEFICIENCY",
                    "description": "气虚体质是以元气不足为主的体质。",
                    "characteristics": [
                        "疲乏无力",
                        "言语低弱",
                        "气短自汗",
                        "易感冒",
                        "舌淡苔薄"
                    ],
                    "common_patterns": ["气虚证"]
                },
                {
                    "name": "阳虚质",
                    "code": "YANG_DEFICIENCY",
                    "description": "阳虚体质是以阳气亏虚，形寒为主的体质。",
                    "characteristics": [
                        "畏寒肢冷",
                        "面色苍白",
                        "喜温喜按",
                        "舌淡胖嫩",
                        "脉沉迟"
                    ],
                    "common_patterns": ["阳虚证"]
                },
                {
                    "name": "阴虚质",
                    "code": "YIN_DEFICIENCY",
                    "description": "阴虚体质是以阴液亏少，形热为主的体质。",
                    "characteristics": [
                        "手足心热",
                        "口干咽燥",
                        "五心烦热",
                        "舌红少苔",
                        "脉细数"
                    ],
                    "common_patterns": ["阴虚证"]
                },
                {
                    "name": "痰湿质",
                    "code": "PHLEGM_DAMPNESS",
                    "description": "痰湿体质是以体内水湿停聚，痰浊内生为主的体质。",
                    "characteristics": [
                        "形体肥胖",
                        "腹部松软",
                        "痰多黏稠",
                        "舌苔厚腻",
                        "脉滑"
                    ],
                    "common_patterns": ["痰湿证"]
                },
                {
                    "name": "湿热质",
                    "code": "DAMP_HEAT",
                    "description": "湿热体质是以体内湿热内蕴为主的体质。",
                    "characteristics": [
                        "面垢油光",
                        "口苦口臭",
                        "大便粘滞",
                        "舌红苔黄腻",
                        "脉弦数"
                    ],
                    "common_patterns": ["湿热证"]
                },
                {
                    "name": "血瘀质",
                    "code": "BLOOD_STASIS",
                    "description": "血瘀体质是以体内血行不畅，血液瘀滞为主的体质。",
                    "characteristics": [
                        "肤色晦暗",
                        "唇色紫暗",
                        "舌质紫黯",
                        "瘀斑瘀点",
                        "脉涩"
                    ],
                    "common_patterns": ["血瘀证"]
                },
                {
                    "name": "气郁质",
                    "code": "QI_STAGNATION",
                    "description": "气郁体质是以气机郁滞为主的体质。",
                    "characteristics": [
                        "情志抑郁",
                        "胸胁胀痛",
                        "善太息",
                        "舌淡红",
                        "脉弦"
                    ],
                    "common_patterns": ["气滞证"]
                },
                {
                    "name": "特禀质",
                    "code": "SPECIAL_CONSTITUTION",
                    "description": "特禀体质是一种先天禀赋特殊的体质。",
                    "characteristics": [
                        "过敏体质",
                        "免疫力低下",
                        "遗传倾向明显",
                        "特殊反应性"
                    ],
                    "common_patterns": []
                }
            ],
            "constitution_pattern_relations": {
                "QI_DEFICIENCY": ["气虚证", "气血两虚", "气阴两虚"],
                "YANG_DEFICIENCY": ["阳虚证", "阴阳两虚"],
                "YIN_DEFICIENCY": ["阴虚证", "气阴两虚", "阴阳两虚"],
                "PHLEGM_DAMPNESS": ["痰湿证", "痰湿困脾"],
                "DAMP_HEAT": ["湿热证"],
                "BLOOD_STASIS": ["血瘀证"],
                "QI_STAGNATION": ["气滞证", "肝郁脾虚"]
            }
        }

    async def map_to_tcm_patterns(
        self, 
        symptoms: List[Dict], 
        user_constitution: str = None,
        body_locations: List[Dict] = None,
        temporal_factors: List[Dict] = None
    ) -> Dict:
        """
        将症状映射到中医证型
        
        Args:
            symptoms: 症状列表
            user_constitution: 用户体质类型
            body_locations: 身体部位列表
            temporal_factors: 时间因素列表
            
        Returns:
            Dict: 包含主证、次证、解释和置信度
        """
        try:
            # 提取症状名称
            symptom_names = [s['symptom_name'] for s in symptoms]
            
            # 获取所有可能的证型
            all_patterns = self.patterns_db.get('patterns', [])
            
            # 计算每个证型的匹配得分
            pattern_scores = []
            for pattern in all_patterns:
                score = self._calculate_pattern_match(pattern, symptom_names, body_locations, temporal_factors)
                
                if score > 0:
                    pattern_scores.append({
                        'pattern_name': pattern['name'],
                        'category': pattern['category'],
                        'match_score': score,
                        'related_symptoms': self._get_related_symptoms(pattern, symptom_names),
                        'description': pattern['description']
                    })
                    
            # 根据匹配得分排序
            pattern_scores.sort(key=lambda x: x['match_score'], reverse=True)
            
            # 区分主证和次证
            primary_patterns = []
            secondary_patterns = []
            
            # 如果有匹配的证型
            if pattern_scores:
                # 获取最高得分
                max_score = pattern_scores[0]['match_score']
                
                # 主证：得分高于阈值的证型
                primary_threshold = max(self.confidence_threshold, max_score * 0.8)
                
                for pattern in pattern_scores:
                    if pattern['match_score'] >= primary_threshold:
                        primary_patterns.append(pattern)
                    elif pattern['match_score'] >= self.confidence_threshold * 0.7:
                        secondary_patterns.append(pattern)
                        
            # 检查证型组合
            combination_patterns = self._check_pattern_combinations(primary_patterns, secondary_patterns)
            if combination_patterns:
                # 添加组合证型到主证中
                primary_patterns.extend(combination_patterns)
                
            # 如果没有找到匹配的证型，但有用户体质信息
            if not primary_patterns and user_constitution:
                # 根据体质推断可能的证型
                constitution_patterns = self._get_patterns_from_constitution(user_constitution)
                if constitution_patterns:
                    # 将体质相关的证型添加为次证
                    for pattern in constitution_patterns:
                        pattern_found = False
                        for p in secondary_patterns:
                            if p['pattern_name'] == pattern['name']:
                                pattern_found = True
                                break
                                
                        if not pattern_found:
                            secondary_patterns.append({
                                'pattern_name': pattern['name'],
                                'category': pattern['category'],
                                'match_score': 0.65,  # 基于体质的默认得分
                                'related_symptoms': [],
                                'description': pattern['description']
                            })
                            
            # 生成结果解释
            interpretation = self._generate_interpretation(primary_patterns, secondary_patterns, symptoms)
            
            # 计算总体置信度
            if primary_patterns:
                confidence_score = sum([p['match_score'] for p in primary_patterns]) / len(primary_patterns)
            elif secondary_patterns:
                confidence_score = 0.6  # 只有次证的默认置信度
            else:
                confidence_score = 0.0
                
            # 构建响应
            result = {
                'primary_patterns': primary_patterns,
                'secondary_patterns': secondary_patterns,
                'interpretation': interpretation,
                'confidence_score': confidence_score
            }
            
            logger.info(f"映射到 {len(primary_patterns)} 个主证和 {len(secondary_patterns)} 个次证")
            
            return result
            
        except Exception as e:
            logger.error(f"映射中医证型失败: {str(e)}")
            return {
                'primary_patterns': [],
                'secondary_patterns': [],
                'interpretation': "无法确定证型",
                'confidence_score': 0.0
            }
            
    def _calculate_pattern_match(
        self, 
        pattern: Dict, 
        symptom_names: List[str],
        body_locations: List[Dict] = None,
        temporal_factors: List[Dict] = None
    ) -> float:
        """计算证型的匹配得分"""
        # 获取关键症状和常见症状
        core_symptoms = pattern.get('core_symptoms', [])
        common_symptoms = pattern.get('common_symptoms', [])
        
        # 计算匹配的关键症状数量
        matched_core = sum(1 for s in core_symptoms if s in symptom_names)
        
        # 计算匹配的常见症状数量
        matched_common = sum(1 for s in common_symptoms if s in symptom_names)
        
        # 只有满足一定数量的关键症状才考虑此证型
        if matched_core < 1:
            return 0.0
            
        # 计算得分：关键症状占更大权重
        total_core = len(core_symptoms)
        total_common = len(common_symptoms)
        
        core_weight = 0.7
        common_weight = 0.3
        
        if total_core > 0:
            core_score = matched_core / total_core * core_weight
        else:
            core_score = 0
            
        if total_common > 0:
            common_score = matched_common / total_common * common_weight
        else:
            common_score = 0
            
        base_score = core_score + common_score
        
        # 考虑舌象和脉象（如果有）
        tongue_symptoms = pattern.get('tongue', [])
        pulse_symptoms = pattern.get('pulse', [])
        
        # 在症状中查找舌脉特征
        has_tongue_match = any(tongue for tongue in tongue_symptoms if any(tongue in s for s in symptom_names))
        has_pulse_match = any(pulse for pulse in pulse_symptoms if any(pulse in s for s in symptom_names))
        
        # 舌脉象匹配加分
        if has_tongue_match:
            base_score += 0.1
        if has_pulse_match:
            base_score += 0.1
            
        # 根据时间因素调整得分
        if temporal_factors:
            # 某些证型与特定时间因素相关
            pattern_time_relations = {
                "阴虚证": ["夜间", "晚上", "潮热", "盗汗"],
                "阳虚证": ["早上", "凌晨", "怕冷"],
                "痰湿证": ["雨季", "梅雨", "湿度大"],
                "湿热证": ["夏季", "湿热"]
            }
            
            if pattern['name'] in pattern_time_relations:
                related_times = pattern_time_relations[pattern['name']]
                for factor in temporal_factors:
                    desc = factor.get('description', '').lower()
                    if any(time in desc for time in related_times):
                        base_score += 0.05
                        break
                        
        # 根据身体部位调整得分
        if body_locations:
            # 某些证型与特定身体部位相关
            pattern_location_relations = {
                "肝胆湿热": ["胁", "肋", "眼"],
                "胃热": ["胃", "腹", "口"],
                "肺热": ["肺", "胸", "喉"],
                "心火": ["心", "胸", "舌"]
            }
            
            if pattern['name'] in pattern_location_relations:
                related_locations = pattern_location_relations[pattern['name']]
                for location in body_locations:
                    loc_name = location.get('location_name', '').lower()
                    if any(loc in loc_name for loc in related_locations):
                        base_score += 0.05
                        break
                        
        # 限制最高分为1.0
        return min(1.0, base_score)
        
    def _get_related_symptoms(self, pattern: Dict, symptom_names: List[str]) -> List[str]:
        """获取与证型相关的症状"""
        core_symptoms = pattern.get('core_symptoms', [])
        common_symptoms = pattern.get('common_symptoms', [])
        
        # 找出用户实际有的与该证型相关的症状
        related = []
        for symptom in symptom_names:
            if symptom in core_symptoms or symptom in common_symptoms:
                related.append(symptom)
                
        return related
        
    def _check_pattern_combinations(self, primary_patterns: List[Dict], secondary_patterns: List[Dict]) -> List[Dict]:
        """检查证型组合"""
        combinations = self.patterns_db.get('pattern_combinations', [])
        matched_combinations = []
        
        # 合并主证和次证
        all_patterns = primary_patterns + secondary_patterns
        pattern_names = [p['pattern_name'] for p in all_patterns]
        
        for combo in combinations:
            combo_patterns = combo.get('patterns', [])
            # 如果组合中的所有证型都存在
            if all(p in pattern_names for p in combo_patterns):
                # 计算组合得分（取平均）
                combo_score = 0
                pattern_count = 0
                for p in all_patterns:
                    if p['pattern_name'] in combo_patterns:
                        combo_score += p['match_score']
                        pattern_count += 1
                        
                if pattern_count > 0:
                    avg_score = combo_score / pattern_count
                    
                    matched_combinations.append({
                        'pattern_name': combo['name'],
                        'category': '复合证型',
                        'match_score': avg_score,
                        'related_symptoms': [],  # 组合证型没有直接关联的症状
                        'description': combo['description']
                    })
                    
        return matched_combinations
        
    def _get_patterns_from_constitution(self, constitution_type: str) -> List[Dict]:
        """根据体质类型获取相关的证型"""
        constitution_pattern_relations = self.constitution_types.get('constitution_pattern_relations', {})
        
        # 获取与该体质类型相关的证型名称
        related_pattern_names = constitution_pattern_relations.get(constitution_type, [])
        
        # 从证型数据库中查找这些证型
        related_patterns = []
        all_patterns = self.patterns_db.get('patterns', [])
        
        for pattern in all_patterns:
            if pattern['name'] in related_pattern_names:
                related_patterns.append(pattern)
                
        return related_patterns
        
    def _generate_interpretation(
        self, 
        primary_patterns: List[Dict], 
        secondary_patterns: List[Dict],
        symptoms: List[Dict]
    ) -> str:
        """生成证型解释"""
        if not primary_patterns and not secondary_patterns:
            return "根据提供的症状信息，暂时无法确定明确的中医证型。建议咨询专业中医师进行详细辨证。"
            
        interpretation = ""
        
        # 主证解释
        if primary_patterns:
            interpretation += "根据您的症状，主要表现为"
            
            for i, pattern in enumerate(primary_patterns):
                if i > 0:
                    interpretation += "、" if i < len(primary_patterns) - 1 else "和"
                interpretation += f"{pattern['pattern_name']}"
                
            interpretation += "。"
            
            # 添加主要证型的描述
            main_pattern = primary_patterns[0]
            interpretation += f"{main_pattern['pattern_name']}是指{main_pattern['description']}。"
            
            # 关联症状
            if main_pattern['related_symptoms']:
                interpretation += f"您表现的相关症状包括{', '.join(main_pattern['related_symptoms'])}。"
                
        # 次证解释
        if secondary_patterns:
            interpretation += "同时可能兼有"
            
            for i, pattern in enumerate(secondary_patterns):
                if i > 0:
                    interpretation += "、" if i < len(secondary_patterns) - 1 else "和"
                interpretation += f"{pattern['pattern_name']}"
                
            interpretation += "的表现。"
            
        # 添加一些通用建议
        interpretation += "建议根据辨证结果，采取相应的调理方案。"
        
        return interpretation 