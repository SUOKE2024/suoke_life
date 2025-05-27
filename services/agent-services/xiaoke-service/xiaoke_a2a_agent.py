#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小克智能体 A2A 协议适配器
XiaoKe Agent A2A Protocol Adapter

将小克智能体服务包装为符合 A2A 协议的智能体
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from python_a2a import A2AServer, AgentCard, skill, agent, TaskStatus, TaskState, Message, TextContent, MessageRole

# 简化的模拟组件实现
class ResourceManager:
    """资源管理器模拟实现"""
    def schedule_resources(self, **kwargs):
        return {
            "scheduled_resources": [
                {"id": "res_001", "type": "中医诊所", "name": "康复中医诊所", "distance": "2.5km"},
                {"id": "res_002", "type": "专科医院", "name": "中医药大学附属医院", "distance": "5.1km"}
            ],
            "total": 2
        }
    
    def manage_appointment(self, **kwargs):
        return {
            "appointment_id": "apt_001",
            "status": "confirmed",
            "time": "2024-01-15 14:00:00",
            "doctor": "李医生",
            "location": "康复中医诊所"
        }

class ProductManager:
    """产品管理器模拟实现"""
    def customize_products(self, **kwargs):
        constitution_type = kwargs.get('constitution_type', '阳虚质')
        return {
            "customized_products": [
                {"id": "prod_001", "name": "温补养生茶", "suitable_for": constitution_type},
                {"id": "prod_002", "name": "有机红枣", "suitable_for": constitution_type},
                {"id": "prod_003", "name": "野生枸杞", "suitable_for": constitution_type}
            ],
            "total": 3
        }
    
    def trace_product(self, **kwargs):
        return {
            "product_id": kwargs.get('product_id'),
            "trace_info": {
                "origin": "有机农场",
                "harvest_date": "2024-01-01",
                "quality_grade": "A级",
                "blockchain_hash": "0x123456789abcdef"
            }
        }
    
    def recommend_products(self, **kwargs):
        return {
            "recommendations": [
                {"id": "rec_001", "name": "季节性养生套餐", "score": 0.95},
                {"id": "rec_002", "name": "体质调理组合", "score": 0.88}
            ]
        }

class SubscriptionRepository:
    """订阅仓库模拟实现"""
    def manage_subscription(self, **kwargs):
        action = kwargs.get('action', 'query')
        if action == 'create':
            return {"subscription_id": "sub_001", "status": "active"}
        elif action == 'cancel':
            return {"subscription_id": kwargs.get('subscription_id'), "status": "cancelled"}
        else:
            return {"subscriptions": [{"id": "sub_001", "type": "月度配送", "status": "active"}]}

logger = logging.getLogger(__name__)


