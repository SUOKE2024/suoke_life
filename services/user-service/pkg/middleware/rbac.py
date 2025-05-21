"""
基于角色的访问控制中间件
"""
import logging
from enum import Enum
from functools import wraps
from typing import Callable, Dict, List, Optional, Set, Union, Any

from fastapi import HTTPException, Request, Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from pydantic import BaseModel

# 日志记录器
logger = logging.getLogger(__name__)


class Role(str, Enum):
    """用户角色"""
    ADMIN = "admin"
    USER = "user"
    HEALTH_PROVIDER = "health_provider"
    RESEARCHER = "researcher"
    AGENT = "agent"


class Permission(str, Enum):
    """权限类型"""
    # 用户权限
    READ_USER_PROFILE = "read:user_profile"
    UPDATE_USER_PROFILE = "update:user_profile"
    DELETE_USER_PROFILE = "delete:user_profile"
    READ_USERS = "read:users"
    CREATE_USER = "create:user"
    
    # 健康数据权限
    READ_HEALTH_DATA = "read:health_data"
    WRITE_HEALTH_DATA = "write:health_data"
    DELETE_HEALTH_DATA = "delete:health_data"
    MANAGE_HEALTH_DATA = "manage:health_data"
    
    # 系统权限
    READ_SYSTEM_METRICS = "read:system_metrics"
    WRITE_SYSTEM_CONFIG = "write:system_config"
    ADMIN_ACCESS = "admin:access"


# 角色-权限映射表
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.READ_USER_PROFILE,
        Permission.UPDATE_USER_PROFILE,
        Permission.DELETE_USER_PROFILE,
        Permission.READ_USERS,
        Permission.CREATE_USER,
        Permission.READ_HEALTH_DATA,
        Permission.WRITE_HEALTH_DATA,
        Permission.DELETE_HEALTH_DATA,
        Permission.MANAGE_HEALTH_DATA,
        Permission.READ_SYSTEM_METRICS,
        Permission.WRITE_SYSTEM_CONFIG,
        Permission.ADMIN_ACCESS,
    },
    Role.USER: {
        Permission.READ_USER_PROFILE,
        Permission.UPDATE_USER_PROFILE,
        Permission.READ_HEALTH_DATA,
        Permission.WRITE_HEALTH_DATA,
    },
    Role.HEALTH_PROVIDER: {
        Permission.READ_USER_PROFILE,
        Permission.READ_HEALTH_DATA,
        Permission.WRITE_HEALTH_DATA,
        Permission.MANAGE_HEALTH_DATA,
    },
    Role.RESEARCHER: {
        Permission.READ_HEALTH_DATA,
        Permission.READ_SYSTEM_METRICS,
    },
    Role.AGENT: {
        Permission.READ_USER_PROFILE,
        Permission.READ_HEALTH_DATA,
        Permission.WRITE_HEALTH_DATA,
    },
}


# JWT配置
JWT_SECRET_KEY = "unsecure_key_for_dev_only_change_in_production"  # 在生产环境中应通过配置文件或环境变量设置
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={perm.value: perm.value for perm in Permission}
)


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据"""
    sub: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    scopes: List[str] = []
    exp: Optional[int] = None


async def get_current_user_scopes(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> TokenData:
    """
    获取当前用户的作用域和权限
    
    Args:
        security_scopes: 安全作用域
        token: JWT令牌
        
    Returns:
        TokenData: 令牌数据
        
    Raises:
        HTTPException: 如果令牌无效或权限不足
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=401,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # 解码令牌
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
            
        # 获取角色和权限
        roles = payload.get("roles", [])
        permissions = payload.get("permissions", [])
        token_scopes = payload.get("scopes", [])
        
        token_data = TokenData(
            sub=sub,
            roles=roles,
            permissions=permissions,
            scopes=token_scopes,
            exp=payload.get("exp")
        )
    except JWTError:
        logger.error("JWT解码失败", exc_info=True)
        raise credentials_exception
        
    # 验证作用域
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=403,
                detail=f"权限不足: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
            
    return token_data


