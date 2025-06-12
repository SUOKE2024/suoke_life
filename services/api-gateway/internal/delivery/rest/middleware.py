"""
middleware - 索克生活项目模块
"""

import fnmatch
import logging
import time
import uuid
from typing import Callable, Dict, List, Optional, Set, Union

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from internal.model.config import (
    AuthConfig,
    CorsConfig,
    GatewayConfig,
    MiddlewareConfig,
    RateLimitConfig,
)
from pkg.utils.auth import JWTManager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
REST API中间件模块
提供CORS、身份验证、请求日志等功能
"""





logger = logging.getLogger(__name__)


def extract_token_from_header(auth_header: str) -> str:
    """
    从Authorization头中提取JWT令牌

    Args:
auth_header: Authorization请求头值

    Returns:
str: JWT令牌

    Raises:
ValueError: 如果令牌格式无效
    """
    if not auth_header:
raise ValueError("Authorization头为空")

    parts = auth_header.split()

    if parts[0].lower() !="bearer":
raise ValueError("认证类型必须为Bearer")

    if len(parts) !=2:
raise ValueError("无效的Authorization头格式")

    return parts[1]


def setup_middlewares(app: FastAPI, config: Union[GatewayConfig, MiddlewareConfig]) -> None:
    """
    设置FastAPI中间件

    Args:
app: FastAPI应用实例
config: 网关配置或中间件配置
    """
    # 获取正确的中间件配置
    middleware_config = config if isinstance(config, MiddlewareConfig) else config.middleware

    # 添加CORS中间件
    if middleware_config.cors and middleware_config.cors.enabled:
app.add_middleware(
            CORSMiddleware,
            allow_origins = middleware_config.cors.allow_origins,
            allow_credentials = middleware_config.cors.allow_credentials,
            allow_methods = middleware_config.cors.allow_methods,
            allow_headers = middleware_config.cors.allow_headers,
            max_age = middleware_config.cors.max_age,
)
logger.info("已启用CORS中间件")

    # 添加请求ID中间件
    app.add_middleware(RequestIdMiddleware)

    # 添加日志中间件
    app.add_middleware(LoggingMiddleware)

    # 添加限流中间件
    if middleware_config.rate_limit and middleware_config.rate_limit.enabled:
app.add_middleware(
            RateLimitMiddleware,
            config = middleware_config.rate_limit,
)
logger.info("已启用限流中间件")

    # 添加认证中间件
    if middleware_config.auth and middleware_config.auth.enabled:
# 创建JWT管理器
jwt_manager = JWTManager(middleware_config.auth.jwt)

app.add_middleware(
            AuthMiddleware,
            config = middleware_config.auth,
            jwt_manager = jwt_manager,
)
logger.info("已启用认证中间件")

    # 添加可信主机中间件
    if middleware_config.trusted_hosts and middleware_config.trusted_hosts:
app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts = middleware_config.trusted_hosts
)
logger.info(f"已启用可信主机中间件，允许的主机: {middleware_config.trusted_hosts}")

    # GZip压缩中间件
    if getattr(config, 'compression_enabled', False):
app.add_middleware(GZipMiddleware, minimum_size = 1000)

    logger.info("所有中间件设置完成")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """为每个请求添加唯一ID"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
request_id = request.headers.get("X - Request - ID") or str(uuid.uuid4())
request.state.request_id = request_id

# 添加请求ID到响应头
response = await call_next(request)
response.headers["X - Request - ID"] = request_id

return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
start_time = time.time()

# 获取请求信息
request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
method = request.method
url = str(request.url)

logger.info(f"Request started: {method} {url} (ID: {request_id})")

try:
            # 调用下一个中间件或路由处理函数
            response = await call_next(request)

            # 记录响应日志
            status_code = response.status_code
            process_time = time.time() - start_time

            logger.info(
                f"Request completed: {method} {url} - Status: {status_code} "
                f"Time: {process_time:.3f}s (ID: {request_id})"
            )

            return response
