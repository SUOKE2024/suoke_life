"""
bagua_calculator - 索克生活项目模块
"""

from datetime import date
from typing import Dict, Optional, List

"""
八卦计算器

用于八卦体质分析和卦象推演
"""



class BaguaCalculator:
    """八卦计算器"""
    
    def __init__(self):
        """初始化计算器"""
        # 八卦基本信息
        self.bagua_info = {
            "乾": {
                "五行": "金",
                "脏腑": "肺、大肠",
                "方位": "西北",
                "特性": ["刚健", "主动", "领导"],
                "体质": "金型体质"
            },
            "坤": {
                "五行": "土",
                "脏腑": "脾、胃",
                "方位": "西南",
                "特性": ["柔顺", "包容", "稳重"],
                "体质": "土型体质"
            },
            "震": {
                "五行": "木",
                "脏腑": "肝、胆",
                "方位": "东",
                "特性": ["动", "进取", "急躁"],
                "体质": "木型体质"
            },
            "巽": {
                "五行": "木",
                "脏腑": "肝、胆",
                "方位": "东南",
                "特性": ["柔和", "渐进", "顺从"],
                "体质": "木型体质"
            },
            "坎": {
                "五行": "水",
                "脏腑": "肾、膀胱",
                "方位": "北",
                "特性": ["智慧", "深沉", "流动"],
                "体质": "水型体质"
            },
            "离": {
                "五行": "火",
                "脏腑": "心、小肠",
                "方位": "南",
                "特性": ["光明", "热情", "外向"],
                "体质": "火型体质"
            },
            "艮": {
                "五行": "土",
                "脏腑": "脾、胃",
                "方位": "东北",
                "特性": ["稳定", "止静", "内敛"],
                "体质": "土型体质"
            },
            "兑": {
                "五行": "金",
                "脏腑": "肺、大肠",
                "方位": "西",
                "特性": ["喜悦", "交流", "灵活"],
                "体质": "金型体质"
            }
        }
    
    def analyze_constitution(self, bazi: Dict, birth_location: Optional[Dict] = None) -> Dict:
        """
        基于八字分析八卦体质
        
        Args:
            bazi: 八字信息
            birth_location: 出生地点
            
        Returns:
            八卦体质分析结果
        """
        # 根据五行分布确定主卦
        wuxing = bazi["wuxing"]
        dominant_element = wuxing["dominant_element"]
        
        # 根据主导五行确定八卦
        primary_gua = self._get_gua_from_element(dominant_element)
        
        # 获取八卦信息
        gua_info = self.bagua_info[primary_gua]
        
        # 分析体质特征
        constitution_analysis = self._analyze_constitution_characteristics(
            primary_gua, gua_info, wuxing
        )
        
        # 生成健康建议
        health_advice = self._generate_health_advice(primary_gua, gua_info)
        
        return {
            "primary_gua": primary_gua,
            "gua_element": gua_info["五行"],
            "organ_correspondence": gua_info["脏腑"],
            "direction": gua_info["方位"],
            "constitution_type": gua_info["体质"],
            "characteristics": constitution_analysis["characteristics"],
            "health_advice": health_advice,
            "disease_location": constitution_analysis["disease_location"],
            "personality_traits": gua_info["特性"]
        }
    
    def _get_gua_from_element(self, element: str) -> str:
        """
        根据五行元素获取对应八卦
        
        Args:
            element: 五行元素
            
        Returns:
            八卦名称
        """
        element_gua_map = {
            "木": "震",  # 震为雷，木之象
            "火": "离",  # 离为火
            "土": "坤",  # 坤为地，土之象
            "金": "乾",  # 乾为天，金之象
            "水": "坎"   # 坎为水
        }
        
        return element_gua_map.get(element, "坤")
    
    def _analyze_constitution_characteristics(self, gua: str, gua_info: Dict, wuxing: Dict) -> Dict:
        """
        分析体质特征
        
        Args:
            gua: 八卦名称
            gua_info: 八卦信息
            wuxing: 五行分布
            
        Returns:
            体质特征分析
        """
        characteristics = []
        disease_location = ""
        
        if gua == "乾":
            characteristics = [
                "性格刚强果断",
                "具有领导能力",
                "肺气充足",
                "皮肤较好"
            ]
            disease_location = "肺系、皮肤、大肠"
            
        elif gua == "坤":
            characteristics = [
                "性格温和包容",
                "消化功能良好",
                "肌肉丰满",
                "适应性强"
            ]
            disease_location = "脾胃系统"
            
        elif gua == "震":
            characteristics = [
                "性格急躁易怒",
                "行动力强",
                "筋骨强健",
                "反应敏捷"
            ]
            disease_location = "肝胆系统、筋骨"
            
        elif gua == "巽":
            characteristics = [
                "性格温和渐进",
                "善于沟通",
                "肝气条达",
                "适应变化"
            ]
            disease_location = "肝胆系统、神经系统"
            
        elif gua == "坎":
            characteristics = [
                "性格深沉智慧",
                "意志坚强",
                "肾气充足",
                "骨骼强健"
            ]
            disease_location = "肾系、泌尿生殖系统"
            
        elif gua == "离":
            characteristics = [
                "性格热情开朗",
                "思维敏捷",
                "心火旺盛",
                "精神饱满"
            ]
            disease_location = "心系、血管、神经系统"
            
        elif gua == "艮":
            characteristics = [
                "性格稳重内敛",
                "思考深入",
                "脾胃功能稳定",
                "耐力较好"
            ]
            disease_location = "脾胃、肌肉系统"
            
        elif gua == "兑":
            characteristics = [
                "性格开朗善交际",
                "表达能力强",
                "肺气宣发良好",
                "声音洪亮"
            ]
            disease_location = "肺系、口舌、呼吸系统"
        
        return {
            "characteristics": characteristics,
            "disease_location": disease_location
        }
    
    def _generate_health_advice(self, gua: str, gua_info: Dict) -> List[str]:
        """
        生成健康建议
        
        Args:
            gua: 八卦名称
            gua_info: 八卦信息
            
        Returns:
            健康建议列表
        """
        advice = []
        
        if gua == "乾":
            advice = [
                "注意润肺止咳",
                "避免过度劳累",
                "保持皮肤湿润",
                "适度运动增强体质"
            ]
            
        elif gua == "坤":
            advice = [
                "健脾益胃",
                "饮食规律清淡",
                "避免过度思虑",
                "适当运动促进消化"
            ]
            
        elif gua == "震":
            advice = [
                "疏肝理气",
                "调畅情志",
                "避免暴怒",
                "适度运动舒筋活血"
            ]
            
        elif gua == "巽":
            advice = [
                "养肝血",
                "保持心情舒畅",
                "避免过度紧张",
                "多做柔和运动"
            ]
            
        elif gua == "坎":
            advice = [
                "补肾益精",
                "避免过度房事",
                "注意保暖",
                "适当进补"
            ]
            
        elif gua == "离":
            advice = [
                "清心降火",
                "养心安神",
                "避免过度兴奋",
                "保持心境平和"
            ]
            
        elif gua == "艮":
            advice = [
                "健脾化湿",
                "避免久坐不动",
                "保持适度运动",
                "注意肌肉锻炼"
            ]
            
        elif gua == "兑":
            advice = [
                "润肺止咳",
                "保护嗓子",
                "避免辛辣刺激",
                "多做呼吸运动"
            ]
        
        return advice

    def calculate_constitution(self, birth_date: date, gender: str) -> Dict:
        """
        计算八卦体质（简化版本，用于测试）
        
        Args:
            birth_date: 出生日期
            gender: 性别
            
        Returns:
            八卦体质分析结果
        """
        # 简化计算：根据出生年份确定主卦
        year = birth_date.year
        
        # 根据年份尾数确定八卦
        year_last_digit = year % 8
        gua_list = ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"]
        primary_gua = gua_list[year_last_digit]
        
        # 获取八卦信息
        gua_info = self.bagua_info[primary_gua]
        
        return {
            "primary_gua": primary_gua,
            "constitution_type": gua_info["体质"],
            "element": gua_info["五行"],
            "organ_correspondence": gua_info["脏腑"],
            "characteristics": gua_info["特性"],
            "direction": gua_info["方位"]
        } 