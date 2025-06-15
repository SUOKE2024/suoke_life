from typing import Any, Dict, List, Optional, Union

"""
graphql_types - 索克生活项目模块
"""

import strawberry
from internal.delivery.graphql.pagination import Connection, Edge

# !/usr/bin/env python

"""
老克智能体服务 - GraphQL 类型定义
提供所有 GraphQL 类型和连接类型
"""


# 基本类型
@strawberry.type
class User:
    """用户信息类型
    
    表示系统中的用户，包含基本信息、角色和专业领域。
    用于社区互动和知识分享。
    """

    id: str
    username: str
    display_name: str
    avatar_url: str | None = None
    role: str
    specialization: list[str]
    contribution_score: int
    joined_at: str


@strawberry.type
class KnowledgeArticle:
    """知识文章类型
    
    表示知识库中的文章，包含内容、分类、标签和评分信息。
    支持相关主题关联和用户互动。
    """

    id: str
    title: str
    content: str
    category: str
    subcategory: str | None = None
    tags: list[str]
    author: User | None = None
    created_at: str
    updated_at: str | None = None
    rating: float | None = None
    rating_count: int = 0
    view_count: int = 0
    related_topics: list["KnowledgeArticle"] = strawberry.field(default_factory=list)


@strawberry.input
class KnowledgeArticleInput:
    """知识文章输入类型
    
    用于创建或更新知识文章的输入数据结构。
    包含文章的基本信息和分类标签。
    """

    title: str
    content: str
    category: str
    subcategory: str | None = None
    tags: list[str]


@strawberry.type
class Resource:
    """学习资源类型
    
    表示学习模块中的资源，如文档、视频、链接等。
    提供多媒体学习支持。
    """

    id: str
    title: str
    type: str
    url: str
    description: str | None = None


@strawberry.type
class QuizQuestion:
    """测验问题类型
    
    表示测验中的单个问题，包含选项、正确答案和解释。
    用于知识掌握程度评估。
    """

    id: str
    question: str
    options: list[str]
    correct_answer: int
    explanation: str | None = None


@strawberry.type
class Quiz:
    """测验类型
    
    表示完整的测验，包含多个问题和及格分数。
    用于学习效果验证。
    """

    id: str
    title: str
    questions: list[QuizQuestion]
    passing_score: float


@strawberry.type
class LearningModule:
    """学习模块类型
    
    表示学习路径中的单个模块，包含内容、资源和测验。
    提供结构化的学习体验。
    """

    id: str
    title: str
    description: str
    content: str
    resources: list[Resource]
    quizzes: list[Quiz]
    order: int


@strawberry.type
class LearningPath:
    """学习路径类型
    
    表示完整的学习路径，包含多个模块和前置条件。
    提供系统化的知识学习体系。
    """

    id: str
    title: str
    description: str
    category: str
    level: str
    estimated_duration: str
    modules: list[LearningModule]
    prerequisites: list["LearningPath"]
    enrolled_users: int = 0
    completion_rate: float = 0.0


@strawberry.type
class Comment:
    """评论类型
    
    表示用户在社区帖子或文章下的评论。
    支持嵌套回复和点赞功能。
    """

    id: str
    content: str
    author: User
    created_at: str
    like_count: int = 0
    replies: list["Comment"] = strawberry.field(default_factory=list)


@strawberry.type
class CommunityPost:
    """社区帖子类型
    
    表示社区中的用户发帖，包含内容、分类和互动数据。
    支持用户交流和知识分享。
    """

    id: str
    title: str
    content: str
    author: User
    category: str
    tags: list[str]
    created_at: str
    updated_at: str | None = None
    like_count: int = 0
    comment_count: int = 0
    comments: list[Comment]
    is_featured: bool = False


@strawberry.input
class CommunityPostInput:
    """社区帖子输入类型
    
    用于创建社区帖子的输入数据结构。
    包含帖子的基本信息和分类标签。
    """

    title: str
    content: str
    category: str
    tags: list[str]


@strawberry.type
class Lesson:
    """课程课时类型
    
    表示教育课程中的单个课时，包含内容和视频资源。
    提供结构化的教学内容。
    """

    id: str
    title: str
    content: str
    video_url: str | None = None
    duration: str
    order: int


@strawberry.type
class CourseModule:
    """课程模块类型
    
    表示教育课程中的模块，包含多个课时和测验。
    提供模块化的教学结构。
    """

    id: str
    title: str
    description: str
    lessons: list[Lesson]
    quiz: Quiz | None = None
    order: int


@strawberry.enum
class CourseLevel:
    """课程难度级别枚举
    
    定义课程的难度等级，从初级到专家级。
    用于课程分类和学习路径规划。
    """

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


@strawberry.type
class EducationCourse:
    """教育课程类型
    
    表示完整的教育课程，包含模块、讲师和认证信息。
    提供系统化的专业教育。
    """

    id: str
    title: str
    description: str
    category: str
    level: CourseLevel
    instructor: User
    modules: list[CourseModule]
    estimated_duration: str
    enrolled_count: int = 0
    rating: float | None = None
    certification_enabled: bool = False


@strawberry.type
class NPCAction:
    """NPC 行动类型
    
    表示游戏化 NPC 可执行的行动，包含要求和奖励。
    用于互动式学习体验。
    """

    id: str
    type: str
    description: str
    requirements_met: bool
    rewards: list[str]


@strawberry.enum
class ActionType:
    """行动类型枚举
    
    定义 NPC 可执行的行动类型，如任务、挑战、对话等。
    用于游戏化学习机制。
    """

    QUEST = "QUEST"
    CHALLENGE = "CHALLENGE"
    REWARD = "REWARD"
    DIALOGUE = "DIALOGUE"
    GAME = "GAME"


@strawberry.type
class GameNPC:
    """游戏 NPC 类型
    
    表示游戏化学习中的 NPC 角色，包含个性和背景故事。
    提供沉浸式的学习体验。
    """

    id: str
    name: str
    role: str
    personality: str
    backstory: str
    avatar_url: str
    dialogue_style: str


@strawberry.type
class NPCInteractionResponse:
    """NPC 交互响应类型
    
    表示与 NPC 交互后的响应，包含消息、情绪和可用行动。
    用于动态的学习互动。
    """

    message: str
    emotion: str
    actions: list[NPCAction] | None = None
    knowledge: list[str] | None = None


# 分页查询连接类型


@strawberry.type
class KnowledgeArticleEdge(Edge[KnowledgeArticle]):
    """知识文章边缘类型"""

    pass


@strawberry.type
class KnowledgeArticleConnection(Connection[KnowledgeArticle]):
    """知识文章连接类型"""

    pass


@strawberry.type
class LearningPathEdge(Edge[LearningPath]):
    """学习路径边缘类型"""

    pass


@strawberry.type
class LearningPathConnection(Connection[LearningPath]):
    """学习路径连接类型"""

    pass


@strawberry.type
class CommunityPostEdge(Edge[CommunityPost]):
    """社区帖子边缘类型"""

    pass


@strawberry.type
class CommunityPostConnection(Connection[CommunityPost]):
    """社区帖子连接类型"""

    pass


@strawberry.type
class EducationCourseEdge(Edge[EducationCourse]):
    """教育课程边缘类型"""

    pass


@strawberry.type
class EducationCourseConnection(Connection[EducationCourse]):
    """教育课程连接类型"""

    pass
