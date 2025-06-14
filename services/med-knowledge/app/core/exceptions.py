"""
自定义异常类
提供医学知识服务的专用异常处理
"""
from typing import Any, Dict, Optional


class MedKnowledgeException(Exception):
    """医学知识服务基础异常"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(MedKnowledgeException):
    """数据库相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details
        )


class ConnectionException(DatabaseException):
    """数据库连接异常"""
    
    def __init__(self, message: str = "数据库连接失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.error_code = "DATABASE_CONNECTION_ERROR"


class QueryException(DatabaseException):
    """数据库查询异常"""
    
    def __init__(self, message: str, query: str = "", details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["query"] = query
        super().__init__(message, details)
        self.error_code = "DATABASE_QUERY_ERROR"


class CacheException(MedKnowledgeException):
    """缓存相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=details
        )


class CacheConnectionException(CacheException):
    """缓存连接异常"""
    
    def __init__(self, message: str = "缓存服务连接失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.error_code = "CACHE_CONNECTION_ERROR"


class ValidationException(MedKnowledgeException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: str = "", details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class EntityNotFoundException(MedKnowledgeException):
    """实体未找到异常"""
    
    def __init__(self, entity_type: str, entity_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"{entity_type} (ID: {entity_id}) 未找到"
        details = details or {}
        details.update({
            "entity_type": entity_type,
            "entity_id": entity_id
        })
        super().__init__(
            message=message,
            error_code="ENTITY_NOT_FOUND",
            details=details
        )


class SearchException(MedKnowledgeException):
    """搜索相关异常"""
    
    def __init__(self, message: str, query: str = "", details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["query"] = query
        super().__init__(
            message=message,
            error_code="SEARCH_ERROR",
            details=details
        )


class InvalidQueryException(SearchException):
    """无效查询异常"""
    
    def __init__(self, query: str, reason: str = "", details: Optional[Dict[str, Any]] = None):
        message = f"无效的查询: {query}"
        if reason:
            message += f" - {reason}"
        details = details or {}
        details["reason"] = reason
        super().__init__(message, query, details)
        self.error_code = "INVALID_QUERY"


class ServiceUnavailableException(MedKnowledgeException):
    """服务不可用异常"""
    
    def __init__(self, service_name: str, details: Optional[Dict[str, Any]] = None):
        message = f"服务 {service_name} 不可用"
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            details=details
        )


class RateLimitException(MedKnowledgeException):
    """限流异常"""
    
    def __init__(self, limit: str, details: Optional[Dict[str, Any]] = None):
        message = f"请求频率超过限制: {limit}"
        details = details or {}
        details["limit"] = limit
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class AuthenticationException(MedKnowledgeException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(MedKnowledgeException):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ConfigurationException(MedKnowledgeException):
    """配置异常"""
    
    def __init__(self, message: str, config_key: str = "", details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["config_key"] = config_key
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details
        )


class DataImportException(MedKnowledgeException):
    """数据导入异常"""
    
    def __init__(self, message: str, source: str = "", details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["source"] = source
        super().__init__(
            message=message,
            error_code="DATA_IMPORT_ERROR",
            details=details
        )


class GraphException(MedKnowledgeException):
    """知识图谱异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="GRAPH_ERROR",
            details=details
        )


class PathNotFoundException(GraphException):
    """路径未找到异常"""
    
    def __init__(self, from_node: str, to_node: str, details: Optional[Dict[str, Any]] = None):
        message = f"未找到从 {from_node} 到 {to_node} 的路径"
        details = details or {}
        details.update({
            "from_node": from_node,
            "to_node": to_node
        })
        super().__init__(message, details)
        self.error_code = "PATH_NOT_FOUND"


class RelationshipException(GraphException):
    """关系异常"""
    
    def __init__(self, message: str, relationship_type: str = "", details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["relationship_type"] = relationship_type
        super().__init__(message, details)
        self.error_code = "RELATIONSHIP_ERROR"


# 异常映射字典，用于HTTP状态码映射
EXCEPTION_STATUS_MAP = {
    MedKnowledgeException: 500,
    DatabaseException: 503,
    ConnectionException: 503,
    QueryException: 500,
    CacheException: 500,
    CacheConnectionException: 503,
    ValidationException: 400,
    EntityNotFoundException: 404,
    SearchException: 500,
    InvalidQueryException: 400,
    ServiceUnavailableException: 503,
    RateLimitException: 429,
    AuthenticationException: 401,
    AuthorizationException: 403,
    ConfigurationException: 500,
    DataImportException: 500,
    GraphException: 500,
    PathNotFoundException: 404,
    RelationshipException: 500,
}


def get_http_status_code(exception: Exception) -> int:
    """根据异常类型获取HTTP状态码"""
    for exc_type, status_code in EXCEPTION_STATUS_MAP.items():
        if isinstance(exception, exc_type):
            return status_code
    return 500  # 默认返回500


def format_error_response(exception: Exception) -> Dict[str, Any]:
    """格式化异常为错误响应"""
    if isinstance(exception, MedKnowledgeException):
        return {
            "error": {
                "code": exception.error_code,
                "message": exception.message,
                "details": exception.details
            }
        }
    else:
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exception),
                "details": {}
            }
        } 