"""
五运六气计算器

实现五运六气推演的核心算法
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from .data import (
    GANZHI_WUYUN_MAP,
    LIUQI_SITIAN_ZAIQUAN,
    WUYUN_DATA,
    LIUQI_DATA,
    YEAR_GANZHI_MAP,
    DISEASE_WUYUN_LIUQI_MAP,
    SOLAR_TERMS_LIUQI_MAP
)


class WuyunLiuqiCalculator:
    """五运六气计算器"""
    
    def __init__(self):
        """初始化计算器"""
        self.tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    def get_year_ganzhi(self, year: int) -> str:
        """
        获取年份对应的干支
        
        Args:
            year: 年份
            
        Returns:
            干支字符串
        """
        if year in YEAR_GANZHI_MAP:
            return YEAR_GANZHI_MAP[year]
        
        # 计算干支（以1984年甲子为基准）
        base_year = 1984
        year_diff = year - base_year
        
        tiangan_index = year_diff % 10
        dizhi_index = year_diff % 12
        
        return self.tiangan[tiangan_index] + self.dizhi[dizhi_index]
    
    def get_wuyun_from_ganzhi(self, ganzhi: str) -> str:
        """
        根据干支获取五运
        
        Args:
            ganzhi: 干支
            
        Returns:
            五运类型
        """
        return GANZHI_WUYUN_MAP.get(ganzhi, "未知")
    
    def get_liuqi_from_dizhi(self, dizhi: str) -> Dict[str, str]:
        """
        根据地支获取六气司天在泉
        
        Args:
            dizhi: 地支
            
        Returns:
            包含司天和在泉的字典
        """
        # 根据地支确定六气
        liuqi_map = {
            "子": "子午", "午": "子午",
            "丑": "丑未", "未": "丑未", 
            "寅": "寅申", "申": "寅申",
            "卯": "卯酉", "酉": "卯酉",
            "辰": "辰戌", "戌": "辰戌",
            "巳": "巳亥", "亥": "巳亥"
        }
        
        liuqi_key = liuqi_map.get(dizhi, "子午")
        return LIUQI_SITIAN_ZAIQUAN.get(liuqi_key, {"司天": "未知", "在泉": "未知"})
    
    def calculate_wuyun_liuqi(self, year: int, patient_birth: Optional[date] = None) -> Dict:
        """
        计算指定年份的五运六气
        
        Args:
            year: 分析年份
            patient_birth: 患者出生日期（可选）
            
        Returns:
            五运六气分析结果
        """
        # 获取年份干支
        ganzhi = self.get_year_ganzhi(year)
        tiangan = ganzhi[0]
        dizhi = ganzhi[1]
        
        # 获取五运
        wuyun_type = self.get_wuyun_from_ganzhi(ganzhi)
        wuyun_data = WUYUN_DATA.get(wuyun_type, {})
        
        # 获取六气
        liuqi_info = self.get_liuqi_from_dizhi(dizhi)
        sitian = liuqi_info["司天"]
        zaiquan = liuqi_info["在泉"]
        
        sitian_data = LIUQI_DATA.get(sitian, {})
        zaiquan_data = LIUQI_DATA.get(zaiquan, {})
        
        # 分析气候影响
        climate_influence = self._analyze_climate_influence(wuyun_type, sitian, zaiquan)
        
        # 预测易发疾病
        diseases_prone = self._predict_diseases(wuyun_type, sitian, zaiquan)
        
        # 生成预防建议
        prevention_advice = self._generate_prevention_advice(wuyun_data, sitian_data, zaiquan_data)
        
        result = {
            "year": year,
            "ganzhi": ganzhi,
            "wuyun": {
                "type": wuyun_type,
                "characteristics": wuyun_data.get("特性", []),
                "diseases_prone": wuyun_data.get("易发疾病", []),
                "prevention_advice": wuyun_data.get("预防建议", []),
                "dietary_advice": wuyun_data.get("饮食宜忌", []),
                "treatment_principle": wuyun_data.get("治疗原则", "")
            },
            "liuqi": {
                "sitian": {
                    "type": sitian,
                    "characteristics": sitian_data.get("特性", []),
                    "climate_features": sitian_data.get("气候特点", []),
                    "diseases_prone": sitian_data.get("易发疾病", []),
                    "prevention_advice": sitian_data.get("预防建议", []),
                    "treatment_principle": sitian_data.get("治疗原则", "")
                },
                "zaiquan": {
                    "type": zaiquan,
                    "characteristics": zaiquan_data.get("特性", []),
                    "climate_features": zaiquan_data.get("气候特点", []),
                    "diseases_prone": zaiquan_data.get("易发疾病", []),
                    "prevention_advice": zaiquan_data.get("预防建议", []),
                    "treatment_principle": zaiquan_data.get("治疗原则", "")
                }
            },
            "climate_influence": climate_influence,
            "diseases_prone": diseases_prone,
            "prevention_advice": prevention_advice
        }
        
        # 如果提供了患者出生信息，进行个性化分析
        if patient_birth:
            result["personalized_analysis"] = self._personalized_analysis(
                result, patient_birth
            )
        
        return result
    
    def _analyze_climate_influence(self, wuyun: str, sitian: str, zaiquan: str) -> str:
        """
        分析气候影响
        
        Args:
            wuyun: 五运类型
            sitian: 司天
            zaiquan: 在泉
            
        Returns:
            气候影响描述
        """
        influences = []
        
        # 五运影响
        if "太过" in wuyun:
            element = wuyun.replace("运太过", "")
            influences.append(f"{element}气偏盛")
        elif "不及" in wuyun:
            element = wuyun.replace("运不及", "")
            influences.append(f"{element}气不足")
        
        # 六气影响
        if "风木" in sitian:
            influences.append("风气主令，多变化")
        elif "君火" in sitian or "相火" in sitian:
            influences.append("火气主令，偏温热")
        elif "湿土" in sitian:
            influences.append("湿气主令，多雨湿")
        elif "燥金" in sitian:
            influences.append("燥气主令，偏干燥")
        elif "寒水" in sitian:
            influences.append("寒气主令，偏寒冷")
        
        return "，".join(influences) if influences else "气候平和"
    
    def _predict_diseases(self, wuyun: str, sitian: str, zaiquan: str) -> List[str]:
        """
        预测易发疾病
        
        Args:
            wuyun: 五运类型
            sitian: 司天
            zaiquan: 在泉
            
        Returns:
            易发疾病列表
        """
        diseases = set()
        
        # 从五运数据获取疾病
        wuyun_data = WUYUN_DATA.get(wuyun, {})
        diseases.update(wuyun_data.get("易发疾病", []))
        
        # 从六气数据获取疾病
        sitian_data = LIUQI_DATA.get(sitian, {})
        diseases.update(sitian_data.get("易发疾病", []))
        
        zaiquan_data = LIUQI_DATA.get(zaiquan, {})
        diseases.update(zaiquan_data.get("易发疾病", []))
        
        # 从疾病运气关系获取相关疾病
        for disease, info in DISEASE_WUYUN_LIUQI_MAP.items():
            related_yunqi = info["相关运气"]
            if wuyun in related_yunqi or sitian in related_yunqi or zaiquan in related_yunqi:
                diseases.add(disease)
        
        return list(diseases)
    
    def _generate_prevention_advice(self, wuyun_data: Dict, sitian_data: Dict, zaiquan_data: Dict) -> List[str]:
        """
        生成预防建议
        
        Args:
            wuyun_data: 五运数据
            sitian_data: 司天数据
            zaiquan_data: 在泉数据
            
        Returns:
            预防建议列表
        """
        advice = set()
        
        # 从各数据源收集建议
        for data in [wuyun_data, sitian_data, zaiquan_data]:
            advice.update(data.get("预防建议", []))
        
        return list(advice)
    
    def _personalized_analysis(self, base_result: Dict, birth_date: date) -> Dict:
        """
        基于出生信息的个性化分析
        
        Args:
            base_result: 基础分析结果
            birth_date: 出生日期
            
        Returns:
            个性化分析结果
        """
        birth_year = birth_date.year
        birth_ganzhi = self.get_year_ganzhi(birth_year)
        birth_wuyun = self.get_wuyun_from_ganzhi(birth_ganzhi)
        
        current_wuyun = base_result["wuyun"]["type"]
        
        # 分析运气相合相克关系
        compatibility = self._analyze_wuyun_compatibility(birth_wuyun, current_wuyun)
        
        # 生成个性化建议
        personalized_advice = self._generate_personalized_advice(
            birth_wuyun, current_wuyun, compatibility
        )
        
        return {
            "birth_year": birth_year,
            "birth_ganzhi": birth_ganzhi,
            "birth_wuyun": birth_wuyun,
            "current_wuyun": current_wuyun,
            "compatibility": compatibility,
            "personalized_advice": personalized_advice
        }
    
    def _analyze_wuyun_compatibility(self, birth_wuyun: str, current_wuyun: str) -> str:
        """
        分析五运相合相克关系
        
        Args:
            birth_wuyun: 出生年五运
            current_wuyun: 当前年五运
            
        Returns:
            相合相克关系描述
        """
        # 提取五行元素
        birth_element = self._extract_element(birth_wuyun)
        current_element = self._extract_element(current_wuyun)
        
        # 五行相生相克关系
        shengke_map = {
            ("木", "火"): "相生", ("火", "土"): "相生", ("土", "金"): "相生",
            ("金", "水"): "相生", ("水", "木"): "相生",
            ("木", "土"): "相克", ("土", "水"): "相克", ("水", "火"): "相克",
            ("火", "金"): "相克", ("金", "木"): "相克"
        }
        
        relation = shengke_map.get((birth_element, current_element), "平和")
        
        if relation == "相生":
            return f"出生年{birth_element}运与当前年{current_element}运相生，有利健康"
        elif relation == "相克":
            return f"出生年{birth_element}运与当前年{current_element}运相克，需要调理"
        else:
            return f"出生年{birth_element}运与当前年{current_element}运关系平和"
    
    def _extract_element(self, wuyun: str) -> str:
        """
        从五运类型中提取五行元素
        
        Args:
            wuyun: 五运类型
            
        Returns:
            五行元素
        """
        if "木运" in wuyun:
            return "木"
        elif "火运" in wuyun:
            return "火"
        elif "土运" in wuyun:
            return "土"
        elif "金运" in wuyun:
            return "金"
        elif "水运" in wuyun:
            return "水"
        else:
            return "未知"
    
    def _generate_personalized_advice(self, birth_wuyun: str, current_wuyun: str, compatibility: str) -> List[str]:
        """
        生成个性化建议
        
        Args:
            birth_wuyun: 出生年五运
            current_wuyun: 当前年五运
            compatibility: 相合相克关系
            
        Returns:
            个性化建议列表
        """
        advice = []
        
        if "相生" in compatibility:
            advice.extend([
                "当前运气对您有利，可适当进补",
                "保持良好的生活习惯",
                "适度运动，增强体质"
            ])
        elif "相克" in compatibility:
            advice.extend([
                "当前运气对您不利，需要特别注意调理",
                "避免过度劳累，注意休息",
                "饮食宜清淡，避免刺激性食物",
                "建议寻求专业中医师指导"
            ])
        else:
            advice.extend([
                "当前运气对您影响中等",
                "保持规律作息",
                "注意季节变化，适时调整"
            ])
        
        # 根据具体五运类型添加建议
        birth_data = WUYUN_DATA.get(birth_wuyun, {})
        current_data = WUYUN_DATA.get(current_wuyun, {})
        
        if birth_data:
            advice.extend(birth_data.get("预防建议", []))
        if current_data:
            advice.extend(current_data.get("预防建议", []))
        
        return list(set(advice))  # 去重
    
    def get_seasonal_liuqi(self, date_obj: date) -> str:
        """
        根据日期获取当前节气对应的六气
        
        Args:
            date_obj: 日期
            
        Returns:
            六气类型
        """
        # 简化版本，实际应该根据精确的节气计算
        month = date_obj.month
        
        if month in [1, 2]:
            return "太阳寒水"
        elif month in [3, 4]:
            return "厥阴风木"
        elif month in [5, 6]:
            return "少阴君火"
        elif month in [7, 8]:
            return "太阴湿土"
        elif month in [9, 10]:
            return "阳明燥金"
        else:  # 11, 12
            return "太阳寒水"

    def calculate_year_analysis(self, year: int) -> Dict:
        """
        计算年份分析（简化版本，用于测试）
        
        Args:
            year: 年份
            
        Returns:
            年份分析结果
        """
        result = self.calculate_wuyun_liuqi(year)
        
        # 简化返回格式以匹配测试期望
        return {
            "year_ganzhi": result["ganzhi"],
            "wuyun": {
                "name": result["wuyun"]["type"],
                "characteristics": result["wuyun"]["characteristics"]
            },
            "liuqi": {
                "name": result["liuqi"]["sitian"]["type"],
                "characteristics": result["liuqi"]["sitian"]["characteristics"]
            }
        } 