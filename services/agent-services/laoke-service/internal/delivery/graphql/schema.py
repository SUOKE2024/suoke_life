"""
schema - 索克生活项目模块
"""

from enum import Enum
from internal.delivery.dependencies import (
from internal.delivery.exceptions import ResourceNotFoundException, ValidationException
import strawberry

#!/usr/bin/env python

"""
老克智能体服务 - GraphQL 模式定义
使用Strawberry库实现GraphQL API
"""



    get_agent_manager,
    get_community_service,
    get_knowledge_service,
)


# 枚举类型
@strawberry.enum
class ResourceType(Enum):
    ARTICLE = "ARTICLE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    PDF = "PDF"
    INTERACTIVE = "INTERACTIVE"

@strawberry.enum
class CourseLevel(Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"

@strawberry.enum
class ActionType(Enum):
    QUEST = "QUEST"
    CHALLENGE = "CHALLENGE"
    REWARD = "REWARD"
    DIALOGUE = "DIALOGUE"
    GAME = "GAME"

@strawberry.enum
class UserRole(Enum):
    STUDENT = "STUDENT"
    CONTRIBUTOR = "CONTRIBUTOR"
    INSTRUCTOR = "INSTRUCTOR"
    EXPERT = "EXPERT"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"

# 用户类型
@strawberry.type
class User:
    id: strawberry.ID
    username: str
    display_name: str
    avatar_url: str | None = None
    role: UserRole
    specialization: list[str]
    contribution_score: int
    joined_at: str

# 知识库类型
@strawberry.type
class KnowledgeArticle:
    id: strawberry.ID
    title: str
    content: str
    category: str
    subcategory: str | None = None
    tags: list[str]
    author: User | None = None
    created_at: str
    updated_at: str | None = None
    rating: float | None = None
    rating_count: int
    view_count: int
    related_topics: list["KnowledgeArticle"] | None = None

@strawberry.input
class KnowledgeArticleInput:
    title: str
    content: str
    category: str
    subcategory: str | None = None
    tags: list[str]

# 学习路径类型
@strawberry.type
class QuizQuestion:
    id: strawberry.ID
    question: str
    options: list[str]
    correct_answer: int
    explanation: str | None = None

@strawberry.type
class Quiz:
    id: strawberry.ID
    title: str
    questions: list[QuizQuestion]
    passing_score: float

@strawberry.type
class Resource:
    id: strawberry.ID
    title: str
    type: ResourceType
    url: str
    description: str | None = None

@strawberry.type
class LearningModule:
    id: strawberry.ID
    title: str
    description: str
    content: str
    resources: list[Resource]
    quizzes: list[Quiz] | None = None
    order: int

@strawberry.type
class LearningPath:
    id: strawberry.ID
    title: str
    description: str
    category: str
    level: str
    estimated_duration: str
    modules: list[LearningModule]
    prerequisites: list["LearningPath"] | None = None
    enrolled_users: int
    completion_rate: float

# 社区内容类型
@strawberry.type
class Comment:
    id: strawberry.ID
    content: str
    author: User
    created_at: str
    like_count: int
    replies: list["Comment"] | None = None

@strawberry.type
class CommunityPost:
    id: strawberry.ID
    title: str
    content: str
    author: User
    category: str
    tags: list[str]
    created_at: str
    updated_at: str | None = None
    like_count: int
    comment_count: int
    comments: list[Comment]
    is_featured: bool

@strawberry.input
class CommunityPostInput:
    title: str
    content: str
    category: str
    tags: list[str]

# 教育课程类型
@strawberry.type
class Lesson:
    id: strawberry.ID
    title: str
    content: str
    video_url: str | None = None
    duration: str
    order: int

@strawberry.type
class CourseModule:
    id: strawberry.ID
    title: str
    description: str
    lessons: list[Lesson]
    quiz: Quiz | None = None
    order: int

@strawberry.type
class EducationCourse:
    id: strawberry.ID
    title: str
    description: str
    category: str
    level: CourseLevel
    instructor: User
    modules: list[CourseModule]
    estimated_duration: str
    enrolled_count: int
    rating: float | None = None
    certification_enabled: bool

# 游戏NPC类型
@strawberry.type
class NPCAction:
    id: strawberry.ID
    type: ActionType
    description: str
    requirements_met: bool
    rewards: list[str]

@strawberry.type
class NPCInteractionResponse:
    message: str
    emotion: str
    actions: list[NPCAction] | None = None
    knowledge: list[str] | None = None

@strawberry.type
class GameNPC:
    id: strawberry.ID
    name: str
    role: str
    personality: str
    backstory: str
    avatar_url: str
    dialogue_style: str

# Query类型
@strawberry.type
class Query:
    # 知识库查询
    @strawberry.field
    async def knowledge_article(self, id: strawberry.ID, info) -> KnowledgeArticle:
        """获取知识文章"""
        knowledge_service = get_knowledge_service(info.context)
        article = await knowledge_service.get_article_by_id(id)
        if not article:
            raise ResourceNotFoundException("知识文章", str(id))
        return article

    @strawberry.field
    async def knowledge_articles(
        self,
        info,
        category: str | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
        offset: int = 0
    ) -> list[KnowledgeArticle]:
        """获取知识文章列表"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.get_articles(category, tags, limit, offset)

    @strawberry.field
    async def search_knowledge(
        self,
        info,
        query: str,
        limit: int = 10
    ) -> list[KnowledgeArticle]:
        """搜索知识库"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.search(query, limit)

    # 学习路径查询
    @strawberry.field
    async def learning_path(self, info, id: strawberry.ID) -> LearningPath:
        """获取学习路径"""
        knowledge_service = get_knowledge_service(info.context)
        path = await knowledge_service.get_learning_path(id)
        if not path:
            raise ResourceNotFoundException("学习路径", str(id))
        return path

    @strawberry.field
    async def user_learning_paths(self, info, user_id: strawberry.ID) -> list[LearningPath]:
        """获取用户的学习路径"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.get_user_learning_paths(user_id)

    @strawberry.field
    async def recommended_learning_paths(
        self,
        info,
        user_id: strawberry.ID,
        limit: int = 5
    ) -> list[LearningPath]:
        """获取推荐的学习路径"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.get_recommended_learning_paths(user_id, limit)

    # 社区内容查询
    @strawberry.field
    async def community_post(self, info, id: strawberry.ID) -> CommunityPost:
        """获取社区帖子"""
        community_service = get_community_service(info.context)
        post = await community_service.get_post(id)
        if not post:
            raise ResourceNotFoundException("社区帖子", str(id))
        return post

    @strawberry.field
    async def community_posts(
        self,
        info,
        category: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[CommunityPost]:
        """获取社区帖子列表"""
        community_service = get_community_service(info.context)
        return await community_service.get_posts(category, tags, limit, offset)

    @strawberry.field
    async def user_community_posts(
        self,
        info,
        user_id: strawberry.ID,
        limit: int = 10,
        offset: int = 0
    ) -> list[CommunityPost]:
        """获取用户的社区帖子"""
        community_service = get_community_service(info.context)
        return await community_service.get_user_posts(user_id, limit, offset)

    # 教育课程查询
    @strawberry.field
    async def education_course(self, info, id: strawberry.ID) -> EducationCourse:
        """获取教育课程"""
        knowledge_service = get_knowledge_service(info.context)
        course = await knowledge_service.get_course(id)
        if not course:
            raise ResourceNotFoundException("教育课程", str(id))
        return course

    @strawberry.field
    async def education_courses(
        self,
        info,
        category: str | None = None,
        level: CourseLevel | None = None,
        limit: int = 10,
        offset: int = 0
    ) -> list[EducationCourse]:
        """获取教育课程列表"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.get_courses(category, level, limit, offset)

    @strawberry.field
    async def user_enrolled_courses(self, info, user_id: strawberry.ID) -> list[EducationCourse]:
        """获取用户已报名的课程"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.get_user_enrolled_courses(user_id)

    # 游戏NPC查询
    @strawberry.field
    async def game_npc(self, info, id: strawberry.ID) -> GameNPC:
        """获取游戏NPC"""
        agent_manager = get_agent_manager(info.context)
        npc = await agent_manager.get_npc(id)
        if not npc:
            raise ResourceNotFoundException("游戏NPC", str(id))
        return npc

    @strawberry.field
    async def game_npc_interaction(
        self,
        info,
        npc_id: strawberry.ID,
        context: str
    ) -> NPCInteractionResponse:
        """NPC交互"""
        agent_manager = get_agent_manager(info.context)
        return await agent_manager.process_npc_interaction(npc_id, context)

# Mutation类型
@strawberry.type
class Mutation:
    # 知识贡献
    @strawberry.mutation
    async def create_knowledge_article(
        self,
        info,
        input: KnowledgeArticleInput
    ) -> KnowledgeArticle:
        """创建知识文章"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.create_article(input)

    @strawberry.mutation
    async def update_knowledge_article(
        self,
        info,
        id: strawberry.ID,
        input: KnowledgeArticleInput
    ) -> KnowledgeArticle:
        """更新知识文章"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.update_article(id, input)

    @strawberry.mutation
    async def rate_knowledge_article(
        self,
        info,
        article_id: strawberry.ID,
        rating: int
    ) -> KnowledgeArticle:
        """评价知识文章"""
        if rating < 1 or rating > 5:
            raise ValidationException("评分必须在1到5之间")

        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.rate_article(article_id, rating)

    # 学习路径
    @strawberry.mutation
    async def enroll_learning_path(
        self,
        info,
        user_id: strawberry.ID,
        path_id: strawberry.ID
    ) -> LearningPath:
        """报名学习路径"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.enroll_learning_path(user_id, path_id)

    @strawberry.mutation
    async def update_learning_progress(
        self,
        info,
        user_id: strawberry.ID,
        path_id: strawberry.ID,
        progress: float
    ) -> LearningPath:
        """更新学习进度"""
        if progress < 0 or progress > 100:
            raise ValidationException("进度必须在0到100之间")

        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.update_learning_progress(user_id, path_id, progress)

    # 社区内容
    @strawberry.mutation
    async def create_community_post(
        self,
        info,
        input: CommunityPostInput
    ) -> CommunityPost:
        """创建社区帖子"""
        community_service = get_community_service(info.context)
        return await community_service.create_post(input)

    @strawberry.mutation
    async def update_community_post(
        self,
        info,
        id: strawberry.ID,
        input: CommunityPostInput
    ) -> CommunityPost:
        """更新社区帖子"""
        community_service = get_community_service(info.context)
        return await community_service.update_post(id, input)

    @strawberry.mutation
    async def create_comment(
        self,
        info,
        post_id: strawberry.ID,
        content: str
    ) -> Comment:
        """创建评论"""
        community_service = get_community_service(info.context)
        return await community_service.create_comment(post_id, content)

    # 教育课程
    @strawberry.mutation
    async def enroll_course(
        self,
        info,
        user_id: strawberry.ID,
        course_id: strawberry.ID
    ) -> EducationCourse:
        """报名课程"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.enroll_course(user_id, course_id)

    @strawberry.mutation
    async def complete_course_module(
        self,
        info,
        user_id: strawberry.ID,
        course_id: strawberry.ID,
        module_id: strawberry.ID
    ) -> bool:
        """完成课程模块"""
        knowledge_service = get_knowledge_service(info.context)
        return await knowledge_service.complete_course_module(user_id, course_id, module_id)

    # 游戏交互
    @strawberry.mutation
    async def send_npc_message(
        self,
        info,
        npc_id: strawberry.ID,
        message: str
    ) -> NPCInteractionResponse:
        """向NPC发送消息"""
        agent_manager = get_agent_manager(info.context)
        return await agent_manager.process_npc_message(npc_id, message)
