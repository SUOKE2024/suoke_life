"""
综合算诊计算器

整合五运六气、子午流注、八字体质分析、八卦配属等所有算诊算法
实现古中医"算"诊的完整功能
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json

from .wuyun_liuqi import WuyunLiuqiCalculator
from .ziwu_liuzhu import ZiwuLiuzhuCalculator
from .constitution import ConstitutionCalculator
from .bagua import BaguaCalculator


class ComprehensiveCalculationService:
    """综合算诊计算服务"""
    
    def __init__(self):
        """初始化所有计算器"""
        self.wuyun_calculator = WuyunLiuqiCalculator()
        self.ziwu_calculator = ZiwuLiuzhuCalculator()
        self.constitution_calculator = ConstitutionCalculator()
        self.bagua_calculator = BaguaCalculator()
    
    def comprehensive_diagnosis(
        self, 
        birth_datetime: datetime,
        current_datetime: datetime = None,
        gender: str = "male",
        location: Tuple[float, float] = None,
        symptoms: List[str] = None
    ) -> Dict[str, Any]:
        """
        综合算诊分析
        
        Args:
            birth_datetime: 出生时间
            current_datetime: 当前时间
            gender: 性别 ("male" 或 "female")
            location: 地理位置 (经度, 纬度)
            symptoms: 当前症状列表
            
        Returns:
            综合算诊分析结果
        """
        if current_datetime is None:
            current_datetime = datetime.now()
        
        if symptoms is None:
            symptoms = []
        
        # 1. 五运六气分析
        wuyun_analysis = self.wuyun_calculator.analyze_current_period(current_datetime)
        
        # 2. 子午流注分析
        ziwu_analysis = self.ziwu_calculator.get_optimal_treatment_time(
            current_datetime, symptoms
        )
        
        # 3. 八字体质分析
        constitution_analysis = self.constitution_calculator.analyze_constitution(
            birth_datetime
        )
        
        # 4. 八卦配属分析
        bagua_analysis = self.bagua_calculator.analyze_bagua_health(
            birth_datetime, current_datetime
        )
        
        # 5. 综合分析
        comprehensive_result = self._integrate_analysis(
            wuyun_analysis, ziwu_analysis, constitution_analysis, 
            bagua_analysis, birth_datetime, current_datetime, symptoms
        )
        
        return {
            "基本信息": {
                "出生时间": birth_datetime.strftime("%Y年%m月%d日 %H时%M分"),
                "当前时间": current_datetime.strftime("%Y年%m月%d日 %H时%M分"),
                "性别": "男" if gender == "male" else "女",
                "当前症状": symptoms
            },
            "五运六气分析": wuyun_analysis,
            "子午流注分析": ziwu_analysis,
            "八字体质分析": constitution_analysis,
            "八卦配属分析": bagua_analysis,
            "综合诊断": comprehensive_result,
            "算诊总结": self._generate_summary(comprehensive_result)
        }
    
    def _integrate_analysis(
        self,
        wuyun_analysis: Dict,
        ziwu_analysis: Dict,
        constitution_analysis: Dict,
        bagua_analysis: Dict,
        birth_datetime: datetime,
        current_datetime: datetime,
        symptoms: List[str]
    ) -> Dict[str, Any]:
        """整合各种分析结果"""
        
        # 提取关键信息
        constitution_type = constitution_analysis.get("体质类型", "")
        birth_bagua = bagua_analysis.get("本命卦", {}).get("卦名", "")
        current_bagua = bagua_analysis.get("当前卦", {}).get("卦名", "")
        
        # 综合健康风险评估
        health_risk = self._assess_comprehensive_health_risk(
            wuyun_analysis, constitution_analysis, bagua_analysis, symptoms
        )
        
        # 综合治疗建议
        treatment_advice = self._generate_comprehensive_treatment(
            wuyun_analysis, ziwu_analysis, constitution_analysis, bagua_analysis
        )
        
        # 时间医学建议
        time_medicine = self._generate_time_medicine_advice(
            ziwu_analysis, wuyun_analysis, current_datetime
        )
        
        # 个性化养生方案
        personalized_plan = self._generate_personalized_plan(
            constitution_analysis, bagua_analysis, wuyun_analysis
        )
        
        # 预防保健建议
        prevention_advice = self._generate_prevention_advice(
            constitution_analysis, bagua_analysis, wuyun_analysis, symptoms
        )
        
        return {
            "健康风险评估": health_risk,
            "综合治疗建议": treatment_advice,
            "时间医学指导": time_medicine,
            "个性化养生方案": personalized_plan,
            "预防保健建议": prevention_advice,
            "调理优先级": self._determine_treatment_priority(
                health_risk, symptoms, constitution_type
            )
        }
    
    def _assess_comprehensive_health_risk(
        self,
        wuyun_analysis: Dict,
        constitution_analysis: Dict,
        bagua_analysis: Dict,
        symptoms: List[str]
    ) -> Dict[str, Any]:
        """综合健康风险评估"""
        
        risk_factors = []
        risk_level = "低"
        
        # 体质风险
        constitution_diseases = constitution_analysis.get("易患疾病", [])
        if constitution_diseases:
            risk_factors.append(f"体质易患：{', '.join(constitution_diseases[:3])}")
        
        # 八卦风险
        bagua_prediction = bagua_analysis.get("健康预测", {})
        bagua_risk = bagua_prediction.get("风险等级", "低")
        if bagua_risk in ["高", "中"]:
            risk_level = bagua_risk
            bagua_diseases = bagua_prediction.get("易发疾病", [])
            if bagua_diseases:
                risk_factors.append(f"八卦预测：{', '.join(bagua_diseases[:3])}")
        
        # 当前症状风险
        if symptoms:
            risk_factors.append(f"当前症状：{', '.join(symptoms)}")
            if len(symptoms) >= 3:
                risk_level = "中" if risk_level == "低" else "高"
        
        # 五运六气影响
        wuyun_diseases = wuyun_analysis.get("易发疾病", [])
        if wuyun_diseases:
            risk_factors.append(f"运气影响：{', '.join(wuyun_diseases[:2])}")
        
        return {
            "风险等级": risk_level,
            "风险因素": risk_factors,
            "重点关注": self._get_priority_concerns(
                constitution_analysis, bagua_analysis, symptoms
            ),
            "风险评分": self._calculate_risk_score(risk_level, len(risk_factors), len(symptoms))
        }
    
    def _generate_comprehensive_treatment(
        self,
        wuyun_analysis: Dict,
        ziwu_analysis: Dict,
        constitution_analysis: Dict,
        bagua_analysis: Dict
    ) -> Dict[str, Any]:
        """生成综合治疗建议"""
        
        # 中药方剂建议
        herbal_formulas = []
        constitution_formulas = constitution_analysis.get("调理方案", {}).get("中药方剂", [])
        herbal_formulas.extend(constitution_formulas[:2])
        
        # 针灸穴位建议
        acupoints = []
        constitution_points = constitution_analysis.get("调理方案", {}).get("针灸穴位", [])
        bagua_points = bagua_analysis.get("养生建议", {}).get("本命卦养生", {}).get("针灸穴位", [])
        acupoints.extend(constitution_points[:3])
        if bagua_points:
            acupoints.extend(bagua_points[:2])
        
        # 最佳治疗时间
        optimal_times = ziwu_analysis.get("最佳治疗时间", [])
        
        # 推拿按摩
        massage_methods = constitution_analysis.get("调理方案", {}).get("推拿手法", [])
        
        return {
            "中药方剂": list(set(herbal_formulas)),
            "针灸穴位": list(set(acupoints)),
            "最佳治疗时间": optimal_times,
            "推拿按摩": massage_methods,
            "治疗原则": self._get_treatment_principles(constitution_analysis, bagua_analysis),
            "疗程建议": self._get_treatment_course_advice(constitution_analysis)
        }
    
    def _generate_time_medicine_advice(
        self,
        ziwu_analysis: Dict,
        wuyun_analysis: Dict,
        current_datetime: datetime
    ) -> Dict[str, Any]:
        """生成时间医学建议"""
        
        current_hour = current_datetime.hour
        current_month = current_datetime.month
        
        # 当前时辰建议
        current_meridian = ziwu_analysis.get("当前经络", {})
        
        # 今日最佳时间
        today_optimal = ziwu_analysis.get("今日最佳时间", [])
        
        # 本月运气特点
        monthly_qi = wuyun_analysis.get("当前月份特点", "")
        
        # 季节调养
        season_advice = wuyun_analysis.get("季节调养建议", [])
        
        return {
            "当前时辰": f"{current_hour}时 - {current_meridian.get('经络名称', '')}经当令",
            "当前宜忌": {
                "宜": current_meridian.get("适宜活动", []),
                "忌": current_meridian.get("禁忌活动", [])
            },
            "今日最佳时间": today_optimal,
            "本月特点": monthly_qi,
            "季节调养": season_advice,
            "下周预测": self._predict_next_week_optimal_times(current_datetime)
        }
    
    def _generate_personalized_plan(
        self,
        constitution_analysis: Dict,
        bagua_analysis: Dict,
        wuyun_analysis: Dict
    ) -> Dict[str, Any]:
        """生成个性化养生方案"""
        
        # 饮食建议
        diet_advice = self._integrate_diet_advice(constitution_analysis, bagua_analysis)
        
        # 运动建议
        exercise_advice = self._integrate_exercise_advice(constitution_analysis, bagua_analysis)
        
        # 情志调养
        emotion_advice = self._integrate_emotion_advice(constitution_analysis, bagua_analysis)
        
        # 起居建议
        lifestyle_advice = self._integrate_lifestyle_advice(constitution_analysis, bagua_analysis)
        
        # 方位调理
        direction_advice = bagua_analysis.get("方位调理", {})
        
        return {
            "饮食调养": diet_advice,
            "运动锻炼": exercise_advice,
            "情志调养": emotion_advice,
            "起居作息": lifestyle_advice,
            "方位调理": direction_advice,
            "个性化重点": constitution_analysis.get("个性化建议", [])
        }
    
    def _generate_prevention_advice(
        self,
        constitution_analysis: Dict,
        bagua_analysis: Dict,
        wuyun_analysis: Dict,
        symptoms: List[str]
    ) -> Dict[str, Any]:
        """生成预防保健建议"""
        
        # 疾病预防
        disease_prevention = []
        
        # 体质相关预防
        constitution_diseases = constitution_analysis.get("易患疾病", [])
        constitution_prevention = constitution_analysis.get("疾病易感性", {}).get("预防重点", [])
        disease_prevention.extend(constitution_prevention)
        
        # 八卦相关预防
        bagua_prevention = bagua_analysis.get("健康预测", {}).get("预防建议", [])
        disease_prevention.extend(bagua_prevention)
        
        # 运气相关预防
        wuyun_prevention = wuyun_analysis.get("预防建议", [])
        disease_prevention.extend(wuyun_prevention)
        
        # 定期检查建议
        checkup_advice = self._generate_checkup_advice(constitution_analysis, bagua_analysis)
        
        # 生活方式建议
        lifestyle_prevention = self._generate_lifestyle_prevention(constitution_analysis)
        
        return {
            "疾病预防": list(set(disease_prevention)),
            "定期检查": checkup_advice,
            "生活方式": lifestyle_prevention,
            "预防重点": self._get_prevention_priorities(constitution_analysis, bagua_analysis),
            "健康监测": self._get_health_monitoring_advice(constitution_analysis, symptoms)
        }
    
    def _determine_treatment_priority(
        self,
        health_risk: Dict,
        symptoms: List[str],
        constitution_type: str
    ) -> List[Dict[str, str]]:
        """确定治疗优先级"""
        
        priorities = []
        
        risk_level = health_risk.get("风险等级", "低")
        
        if symptoms:
            priorities.append({
                "优先级": "紧急",
                "内容": "症状治疗",
                "说明": f"优先处理当前症状：{', '.join(symptoms[:3])}"
            })
        
        if risk_level == "高":
            priorities.append({
                "优先级": "高",
                "内容": "风险防控",
                "说明": "重点防控高风险疾病"
            })
        
        priorities.append({
            "优先级": "中",
            "内容": "体质调理",
            "说明": f"根据{constitution_type}进行体质调理"
        })
        
        priorities.append({
            "优先级": "低",
            "内容": "日常养生",
            "说明": "日常养生保健，预防疾病"
        })
        
        return priorities
    
    def _generate_summary(self, comprehensive_result: Dict) -> Dict[str, str]:
        """生成算诊总结"""
        
        health_risk = comprehensive_result.get("健康风险评估", {})
        risk_level = health_risk.get("风险等级", "低")
        
        # 总体评估
        if risk_level == "高":
            overall_assessment = "需要重点关注，建议及时调理"
        elif risk_level == "中":
            overall_assessment = "存在一定风险，建议适度调理"
        else:
            overall_assessment = "整体状况良好，注意日常养生"
        
        # 核心建议
        priorities = comprehensive_result.get("调理优先级", [])
        core_advice = priorities[0]["说明"] if priorities else "注意日常养生保健"
        
        # 时间建议
        time_advice = "遵循子午流注规律，选择最佳治疗时间"
        
        return {
            "总体评估": overall_assessment,
            "核心建议": core_advice,
            "时间指导": time_advice,
            "算诊特色": "融合五运六气、子午流注、八字体质、八卦配属的综合分析",
            "注意事项": "算诊结果仅供参考，具体治疗请咨询专业医师"
        }
    
    # 辅助方法
    def _get_priority_concerns(self, constitution_analysis: Dict, bagua_analysis: Dict, symptoms: List[str]) -> List[str]:
        """获取重点关注事项"""
        concerns = []
        if symptoms:
            concerns.extend(symptoms[:2])
        
        constitution_diseases = constitution_analysis.get("易患疾病", [])
        concerns.extend(constitution_diseases[:2])
        
        bagua_diseases = bagua_analysis.get("健康预测", {}).get("易发疾病", [])
        concerns.extend(bagua_diseases[:1])
        
        return list(set(concerns))[:5]
    
    def _calculate_risk_score(self, risk_level: str, risk_factors_count: int, symptoms_count: int) -> int:
        """计算风险评分（0-100）"""
        base_score = {"低": 20, "中": 50, "高": 80}.get(risk_level, 20)
        factor_score = min(risk_factors_count * 5, 15)
        symptom_score = min(symptoms_count * 3, 10)
        return min(base_score + factor_score + symptom_score, 100)
    
    def _get_treatment_principles(self, constitution_analysis: Dict, bagua_analysis: Dict) -> List[str]:
        """获取治疗原则"""
        principles = []
        
        constitution_principles = constitution_analysis.get("养生原则", [])
        principles.extend(constitution_principles[:2])
        
        bagua_focus = bagua_analysis.get("重点关注", [])
        if bagua_focus:
            principles.append(bagua_focus[0])
        
        return principles
    
    def _get_treatment_course_advice(self, constitution_analysis: Dict) -> str:
        """获取疗程建议"""
        constitution_type = constitution_analysis.get("体质类型", "")
        
        if "虚" in constitution_type:
            return "建议长期调理，疗程3-6个月"
        elif "热" in constitution_type or "火" in constitution_type:
            return "建议短期调理，疗程1-2个月"
        else:
            return "建议中期调理，疗程2-3个月"
    
    def _predict_next_week_optimal_times(self, current_datetime: datetime) -> List[str]:
        """预测下周最佳时间"""
        optimal_times = []
        for i in range(7):
            future_date = current_datetime + timedelta(days=i+1)
            day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][future_date.weekday()]
            optimal_times.append(f"{day_name}: 寅时(3-5点)、午时(11-13点)")
        return optimal_times
    
    def _integrate_diet_advice(self, constitution_analysis: Dict, bagua_analysis: Dict) -> Dict[str, List[str]]:
        """整合饮食建议"""
        constitution_diet = constitution_analysis.get("饮食宜忌", {})
        bagua_diet = bagua_analysis.get("养生建议", {}).get("本命卦养生", {}).get("饮食", [])
        
        return {
            "宜食": constitution_diet.get("宜", []) + bagua_diet[:2],
            "忌食": constitution_diet.get("忌", []),
            "特色建议": ["根据体质选择食物", "遵循时令饮食", "注意五味调和"]
        }
    
    def _integrate_exercise_advice(self, constitution_analysis: Dict, bagua_analysis: Dict) -> List[str]:
        """整合运动建议"""
        constitution_exercise = constitution_analysis.get("调理方案", {}).get("运动建议", [])
        bagua_exercise = bagua_analysis.get("养生建议", {}).get("本命卦养生", {}).get("运动", [])
        
        return list(set(constitution_exercise + bagua_exercise))
    
    def _integrate_emotion_advice(self, constitution_analysis: Dict, bagua_analysis: Dict) -> List[str]:
        """整合情志建议"""
        constitution_emotion = constitution_analysis.get("调理方案", {}).get("情志调养", [])
        bagua_emotion = bagua_analysis.get("养生建议", {}).get("本命卦养生", {}).get("情志", [])
        
        return list(set(constitution_emotion + bagua_emotion))
    
    def _integrate_lifestyle_advice(self, constitution_analysis: Dict, bagua_analysis: Dict) -> List[str]:
        """整合起居建议"""
        constitution_lifestyle = constitution_analysis.get("调理方案", {}).get("起居建议", [])
        bagua_lifestyle = bagua_analysis.get("养生建议", {}).get("本命卦养生", {}).get("起居", [])
        
        return list(set(constitution_lifestyle + bagua_lifestyle))
    
    def _generate_checkup_advice(self, constitution_analysis: Dict, bagua_analysis: Dict) -> List[str]:
        """生成检查建议"""
        checkups = []
        
        constitution_diseases = constitution_analysis.get("易患疾病", [])
        for disease in constitution_diseases[:3]:
            if "心" in disease:
                checkups.append("定期心电图检查")
            elif "肝" in disease:
                checkups.append("定期肝功能检查")
            elif "肾" in disease:
                checkups.append("定期肾功能检查")
            elif "肺" in disease:
                checkups.append("定期胸部X光检查")
        
        checkups.append("年度体检")
        return list(set(checkups))
    
    def _generate_lifestyle_prevention(self, constitution_analysis: Dict) -> List[str]:
        """生成生活方式预防建议"""
        return [
            "保持规律作息",
            "适度运动锻炼",
            "均衡营养饮食",
            "保持心情愉悦",
            "避免过度劳累"
        ]
    
    def _get_prevention_priorities(self, constitution_analysis: Dict, bagua_analysis: Dict) -> List[str]:
        """获取预防重点"""
        priorities = []
        
        constitution_prevention = constitution_analysis.get("疾病易感性", {}).get("预防重点", [])
        priorities.extend(constitution_prevention[:2])
        
        bagua_focus = bagua_analysis.get("重点关注", [])
        priorities.extend(bagua_focus[:1])
        
        return list(set(priorities))
    
    def _get_health_monitoring_advice(self, constitution_analysis: Dict, symptoms: List[str]) -> List[str]:
        """获取健康监测建议"""
        monitoring = ["定期自我健康评估", "关注身体变化"]
        
        if symptoms:
            monitoring.append("密切观察症状变化")
        
        constitution_type = constitution_analysis.get("体质类型", "")
        if "虚" in constitution_type:
            monitoring.append("注意精神状态和体力变化")
        
        return monitoring 