#!/usr/bin/env python3
"""
索克生活 - 小克智能体优化服务
基于OptimizedAgentBase实现的健康监测智能体
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from optimized_agent_base import OptimizedAgentBase, AgentRequest, cpu_intensive_task, cached_result
from aiohttp import web

class XiaokeOptimizedService(OptimizedAgentBase):
    """小克智能体优化服务 - 健康监测专家"""
    
    def __init__(self):
        super().__init__(
            agent_name="xiaoke",
            max_workers=int(os.getenv("MAX_WORKERS", "8")),
            redis_url=os.getenv("REDIS_URL"),
            database_url=os.getenv("DATABASE_URL")
        )
    
    def _register_agent_routes(self):
        """注册小克特定路由"""
        self.app.router.add_post("/monitor", self._monitor_handler)
        self.app.router.add_post("/analyze", self._analyze_handler)
        self.app.router.add_post("/alert", self._alert_handler)
        self.app.router.add_get("/status", self._status_handler)
    
    async def _process_action(self, request: AgentRequest) -> Dict[str, Any]:
        """处理小克的具体动作"""
        action = request.action
        input_data = request.input_data
        
        if action == "monitor":
            return await self._handle_monitoring(input_data)
        elif action == "analyze":
            return await self._handle_analysis(input_data)
        elif action == "alert":
            return await self._handle_alert(input_data)
        elif action == "trend_analysis":
            return await self._handle_trend_analysis(input_data)
        else:
            raise ValueError(f"未知的动作类型: {action}")
    
    @cached_result(ttl=300)
    async def _handle_monitoring(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康监测请求"""
        user_id = input_data.get("user_id")
        vital_signs = input_data.get("vital_signs", {})
        
        # 实时健康指标分析
        analysis_result = await self._analyze_vital_signs(vital_signs)
        
        # 风险评估
        risk_assessment = await self._assess_health_risks(vital_signs, user_id)
        
        return {
            "monitoring_result": analysis_result,
            "risk_assessment": risk_assessment,
            "recommendations": self._generate_monitoring_recommendations(analysis_result),
            "next_check_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "timestamp": datetime.now().isoformat()
        }
    
    @cpu_intensive_task
    def _analyze_health_trends(self, health_data: np.ndarray) -> Dict[str, Any]:
        """分析健康趋势 - CPU密集型任务"""
        # 时间序列分析
        if len(health_data.shape) == 1:
            health_data = health_data.reshape(-1, 1)
        
        # 计算趋势指标
        trends = []
        for i in range(health_data.shape[1]):
            series = health_data[:, i]
            
            # 线性趋势
            x = np.arange(len(series))
            coeffs = np.polyfit(x, series, 1)
            trend_slope = coeffs[0]
            
            # 变异性
            variability = np.std(series)
            
            # 异常值检测
            q75, q25 = np.percentile(series, [75, 25])
            iqr = q75 - q25
            outliers = np.sum((series < (q25 - 1.5 * iqr)) | (series > (q75 + 1.5 * iqr)))
            
            trends.append({
                "trend_slope": float(trend_slope),
                "variability": float(variability),
                "outlier_count": int(outliers),
                "mean_value": float(np.mean(series)),
                "latest_value": float(series[-1])
            })
        
        return {
            "trends": trends,
            "overall_stability": float(np.mean([t["variability"] for t in trends])),
            "trend_direction": "improving" if np.mean([t["trend_slope"] for t in trends]) > 0 else "declining"
        }
    
    async def _handle_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康数据分析请求"""
        if "health_history" in input_data:
            health_data = np.array(input_data["health_history"], dtype=np.float32)
            
            # 使用CPU密集型任务进行趋势分析
            trend_analysis = await self._analyze_health_trends(health_data)
            
            # 生成健康报告
            health_report = await self._generate_health_report(trend_analysis, input_data)
            
            return {
                "trend_analysis": trend_analysis,
                "health_report": health_report,
                "insights": self._generate_health_insights(trend_analysis),
                "timestamp": datetime.now().isoformat()
            }
        
        return {"message": "小克分析完成", "timestamp": datetime.now().isoformat()}
    
    async def _handle_alert(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康预警请求"""
        alert_type = input_data.get("alert_type", "general")
        severity = input_data.get("severity", "medium")
        user_id = input_data.get("user_id")
        
        # 生成预警信息
        alert_info = await self._generate_alert_info(alert_type, severity, input_data)
        
        # 推荐行动
        recommended_actions = self._get_recommended_actions(alert_type, severity)
        
        return {
            "alert_info": alert_info,
            "recommended_actions": recommended_actions,
            "urgency_level": self._calculate_urgency_level(severity),
            "follow_up_required": severity in ["high", "critical"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_trend_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理趋势分析请求"""
        time_series_data = input_data.get("time_series", [])
        analysis_period = input_data.get("period", "week")
        
        # 长期趋势分析
        long_term_trends = await self._analyze_long_term_trends(time_series_data, analysis_period)
        
        # 预测未来趋势
        predictions = await self._predict_health_trends(time_series_data)
        
        return {
            "long_term_trends": long_term_trends,
            "predictions": predictions,
            "trend_summary": self._summarize_trends(long_term_trends),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_vital_signs(self, vital_signs: Dict[str, Any]) -> Dict[str, Any]:
        """分析生命体征"""
        analysis = {}
        
        # 血压分析
        if "blood_pressure" in vital_signs:
            bp = vital_signs["blood_pressure"]
            systolic = bp.get("systolic", 120)
            diastolic = bp.get("diastolic", 80)
            
            analysis["blood_pressure"] = {
                "status": self._classify_blood_pressure(systolic, diastolic),
                "risk_level": self._assess_bp_risk(systolic, diastolic),
                "values": {"systolic": systolic, "diastolic": diastolic}
            }
        
        # 心率分析
        if "heart_rate" in vital_signs:
            hr = vital_signs["heart_rate"]
            analysis["heart_rate"] = {
                "status": self._classify_heart_rate(hr),
                "risk_level": self._assess_hr_risk(hr),
                "value": hr
            }
        
        # 体温分析
        if "temperature" in vital_signs:
            temp = vital_signs["temperature"]
            analysis["temperature"] = {
                "status": self._classify_temperature(temp),
                "risk_level": self._assess_temp_risk(temp),
                "value": temp
            }
        
        return analysis
    
    async def _assess_health_risks(self, vital_signs: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """评估健康风险"""
        risk_factors = []
        overall_risk = "low"
        
        # 基于生命体征评估风险
        if "blood_pressure" in vital_signs:
            bp = vital_signs["blood_pressure"]
            if bp.get("systolic", 120) > 140 or bp.get("diastolic", 80) > 90:
                risk_factors.append("高血压风险")
                overall_risk = "medium"
        
        if "heart_rate" in vital_signs:
            hr = vital_signs["heart_rate"]
            if hr > 100 or hr < 60:
                risk_factors.append("心率异常")
                if overall_risk == "low":
                    overall_risk = "medium"
        
        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "risk_score": self._calculate_risk_score(vital_signs),
            "assessment_time": datetime.now().isoformat()
        }
    
    async def _generate_health_report(self, trend_analysis: Dict[str, Any], 
                                    input_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成健康报告"""
        return {
            "report_id": f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": input_data.get("user_id"),
            "analysis_period": input_data.get("period", "recent"),
            "key_findings": self._extract_key_findings(trend_analysis),
            "health_score": self._calculate_health_score(trend_analysis),
            "improvement_areas": self._identify_improvement_areas(trend_analysis),
            "generated_at": datetime.now().isoformat()
        }
    
    async def _generate_alert_info(self, alert_type: str, severity: str, 
                                 input_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成预警信息"""
        alert_messages = {
            "blood_pressure": "血压异常检测",
            "heart_rate": "心率异常检测", 
            "temperature": "体温异常检测",
            "general": "健康指标异常"
        }
        
        return {
            "alert_id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "message": alert_messages.get(alert_type, "健康监测预警"),
            "severity": severity,
            "details": input_data.get("details", ""),
            "detected_at": datetime.now().isoformat()
        }
    
    async def _analyze_long_term_trends(self, time_series: List[Dict], 
                                      period: str) -> Dict[str, Any]:
        """分析长期趋势"""
        if not time_series:
            return {"trends": [], "summary": "无足够数据"}
        
        # 模拟长期趋势分析
        return {
            "period": period,
            "data_points": len(time_series),
            "trend_direction": "stable",
            "significant_changes": [],
            "analysis_date": datetime.now().isoformat()
        }
    
    async def _predict_health_trends(self, time_series: List[Dict]) -> Dict[str, Any]:
        """预测健康趋势"""
        # 简单的趋势预测
        return {
            "prediction_horizon": "7_days",
            "predicted_values": [],
            "confidence_level": 0.75,
            "prediction_date": datetime.now().isoformat()
        }
    
    def _classify_blood_pressure(self, systolic: float, diastolic: float) -> str:
        """血压分类"""
        if systolic < 120 and diastolic < 80:
            return "正常"
        elif systolic < 130 and diastolic < 80:
            return "正常高值"
        elif systolic < 140 or diastolic < 90:
            return "高血压1级"
        else:
            return "高血压2级"
    
    def _classify_heart_rate(self, heart_rate: float) -> str:
        """心率分类"""
        if 60 <= heart_rate <= 100:
            return "正常"
        elif heart_rate < 60:
            return "心动过缓"
        else:
            return "心动过速"
    
    def _classify_temperature(self, temperature: float) -> str:
        """体温分类"""
        if 36.1 <= temperature <= 37.2:
            return "正常"
        elif temperature < 36.1:
            return "体温偏低"
        else:
            return "发热"
    
    def _assess_bp_risk(self, systolic: float, diastolic: float) -> str:
        """评估血压风险"""
        if systolic >= 140 or diastolic >= 90:
            return "high"
        elif systolic >= 130 or diastolic >= 80:
            return "medium"
        else:
            return "low"
    
    def _assess_hr_risk(self, heart_rate: float) -> str:
        """评估心率风险"""
        if heart_rate < 50 or heart_rate > 120:
            return "high"
        elif heart_rate < 60 or heart_rate > 100:
            return "medium"
        else:
            return "low"
    
    def _assess_temp_risk(self, temperature: float) -> str:
        """评估体温风险"""
        if temperature >= 38.5 or temperature < 35.5:
            return "high"
        elif temperature >= 37.5 or temperature < 36.0:
            return "medium"
        else:
            return "low"
    
    def _calculate_risk_score(self, vital_signs: Dict[str, Any]) -> float:
        """计算风险评分"""
        score = 0.0
        
        if "blood_pressure" in vital_signs:
            bp = vital_signs["blood_pressure"]
            if bp.get("systolic", 120) > 140:
                score += 0.3
            if bp.get("diastolic", 80) > 90:
                score += 0.3
        
        if "heart_rate" in vital_signs:
            hr = vital_signs["heart_rate"]
            if hr > 100 or hr < 60:
                score += 0.2
        
        return min(score, 1.0)
    
    def _generate_monitoring_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成监测建议"""
        recommendations = []
        
        for vital_sign, data in analysis.items():
            if data.get("risk_level") == "high":
                recommendations.append(f"建议立即就医检查{vital_sign}")
            elif data.get("risk_level") == "medium":
                recommendations.append(f"建议密切监测{vital_sign}")
        
        if not recommendations:
            recommendations.append("继续保持良好的健康状态")
        
        return recommendations
    
    def _generate_health_insights(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """生成健康洞察"""
        insights = []
        
        if trend_analysis.get("trend_direction") == "improving":
            insights.append("您的健康指标呈现改善趋势")
        elif trend_analysis.get("trend_direction") == "declining":
            insights.append("需要关注健康指标的下降趋势")
        else:
            insights.append("您的健康指标保持稳定")
        
        return insights
    
    def _get_recommended_actions(self, alert_type: str, severity: str) -> List[str]:
        """获取推荐行动"""
        actions = {
            "high": ["立即就医", "联系医生", "停止当前活动"],
            "medium": ["密切观察", "记录症状", "适当休息"],
            "low": ["继续监测", "保持健康生活方式"]
        }
        
        return actions.get(severity, ["继续监测"])
    
    def _calculate_urgency_level(self, severity: str) -> int:
        """计算紧急程度"""
        urgency_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
        return urgency_map.get(severity, 1)
    
    def _extract_key_findings(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """提取关键发现"""
        findings = []
        
        if trend_analysis.get("overall_stability", 0) > 0.5:
            findings.append("健康指标波动较大")
        else:
            findings.append("健康指标相对稳定")
        
        return findings
    
    def _calculate_health_score(self, trend_analysis: Dict[str, Any]) -> float:
        """计算健康评分"""
        base_score = 0.8
        stability = trend_analysis.get("overall_stability", 0)
        
        # 稳定性越高，评分越低
        score = base_score - (stability * 0.3)
        return max(min(score, 1.0), 0.0)
    
    def _identify_improvement_areas(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """识别改进领域"""
        areas = []
        
        if trend_analysis.get("overall_stability", 0) > 0.3:
            areas.append("提高生活规律性")
        
        if trend_analysis.get("trend_direction") == "declining":
            areas.append("加强健康管理")
        
        return areas if areas else ["保持当前良好状态"]
    
    def _summarize_trends(self, trends: Dict[str, Any]) -> str:
        """总结趋势"""
        return f"分析了{trends.get('data_points', 0)}个数据点，趋势为{trends.get('trend_direction', '未知')}"
    
    async def _monitor_handler(self, request):
        """监测接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'mon_' + str(hash(str(data)))),
                agent_type="xiaoke",
                action="monitor",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _analyze_handler(self, request):
        """分析接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'ana_' + str(hash(str(data)))),
                agent_type="xiaoke",
                action="analyze",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _alert_handler(self, request):
        """预警接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'alert_' + str(hash(str(data)))),
                agent_type="xiaoke",
                action="alert",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _status_handler(self, request):
        """状态信息处理器"""
        return web.json_response({
            "agent": "xiaoke",
            "status": "active",
            "capabilities": [
                "实时健康监测",
                "生命体征分析",
                "健康风险评估",
                "趋势分析",
                "健康预警"
            ],
            "monitoring_metrics": {
                "active_monitors": 0,
                "alerts_today": 0,
                "last_analysis": datetime.now().isoformat()
            }
        })

async def main():
    """主函数"""
    service = XiaokeOptimizedService()
    
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")
    
    await service.start_server(host=host, port=port)

if __name__ == "__main__":
    asyncio.run(main()) 