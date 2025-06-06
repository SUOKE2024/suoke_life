"""
calculation - 索克生活项目模块
"""

from ..core.algorithms.wuyun_liuqi import WuyunLiuqiCalculator
from ..core.models.calculation import (
from ..utils.bagua_calculator import BaguaCalculator
from ..utils.bazi_calculator import BaziCalculator
from ..utils.ziwu_calculator import ZiwuCalculator
from datetime import date, datetime, time
from typing import Dict, List, Optional, Any
from uuid import uuid4
import asyncio
import logging

"""
算诊计算服务

提供算诊相关的核心业务逻辑
"""


    WuyunLiuqiModel,
    BaguaAnalysisModel,
    ZiwuLiuzhuModel,
    ConstitutionAnalysisModel,
    ComprehensiveAnalysisModel
)

class CalculationService:
    """算诊计算服务"""
    
    def __init__(self):
        """初始化服务"""
        self.wuyun_calculator = WuyunLiuqiCalculator()
        self.bazi_calculator = BaziCalculator()
        self.bagua_calculator = BaguaCalculator()
        self.ziwu_calculator = ZiwuCalculator()
    
    async def analyze_bagua_constitution(
        self,
        birth_date: date,
        birth_time: Optional[str] = None,
        birth_location: Optional[Dict] = None
    ) -> Dict:
        """
        八卦体质分析
        
        Args:
            birth_date: 出生日期
            birth_time: 出生时间
            birth_location: 出生地点
            
        Returns:
            八卦体质分析结果
        """
        # 计算八字
        bazi = self.bazi_calculator.calculate_bazi(birth_date, birth_time)
        
        # 八卦分析
        bagua_result = self.bagua_calculator.analyze_constitution(
            bazi, birth_location
        )
        
        return {
            "analysis_id": str(uuid4()),
            "birth_info": {
                "date": birth_date.isoformat(),
                "time": birth_time,
                "location": birth_location
            },
            "bazi": bazi,
            "bagua_analysis": bagua_result,
            "analysis_time": datetime.utcnow().isoformat()
        }
    
    async def analyze_ziwu_liuzhu(
        self,
        condition: str,
        treatment_type: str,
        analysis_date: date
    ) -> Dict:
        """
        子午流注分析
        
        Args:
            condition: 病症
            treatment_type: 治疗类型
            analysis_date: 分析日期
            
        Returns:
            子午流注分析结果
        """
        # 计算当日经络流注
        meridian_flow = self.ziwu_calculator.calculate_daily_flow(analysis_date)
        
        # 推荐最佳治疗时间
        optimal_times = self.ziwu_calculator.recommend_treatment_times(
            condition, treatment_type, analysis_date
        )
        
        # 生成治疗建议
        treatment_advice = self.ziwu_calculator.generate_treatment_advice(
            condition, treatment_type, optimal_times
        )
        
        return {
            "analysis_id": str(uuid4()),
            "condition": condition,
            "treatment_type": treatment_type,
            "analysis_date": analysis_date.isoformat(),
            "daily_meridian_flow": meridian_flow,
            "optimal_treatment_times": optimal_times,
            "treatment_advice": treatment_advice,
            "analysis_time": datetime.utcnow().isoformat()
        }
    
    async def comprehensive_analysis(
        self,
        patient_info: Dict,
        current_symptoms: Optional[List[str]] = None,
        analysis_date: date = None,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        综合算诊分析
        
        Args:
            patient_info: 患者信息
            current_symptoms: 当前症状
            analysis_date: 分析日期
            options: 分析选项
            
        Returns:
            综合分析结果
        """
        if analysis_date is None:
            analysis_date = date.today()
        
        # 提取患者基本信息
        birth_date = datetime.fromisoformat(patient_info["birth_date"]).date()
        birth_time = patient_info.get("birth_time")
        birth_location = patient_info.get("birth_location")
        
        # 并行执行各种分析
        tasks = []
        
        # 五运六气分析
        if options is None or options.get("include_wuyun_liuqi", True):
            tasks.append(self._analyze_wuyun_liuqi_async(analysis_date.year, birth_date))
        
        # 八卦体质分析
        if options is None or options.get("include_bagua", True):
            tasks.append(self.analyze_bagua_constitution(birth_date, birth_time, birth_location))
        
        # 子午流注分析（如果有症状）
        if current_symptoms and (options is None or options.get("include_ziwu", True)):
            for symptom in current_symptoms[:3]:  # 限制最多3个症状
                tasks.append(self.analyze_ziwu_liuzhu(symptom, "综合治疗", analysis_date))
        
        # 等待所有分析完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理分析结果
        comprehensive_result = {
            "analysis_id": str(uuid4()),
            "patient_info": patient_info,
            "current_symptoms": current_symptoms,
            "analysis_date": analysis_date.isoformat(),
            "analysis_time": datetime.utcnow().isoformat()
        }
        
        # 添加各项分析结果
        result_index = 0
        if options is None or options.get("include_wuyun_liuqi", True):
            if not isinstance(results[result_index], Exception):
                comprehensive_result["wuyun_liuqi"] = results[result_index]
            result_index += 1
        
        if options is None or options.get("include_bagua", True):
            if not isinstance(results[result_index], Exception):
                comprehensive_result["bagua_analysis"] = results[result_index]
            result_index += 1
        
        if current_symptoms and (options is None or options.get("include_ziwu", True)):
            ziwu_results = []
            for i in range(min(len(current_symptoms), 3)):
                if not isinstance(results[result_index + i], Exception):
                    ziwu_results.append(results[result_index + i])
            if ziwu_results:
                comprehensive_result["ziwu_liuzhu"] = ziwu_results
        
        # 生成综合评估
        comprehensive_result["comprehensive_assessment"] = self._generate_comprehensive_assessment(
            comprehensive_result
        )
        
        # 生成综合建议
        comprehensive_result["comprehensive_recommendations"] = self._generate_comprehensive_recommendations(
            comprehensive_result
        )
        
        return comprehensive_result
    
    async def _analyze_wuyun_liuqi_async(self, year: int, patient_birth: Optional[date] = None) -> Dict:
        """异步五运六气分析"""
        return self.wuyun_calculator.calculate_wuyun_liuqi(year, patient_birth)
    
    def _generate_comprehensive_assessment(self, analysis_result: Dict) -> str:
        """
        生成综合评估
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            综合评估文本
        """
        assessments = []
        
        # 五运六气评估
        if "wuyun_liuqi" in analysis_result:
            wuyun_data = analysis_result["wuyun_liuqi"]
            wuyun_type = wuyun_data["wuyun"]["type"]
            assessments.append(f"当前年份{wuyun_type}，{wuyun_data['climate_influence']}")
        
        # 八卦体质评估
        if "bagua_analysis" in analysis_result:
            bagua_data = analysis_result["bagua_analysis"]
            if "bagua_analysis" in bagua_data:
                constitution_type = bagua_data["bagua_analysis"].get("constitution_type", "")
                assessments.append(f"体质类型为{constitution_type}")
        
        # 症状评估
        if analysis_result.get("current_symptoms"):
            symptoms = analysis_result["current_symptoms"]
            assessments.append(f"当前主要症状包括：{', '.join(symptoms[:3])}")
        
        return "；".join(assessments) if assessments else "综合分析显示体质平和，无明显异常"
    
    def _generate_comprehensive_recommendations(self, analysis_result: Dict) -> List[str]:
        """
        生成综合建议
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            综合建议列表
        """
        recommendations = set()
        
        # 从五运六气获取建议
        if "wuyun_liuqi" in analysis_result:
            wuyun_data = analysis_result["wuyun_liuqi"]
            recommendations.update(wuyun_data.get("prevention_advice", []))
            
            # 个性化建议
            if "personalized_analysis" in wuyun_data:
                personal_advice = wuyun_data["personalized_analysis"].get("personalized_advice", [])
                recommendations.update(personal_advice)
        
        # 从八卦分析获取建议
        if "bagua_analysis" in analysis_result:
            bagua_data = analysis_result["bagua_analysis"]
            if "bagua_analysis" in bagua_data:
                health_advice = bagua_data["bagua_analysis"].get("health_advice", [])
                recommendations.update(health_advice)
        
        # 从子午流注获取建议
        if "ziwu_liuzhu" in analysis_result:
            ziwu_results = analysis_result["ziwu_liuzhu"]
            if isinstance(ziwu_results, list):
                for ziwu_data in ziwu_results:
                    treatment_advice = ziwu_data.get("treatment_advice", [])
                    recommendations.update(treatment_advice)
        
        # 添加通用建议
        recommendations.update([
            "保持规律作息，早睡早起",
            "饮食清淡，营养均衡",
            "适度运动，增强体质",
            "调畅情志，保持心情愉悦"
        ])
        
        return list(recommendations)
    
    async def log_analysis(
        self,
        analysis_type: str,
        request_data: Dict,
        result_data: Dict
    ) -> None:
        """
        记录分析日志
        
        Args:
            analysis_type: 分析类型
            request_data: 请求数据
            result_data: 结果数据
        """
        # 这里可以实现日志记录逻辑
        # 例如保存到数据库、发送到日志服务等
        pass
    
    async def get_analysis_history(
        self,
        patient_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """
        获取分析历史
        
        Args:
            patient_id: 患者ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            分析历史记录
        """
        # 这里应该从数据库查询历史记录
        # 暂时返回空列表
        return []
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """
        删除分析记录
        
        Args:
            analysis_id: 分析记录ID
            
        Returns:
            删除是否成功
        """
        # 这里应该从数据库删除记录
        # 暂时返回True
        return True 