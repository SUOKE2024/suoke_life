"""
response_models - 索克生活项目模块
"""

from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Optional
from enum import Enum


"""
统一响应模型
"""


T = TypeVar('T')


class ResponseStatus(Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ApiResponse(Generic[T]):
    """统一API响应格式"""
    status: ResponseStatus
    data: Optional[T] = None
    message: str = ""
    error_code: Optional[str] = None
    timestamp: Optional[str] = None

    @classmethod
    def success(cls, data: T = None, message: str = "操作成功") -> 'ApiResponse[T]':
        """创建成功响应"""
        from datetime import datetime
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            message=message,
            timestamp=datetime.utcnow().isoformat()
        )

    @classmethod
    def error(cls, message: str, error_code: str = None,
              data: T = None) -> 'ApiResponse[T]':
        """创建错误响应"""
        from datetime import datetime
        return cls(
            status=ResponseStatus.ERROR,
            data=data,
            message=message,
            error_code=error_code,
            timestamp=datetime.utcnow().isoformat()
        )

    @classmethod
    def warning(cls, message: str, data: T = None) -> 'ApiResponse[T]':
        """创建警告响应"""
        from datetime import datetime
        return cls(
            status=ResponseStatus.WARNING,
            data=data,
            message=message,
            timestamp=datetime.utcnow().isoformat()
        )


@dataclass
class PaginatedResponse(Generic[T]):
    """分页响应格式"""
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

    @property
    def total_pages(self) -> int:
        """总页数"""
        return (self.total + self.page_size - 1)//self.page_size


@dataclass
class ArticleResponse:
    """文章响应模型"""
    id: str
    title: str
    content: str
    category: str
    tags: list[str]
    author_id: str
    created_at: str
    view_count: int
    rating: float
    rating_count: int


@dataclass
class LearningPathResponse:
    """学习路径响应模型"""
    id: str
    title: str
    description: str
    category: str
    level: str
    estimated_duration: str
    modules_count: int
    enrolled_users: int
    completion_rate: float


@dataclass
class UserProgressResponse:
    """用户进度响应模型"""
    user_id: str
    path_id: str
    progress_percentage: float
    completed_modules: int
    total_modules: int
    last_accessed: str
    estimated_completion: str
