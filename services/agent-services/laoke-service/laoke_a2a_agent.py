#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
老克智能体 A2A 协议适配器
LaoKe Agent A2A Protocol Adapter

将老克智能体服务包装为符合 A2A 协议的智能体
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from python_a2a import A2AServer, AgentCard, skill, agent, TaskStatus, TaskState, Message, TextContent, MessageRole

logger = logging.getLogger(__name__)


@agent(
    name="老克智能体",
    description="索克生活平台的知识传播和社区管理智能体，专注于中医知识传播、学习路径规划和社区内容管理",
    version="1.0.0",
    capabilities={
        "knowledge_content_management": True,
        "learning_path_planning": True,
        "community_content_management": True,
        "tcm_knowledge_qa": True,
        "content_recommendation": True,
        "educational_content_creation": True,
        "user_learning_tracking": True,
        "google_a2a_compatible": True
    }
)
class LaoKeA2AAgent(A2AServer):
    """老克智能体 A2A 协议实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化老克 A2A 智能体
        
        Args:
            config: 配置字典
        """
        # 创建智能体卡片
        agent_card = AgentCard(
            name="老克智能体",
            description="索克生活平台的知识传播和社区管理智能体，专注于中医知识传播、学习路径规划和社区内容管理",
            url="http://localhost:5003",
            version="1.0.0",
            capabilities={
                "knowledge_content_management": True,
                "learning_path_planning": True,
                "community_content_management": True,
                "tcm_knowledge_qa": True,
                "content_recommendation": True,
                "educational_content_creation": True,
                "user_learning_tracking": True,
                "google_a2a_compatible": True
            }
        )
        
        # 初始化 A2A 服务器
        super().__init__(agent_card=agent_card)
        
        # 初始化老克服务组件（模拟实现）
        self.knowledge_manager = self._init_knowledge_manager()
        self.learning_planner = self._init_learning_planner()
        self.community_manager = self._init_community_manager()
        self.content_recommender = self._init_content_recommender()
        self.qa_engine = self._init_qa_engine()
        
        logger.info("老克 A2A 智能体初始化完成")
    
    def _init_knowledge_manager(self):
        """初始化知识管理器"""
        return {
            "knowledge_categories": {
                "中医基础理论": ["阴阳学说", "五行学说", "脏腑学说", "经络学说"],
                "中医诊断": ["望诊", "闻诊", "问诊", "切诊", "辨证论治"],
                "中药学": ["中药性味", "中药归经", "中药配伍", "方剂学"],
                "养生保健": ["四季养生", "体质养生", "饮食养生", "运动养生"],
                "疾病防治": ["常见病防治", "慢性病管理", "亚健康调理"]
            },
            "content_types": ["文章", "视频", "音频", "图片", "互动课程"],
            "difficulty_levels": ["入门", "初级", "中级", "高级", "专家"]
        }
    
    def _init_learning_planner(self):
        """初始化学习规划器"""
        return {
            "learning_paths": {
                "中医入门": {
                    "duration": "30天",
                    "modules": [
                        {"name": "中医基础概念", "duration": "5天", "difficulty": "入门"},
                        {"name": "阴阳五行理论", "duration": "7天", "difficulty": "初级"},
                        {"name": "脏腑经络基础", "duration": "10天", "difficulty": "初级"},
                        {"name": "基础诊断方法", "duration": "8天", "difficulty": "中级"}
                    ]
                },
                "体质养生": {
                    "duration": "21天",
                    "modules": [
                        {"name": "九种体质识别", "duration": "7天", "difficulty": "初级"},
                        {"name": "体质调理方法", "duration": "7天", "difficulty": "中级"},
                        {"name": "个性化养生方案", "duration": "7天", "difficulty": "中级"}
                    ]
                },
                "食疗养生": {
                    "duration": "28天",
                    "modules": [
                        {"name": "中医营养学基础", "duration": "7天", "difficulty": "入门"},
                        {"name": "食物性味归经", "duration": "7天", "difficulty": "初级"},
                        {"name": "常用食疗方", "duration": "7天", "difficulty": "中级"},
                        {"name": "季节性食疗", "duration": "7天", "difficulty": "中级"}
                    ]
                }
            },
            "assessment_methods": ["知识测试", "实践作业", "案例分析", "同伴评议"]
        }
    
    def _init_community_manager(self):
        """初始化社区管理器"""
        return {
            "community_sections": {
                "学习交流": ["学习心得", "问题讨论", "经验分享"],
                "养生实践": ["养生日记", "体质调理", "食疗分享"],
                "专家答疑": ["专家问答", "案例分析", "在线咨询"],
                "资源分享": ["学习资料", "工具推荐", "书籍推荐"]
            },
            "content_moderation": {
                "auto_review": True,
                "keyword_filter": ["广告", "违规", "不当"],
                "expert_review": True
            },
            "engagement_features": ["点赞", "评论", "收藏", "分享", "关注"]
        }
    
    def _init_content_recommender(self):
        """初始化内容推荐器"""
        return {
            "recommendation_algorithms": ["协同过滤", "内容相似度", "知识图谱", "学习路径"],
            "personalization_factors": [
                "学习历史", "兴趣偏好", "知识水平", "学习目标", "体质类型"
            ],
            "content_scoring": {
                "relevance": 0.3,
                "quality": 0.25,
                "popularity": 0.2,
                "recency": 0.15,
                "personalization": 0.1
            }
        }
    
    def _init_qa_engine(self):
        """初始化问答引擎"""
        return {
            "knowledge_base": {
                "中医基础": {
                    "什么是阴阳": "阴阳是中医理论的核心概念，指事物内部相互对立统一的两个方面",
                    "五行是什么": "五行指木、火、土、金、水五种基本物质，用来说明事物的属性和相互关系",
                    "什么是气血": "气血是人体生命活动的基本物质，气为血之帅，血为气之母"
                },
                "体质养生": {
                    "阳虚体质如何调理": "阳虚体质应温补阳气，多食温热食物，适当运动，避免寒凉",
                    "阴虚体质特点": "阴虚体质表现为口干、盗汗、五心烦热，应滋阴润燥",
                    "湿热体质调理": "湿热体质应清热利湿，饮食清淡，避免油腻辛辣"
                },
                "食疗养生": {
                    "春季养生食物": "春季宜食韭菜、春笋、豆芽等升发阳气的食物",
                    "夏季清热食物": "夏季可食绿豆、冬瓜、苦瓜等清热解暑食物",
                    "秋季润燥食物": "秋季宜食梨、百合、银耳等润燥养肺食物"
                }
            },
            "response_templates": {
                "知识解答": "根据中医理论，{question}的答案是：{answer}。建议您{suggestion}。",
                "养生建议": "针对您的{constitution}体质，建议{advice}。同时要注意{precautions}。",
                "学习指导": "关于{topic}的学习，建议您{learning_path}。可以参考{resources}。"
            }
        }
    
    @skill(
        name="知识内容管理",
        description="管理中医知识内容，包括内容创建、编辑、分类和质量控制",
        tags=["知识管理", "内容创建", "质量控制"]
    )
    async def manage_knowledge_content(self, action: str = "query", 
                                     content_type: str = "", 
                                     category: str = "",
                                     query: str = "",
                                     limit: int = 10) -> Dict[str, Any]:
        """
        知识内容管理技能
        
        Args:
            action: 操作类型 (query, create, update, delete)
            content_type: 内容类型
            category: 内容分类
            query: 查询关键词
            limit: 返回数量限制
            
        Returns:
            知识内容管理结果
        """
        try:
            if action == "query":
                # 查询知识内容
                results = []
                categories = self.knowledge_manager["knowledge_categories"]
                
                if category and category in categories:
                    # 按分类查询
                    topics = categories[category]
                    for topic in topics[:limit]:
                        results.append({
                            "title": topic,
                            "category": category,
                            "type": "知识点",
                            "difficulty": "初级",
                            "views": 100,
                            "likes": 20
                        })
                elif query:
                    # 按关键词查询
                    for cat, topics in categories.items():
                        for topic in topics:
                            if query in topic:
                                results.append({
                                    "title": topic,
                                    "category": cat,
                                    "type": "知识点",
                                    "difficulty": "初级",
                                    "views": 100,
                                    "likes": 20
                                })
                                if len(results) >= limit:
                                    break
                        if len(results) >= limit:
                            break
                else:
                    # 返回热门内容
                    for cat, topics in list(categories.items())[:3]:
                        for topic in topics[:2]:
                            results.append({
                                "title": topic,
                                "category": cat,
                                "type": "知识点",
                                "difficulty": "初级",
                                "views": 100,
                                "likes": 20
                            })
                
                return {
                    "success": True,
                    "action": action,
                    "results": results,
                    "total": len(results)
                }
            
            elif action == "create":
                return {
                    "success": True,
                    "action": action,
                    "message": "知识内容创建成功",
                    "content_id": "content_001"
                }
            
            else:
                return {
                    "success": True,
                    "action": action,
                    "message": f"操作 {action} 执行成功"
                }
                
        except Exception as e:
            logger.error(f"知识内容管理失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="学习路径规划",
        description="为用户规划个性化的中医学习路径，包括课程安排和进度跟踪",
        tags=["学习规划", "个性化教育", "进度跟踪"]
    )
    async def plan_learning_path(self, user_id: str, learning_goal: str,
                               current_level: str = "入门",
                               available_time: str = "30分钟/天",
                               interests: List[str] = None) -> Dict[str, Any]:
        """
        学习路径规划技能
        
        Args:
            user_id: 用户ID
            learning_goal: 学习目标
            current_level: 当前水平
            available_time: 可用时间
            interests: 兴趣领域
            
        Returns:
            学习路径规划结果
        """
        try:
            # 根据学习目标选择合适的学习路径
            available_paths = self.learning_planner["learning_paths"]
            
            # 简单的路径匹配逻辑
            selected_path = None
            if "入门" in learning_goal or "基础" in learning_goal:
                selected_path = available_paths["中医入门"]
                path_name = "中医入门"
            elif "体质" in learning_goal or "养生" in learning_goal:
                selected_path = available_paths["体质养生"]
                path_name = "体质养生"
            elif "食疗" in learning_goal or "饮食" in learning_goal:
                selected_path = available_paths["食疗养生"]
                path_name = "食疗养生"
            else:
                selected_path = available_paths["中医入门"]
                path_name = "中医入门"
            
            # 根据可用时间调整学习计划
            time_factor = 1.0
            if "15分钟" in available_time:
                time_factor = 0.5
            elif "60分钟" in available_time or "1小时" in available_time:
                time_factor = 2.0
            
            # 生成个性化学习计划
            personalized_modules = []
            for module in selected_path["modules"]:
                adjusted_duration = int(int(module["duration"].replace("天", "")) * time_factor)
                personalized_modules.append({
                    "name": module["name"],
                    "duration": f"{adjusted_duration}天",
                    "difficulty": module["difficulty"],
                    "daily_time": available_time,
                    "resources": ["视频课程", "阅读材料", "练习题"],
                    "assessment": "模块测试"
                })
            
            learning_plan = {
                "user_id": user_id,
                "path_name": path_name,
                "learning_goal": learning_goal,
                "current_level": current_level,
                "total_duration": selected_path["duration"],
                "daily_time": available_time,
                "modules": personalized_modules,
                "milestones": [
                    {"week": 1, "goal": "掌握基础概念"},
                    {"week": 2, "goal": "理解核心理论"},
                    {"week": 3, "goal": "应用实践知识"},
                    {"week": 4, "goal": "综合运用能力"}
                ],
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            return {"success": True, "learning_plan": learning_plan}
            
        except Exception as e:
            logger.error(f"学习路径规划失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="社区内容管理",
        description="管理社区内容，包括内容审核、用户互动和社区活动组织",
        tags=["社区管理", "内容审核", "用户互动"]
    )
    async def manage_community_content(self, action: str, content_id: str = "",
                                     user_id: str = "", content_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        社区内容管理技能
        
        Args:
            action: 操作类型 (review, approve, reject, feature, moderate)
            content_id: 内容ID
            user_id: 用户ID
            content_data: 内容数据
            
        Returns:
            社区内容管理结果
        """
        try:
            community_sections = self.community_manager["community_sections"]
            
            if action == "review":
                # 内容审核
                review_result = {
                    "content_id": content_id,
                    "status": "approved",
                    "review_score": 85,
                    "suggestions": ["内容质量良好", "建议增加更多实例"],
                    "reviewer": "auto_system",
                    "review_time": "2024-01-01T00:00:00Z"
                }
                return {"success": True, "review_result": review_result}
            
            elif action == "feature":
                # 推荐内容
                featured_content = {
                    "content_id": content_id,
                    "featured_reason": "高质量内容，用户反馈良好",
                    "featured_duration": "7天",
                    "featured_position": "首页推荐"
                }
                return {"success": True, "featured_content": featured_content}
            
            elif action == "moderate":
                # 内容管理
                moderation_actions = [
                    "内容质量检查完成",
                    "用户互动数据更新",
                    "违规内容已处理",
                    "社区活跃度统计更新"
                ]
                return {"success": True, "moderation_actions": moderation_actions}
            
            elif action == "get_stats":
                # 获取社区统计
                community_stats = {
                    "total_posts": 1250,
                    "active_users": 320,
                    "daily_posts": 45,
                    "engagement_rate": 0.78,
                    "top_categories": ["体质养生", "食疗分享", "学习心得"],
                    "trending_topics": ["春季养生", "阳虚调理", "食疗方法"]
                }
                return {"success": True, "community_stats": community_stats}
            
            else:
                return {"success": True, "message": f"操作 {action} 执行成功"}
                
        except Exception as e:
            logger.error(f"社区内容管理失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="中医知识问答",
        description="回答用户的中医相关问题，提供专业的知识解答和建议",
        tags=["知识问答", "专业咨询", "中医知识"]
    )
    async def answer_tcm_question(self, question: str, user_id: str = "",
                                context: str = "", question_type: str = "general") -> Dict[str, Any]:
        """
        中医知识问答技能
        
        Args:
            question: 用户问题
            user_id: 用户ID
            context: 问题上下文
            question_type: 问题类型
            
        Returns:
            问答结果
        """
        try:
            knowledge_base = self.qa_engine["knowledge_base"]
            templates = self.qa_engine["response_templates"]
            
            # 简单的问题匹配逻辑
            answer = None
            category = None
            
            for cat, qa_pairs in knowledge_base.items():
                for q, a in qa_pairs.items():
                    if any(keyword in question for keyword in q.split()):
                        answer = a
                        category = cat
                        break
                if answer:
                    break
            
            if not answer:
                # 默认回答
                answer = "这是一个很好的问题。建议您咨询专业的中医师获得更准确的答案。"
                category = "通用咨询"
            
            # 生成建议
            suggestions = []
            if "体质" in question:
                suggestions = ["进行体质测试", "咨询专业医师", "学习体质调理方法"]
            elif "食疗" in question:
                suggestions = ["了解食物性味", "学习配伍禁忌", "制定个人食疗方案"]
            elif "养生" in question:
                suggestions = ["制定养生计划", "学习四季养生", "培养良好生活习惯"]
            else:
                suggestions = ["深入学习相关知识", "实践应用", "寻求专业指导"]
            
            # 推荐相关内容
            related_content = []
            if category in knowledge_base:
                related_topics = list(knowledge_base[category].keys())[:3]
                for topic in related_topics:
                    if topic != question:
                        related_content.append({
                            "title": topic,
                            "category": category,
                            "type": "知识问答"
                        })
            
            qa_result = {
                "question": question,
                "answer": answer,
                "category": category,
                "confidence": 0.85,
                "suggestions": suggestions,
                "related_content": related_content,
                "expert_review": False,
                "response_time": "2024-01-01T00:00:00Z"
            }
            
            return {"success": True, "qa_result": qa_result}
            
        except Exception as e:
            logger.error(f"中医知识问答失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="内容推荐",
        description="基于用户兴趣和学习历史推荐个性化的学习内容",
        tags=["个性化推荐", "内容发现", "学习优化"]
    )
    async def recommend_content(self, user_id: str, recommendation_type: str = "learning",
                              user_interests: List[str] = None,
                              learning_history: List[str] = None,
                              limit: int = 10) -> Dict[str, Any]:
        """
        内容推荐技能
        
        Args:
            user_id: 用户ID
            recommendation_type: 推荐类型 (learning, community, expert)
            user_interests: 用户兴趣
            learning_history: 学习历史
            limit: 推荐数量
            
        Returns:
            内容推荐结果
        """
        try:
            recommendations = []
            
            if recommendation_type == "learning":
                # 学习内容推荐
                learning_contents = [
                    {
                        "id": "learn_001",
                        "title": "春季养生要点",
                        "type": "视频课程",
                        "category": "四季养生",
                        "difficulty": "初级",
                        "duration": "15分钟",
                        "rating": 4.8,
                        "views": 1200,
                        "reason": "基于您对养生的兴趣推荐"
                    },
                    {
                        "id": "learn_002",
                        "title": "阳虚体质调理方法",
                        "type": "图文教程",
                        "category": "体质养生",
                        "difficulty": "中级",
                        "duration": "20分钟",
                        "rating": 4.9,
                        "views": 800,
                        "reason": "与您的学习历史相关"
                    },
                    {
                        "id": "learn_003",
                        "title": "常用食疗方介绍",
                        "type": "音频课程",
                        "category": "食疗养生",
                        "difficulty": "初级",
                        "duration": "25分钟",
                        "rating": 4.7,
                        "views": 950,
                        "reason": "热门推荐内容"
                    }
                ]
                recommendations.extend(learning_contents[:limit])
            
            elif recommendation_type == "community":
                # 社区内容推荐
                community_contents = [
                    {
                        "id": "post_001",
                        "title": "我的春季养生心得分享",
                        "type": "用户分享",
                        "author": "养生达人",
                        "category": "经验分享",
                        "likes": 156,
                        "comments": 23,
                        "reason": "高质量用户分享"
                    },
                    {
                        "id": "post_002",
                        "title": "阳虚体质的食疗调理经验",
                        "type": "案例分析",
                        "author": "中医师李医生",
                        "category": "专家分享",
                        "likes": 289,
                        "comments": 45,
                        "reason": "专家权威内容"
                    }
                ]
                recommendations.extend(community_contents[:limit])
            
            elif recommendation_type == "expert":
                # 专家内容推荐
                expert_contents = [
                    {
                        "id": "expert_001",
                        "title": "中医体质辨识要点",
                        "type": "专家讲座",
                        "expert": "王教授",
                        "institution": "中医药大学",
                        "category": "专业知识",
                        "duration": "45分钟",
                        "rating": 4.9,
                        "reason": "权威专家内容"
                    }
                ]
                recommendations.extend(expert_contents[:limit])
            
            # 计算推荐分数
            for item in recommendations:
                item["recommendation_score"] = 0.85  # 简化计算
            
            recommendation_result = {
                "user_id": user_id,
                "recommendation_type": recommendation_type,
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "algorithm": "hybrid_recommendation",
                "generated_at": "2024-01-01T00:00:00Z"
            }
            
            return {"success": True, "recommendation_result": recommendation_result}
            
        except Exception as e:
            logger.error(f"内容推荐失败: {e}")
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
            if "学习" in text or "课程" in text or "规划" in text:
                # 学习路径规划请求
                result = await self.plan_learning_path(
                    user_id=user_id,
                    learning_goal=text,
                    current_level="入门"
                )
                
            elif "问题" in text or "什么是" in text or "如何" in text or "?" in text or "？" in text:
                # 知识问答请求
                result = await self.answer_tcm_question(
                    question=text,
                    user_id=user_id
                )
                
            elif "推荐" in text or "内容" in text:
                # 内容推荐请求
                result = await self.recommend_content(
                    user_id=user_id,
                    recommendation_type="learning"
                )
                
            elif "社区" in text or "管理" in text:
                # 社区管理请求
                result = await self.manage_community_content(
                    action="get_stats",
                    user_id=user_id
                )
                
            elif "知识" in text or "搜索" in text or "查询" in text:
                # 知识内容管理请求
                result = await self.manage_knowledge_content(
                    action="query",
                    query=text
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
    
    async def _handle_general_consultation(self, text: str, user_id: str) -> Dict[str, Any]:
        """处理通用咨询"""
        return {
            "response": f"您好！我是老克智能体，专注于中医知识传播和学习指导。关于您的问题：{text}，我可以为您提供以下服务：",
            "services": [
                "个性化学习路径规划",
                "中医知识问答解答",
                "优质内容推荐",
                "社区学习交流",
                "专家知识分享"
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
        elif "learning_plan" in result:
            plan = result["learning_plan"]
            response = f"为您制定的学习计划：{plan['path_name']}\n"
            response += f"学习目标：{plan['learning_goal']}\n"
            response += f"总时长：{plan['total_duration']}\n"
            response += f"每日时间：{plan['daily_time']}\n"
            response += f"包含 {len(plan['modules'])} 个学习模块"
            return response
        elif "qa_result" in result:
            qa = result["qa_result"]
            response = f"问题：{qa['question']}\n"
            response += f"回答：{qa['answer']}\n"
            if qa['suggestions']:
                response += f"建议：{', '.join(qa['suggestions'][:3])}"
            return response
        elif "recommendation_result" in result:
            rec = result["recommendation_result"]
            response = f"为您推荐 {len(rec['recommendations'])} 个内容：\n"
            for i, item in enumerate(rec['recommendations'][:3], 1):
                response += f"{i}. {item['title']} ({item['type']})\n"
            return response
        elif "community_stats" in result:
            stats = result["community_stats"]
            response = f"社区统计信息：\n"
            response += f"总帖子数：{stats['total_posts']}\n"
            response += f"活跃用户：{stats['active_users']}\n"
            response += f"参与度：{stats['engagement_rate']*100:.1f}%"
            return response
        elif "results" in result:
            results = result["results"]
            response = f"找到 {len(results)} 个相关内容：\n"
            for i, item in enumerate(results[:3], 1):
                response += f"{i}. {item['title']} ({item['category']})\n"
            return response
        else:
            return json.dumps(result, ensure_ascii=False, indent=2)


# 创建智能体实例的工厂函数
def create_laoke_a2a_agent(config: Optional[Dict[str, Any]] = None) -> LaoKeA2AAgent:
    """
    创建老克 A2A 智能体实例
    
    Args:
        config: 配置字典
        
    Returns:
        老克 A2A 智能体实例
    """
    return LaoKeA2AAgent(config) 