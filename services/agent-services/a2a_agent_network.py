#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活 A2A 智能体网络管理器
Suoke Life A2A Agent Network Manager

统一管理和协调四大智能体的 A2A 协议通信
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from python_a2a import AgentNetwork, AgentCard, AIAgentRouter, WorkflowStep, WorkflowContext, Flow

# 导入四大智能体
from xiaoai_service.xiaoai.a2a_agent import create_xiaoai_a2a_agent
from xiaoke_service.xiaoke_a2a_agent import create_xiaoke_a2a_agent
from laoke_service.laoke_a2a_agent import create_laoke_a2a_agent
from soer_service.soer_a2a_agent import create_soer_a2a_agent

logger = logging.getLogger(__name__)


class SuokeLifeA2ANetwork:
    """索克生活 A2A 智能体网络"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 A2A 智能体网络
        
        Args:
            config: 网络配置
        """
        self.config = config or {}
        
        # 初始化四大智能体
        self.xiaoai_agent = create_xiaoai_a2a_agent(config.get("xiaoai", {}))
        self.xiaoke_agent = create_xiaoke_a2a_agent(config.get("xiaoke", {}))
        self.laoke_agent = create_laoke_a2a_agent(config.get("laoke", {}))
        self.soer_agent = create_soer_a2a_agent(config.get("soer", {}))
        
        # 创建智能体网络
        self.agent_network = AgentNetwork()
        
        # 注册智能体到网络
        self._register_agents()
        
        # 创建 AI 路由器
        self.ai_router = AIAgentRouter(
            agents=[
                self.xiaoai_agent,
                self.xiaoke_agent,
                self.laoke_agent,
                self.soer_agent
            ]
        )
        
        # 创建工作流管理器
        self.workflows = {}
        
        # 定义预设工作流
        self._define_workflows()
        
        logger.info("索克生活 A2A 智能体网络初始化完成")
    
    def _register_agents(self):
        """注册智能体到网络"""
        agents = [
            ("xiaoai", self.xiaoai_agent),
            ("xiaoke", self.xiaoke_agent),
            ("laoke", self.laoke_agent),
            ("soer", self.soer_agent)
        ]
        
        for agent_id, agent in agents:
            self.agent_network.register_agent(agent_id, agent)
            logger.info(f"已注册智能体: {agent_id}")
    
    def _define_workflows(self):
        """定义预设工作流"""
        
        # 1. 健康咨询工作流
        health_consultation_workflow = {
            "name": "健康咨询工作流",
            "description": "用户健康咨询的完整处理流程",
            "steps": [
                {
                    "id": "reception",
                    "agent": "xiaoai",
                    "action": "接收用户咨询",
                    "description": "小艾接收用户的健康咨询请求"
                },
                {
                    "id": "diagnosis_routing",
                    "agent": "xiaoai",
                    "action": "路由诊断请求",
                    "description": "根据咨询内容决定是否需要诊断服务"
                },
                {
                    "id": "tcm_diagnosis",
                    "agent": "xiaoke",
                    "action": "中医诊断",
                    "description": "小克进行中医体质辨识和诊断",
                    "condition": "需要诊断"
                },
                {
                    "id": "health_plan",
                    "agent": "soer",
                    "action": "制定健康计划",
                    "description": "索儿基于诊断结果制定个性化健康计划"
                },
                {
                    "id": "knowledge_support",
                    "agent": "laoke",
                    "action": "提供知识支持",
                    "description": "老克提供相关的健康知识和学习资源"
                },
                {
                    "id": "response_synthesis",
                    "agent": "xiaoai",
                    "action": "综合回复",
                    "description": "小艾整合各智能体的结果，给出综合回复"
                }
            ]
        }
        
        # 2. 农产品定制工作流
        product_customization_workflow = {
            "name": "农产品定制工作流",
            "description": "个性化农产品定制的完整流程",
            "steps": [
                {
                    "id": "requirement_analysis",
                    "agent": "xiaoai",
                    "action": "需求分析",
                    "description": "分析用户的农产品定制需求"
                },
                {
                    "id": "constitution_assessment",
                    "agent": "xiaoke",
                    "action": "体质评估",
                    "description": "评估用户体质，确定适合的食物类型"
                },
                {
                    "id": "nutrition_analysis",
                    "agent": "soer",
                    "action": "营养分析",
                    "description": "分析营养需求，制定饮食方案"
                },
                {
                    "id": "product_recommendation",
                    "agent": "xiaoke",
                    "action": "产品推荐",
                    "description": "推荐合适的农产品"
                },
                {
                    "id": "education_content",
                    "agent": "laoke",
                    "action": "教育内容",
                    "description": "提供食疗知识和使用指导"
                }
            ]
        }
        
        # 3. 健康数据分析工作流
        health_data_analysis_workflow = {
            "name": "健康数据分析工作流",
            "description": "多源健康数据的综合分析流程",
            "steps": [
                {
                    "id": "data_collection",
                    "agent": "xiaoai",
                    "action": "数据收集",
                    "description": "收集用户的多源健康数据"
                },
                {
                    "id": "sensor_analysis",
                    "agent": "soer",
                    "action": "传感器数据分析",
                    "description": "分析传感器和生物标志物数据"
                },
                {
                    "id": "tcm_interpretation",
                    "agent": "xiaoke",
                    "action": "中医解读",
                    "description": "从中医角度解读健康数据"
                },
                {
                    "id": "trend_prediction",
                    "agent": "soer",
                    "action": "趋势预测",
                    "description": "预测健康趋势和风险"
                },
                {
                    "id": "knowledge_correlation",
                    "agent": "laoke",
                    "action": "知识关联",
                    "description": "关联相关的健康知识和建议"
                },
                {
                    "id": "comprehensive_report",
                    "agent": "xiaoai",
                    "action": "综合报告",
                    "description": "生成综合健康分析报告"
                }
            ]
        }
        
        # 注册工作流
        workflows = [
            health_consultation_workflow,
            product_customization_workflow,
            health_data_analysis_workflow
        ]
        
        for workflow in workflows:
            self.workflows[workflow["name"]] = workflow
            logger.info(f"已注册工作流: {workflow['name']}")
    
    async def process_user_request(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理用户请求
        
        Args:
            user_request: 用户请求
            
        Returns:
            处理结果
        """
        try:
            user_id = user_request.get("user_id", "default_user")
            message = user_request.get("message", "")
            request_type = user_request.get("type", "general")
            
            # 使用 AI 路由器选择合适的智能体或工作流
            if request_type == "workflow":
                # 执行工作流
                workflow_name = user_request.get("workflow", "健康咨询工作流")
                result = await self._execute_workflow(workflow_name, user_request)
            else:
                # 单智能体处理
                target_agent = await self.ai_router.route_request(user_request)
                result = await self._process_with_agent(target_agent, user_request)
            
            return {
                "success": True,
                "user_id": user_id,
                "result": result,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            logger.error(f"处理用户请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
    
    async def _execute_workflow(self, workflow_name: str, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            workflow_name: 工作流名称
            user_request: 用户请求
            
        Returns:
            工作流执行结果
        """
        try:
            workflow = self.workflows.get(workflow_name)
            if not workflow:
                return {"error": f"工作流 {workflow_name} 不存在"}
            
            workflow_results = {}
            context = {"user_request": user_request}
            
            for step in workflow["steps"]:
                agent_id = step["agent"]
                action = step["action"]
                
                # 检查执行条件
                if "condition" in step:
                    if not self._check_condition(step["condition"], context):
                        continue
                
                # 获取对应的智能体
                agent = getattr(self, f"{agent_id}_agent", None)
                if not agent:
                    logger.warning(f"智能体 {agent_id} 不存在")
                    continue
                
                # 执行步骤
                step_result = await self._execute_workflow_step(agent, action, context)
                workflow_results[step["id"]] = step_result
                
                # 更新上下文
                context[step["id"]] = step_result
            
            return {
                "workflow": workflow_name,
                "results": workflow_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _execute_workflow_step(self, agent, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流步骤
        
        Args:
            agent: 智能体实例
            action: 动作名称
            context: 上下文
            
        Returns:
            步骤执行结果
        """
        try:
            user_request = context["user_request"]
            message = user_request.get("message", "")
            
            # 根据动作类型调用相应的智能体方法
            if action == "接收用户咨询":
                result = await agent.coordinate_four_diagnoses(
                    diagnosis_request={"symptoms": message, "type": "consultation"},
                    user_id=user_request.get("user_id", "")
                )
            elif action == "中医诊断":
                result = await agent.schedule_medical_resources(
                    user_id=user_request.get("user_id", ""),
                    resource_type="diagnosis",
                    constitution_type="",
                    requirements=[message]
                )
            elif action == "制定健康计划":
                result = await agent.generate_health_plan(
                    user_id=user_request.get("user_id", ""),
                    constitution_type="阳虚质",
                    health_goals=[message]
                )
            elif action == "提供知识支持":
                result = await agent.manage_knowledge_content(
                    query=message,
                    limit=5
                )
            else:
                # 通用处理
                result = {"action": action, "message": "步骤执行完成"}
            
            return result
            
        except Exception as e:
            logger.error(f"工作流步骤执行失败: {e}")
            return {"error": str(e)}
    
    def _check_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        检查执行条件
        
        Args:
            condition: 条件字符串
            context: 上下文
            
        Returns:
            条件是否满足
        """
        # 简化的条件检查逻辑
        if condition == "需要诊断":
            user_request = context.get("user_request", {})
            message = user_request.get("message", "")
            return any(keyword in message for keyword in ["诊断", "体质", "症状", "不舒服"])
        
        return True
    
    async def _process_with_agent(self, agent_name: str, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用指定智能体处理请求
        
        Args:
            agent_name: 智能体名称
            user_request: 用户请求
            
        Returns:
            处理结果
        """
        try:
            agent = getattr(self, f"{agent_name}_agent", None)
            if not agent:
                return {"error": f"智能体 {agent_name} 不存在"}
            
            # 创建任务对象
            task = type('Task', (), {
                'message': {"content": {"text": user_request.get("message", "")}},
                'user_id': user_request.get("user_id", ""),
                'artifacts': [],
                'status': None
            })()
            
            # 处理任务
            result_task = await agent.handle_task(task)
            
            # 提取结果
            if result_task.artifacts:
                response_text = result_task.artifacts[0]["parts"][0]["text"]
                return {"response": response_text, "agent": agent_name}
            else:
                return {"response": "处理完成", "agent": agent_name}
                
        except Exception as e:
            logger.error(f"智能体处理失败: {e}")
            return {"error": str(e)}
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """
        获取所有智能体的状态
        
        Returns:
            智能体状态信息
        """
        status = {
            "network_status": "active",
            "agents": {
                "xiaoai": {
                    "name": "小艾智能体",
                    "status": "active",
                    "capabilities": list(self.xiaoai_agent.agent_card.capabilities.keys())
                },
                "xiaoke": {
                    "name": "小克智能体", 
                    "status": "active",
                    "capabilities": list(self.xiaoke_agent.agent_card.capabilities.keys())
                },
                "laoke": {
                    "name": "老克智能体",
                    "status": "active", 
                    "capabilities": list(self.laoke_agent.agent_card.capabilities.keys())
                },
                "soer": {
                    "name": "索儿智能体",
                    "status": "active",
                    "capabilities": list(self.soer_agent.agent_card.capabilities.keys())
                }
            },
            "workflows": list(self.workflows.keys()),
            "total_agents": 4,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return status
    
    async def start_network(self):
        """启动智能体网络"""
        try:
            # 启动所有智能体
            agents = [
                self.xiaoai_agent,
                self.xiaoke_agent,
                self.laoke_agent,
                self.soer_agent
            ]
            
            for agent in agents:
                if hasattr(agent, 'start'):
                    await agent.start()
            
            logger.info("索克生活 A2A 智能体网络已启动")
            
        except Exception as e:
            logger.error(f"网络启动失败: {e}")
            raise
    
    async def stop_network(self):
        """停止智能体网络"""
        try:
            # 停止所有智能体
            agents = [
                self.xiaoai_agent,
                self.xiaoke_agent,
                self.laoke_agent,
                self.soer_agent
            ]
            
            for agent in agents:
                if hasattr(agent, 'stop'):
                    await agent.stop()
            
            logger.info("索克生活 A2A 智能体网络已停止")
            
        except Exception as e:
            logger.error(f"网络停止失败: {e}")
            raise


# 创建网络实例的工厂函数
def create_suoke_life_a2a_network(config: Optional[Dict[str, Any]] = None) -> SuokeLifeA2ANetwork:
    """
    创建索克生活 A2A 智能体网络实例
    
    Args:
        config: 网络配置
        
    Returns:
        A2A 智能体网络实例
    """
    return SuokeLifeA2ANetwork(config)


# 示例使用
async def main():
    """示例主函数"""
    # 创建网络
    network = create_suoke_life_a2a_network()
    
    # 启动网络
    await network.start_network()
    
    # 获取状态
    status = await network.get_agent_status()
    print("网络状态:", json.dumps(status, ensure_ascii=False, indent=2))
    
    # 处理用户请求示例
    user_requests = [
        {
            "user_id": "user123",
            "message": "我最近感觉很累，想了解一下我的体质",
            "type": "workflow",
            "workflow": "健康咨询工作流"
        },
        {
            "user_id": "user456", 
            "message": "我想定制一些适合我体质的农产品",
            "type": "workflow",
            "workflow": "农产品定制工作流"
        },
        {
            "user_id": "user789",
            "message": "帮我分析一下我的健康数据",
            "type": "general"
        }
    ]
    
    for request in user_requests:
        result = await network.process_user_request(request)
        print(f"\n用户请求: {request['message']}")
        print(f"处理结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 停止网络
    await network.stop_network()


if __name__ == "__main__":
    asyncio.run(main()) 