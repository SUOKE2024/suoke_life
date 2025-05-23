"""
认证服务业务逻辑模块

导入所有服务模块，使其可以通过internal.service命名空间访问
"""
from . import auth_service
from . import user_service
from . import permission_service
from . import role_service
from . import oauth_service 