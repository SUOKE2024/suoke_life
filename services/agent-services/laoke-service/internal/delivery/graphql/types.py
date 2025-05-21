#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - GraphQL 类型定义
提供所有 GraphQL 类型和连接类型
"""

from typing import List, Optional
import datetime

import strawberry
from strawberry.types import Info

from internal.delivery.graphql.pagination import Connection, Edge, PageInfo

# 基本类型
@strawberry.type
class User:
    id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    role: str
    specialization: List[str]
    contribution_score: int
    joined_at: str

@strawberry.type
class KnowledgeArticle:
    id: str
    title: str
    content: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str]
    author: Optional[User] = None
    created_at: str
    updated_at: Optional[str] = None
    rating: Optional[float] = None
    rating_count: int = 0
    view_count: int = 0
    related_topics: List["KnowledgeArticle"] = strawberry.field(default_factory=list)

@strawberry.input
class KnowledgeArticleInput:
    title: str
    content: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str]

@strawberry.type
class Resource:
    id: str
    title: str
    type: str
    url: str
    description: Optional[str] = None

@strawberry.type
class QuizQuestion:
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None

@strawberry.type
class Quiz:
    id: str
    title: str
    questions: List[QuizQuestion]
    passing_score: float

@strawberry.type
class LearningModule:
    id: str
    title: str
    description: str
    content: str
    resources: List[Resource]
    quizzes: List[Quiz]
    order: int

@strawberry.type
class LearningPath:
    id: str
    title: str
    description: str
    category: str
    level: str
    estimated_duration: str
    modules: List[LearningModule]
    prerequisites: List["LearningPath"]
    enrolled_users: int = 0
    completion_rate: float = 0.0

@strawberry.type
class Comment:
    id: str
    content: str
    author: User
    created_at: str
    like_count: int = 0
    replies: List["Comment"] = strawberry.field(default_factory=list)

@strawberry.type
class CommunityPost:
    id: str
    title: str
    content: str
    author: User
    category: str
    tags: List[str]
    created_at: str
    updated_at: Optional[str] = None
    like_count: int = 0
    comment_count: int = 0
    comments: List[Comment]
    is_featured: bool = False

@strawberry.input
class CommunityPostInput:
    title: str
    content: str
    category: str
    tags: List[str]

@strawberry.type
class Lesson:
    id: str
    title: str
    content: str
    video_url: Optional[str] = None
    duration: str
    order: int

@strawberry.type
class CourseModule:
    id: str
    title: str
    description: str
    lessons: List[Lesson]
    quiz: Optional[Quiz] = None
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
    modules: List[CourseModule]
    estimated_duration: str
    enrolled_count: int = 0
    rating: Optional[float] = None
    certification_enabled: bool = False

@strawberry.type
class NPCAction:
    id: str
    type: str
    description: str
    requirements_met: bool
    rewards: List[str]

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
    actions: Optional[List[NPCAction]] = None
    knowledge: Optional[List[str]] = None

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