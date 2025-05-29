#!/usr/bin/env python

"""
老克智能体服务 - GraphQL 类型定义
提供所有 GraphQL 类型和连接类型
"""


import strawberry

from internal.delivery.graphql.pagination import Connection, Edge


# 基本类型
@strawberry.type
class User:
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
    title: str
    content: str
    category: str
    subcategory: str | None = None
    tags: list[str]

@strawberry.type
class Resource:
    id: str
    title: str
    type: str
    url: str
    description: str | None = None

@strawberry.type
class QuizQuestion:
    id: str
    question: str
    options: list[str]
    correct_answer: int
    explanation: str | None = None

@strawberry.type
class Quiz:
    id: str
    title: str
    questions: list[QuizQuestion]
    passing_score: float

@strawberry.type
class LearningModule:
    id: str
    title: str
    description: str
    content: str
    resources: list[Resource]
    quizzes: list[Quiz]
    order: int

@strawberry.type
class LearningPath:
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
    id: str
    content: str
    author: User
    created_at: str
    like_count: int = 0
    replies: list["Comment"] = strawberry.field(default_factory=list)

@strawberry.type
class CommunityPost:
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
    title: str
    content: str
    category: str
    tags: list[str]

@strawberry.type
class Lesson:
    id: str
    title: str
    content: str
    video_url: str | None = None
    duration: str
    order: int

@strawberry.type
class CourseModule:
    id: str
    title: str
    description: str
    lessons: list[Lesson]
    quiz: Quiz | None = None
    order: int

@strawberry.enum
class CourseLevel:
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"

@strawberry.type
class EducationCourse:
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
    id: str
    type: str
    description: str
    requirements_met: bool
    rewards: list[str]

@strawberry.enum
class ActionType:
    QUEST = "QUEST"
    CHALLENGE = "CHALLENGE"
    REWARD = "REWARD"
    DIALOGUE = "DIALOGUE"
    GAME = "GAME"

@strawberry.type
class GameNPC:
    id: str
    name: str
    role: str
    personality: str
    backstory: str
    avatar_url: str
    dialogue_style: str

@strawberry.type
class NPCInteractionResponse:
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
