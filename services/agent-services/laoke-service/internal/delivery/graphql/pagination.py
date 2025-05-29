#!/usr/bin/env python

"""
老克智能体服务 - GraphQL分页类型与辅助函数
提供标准的游标分页和边缘连接类型
"""

import base64
import json
from typing import Any, Generic, TypeVar

import strawberry

# 泛型类型变量
T = TypeVar('T')

@strawberry.type
class PageInfo:
    """分页信息类型"""
    has_next_page: bool
    has_previous_page: bool
    start_cursor: str | None = None
    end_cursor: str | None = None

@strawberry.type
class Edge(Generic[T]):
    """边缘类型，包含节点和游标"""
    node: T
    cursor: str

@strawberry.type
class Connection(Generic[T]):
    """连接类型，包含边缘列表和分页信息"""
    edges: list[Edge[T]]
    page_info: PageInfo
    total_count: int

# 辅助函数

def encode_cursor(node_id: str, offset: int) -> str:
    """
    编码游标，使用Base64编码

    Args:
        node_id: 节点ID
        offset: 偏移量

    Returns:
        str: 编码后的游标
    """
    cursor_data = {"id": node_id, "offset": offset}
    json_str = json.dumps(cursor_data)
    return base64.b64encode(json_str.encode()).decode()

def decode_cursor(cursor: str) -> dict[str, Any]:
    """
    解码游标

    Args:
        cursor: 游标字符串

    Returns:
        Dict[str, Any]: 解码后的游标数据，包含id和offset
    """
    try:
        json_str = base64.b64decode(cursor.encode()).decode()
        return json.loads(json_str)
    except Exception:
        return {"id": "", "offset": 0}

def get_pagination_values(
    first: int | None = None,
    after: str | None = None,
    last: int | None = None,
    before: str | None = None,
    default_size: int = 10
) -> tuple[int, int, str, bool]:
    """
    获取分页参数值

    Args:
        first: 向前获取的数量
        after: 之后的游标
        last: 向后获取的数量
        before: 之前的游标
        default_size: 默认分页大小

    Returns:
        Tuple[int, int, str, bool]: (limit, offset, cursor, is_backward)
    """
    # 设置默认值
    limit = default_size
    offset = 0
    cursor = None
    is_backward = False

    # 如果提供了after，解析游标并设置偏移量
    if after:
        cursor_data = decode_cursor(after)
        offset = cursor_data.get("offset", 0) + 1
        cursor = after

    # 如果提供了before，处理backward分页
    if before:
        cursor_data = decode_cursor(before)
        offset = max(0, cursor_data.get("offset", 0) - (last or default_size))
        limit = last or default_size
        cursor = before
        is_backward = True

    # 优先使用first/last设置limit
    if first is not None:
        limit = first
    elif last is not None:
        limit = last
        is_backward = True

    return limit, offset, cursor, is_backward

def create_connection(
    items: list[dict[str, Any]],
    total_count: int,
    limit: int,
    offset: int,
    has_more: bool,
    id_field: str = "id",
    node_type: Any = None
) -> dict[str, Any]:
    """
    创建连接对象

    Args:
        items: 项目列表
        total_count: 总数
        limit: 限制
        offset: 偏移量
        has_more: 是否有更多
        id_field: ID字段名
        node_type: 节点类型（用于类型转换）

    Returns:
        Dict[str, Any]: 连接对象
    """
    edges = []

    # 为每个项目创建边缘
    for i, item in enumerate(items):
        # 获取节点ID
        node_id = str(item.get(id_field, f"item-{i}"))
        # 创建游标
        cursor = encode_cursor(node_id, offset + i)

        # 如果提供了节点类型，转换节点
        node = item
        if node_type:
            node = node_type(**item)

        # 添加边缘
        edges.append({"node": node, "cursor": cursor})

    # 创建分页信息
    page_info = {
        "has_next_page": has_more,
        "has_previous_page": offset > 0,
        "start_cursor": edges[0]["cursor"] if edges else None,
        "end_cursor": edges[-1]["cursor"] if edges else None
    }

    # 返回连接对象
    return {
        "edges": edges,
        "page_info": page_info,
        "total_count": total_count
    }
