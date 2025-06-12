"""
base - 索克生活项目模块
"""

from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

"""基础数据模型"""




class BaseEntity(BaseModel):
"""基础实体模型"""

    model_config = ConfigDict(
from_attributes = True,
validate_assignment = True,
arbitrary_types_allowed = True,
    )

    id: Optional[int] = Field(default = None, description = "主键ID")
    created_at: Optional[datetime] = Field(default = None, description = "创建时间")
    updated_at: Optional[datetime] = Field(default = None, description = "更新时间")


class BaseRequest(BaseModel):
"""基础请求模型"""

    model_config = ConfigDict(
validate_assignment = True,
str_strip_whitespace = True,
    )


class BaseResponse(BaseModel):
"""基础响应模型"""

    model_config = ConfigDict(
from_attributes = True,
    )

    success: bool = Field(default = True, description = "请求是否成功")
    message: str = Field(default = "操作成功", description = "响应消息")
    timestamp: datetime = Field(default_factory = datetime.now, description = "响应时间")


class PaginatedResponse(BaseResponse):
"""分页响应模型"""

    total: int = Field(description = "总记录数")
    page: int = Field(description = "当前页码")
    page_size: int = Field(description = "每页大小")
    total_pages: int = Field(description = "总页数")
    data: list[Any] = Field(description = "数据列表")

    @classmethod
def create(
cls,
data: list[Any],
total: int,
page: int,
page_size: int,
message: str = "查询成功",
    ) -> "PaginatedResponse":
    """创建分页响应"""
total_pages = (total + page_size - 1)//page_size
return cls(
data = data,
total = total,
page = page,
page_size = page_size,
total_pages = total_pages,
message = message,
)


class ErrorResponse(BaseModel):
"""错误响应模型"""

    success: bool = Field(default = False, description = "请求是否成功")
    error: dict[str, Any] = Field(description = "错误信息")
    timestamp: datetime = Field(default_factory = datetime.now, description = "响应时间")
