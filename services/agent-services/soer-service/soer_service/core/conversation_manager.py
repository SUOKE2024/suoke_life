"""
对话管理模块

处理多轮对话、上下文记忆、个性化响应等功能
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .ai_client import AIClient, AIMessage
from ..models.user import TCMConstitution


class ConversationContext:
    """对话上下文类"""
    
    def __init__(self, user_id: str, conversation_id: Optional[str] = None):
        self.user_id = user_id
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.messages: List[Dict[str, Any]] = []
        self.user_profile: Dict[str, Any] = {}
        self.session_data: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.max_history = 20  # 最大历史消息数
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """添加消息到上下文"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        # 保持历史消息在限制范围内
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_recent_messages(self, count: int = 10) -> List[AIMessage]:
        """获取最近的消息"""
        recent = self.messages[-count:] if count > 0 else self.messages
        return [AIMessage(msg["role"], msg["content"], msg.get("metadata")) for msg in recent]
    
    def update_user_profile(self, profile: Dict[str, Any]):
        """更新用户档案"""
        self.user_profile.update(profile)
        self.updated_at = datetime.now()
    
    def set_session_data(self, key: str, value: Any):
        """设置会话数据"""
        self.session_data[key] = value
        self.updated_at = datetime.now()
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """获取会话数据"""
        return self.session_data.get(key, default)


class PersonalityEngine:
    """个性化引擎"""
    
    def __init__(self):
        self.personality_templates = {
            "friendly": {
                "tone": "友好亲切",
                "style": "温暖关怀",
                "emoji_usage": True,
                "response_length": "medium"
            },
            "professional": {
                "tone": "专业严谨",
                "style": "客观准确",
                "emoji_usage": False,
                "response_length": "detailed"
            },
            "casual": {
                "tone": "轻松随意",
                "style": "简洁明了",
                "emoji_usage": True,
                "response_length": "short"
            }
        }
    
    def get_personality_prompt(self, user_profile: Dict[str, Any]) -> str:
        """根据用户档案生成个性化提示"""
        personality = user_profile.get("preferences", {}).get("personality", "friendly")
        template = self.personality_templates.get(personality, self.personality_templates["friendly"])
        
        # 基础个性化提示
        prompt = f"""你是索儿，索克生活平台的健康管理智能助手。你的特点：
- 语调：{template['tone']}
- 风格：{template['style']}
- 回答长度：{template['response_length']}
"""
        
        if template['emoji_usage']:
            prompt += "- 适当使用表情符号让对话更生动\n"
        
        # 添加用户特定信息
        if user_profile.get("full_name"):
            prompt += f"- 用户姓名：{user_profile['full_name']}\n"
        
        if user_profile.get("tcm_constitution"):
            constitution = user_profile["tcm_constitution"]
            prompt += f"- 用户体质：{constitution}，请结合中医理论提供建议\n"
        
        if user_profile.get("health_goals"):
            goals = ", ".join(user_profile["health_goals"])
            prompt += f"- 健康目标：{goals}\n"
        
        if user_profile.get("dietary_preferences"):
            preferences = ", ".join(user_profile["dietary_preferences"])
            prompt += f"- 饮食偏好：{preferences}\n"
        
        prompt += "\n请根据用户的具体情况提供个性化的健康建议。"
        
        return prompt


