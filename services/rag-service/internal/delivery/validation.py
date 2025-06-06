"""
validation - 索克生活项目模块
"""

from datetime import datetime
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator, ValidationError
from typing import Any, Dict, List, Optional, Union, Tuple
import re
import structlog
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
输入验证和错误处理模块
提供统一的请求验证、错误处理和响应格式化功能
"""


logger = structlog.get_logger(__name__)

class ErrorCode:
    """错误代码常量"""
    
    # 通用错误
    INVALID_REQUEST = "INVALID_REQUEST"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # 业务错误
    QUERY_TOO_LONG = "QUERY_TOO_LONG"
    QUERY_TOO_SHORT = "QUERY_TOO_SHORT"
    INVALID_TOP_K = "INVALID_TOP_K"
    INVALID_COLLECTION = "INVALID_COLLECTION"
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    DOCUMENT_TOO_LARGE = "DOCUMENT_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    
    # 系统错误
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    VECTOR_DB_ERROR = "VECTOR_DB_ERROR"
    MODEL_ERROR = "MODEL_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

class APIError(Exception):
    """API错误基类"""
    
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)

class ValidationError(APIError):
    """验证错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.INVALID_REQUEST,
            message=message,
            details=details,
            status_code=400
        )

class AuthenticationError(APIError):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=401
        )

class AuthorizationError(APIError):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            status_code=403
        )

class ResourceNotFoundError(APIError):
    """资源未找到错误"""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=f"{resource}未找到",
            details={"resource": resource, "identifier": identifier},
            status_code=404
        )

class RateLimitError(APIError):
    """限流错误"""
    
    def __init__(self, limit: int, window: str, retry_after: int):
        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message="API调用频率超限",
            details={
                "limit": limit,
                "window": window,
                "retry_after": retry_after
            },
            status_code=429
        )

class ServiceUnavailableError(APIError):
    """服务不可用错误"""
    
    def __init__(self, service: str, message: str = "服务暂时不可用"):
        super().__init__(
            code=ErrorCode.SERVICE_UNAVAILABLE,
            message=message,
            details={"service": service},
            status_code=503
        )

# 请求验证模型

class QueryRequest(BaseModel):
    """查询请求验证模型"""
    
    query: str = Field(..., min_length=1, max_length=10000, description="查询内容")
    top_k: int = Field(default=5, ge=1, le=50, description="返回结果数量")
    system_prompt: Optional[str] = Field(None, max_length=5000, description="系统提示词")
    collection_names: Optional[List[str]] = Field(default=[], description="集合名称列表")
    generation_params: Optional[Dict[str, Any]] = Field(default={}, description="生成参数")
    metadata_filter: Optional[Dict[str, Any]] = Field(default={}, description="元数据过滤条件")
    user_id: Optional[str] = Field(None, description="用户ID")
    
    @validator('query')
        @cache(timeout=300)  # 5分钟缓存
def validate_query(cls, v):
        """验证查询内容"""
        if not v or not v.strip():
            raise ValueError("查询内容不能为空")
        
        # 检查是否包含恶意内容
        malicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'exec\s*\('
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("查询内容包含不安全字符")
        
        return v.strip()
    
    @validator('collection_names')
    def validate_collection_names(cls, v):
        """验证集合名称"""
        if v:
            for name in v:
                if not re.match(r'^[a-zA-Z0-9_-]+$', name):
                    raise ValueError(f"无效的集合名称: {name}")
        return v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """验证用户ID"""
        if v:
            try:
                uuid.UUID(v)
            except ValueError:
                if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                    raise ValueError("无效的用户ID格式")
        return v
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'queryrequest'
        ordering = ['-created_at']


