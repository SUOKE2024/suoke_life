#!/usr/bin/env python3

"""
用户进度服务

管理用户在迷宫中的进度和状态
"""

from datetime import datetime
import logging
import time
from typing import Any
import uuid

from corn_maze_service.internal.model.maze import Maze
from corn_maze_service.pkg.utils.cache import CacheManager
from internal.model.progress import UserProgress
from internal.repository.maze_repository import MazeRepository
from internal.repository.progress_repository import ProgressRepository

logger = logging.getLogger(__name__)

class ProgressService:
    """用户进度服务"""

    # 方向常量
    DIRECTION_NORTH = 0
    DIRECTION_EAST = 1
    DIRECTION_SOUTH = 2
    DIRECTION_WEST = 3

    # 奖励计算常量
    BASE_POINTS = 100
    DIFFICULTY_BONUS_MULTIPLIER = 20
    KNOWLEDGE_BONUS_PER_NODE = 10
    CHALLENGE_BONUS_PER_CHALLENGE = 15
    MAX_TIME_PENALTY = 50
    TIME_PENALTY_DIVISOR = 60  # 每分钟的惩罚

    # 奖励阈值常量
    KNOWLEDGE_DISCOVERY_THRESHOLD = 5
    BONUS_DIFFICULTY_THRESHOLD = 4  # 高难度奖励阈值
    BONUS_KNOWLEDGE_THRESHOLD = 5   # 知识发现奖励阈值

    def __init__(self, cache_manager: CacheManager | None = None):
        self.progress_repo = ProgressRepository()
        self.maze_repo = MazeRepository()
        self.cache_manager = cache_manager or CacheManager()
        self._user_sessions: dict[str, dict[str, Any]] = {}
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
        logger.info(f"用户 {user_id} 在迷宫 {maze_id} 中向方向 {direction} 移动")

        # 获取迷宫
        maze = await self.maze_repo.get_maze(maze_id)
        if not maze:
            return self._create_move_result(False, {"x": 0, "y": 0}, f"迷宫 {maze_id} 不存在")

        # 获取或创建用户进度
        progress = await self._get_or_create_progress(user_id, maze_id, maze)

        # 验证移动
        move_validation = self._validate_move(progress, maze, direction)
        if not move_validation["valid"]:
            return move_validation["result"]

        # 执行移动
        new_position = move_validation["new_position"]
        await self._execute_move(progress, maze, new_position)

        # 检查事件
        event_info = self._check_events(progress, maze, new_position)

        # 保存进度
        await self.progress_repo.save_progress(progress)

        return self._create_move_result(
            True,
            new_position,
            event_info["message"],
            event_info["event_type"],
            event_info["event_id"]
        )

    def _create_move_result(
        self,
        success: bool,
        position: dict[str, int],
        message: str,
        event_type: str = "NONE",
        event_id: str = ""
    ) -> dict[str, Any]:
        """创建移动结果"""
        result = {
            "success": success,
            "position": position,
            "message": message
        }
        if success:
            result.update({
                "event_type": event_type,
                "event_id": event_id
            })
        return result

    async def _get_or_create_progress(self, user_id: str, maze_id: str, maze: Maze) -> UserProgress:
        """获取或创建用户进度"""
        progress = await self.progress_repo.get_progress(user_id, maze_id)
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                maze_id=maze_id,
                current_position=maze.start_position,
                visited_cells=[f"{maze.start_position['x']},{maze.start_position['y']}"],
                status="IN_PROGRESS",
                start_time=datetime.now(),
                completion_percentage=0,
                steps_taken=0,
                acquired_knowledge=[],
                completed_challenges=[]
            )
        return progress

    def _validate_move(self, progress: UserProgress, maze: Maze, direction: int) -> dict[str, Any]:
        """验证移动是否有效"""
        current_x = progress.current_position["x"]
        current_y = progress.current_position["y"]

        # 计算新位置
        new_position = self._calculate_new_position(current_x, current_y, direction)
        if not new_position:
            return {
                "valid": False,
                "result": self._create_move_result(False, {"x": current_x, "y": current_y}, "无效的移动方向")
            }

        new_x, new_y = new_position["x"], new_position["y"]

        # 检查边界
        if not self._is_within_bounds(new_x, new_y, maze):
            return {
                "valid": False,
                "result": self._create_move_result(False, {"x": current_x, "y": current_y}, "无法移动到迷宫边界外")
            }

        # 检查墙壁
        wall_check = self._check_wall_blocking(maze, current_x, current_y, direction)
        if wall_check:
            return {
                "valid": False,
                "result": self._create_move_result(False, {"x": current_x, "y": current_y}, wall_check)
            }

        return {
            "valid": True,
            "new_position": new_position
        }

    def _calculate_new_position(self, current_x: int, current_y: int, direction: int) -> dict[str, int] | None:
        """计算新位置"""
        direction_map = {
            self.DIRECTION_NORTH: (0, -1),
            self.DIRECTION_EAST: (1, 0),
            self.DIRECTION_SOUTH: (0, 1),
            self.DIRECTION_WEST: (-1, 0)
        }

        if direction not in direction_map:
            return None

        dx, dy = direction_map[direction]
        return {"x": current_x + dx, "y": current_y + dy}

    def _is_within_bounds(self, x: int, y: int, maze: Maze) -> bool:
        """检查位置是否在迷宫边界内"""
        return 0 <= x < maze.size_x and 0 <= y < maze.size_y

    def _check_wall_blocking(self, maze: Maze, current_x: int, current_y: int, direction: int) -> str | None:
        """检查是否有墙阻挡移动"""
        current_cell = maze.cells[current_y][current_x]

        wall_checks = {
            self.DIRECTION_NORTH: ("north_wall", "北面有墙, 无法移动"),
            self.DIRECTION_EAST: ("east_wall", "东面有墙, 无法移动"),
            self.DIRECTION_SOUTH: ("south_wall", "南面有墙, 无法移动"),
            self.DIRECTION_WEST: ("west_wall", "西面有墙, 无法移动")
        }

        if direction in wall_checks:
            wall_attr, message = wall_checks[direction]
            if current_cell.get(wall_attr, True):
                return message

        return None

    async def _execute_move(self, progress: UserProgress, maze: Maze, new_position: dict[str, int]) -> None:
        """执行移动操作"""
        # 更新用户位置
        progress.current_position = new_position

        # 记录访问的单元格
        cell_key = f"{new_position['x']},{new_position['y']}"
        if cell_key not in progress.visited_cells:
            progress.visited_cells.append(cell_key)

        # 更新步数和活动时间
        progress.steps_taken += 1
        progress.last_active_time = datetime.now()

        # 计算完成百分比
        total_cells = maze.size_x * maze.size_y
        visited_cells_count = len(progress.visited_cells)
        progress.completion_percentage = min(100, int((visited_cells_count / total_cells) * 100))

    def _check_events(self, progress: UserProgress, maze: Maze, new_position: dict[str, int]) -> dict[str, Any]:
        """检查是否触发事件"""
        new_x, new_y = new_position["x"], new_position["y"]
        target_cell = maze.cells[new_y][new_x]

        # 检查是否到达目标
        if new_x == maze.goal_position["x"] and new_y == maze.goal_position["y"]:
            progress.status = "COMPLETED"
            progress.completion_percentage = 100
            return {
                "event_type": "GOAL",
                "event_id": "",
                "message": "恭喜, 你到达了迷宫的终点!"
            }

        # 检查知识节点
        if target_cell.get("type") == "KNOWLEDGE" and target_cell.get("content_id"):
            event_id = target_cell["content_id"]
            if event_id not in progress.acquired_knowledge:
                progress.acquired_knowledge.append(event_id)
            return {
                "event_type": "KNOWLEDGE",
                "event_id": event_id,
                "message": "你发现了一个中医养生知识点!"
            }

        # 检查挑战
        if target_cell.get("type") == "CHALLENGE" and target_cell.get("content_id"):
            return {
                "event_type": "CHALLENGE",
                "event_id": target_cell["content_id"],
                "message": "你遇到了一个养生挑战!"
            }

        return {
            "event_type": "NONE",
            "event_id": "",
            "message": "移动成功"
        }

    async def record_completion(
        self,
        user_id: str,
        maze_id: str,
        _steps_taken: int,
        time_spent_seconds: int,
        knowledge_nodes_discovered: int,
        challenges_completed: int
    ) -> dict[str, Any]:
        """
        记录用户完成迷宫的情况

        Args:
            user_id: 用户ID
            maze_id: 迷宫ID
            _steps_taken: 花费的步数
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
        base_points = self.BASE_POINTS
        difficulty_bonus = maze.difficulty * self.DIFFICULTY_BONUS_MULTIPLIER
        knowledge_bonus = knowledge_nodes_discovered * self.KNOWLEDGE_BONUS_PER_NODE
        challenge_bonus = challenges_completed * self.CHALLENGE_BONUS_PER_CHALLENGE

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

        # 高难度奖励
        if maze.difficulty >= self.BONUS_DIFFICULTY_THRESHOLD:
            rewards.append({
                "reward_id": str(uuid.uuid4()),
                "reward_type": "ACHIEVEMENT",
                "name": "迷宫探索者",
                "description": "成功完成高难度迷宫",
                "value": 1
            })

        # 如果发现了大量知识节点，添加额外奖励
        if knowledge_nodes_discovered >= self.BONUS_KNOWLEDGE_THRESHOLD:
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

    async def start_maze_session(
        self,
        user_id: str,
        maze_id: str,
        maze: Maze
    ) -> UserProgress:
        """开始迷宫会话"""
        session_id = str(uuid.uuid4())

        # 创建用户进度
        progress = UserProgress(
            user_id=user_id,
            maze_id=maze_id,
            session_id=session_id,
            current_position={"x": 0, "y": 0},
            visited_cells=[{"x": 0, "y": 0}],
            status="IN_PROGRESS",
            start_time=time.time(),
            completion_percentage=0,
            knowledge_nodes_discovered=[],
            challenges_completed=[],
            rewards_earned=[]
        )

        # 缓存会话信息
        session_data = {
            "maze": maze,
            "progress": progress,
            "start_time": time.time()
        }

        self._user_sessions[session_id] = session_data
        await self.cache_manager.set(f"session:{session_id}", session_data, ttl=3600)

        logger.info(f"用户 {user_id} 开始迷宫会话: {session_id}")
        return progress

    async def move_player(
        self,
        user_id: str,
        maze_id: str,
        direction: int,
        maze: Maze
    ) -> dict[str, Any]:
        """移动玩家"""
        # 获取当前进度
        progress = await self.get_user_progress(user_id, maze_id)
        if not progress:
            raise ValueError("未找到用户进度")

        # 计算新位置
        new_x, new_y = self._calculate_new_position(
            progress.current_x, progress.current_y, direction
        )

        # 验证移动是否有效
        if not self._is_valid_move(maze, progress.current_x, progress.current_y, new_x, new_y):
            return {
                "success": False,
                "message": "无效的移动",
                "current_position": {"x": progress.current_x, "y": progress.current_y}
            }

        # 更新位置
        progress.current_x = new_x
        progress.current_y = new_y
        progress.steps_taken += 1

        # 添加到访问过的单元格
        if (new_x, new_y) not in progress.visited_cells:
            progress.visited_cells.append((new_x, new_y))

        # 检查是否到达终点
        if new_x == maze.end_x and new_y == maze.end_y:
            progress.is_completed = True
            progress.completion_time = time.time()
            progress.completion_percentage = 100.0

        # 检查单元格事件
        event_type = "NONE"
        event_id = ""
        message = ""

        target_cell = self._get_cell_at_position(maze, new_x, new_y)
        if target_cell and "content_type" in target_cell:
            if target_cell["content_type"] == "knowledge":
                event_type = "KNOWLEDGE"
                event_id = target_cell["content_id"]
                message = "你发现了一个中医养生知识点!"

                # 记录获取的知识
                progress.knowledge_nodes_discovered += 1

            elif target_cell["content_type"] == "challenge":
                event_type = "CHALLENGE"
                event_id = target_cell["content_id"]
                message = "你遇到了一个养生挑战!"

        # 计算完成百分比（基于访问的单元格数量）
        total_cells = maze.size_x * maze.size_y
        progress.completion_percentage = (len(progress.visited_cells) / total_cells) * 100

        # 更新缓存
        await self.cache_manager.set(
            f"progress:{user_id}:{maze_id}",
            progress.to_dict(),
            ttl=3600
        )

        return {
            "success": True,
            "new_position": {"x": new_x, "y": new_y},
            "event_type": event_type,
            "event_id": event_id,
            "message": message,
            "is_completed": progress.is_completed,
            "completion_percentage": progress.completion_percentage
        }

    async def complete_maze(
        self,
        user_id: str,
        maze_id: str,
        time_spent_seconds: int,
        knowledge_nodes_discovered: int,
        maze: Maze
    ) -> dict[str, Any]:
        """完成迷宫"""
        # 获取进度
        progress = await self.get_user_progress(user_id, maze_id)
        if not progress:
            raise ValueError("未找到用户进度")

        # 标记为完成
        progress.is_completed = True
        progress.completion_time = time.time()
        progress.completion_percentage = 100.0

        # 计算奖励
        rewards = await self._calculate_rewards(
            user_id, maze, time_spent_seconds, knowledge_nodes_discovered
        )

        # 更新缓存
        await self.cache_manager.set(
            f"progress:{user_id}:{maze_id}",
            progress.to_dict(),
            ttl=3600
        )

        # 记录完成事件
        completion_event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "MAZE_COMPLETED",
            "timestamp": time.time(),
            "data": {
                "time_spent": time_spent_seconds,
                "knowledge_discovered": knowledge_nodes_discovered,
                "rewards": rewards
            }
        }

        progress.events_triggered.append(completion_event)

        logger.info(f"用户 {user_id} 完成迷宫 {maze_id}, 耗时: {time_spent_seconds}秒")

        return {
            "completed": True,
            "rewards": rewards,
            "completion_time": progress.completion_time,
            "total_time": time_spent_seconds,
            "knowledge_discovered": knowledge_nodes_discovered
        }

    async def _calculate_rewards(
        self,
        _user_id: str,
        maze: Maze,
        _time_spent_seconds: int,
        knowledge_nodes_discovered: int
    ) -> list[dict[str, Any]]:
        """计算奖励"""
        rewards = []

        # 基础完成奖励
        rewards.append({
            "reward_id": str(uuid.uuid4()),
            "type": "completion",
            "name": "迷宫完成奖励",
            "description": "成功完成迷宫的基础奖励",
            "points": 100
        })

        # 高难度奖励
        if maze.difficulty >= self.BONUS_DIFFICULTY_THRESHOLD:
            rewards.append({
                "reward_id": str(uuid.uuid4()),
                "type": "difficulty_bonus",
                "name": "高难度挑战奖励",
                "description": "完成高难度迷宫的额外奖励",
                "points": 50
            })

        # 如果发现了大量知识节点, 添加额外奖励
        if knowledge_nodes_discovered >= self.BONUS_KNOWLEDGE_THRESHOLD:
            rewards.append({
                "reward_id": str(uuid.uuid4()),
                "type": "knowledge_bonus",
                "name": "知识探索奖励",
                "description": "发现大量知识节点的额外奖励",
                "points": 30
            })

        return rewards
