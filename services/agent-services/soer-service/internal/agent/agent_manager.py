#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索尔智能体管理器
负责协调索尔智能体的不同功能组件，处理用户请求，生成健康计划和生活建议
"""
import logging
import asyncio
import uuid
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from internal.agent.model_factory import ModelFactory
from internal.repository.session_repository import SessionRepository
from internal.repository.knowledge_repository import KnowledgeRepository
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class AgentManager:
    """索尔智能体管理器"""
    
    def __init__(self, session_repository=None, knowledge_repository=None):
        """初始化智能体管理器"""
        logger.info("初始化索尔智能体管理器")
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 初始化依赖组件
        self.session_repository = session_repository or SessionRepository()
        self.knowledge_repository = knowledge_repository or KnowledgeRepository()
        
        # 初始化模型工厂
        self.model_factory = ModelFactory(self.config)
        
        # 加载提示词模板
        self.prompt_templates = self._load_prompt_templates()
        
        # 会话配置
        self.conversation_config = self.config.get_section('conversation')
        self.system_prompt = self.conversation_config.get('system_prompt', '')
        self.max_history_turns = self.conversation_config.get('max_history_turns', 20)
        
        # 活跃会话状态
        self.active_sessions = {}
        
        # 初始化定期内存清理任务
        asyncio.create_task(self._schedule_session_cleanup())
        
        logger.info("索尔智能体管理器初始化完成")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载提示词模板"""
        # 从配置目录加载提示词模板
        try:
            templates_dir = os.path.join("config", "prompts")
            templates = {}
            
            if os.path.exists(templates_dir):
                for filename in os.listdir(templates_dir):
                    if filename.endswith(".txt") or filename.endswith(".prompt"):
                        template_name = os.path.splitext(filename)[0]
                        file_path = os.path.join(templates_dir, filename)
                        
                        with open(file_path, "r", encoding="utf-8") as f:
                            templates[template_name] = f.read()
                            
                logger.info(f"已加载{len(templates)}个提示词模板")
            else:
                logger.warning(f"提示词模板目录不存在: {templates_dir}")
                
            return templates
        except Exception as e:
            logger.error(f"加载提示词模板失败: {str(e)}")
            return {}
    
    async def _schedule_session_cleanup(self):
        """定期清理过期会话"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时执行一次
                
                # 清理内存中的过期会话
                expired_count = self.cleanup_expired_sessions(max_age_minutes=60)
                logger.info(f"清理了{expired_count}个过期会话")
                
                # 清理数据库中的过期会话(保留90天的数据)
                if self.session_repository:
                    db_expired_count = await self.session_repository.delete_expired_sessions(days=90)
                    logger.info(f"清理了{db_expired_count}个数据库过期会话")
            except Exception as e:
                logger.error(f"会话清理任务异常: {str(e)}")
    
    async def process_user_input(self, user_id: str, input_data: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理用户输入
        
        Args:
            user_id: 用户ID
            input_data: 用户输入数据
            session_id: 会话ID，可选
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 确保会话ID存在
        if not session_id:
            session_id = await self.session_repository.create_session(user_id)
            logger.info(f"为用户{user_id}创建新会话: {session_id}")
        
        # 记录请求指标
        self.metrics.increment_counter("soer_requests", {"user_id": user_id})
        
        try:
            # 获取用户消息
            user_message = input_data.get("message", "")
            message_type = input_data.get("type", "text")
            context = input_data.get("context", {})
            
            # 获取会话历史
            session_messages = await self.session_repository.get_latest_messages(session_id, self.max_history_turns)
            
            # 保存用户消息
            message_metadata = {
                "type": message_type,
                "context": context
            }
            await self.session_repository.save_message(session_id, "user", user_message, message_metadata)
            
            # 处理用户输入类型
            if message_type == "health_plan_request":
                response = await self._generate_health_plan(user_id, user_message, session_id, session_messages, context)
            elif message_type == "lifestyle_advice":
                response = await self._generate_lifestyle_advice(user_id, user_message, session_id, session_messages, context)
            elif message_type == "health_query":
                response = await self._answer_health_query(user_id, user_message, session_id, session_messages, context)
            else:
                # 默认对话处理
                response = await self._handle_general_conversation(user_id, user_message, session_id, session_messages, context)
            
            # 保存系统响应
            agent_message = response.get("message", "")
            agent_metadata = {
                "type": response.get("type", "text"),
                "is_memory_anchor": response.get("is_memory_anchor", False),
                "topic": response.get("topic", "general"),
                "importance": response.get("importance", 0),
                "context": response.get("context", {})
            }
            
            await self.session_repository.save_message(session_id, "agent", agent_message, agent_metadata)
            
            # 提取并保存用户洞察
            if response.get("extract_insights", False) and self.knowledge_repository:
                insights = response.get("insights", [])
                for insight in insights:
                    await self.knowledge_repository.add_user_insight(user_id, insight)
            
            # 更新会话信息
            session_update = {
                "last_activity": datetime.now().isoformat()
            }
            
            # 添加健康关注点
            if response.get("health_focus"):
                session_update["health_focus"] = response.get("health_focus")
            
            # 添加会话标签
            if response.get("tags"):
                session_update["tags"] = response.get("tags")
            
            await self.session_repository.update_session(session_id, session_update)
            
            return {
                "session_id": session_id,
                "message": agent_message,
                "type": response.get("type", "text"),
                "suggestions": response.get("suggestions", []),
                "references": response.get("references", []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"处理用户输入失败: {str(e)}")
            
            # 保存错误消息
            error_message = "抱歉，我现在无法处理您的请求。请稍后再试。"
            await self.session_repository.save_message(session_id, "agent", error_message, {"error": str(e)})
            
            return {
                "session_id": session_id,
                "message": error_message,
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_general_conversation(
        self, 
        user_id: str, 
        message: str, 
        session_id: str,
        session_messages: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理一般对话
        
        Args:
            user_id: 用户ID
            message: 用户消息
            session_id: 会话ID
            session_messages: 会话历史消息
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        # 构建消息历史
        messages = self._format_message_history(session_messages)
        
        # 检索用户记忆锚点(重要记忆)
        memory_anchors = await self.session_repository.get_memory_anchors(user_id, limit=3)
        memory_context = ""
        if memory_anchors:
            memory_context = "用户重要记忆:\n"
            for i, anchor in enumerate(memory_anchors, 1):
                memory_context += f"{i}. {anchor['content']}\n"
        
        # 获取用户偏好
        user_preferences = {}
        if self.knowledge_repository:
            prefs = await self.knowledge_repository.get_user_preferences(user_id)
            if prefs:
                user_preferences = prefs
        
        # 构建系统提示
        system_prompt = self.system_prompt
        if memory_context:
            system_prompt += f"\n\n{memory_context}"
        
        if user_preferences:
            pref_str = "用户偏好:\n"
            for key, value in user_preferences.items():
                if key not in ["id", "_id", "user_id", "created_at", "updated_at"]:
                    if isinstance(value, list):
                        pref_str += f"{key}: {', '.join(value)}\n"
                    else:
                        pref_str += f"{key}: {value}\n"
            system_prompt += f"\n\n{pref_str}"
        
        # 添加系统消息
        messages.insert(0, {"role": "system", "content": system_prompt})
        
        # 获取用户洞察
        user_insights = []
        if self.knowledge_repository:
            insights = await self.knowledge_repository.get_user_insights(
                user_id=user_id, 
                min_confidence=0.7,
                limit=5
            )
            user_insights = insights
        
        # 分析用户消息是否需要创建记忆锚点
        is_memory_anchor = False
        importance = 0
        topics = []
        
        # 简单启发式判断消息重要性
        important_keywords = ["记住", "请记住", "重要", "注意", "过敏", "不能吃", "喜欢", "不喜欢", "习惯"]
        for keyword in important_keywords:
            if keyword in message:
                is_memory_anchor = True
                importance += 2
                
        # 分析主题
        health_topic_keywords = {
            "饮食": ["饮食", "食物", "吃", "喝", "营养", "饮料", "餐", "菜"],
            "运动": ["运动", "锻炼", "健身", "跑步", "游泳", "瑜伽", "步行"],
            "睡眠": ["睡眠", "睡觉", "失眠", "梦", "床", "休息"],
            "心理": ["情绪", "心理", "压力", "焦虑", "抑郁", "心情", "放松"],
            "医疗": ["疾病", "症状", "医生", "检查", "治疗", "药物", "疼痛"]
        }
        
        for topic, keywords in health_topic_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    topics.append(topic)
                    break
        
        topics = list(set(topics))  # 去重
        
        # 使用LLM生成回复
        response = await self.model_factory.generate_response(
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )
        
        # 分析响应中是否包含需要记忆的信息
        response_content = response.get("content", "")
        
        # 同样分析响应中的重要信息
        for keyword in important_keywords:
            if keyword in response_content:
                is_memory_anchor = True
                importance += 1
        
        # 如果是重要内容，从响应中提取洞察
        insights = []
        if is_memory_anchor and importance >= 3:
            # 提取可能的用户洞察
            insight_types = ["preference", "health_condition", "lifestyle_habit", "goal"]
            for insight_type in insight_types:
                # 简单启发式提取
                if insight_type == "preference" and ("喜欢" in message or "不喜欢" in message or "偏好" in message):
                    insights.append({
                        "type": insight_type,
                        "content": message,
                        "category": topics[0] if topics else "general",
                        "confidence": 0.8,
                        "importance": importance,
                        "tags": topics
                    })
                elif insight_type == "health_condition" and ("过敏" in message or "症状" in message or "疾病" in message):
                    insights.append({
                        "type": insight_type,
                        "content": message,
                        "category": "medical",
                        "confidence": 0.9,  # 健康状况通常更重要
                        "importance": importance + 2,
                        "tags": topics
                    })
        
        # 构建响应
        return {
            "message": response_content,
            "type": "text",
            "is_memory_anchor": is_memory_anchor,
            "importance": importance,
            "topic": topics[0] if topics else "general",
            "topics": topics,
            "context": context,
            "extract_insights": len(insights) > 0,
            "insights": insights,
            "suggestions": [],
            "references": []
        }
    
    async def _generate_health_plan(
        self, 
        user_id: str, 
        message: str, 
        session_id: str,
        session_messages: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成健康计划
        
        Args:
            user_id: 用户ID
            message: 用户消息
            session_id: 会话ID
            session_messages: 会话历史消息
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        # 实现健康计划生成逻辑...
        # 获取用户偏好和洞察
        user_preferences = {}
        user_insights = []
        
        if self.knowledge_repository:
            prefs = await self.knowledge_repository.get_user_preferences(user_id)
            if prefs:
                user_preferences = prefs
                
            insights = await self.knowledge_repository.get_user_insights(
                user_id=user_id, 
                min_confidence=0.6,
                limit=10
            )
            user_insights = insights
        
        # 构建提示
        health_plan_prompt = self.prompt_templates.get("health_plan", "")
        if not health_plan_prompt:
            health_plan_prompt = "请为用户生成一个健康计划，考虑以下要素:\n1. 用户的健康目标\n2. 用户的健康状况和偏好\n3. 可持续性和可行性\n请提供具体的饮食、运动和生活习惯建议。"
        
        # 添加用户偏好和洞察
        preferences_text = "\n用户偏好:"
        if user_preferences:
            for key, value in user_preferences.items():
                if key not in ["id", "_id", "user_id", "created_at", "updated_at"]:
                    if isinstance(value, list):
                        preferences_text += f"\n- {key}: {', '.join(value)}"
                    else:
                        preferences_text += f"\n- {key}: {value}"
        else:
            preferences_text += "\n- 无已知偏好"
        
        insights_text = "\n用户健康洞察:"
        if user_insights:
            for insight in user_insights:
                insights_text += f"\n- {insight.get('content', '')}"
        else:
            insights_text += "\n- 无已知洞察"
        
        # 构建消息
        messages = [
            {"role": "system", "content": self.system_prompt + "\n\n" + health_plan_prompt + preferences_text + insights_text},
        ]
        
        # 添加历史消息
        history_messages = self._format_message_history(session_messages[-5:])  # 只使用最近的5条消息
        messages.extend(history_messages)
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        # 生成响应
        response = await self.model_factory.generate_response(
            messages=messages,
            max_tokens=1500,
            temperature=0.5
        )
        
        response_content = response.get("content", "")
        
        # 自动提取健康计划的关注点
        health_focus = []
        if "饮食" in response_content or "营养" in response_content:
            health_focus.append("nutrition")
        if "运动" in response_content or "健身" in response_content:
            health_focus.append("exercise")
        if "睡眠" in response_content:
            health_focus.append("sleep")
        if "压力" in response_content or "情绪" in response_content:
            health_focus.append("mental_health")
        
        # 提取可能的建议
        suggestions = []
        # 简单的启发式提取，实际应用中可能需要更复杂的算法
        lines = response_content.split("\n")
        for line in lines:
            if "建议" in line or ":" in line or "：" in line:
                if len(line) > 10 and len(line) < 100:  # 合理长度的建议
                    suggestions.append(line.strip())
        
        # 限制建议数量
        suggestions = suggestions[:5]
        
        return {
            "message": response_content,
            "type": "health_plan",
            "is_memory_anchor": True,  # 健康计划通常是重要信息
            "importance": 8,
            "topic": "health_plan",
            "topics": ["health", "planning"] + health_focus,
            "health_focus": health_focus,
            "context": context,
            "suggestions": suggestions,
            "tags": ["health_plan"] + health_focus,
            "references": []
        }
    
    async def _generate_lifestyle_advice(
        self, 
        user_id: str, 
        message: str, 
        session_id: str,
        session_messages: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成生活方式建议
        
        Args:
            user_id: 用户ID
            message: 用户消息
            session_id: 会话ID
            session_messages: 会话历史消息
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        # 获取个性化建议
        recommendations = []
        if self.knowledge_repository:
            recommendations = await self.knowledge_repository.get_personalized_recommendations(
                user_id=user_id,
                limit=3
            )
        
        # 构建提示
        lifestyle_prompt = self.prompt_templates.get("lifestyle_advice", "")
        if not lifestyle_prompt:
            lifestyle_prompt = "请为用户提供生活方式建议，考虑以下方面:\n1. 饮食习惯\n2. 运动建议\n3. 睡眠质量\n4. 压力管理\n5. 日常习惯\n请给出具体、可行的建议，帮助用户改善生活质量。"
        
        # 添加推荐内容
        if recommendations:
            recommendations_text = "\n系统推荐给用户的个性化内容:"
            for rec in recommendations:
                recommendations_text += f"\n- {rec.get('title', '')}: {rec.get('summary', '')}"
            lifestyle_prompt += recommendations_text
        
        # 构建消息
        messages = [
            {"role": "system", "content": self.system_prompt + "\n\n" + lifestyle_prompt},
        ]
        
        # 添加历史消息
        history_messages = self._format_message_history(session_messages[-5:])
        messages.extend(history_messages)
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        # 生成响应
        response = await self.model_factory.generate_response(
            messages=messages,
            max_tokens=1200,
            temperature=0.6
        )
        
        response_content = response.get("content", "")
        
        # 提取建议
        suggestions = []
        lines = response_content.split("\n")
        for line in lines:
            if (":" in line or "：" in line) and len(line) > 10:
                suggestions.append(line.strip())
        
        suggestions = suggestions[:5]
        
        # 提取主题标签
        topics = []
        lifestyle_keywords = {
            "饮食": ["饮食", "食物", "餐", "营养", "食谱"],
            "运动": ["运动", "锻炼", "健身", "活动"],
            "睡眠": ["睡眠", "休息", "睡觉"],
            "放松": ["放松", "压力", "冥想", "休闲"],
            "习惯": ["习惯", "日常", "常规"]
        }
        
        for topic, keywords in lifestyle_keywords.items():
            for keyword in keywords:
                if keyword in response_content.lower():
                    topics.append(topic)
                    break
        
        topics = list(set(topics))
        
        # 提取参考资料
        references = []
        for rec in recommendations:
            references.append({
                "title": rec.get("title", ""),
                "id": rec.get("id", ""),
                "type": "recommendation"
            })
        
        return {
            "message": response_content,
            "type": "lifestyle_advice",
            "is_memory_anchor": True,
            "importance": 7,
            "topic": "lifestyle",
            "topics": topics,
            "context": context,
            "suggestions": suggestions,
            "tags": ["lifestyle"] + topics,
            "references": references
        }
    
    async def _answer_health_query(
        self, 
        user_id: str, 
        message: str, 
        session_id: str,
        session_messages: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        回答健康查询
        
        Args:
            user_id: 用户ID
            message: 用户消息
            session_id: 会话ID
            session_messages: 会话历史消息
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        # 搜索相关健康知识
        knowledge_items = []
        if self.knowledge_repository:
            # 简单的关键词提取
            keywords = message.split()
            # 去除停用词和标点
            keywords = [k for k in keywords if len(k) > 1 and k not in ["的", "了", "是", "什么", "如何", "为什么"]]
            
            if keywords:
                # 搜索相关知识
                knowledge_items = await self.knowledge_repository.search_health_knowledge(
                    query=" ".join(keywords),
                    limit=3
                )
        
        # 构建提示
        health_query_prompt = self.prompt_templates.get("health_query", "")
        if not health_query_prompt:
            health_query_prompt = "请回答用户的健康问题，提供准确、科学的信息。如果是专业医疗问题，建议用户咨询医生。"
        
        # 添加知识项
        if knowledge_items:
            knowledge_text = "\n相关健康知识:"
            for item in knowledge_items:
                knowledge_text += f"\n- {item.get('title', '')}: {item.get('summary', '')}"
            health_query_prompt += knowledge_text
        
        # 构建消息
        messages = [
            {"role": "system", "content": self.system_prompt + "\n\n" + health_query_prompt},
        ]
        
        # 添加历史消息
        history_messages = self._format_message_history(session_messages[-5:])
        messages.extend(history_messages)
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        # 生成响应
        response = await self.model_factory.generate_response(
            messages=messages,
            max_tokens=1000,
            temperature=0.4  # 降低温度以提高准确性
        )
        
        response_content = response.get("content", "")
        
        # 提取参考资料
        references = []
        for item in knowledge_items:
            references.append({
                "title": item.get("title", ""),
                "id": item.get("id", ""),
                "type": "knowledge_item"
            })
        
        # 判断是否需要专业医疗建议的免责声明
        medical_disclaimer = False
        medical_terms = ["疾病", "症状", "诊断", "治疗", "药物", "医生", "医院", "检查", "手术"]
        for term in medical_terms:
            if term in message or term in response_content:
                medical_disclaimer = True
                break
        
        if medical_disclaimer:
            response_content += "\n\n请注意：以上信息仅供参考，不构成医疗建议。如有健康问题，请咨询专业医疗人员。"
        
        return {
            "message": response_content,
            "type": "health_query",
            "is_memory_anchor": False,  # 一般查询不需要作为记忆锚点
            "importance": 4,
            "topic": "health_query",
            "context": context,
            "references": references,
            "medical_disclaimer": medical_disclaimer
        }
    
    def _format_message_history(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        格式化消息历史为LLM对话格式
        
        Args:
            messages: 会话消息列表
            
        Returns:
            List[Dict[str, str]]: 格式化的消息列表
        """
        formatted_messages = []
        
        for message in messages:
            role = message.get("role", "")
            # 转换role以符合OpenAI格式
            if role == "user":
                formatted_role = "user"
            elif role == "agent":
                formatted_role = "assistant"
            else:
                continue  # 跳过未知角色
                
            formatted_messages.append({
                "role": formatted_role,
                "content": message.get("content", "")
            })
            
        return formatted_messages
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """获取活跃会话列表"""
        return self.active_sessions
    
    def cleanup_expired_sessions(self, max_age_minutes: int = 60) -> int:
        """清理过期会话"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            last_activity = session.get("last_activity", session.get("start_time"))
            age_minutes = (now - last_activity).total_seconds() / 60
            
            if age_minutes > max_age_minutes:
                expired_sessions.append(session_id)
        
        # 删除过期会话
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        return len(expired_sessions)
    
    async def close(self):
        """关闭智能体管理器，释放资源"""
        logger.info("正在关闭索尔智能体管理器...")
        # 关闭模型工厂
        if hasattr(self.model_factory, 'close'):
            await self.model_factory.close()
        logger.info("索尔智能体管理器已关闭") 