class DocumentRequest(BaseModel):
    """文档请求验证模型"""
    
    content: str = Field(..., min_length=1, max_length=1000000, description="文档内容")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="文档元数据")
    source: Optional[str] = Field(None, max_length=200, description="文档来源")
    
    @validator('content')
    def validate_content(cls, v):
        """验证文档内容"""
        if not v or not v.strip():
            raise ValueError("文档内容不能为空")
        
        # 检查内容长度（字符数）
        if len(v) > 1000000:  # 1MB限制
            raise ValueError("文档内容过长，最大支持1MB")
        
        return v.strip()
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """验证元数据"""
        if v:
            # 检查元数据大小
            if len(str(v)) > 10000:  # 10KB限制
                raise ValueError("元数据过大，最大支持10KB")
            
            # 验证元数据键名
            for key in v.keys():
                if not isinstance(key, str) or not re.match(r'^[a-zA-Z0-9_-]+$', key):
                    raise ValueError(f"无效的元数据键名: {key}")
        
        return v
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'adddocumentrequest'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'tcmsyndromerequest'
        ordering = ['-created_at']


class AddDocumentRequest(BaseModel):
    """添加文档请求验证模型"""
    
    document: DocumentRequest = Field(..., description="文档信息")
    collection_name: str = Field(default="default", description="集合名称")
    reindex: bool = Field(default=True, description="是否重新索引")
    
    @validator('collection_name')
    def validate_collection_name(cls, v):
        """验证集合名称"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("无效的集合名称格式")
        return v
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'herbrecommendationrequest'
        ordering = ['-created_at']


class TCMSyndromeRequest(BaseModel):
    """中医证候分析请求验证模型"""
    
    symptoms: List[str] = Field(..., min_items=1, max_items=50, description="症状列表")
    pulse: Optional[str] = Field(None, max_length=100, description="脉象")
    tongue: Optional[str] = Field(None, max_length=100, description="舌象")
    constitution: Optional[str] = Field(None, max_length=50, description="体质类型")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    gender: Optional[str] = Field(None, regex=r'^(male|female|其他)$', description="性别")
    
    @validator('symptoms')
    def validate_symptoms(cls, v):
        """验证症状列表"""
        if not v:
            raise ValueError("症状列表不能为空")
        
        for symptom in v:
            if not symptom or not symptom.strip():
                raise ValueError("症状描述不能为空")
            if len(symptom) > 100:
                raise ValueError("单个症状描述过长")
        
        return [s.strip() for s in v]
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'batchqueryrequest'
        ordering = ['-created_at']


class HerbRecommendationRequest(BaseModel):
    """中药推荐请求验证模型"""
    
    condition: str = Field(..., min_length=1, max_length=200, description="病症描述")
    constitution: Optional[str] = Field(None, max_length=50, description="体质类型")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    gender: Optional[str] = Field(None, regex=r'^(male|female|其他)$', description="性别")
    contraindications: Optional[List[str]] = Field(default=[], description="禁忌症")
    
    @validator('condition')
    def validate_condition(cls, v):
        """验证病症描述"""
        if not v or not v.strip():
            raise ValueError("病症描述不能为空")
        return v.strip()

class BatchQueryRequest(BaseModel):
    """批量查询请求验证模型"""
    
    queries: List[QueryRequest] = Field(..., min_items=1, max_items=10, description="查询列表")
    parallel: bool = Field(default=True, description="是否并行处理")
    
    @validator('queries')
    def validate_queries(cls, v):
        """验证查询列表"""
        if len(v) > 10:
            raise ValueError("批量查询最多支持10个查询")
        return v

# 验证器函数

def validate_file_upload(file_content: bytes, filename: str) -> None:
    """验证上传文件"""
    
    # 检查文件大小（最大10MB）
    max_size = 10 * 1024 * 1024
    if len(file_content) > max_size:
        raise ValidationError(
            "文件过大",
            details={"max_size": "10MB", "actual_size": f"{len(file_content)} bytes"}
        )
    
    # 检查文件类型
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.doc', '.docx'}
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if f'.{file_ext}' not in allowed_extensions:
        raise ValidationError(
            "不支持的文件类型",
            details={
                "allowed_types": list(allowed_extensions),
                "actual_type": f".{file_ext}"
            }
        )
    
    # 检查文件内容（简单的魔数检查）
    if file_ext in ['jpg', 'jpeg']:
        if not file_content.startswith(b'\xff\xd8\xff'):
            raise ValidationError("文件内容与扩展名不匹配")
    elif file_ext == 'png':
        if not file_content.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValidationError("文件内容与扩展名不匹配")
    elif file_ext == 'pdf':
        if not file_content.startswith(b'%PDF'):
            raise ValidationError("文件内容与扩展名不匹配")

def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式"""
    if not api_key:
        return False
    
    # API密钥应该是32-64位的字母数字字符串
    if not re.match(r'^[a-zA-Z0-9_-]{32,64}$', api_key):
        return False
    
    return True