class TCMKnowledgeBase:
    """中医知识库"""
    
    def __init__(self):
        self.constitution_characteristics = {
            TCMConstitution.BALANCED: {
                "特点": "体质平和，精力充沛，睡眠良好",
                "养生建议": "保持现有的良好生活习惯，适度运动，饮食均衡",
                "饮食宜忌": "宜：五谷杂粮、新鲜蔬果；忌：过度偏食"
            },
            TCMConstitution.QI_DEFICIENCY: {
                "特点": "容易疲劳，气短懒言，抵抗力差",
                "养生建议": "适度运动，避免过度劳累，注意保暖",
                "饮食宜忌": "宜：山药、大枣、人参；忌：生冷食物"
            },
            TCMConstitution.YANG_DEFICIENCY: {
                "特点": "畏寒怕冷，手脚冰凉，精神不振",
                "养生建议": "温阳补肾，适当运动，避免寒凉",
                "饮食宜忌": "宜：羊肉、生姜、肉桂；忌：寒凉食物"
            },
            TCMConstitution.YIN_DEFICIENCY: {
                "特点": "口干咽燥，手脚心热，失眠多梦",
                "养生建议": "滋阴润燥，避免熬夜，保持心情平和",
                "饮食宜忌": "宜：银耳、百合、枸杞；忌：辛辣燥热"
            },
            TCMConstitution.PHLEGM_DAMPNESS: {
                "特点": "体形肥胖，胸闷痰多，困倦乏力",
                "养生建议": "化痰除湿，适度运动，控制体重",
                "饮食宜忌": "宜：薏米、冬瓜、陈皮；忌：甜腻油腻"
            },
            TCMConstitution.DAMP_HEAT: {
                "特点": "面部油腻，口苦口干，大便黏腻",
                "养生建议": "清热利湿，避免湿热环境",
                "饮食宜忌": "宜：绿豆、苦瓜、茯苓；忌：辛辣油腻"
            },
            TCMConstitution.BLOOD_STASIS: {
                "特点": "面色晦暗，容易健忘，身体疼痛",
                "养生建议": "活血化瘀，适度运动，保持心情舒畅",
                "饮食宜忌": "宜：山楂、红花、当归；忌：寒凉收敛"
            },
            TCMConstitution.QI_STAGNATION: {
                "特点": "情绪不稳，胸胁胀满，多愁善感",
                "养生建议": "疏肝理气，调节情志，适当运动",
                "饮食宜忌": "宜：玫瑰花、柑橘、佛手；忌：收敛酸涩"
            },
            TCMConstitution.SPECIAL_DIATHESIS: {
                "特点": "过敏体质，适应能力差",
                "养生建议": "避免过敏原，增强体质，谨慎用药",
                "饮食宜忌": "宜：益气固表食物；忌：致敏食物"
            }
        }
        
        self.seasonal_advice = {
            "spring": "春季养肝，宜疏肝理气，多食绿色蔬菜",
            "summer": "夏季养心，宜清热解暑，适度运动",
            "autumn": "秋季养肺，宜润燥养阴，多食白色食物",
            "winter": "冬季养肾，宜温阳补肾，适当进补"
        }
    
    def get_constitution_advice(self, constitution: TCMConstitution) -> Dict[str, str]:
        """获取体质建议"""
        return self.constitution_characteristics.get(constitution, {})
    
    def get_seasonal_advice(self, season: str) -> str:
        """获取季节性建议"""
        return self.seasonal_advice.get(season, "根据季节特点调整生活方式")


