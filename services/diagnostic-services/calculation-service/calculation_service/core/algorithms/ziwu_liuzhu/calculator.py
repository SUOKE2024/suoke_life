"""
子午流注计算器

实现子午流注时间医学的核心算法
"""

from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

from .data import (
    MERIDIAN_TIME_MAP,
    ACUPOINT_TIME_MAP, 
    SHICHEN_DIZHI_MAP,
    NAJIA_TIME_MAP,
    MERIDIAN_ORGAN_MAP,
    DISEASE_OPTIMAL_TIME
)

class ZiwuLiuzhuCalculator:
    """子午流注计算器"""
    
    def __init__(self):
        """初始化计算器"""
        self.tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        # 时辰对应的小时范围
        self.shichen_hours = {
            "子时": (23, 1), "丑时": (1, 3), "寅时": (3, 5), "卯时": (5, 7),
            "辰时": (7, 9), "巳时": (9, 11), "午时": (11, 13), "未时": (13, 15),
            "申时": (15, 17), "酉时": (17, 19), "戌时": (19, 21), "亥时": (21, 23)
        }
    
    def get_current_shichen(self, dt: Optional[datetime] = None) -> str:
        """
        获取当前时辰
        
        Args:
            dt: 指定时间，默认为当前时间
            
        Returns:
            时辰名称
        """
        if dt is None:
            dt = datetime.now()
        
        hour = dt.hour
        
        # 根据小时确定时辰
        if hour >= 23 or hour < 1:
            return "子时"
        elif 1 <= hour < 3:
            return "丑时"
        elif 3 <= hour < 5:
            return "寅时"
        elif 5 <= hour < 7:
            return "卯时"
        elif 7 <= hour < 9:
            return "辰时"
        elif 9 <= hour < 11:
            return "巳时"
        elif 11 <= hour < 13:
            return "午时"
        elif 13 <= hour < 15:
            return "未时"
        elif 15 <= hour < 17:
            return "申时"
        elif 17 <= hour < 19:
            return "酉时"
        elif 19 <= hour < 21:
            return "戌时"
        else:  # 21 <= hour < 23
            return "亥时"
    
    def get_current_meridian(self, dt: Optional[datetime] = None) -> Dict:
        """
        获取当前时辰对应的经络
        
        Args:
            dt: 指定时间，默认为当前时间
            
        Returns:
            经络信息
        """
        shichen = self.get_current_shichen(dt)
        
        # 根据时辰找到对应的经络
        for meridian, info in MERIDIAN_TIME_MAP.items():
            if info["时辰"] == shichen:
                return {
                    "经络": meridian,
                    "时辰": shichen,
                    "时间": info["时间"],
                    "气血状态": info["气血"],
                    "主治疾病": info["主治"],
                    "最佳针灸时间": info["最佳针灸时间"],
                    "禁忌时间": info["禁忌时间"],
                    "脏腑信息": MERIDIAN_ORGAN_MAP.get(meridian, {})
                }
        
        return {"经络": "未知", "时辰": shichen}
    
    def get_optimal_treatment_time(self, disease: str) -> Dict:
        """
        获取疾病的最佳治疗时间
        
        Args:
            disease: 疾病名称
            
        Returns:
            最佳治疗时间信息
        """
        if disease in DISEASE_OPTIMAL_TIME:
            disease_info = DISEASE_OPTIMAL_TIME[disease]
            meridian = disease_info["经络"]
            meridian_info = MERIDIAN_TIME_MAP.get(meridian, {})
            
            return {
                "疾病": disease,
                "最佳治疗时间": disease_info["最佳时间"],
                "对应经络": meridian,
                "治疗原理": disease_info["原理"],
                "具体时间": meridian_info.get("时间", ""),
                "主治方法": meridian_info.get("主治", []),
                "注意事项": f"避免在{meridian_info.get('禁忌时间', '')}治疗"
            }
        
        # 如果没有找到特定疾病，尝试模糊匹配
        for key, value in DISEASE_OPTIMAL_TIME.items():
            if disease in key or key in disease:
                return self.get_optimal_treatment_time(key)
        
        return {"疾病": disease, "建议": "请咨询专业医师确定最佳治疗时间"}
    
    def calculate_lingui_bafa(self, dt: Optional[datetime] = None) -> Dict:
        """
        计算灵龟八法穴位开合
        
        Args:
            dt: 指定时间，默认为当前时间
            
        Returns:
            灵龟八法分析结果
        """
        if dt is None:
            dt = datetime.now()
        
        shichen = self.get_current_shichen(dt)
        
        # 查找当前时辰开放的穴位
        open_acupoints = []
        for acupoint, info in ACUPOINT_TIME_MAP.items():
            if shichen in info["开穴时间"]:
                open_acupoints.append({
                    "穴位": acupoint,
                    "配穴": info["配穴"],
                    "主治": info["主治"],
                    "对应奇经": info["八脉"],
                    "最佳时间": info["最佳时间"]
                })
        
        return {
            "当前时辰": shichen,
            "开放穴位": open_acupoints,
            "建议": "选择开放穴位进行针灸治疗，效果更佳" if open_acupoints else "当前时辰无特殊开放穴位"
        }
    
    def calculate_najia_time(self, dt: Optional[datetime] = None) -> Dict:
        """
        计算纳甲法时间
        
        Args:
            dt: 指定时间，默认为当前时间
            
        Returns:
            纳甲法分析结果
        """
        if dt is None:
            dt = datetime.now()
        
        # 获取日干
        day_tiangan = self.get_day_tiangan(dt)
        
        if day_tiangan in NAJIA_TIME_MAP:
            najia_info = NAJIA_TIME_MAP[day_tiangan]
            current_shichen = self.get_current_shichen(dt)
            
            # 判断当前是开时还是阖时
            is_open_time = current_shichen == najia_info["开"]
            is_close_time = current_shichen == najia_info["阖"]
            
            return {
                "日干": day_tiangan,
                "开时": najia_info["开"],
                "阖时": najia_info["阖"],
                "当前时辰": current_shichen,
                "当前状态": "开时" if is_open_time else "阖时" if is_close_time else "平时",
                "建议": self._get_najia_advice(is_open_time, is_close_time)
            }
        
        return {"日干": day_tiangan, "建议": "纳甲法数据不完整"}
    
    def get_day_tiangan(self, dt: datetime) -> str:
        """
        获取日干
        
        Args:
            dt: 日期时间
            
        Returns:
            日干
        """
        # 以1984年1月1日甲子日为基准
        base_date = datetime(1984, 1, 1)
        days_diff = (dt.date() - base_date.date()).days
        
        tiangan_index = days_diff % 10
        return self.tiangan[tiangan_index]
    
    def _get_najia_advice(self, is_open: bool, is_close: bool) -> str:
        """
        获取纳甲法建议
        
        Args:
            is_open: 是否为开时
            is_close: 是否为阖时
            
        Returns:
            建议内容
        """
        if is_open:
            return "开时宜补益、温阳、开窍类治疗"
        elif is_close:
            return "阖时宜清热、泻实、安神类治疗"
        else:
            return "平时可进行常规治疗"
    
    def analyze_daily_meridian_flow(self, date_obj: Optional[datetime] = None) -> List[Dict]:
        """
        分析一日经络流注
        
        Args:
            date_obj: 指定日期，默认为当前日期
            
        Returns:
            一日经络流注分析
        """
        if date_obj is None:
            date_obj = datetime.now()
        
        daily_flow = []
        
        # 按时辰顺序排列经络
        shichen_order = ["子时", "丑时", "寅时", "卯时", "辰时", "巳时", 
                        "午时", "未时", "申时", "酉时", "戌时", "亥时"]
        
        for shichen in shichen_order:
            # 找到对应的经络
            for meridian, info in MERIDIAN_TIME_MAP.items():
                if info["时辰"] == shichen:
                    # 计算具体时间
                    start_hour, end_hour = self.shichen_hours[shichen]
                    if start_hour > end_hour:  # 跨日情况（如子时）
                        if shichen == "子时":
                            start_time = time(23, 0)
                            end_time = time(1, 0)
                        else:
                            start_time = time(start_hour, 0)
                            end_time = time(end_hour, 0)
                    else:
                        start_time = time(start_hour, 0)
                        end_time = time(end_hour, 0)
                    
                    daily_flow.append({
                        "时辰": shichen,
                        "时间": f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
                        "经络": meridian,
                        "脏腑": MERIDIAN_ORGAN_MAP.get(meridian, {}).get("脏腑", ""),
                        "五行": MERIDIAN_ORGAN_MAP.get(meridian, {}).get("五行", ""),
                        "气血状态": info["气血"],
                        "主治": info["主治"],
                        "养生建议": self._get_meridian_health_advice(meridian, shichen)
                    })
                    break
        
        return daily_flow
    
    def _get_meridian_health_advice(self, meridian: str, shichen: str) -> str:
        """
        获取经络养生建议
        
        Args:
            meridian: 经络名称
            shichen: 时辰
            
        Returns:
            养生建议
        """
        advice_map = {
            "肺经": "深呼吸，适宜晨练，注意保暖",
            "大肠经": "排便最佳时间，多喝温水",
            "胃经": "早餐时间，宜温热易消化食物",
            "脾经": "思考学习最佳时间，避免过度思虑",
            "心经": "午休时间，静心养神",
            "小肠经": "消化吸收时间，适量饮水",
            "膀胱经": "工作学习时间，注意用眼卫生",
            "肾经": "晚餐时间，宜清淡，避免过咸",
            "心包经": "放松时间，适宜散步聊天",
            "三焦经": "准备睡眠，避免剧烈运动",
            "胆经": "深度睡眠时间，保证充足睡眠",
            "肝经": "肝脏排毒时间，深度睡眠最重要"
        }
        
        return advice_map.get(meridian, "遵循自然规律，顺应时辰养生")
    
    def get_treatment_recommendation(self, symptoms: List[str], dt: Optional[datetime] = None) -> Dict:
        """
        根据症状和时间推荐治疗方案
        
        Args:
            symptoms: 症状列表
            dt: 指定时间，默认为当前时间
            
        Returns:
            治疗推荐
        """
        if dt is None:
            dt = datetime.now()
        
        current_meridian = self.get_current_meridian(dt)
        current_shichen = self.get_current_shichen(dt)
        
        recommendations = []
        
        # 分析每个症状
        for symptom in symptoms:
            # 查找最佳治疗时间
            optimal_time = self.get_optimal_treatment_time(symptom)
            
            # 检查当前时间是否适合治疗该症状
            is_optimal_now = False
            if "最佳治疗时间" in optimal_time:
                is_optimal_now = optimal_time["最佳治疗时间"] == current_shichen
            
            # 检查当前经络是否能治疗该症状
            can_treat_now = symptom in current_meridian.get("主治疾病", [])
            
            recommendation = {
                "症状": symptom,
                "当前时间适宜度": "最佳" if is_optimal_now else "适宜" if can_treat_now else "一般",
                "最佳治疗时间": optimal_time.get("最佳治疗时间", ""),
                "对应经络": optimal_time.get("对应经络", ""),
                "治疗原理": optimal_time.get("治疗原理", ""),
                "当前建议": self._get_current_treatment_advice(symptom, is_optimal_now, can_treat_now)
            }
            
            recommendations.append(recommendation)
        
        # 灵龟八法推荐
        lingui_info = self.calculate_lingui_bafa(dt)
        
        return {
            "分析时间": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "当前时辰": current_shichen,
            "当前经络": current_meridian["经络"],
            "症状分析": recommendations,
            "灵龟八法": lingui_info,
            "综合建议": self._generate_comprehensive_advice(recommendations, current_meridian)
        }
    
    def _get_current_treatment_advice(self, symptom: str, is_optimal: bool, can_treat: bool) -> str:
        """
        获取当前治疗建议
        
        Args:
            symptom: 症状
            is_optimal: 是否为最佳时间
            can_treat: 当前经络是否能治疗
            
        Returns:
            治疗建议
        """
        if is_optimal:
            return f"当前是治疗{symptom}的最佳时间，建议立即治疗"
        elif can_treat:
            return f"当前经络可以治疗{symptom}，效果良好"
        else:
            return f"建议等待最佳治疗时间，或选择其他治疗方法"
    
    def _generate_comprehensive_advice(self, recommendations: List[Dict], current_meridian: Dict) -> str:
        """
        生成综合建议
        
        Args:
            recommendations: 推荐列表
            current_meridian: 当前经络信息
            
        Returns:
            综合建议
        """
        optimal_count = sum(1 for r in recommendations if r["当前时间适宜度"] == "最佳")
        suitable_count = sum(1 for r in recommendations if r["当前时间适宜度"] == "适宜")
        
        if optimal_count > 0:
            return f"当前时间是{optimal_count}个症状的最佳治疗时间，建议优先治疗"
        elif suitable_count > 0:
            return f"当前时间适宜治疗{suitable_count}个症状，可以进行相关治疗"
        else:
            return f"当前{current_meridian['经络']}当令，建议进行相关经络的保健养生" 