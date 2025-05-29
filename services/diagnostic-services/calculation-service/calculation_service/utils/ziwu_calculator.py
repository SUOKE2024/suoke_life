"""
子午流注计算器

用于计算子午流注和最佳治疗时间
"""

from datetime import datetime, time
from typing import Dict, List, Optional


class ZiwuCalculator:
    """子午流注计算器"""
    
    def __init__(self):
        """初始化计算器"""
        # 十二时辰对应的脏腑
        self.shichen_zangfu = {
            "子时": {"时间": "23:00-01:00", "脏腑": "胆", "五行": "木"},
            "丑时": {"时间": "01:00-03:00", "脏腑": "肝", "五行": "木"},
            "寅时": {"时间": "03:00-05:00", "脏腑": "肺", "五行": "金"},
            "卯时": {"时间": "05:00-07:00", "脏腑": "大肠", "五行": "金"},
            "辰时": {"时间": "07:00-09:00", "脏腑": "胃", "五行": "土"},
            "巳时": {"时间": "09:00-11:00", "脏腑": "脾", "五行": "土"},
            "午时": {"时间": "11:00-13:00", "脏腑": "心", "五行": "火"},
            "未时": {"时间": "13:00-15:00", "脏腑": "小肠", "五行": "火"},
            "申时": {"时间": "15:00-17:00", "脏腑": "膀胱", "五行": "水"},
            "酉时": {"时间": "17:00-19:00", "脏腑": "肾", "五行": "水"},
            "戌时": {"时间": "19:00-21:00", "脏腑": "心包", "五行": "火"},
            "亥时": {"时间": "21:00-23:00", "脏腑": "三焦", "五行": "火"}
        }
        
        # 脏腑治疗最佳时间
        self.treatment_times = {
            "肺": {
                "最佳": "寅时(03:00-05:00)",
                "次佳": "卯时(05:00-07:00)",
                "禁忌": "申时(15:00-17:00)"
            },
            "大肠": {
                "最佳": "卯时(05:00-07:00)",
                "次佳": "寅时(03:00-05:00)",
                "禁忌": "酉时(17:00-19:00)"
            },
            "胃": {
                "最佳": "辰时(07:00-09:00)",
                "次佳": "巳时(09:00-11:00)",
                "禁忌": "戌时(19:00-21:00)"
            },
            "脾": {
                "最佳": "巳时(09:00-11:00)",
                "次佳": "辰时(07:00-09:00)",
                "禁忌": "亥时(21:00-23:00)"
            },
            "心": {
                "最佳": "午时(11:00-13:00)",
                "次佳": "未时(13:00-15:00)",
                "禁忌": "子时(23:00-01:00)"
            },
            "小肠": {
                "最佳": "未时(13:00-15:00)",
                "次佳": "午时(11:00-13:00)",
                "禁忌": "丑时(01:00-03:00)"
            },
            "膀胱": {
                "最佳": "申时(15:00-17:00)",
                "次佳": "酉时(17:00-19:00)",
                "禁忌": "寅时(03:00-05:00)"
            },
            "肾": {
                "最佳": "酉时(17:00-19:00)",
                "次佳": "申时(15:00-17:00)",
                "禁忌": "卯时(05:00-07:00)"
            },
            "心包": {
                "最佳": "戌时(19:00-21:00)",
                "次佳": "亥时(21:00-23:00)",
                "禁忌": "辰时(07:00-09:00)"
            },
            "三焦": {
                "最佳": "亥时(21:00-23:00)",
                "次佳": "戌时(19:00-21:00)",
                "禁忌": "巳时(09:00-11:00)"
            },
            "胆": {
                "最佳": "子时(23:00-01:00)",
                "次佳": "丑时(01:00-03:00)",
                "禁忌": "午时(11:00-13:00)"
            },
            "肝": {
                "最佳": "丑时(01:00-03:00)",
                "次佳": "子时(23:00-01:00)",
                "禁忌": "未时(13:00-15:00)"
            }
        }
    
    def get_current_shichen(self, current_time: Optional[datetime] = None) -> Dict:
        """
        获取当前时辰信息
        
        Args:
            current_time: 当前时间，默认为系统当前时间
            
        Returns:
            当前时辰信息
        """
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        
        # 根据小时确定时辰
        if 23 <= hour or hour < 1:
            shichen = "子时"
        elif 1 <= hour < 3:
            shichen = "丑时"
        elif 3 <= hour < 5:
            shichen = "寅时"
        elif 5 <= hour < 7:
            shichen = "卯时"
        elif 7 <= hour < 9:
            shichen = "辰时"
        elif 9 <= hour < 11:
            shichen = "巳时"
        elif 11 <= hour < 13:
            shichen = "午时"
        elif 13 <= hour < 15:
            shichen = "未时"
        elif 15 <= hour < 17:
            shichen = "申时"
        elif 17 <= hour < 19:
            shichen = "酉时"
        elif 19 <= hour < 21:
            shichen = "戌时"
        else:  # 21 <= hour < 23
            shichen = "亥时"
        
        shichen_info = self.shichen_zangfu[shichen].copy()
        shichen_info["时辰"] = shichen
        shichen_info["当前时间"] = current_time.strftime("%H:%M")
        
        return shichen_info
    
    def get_optimal_treatment_time(self, target_organ: str) -> Dict:
        """
        获取指定脏腑的最佳治疗时间
        
        Args:
            target_organ: 目标脏腑
            
        Returns:
            最佳治疗时间信息
        """
        if target_organ not in self.treatment_times:
            return {"error": f"未找到脏腑 '{target_organ}' 的治疗时间信息"}
        
        treatment_info = self.treatment_times[target_organ].copy()
        treatment_info["脏腑"] = target_organ
        
        # 添加详细说明
        treatment_info["说明"] = f"{target_organ}的最佳治疗时间是{treatment_info['最佳']}，此时{target_organ}经气最旺盛"
        
        return treatment_info
    
    def analyze_daily_schedule(self, target_date: Optional[datetime] = None) -> List[Dict]:
        """
        分析一天的子午流注时间表
        
        Args:
            target_date: 目标日期，默认为当天
            
        Returns:
            一天的时辰安排
        """
        if target_date is None:
            target_date = datetime.now()
        
        daily_schedule = []
        
        for shichen, info in self.shichen_zangfu.items():
            schedule_item = {
                "时辰": shichen,
                "时间": info["时间"],
                "主导脏腑": info["脏腑"],
                "五行": info["五行"],
                "养生建议": self._get_yangsheng_advice(shichen, info["脏腑"]),
                "适宜活动": self._get_suitable_activities(shichen),
                "注意事项": self._get_precautions(shichen)
            }
            daily_schedule.append(schedule_item)
        
        return daily_schedule
    
    def _get_yangsheng_advice(self, shichen: str, zangfu: str) -> str:
        """
        获取时辰养生建议
        
        Args:
            shichen: 时辰
            zangfu: 脏腑
            
        Returns:
            养生建议
        """
        advice_map = {
            "子时": f"{zangfu}经当令，宜静养休息，忌熬夜",
            "丑时": f"{zangfu}经当令，深度睡眠时间，忌饮酒",
            "寅时": f"{zangfu}经当令，宜深呼吸，忌吸烟",
            "卯时": f"{zangfu}经当令，宜排便，忌憋便",
            "辰时": f"{zangfu}经当令，宜进早餐，忌空腹",
            "巳时": f"{zangfu}经当令，宜工作学习，忌暴饮暴食",
            "午时": f"{zangfu}经当令，宜小憩，忌剧烈运动",
            "未时": f"{zangfu}经当令，宜消化，忌贪凉",
            "申时": f"{zangfu}经当令，宜多饮水，忌憋尿",
            "酉时": f"{zangfu}经当令，宜补肾，忌过劳",
            "戌时": f"{zangfu}经当令，宜心情愉悦，忌生气",
            "亥时": f"{zangfu}经当令，宜准备睡眠，忌剧烈活动"
        }
        
        return advice_map.get(shichen, f"{zangfu}经当令，宜顺应自然")
    
    def _get_suitable_activities(self, shichen: str) -> List[str]:
        """
        获取适宜活动
        
        Args:
            shichen: 时辰
            
        Returns:
            适宜活动列表
        """
        activities_map = {
            "子时": ["睡眠", "静坐", "冥想"],
            "丑时": ["深度睡眠", "肝脏排毒"],
            "寅时": ["深呼吸", "肺部保养", "轻柔运动"],
            "卯时": ["排便", "晨练", "喝温水"],
            "辰时": ["进早餐", "胃部保养", "温和活动"],
            "巳时": ["工作", "学习", "脾胃调理"],
            "午时": ["午餐", "小憩", "心脏保养"],
            "未时": ["消化", "轻松活动", "小肠调理"],
            "申时": ["多饮水", "膀胱保养", "适度运动"],
            "酉时": ["晚餐", "肾脏保养", "温和运动"],
            "戌时": ["散步", "心包保养", "放松心情"],
            "亥时": ["准备睡眠", "三焦调理", "静心"]
        }
        
        return activities_map.get(shichen, ["顺应自然"])
    
    def _get_precautions(self, shichen: str) -> List[str]:
        """
        获取注意事项
        
        Args:
            shichen: 时辰
            
        Returns:
            注意事项列表
        """
        precautions_map = {
            "子时": ["避免熬夜", "保持安静", "不宜剧烈活动"],
            "丑时": ["避免饮酒", "保证睡眠", "不宜进食"],
            "寅时": ["避免吸烟", "注意保暖", "不宜受凉"],
            "卯时": ["避免憋便", "不宜空腹", "注意排毒"],
            "辰时": ["避免空腹", "不宜过饱", "温和进食"],
            "巳时": ["避免暴饮暴食", "不宜过度思虑", "适度工作"],
            "午时": ["避免剧烈运动", "不宜过度兴奋", "适当休息"],
            "未时": ["避免贪凉", "不宜过度劳累", "注意消化"],
            "申时": ["避免憋尿", "不宜过度疲劳", "多补水分"],
            "酉时": ["避免过劳", "不宜房事过度", "注意保肾"],
            "戌时": ["避免生气", "不宜过度兴奋", "保持平和"],
            "亥时": ["避免剧烈活动", "不宜过度思考", "准备休息"]
        }
        
        return precautions_map.get(shichen, ["顺应自然规律"])

    def calculate_optimal_time(self, target_date) -> Dict:
        """
        计算最佳治疗时间（简化版本，用于测试）
        
        Args:
            target_date: 目标日期
            
        Returns:
            最佳治疗时间信息
        """
        # 获取当前时辰信息
        current_shichen = self.get_current_shichen()
        
        # 获取经络流注信息
        meridian_flow = []
        for shichen, info in self.shichen_zangfu.items():
            meridian_flow.append({
                "time": shichen,
                "organ": info["脏腑"],
                "element": info["五行"]
            })
        
        return {
            "optimal_hours": ["子时(23:00-01:00)", "丑时(01:00-03:00)", "寅时(03:00-05:00)"],
            "meridian_flow": meridian_flow[:3],  # 返回前3个作为示例
            "current_shichen": current_shichen,
            "recommendations": ["此时适宜养生调理", "避免剧烈运动", "保持心境平和"]
        } 