class ConversationManager:
    """对话管理器"""
    
    def __init__(self):
        self.ai_client = AIClient()
        self.personality_engine = PersonalityEngine()
        self.tcm_knowledge = TCMKnowledgeBase()
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.conversation_timeout = timedelta(hours=2)  # 对话超时时间
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        处理用户消息
        
        Args:
            user_id: 用户ID
            message: 用户消息
            conversation_id: 对话ID
            user_profile: 用户档案
            context: 额外上下文
        
        Returns:
            (AI响应, 响应元数据)
        """
        # 获取或创建对话上下文
        conv_context = self._get_or_create_conversation(user_id, conversation_id)
        
        # 更新用户档案
        if user_profile:
            conv_context.update_user_profile(user_profile)
        
        # 添加用户消息
        conv_context.add_message("user", message, context)
        
        # 意图识别
        intent_data = await self.ai_client.extract_intent(message)
        intent = intent_data.get("intent", "general_chat")
        
        # 情感分析
        sentiment_data = await self.ai_client.analyze_sentiment(message)
        
        # 构建系统提示
        system_prompt = self._build_system_prompt(conv_context, intent)
        
        # 构建消息历史
        messages = [AIMessage("system", system_prompt)]
        messages.extend(conv_context.get_recent_messages(8))  # 获取最近8条消息
        
        # 生成AI响应
        ai_response = await self.ai_client.chat_completion(
            messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # 后处理响应
        processed_response, response_metadata = self._post_process_response(
            ai_response, intent, conv_context, sentiment_data
        )
        
        # 添加AI响应到上下文
        conv_context.add_message("assistant", processed_response, response_metadata)
        
        return processed_response, response_metadata
    
    def _get_or_create_conversation(self, user_id: str, conversation_id: Optional[str]) -> ConversationContext:
        """获取或创建对话上下文"""
        if conversation_id and conversation_id in self.active_conversations:
            conv_context = self.active_conversations[conversation_id]
            # 检查是否超时
            if datetime.now() - conv_context.updated_at > self.conversation_timeout:
                # 超时则创建新对话
                conv_context = ConversationContext(user_id)
                self.active_conversations[conv_context.conversation_id] = conv_context
        else:
            # 创建新对话
            conv_context = ConversationContext(user_id, conversation_id)
            self.active_conversations[conv_context.conversation_id] = conv_context
        
        return conv_context
    
    def _build_system_prompt(self, conv_context: ConversationContext, intent: str) -> str:
        """构建系统提示"""
        # 基础个性化提示
        base_prompt = self.personality_engine.get_personality_prompt(conv_context.user_profile)
        
        # 根据意图添加专业知识
        if intent == "tcm_consultation":
            tcm_prompt = "\n\n你特别擅长中医养生咨询，请结合中医理论提供建议。"
            base_prompt += tcm_prompt
            
            # 添加体质相关建议
            constitution = conv_context.user_profile.get("tcm_constitution")
            if constitution:
                constitution_advice = self.tcm_knowledge.get_constitution_advice(constitution)
                if constitution_advice:
                    base_prompt += f"\n\n用户体质特点：{constitution_advice}"
        
        elif intent == "nutrition_analysis":
            nutrition_prompt = "\n\n你特别擅长营养分析，请提供科学的营养建议。"
            base_prompt += nutrition_prompt
        
        elif intent == "exercise_plan":
            exercise_prompt = "\n\n你特别擅长运动规划，请提供个性化的运动建议。"
            base_prompt += exercise_prompt
        
        # 添加当前季节建议
        current_season = self._get_current_season()
        seasonal_advice = self.tcm_knowledge.get_seasonal_advice(current_season)
        base_prompt += f"\n\n当前季节养生要点：{seasonal_advice}"
        
        return base_prompt
    
    def _post_process_response(
        self,
        response: str,
        intent: str,
        conv_context: ConversationContext,
        sentiment_data: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """后处理AI响应"""
        metadata = {
            "intent": intent,
            "sentiment": sentiment_data,
            "conversation_id": conv_context.conversation_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # 根据情感调整响应
        if sentiment_data.get("sentiment") == "negative":
            # 如果用户情绪消极，添加更多关怀
            if not any(word in response for word in ["理解", "关心", "支持"]):
                response = "我理解您的感受，" + response
        
        # 添加建议和快速回复
        suggestions = self._generate_suggestions(intent, conv_context)
        quick_replies = self._generate_quick_replies(intent)
        
        metadata.update({
            "suggestions": suggestions,
            "quick_replies": quick_replies
        })
        
        return response, metadata
    
    def _generate_suggestions(self, intent: str, conv_context: ConversationContext) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if intent == "health_query":
            suggestions = ["查看健康报告", "制定健康计划", "咨询专家"]
        elif intent == "nutrition_analysis":
            suggestions = ["查看营养建议", "制定膳食计划", "食物搭配建议"]
        elif intent == "exercise_plan":
            suggestions = ["个性化运动计划", "运动记录", "健身指导"]
        elif intent == "tcm_consultation":
            suggestions = ["体质测试", "中医养生", "季节性调理"]
        else:
            suggestions = ["健康咨询", "营养分析", "运动计划"]
        
        return suggestions
    
    def _generate_quick_replies(self, intent: str) -> List[str]:
        """生成快速回复"""
        quick_replies = []
        
        if intent == "health_query":
            quick_replies = ["我想了解更多", "制定计划", "预约咨询"]
        elif intent == "nutrition_analysis":
            quick_replies = ["查看详情", "保存建议", "分享给朋友"]
        elif intent == "exercise_plan":
            quick_replies = ["开始锻炼", "调整计划", "记录进度"]
        else:
            quick_replies = ["继续聊天", "查看建议", "结束对话"]
        
        return quick_replies
    
    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"
    
    def get_conversation_history(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """获取对话历史"""
        if conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id].messages
        return None
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """清除对话"""
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
            return True
        return False
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "active_conversations": len(self.active_conversations),
            "ai_client_status": self.ai_client.health_check()
        }


# 全局对话管理器实例
conversation_manager = ConversationManager()