#!/usr/bin/env python3

"""
知识节点模型定义
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeNode:
    """中医养生知识节点模型"""

    node_id: str  # 节点ID
    title: str  # 标题
    content: str  # 内容
    category: str  # 类别（四季养生、五行平衡、经络调理等）
    difficulty_level: str  # 难度级别
    related_tags: list[str] = field(default_factory=list)  # 相关标签
    references: list[dict[str, str]] = field(default_factory=list)  # 引用参考资料
    media_links: list[dict[str, str]] = field(default_factory=list)  # 相关媒体链接

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "node_id": self.node_id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "difficulty_level": self.difficulty_level,
            "related_tags": self.related_tags,
            "references": self.references,
            "media_links": self.media_links
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'KnowledgeNode':
        """从字典创建对象"""
        return cls(
            node_id=data["node_id"],
            title=data["title"],
            content=data["content"],
            category=data["category"],
            difficulty_level=data["difficulty_level"],
            related_tags=data.get("related_tags", []),
            references=data.get("references", []),
            media_links=data.get("media_links", [])
        )