@agent(
    name="小克智能体",
    description="索克生活平台的医疗资源管理和农产品定制智能体，专注于资源调度、产品定制和服务订阅",
    version="1.0.0",
    capabilities={
        "medical_resource_scheduling": True,
        "product_customization": True,
        "food_therapy_recommendation": True,
        "blockchain_traceability": True,
        "subscription_management": True,
        "appointment_management": True,
        "google_a2a_compatible": True
    }
)
class XiaoKeA2AAgent(A2AServer):
    """小克智能体 A2A 协议实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化小克 A2A 智能体
        
        Args:
            config: 配置字典
        """
        # 创建智能体卡片
        agent_card = AgentCard(
            name="小克智能体",
            description="索克生活平台的医疗资源管理和农产品定制智能体，专注于资源调度、产品定制和服务订阅",
            url="http://localhost:5002",
            version="1.0.0",
            capabilities={
                "medical_resource_scheduling": True,
                "product_customization": True,
                "food_therapy_recommendation": True,
                "blockchain_traceability": True,
                "subscription_management": True,
                "appointment_management": True,
                "google_a2a_compatible": True
            }
        )
        
        # 初始化 A2A 服务器
        super().__init__(agent_card=agent_card)
        
        # 初始化小克服务组件
        self.resource_manager = ResourceManager()
        self.product_manager = ProductManager()
        self.subscription_repo = SubscriptionRepository()
        
        logger.info("小克 A2A 智能体初始化完成")
    
    @skill(
        name="医疗资源调度",
        description="根据用户体质和需求调度医疗资源，包括医生预约、医院推荐等",
        tags=["医疗资源", "预约管理", "资源调度"]
    )
    async def schedule_medical_resources(self, user_id: str, resource_type: str, 
                                       constitution_type: str, location: str = "",
                                       requirements: List[str] = None) -> Dict[str, Any]:
        """
        医疗资源调度技能
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            constitution_type: 体质类型
            location: 位置
            requirements: 需求列表
            
        Returns:
            医疗资源调度结果
        """
        try:
            result = self.resource_manager.schedule_resources(
                user_id=user_id,
                resource_type=resource_type,
                constitution_type=constitution_type,
                location=location,
                requirements=requirements or [],
                page_size=10,
                page_number=1
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"医疗资源调度失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="预约管理",
        description="管理医疗预约，包括预约创建、修改、取消等",
        tags=["预约管理", "医疗服务", "时间安排"]
    )
    async def manage_appointment(self, user_id: str, doctor_id: str, 
                               appointment_type: str, preferred_time: str,
                               symptoms: str = "", constitution_type: str = "") -> Dict[str, Any]:
        """
        预约管理技能
        
        Args:
            user_id: 用户ID
            doctor_id: 医生ID
            appointment_type: 预约类型
            preferred_time: 首选时间
            symptoms: 症状描述
            constitution_type: 体质类型
            
        Returns:
            预约管理结果
        """
        try:
            result = self.resource_manager.manage_appointment(
                user_id=user_id,
                doctor_id=doctor_id,
                appointment_type=appointment_type,
                preferred_time=preferred_time,
                symptoms=symptoms,
                constitution_type=constitution_type,
                metadata={}
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"预约管理失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="农产品定制",
        description="根据用户体质和健康状况定制个性化农产品",
        tags=["农产品定制", "个性化推荐", "健康食品"]
    )
    async def customize_products(self, user_id: str, constitution_type: str,
                               health_conditions: List[str] = None,
                               preferences: List[str] = None,
                               season: str = "current") -> Dict[str, Any]:
        """
        农产品定制技能
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_conditions: 健康状况列表
            preferences: 偏好列表
            season: 季节
            
        Returns:
            农产品定制结果
        """
        try:
            result = self.product_manager.customize_products(
                user_id=user_id,
                constitution_type=constitution_type,
                health_conditions=health_conditions or [],
                preferences=preferences or [],
                season=season,
                packaging_preference="standard",
                quantity=1,
                need_delivery=True,
                delivery_address=""
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"农产品定制失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="产品溯源",
        description="提供农产品的区块链溯源信息，确保食品安全和质量",
        tags=["区块链溯源", "食品安全", "质量追踪"]
    )
    async def trace_product(self, product_id: str, batch_id: str = "",
                          trace_token: str = "") -> Dict[str, Any]:
        """
        产品溯源技能
        
        Args:
            product_id: 产品ID
            batch_id: 批次ID
            trace_token: 溯源令牌
            
        Returns:
            产品溯源结果
        """
        try:
            result = self.product_manager.trace_product(
                product_id=product_id,
                batch_id=batch_id,
                trace_token=trace_token
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"产品溯源失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="产品推荐",
        description="基于用户体质和健康状况推荐合适的农产品",
        tags=["产品推荐", "智能推荐", "健康匹配"]
    )
    async def recommend_products(self, user_id: str, constitution_type: str,
                               category: str = "", season: str = "current") -> Dict[str, Any]:
        """
        产品推荐技能
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            category: 产品类别
            season: 季节
            
        Returns:
            产品推荐结果
        """
        try:
            result = self.product_manager.recommend_products(
                user_id=user_id,
                constitution_type=constitution_type,
                category=category,
                season=season,
                page_size=10,
                page_number=1
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"产品推荐失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="订阅管理",
        description="管理用户的服务订阅，包括会员服务、定期配送等",
        tags=["订阅管理", "会员服务", "定期配送"]
    )
    async def manage_subscription(self, user_id: str, action: str,
                                subscription_type: str = "",
                                plan_id: str = "") -> Dict[str, Any]:
        """
        订阅管理技能
        
        Args:
            user_id: 用户ID
            action: 操作类型 (create, update, cancel, query)
            subscription_type: 订阅类型
            plan_id: 计划ID
            
        Returns:
            订阅管理结果
        """
        try:
            if action == "query":
                result = self.subscription_repo.get_user_subscriptions(user_id)
            elif action == "create":
                result = self.subscription_repo.create_subscription(
                    user_id, subscription_type, plan_id
                )
            elif action == "cancel":
                result = self.subscription_repo.cancel_subscription(user_id, plan_id)
            else:
                result = {"error": f"不支持的操作: {action}"}
            
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"订阅管理失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_task(self, task):
        """
        处理 A2A 任务
        
        Args:
            task: A2A 任务对象
            
        Returns:
            处理后的任务对象
        """
        try:
            # 解析消息内容
            message_data = task.message or {}
            content = message_data.get("content", {})
            
            if isinstance(content, dict):
                text = content.get("text", "")
            else:
                text = str(content)
            
            # 提取用户ID
            user_id = getattr(task, 'user_id', 'default_user')
            
            # 根据消息内容路由到相应的技能
            if "预约" in text or "挂号" in text:
                # 预约管理请求
                appointment_info = self._extract_appointment_info(text)
                result = await self.manage_appointment(
                    user_id=user_id,
                    doctor_id=appointment_info.get("doctor_id", ""),
                    appointment_type=appointment_info.get("type", "consultation"),
                    preferred_time=appointment_info.get("time", ""),
                    symptoms=appointment_info.get("symptoms", ""),
                    constitution_type=appointment_info.get("constitution", "")
                )
                
            elif "定制" in text or "农产品" in text:
                # 农产品定制请求
                customization_info = self._extract_customization_info(text)
                result = await self.customize_products(
                    user_id=user_id,
                    constitution_type=customization_info.get("constitution", ""),
                    health_conditions=customization_info.get("conditions", []),
                    preferences=customization_info.get("preferences", [])
                )
                
            elif "溯源" in text or "追踪" in text:
                # 产品溯源请求
                trace_info = self._extract_trace_info(text)
                result = await self.trace_product(
                    product_id=trace_info.get("product_id", ""),
                    batch_id=trace_info.get("batch_id", "")
                )
                
            elif "推荐" in text:
                # 产品推荐请求
                recommend_info = self._extract_recommend_info(text)
                result = await self.recommend_products(
                    user_id=user_id,
                    constitution_type=recommend_info.get("constitution", ""),
                    category=recommend_info.get("category", "")
                )
                
            elif "订阅" in text or "会员" in text:
                # 订阅管理请求
                subscription_info = self._extract_subscription_info(text)
                result = await self.manage_subscription(
                    user_id=user_id,
                    action=subscription_info.get("action", "query"),
                    subscription_type=subscription_info.get("type", ""),
                    plan_id=subscription_info.get("plan_id", "")
                )
                
            else:
                # 通用咨询
                result = await self._handle_general_consultation(text, user_id)
            
            # 构建响应
            response_text = self._format_response(result)
            
            task.artifacts = [{
                "parts": [{"type": "text", "text": response_text}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
            
        except Exception as e:
            logger.error(f"任务处理失败: {e}")
            task.artifacts = [{
                "parts": [{"type": "text", "text": f"处理失败: {str(e)}"}]
            }]
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message={"role": "agent", "content": {"type": "text", "text": f"处理失败: {str(e)}"}}
            )
        
        return task
    
    def _extract_appointment_info(self, text: str) -> Dict[str, Any]:
        """从文本中提取预约信息"""
        return {
            "doctor_id": "",
            "type": "consultation",
            "time": "",
            "symptoms": text,
            "constitution": ""
        }
    
    def _extract_customization_info(self, text: str) -> Dict[str, Any]:
        """从文本中提取定制信息"""
        return {
            "constitution": "",
            "conditions": [],
            "preferences": text.split()
        }
    
    def _extract_trace_info(self, text: str) -> Dict[str, Any]:
        """从文本中提取溯源信息"""
        return {
            "product_id": "",
            "batch_id": ""
        }
    
    def _extract_recommend_info(self, text: str) -> Dict[str, Any]:
        """从文本中提取推荐信息"""
        return {
            "constitution": "",
            "category": ""
        }
    
    def _extract_subscription_info(self, text: str) -> Dict[str, Any]:
        """从文本中提取订阅信息"""
        if "查询" in text:
            action = "query"
        elif "取消" in text:
            action = "cancel"
        else:
            action = "create"
        
        return {
            "action": action,
            "type": "",
            "plan_id": ""
        }
    
    async def _handle_general_consultation(self, text: str, user_id: str) -> Dict[str, Any]:
        """处理通用咨询"""
        return {
            "response": f"您好！我是小克智能体，专注于医疗资源管理和农产品定制。关于您的问题：{text}，我可以为您提供以下服务：",
            "services": [
                "医疗资源调度和预约管理",
                "个性化农产品定制",
                "产品区块链溯源查询",
                "智能产品推荐",
                "服务订阅管理"
            ],
            "success": True
        }
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """格式化响应内容"""
        if not result.get("success", True):
            return f"处理失败: {result.get('error', '未知错误')}"
        
        if "response" in result:
            response = result["response"]
            if "services" in result:
                response += "\n\n可用服务："
                for service in result["services"]:
                    response += f"\n• {service}"
            return response
        elif "data" in result:
            return json.dumps(result["data"], ensure_ascii=False, indent=2)
        else:
            return json.dumps(result, ensure_ascii=False, indent=2)


# 创建智能体实例的工厂函数
def create_xiaoke_a2a_agent(config: Optional[Dict[str, Any]] = None) -> XiaoKeA2AAgent:
    """
    创建小克 A2A 智能体实例
    
    Args:
        config: 配置字典
        
    Returns:
        小克 A2A 智能体实例
    """
    return XiaoKeA2AAgent(config) 