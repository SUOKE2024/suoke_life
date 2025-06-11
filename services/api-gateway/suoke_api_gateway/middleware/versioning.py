"""
versioning - 索克生活项目模块
"""

from ..core.logging import get_logger
from enum import Enum
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Dict, List, Optional, Tuple
import re

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
API 版本管理中间件

支持多种 API 版本控制策略，包括 URL 路径、查询参数、请求头等方式。
"""




logger = get_logger(__name__)

class VersionStrategy(Enum):
    """版本控制策略"""
    URL_PATH = "url_path"          # / v1 / users, / v2 / users
    QUERY_PARAM = "query_param"    # / users?version = v1
    HEADER = "header"              # Accept: application / vnd.api + json;version = 1
    SUBDOMAIN = "subdomain"        # v1.api.example.com
    CUSTOM_HEADER = "custom_header" # X - API - Version: v1

class VersionInfo:
    """版本信息"""

    def __init__(
self,
version: str,
major: int,
minor: int = 0,
patch: int = 0,
is_deprecated: bool = False,
deprecation_date: Optional[str] = None,
sunset_date: Optional[str] = None,
    ):
self.version = version
self.major = major
self.minor = minor
self.patch = patch
self.is_deprecated = is_deprecated
self.deprecation_date = deprecation_date
self.sunset_date = sunset_date

    @classmethod
    def from_string(cls, version_str: str) -> 'VersionInfo':
"""从版本字符串创建版本信息"""
# 移除 'v' 前缀
if version_str.startswith('v'):
            version_str = version_str[1:]

# 解析版本号
parts = version_str.split('.')
major = int(parts[0]) if len(parts) > 0 else 1
minor = int(parts[1]) if len(parts) > 1 else 0
patch = int(parts[2]) if len(parts) > 2 else 0

return cls(
            version = f"v{major}.{minor}.{patch}",
            major = major,
            minor = minor,
            patch = patch,
)

    def __str__(self) -> str:
"""TODO: 添加文档字符串"""
return self.version

    def __eq__(self, other) -> bool:
"""TODO: 添加文档字符串"""
if isinstance(other, VersionInfo):
            return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
return False

    def __lt__(self, other) -> bool:
"""TODO: 添加文档字符串"""
if isinstance(other, VersionInfo):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
return False

    def __le__(self, other) -> bool:
"""TODO: 添加文档字符串"""
return self == other or self < other

    def __gt__(self, other) -> bool:
"""TODO: 添加文档字符串"""
return not self < = other

    def __ge__(self, other) -> bool:
"""TODO: 添加文档字符串"""
return not self < other

class VersionMatcher:
    """版本匹配器"""

    def __init__(self) -> None:
"""TODO: 添加文档字符串"""
self.route_versions: Dict[str, List[VersionInfo]] = {}
self.default_version: Optional[VersionInfo] = None
self.supported_versions: List[VersionInfo] = []

    def add_route_version(self, route_pattern: str, version: VersionInfo) -> None:
"""添加路由版本映射"""
if route_pattern not in self.route_versions:
            self.route_versions[route_pattern] = []

self.route_versions[route_pattern].append(version)
self.route_versions[route_pattern].sort(reverse = True)  # 按版本号降序排列

    def set_default_version(self, version: VersionInfo) -> None:
"""设置默认版本"""
self.default_version = version

    def add_supported_version(self, version: VersionInfo) -> None:
"""添加支持的版本"""
if version not in self.supported_versions:
            self.supported_versions.append(version)
            self.supported_versions.sort(reverse = True)

    def find_best_version(self, route: str, requested_version: Optional[VersionInfo]) -> Optional[VersionInfo]:
"""查找最佳匹配版本"""
# 查找匹配的路由模式
matching_versions = []

for pattern, versions in self.route_versions.items():
            if self._match_route_pattern(route, pattern):
                matching_versions.extend(versions)

if not matching_versions:
            matching_versions = self.supported_versions

if not matching_versions:
            return self.default_version

# 如果没有请求特定版本，返回最新版本
if requested_version is None:
            return matching_versions[0]

# 查找精确匹配
for version in matching_versions:
            if version == requested_version:
                return version

# 查找兼容版本（同主版本号的最新版本）
compatible_versions = [
            v for v in matching_versions
            if v.major == requested_version.major and v > = requested_version
]

if compatible_versions:
            return compatible_versions[0]

# 返回默认版本
return self.default_version

    def _match_route_pattern(self, route: str, pattern: str) -> bool:
"""匹配路由模式"""
# 简单的通配符匹配
pattern = pattern.replace(' * ', '. * ')
return bool(re.match(pattern, route))

class APIVersioningMiddleware(BaseHTTPMiddleware):
    """API 版本管理中间件"""

    def __init__(
self,
app,
strategy: VersionStrategy = VersionStrategy.URL_PATH,
default_version: str = "v1",
supported_versions: Optional[List[str]] = None,
version_header: str = "X - API - Version",
accept_header_pattern: str = r"application / vnd\.api\ + json;version = (\d + )",
query_param: str = "version",
strict_mode: bool = False,
    ):
super().__init__(app)
self.strategy = strategy
self.version_header = version_header
self.accept_header_pattern = accept_header_pattern
self.query_param = query_param
self.strict_mode = strict_mode

# 初始化版本匹配器
self.matcher = VersionMatcher()

# 设置默认版本
default_version_info = VersionInfo.from_string(default_version)
self.matcher.set_default_version(default_version_info)

# 添加支持的版本
if supported_versions:
            for version_str in supported_versions:
                version_info = VersionInfo.from_string(version_str)
                self.matcher.add_supported_version(version_info)
else:
            # 默认支持 v1
            self.matcher.add_supported_version(default_version_info)

    async def dispatch(self, request: Request, call_next) -> Response:
"""处理请求"""
try:
            # 提取版本信息
            requested_version = self._extract_version(request)

            # 获取原始路径（移除版本信息）
            original_path = self._get_original_path(request)

            # 查找最佳匹配版本
            best_version = self.matcher.find_best_version(original_path, requested_version)

            if best_version is None:
                return self._create_error_response(
                    "No supported API version found",
                    400
                )

            # 检查版本是否被弃用
            if best_version.is_deprecated:
                logger.warning(
                    "Using deprecated API version",
                    version = str(best_version),
                    path = original_path,
                    deprecation_date = best_version.deprecation_date,
                    sunset_date = best_version.sunset_date,
                )

            # 更新请求信息
            self._update_request(request, best_version, original_path)

            # 调用下一个中间件
            response = await call_next(request)

            # 添加版本信息到响应头
            self._add_version_headers(response, best_version, requested_version)

            return response

except Exception as e:
            logger.error("API versioning middleware error", error = str(e))
            return self._create_error_response(
                "Internal server error in API versioning",
                500
            )

    def _extract_version(self, request: Request) -> Optional[VersionInfo]:
"""提取请求的版本信息"""
try:
            if self.strategy == VersionStrategy.URL_PATH:
                return self._extract_version_from_path(request)
            elif self.strategy == VersionStrategy.QUERY_PARAM:
                return self._extract_version_from_query(request)
            elif self.strategy == VersionStrategy.HEADER:
                return self._extract_version_from_accept_header(request)
            elif self.strategy == VersionStrategy.CUSTOM_HEADER:
                return self._extract_version_from_custom_header(request)
            elif self.strategy == VersionStrategy.SUBDOMAIN:
                return self._extract_version_from_subdomain(request)

except Exception as e:
            logger.warning("Failed to extract version", error = str(e))

return None

    def _extract_version_from_path(self, request: Request) -> Optional[VersionInfo]:
"""从 URL 路径提取版本"""
path = request.url.path
match = re.match(r'^ / v(\d + )(?:\.(\d + ))?(?:\.(\d + ))? / ', path)

if match:
            major = int(match.group(1))
            minor = int(match.group(2)) if match.group(2) else 0
            patch = int(match.group(3)) if match.group(3) else 0

            return VersionInfo(
                version = f"v{major}.{minor}.{patch}",
                major = major,
                minor = minor,
                patch = patch,
            )

return None

    def _extract_version_from_query(self, request: Request) -> Optional[VersionInfo]:
"""从查询参数提取版本"""
version_str = request.query_params.get(self.query_param)
if version_str:
            return VersionInfo.from_string(version_str)
return None

    def _extract_version_from_accept_header(self, request: Request) -> Optional[VersionInfo]:
"""从 Accept 头部提取版本"""
accept_header = request.headers.get("accept", "")
match = re.search(self.accept_header_pattern, accept_header)

if match:
            version_str = match.group(1)
            return VersionInfo.from_string(f"v{version_str}")

return None

    def _extract_version_from_custom_header(self, request: Request) -> Optional[VersionInfo]:
"""从自定义头部提取版本"""
version_str = request.headers.get(self.version_header)
if version_str:
            return VersionInfo.from_string(version_str)
return None

    def _extract_version_from_subdomain(self, request: Request) -> Optional[VersionInfo]:
"""从子域名提取版本"""
host = request.headers.get("host", "")
match = re.match(r'^v(\d + )(?:\.(\d + ))?(?:\.(\d + ))?\.', host)

if match:
            major = int(match.group(1))
            minor = int(match.group(2)) if match.group(2) else 0
            patch = int(match.group(3)) if match.group(3) else 0

            return VersionInfo(
                version = f"v{major}.{minor}.{patch}",
                major = major,
                minor = minor,
                patch = patch,
            )

return None

    def _get_original_path(self, request: Request) -> str:
"""获取移除版本信息后的原始路径"""
path = request.url.path

if self.strategy == VersionStrategy.URL_PATH:
            # 移除路径中的版本信息
            path = re.sub(r'^ / v\d + (?:\.\d + )?(?:\.\d + )?', '', path)
            if not path.startswith(' / '):
                path = ' / ' + path

return path

    def _update_request(self, request: Request, version: VersionInfo, original_path: str) -> None:
"""更新请求信息"""
# 添加版本信息到请求状态
request.state.api_version = version
request.state.original_path = original_path

# 如果使用 URL 路径策略，更新路径
if self.strategy == VersionStrategy.URL_PATH:
            # 创建新的 URL
            new_url = request.url.replace(path = original_path)
            request._url = new_url

    def _add_version_headers(
self,
response: Response,
used_version: VersionInfo,
requested_version: Optional[VersionInfo]
    ) -> None:
"""添加版本信息到响应头"""
response.headers["X - API - Version"] = str(used_version)

if requested_version and requested_version ! = used_version:
            response.headers["X - API - Version - Requested"] = str(requested_version)

# 添加支持的版本列表
supported_versions = [str(v) for v in self.matcher.supported_versions]
response.headers["X - API - Versions - Supported"] = ",".join(supported_versions)

# 添加弃用警告
if used_version.is_deprecated:
            warning_msg = f"API version {used_version} is deprecated"
            if used_version.sunset_date:
                warning_msg += f" and will be removed on {used_version.sunset_date}"
            response.headers["Warning"] = f'299 - "{warning_msg}"'

    def _create_error_response(self, message: str, status_code: int) -> JSONResponse:
"""创建错误响应"""
return JSONResponse(
            status_code = status_code,
            content = {
                "error": "API_VERSION_ERROR",
                "message": message,
                "supported_versions": [str(v) for v in self.matcher.supported_versions],
            }
)

    def add_route_version(self, route_pattern: str, version: str) -> None:
"""添加路由版本映射"""
version_info = VersionInfo.from_string(version)
self.matcher.add_route_version(route_pattern, version_info)

    def deprecate_version(
self,
version: str,
deprecation_date: Optional[str] = None,
sunset_date: Optional[str] = None
    ) -> None:
"""标记版本为已弃用"""
for supported_version in self.matcher.supported_versions:
            if str(supported_version) == version:
                supported_version.is_deprecated = True
                supported_version.deprecation_date = deprecation_date
                supported_version.sunset_date = sunset_date
                break

def create_versioning_middleware(
    strategy: VersionStrategy = VersionStrategy.URL_PATH,
    default_version: str = "v1",
    supported_versions: Optional[List[str]] = None,
    **kwargs
) -> APIVersioningMiddleware:
    """创建 API 版本管理中间件"""

    if supported_versions is None:
supported_versions = ["v1", "v2"]

    def middleware_factory(app):
"""TODO: 添加文档字符串"""
return APIVersioningMiddleware(
            app,
            strategy = strategy,
            default_version = default_version,
            supported_versions = supported_versions,
            **kwargs
)

    return middleware_factory