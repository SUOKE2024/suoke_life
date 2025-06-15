"""
智能体服务类

处理智能体交互相关的业务逻辑
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_service import BaseService
from ..clients.auth_client import get_auth_client
from ..core.conversation_manager import conversation_manager
from ..models.agent import AgentMessage, AgentResponse, ConversationHistory, MessageType


class AgentService(BaseService):
    """智能体服务类"""

    def __init__(self):
        super().__init__()
        self.collection_name = "conversations"
        self.auth_client = get_auth_client()

    async def process_message(
        self,
        user_id: str,
        message_content: str,
        conversation_id: Optional[str] = None,
        message_type: MessageType = MessageType.TEXT,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """处理用户消息"""
        try:
            # 获取用户档案
            user_profile = await self.auth_client.get_user_profile(user_id)
            
            # 使用对话管理器处理消息
            ai_response, response_metadata = await conversation_manager.process_message(
                user_id=user_id,
                message=message_content,
                conversation_id=conversation_id,
                user_profile=user_profile,
                context=context
            )
            
            # 创建消息对象
            agent_message = AgentMessage(
                message_id=str(uuid.uuid4()),
                user_id=user_id,
                content=message_content,
                message_type=message_type,
                timestamp=datetime.now()
            )

            # 创建响应对象
            agent_response = AgentResponse(
                response_id=str(uuid.uuid4()),
                conversation_id=response_metadata.get("conversation_id", conversation_id or str(uuid.uuid4())),
                message_id=agent_message.message_id,
                content=ai_response,
                confidence_score=0.9,  # 基于AI模型的置信度
                suggestions=response_metadata.get("suggestions", []),
                quick_replies=response_metadata.get("quick_replies", []),
                tcm_insights=self._extract_tcm_insights(response_metadata, user_profile),
                timestamp=datetime.now()
            )

            # 保存对话历史
            await self._save_conversation(user_id, agent_message, agent_response)

            await self.log_operation("process_message", True, {"user_id": user_id})
            return agent_response

        except Exception as e:
            await self.log_operation("process_message", False, {"error": str(e)})
            raise

    async def send_message(self, user_id: str, message: str, message_type: MessageType = MessageType.TEXT) -> AgentResponse:
        """发送消息给智能体（兼容旧接口）"""
        return await self.process_message(user_id, message, None, message_type)

    async def get_capabilities(self) -> Dict[str, Any]:
        """获取智能体能力"""
        return {
            "name": "索儿 (Soer)",
            "version": "2.0.0",
            "description": "索克生活健康管理智能助手",
            "capabilities": [
                {
                    "name": "健康咨询",
                    "description": "提供个性化健康建议和咨询",
                    "features": ["症状分析", "健康评估", "预防建议"]
                },
                {
                    "name": "营养分析",
                    "description": "食物营养成分分析和膳食建议",
                    "features": ["营养计算", "膳食规划", "食物搭配"]
                },
                {
                    "name": "运动指导",
                    "description": "个性化运动计划和健身指导",
                    "features": ["运动计划", "健身指导", "进度跟踪"]
                },
                {
                    "name": "中医养生",
                    "description": "基于中医理论的体质分析和养生建议",
                    "features": ["体质分析", "经络指导", "季节养生"]
                },
                {
                    "name": "生活方式",
                    "description": "睡眠、压力管理等生活方式建议",
                    "features": ["睡眠分析", "压力管理", "生活习惯"]
                }
            ],
            "supported_languages": ["中文", "English"],
            "ai_models": ["GPT-3.5", "GPT-4", "Claude-3"],
            "features": {
                "real_time_chat": True,
                "voice_interaction": False,
                "image_analysis": False,
                "multi_modal": False,
                "context_memory": True,
                "personalization": True,
                "tcm_integration": True
            }
        }

    async def get_conversation_history(self, user_id: str, limit: int = 50) -> Optional[ConversationHistory]:
        """获取对话历史"""
        try:
            if not self.mongodb:
                return None

            conversation = await self.mongodb[self.collection_name].find_one({"user_id": user_id})
            if conversation:
                # 限制返回的消息数量
                conversation["messages"] = conversation["messages"][-limit:]
                conversation["responses"] = conversation["responses"][-limit:]
                return ConversationHistory(**conversation)

            return None

        except Exception as e:
            await self.log_operation("get_conversation_history", False, {"error": str(e)})
            return None

    async def get_user_config(self, user_id: str) -> Dict[str, Any]:
        """获取用户配置"""
        try:
            user_profile = await self.user_service.get_user_profile(user_id)
            if not user_profile:
                return self._get_default_config()
            
            preferences = user_profile.get("preferences", {})
            return {
                "personality": preferences.get("personality", "friendly"),
                "expertise_level": preferences.get("expertise_level", "beginner"),
                "language": preferences.get("language", "zh-CN"),
                "response_length": preferences.get("response_length", "medium"),
                "use_emojis": preferences.get("use_emojis", True),
                "tcm_focus": preferences.get("tcm_focus", True),
                "notification_enabled": preferences.get("notification_enabled", True)
            }

        except Exception as e:
            await self.log_operation("get_user_config", False, {"error": str(e)})
            return self._get_default_config()

    async def update_user_config(self, user_id: str, config: Dict[str, Any]) -> bool:
        """更新用户配置"""
        try:
            # 获取当前用户档案
            user_profile = await self.user_service.get_user_profile(user_id)
            if not user_profile:
                return False
            
            # 更新偏好设置
            current_preferences = user_profile.get("preferences", {})
            current_preferences.update(config)
            
            # 使用用户服务更新档案
            from ..models.user import ProfileUpdateRequest
            update_request = ProfileUpdateRequest(preferences=current_preferences)
            
            success = await self.user_service.update_user_profile(user_id, update_request)
            
            if success:
                await self.log_operation("update_user_config", True, {"user_id": user_id})
            
            return success

        except Exception as e:
            await self.log_operation("update_user_config", False, {"error": str(e)})
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "personality": "friendly",
            "expertise_level": "beginner",
            "language": "zh-CN",
            "response_length": "medium",
            "use_emojis": True,
            "tcm_focus": True,
            "notification_enabled": True
        }

    def _extract_tcm_insights(self, response_metadata: Dict[str, Any], user_profile: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """提取中医相关洞察"""
        if not user_profile:
            return None
        
        tcm_insights = {}
        
        # 体质相关信息
        constitution = user_profile.get("tcm_constitution")
        if constitution:
            tcm_insights["constitution"] = constitution
            tcm_insights["constitution_advice"] = f"根据您的{constitution}体质特点，建议..."
        
        # 季节性建议
        current_month = datetime.now().month
        if current_month in [3, 4, 5]:
            season = "春季"
            tcm_insights["seasonal_advice"] = "春季养肝，宜疏肝理气"
        elif current_month in [6, 7, 8]:
            season = "夏季"
            tcm_insights["seasonal_advice"] = "夏季养心，宜清热解暑"
        elif current_month in [9, 10, 11]:
            season = "秋季"
            tcm_insights["seasonal_advice"] = "秋季养肺，宜润燥养阴"
        else:
            season = "冬季"
            tcm_insights["seasonal_advice"] = "冬季养肾，宜温阳补肾"
        
        tcm_insights["current_season"] = season
        
        # 根据意图添加特定建议
        intent = response_metadata.get("intent")
        if intent == "tcm_consultation":
            tcm_insights["consultation_type"] = "中医咨询"
            tcm_insights["recommended_actions"] = ["体质测试", "经络调理", "饮食调养"]
        
        return tcm_insights if tcm_insights else None

    async def _save_conversation(self, user_id: str, message: AgentMessage, response: AgentResponse):
        """保存对话历史"""
        if not self.mongodb:
            return

        # 查找或创建对话历史
        conversation = await self.mongodb[self.collection_name].find_one({"user_id": user_id})

        if conversation:
            # 更新现有对话
            await self.mongodb[self.collection_name].update_one(
                {"user_id": user_id},
                {
                    "$push": {
                        "messages": message.dict(),
                        "responses": response.dict()
                    },
                    "$set": {"updated_at": datetime.now()}
                }
            )
        else:
            # 创建新对话
            new_conversation = ConversationHistory(
                user_id=user_id,
                messages=[message],
                responses=[response]
            )
            await self.mongodb[self.collection_name].insert_one(new_conversation.dict())

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "service": "AgentService",
            "status": "healthy",
            "mongodb_connected": self.mongodb is not None,
            "redis_connected": self.redis is not None,
            "ai_client_status": conversation_manager.health_check()
        }

        # 测试数据库连接
        if self.mongodb:
            try:
                await self.mongodb.command("ping")
                status["mongodb_ping"] = True
            except Exception:
                status["mongodb_ping"] = False
                status["status"] = "degraded"

        return status