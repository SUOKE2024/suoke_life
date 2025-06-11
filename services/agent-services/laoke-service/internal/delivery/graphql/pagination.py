"""
GraphQL分页支持模块
提供Connection和Edge类型用于GraphQL分页查询
"""

from typing import TypeVar, Generic, List, Optional
import strawberry

T = TypeVar('T')

class PageInfo:
    def __init__(self, has_next_page: bool, has_previous_page: bool, start_cursor=None, end_cursor=None):
        self.has_next_page = has_next_page
        self.has_previous_page = has_previous_page
        self.start_cursor = start_cursor
        self.end_cursor = end_cursor

class Edge(Generic[T]):
    def __init__(self, node: T, cursor: str):
        self.node = node
        self.cursor = cursor

class Connection(Generic[T]):
    def __init__(self, edges: List[Edge[T]], page_info: PageInfo, total_count=None):
        self.edges = edges
        self.page_info = page_info
        self.total_count = total_count

@strawberry.type
class PageInfo:
    """分页信息"""
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None

@strawberry.type
class Edge(Generic[T]):
    """边缘类型，包含节点和游标"""
    node: T
    cursor: str

@strawberry.type  
class Connection(Generic[T]):
    """连接类型，用于分页查询结果"""
    edges: List[Edge[T]]
    page_info: PageInfo
    total_count: Optional[int] = None 