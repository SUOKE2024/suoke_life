"""
auth - 索克生活项目模块
"""

import time

from fastapi import Request, Response, status
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import get_settings
from ..core.logging import get_logger

"""
认证中间件

处理 JWT 令牌验证、用户身份认证等功能。
"""




logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""

    def __init__(self, app, settings = None):
"""TODO: 添加文档字符串"""
super().__init__(app)
self.settings = settings or get_settings()
self.jwt_config = self.settings.jwt

# 不需要认证的路径
self.public_paths = {
            " / ",
            " / health",
            " / health / ready",
            " / health / live",
            " / metrics",
            " / docs",
            " / redoc",
            " / openapi.json",
            " / api / v1 / auth / login",
            " / api / v1 / auth / register",
            " / api / v1 / auth / refresh",
}

    async def dispatch(self, request: Request, call_next):
"""处理请求"""
start_time = time.time()

# 检查是否为公开路径
if self._is_public_path(request.url.path):
            response = await call_next(request)
            return response

# 提取并验证 JWT 令牌
token = self._extract_token(request)
if not token:
            return self._create_auth_error("Missing authentication token")

try:
            # 验证令牌
            payload = self._verify_token(token)

            # 将用户信息添加到请求状态
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")
            request.state.user_roles = payload.get("roles", [])

            # 记录认证成功
            logger.info(
                "Authentication successful",
                user_id = request.state.user_id,
                path = request.url.path,
                method = request.method,
            )

except JWTError as e:
            logger.warning(
                "JWT validation failed",
                error = str(e),
                path = request.url.path,
                method = request.method,
            )
            return self._create_auth_error("Invalid authentication token")

except Exception as e:
            logger.error(
                "Authentication error",
                error = str(e),
                path = request.url.path,
                method = request.method,
                exc_info = True,
            )
            return self._create_auth_error("Authentication failed")

# 继续处理请求
response = await call_next(request)

# 记录处理时间
process_time = time.time() - start_time
response.headers["X - Process - Time"] = str(process_time)

return response

    def _is_public_path(self, path: str) -> bool:
"""检查是否为公开路径"""
# 精确匹配
if path in self.public_paths:
            return True

# 前缀匹配
public_prefixes = [" / docs", " / redoc", " / static"]
return any(path.startswith(prefix) for prefix in public_prefixes)

    def _extract_token(self, request: Request) -> str | None:
"""从请求中提取 JWT 令牌"""
# 从 Authorization 头提取
authorization = request.headers.get("Authorization")
if authorization and authorization.startswith("Bearer "):
            return authorization[7:]  # 移除 "Bearer " 前缀

# 从查询参数提取（不推荐，仅用于特殊情况）
token = request.query_params.get("token")
if token:
            return token

return None

    def _verify_token(self, token: str) -> dict:
"""验证 JWT 令牌"""
try:
            payload = jwt.decode(
                token,
                self.jwt_config.secret_key,
                algorithms = [self.jwt_config.algorithm],
            )

            # 检查令牌是否过期
            exp = payload.get("exp")
            if exp and time.time() > exp:
                raise JWTError("Token has expired")

            return payload

except JWTError:
            raise
except Exception as e:
            raise JWTError(f"Token validation failed: {e!s}")

    def _create_auth_error(self, message: str) -> Response:
"""创建认证错误响应"""
return Response(
            content = f'{{"error": "Unauthorized", "message": "{message}"}}',
            status_code = status.HTTP_401_UNAUTHORIZED,
            headers = {"Content - Type": "application / json"},
)
