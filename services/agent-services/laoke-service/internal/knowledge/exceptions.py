"""
exceptions - 索克生活项目模块
"""

from laoke_service.core.exceptions import ServiceException

"""
知识服务专用异常类
"""


class KnowledgeServiceException(ServiceException):
    """知识服务基础异常"""

    pass


class ArticleNotFoundException(KnowledgeServiceException):
    """文章未找到异常"""

    def __init__(self, article_id: str):
        super().__init__(f"文章未找到: {article_id}")
        self.article_id = article_id


class ArticleCreationException(KnowledgeServiceException):
    """文章创建异常"""

    def __init__(self, reason: str):
        super().__init__(f"文章创建失败: {reason}")


class ArticleUpdateException(KnowledgeServiceException):
    """文章更新异常"""

    def __init__(self, article_id: str, reason: str):
        super().__init__(f"文章更新失败 {article_id}: {reason}")
        self.article_id = article_id


class LearningPathNotFoundException(KnowledgeServiceException):
    """学习路径未找到异常"""

    def __init__(self, path_id: str):
        super().__init__(f"学习路径未找到: {path_id}")
        self.path_id = path_id


class UserProgressException(KnowledgeServiceException):
    """用户进度异常"""

    def __init__(self, user_id: str, path_id: str, reason: str):
        super().__init__(f"用户进度操作失败 {user_id}/{path_id}: {reason}")
        self.user_id = user_id
        self.path_id = path_id


class RepositoryException(KnowledgeServiceException):
    """数据访问异常"""

    def __init__(self, operation: str, reason: str):
        super().__init__(f"数据访问失败 {operation}: {reason}")
        self.operation = operation


class ValidationException(KnowledgeServiceException):
    """数据验证异常"""

    def __init__(self, field: str, reason: str):
        super().__init__(f"数据验证失败 {field}: {reason}")
        self.field = field
