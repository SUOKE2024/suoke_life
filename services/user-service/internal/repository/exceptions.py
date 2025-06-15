"""
用户存储层异常类定义
"""

class RepositoryError(Exception):
    """仓库基础异常类"""
    pass

class UserError(RepositoryError):
    """用户相关错误基类"""
    pass

class UserNotFoundError(UserError):
    """用户不存在错误"""
    pass

class UserAlreadyExistsError(UserError):
    """用户已存在错误"""
    pass

class DeviceError(RepositoryError):
    """设备相关错误基类"""
    pass

class DeviceNotFoundError(DeviceError):
    """设备不存在错误"""
    pass

class DeviceAlreadyBoundError(DeviceError):
    """设备已绑定错误"""
    pass

class DatabaseError(RepositoryError):
    """数据库错误"""
    pass 