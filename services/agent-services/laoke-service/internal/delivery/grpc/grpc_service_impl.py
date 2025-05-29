#!/usr/bin/env python

"""
老克智能体 gRPC 服务实现
"""

import time

import grpc

# proto定义导入
from api.grpc.laoke_service_pb2 import (
    ContentModerationResponse,
    ContributionEvaluationResponse,
    CourseInfo,
    EducationalContentResponse,
    KnowledgeItem,
    LearningPathInfo,
    ModuleInfo,
    NPCAction,
    NPCInteractionResponse,
    SearchKnowledgeResponse,
    TrendingContentResponse,
    TrendingItem,
    UserLearningPathResponse,
)
from api.grpc.laoke_service_pb2_grpc import (
    LaokeServiceServicer,
    add_LaokeServiceServicer_to_server,
)
from internal.agent.agent_manager import AgentManager
from internal.community.community_service import CommunityService

# 服务依赖导入
from internal.knowledge.knowledge_service import KnowledgeService
from pkg.utils.config import Config
from pkg.utils.logger import get_logger
from pkg.utils.metrics import increment_counter, observe_latency

logger = get_logger(__name__)
config = Config()


class LaokeServiceServicer(LaokeServiceServicer):
    """老克智能体服务实现"""

    def __init__(self):
        """初始化服务"""
        self.knowledge_service = KnowledgeService()
        self.community_service = CommunityService()
        self.agent_manager = AgentManager()
        self.learning_service = None  # 延迟初始化

    async def SearchKnowledge(self, request, context):
        """
        知识检索接口实现
        """
        start_time = time.time()
        logger.info(f"接收知识检索请求: query={request.query}, categories={request.categories}")

        try:
            # 调用知识服务进行检索
            knowledge_items = await self.knowledge_service.search_knowledge(
                query=request.query,
                categories=list(request.categories) if request.categories else None,
                tags=list(request.tags) if request.tags else None,
                limit=request.limit
            )

            # 获取相关主题
            related_topics = await self.knowledge_service.get_related_topics(request.query)

            # 构造响应
            response = SearchKnowledgeResponse()

            for item in knowledge_items:
                knowledge_item = KnowledgeItem(
                    id=item['id'],
                    title=item['title'],
                    summary=item.get('summary', ''),
                    content=item['content'],
                    category=item['category'],
                    tags=item['tags'],
                    relevance_score=item.get('relevance_score', 0.0),
                    related_topics=related_topics
                )
                response.items.append(knowledge_item)

            # 记录处理延迟
            latency_ms = (time.time() - start_time) * 1000
            response.search_latency_ms = latency_ms

            # 记录指标
            observe_latency("knowledge_search_latency", latency_ms)
            increment_counter("knowledge_search_total")

            logger.info(f"知识检索成功: 找到 {len(response.items)} 条结果，耗时 {latency_ms:.2f}ms")
            return response

        except Exception as e:
            logger.error(f"知识检索失败: {str(e)}")
            increment_counter("knowledge_search_error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"知识检索失败: {str(e)}")
            return SearchKnowledgeResponse()

    async def GetUserLearningPath(self, request, context):
        """
        获取用户学习路径接口实现
        """
        logger.info(f"接收用户学习路径请求: user_id={request.user_id}, path_id={request.path_id}")

        try:
            # 延迟初始化学习服务
            if self.learning_service is None:
                from internal.knowledge.learning_service import LearningService
                self.learning_service = LearningService()

            # 调用学习服务获取学习路径
            result = await self.learning_service.get_user_learning_paths(
                user_id=request.user_id,
                path_id=request.path_id if request.path_id else None,
                include_progress=request.include_progress
            )

            # 构造响应
            response = UserLearningPathResponse()

            # 添加学习路径信息
            for path in result.get('paths', []):
                modules = []

                # 添加模块信息
                for module in path.get('modules', []):
                    modules.append(ModuleInfo(
                        id=module['id'],
                        title=module['title'],
                        completed=module['completed'],
                        order=module['order']
                    ))

                # 创建路径信息
                path_info = LearningPathInfo(
                    id=path['id'],
                    title=path['title'],
                    description=path['description'],
                    level=path['level'],
                    total_modules=path['total_modules'],
                    completed_modules=path['completed_modules'],
                    progress_percentage=path['progress_percentage'],
                    modules=modules
                )

                response.paths.append(path_info)

            # 设置完成百分比和下一步建议
            response.completion_percentage = result.get('completion_percentage', 0.0)
            response.next_recommended_action = result.get('next_recommended_action', '')

            increment_counter("learning_path_request_total")
            logger.info(f"获取用户学习路径成功: 找到 {len(response.paths)} 条路径")
            return response

        except Exception as e:
            logger.error(f"获取用户学习路径失败: {str(e)}")
            increment_counter("learning_path_request_error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取用户学习路径失败: {str(e)}")
            return UserLearningPathResponse()

    async def EvaluateContribution(self, request, context):
        """
        评估用户贡献接口实现
        """
        logger.info(f"接收贡献评估请求: user_id={request.user_id}, content_type={request.content_type}")

        try:
            # 调用知识服务评估贡献
            evaluation_result = await self.knowledge_service.evaluate_contribution(
                user_id=request.user_id,
                content_id=request.content_id,
                content_type=request.content_type,
                content=request.content
            )

            # 构造响应
            response = ContributionEvaluationResponse(
                quality_score=evaluation_result.get('quality_score', 0.0),
                originality_score=evaluation_result.get('originality_score', 0.0),
                usefulness_score=evaluation_result.get('usefulness_score', 0.0),
                contribution_points=evaluation_result.get('contribution_points', 0),
                improvement_suggestions=evaluation_result.get('improvement_suggestions', []),
                is_approved=evaluation_result.get('is_approved', False)
            )

            increment_counter("contribution_evaluation_total")
            logger.info(f"贡献评估成功: is_approved={response.is_approved}, points={response.contribution_points}")
            return response

        except Exception as e:
            logger.error(f"贡献评估失败: {str(e)}")
            increment_counter("contribution_evaluation_error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"贡献评估失败: {str(e)}")
            return ContributionEvaluationResponse()

    async def NPCInteraction(self, request, context):
        """
        NPC交互接口实现
        """
        logger.info(f"接收NPC交互请求: npc_id={request.npc_id}, user_id={request.user_id}")

        try:
            # 调用智能体管理器处理NPC交互
            interaction_result = await self.agent_manager.process_npc_interaction(
                npc_id=request.npc_id,
                user_id=request.user_id,
                message=request.message,
                context=request.interaction_context,
                location=request.location,
                active_quests=list(request.active_quests) if request.active_quests else None
            )

            # 构造响应
            response = NPCInteractionResponse(
                response_text=interaction_result.get('response_text', ''),
                emotion=interaction_result.get('emotion', 'neutral')
            )

            # 添加动作
            for action in interaction_result.get('actions', []):
                npc_action = NPCAction(
                    id=action.get('id', ''),
                    type=action.get('type', ''),
                    description=action.get('description', ''),
                    requirements_met=action.get('requirements_met', False),
                    rewards=action.get('rewards', [])
                )
                response.actions.append(npc_action)

            # 添加知识提示
            if 'knowledge_hints' in interaction_result:
                response.knowledge_hints.extend(interaction_result['knowledge_hints'])

            increment_counter("npc_interaction_total")
            logger.info(f"NPC交互成功: emotion={response.emotion}, actions={len(response.actions)}")
            return response

        except Exception as e:
            logger.error(f"NPC交互失败: {str(e)}")
            increment_counter("npc_interaction_error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"NPC交互失败: {str(e)}")
            return NPCInteractionResponse()

    async def ModerateContent(self, request, context):
        """
        内容审核接口实现
        """
        logger.info(f"接收内容审核请求: content_type={request.content_type}, content_id={request.content_id}")

        try:
            # 调用社区服务进行内容审核
            moderation_result = await self.community_service.moderate_content(
                content_id=request.content_id,
                content_type=request.content_type,
                content=request.content,
                context_items=list(request.context_items) if request.context_items else None
            )

            # 构造响应
            response = ContentModerationResponse(
                is_approved=moderation_result.get('is_approved', False),
                violation_types=moderation_result.get('violation_types', []),
                review_comment=moderation_result.get('review_comment', ''),
                moderation_level=moderation_result.get('moderation_level', 'needs_review'),
                confidence_score=moderation_result.get('confidence_score', 0.0)
            )

            increment_counter("content_moderation_total")
            if response.is_approved:
                increment_counter("content_moderation_approved")
            else:
                increment_counter("content_moderation_rejected")

            logger.info(f"内容审核成功: is_approved={response.is_approved}, level={response.moderation_level}")
            return response

        except Exception as e:
            logger.error(f"内容审核失败: {str(e)}")
            increment_counter("content_moderation_error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内容审核失败: {str(e)}")
            return ContentModerationResponse()

    async def GetTrendingContent(self, request, context):
        """
        获取热门内容接口实现
        """
        logger.info(f"接收热门内容请求: content_type={request.content_type}, time_window={request.time_window_hours}h")

        try:
            # 调用社区服务获取热门内容
            trending_results = await self.community_service.get_trending_posts(
                content_type=request.content_type,
                time_window_hours=request.time_window_hours,
                limit=request.limit,
                category=request.category if request.category else None
            )

            # 构造响应
            response = TrendingContentResponse(
                trending_algorithm_version="v1.2.0"  # 算法版本
            )

            # 添加热门内容
            for item in trending_results:
                trending_item = TrendingItem(
                    id=item.get('id', ''),
                    title=item.get('title', ''),
                    type=item.get('type', ''),
                    view_count=item.get('view_count', 0),
                    like_count=item.get('like_count', 0),
                    comment_count=item.get('comment_count', 0),
                    trending_score=item.get('trending_score', 0.0),
                    author_id=item.get('author_id', ''),
                    created_at=item.get('created_at', '')
                )
                response.items.append(trending_item)

            increment_counter("trending_content_request_total")
            logger.info(f"获取热门内容成功: 找到 {len(response.items)} 条内容")
            return response

        except Exception as e:
            logger.error(f"获取热门内容失败: {str(e)}")
            increment_counter("trending_content_request_error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取热门内容失败: {str(e)}")
            return TrendingContentResponse()

    async def GetEducationalContent(self, request, context):
        """
        获取教育内容接口实现
        """
        logger.info(f"接收教育内容请求: user_id={request.user_id}, category={request.category}, level={request.level}")

        try:
            # 延迟初始化学习服务
            if self.learning_service is None:
                from internal.knowledge.learning_service import LearningService
                self.learning_service = LearningService()

            # 调用学习服务获取教育内容
            courses = await self.learning_service.get_educational_content(
                user_id=request.user_id,
                category=request.category if request.category else None,
                level=request.level if request.level else None,
                personalized=request.personalized,
                limit=request.limit
            )

            # 构造响应
            response = EducationalContentResponse(
                recommended_categories=courses.get('recommended_categories', []),
                personalization_info=courses.get('personalization_info', '')
            )

            # 添加课程信息
            for course in courses.get('courses', []):
                course_info = CourseInfo(
                    id=course.get('id', ''),
                    title=course.get('title', ''),
                    description=course.get('description', ''),
                    category=course.get('category', ''),
                    level=course.get('level', ''),
                    instructor_id=course.get('instructor_id', ''),
                    module_count=course.get('module_count', 0),
                    estimated_duration=course.get('estimated_duration', ''),
                    rating=course.get('rating', 0.0),
                    enrolled_count=course.get('enrolled_count', 0),
                    certification_enabled=course.get('certification_enabled', False)
                )
                response.courses.append(course_info)

            increment_counter("educational_content_request_total")
            logger.info(f"获取教育内容成功: 找到 {len(response.courses)} 个课程")
            return response

        except Exception as e:
            logger.error(f"获取教育内容失败: {str(e)}")
            increment_counter("educational_content_request_error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取教育内容失败: {str(e)}")
            return EducationalContentResponse()


def add_service_to_server(server):
    """将老克服务添加到gRPC服务器"""
    add_LaokeServiceServicer_to_server(LaokeServiceServicer(), server)