except Exception as e:
            # 记录异常日志
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {method} {url} - Error: {str(e)} "
                f"Time: {process_time:.3f}s (ID: {request_id})",
                exc_info = True
            )

            # 返回错误响应
            return JSONResponse(
                status_code = 500,
                content = {"detail": "服务器内部错误"},
                headers = {
                    "X - Request - ID": request_id,
                    "X - Process - Time": str(process_time),
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """请求限流中间件"""

    def __init__(self, app: FastAPI, config: RateLimitConfig) -> None:
"""
初始化限流中间件

Args:
            app: FastAPI应用实例
            config: 限流配置
"""
super().__init__(app)
self.config = config
self.request_counts = {}  # 简单计数器，生产环境应使用Redis
self.last_reset = time.time()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
# 如果未启用速率限制，直接处理请求
if not self.config.enabled:
            return await call_next(request)

# 获取客户端IP
client_ip = request.client.host if request.client else "unknown"

# 检查是否需要重置计数器
now = time.time()
if now - self.last_reset > self.config.reset_interval:
            self.request_counts = {}
            self.last_reset = now

# 检查请求计数
current_count = self.request_counts.get(client_ip, 0)

if current_count >=self.config.max_requests:
            logger.warning(f"请求被限流 - IP: {client_ip}")
            return JSONResponse(
                status_code = 429,
                content = {"detail": "请求过于频繁，请稍后重试"}
            )

# 更新计数器
self.request_counts[client_ip] = current_count + 1

# 调用下一个中间件或路由处理函数
return await call_next(request)


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""

    def __init__(self, app: FastAPI, config: AuthConfig, jwt_manager) -> None:
"""
初始化认证中间件

Args:
            app: FastAPI应用实例
            config: 认证配置
            jwt_manager: JWT管理器
"""
super().__init__(app)
self.config = config
self.jwt_manager = jwt_manager
self.public_paths: List[str] = config.public_paths or []
self.public_path_prefixes: Set[str] = {
            path.rstrip(" * ") for path in self.public_paths if path.endswith(" * ")
}

    def _is_public_path(self, path: str) -> bool:
"""
检查路径是否为公共路径（不需要认证）

Args:
            path: 请求路径

Returns:
            是否为公共路径
"""
# 检查完全匹配
if path in self.public_paths:
            return True

# 检查通配符匹配
for pattern in self.public_paths:
            if " * " in pattern and fnmatch.fnmatch(path, pattern):
                return True

# 检查前缀匹配
for prefix in self.public_path_prefixes:
            if path.startswith(prefix):
                return True

return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
"""
处理请求

Args:
            request: 请求对象
            call_next: 下一个处理器

Returns:
            响应对象
"""
# 如果未启用认证，直接处理请求
if not self.config.enabled:
            return await call_next(request)

# 检查是否为公共路径
path = request.url.path
if self._is_public_path(path):
            return await call_next(request)

# 从请求头获取认证令牌
auth_header = request.headers.get("Authorization")
if not auth_header:
            logger.warning(f"未提供认证令牌 - 路径: {path}")
            return JSONResponse(
                status_code = 401,
                content = {"detail": "未提供认证令牌"}
            )

# 提取令牌
try:
            # 使用独立的extract_token_from_header函数
            token = extract_token_from_header(auth_header)
except ValueError as e:
            logger.warning(f"无效的认证令牌格式 - 路径: {path}, 错误: {str(e)}")
            return JSONResponse(
                status_code = 401,
                content = {"detail": "无效的认证令牌格式"}
            )

# 验证令牌
try:
            # 使用validate_token方法验证令牌
            token_data = self.jwt_manager.validate_token(token)
except ValueError as e:
            error_msg = str(e)
            logger.warning(f"令牌验证失败 - 路径: {path}, 错误: {error_msg}")

            # 根据错误类型返回适当的状态码
            status_code = 401
            if "已过期" in error_msg:
                error_detail = "令牌已过期"
            elif "尚未生效" in error_msg:
                error_detail = "令牌尚未生效"
            elif "签名无效" in error_msg:
                error_detail = "令牌签名无效"
            elif "已被撤销" in error_msg:
                error_detail = "令牌已被撤销"
            else:
                error_detail = "无效的认证令牌"

            return JSONResponse(
                status_code = status_code,
                content = {"detail": error_detail}
            )

# 令牌有效，提取用户信息
user_id = token_data.sub
user_roles = token_data.roles

# 将用户信息存储在请求状态中，供后续处理使用
request.state.user_id = user_id
request.state.user_roles = user_roles
request.state.token_data = token_data

# 调用下一个中间件或路由处理函数
return await call_next(request)
