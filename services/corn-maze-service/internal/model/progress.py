"""
progress - 索克生活项目模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

#!/usr/bin/env python3

"""
用户进度模型定义
"""



@dataclass
class UserProgress:
    """用户在迷宫中的进度模型"""

    user_id: str  # 用户ID
    maze_id: str  # 迷宫ID
    current_position: dict[str, int]  # 当前位置 {x, y}
    visited_cells: list[str]  # 已访问的单元格
    completed_challenges: list[str]  # 已完成的挑战
    acquired_knowledge: list[str]  # 已获取的知识
    completion_percentage: int  # 完成百分比
    status: str  # 状态（进行中、已完成等）
    steps_taken: int  # 已走的步数
    start_time: datetime  # 开始时间
    last_active_time: datetime  # 最后活动时间
    notes: dict[str, Any] = field(default_factory=dict)  # 附加笔记

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "maze_id": self.maze_id,
            "current_position": self.current_position,
            "visited_cells": self.visited_cells,
            "completed_challenges": self.completed_challenges,
            "acquired_knowledge": self.acquired_knowledge,
            "completion_percentage": self.completion_percentage,
            "status": self.status,
            "steps_taken": self.steps_taken,
            "start_time": self.start_time,
            "last_active_time": self.last_active_time,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'UserProgress':
        """从字典创建对象"""
        return cls(
            user_id=data["user_id"],
            maze_id=data["maze_id"],
            current_position=data["current_position"],
            visited_cells=data["visited_cells"],
            completed_challenges=data["completed_challenges"],
            acquired_knowledge=data["acquired_knowledge"],
            completion_percentage=data["completion_percentage"],
            status=data["status"],
            steps_taken=data["steps_taken"],
            start_time=data["start_time"] if isinstance(data["start_time"], datetime) else datetime.fromisoformat(data["start_time"]),
            last_active_time=data["last_active_time"] if isinstance(data["last_active_time"], datetime) else datetime.fromisoformat(data["last_active_time"]),
            notes=data.get("notes", {})
        )
