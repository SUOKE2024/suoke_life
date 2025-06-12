"""
base - 索克生活项目模块
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from health_data_service.core.logging import log_database_operation

"""基础服务类"""



# 泛型类型变量
T = TypeVar("T")
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")

class BaseService(ABC, Generic[T, CreateT, UpdateT]):
"""基础服务类"""

    def __init__(self) -> None:
    """TODO: 添加文档字符串"""
self.logger_name = self.__class__.__name__

    @abstractmethod
async def create(self, data: CreateT) -> T:
    """创建资源"""
pass

    @abstractmethod
async def get_by_id(self, id: int) -> T | None:
    """根据ID获取资源"""
pass

    @abstractmethod
async def update(self, id: int, data: UpdateT) -> T | None:
    """更新资源"""
pass

    @abstractmethod
async def delete(self, id: int) -> bool:
    """删除资源"""
pass

    @abstractmethod
async def list(
self,
skip: int = 0,
limit: int = 100,
**filters: Any
    ) -> tuple[list[T], int]:
    """获取资源列表"""
pass

    def _log_operation(
self,
operation: str,
table: str,
duration: float,
affected_rows: int | None = None,
**kwargs: Any,
    ) -> None:
    """记录数据库操作日志"""
log_database_operation(
operation = operation,
table = table,
duration = duration,
affected_rows = affected_rows,
service = self.logger_name,
**kwargs,
)
