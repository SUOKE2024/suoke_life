"""
五运六气计算器

实现五运六气运气学说的核心算法
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import calendar

from .data import (
    WUYUN_DATA,
    LIUQI_DATA,
    JIAZI_NAYIN,
    YUNQI_DISEASE_MAP,
    LIUQI_DISEASE_MAP,
    ZHUKE_QI_TIME,
    SITIAN_ZAIQUAN,
    YUNQI_HEHUA
)


class WuyunLiuqiCalculator:
    """五运六气计算器"""
    
    def __init__(self):
        """初始化计算器"""
        self.tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        # 运气推算基准年（甲子年）
        self.base_year = 1984
        
        # 六气循环顺序
        self.liuqi_order = ["厥阴风木", "少阴君火", "太阴湿土", "少阳相火", "阳明燥金", "太阳寒水"]
    
    def get_year_ganzhi(self, year: int) -> str:
        """获取年份干支"""
        year_diff = year - self.base_year
        tiangan_index = year_diff % 10
        dizhi_index = year_diff % 12
        return self.tiangan[tiangan_index] + self.dizhi[dizhi_index]
    
    def get_wuyun(self, year: int) -> Dict:
        """
        获取年份五运
        
        Args:
            year: 年份
            
        Returns:
            五运信息
        """
        ganzhi = self.get_year_ganzhi(year)
        year_gan = ganzhi[0]
        
        # 根据年干确定五运
        wuyun_key = None
        for key in WUYUN_DATA.keys():
            if year_gan in key:
                wuyun_key = key
                break
        
        if wuyun_key:
            wuyun_info = WUYUN_DATA[wuyun_key].copy()
            wuyun_info["年干"] = year_gan
            wuyun_info["年支"] = ganzhi[1]
            wuyun_info["干支"] = ganzhi
            
            # 判断运的强弱
            wuyun_strength = self._determine_wuyun_strength(year, wuyun_info)
            wuyun_info.update(wuyun_strength)
            
            return wuyun_info
        
        return {"运": "未知", "年干": year_gan}
    
    def get_sitian_zaiquan(self, year: int) -> Dict:
        """
        获取司天在泉
        
        Args:
            year: 年份
            
        Returns:
            司天在泉信息
        """
        ganzhi = self.get_year_ganzhi(year)
        year_zhi = ganzhi[1]
        
        # 根据年支确定司天在泉
        for key, value in SITIAN_ZAIQUAN.items():
            if year_zhi in key:
                return {
                    "年支": year_zhi,
                    "司天": value["司天"],
                    "在泉": value["在泉"],
                    "司天信息": LIUQI_DATA.get(value["司天"], {}),
                    "在泉信息": LIUQI_DATA.get(value["在泉"], {})
                }
        
        return {"年支": year_zhi, "司天": "未知", "在泉": "未知"}
    
    def get_current_qi(self, dt: datetime) -> Dict:
        """
        获取当前时期的气
        
        Args:
            dt: 日期时间
            
        Returns:
            当前气信息
        """
        month = dt.month
        
        # 根据月份确定当前是第几气
        current_qi = None
        for qi_name, qi_info in ZHUKE_QI_TIME.items():
            if month in qi_info["月份"]:
                current_qi = qi_name
                break
        
        if current_qi:
            qi_info = ZHUKE_QI_TIME[current_qi]
            zhuqi = qi_info["主气"]
            
            # 获取客气（需要根据年份司天推算）
            year = dt.year
            sitian_info = self.get_sitian_zaiquan(year)
            keqi = self._calculate_keqi(current_qi, sitian_info["司天"])
            
            return {
                "当前气": current_qi,
                "时间范围": qi_info["时间"],
                "主气": zhuqi,
                "客气": keqi,
                "主气信息": LIUQI_DATA.get(zhuqi, {}),
                "客气信息": LIUQI_DATA.get(keqi, {}),
                "月份": qi_info["月份"]
            }
        
        return {"当前气": "未知", "月份": month}
    
    def analyze_current_period(self, dt: datetime = None) -> Dict:
        """
        分析当前时期的运气特点
        
        Args:
            dt: 日期时间，默认为当前时间
            
        Returns:
            当前时期运气分析
        """
        if dt is None:
            dt = datetime.now()
        
        year = dt.year
        
        # 获取五运
        wuyun_info = self.get_wuyun(year)
        
        # 获取司天在泉
        sitian_info = self.get_sitian_zaiquan(year)
        
        # 获取当前气
        current_qi_info = self.get_current_qi(dt)
        
        # 分析运气相合
        yunqi_relation = self._analyze_yunqi_relation(wuyun_info, sitian_info)
        
        # 预测易发疾病
        disease_prediction = self._predict_diseases(wuyun_info, current_qi_info, yunqi_relation)
        
        # 生成调养建议
        health_advice = self._generate_health_advice(wuyun_info, current_qi_info, disease_prediction)
        
        return {
            "分析时间": dt.strftime("%Y年%m月%d日"),
            "年份干支": wuyun_info.get("干支", ""),
            "五运分析": wuyun_info,
            "司天在泉": sitian_info,
            "当前气分析": current_qi_info,
            "运气相合": yunqi_relation,
            "疾病预测": disease_prediction,
            "调养建议": health_advice,
            "总体特点": self._summarize_period_characteristics(wuyun_info, sitian_info, current_qi_info)
        }
    
    def _determine_wuyun_strength(self, year: int, wuyun_info: Dict) -> Dict:
        """判断五运强弱"""
        # 简化算法：根据年份和运的特点判断
        year_last_digit = year % 10
        
        if year_last_digit in [4, 9]:  # 甲己年
            if wuyun_info["运"] == "土运":
                return {"运势": "平气", "特点": wuyun_info["平气"]}
        elif year_last_digit in [5, 0]:  # 乙庚年
            if wuyun_info["运"] == "金运":
                return {"运势": "太过", "特点": wuyun_info["太过"]}
        elif year_last_digit in [6, 1]:  # 丙辛年
            if wuyun_info["运"] == "水运":
                return {"运势": "不及", "特点": wuyun_info["不及"]}
        elif year_last_digit in [7, 2]:  # 丁壬年
            if wuyun_info["运"] == "木运":
                return {"运势": "太过", "特点": wuyun_info["太过"]}
        elif year_last_digit in [8, 3]:  # 戊癸年
            if wuyun_info["运"] == "火运":
                return {"运势": "不及", "特点": wuyun_info["不及"]}
        
        return {"运势": "平气", "特点": "运气平和"}
    
    def _calculate_keqi(self, current_qi: str, sitian: str) -> str:
        """计算客气"""
        # 根据司天推算客气
        sitian_index = self.liuqi_order.index(sitian) if sitian in self.liuqi_order else 0
        
        qi_mapping = {
            "初之气": (sitian_index + 2) % 6,
            "二之气": (sitian_index + 3) % 6,
            "三之气": (sitian_index + 4) % 6,
            "四之气": (sitian_index + 5) % 6,
            "五之气": (sitian_index + 0) % 6,
            "六之气": (sitian_index + 1) % 6
        }
        
        keqi_index = qi_mapping.get(current_qi, 0)
        return self.liuqi_order[keqi_index]
    
    def _analyze_yunqi_relation(self, wuyun_info: Dict, sitian_info: Dict) -> Dict:
        """分析运气相合关系"""
        wuyun = wuyun_info.get("运", "")
        sitian = sitian_info.get("司天", "")
        
        # 获取五行属性
        wuyun_wuxing = wuyun_info.get("五行", "")
        sitian_wuxing = LIUQI_DATA.get(sitian, {}).get("五行", "")
        
        # 判断相合关系
        relations = []
        
        if wuyun_wuxing == sitian_wuxing:
            relations.append("天符")
        
        # 简化的相合判断
        if wuyun == "火运" and sitian == "少阴君火":
            relations.append("太乙天符")
        
        if not relations:
            relations.append("一般")
        
        return {
            "相合类型": relations,
            "运气关系": f"{wuyun}与{sitian}",
            "五行关系": f"{wuyun_wuxing}与{sitian_wuxing}",
            "影响程度": "强" if "天符" in relations else "中等"
        }
    
    def _predict_diseases(self, wuyun_info: Dict, current_qi_info: Dict, yunqi_relation: Dict) -> Dict:
        """预测易发疾病"""
        diseases = []
        
        # 根据五运预测
        wuyun = wuyun_info.get("运", "")
        yunshi = wuyun_info.get("运势", "")
        wuyun_key = f"{wuyun}{yunshi}"
        
        if wuyun_key in YUNQI_DISEASE_MAP:
            wuyun_diseases = YUNQI_DISEASE_MAP[wuyun_key]["易发疾病"]
            diseases.extend(wuyun_diseases)
        
        # 根据当前气预测
        keqi = current_qi_info.get("客气", "")
        keqi_info = LIUQI_DATA.get(keqi, {})
        
        if keqi_info.get("太过"):
            taiguo_key = keqi_info["太过"]
            if taiguo_key in LIUQI_DISEASE_MAP:
                qi_diseases = LIUQI_DISEASE_MAP[taiguo_key]["易发疾病"]
                diseases.extend(qi_diseases)
        
        # 去重并限制数量
        unique_diseases = list(set(diseases))[:6]
        
        return {
            "易发疾病": unique_diseases,
            "主要原因": [
                f"{wuyun}{yunshi}",
                f"{keqi}当令"
            ],
            "风险等级": self._assess_disease_risk(yunqi_relation, len(unique_diseases)),
            "重点防护": unique_diseases[:3] if unique_diseases else []
        }
    
    def _generate_health_advice(self, wuyun_info: Dict, current_qi_info: Dict, disease_prediction: Dict) -> Dict:
        """生成调养建议"""
        advice = {
            "饮食调养": [],
            "起居调养": [],
            "情志调养": [],
            "运动调养": [],
            "预防措施": []
        }
        
        # 根据五运调养
        wuyun = wuyun_info.get("运", "")
        yunshi = wuyun_info.get("运势", "")
        wuyun_key = f"{wuyun}{yunshi}"
        
        if wuyun_key in YUNQI_DISEASE_MAP:
            wuyun_advice = YUNQI_DISEASE_MAP[wuyun_key]
            advice["预防措施"].extend(wuyun_advice.get("预防方法", []))
        
        # 根据当前气调养
        keqi = current_qi_info.get("客气", "")
        keqi_info = LIUQI_DATA.get(keqi, {})
        
        if keqi_info:
            wuxing = keqi_info.get("五行", "")
            advice["饮食调养"].append(f"适宜{wuxing}行食物")
            advice["起居调养"].append(f"顺应{keqi_info.get('季节', '')}特点")
        
        # 通用建议
        advice["情志调养"].extend(["保持心情舒畅", "避免情绪波动"])
        advice["运动调养"].extend(["适度运动", "顺应时令"])
        
        return advice
    
    def _summarize_period_characteristics(self, wuyun_info: Dict, sitian_info: Dict, current_qi_info: Dict) -> str:
        """总结时期特点"""
        wuyun = wuyun_info.get("运", "")
        yunshi = wuyun_info.get("运势", "")
        sitian = sitian_info.get("司天", "")
        current_qi = current_qi_info.get("当前气", "")
        
        return f"本年{wuyun}{yunshi}，{sitian}司天，当前{current_qi}，宜顺应天时，注意调养"
    
    def _assess_disease_risk(self, yunqi_relation: Dict, disease_count: int) -> str:
        """评估疾病风险等级"""
        influence = yunqi_relation.get("影响程度", "中等")
        
        if influence == "强" and disease_count >= 4:
            return "高"
        elif disease_count >= 3:
            return "中"
        else:
            return "低"
    
    def get_yearly_prediction(self, year: int) -> Dict:
        """
        获取全年运气预测
        
        Args:
            year: 年份
            
        Returns:
            全年运气预测
        """
        # 获取年运
        wuyun_info = self.get_wuyun(year)
        sitian_info = self.get_sitian_zaiquan(year)
        
        # 分析各个时期
        periods = []
        for qi_name, qi_info in ZHUKE_QI_TIME.items():
            # 模拟该时期的日期
            month = qi_info["月份"][0]
            period_date = datetime(year, month, 15)
            
            period_analysis = self.analyze_current_period(period_date)
            periods.append({
                "时期": qi_name,
                "时间": qi_info["时间"],
                "特点": period_analysis["总体特点"],
                "易发疾病": period_analysis["疾病预测"]["易发疾病"][:3],
                "调养重点": period_analysis["调养建议"]["预防措施"][:2]
            })
        
        return {
            "年份": year,
            "年运总览": {
                "五运": wuyun_info,
                "司天在泉": sitian_info
            },
            "分期预测": periods,
            "全年建议": self._generate_yearly_advice(wuyun_info, sitian_info),
            "重点关注": self._get_yearly_focus(wuyun_info, sitian_info)
        }
    
    def _generate_yearly_advice(self, wuyun_info: Dict, sitian_info: Dict) -> List[str]:
        """生成全年建议"""
        advice = []
        
        wuyun = wuyun_info.get("运", "")
        yunshi = wuyun_info.get("运势", "")
        
        if yunshi == "太过":
            advice.append(f"本年{wuyun}太过，宜适度泄耗")
        elif yunshi == "不及":
            advice.append(f"本年{wuyun}不及，宜适当补益")
        
        advice.extend([
            "顺应四时变化，调整生活作息",
            "注意饮食调养，避免偏食",
            "保持情志平和，适度运动",
            "定期体检，预防疾病"
        ])
        
        return advice
    
    def _get_yearly_focus(self, wuyun_info: Dict, sitian_info: Dict) -> List[str]:
        """获取全年关注重点"""
        focus = []
        
        # 根据五运确定重点脏腑
        zangfu = wuyun_info.get("脏腑", "")
        if zangfu:
            focus.append(f"重点保养{zangfu}")
        
        # 根据司天确定重点
        sitian = sitian_info.get("司天", "")
        sitian_zangfu = LIUQI_DATA.get(sitian, {}).get("脏腑", "")
        if sitian_zangfu:
            focus.append(f"注意{sitian_zangfu}调理")
        
        focus.extend([
            "防范运气相关疾病",
            "适应气候变化",
            "调整生活方式"
        ])
        
        return focus 