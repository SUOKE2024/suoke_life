#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
迷宫数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict, Union

# 类型定义
class Position(TypedDict):
    """位置坐标"""
    x: int
    y: int

class Cell(TypedDict):
    """迷宫单元格"""
    walls: Dict[str, bool]  # 记录四个方向的墙：north, east, south, west
    content: Optional[str]  # 单元格内容，如空、障碍物等

@dataclass
class KnowledgeNode:
    """知识节点"""
    node_id: str
    title: str
    content: str
    type: str  # 知识类型：health_tip, nutrition_fact, tcm_wisdom, etc.
    position: Position
    is_visited: bool
    icon: Optional[str] = None  # 图标路径
    related_links: List[str] = field(default_factory=list)  # 相关知识链接
    media_url: Optional[str] = None  # 媒体内容URL

@dataclass
class Challenge:
    """挑战任务"""
    challenge_id: str
    title: str
    description: str
    type: str  # 挑战类型：quiz, exercise, daily_task, etc.
    difficulty: int  # 难度级别：1-5
    reward_points: int  # 完成奖励点数
    position: Position
    is_completed: bool
    prerequisites: List[str] = field(default_factory=list)  # 前置条件
    time_limit: Optional[int] = None  # 时间限制（秒）
    hint: Optional[str] = None  # 提示

@dataclass
class UserProgress:
    """用户进度"""
    user_id: str
    maze_id: str
    current_position: Position
    visited_nodes: List[str]  # 已访问的知识节点ID
    completed_challenges: List[str]  # 已完成的挑战ID
    start_time: datetime
    last_updated: datetime
    time_spent: int = 0  # 花费的时间（秒）
    steps_taken: int = 0  # 走过的步数
    hints_used: int = 0  # 使用的提示数量

@dataclass
class CompletionReward:
    """完成奖励"""
    experience_points: int
    health_points: int
    knowledge_points: int
    unlocked_content: List[str]
    achievement_id: Optional[str] = None

@dataclass
class Maze:
    """迷宫主数据模型"""
    maze_id: str
    user_id: str
    maze_type: str  # 迷宫类型：health_path, nutrition_garden, tcm_journey, balanced_life
    size_x: int
    size_y: int
    cells: List[List[Cell]]
    start_position: Position
    goal_position: Position
    knowledge_nodes: List[KnowledgeNode]
    challenges: List[Challenge]
    created_at: datetime
    difficulty: int  # 难度级别：1-5
    status: str  # 状态：ACTIVE, COMPLETED, ARCHIVED
    is_public: bool = False  # 是否公开
    description: str = ""  # 迷宫描述
    tags: List[str] = field(default_factory=list)  # 标签
    thumbnail_url: Optional[str] = None  # 缩略图URL
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将迷宫对象转换为字典
        
        Returns:
            Dict: 迷宫字典表示
        """
        return {
            "maze_id": self.maze_id,
            "user_id": self.user_id,
            "maze_type": self.maze_type,
            "size_x": self.size_x,
            "size_y": self.size_y,
            "cells": self.cells,
            "start_position": self.start_position,
            "goal_position": self.goal_position,
            "knowledge_nodes": [
                {
                    "node_id": node.node_id,
                    "title": node.title,
                    "content": node.content,
                    "type": node.type,
                    "position": node.position,
                    "is_visited": node.is_visited,
                    "icon": node.icon,
                    "related_links": node.related_links,
                    "media_url": node.media_url
                }
                for node in self.knowledge_nodes
            ],
            "challenges": [
                {
                    "challenge_id": challenge.challenge_id,
                    "title": challenge.title,
                    "description": challenge.description,
                    "type": challenge.type,
                    "difficulty": challenge.difficulty,
                    "reward_points": challenge.reward_points,
                    "position": challenge.position,
                    "is_completed": challenge.is_completed,
                    "prerequisites": challenge.prerequisites,
                    "time_limit": challenge.time_limit,
                    "hint": challenge.hint
                }
                for challenge in self.challenges
            ],
            "created_at": self.created_at.isoformat(),
            "difficulty": self.difficulty,
            "status": self.status,
            "is_public": self.is_public,
            "description": self.description,
            "tags": self.tags,
            "thumbnail_url": self.thumbnail_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Maze':
        """
        从字典创建迷宫对象
        
        Args:
            data: 迷宫字典数据
            
        Returns:
            Maze: 迷宫对象
        """
        # 处理知识节点
        knowledge_nodes = [
            KnowledgeNode(
                node_id=node["node_id"],
                title=node["title"],
                content=node["content"],
                type=node["type"],
                position=node["position"],
                is_visited=node["is_visited"],
                icon=node.get("icon"),
                related_links=node.get("related_links", []),
                media_url=node.get("media_url")
            )
            for node in data.get("knowledge_nodes", [])
        ]
        
        # 处理挑战
        challenges = [
            Challenge(
                challenge_id=challenge["challenge_id"],
                title=challenge["title"],
                description=challenge["description"],
                type=challenge["type"],
                difficulty=challenge["difficulty"],
                reward_points=challenge["reward_points"],
                position=challenge["position"],
                is_completed=challenge["is_completed"],
                prerequisites=challenge.get("prerequisites", []),
                time_limit=challenge.get("time_limit"),
                hint=challenge.get("hint")
            )
            for challenge in data.get("challenges", [])
        ]
        
        # 处理日期时间
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif not isinstance(created_at, datetime):
            created_at = datetime.now()
        
        # 创建迷宫对象
        return cls(
            maze_id=data["maze_id"],
            user_id=data["user_id"],
            maze_type=data["maze_type"],
            size_x=data["size_x"],
            size_y=data["size_y"],
            cells=data["cells"],
            start_position=data["start_position"],
            goal_position=data["goal_position"],
            knowledge_nodes=knowledge_nodes,
            challenges=challenges,
            created_at=created_at,
            difficulty=data["difficulty"],
            status=data["status"],
            is_public=data.get("is_public", False),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            thumbnail_url=data.get("thumbnail_url")
        )