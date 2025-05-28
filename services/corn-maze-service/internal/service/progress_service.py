#!/usr/bin/env python3

"""
进度服务 - 负责跟踪和管理用户在迷宫中的进度
"""

from datetime import datetime
import logging
from typing import Any
import uuid

from internal.model.progress import UserProgress
from internal.repository.maze_repository import MazeRepository
from internal.repository.progress_repository import ProgressRepository

logger = logging.getLogger(__name__)

class ProgressService:
    """用户进度服务，负责管理用户在迷宫中的进度"""

    def __init__(self):
        self.progress_repo = ProgressRepository()
        self.maze_repo = MazeRepository()
        logger.info("进度服务初始化完成")

    async def get_user_progress(self, user_id: str, maze_id: str) -> dict[str, Any] | None:
        """
        获取用户在迷宫中的进度
        
        Args:
            user_id: 用户ID
            maze_id: 迷宫ID
            
        Returns:
            Optional[Dict]: 进度信息或None（如果未找到）
        """
        logger.info(f"获取用户 {user_id} 在迷宫 {maze_id} 中的进度")

        progress = await self.progress_repo.get_progress(user_id, maze_id)

        if not progress:
            logger.warning(f"未找到用户 {user_id} 在迷宫 {maze_id} 中的进度")
            return None

        return progress.to_dict()

    async def move_user(self, maze_id: str, user_id: str, direction: int) -> dict[str, Any]:
        """
        用户在迷宫中移动
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID
            direction: 移动方向（0-3，北东南西）
            
        Returns:
            Dict: 移动结果，包含新位置和事件信息
        """
        # 方向映射
        direction_map = {
            0: (0, -1),  # 北
            1: (1, 0),   # 东
            2: (0, 1),   # 南
            3: (-1, 0)   # 西
        }
        dx, dy = direction_map.get(direction, (0, 0))

        # 获取迷宫和用户进度
        maze = await self.maze_repo.get_maze(maze_id)
        if not maze:
            return {
                "success": False,
                "position": {"x": 0, "y": 0},
                "message": f"迷宫 {maze_id} 不存在"
            }

        # 获取或创建进度
        progress = await self.progress_repo.get_progress(user_id, maze_id)
        if not progress:
            # 如果不存在进度记录，创建一个新的
            progress = UserProgress(
                user_id=user_id,
                maze_id=maze_id,
                current_position=maze.start_position,
                visited_cells=[f"{maze.start_position['x']},{maze.start_position['y']}"],
                completed_challenges=[],
                acquired_knowledge=[],
                completion_percentage=0,
                status="IN_PROGRESS",
                steps_taken=0,
                start_time=datetime.now(),
                last_active_time=datetime.now()
            )

        # 当前位置
        current_x = progress.current_position["x"]
        current_y = progress.current_position["y"]

        # 计算新位置
        new_x = current_x + dx
        new_y = current_y + dy

        # 检查是否可以移动（边界检查）
        if new_x < 0 or new_x >= maze.size_x or new_y < 0 or new_y >= maze.size_y:
            return {
                "success": False,
                "position": {"x": current_x, "y": current_y},
                "message": "无法移动到迷宫边界外"
            }

        # 获取当前单元格和目标单元格
        current_cell = None
        target_cell = None

        for cell in maze.cells:
            if cell["x"] == current_x and cell["y"] == current_y:
                current_cell = cell
            if cell["x"] == new_x and cell["y"] == new_y:
                target_cell = cell

        if not current_cell or not target_cell:
            return {
                "success": False,
                "position": {"x": current_x, "y": current_y},
                "message": "单元格信息获取失败"
            }

        # 检查墙壁
        if direction == 0 and current_cell.get("north_wall", True):  # 北
            return {
                "success": False,
                "position": {"x": current_x, "y": current_y},
                "message": "北面有墙，无法移动"
            }
        elif direction == 1 and current_cell.get("east_wall", True):  # 东
            return {
                "success": False,
                "position": {"x": current_x, "y": current_y},
                "message": "东面有墙，无法移动"
            }
        elif direction == 2 and current_cell.get("south_wall", True):  # 南
            return {
                "success": False,
                "position": {"x": current_x, "y": current_y},
                "message": "南面有墙，无法移动"
            }
        elif direction == 3 and current_cell.get("west_wall", True):  # 西
            return {
                "success": False,
                "position": {"x": current_x, "y": current_y},
                "message": "西面有墙，无法移动"
            }

        # 更新用户位置
        progress.current_position = {"x": new_x, "y": new_y}

        # 记录访问的单元格
        cell_key = f"{new_x},{new_y}"
        if cell_key not in progress.visited_cells:
            progress.visited_cells.append(cell_key)

        # 更新步数和活动时间
        progress.steps_taken += 1
        progress.last_active_time = datetime.now()

        # 检查是否触发事件
        event_type = "NONE"
        event_id = ""
        message = "移动成功"

        # 检查是否到达目标
        if new_x == maze.goal_position["x"] and new_y == maze.goal_position["y"]:
            event_type = "GOAL"
            message = "恭喜，你到达了迷宫的终点！"
            progress.status = "COMPLETED"
            progress.completion_percentage = 100

        # 检查是否触发知识节点
        elif target_cell.get("type") == "KNOWLEDGE" and target_cell.get("content_id"):
            event_type = "KNOWLEDGE"
            event_id = target_cell["content_id"]
            message = "你发现了一个中医养生知识点！"

            # 记录获取的知识
            if event_id not in progress.acquired_knowledge:
                progress.acquired_knowledge.append(event_id)

        # 检查是否触发挑战
        elif target_cell.get("type") == "CHALLENGE" and target_cell.get("content_id"):
            event_type = "CHALLENGE"
            event_id = target_cell["content_id"]
            message = "你遇到了一个养生挑战！"

        # 计算完成百分比（基于访问的单元格数量）
        total_cells = maze.size_x * maze.size_y
        visited_cells_count = len(progress.visited_cells)
        progress.completion_percentage = min(100, int((visited_cells_count / total_cells) * 100))

        # 保存进度
        await self.progress_repo.save_progress(progress)

        return {
            "success": True,
            "position": {"x": new_x, "y": new_y},
            "event_type": event_type,
            "event_id": event_id,
            "message": message
        }

    async def record_completion(
        self,
        user_id: str,
        maze_id: str,
        steps_taken: int,
        time_spent_seconds: int,
        knowledge_nodes_discovered: int,
        challenges_completed: int
    ) -> dict[str, Any]:
        """
        记录用户完成迷宫的情况
        
        Args:
            user_id: 用户ID
            maze_id: 迷宫ID
            steps_taken: 花费的步数
            time_spent_seconds: 花费的时间（秒）
            knowledge_nodes_discovered: 发现的知识节点数量
            challenges_completed: 完成的挑战数量
            
        Returns:
            Dict: 记录结果，包含获得的积分和奖励
        """
        logger.info(f"记录用户 {user_id} 完成迷宫 {maze_id} 的情况")

        # 获取进度
        progress = await self.progress_repo.get_progress(user_id, maze_id)
        if not progress:
            return {
                "success": False,
                "completion_id": "",
                "points_earned": 0,
                "rewards": [],
                "message": f"未找到用户 {user_id} 在迷宫 {maze_id} 中的进度"
            }

        # 获取迷宫
        maze = await self.maze_repo.get_maze(maze_id)
        if not maze:
            return {
                "success": False,
                "completion_id": "",
                "points_earned": 0,
                "rewards": [],
                "message": f"迷宫 {maze_id} 不存在"
            }

        # 更新进度状态
        progress.status = "COMPLETED"
        progress.completion_percentage = 100
        progress.last_active_time = datetime.now()

        # 保存更新的进度
        await self.progress_repo.save_progress(progress)

        # 计算获得的积分
        # 基础分 + 难度加成 + 知识节点加成 + 挑战加成 - 时间惩罚
        base_points = 100
        difficulty_bonus = maze.difficulty * 20
        knowledge_bonus = knowledge_nodes_discovered * 10
        challenge_bonus = challenges_completed * 15

        # 时间惩罚（时间越短越好）
        time_penalty = min(50, int(time_spent_seconds / 60))

        total_points = base_points + difficulty_bonus + knowledge_bonus + challenge_bonus - time_penalty

        # 生成奖励
        rewards = [
            {
                "reward_id": str(uuid.uuid4()),
                "reward_type": "EXPERIENCE",
                "name": "经验值",
                "description": "完成迷宫获得的经验值",
                "value": total_points
            }
        ]

        # 如果是高难度迷宫，添加额外奖励
        if maze.difficulty >= 4:
            rewards.append({
                "reward_id": str(uuid.uuid4()),
                "reward_type": "ACHIEVEMENT",
                "name": "迷宫探索者",
                "description": "成功完成高难度迷宫",
                "value": 1
            })

        # 如果发现了大量知识节点，添加额外奖励
        if knowledge_nodes_discovered >= 5:
            rewards.append({
                "reward_id": str(uuid.uuid4()),
                "reward_type": "BADGE",
                "name": "中医智者",
                "description": "在迷宫中发现多个中医养生知识点",
                "value": 1
            })

        completion_id = str(uuid.uuid4())

        return {
            "success": True,
            "completion_id": completion_id,
            "points_earned": total_points,
            "rewards": rewards,
            "message": "迷宫完成记录已保存"
        }
