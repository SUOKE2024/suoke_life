#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
迷宫模板模型定义
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional


@dataclass
class MazeTemplate:
    """迷宫模板模型"""
    
    template_id: str  # 模板ID
    name: str  # 模板名称
    description: str  # 描述
    maze_type: str  # 迷宫类型（四季养生、五行平衡、经络调理等）
    difficulty: int  # 难度级别（1-5）
    preview_image_url: str  # 预览图URL
    size_x: int  # 宽度
    size_y: int  # 高度
    cells: List[Dict[str, Any]]  # 迷宫单元格模板
    start_position: Dict[str, int]  # 起点位置 {x, y}
    goal_position: Dict[str, int]  # 终点位置 {x, y}
    knowledge_node_count: int  # 知识节点数量
    challenge_count: int  # 挑战数量
    created_at: datetime  # 创建时间
    tags: List[str] = field(default_factory=list)  # 标签
    author: str = ""  # 作者
    is_official: bool = False  # 是否官方模板
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "maze_type": self.maze_type,
            "difficulty": self.difficulty,
            "preview_image_url": self.preview_image_url,
            "size_x": self.size_x,
            "size_y": self.size_y,
            "cells": self.cells,
            "start_position": self.start_position,
            "goal_position": self.goal_position,
            "knowledge_node_count": self.knowledge_node_count,
            "challenge_count": self.challenge_count,
            "created_at": self.created_at,
            "tags": self.tags,
            "author": self.author,
            "is_official": self.is_official
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MazeTemplate':
        """从字典创建对象"""
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data["description"],
            maze_type=data["maze_type"],
            difficulty=data["difficulty"],
            preview_image_url=data["preview_image_url"],
            size_x=data["size_x"],
            size_y=data["size_y"],
            cells=data["cells"],
            start_position=data["start_position"],
            goal_position=data["goal_position"],
            knowledge_node_count=data["knowledge_node_count"],
            challenge_count=data["challenge_count"],
            created_at=data["created_at"] if isinstance(data["created_at"], datetime) else datetime.fromisoformat(data["created_at"]),
            tags=data.get("tags", []),
            author=data.get("author", ""),
            is_official=data.get("is_official", False)
        )