def has_permission(permission: Permission) -> Callable:
    """
    权限检查装饰器
    
    Args:
        permission: 所需权限
        
    Returns:
        装饰后的处理函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
                    
            if not request:
                for _, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
                        
            if not request:
                raise ValueError("Request对象未在函数参数中找到")
                
            # 获取令牌
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=401,
                    detail="需要认证",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            try:
                # 解析令牌
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    raise HTTPException(
                        status_code=401,
                        detail="认证类型无效",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                    
                # 解码令牌
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                
                # 检查权限
                token_permissions = payload.get("permissions", [])
                if permission.value not in token_permissions:
                    roles = payload.get("roles", [])
                    has_perm_through_role = False
                    
                    # 检查角色隐含的权限
                    for role_name in roles:
                        try:
                            role = Role(role_name)
                            if permission in ROLE_PERMISSIONS.get(role, set()):
                                has_perm_through_role = True
                                break
                        except ValueError:
                            # 忽略无效的角色名称
                            pass
                            
                    if not has_perm_through_role:
                        logger.warning(
                            f"权限拒绝: 用户 {payload.get('sub')} 请求 {permission.value}",
                            extra={
                                "user_id": payload.get("sub"),
                                "permission": permission.value,
                                "roles": roles,
                                "permissions": token_permissions
                            }
                        )
                        raise HTTPException(
                            status_code=403,
                            detail=f"权限不足: {permission.value}",
                        )
                
            except (JWTError, ValueError):
                logger.error("令牌验证失败", exc_info=True)
                raise HTTPException(
                    status_code=401,
                    detail="无效的认证凭据",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def has_role(role: Role) -> Callable:
    """
    角色检查装饰器
    
    Args:
        role: 所需角色
        
    Returns:
        装饰后的处理函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
                    
            if not request:
                for _, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
                        
            if not request:
                raise ValueError("Request对象未在函数参数中找到")
                
            # 获取令牌
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=401,
                    detail="需要认证",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            try:
                # 解析令牌
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    raise HTTPException(
                        status_code=401,
                        detail="认证类型无效",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                    
                # 解码令牌
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                
                # 检查角色
                roles = payload.get("roles", [])
                if role.value not in roles:
                    logger.warning(
                        f"角色拒绝: 用户 {payload.get('sub')} 需要角色 {role.value}",
                        extra={
                            "user_id": payload.get("sub"),
                            "required_role": role.value,
                            "user_roles": roles
                        }
                    )
                    raise HTTPException(
                        status_code=403,
                        detail=f"角色不足: 需要 {role.value}",
                    )
                
            except (JWTError, ValueError):
                logger.error("令牌验证失败", exc_info=True)
                raise HTTPException(
                    status_code=401,
                    detail="无效的认证凭据",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class RBACMiddleware:
    """
    基于角色的访问控制中间件
    允许基于路径和HTTP方法配置访问控制规则
    """
    
    def __init__(self, exclude_paths: Optional[List[str]] = None):
        """
        初始化RBAC中间件
        
        Args:
            exclude_paths: 排除的路径列表（不检查认证）
        """
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        self.url_role_map: Dict[str, Dict[str, Union[Role, List[Role]]]] = {}
        self.url_permission_map: Dict[str, Dict[str, Union[Permission, List[Permission]]]] = {}
        
    def configure_role_access(self, url_pattern: str, method: str, role: Union[Role, List[Role]]):
        """
        配置基于角色的URL访问规则
        
        Args:
            url_pattern: URL模式
            method: HTTP方法（GET, POST, PUT, DELETE等）
            role: 所需角色或角色列表
        """
        if url_pattern not in self.url_role_map:
            self.url_role_map[url_pattern] = {}
            
        self.url_role_map[url_pattern][method.upper()] = role
        
    def configure_permission_access(self, url_pattern: str, method: str, permission: Union[Permission, List[Permission]]):
        """
        配置基于权限的URL访问规则
        
        Args:
            url_pattern: URL模式
            method: HTTP方法
            permission: 所需权限或权限列表
        """
        if url_pattern not in self.url_permission_map:
            self.url_permission_map[url_pattern] = {}
            
        self.url_permission_map[url_pattern][method.upper()] = permission
        
    def _is_path_excluded(self, path: str) -> bool:
        """
        检查路径是否在排除列表中
        
        Args:
            path: 请求路径
            
        Returns:
            bool: 是否排除
        """
        return any(path.startswith(excluded) for excluded in self.exclude_paths)
        
    def _match_url_pattern(self, path: str, patterns: Dict[str, Any]) -> Optional[str]:
        """
        匹配URL模式
        
        Args:
            path: 请求路径
            patterns: URL模式字典
            
        Returns:
            Optional[str]: 匹配的模式或None
        """
        # 精确匹配
        if path in patterns:
            return path
            
        # 前缀匹配
        for pattern in patterns:
            if pattern.endswith('*') and path.startswith(pattern[:-1]):
                return pattern
                
        return None
        
    async def __call__(self, request: Request, call_next):
        """
        处理请求并进行访问控制
        
        Args:
            request: FastAPI请求对象
            call_next: 下一个中间件或路由处理函数
            
        Returns:
            响应对象
        """
        path = request.url.path
        method = request.method
        
        # 跳过排除的路径
        if self._is_path_excluded(path):
            return await call_next(request)
            
        # 获取认证头
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="需要认证",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        try:
            # 解析令牌
            token_type, token = auth_header.split()
            if token_type.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="认证类型无效",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            # 解码令牌
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_roles = payload.get("roles", [])
            user_permissions = payload.get("permissions", [])
            
            # 检查是否需要角色访问控制
            matched_role_pattern = self._match_url_pattern(path, self.url_role_map)
            if matched_role_pattern:
                method_roles = self.url_role_map[matched_role_pattern].get(method.upper())
                if method_roles:
                    required_roles = [method_roles] if isinstance(method_roles, Role) else method_roles
                    if not any(role.value in user_roles for role in required_roles):
                        logger.warning(
                            f"角色访问拒绝: 用户 {payload.get('sub')} 访问 {path} [{method}]",
                            extra={
                                "user_id": payload.get("sub"),
                                "path": path,
                                "method": method,
                                "required_roles": [r.value for r in required_roles],
                                "user_roles": user_roles
                            }
                        )
                        raise HTTPException(
                            status_code=403,
                            detail="权限不足",
                        )
                
            # 检查是否需要权限访问控制
            matched_permission_pattern = self._match_url_pattern(path, self.url_permission_map)
            if matched_permission_pattern:
                method_permissions = self.url_permission_map[matched_permission_pattern].get(method.upper())
                if method_permissions:
                    required_permissions = [method_permissions] if isinstance(method_permissions, Permission) else method_permissions
                    
                    # 检查直接权限
                    direct_permission_check = any(perm.value in user_permissions for perm in required_permissions)
                    
                    # 如果没有直接权限，检查通过角色获得的权限
                    role_permission_check = False
                    if not direct_permission_check:
                        for role_name in user_roles:
                            try:
                                role = Role(role_name)
                                role_perms = ROLE_PERMISSIONS.get(role, set())
                                if any(perm in role_perms for perm in required_permissions):
                                    role_permission_check = True
                                    break
                            except ValueError:
                                # 忽略无效的角色名称
                                pass
                                
                    if not (direct_permission_check or role_permission_check):
                        logger.warning(
                            f"权限访问拒绝: 用户 {payload.get('sub')} 访问 {path} [{method}]",
                            extra={
                                "user_id": payload.get("sub"),
                                "path": path,
                                "method": method,
                                "required_permissions": [p.value for p in required_permissions],
                                "user_permissions": user_permissions,
                                "user_roles": user_roles
                            }
                        )
                        raise HTTPException(
                            status_code=403,
                            detail="权限不足",
                        )
            
        except (JWTError, ValueError):
            logger.error("令牌验证失败", exc_info=True)
            raise HTTPException(
                status_code=401,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # 继续处理请求
        return await call_next(request) 