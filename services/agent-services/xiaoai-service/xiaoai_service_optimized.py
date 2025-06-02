#!/usr/bin/env python3
"""
索克生活 - 小艾智能体优化服务
基于OptimizedAgentBase实现的AI推理智能体
"""

import asyncio
import os
import sys
import numpy as np
from typing import Dict, Any
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from optimized_agent_base import OptimizedAgentBase, AgentRequest, cpu_intensive_task, cached_result
from aiohttp import web


class XiaoaiOptimizedService(OptimizedAgentBase):
    """小艾智能体优化服务 - AI推理专家"""
    
    def __init__(self):
        super().__init__(
            agent_name="xiaoai",
            max_workers=int(os.getenv("MAX_WORKERS", "8")),
            redis_url=os.getenv("REDIS_URL"),
            database_url=os.getenv("DATABASE_URL")
        )
    
    def _register_agent_routes(self):
        """注册小艾特定路由"""
        self.app.router.add_post("/inference", self._inference_handler)
        self.app.router.add_post("/conversation", self._conversation_handler)
        self.app.router.add_post("/analysis", self._analysis_handler)
        self.app.router.add_get("/models", self._models_handler)
    
    async def _process_action(self, request: AgentRequest) -> Dict[str, Any]:
        """处理小艾的具体动作"""
        action = request.action
        input_data = request.input_data
        
        if action == "inference":
            return await self._handle_inference(input_data)
        elif action == "conversation":
            return await self._handle_conversation(input_data)
        elif action == "analysis":
            return await self._handle_analysis(input_data)
        elif action == "health_assessment":
            return await self._handle_health_assessment(input_data)
        else:
            raise ValueError(f"未知的动作类型: {action}")
    
    @cached_result(ttl=600)
    async def _handle_inference(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理AI推理请求"""
        if "symptoms" in input_data and "weights" in input_data:
            # 中医辨证分析
            symptoms = np.array(input_data["symptoms"], dtype=np.float32)
            weights = np.array(input_data["weights"], dtype=np.float32)
            
            # 使用JIT优化算法
            loop = asyncio.get_event_loop()
            syndrome_scores = await loop.run_in_executor(
                self.cpu_pool,
                self.algorithms.vector_similarity,
                symptoms,
                weights
            )
            
            return {
                "syndrome_analysis": float(syndrome_scores),
                "confidence": min(max(float(syndrome_scores), 0.0), 1.0),
                "recommendations": self._generate_tcm_recommendations(syndrome_scores),
                "timestamp": datetime.now().isoformat()
            }
        
        return {"message": "小艾AI推理完成", "timestamp": datetime.now().isoformat()}
    
    @cached_result(ttl=300)
    async def _handle_conversation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理对话请求"""
        user_message = input_data.get("message", "")
        context = input_data.get("context", {})
        
        # 模拟AI对话处理
        response = await self._generate_ai_response(user_message, context)
        
        return {
            "response": response,
            "context_updated": True,
            "emotion": "friendly",
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat()
        }
    
    @cpu_intensive_task
    def _analyze_health_patterns(self, health_data: np.ndarray) -> Dict[str, Any]:
        """分析健康模式 - CPU密集型任务"""
        # 模拟复杂的健康数据分析
        mean_values = np.mean(health_data, axis=0)
        std_values = np.std(health_data, axis=0)
        trends = np.diff(health_data, axis=0)
        
        return {
            "mean_indicators": mean_values.tolist(),
            "variability": std_values.tolist(),
            "trends": np.mean(trends, axis=0).tolist(),
            "risk_score": float(np.mean(mean_values))
        }
    
    async def _handle_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理分析请求"""
        if "health_data" in input_data:
            health_data = np.array(input_data["health_data"], dtype=np.float32)
            
            # 使用CPU密集型任务装饰器
            analysis_result = await self._analyze_health_patterns(health_data)
            
            return {
                "analysis": analysis_result,
                "insights": self._generate_health_insights(analysis_result),
                "timestamp": datetime.now().isoformat()
            }
        
        return {"message": "小艾分析完成", "timestamp": datetime.now().isoformat()}
    
    async def _handle_health_assessment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康评估请求"""
        user_profile = input_data.get("user_profile", {})
        symptoms = input_data.get("symptoms", [])
        
        # 综合健康评估
        assessment = await self._comprehensive_health_assessment(user_profile, symptoms)
        
        return {
            "assessment": assessment,
            "recommendations": self._generate_personalized_recommendations(assessment),
            "follow_up": self._suggest_follow_up_actions(assessment),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """生成AI响应"""
        # 模拟AI对话生成
        await asyncio.sleep(0.1)  # 模拟处理时间
        
        responses = [
            f"我理解您提到的'{message}'，让我为您分析一下。",
            f"根据您的描述'{message}'，我建议您注意以下几点。",
            f"关于'{message}'这个问题，从中医角度来看...",
            f"您提到的'{message}'很重要，我来为您详细解答。"
        ]
        
        return responses[hash(message) % len(responses)]
    
    async def _comprehensive_health_assessment(self, user_profile: Dict[str, Any], 
                                             symptoms: list) -> Dict[str, Any]:
        """综合健康评估"""
        # 模拟综合评估
        await asyncio.sleep(0.2)  # 模拟处理时间
        
        age = user_profile.get("age", 30)
        gender = user_profile.get("gender", "unknown")
        
        base_score = 0.8
        if age > 60:
            base_score -= 0.1
        if len(symptoms) > 3:
            base_score -= 0.2
        
        return {
            "overall_score": max(min(base_score, 1.0), 0.0),
            "risk_factors": self._identify_risk_factors(user_profile, symptoms),
            "health_status": "良好" if base_score > 0.7 else "需要关注",
            "assessment_date": datetime.now().isoformat()
        }
    
    def _generate_tcm_recommendations(self, syndrome_score: float) -> list:
        """生成中医建议"""
        if syndrome_score > 0.7:
            return ["清热解毒", "养阴润燥", "定期复查"]
        elif syndrome_score > 0.4:
            return ["健脾益气", "调理气血", "适度运动"]
        else:
            return ["温阳散寒", "补肾固本", "注意保暖"]
    
    def _generate_health_insights(self, analysis: Dict[str, Any]) -> list:
        """生成健康洞察"""
        insights = []
        risk_score = analysis.get("risk_score", 0.5)
        
        if risk_score > 0.7:
            insights.append("您的健康指标显示需要特别关注")
        elif risk_score > 0.4:
            insights.append("您的健康状况总体良好，建议保持")
        else:
            insights.append("您的健康指标优秀，请继续保持")
        
        return insights
    
    def _generate_personalized_recommendations(self, assessment: Dict[str, Any]) -> list:
        """生成个性化建议"""
        score = assessment.get("overall_score", 0.5)
        
        if score > 0.8:
            return ["保持良好生活习惯", "定期体检", "适度运动"]
        elif score > 0.6:
            return ["调整作息时间", "均衡饮食", "增加运动量"]
        else:
            return ["及时就医咨询", "改善生活方式", "密切监测健康状况"]
    
    def _suggest_follow_up_actions(self, assessment: Dict[str, Any]) -> list:
        """建议后续行动"""
        return [
            "一周后复查相关指标",
            "记录日常症状变化",
            "如有异常及时联系医生"
        ]
    
    def _identify_risk_factors(self, user_profile: Dict[str, Any], symptoms: list) -> list:
        """识别风险因素"""
        risk_factors = []
        
        age = user_profile.get("age", 30)
        if age > 50:
            risk_factors.append("年龄相关风险")
        
        if len(symptoms) > 5:
            risk_factors.append("症状复杂性")
        
        return risk_factors
    
    async def _inference_handler(self, request):
        """推理接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'inf_' + str(hash(str(data)))),
                agent_type="xiaoai",
                action="inference",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _conversation_handler(self, request):
        """对话接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'conv_' + str(hash(str(data)))),
                agent_type="xiaoai",
                action="conversation",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _analysis_handler(self, request):
        """分析接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'ana_' + str(hash(str(data)))),
                agent_type="xiaoai",
                action="analysis",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _models_handler(self, request):
        """模型信息处理器"""
        return web.json_response({
            "agent": "xiaoai",
            "models": [
                {
                    "name": "tcm_syndrome_classifier",
                    "version": "v2.1.0",
                    "status": "active"
                },
                {
                    "name": "conversation_llm",
                    "version": "v1.5.0",
                    "status": "active"
                }
            ],
            "capabilities": [
                "中医辨证分析",
                "智能对话",
                "健康评估",
                "个性化建议"
            ]
        })


async def main():
    """主函数"""
    service = XiaoaiOptimizedService()
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    await service.start_server(host=host, port=port)


if __name__ == "__main__":
    asyncio.run(main()) 