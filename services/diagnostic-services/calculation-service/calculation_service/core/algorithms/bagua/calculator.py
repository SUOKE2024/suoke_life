"""
calculator - 索克生活项目模块
"""

from .data import (
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

"""
八卦配属计算器

实现八卦与人体脏腑对应的分析功能
"""


    BAGUA_DATA,
    BAGUA_ORGAN_MAP,
    JIUGONG_BAGUA_MAP,
    BAGUA_RELATIONS,
    BAGUA_DISEASE_PREDICTION,
    BAGUA_HEALTH_METHODS,
    BAGUA_TIME_MAP
)

class BaguaCalculator:
    """八卦配属计算器"""
    
    def __init__(self):
        """初始化计算器"""
        self.bagua_order = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
        self.directions = {
            "北": 0, "东北": 45, "东": 90, "东南": 135,
            "南": 180, "西南": 225, "西": 270, "西北": 315
        }
        
        # 八卦对应角度
        self.bagua_angles = {
            "坎": 0,    # 北
            "艮": 45,   # 东北
            "震": 90,   # 东
            "巽": 135,  # 东南
            "离": 180,  # 南
            "坤": 225,  # 西南
            "兑": 270,  # 西
            "乾": 315   # 西北
        }
    
    def get_birth_bagua(self, birth_datetime: datetime) -> str:
        """
        根据出生时间确定本命卦
        
        Args:
            birth_datetime: 出生时间
            
        Returns:
            本命卦
        """
        year = birth_datetime.year
        month = birth_datetime.month
        day = birth_datetime.day
        hour = birth_datetime.hour
        
        # 根据年份计算本命卦（简化算法）
        # 男性：(100 - 出生年份后两位) / 9 的余数
        # 女性：(出生年份后两位 - 4) / 9 的余数
        
        year_last_two = year % 100
        
        # 这里假设为男性，实际应用中需要传入性别参数
        remainder = (100 - year_last_two) % 9
        if remainder == 0:
            remainder = 9
        
        # 根据余数确定卦
        bagua_map = {
            1: "坎", 2: "坤", 3: "震", 4: "巽",
            5: "坤", 6: "乾", 7: "兑", 8: "艮", 9: "离"
        }
        
        return bagua_map.get(remainder, "坎")
    
    def get_current_bagua(self, current_datetime: datetime) -> str:
        """
        根据当前时间确定当前卦
        
        Args:
            current_datetime: 当前时间
            
        Returns:
            当前卦
        """
        month = current_datetime.month
        hour = current_datetime.hour
        
        # 根据月份确定卦
        for bagua, time_info in BAGUA_TIME_MAP.items():
            if month in time_info["月份"]:
                return bagua
        
        return "坎"  # 默认值
    
    def analyze_personal_bagua(self, birth_info: Dict) -> Dict:
        """
        个人八卦分析（兼容测试）
        
        Args:
            birth_info: 出生信息
            
        Returns:
            个人八卦分析结果
        """
        birth_dt = datetime(
            year=birth_info["year"],
            month=birth_info["month"],
            day=birth_info["day"],
            hour=birth_info.get("hour", 12)
        )
        
        # 获取本命卦
        benming_gua = self.calculate_benming_gua(birth_info)
        
        # 获取八卦信息
        bagua_info = BAGUA_DATA.get(benming_gua, {})
        organ_info = BAGUA_ORGAN_MAP.get(benming_gua, {})
        
        # 健康分析
        health_analysis = self._analyze_personal_health(benming_gua, birth_info.get("gender", "男"))
        
        # 调理建议
        treatment_advice = BAGUA_HEALTH_METHODS.get(benming_gua, {})
        
        # 方位指导
        direction_guidance = self._get_personal_direction_guidance(benming_gua)
        
        return {
            "本命卦": benming_gua,
            "卦象信息": {
                "卦象": bagua_info.get("卦象", ""),
                "五行": bagua_info.get("五行", ""),
                "方位": bagua_info.get("方位", ""),
                "特性": bagua_info.get("特性", [])
            },
            "卦象特点": bagua_info.get("特性", []),  # 添加卦象特点字段
            "健康分析": health_analysis,
            "脏腑对应": {
                "主脏": organ_info.get("主脏", ""),
                "主腑": organ_info.get("主腑", ""),
                "对应部位": organ_info.get("对应部位", [])
            },
            "调理建议": treatment_advice,
            "方位指导": direction_guidance,
            "个性化建议": self._generate_personal_advice(benming_gua, birth_info)
        }
    
    def calculate_benming_gua(self, year_or_birth_info, gender=None) -> str:
        """
        计算本命卦（兼容测试）
        
        Args:
            year_or_birth_info: 年份或出生信息字典
            gender: 性别（当第一个参数是年份时使用）
            
        Returns:
            本命卦名称
        """
        if isinstance(year_or_birth_info, dict):
            # 字典格式
            birth_info = year_or_birth_info
            year = birth_info["year"]
            gender = birth_info.get("gender", "男")
        else:
            # 分别传递参数格式
            year = year_or_birth_info
            gender = gender if gender is not None else "男"
        
        year_last_two = year % 100
        
        if gender == "男":
            remainder = (100 - year_last_two) % 9
        else:  # 女性
            remainder = (year_last_two - 4) % 9
        
        if remainder == 0:
            remainder = 9
        
        # 根据余数确定卦
        bagua_map = {
            1: "坎", 2: "坤", 3: "震", 4: "巽",
            5: "坤", 6: "乾", 7: "兑", 8: "艮", 9: "离"
        }
        
        return bagua_map.get(remainder, "坎")
    
    def _analyze_personal_health(self, benming_gua: str, gender: str) -> Dict:
        """分析个人健康状况"""
        bagua_info = BAGUA_DATA.get(benming_gua, {})
        organ_info = BAGUA_ORGAN_MAP.get(benming_gua, {})
        
        # 基于八卦的健康特点
        health_features = []
        if benming_gua in ["乾", "兑"]:
            health_features.extend(["呼吸系统较强", "肺功能良好", "皮肤状态佳"])
        elif benming_gua in ["震", "巽"]:
            health_features.extend(["肝胆功能活跃", "神经系统敏感", "情绪变化较大"])
        elif benming_gua == "离":
            health_features.extend(["心血管系统活跃", "精神状态良好", "易上火"])
        elif benming_gua in ["坤", "艮"]:
            health_features.extend(["脾胃功能稳定", "消化能力强", "体质偏实"])
        elif benming_gua == "坎":
            health_features.extend(["肾功能较强", "生殖系统健康", "耐寒能力强"])
        
        # 易患疾病
        disease_tendency = BAGUA_DISEASE_PREDICTION.get(benming_gua, {}).get("易患疾病", [])
        
        # 预防建议
        prevention_advice = BAGUA_DISEASE_PREDICTION.get(benming_gua, {}).get("预防建议", [])
        
        return {
            "健康特点": health_features,
            "易患疾病": disease_tendency,
            "预防建议": prevention_advice,
            "重点关注": organ_info.get("对应部位", [])
        }
    
    def _get_personal_direction_guidance(self, benming_gua: str) -> Dict:
        """获取个人方位指导"""
        bagua_info = BAGUA_DATA.get(benming_gua, {})
        
        # 吉方和凶方
        favorable_direction = bagua_info.get("方位", "")
        unfavorable_directions = []
        
        # 根据八卦相对关系确定不利方位
        opposite_bagua = BAGUA_RELATIONS.get("相对", {}).get(benming_gua, "")
        if opposite_bagua:
            opposite_info = BAGUA_DATA.get(opposite_bagua, {})
            unfavorable_directions.append(opposite_info.get("方位", ""))
        
        return {
            "吉方": favorable_direction,
            "凶方": unfavorable_directions,
            "居住建议": f"宜居住在{favorable_direction}方位，避免{unfavorable_directions}方位",
            "办公建议": f"办公桌宜面向{favorable_direction}方",
            "睡眠建议": f"床头宜朝{favorable_direction}方"
        }
    
    def _generate_personal_advice(self, benming_gua: str, birth_info: Dict) -> List[str]:
        """生成个性化建议"""
        advice = []
        
        # 基于八卦的基本建议
        bagua_methods = BAGUA_HEALTH_METHODS.get(benming_gua, {})
        advice.extend(bagua_methods.get("养生方法", []))
        
        # 基于性别的建议
        gender = birth_info.get("gender", "男")
        if gender == "男":
            advice.append("注重阳气的培养和保护")
        else:
            advice.append("注重阴血的滋养和调理")
        
        # 基于年龄的建议（简化）
        current_year = datetime.now().year
        age = current_year - birth_info["year"]
        if age < 30:
            advice.append("年轻时期，注重基础体质的建立")
        elif age < 50:
            advice.append("中年时期，注重工作与健康的平衡")
        else:
            advice.append("中老年时期，注重养生保健")
        
        return list(set(advice))  # 去重
    
    def analyze_bagua_health(self, birth_datetime: datetime, current_datetime: datetime = None) -> Dict:
        """
        八卦健康分析
        
        Args:
            birth_datetime: 出生时间
            current_datetime: 当前时间（可选）
            
        Returns:
            八卦健康分析结果
        """
        if current_datetime is None:
            current_datetime = datetime.now()
        
        # 获取本命卦和当前卦
        birth_bagua = self.get_birth_bagua(birth_datetime)
        current_bagua = self.get_current_bagua(current_datetime)
        
        # 分析卦象关系
        bagua_relation = self._analyze_bagua_relation(birth_bagua, current_bagua)
        
        # 获取脏腑对应
        birth_organ = BAGUA_ORGAN_MAP.get(birth_bagua, {})
        current_organ = BAGUA_ORGAN_MAP.get(current_bagua, {})
        
        # 健康预测
        health_prediction = self._predict_health_by_bagua(birth_bagua, current_bagua, bagua_relation)
        
        # 养生建议
        health_advice = self._generate_bagua_health_advice(birth_bagua, current_bagua)
        
        # 方位调理
        direction_therapy = self._get_direction_therapy(birth_bagua, current_bagua)
        
        return {
            "出生时间": birth_datetime.strftime("%Y年%m月%d日 %H时"),
            "当前时间": current_datetime.strftime("%Y年%m月%d日 %H时"),
            "本命卦": {
                "卦名": birth_bagua,
                "卦象": BAGUA_DATA[birth_bagua]["卦象"],
                "五行": BAGUA_DATA[birth_bagua]["五行"],
                "方位": BAGUA_DATA[birth_bagua]["方位"],
                "主脏": birth_organ.get("主脏", ""),
                "主腑": birth_organ.get("主腑", ""),
                "对应部位": birth_organ.get("对应部位", [])
            },
            "当前卦": {
                "卦名": current_bagua,
                "卦象": BAGUA_DATA[current_bagua]["卦象"],
                "五行": BAGUA_DATA[current_bagua]["五行"],
                "方位": BAGUA_DATA[current_bagua]["方位"],
                "主脏": current_organ.get("主脏", ""),
                "主腑": current_organ.get("主腑", ""),
                "对应部位": current_organ.get("对应部位", [])
            },
            "卦象关系": bagua_relation,
            "健康预测": health_prediction,
            "养生建议": health_advice,
            "方位调理": direction_therapy,
            "重点关注": self._get_health_focus(birth_bagua, current_bagua)
        }
    
    def _analyze_bagua_relation(self, bagua1: str, bagua2: str) -> Dict:
        """分析两卦关系"""
        if bagua1 == bagua2:
            relation_type = "同卦"
            description = "本命卦与当前卦相同，气场和谐"
        elif BAGUA_RELATIONS["相对"].get(bagua1) == bagua2:
            relation_type = "相对"
            description = "本命卦与当前卦相对，需要平衡调和"
        elif bagua2 in BAGUA_RELATIONS["相邻"].get(bagua1, []):
            relation_type = "相邻"
            description = "本命卦与当前卦相邻，影响温和"
        else:
            relation_type = "其他"
            description = "本命卦与当前卦关系一般"
        
        # 分析五行关系
        wuxing1 = BAGUA_DATA[bagua1]["五行"]
        wuxing2 = BAGUA_DATA[bagua2]["五行"]
        wuxing_relation = self._analyze_wuxing_relation(wuxing1, wuxing2)
        
        return {
            "关系类型": relation_type,
            "关系描述": description,
            "五行关系": wuxing_relation,
            "影响程度": self._get_influence_level(relation_type, wuxing_relation)
        }
    
    def _analyze_wuxing_relation(self, wuxing1: str, wuxing2: str) -> str:
        """分析五行关系"""
        wuxing_sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        wuxing_ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        
        if wuxing1 == wuxing2:
            return "同类"
        elif wuxing_sheng.get(wuxing1) == wuxing2:
            return "相生"
        elif wuxing_sheng.get(wuxing2) == wuxing1:
            return "被生"
        elif wuxing_ke.get(wuxing1) == wuxing2:
            return "相克"
        elif wuxing_ke.get(wuxing2) == wuxing1:
            return "被克"
        else:
            return "平和"
    
    def _get_influence_level(self, relation_type: str, wuxing_relation: str) -> str:
        """获取影响程度"""
        if relation_type == "同卦" and wuxing_relation == "同类":
            return "非常有利"
        elif relation_type == "相邻" and wuxing_relation in ["相生", "被生"]:
            return "有利"
        elif relation_type == "其他" and wuxing_relation == "平和":
            return "中性"
        elif relation_type == "相对" or wuxing_relation in ["相克", "被克"]:
            return "需要调理"
        else:
            return "一般"
    
    def _predict_health_by_bagua(self, birth_bagua: str, current_bagua: str, relation: Dict) -> Dict:
        """根据八卦预测健康状况"""
        influence_level = relation["影响程度"]
        wuxing_relation = relation["五行关系"]
        
        # 获取可能的健康问题
        birth_diseases = BAGUA_ORGAN_MAP[birth_bagua]["主治疾病"]
        current_diseases = BAGUA_ORGAN_MAP[current_bagua]["主治疾病"]
        
        if influence_level == "需要调理":
            # 查找对应的疾病预测
            disease_key = f"{birth_bagua}卦受克"
            if disease_key in BAGUA_DISEASE_PREDICTION:
                prediction_info = BAGUA_DISEASE_PREDICTION[disease_key]
                risk_diseases = prediction_info["表现"]
                risk_level = "高"
            else:
                risk_diseases = birth_diseases
                risk_level = "中"
        elif influence_level == "中性":
            risk_diseases = list(set(birth_diseases) & set(current_diseases))
            risk_level = "低"
        else:
            risk_diseases = []
            risk_level = "很低"
        
        return {
            "风险等级": risk_level,
            "易发疾病": risk_diseases,
            "重点关注脏腑": [
                BAGUA_ORGAN_MAP[birth_bagua]["主脏"],
                BAGUA_ORGAN_MAP[current_bagua]["主脏"]
            ],
            "预防建议": self._get_prevention_advice(birth_bagua, current_bagua, influence_level)
        }
    
    def _generate_bagua_health_advice(self, birth_bagua: str, current_bagua: str) -> Dict:
        """生成八卦养生建议"""
        birth_methods = BAGUA_HEALTH_METHODS.get(birth_bagua, {})
        current_methods = BAGUA_HEALTH_METHODS.get(current_bagua, {})
        
        # 综合建议
        combined_advice = {
            "运动": list(set(birth_methods.get("运动", []) + current_methods.get("运动", []))),
            "饮食": list(set(birth_methods.get("饮食", []) + current_methods.get("饮食", []))),
            "情志": list(set(birth_methods.get("情志", []) + current_methods.get("情志", []))),
            "起居": list(set(birth_methods.get("起居", []) + current_methods.get("起居", [])))
        }
        
        return {
            "本命卦养生": birth_methods,
            "当前卦养生": current_methods,
            "综合建议": combined_advice,
            "重点方法": self._get_priority_methods(birth_bagua, current_bagua)
        }
    
    def _get_direction_therapy(self, birth_bagua: str, current_bagua: str) -> Dict:
        """获取方位调理建议"""
        birth_direction = BAGUA_DATA[birth_bagua]["方位"]
        current_direction = BAGUA_DATA[current_bagua]["方位"]
        
        # 有利方位
        beneficial_directions = [birth_direction]
        
        # 需要避免的方位
        avoid_directions = []
        
        # 根据相克关系确定避免方位
        birth_wuxing = BAGUA_DATA[birth_bagua]["五行"]
        wuxing_ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        ke_wuxing = wuxing_ke.get(birth_wuxing)
        
        if ke_wuxing:
            for bagua, data in BAGUA_DATA.items():
                if data["五行"] == ke_wuxing:
                    avoid_directions.append(data["方位"])
        
        return {
            "有利方位": beneficial_directions,
            "避免方位": avoid_directions,
            "居住建议": f"宜居住在{birth_direction}方向，或面向{birth_direction}方向",
            "工作建议": f"工作位置宜选择{birth_direction}方向",
            "运动建议": f"运动时宜面向{birth_direction}方向",
            "睡眠建议": f"睡觉时头部宜朝向{birth_direction}方向"
        }
    
    def _get_health_focus(self, birth_bagua: str, current_bagua: str) -> List[str]:
        """获取健康重点关注事项"""
        focus_points = []
        
        birth_organ = BAGUA_ORGAN_MAP[birth_bagua]
        current_organ = BAGUA_ORGAN_MAP[current_bagua]
        
        # 重点关注脏腑
        focus_points.append(f"重点保养{birth_organ['主脏']}和{birth_organ['主腑']}")
        
        # 重点关注部位
        focus_parts = birth_organ["对应部位"]
        if focus_parts:
            focus_points.append(f"注意保护{', '.join(focus_parts)}")
        
        # 情志调养
        emotion = birth_organ["情志"]
        focus_points.append(f"避免过度{emotion}，保持情志平和")
        
        # 季节调养
        season = BAGUA_DATA[birth_bagua]["季节"]
        focus_points.append(f"在{season}时期特别注意调养")
        
        return focus_points
    
    def _get_prevention_advice(self, birth_bagua: str, current_bagua: str, influence_level: str) -> List[str]:
        """获取预防建议"""
        advice = []
        
        if influence_level == "需要调理":
            disease_key = f"{birth_bagua}卦受克"
            if disease_key in BAGUA_DISEASE_PREDICTION:
                prediction_info = BAGUA_DISEASE_PREDICTION[disease_key]
                advice.append(prediction_info["治疗"])
                advice.append(prediction_info["方位调理"])
        
        # 基础预防建议
        birth_methods = BAGUA_HEALTH_METHODS.get(birth_bagua, {})
        advice.extend(birth_methods.get("情志", []))
        advice.extend(birth_methods.get("起居", []))
        
        return list(set(advice))
    
    def _get_priority_methods(self, birth_bagua: str, current_bagua: str) -> List[str]:
        """获取优先养生方法"""
        priority_methods = []
        
        # 根据本命卦确定基础方法
        birth_methods = BAGUA_HEALTH_METHODS.get(birth_bagua, {})
        priority_methods.extend(birth_methods.get("运动", [])[:2])  # 取前两个
        priority_methods.extend(birth_methods.get("饮食", [])[:2])  # 取前两个
        
        # 根据当前卦调整
        current_methods = BAGUA_HEALTH_METHODS.get(current_bagua, {})
        priority_methods.extend(current_methods.get("情志", [])[:1])  # 取一个
        
        return list(set(priority_methods))
    
    def get_bagua_compatibility(self, person1_birth: datetime, person2_birth: datetime) -> Dict:
        """
        分析两人八卦相配性
        
        Args:
            person1_birth: 第一人出生时间
            person2_birth: 第二人出生时间
            
        Returns:
            八卦相配性分析结果
        """
        bagua1 = self.get_birth_bagua(person1_birth)
        bagua2 = self.get_birth_bagua(person2_birth)
        
        # 分析卦象关系
        relation = self._analyze_bagua_relation(bagua1, bagua2)
        
        # 获取脏腑信息
        organ1 = BAGUA_ORGAN_MAP[bagua1]
        organ2 = BAGUA_ORGAN_MAP[bagua2]
        
        # 相配性评分
        compatibility_score = self._calculate_compatibility_score(bagua1, bagua2, relation)
        
        return {
            "人员1": {
                "本命卦": bagua1,
                "卦象": BAGUA_DATA[bagua1]["卦象"],
                "主脏腑": f"{organ1['主脏']}{organ1['主腑']}",
                "方位": BAGUA_DATA[bagua1]["方位"]
            },
            "人员2": {
                "本命卦": bagua2,
                "卦象": BAGUA_DATA[bagua2]["卦象"],
                "主脏腑": f"{organ2['主脏']}{organ2['主腑']}",
                "方位": BAGUA_DATA[bagua2]["方位"]
            },
            "相配性": {
                "关系类型": relation["关系类型"],
                "五行关系": relation["五行关系"],
                "相配评分": compatibility_score,
                "相配等级": self._get_compatibility_level(compatibility_score)
            },
            "建议": self._get_compatibility_advice(bagua1, bagua2, relation)
        }
    
    def _calculate_compatibility_score(self, bagua1: str, bagua2: str, relation: Dict) -> int:
        """计算相配性评分（0-100）"""
        base_score = 50
        
        relation_type = relation["关系类型"]
        wuxing_relation = relation["五行关系"]
        
        # 根据卦象关系调整分数
        if relation_type == "同卦":
            base_score += 20
        elif relation_type == "相邻":
            base_score += 10
        elif relation_type == "相对":
            base_score -= 10
        
        # 根据五行关系调整分数
        if wuxing_relation == "同类":
            base_score += 15
        elif wuxing_relation in ["相生", "被生"]:
            base_score += 10
        elif wuxing_relation == "平和":
            base_score += 0
        elif wuxing_relation in ["相克", "被克"]:
            base_score -= 15
        
        return max(0, min(100, base_score))
    
    def _get_compatibility_level(self, score: int) -> str:
        """根据评分获取相配等级"""
        if score >= 80:
            return "非常相配"
        elif score >= 65:
            return "比较相配"
        elif score >= 50:
            return "一般相配"
        elif score >= 35:
            return "需要磨合"
        else:
            return "不太相配"
    
    def _get_compatibility_advice(self, bagua1: str, bagua2: str, relation: Dict) -> List[str]:
        """获取相配性建议"""
        advice = []
        
        relation_type = relation["关系类型"]
        wuxing_relation = relation["五行关系"]
        
        if relation_type == "同卦":
            advice.append("两人本命卦相同，容易理解对方")
            advice.append("注意避免共同的弱点和缺陷")
        elif relation_type == "相对":
            advice.append("两人本命卦相对，需要相互包容")
            advice.append("可以通过中间方位调和关系")
        elif relation_type == "相邻":
            advice.append("两人本命卦相邻，关系和谐")
            advice.append("可以相互学习对方的优点")
        
        if wuxing_relation in ["相克", "被克"]:
            advice.append("五行相克，需要通过调理化解")
            advice.append("建议多在中性方位共同活动")
        elif wuxing_relation in ["相生", "被生"]:
            advice.append("五行相生，关系互补")
            advice.append("可以相互促进健康发展")
        
        return advice 
    
    def analyze_bagua(self, birth_info: Dict) -> Dict:
        """
        八卦分析（兼容测试）
        
        Args:
            birth_info: 出生信息
            
        Returns:
            八卦分析结果
        """
        return self.analyze_personal_bagua(birth_info)