"""
子午流注计算器
索克生活 - 传统中医算诊微服务
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ZiwuLiuzhuCalculator:
    """子午流注计算器"""

    def __init__(self):
        """初始化子午流注计算器"""
        self.meridian_schedule = {
            3: {"经络": "肺经", "时辰": "寅时", "养生": "深度睡眠，养肺润燥"},
            5: {"经络": "大肠经", "时辰": "卯时", "养生": "排便时间，清肠排毒"},
            7: {"经络": "胃经", "时辰": "辰时", "养生": "早餐时间，健脾养胃"},
            9: {"经络": "脾经", "时辰": "巳时", "养生": "工作学习，健脾益气"},
            11: {"经络": "心经", "时辰": "午时", "养生": "午休时间，养心安神"},
            13: {"经络": "小肠经", "时辰": "未时", "养生": "午餐消化，分清浊"},
            15: {"经络": "膀胱经", "时辰": "申时", "养生": "多饮水，利水排毒"},
            17: {"经络": "肾经", "时辰": "酉时", "养生": "补肾时间，固精养元"},
            19: {"经络": "心包经", "时辰": "戌时", "养生": "晚餐时间，护心包"},
            21: {"经络": "三焦经", "时辰": "亥时", "养生": "准备睡眠，调三焦"},
            23: {"经络": "胆经", "时辰": "子时", "养生": "深度睡眠，养胆气"},
            1: {"经络": "肝经", "时辰": "丑时", "养生": "肝脏排毒，深度睡眠"},
        }

    def analyze_current_time(self, current_time: datetime) -> dict[str, Any]:
        """分析当前时间的子午流注"""
        try:
            hour = current_time.hour

            # 找到对应的经络
            meridian_hour = None
            for h in sorted(self.meridian_schedule.keys()):
                if hour >= h:
                    meridian_hour = h
                else:
                    break

            if meridian_hour is None:
                meridian_hour = 23  # 默认为子时

            current_meridian = self.meridian_schedule[meridian_hour]

            # 获取下一个经络
            next_hours = [h for h in sorted(self.meridian_schedule.keys()) if h > hour]
            if next_hours:
                next_hour = next_hours[0]
            else:
                next_hour = sorted(self.meridian_schedule.keys())[0]
            next_meridian = self.meridian_schedule[next_hour]

            result = {
                "当前时间": current_time.strftime("%Y-%m-%d %H:%M"),
                "当前经络": current_meridian["经络"],
                "当前时辰": current_meridian["时辰"],
                "养生建议": current_meridian["养生"],
                "下一经络": {
                    "经络": next_meridian["经络"],
                    "时间": f"{next_hour}:00",
                    "建议": next_meridian["养生"],
                },
                "最佳治疗时间": self._get_treatment_times(current_meridian["经络"]),
                "注意事项": self._get_precautions(current_meridian["经络"]),
            }

            logger.info(f"子午流注分析完成: {current_meridian['经络']}")
            return result

        except Exception as e:
            logger.error(f"子午流注分析失败: {e}")
            raise

    def _get_treatment_times(self, meridian: str) -> list:
        """获取最佳治疗时间"""
        treatment_map = {
            "肺经": ["3-5时", "15-17时"],
            "大肠经": ["5-7时", "17-19时"],
            "胃经": ["7-9时", "19-21时"],
            "脾经": ["9-11时", "21-23时"],
            "心经": ["11-13时", "23-1时"],
            "小肠经": ["13-15时", "1-3时"],
            "膀胱经": ["15-17时", "3-5时"],
            "肾经": ["17-19时", "5-7时"],
            "心包经": ["19-21时", "7-9时"],
            "三焦经": ["21-23时", "9-11时"],
            "胆经": ["23-1时", "11-13时"],
            "肝经": ["1-3时", "13-15时"],
        }
        return treatment_map.get(meridian, ["当前时间"])

    def _get_precautions(self, meridian: str) -> list:
        """获取注意事项"""
        precaution_map = {
            "肺经": ["保持室内空气清新", "避免吸烟", "深呼吸练习"],
            "大肠经": ["保持排便规律", "多饮温水", "腹部按摩"],
            "胃经": ["按时进餐", "细嚼慢咽", "避免暴饮暴食"],
            "脾经": ["避免思虑过度", "适度运动", "保持心情愉悦"],
            "心经": ["保持心情平静", "避免情绪激动", "适当休息"],
            "小肠经": ["注意营养吸收", "避免生冷食物", "腹部保暖"],
            "膀胱经": ["多饮水", "避免憋尿", "注意腰部保暖"],
            "肾经": ["避免过度劳累", "保持充足睡眠", "腰部保暖"],
            "心包经": ["保护心脏", "避免剧烈运动", "情志调节"],
            "三焦经": ["调节水液代谢", "保持体温", "避免寒凉"],
            "胆经": ["保证充足睡眠", "避免熬夜", "侧卧位睡眠"],
            "肝经": ["避免愤怒", "保持心情舒畅", "适度运动"],
        }
        return precaution_map.get(meridian, ["保持健康生活方式"])