def validate_pagination(page: int, limit: int) -> Tuple[int, int]:
    """验证分页参数"""
    if page < 1:
        raise ValidationError("页码必须大于0")
    
    if limit < 1 or limit > 100:
        raise ValidationError("每页数量必须在1-100之间")
    
    return page, limit

def sanitize_input(text: str) -> str:
    """清理输入文本"""
    if not text:
        return ""
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除控制字符
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return text.strip()

# 错误处理器

async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """API错误处理器"""
    
    error_response = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        },
        "request_id": getattr(request.state, 'request_id', str(uuid.uuid4())),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # 记录错误日志
    logger.error(
        "API错误",
        error_code=exc.code,
        error_message=exc.message,
        error_details=exc.details,
        request_id=error_response["request_id"],
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Pydantic验证错误处理器"""
    
    details = {}
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'])
        details[field] = error['msg']
    
    api_error = APIError(
        code=ErrorCode.INVALID_REQUEST,
        message="请求参数验证失败",
        details=details,
        status_code=400
    )
    
    return await api_error_handler(request, api_error)

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    
    # 将HTTPException转换为APIError
    error_code_map = {
        400: ErrorCode.INVALID_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        503: ErrorCode.SERVICE_UNAVAILABLE
    }
    
    api_error = APIError(
        code=error_code_map.get(exc.status_code, "UNKNOWN_ERROR"),
        message=exc.detail,
        status_code=exc.status_code
    )
    
    return await api_error_handler(request, api_error)

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    
    # 记录未处理的异常
    logger.exception(
        "未处理的异常",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    api_error = APIError(
        code="INTERNAL_SERVER_ERROR",
        message="服务器内部错误",
        status_code=500
    )
    
    return await api_error_handler(request, api_error)

# 中间件

class RequestValidationMiddleware:
    """请求验证中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 添加请求ID
            request_id = str(uuid.uuid4())
            scope["state"] = {"request_id": request_id}
            
            # 添加请求开始时间
            scope["state"]["start_time"] = datetime.utcnow()
        
        await self.app(scope, receive, send)

# 装饰器

def validate_request(model_class):
    """请求验证装饰器"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 查找请求数据
            request_data = None
            for arg in args:
                if hasattr(arg, 'json'):
                    request_data = await arg.json()
                    break
            
            if request_data is None:
                for key, value in kwargs.items():
                    if isinstance(value, dict):
                        request_data = value
                        break
            
            if request_data:
                try:
                    # 验证请求数据
                    validated_data = model_class(**request_data)
                    # 将验证后的数据传递给函数
                    kwargs['validated_data'] = validated_data
                except ValidationError as e:
                    raise APIError(
                        code=ErrorCode.INVALID_REQUEST,
                        message="请求参数验证失败",
                        details={error['loc'][0]: error['msg'] for error in e.errors()},
                        status_code=400
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_api_key(func):
    """API密钥验证装饰器"""
    
    async def wrapper(*args, **kwargs):
        # 查找请求对象
        request = None
        for arg in args:
            if hasattr(arg, 'headers'):
                request = arg
                break
        
        if request:
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                raise AuthenticationError("缺少API密钥")
            
            if not validate_api_key(api_key):
                raise AuthenticationError("无效的API密钥格式")
            
            # 这里可以添加API密钥验证逻辑
            # 例如：从数据库验证密钥是否有效
        
        return await func(*args, **kwargs)
    
    return wrapper 