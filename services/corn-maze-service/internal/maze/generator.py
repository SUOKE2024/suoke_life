#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
迷宫生成模块 - 优化版本
"""

import logging
import random
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from functools import lru_cache

from internal.model.maze import Maze, Cell, KnowledgeNode, Challenge, Position
from pkg.utils.metrics import maze_generation_time, record_maze_generation_error
from pkg.utils.cache import CacheManager

logger = logging.getLogger(__name__)

class MazeGenerator:
    """迷宫生成器，负责生成各种类型的迷宫"""
    
    MAZE_TYPES = ["health_path", "nutrition_garden", "tcm_journey", "balanced_life"]
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """初始化迷宫生成器"""
        self.cache_manager = cache_manager or CacheManager()
        self.generators = {
            "health_path": self._generate_health_path,
            "nutrition_garden": self._generate_nutrition_garden,
            "tcm_journey": self._generate_tcm_journey,
            "balanced_life": self._generate_balanced_life,
        }
        logger.info("迷宫生成器初始化完成")
    
    @maze_generation_time
    async def generate_maze(
        self,
        user_id: str,
        maze_type: str,
        size_x: int = 10,
        size_y: int = 10,
        difficulty: int = 1,
        health_attributes: Optional[Dict[str, str]] = None
    ) -> Maze:
        """
        生成迷宫
        
        Args:
            user_id: 用户ID
            maze_type: 迷宫类型
            size_x: 迷宫宽度
            size_y: 迷宫高度
            difficulty: 难度级别(1-5)
            health_attributes: 用户健康属性
            
        Returns:
            Maze: 生成的迷宫对象
            
        Raises:
            ValueError: 如果迷宫类型无效
        """
        # 参数验证
        if not user_id:
            error_msg = "用户ID不能为空"
            logger.error(error_msg)
            record_maze_generation_error(maze_type, "invalid_user_id")
            raise ValueError(error_msg)
            
        if maze_type not in self.MAZE_TYPES:
            error_msg = f"无效的迷宫类型: {maze_type}，支持的类型: {', '.join(self.MAZE_TYPES)}"
            logger.error(error_msg)
            record_maze_generation_error(maze_type, "invalid_type")
            raise ValueError(error_msg)
        
        if size_x < 3 or size_y < 3:
            error_msg = "迷宫大小不能小于3x3"
            logger.error(error_msg)
            record_maze_generation_error(maze_type, "invalid_size")
            raise ValueError(error_msg)
        
        if difficulty < 1 or difficulty > 5:
            error_msg = "难度级别必须在1-5之间"
            logger.error(error_msg)
            record_maze_generation_error(maze_type, "invalid_difficulty")
            raise ValueError(error_msg)
        
        logger.info(f"为用户 {user_id} 生成迷宫，类型: {maze_type}, 大小: {size_x}x{size_y}, 难度: {difficulty}")
        
        # 检查缓存
        cache_key = f"maze_template:{maze_type}:{size_x}x{size_y}:{difficulty}"
        cached_template = await self.cache_manager.get(cache_key)
        
        try:
            if cached_template:
                logger.info(f"使用缓存的迷宫模板: {cache_key}")
                maze = await self._create_from_template(cached_template, user_id, health_attributes or {})
            else:
                # 调用对应类型的生成函数
                generator = self.generators.get(maze_type)
                if not generator:
                    raise ValueError(f"未找到迷宫类型 {maze_type} 的生成器")
                    
                maze = await generator(user_id, size_x, size_y, difficulty, health_attributes or {})
                
                # 缓存模板（不包含用户特定信息）
                template = self._extract_template(maze)
                await self.cache_manager.set(cache_key, template, ttl=3600)  # 缓存1小时
            
            logger.info(f"成功生成迷宫 {maze.maze_id}，类型: {maze_type}")
            return maze
            
        except Exception as e:
            logger.exception(f"生成迷宫时发生错误: {str(e)}")
            record_maze_generation_error(maze_type, "generation_failed")
            raise
    
    async def _generate_health_path(
        self,
        user_id: str,
        size_x: int,
        size_y: int,
        difficulty: int,
        health_attributes: Dict[str, str]
    ) -> Maze:
        """生成健康路径迷宫"""
        logger.info(f"生成健康路径迷宫，大小: {size_x}x{size_y}")
        
        # 生成基础迷宫结构
        cells = await self._generate_maze_grid(size_x, size_y, difficulty)
        
        # 获取健康相关的知识节点
        knowledge_nodes = await self._get_health_knowledge_nodes(health_attributes, difficulty)
        
        # 生成健康挑战
        challenges = await self._generate_health_challenges(difficulty)
        
        # 创建迷宫对象
        maze = Maze(
            maze_id=str(uuid.uuid4()),
            user_id=user_id,
            maze_type="health_path",
            size_x=size_x,
            size_y=size_y,
            cells=cells,
            start_position={"x": 0, "y": 0},
            goal_position={"x": size_x - 1, "y": size_y - 1},
            knowledge_nodes=knowledge_nodes,
            challenges=challenges,
            created_at=datetime.now(),
            difficulty=difficulty,
            status="ACTIVE",
            description="探索健康生活的智慧路径",
            tags=["健康", "养生", "预防"]
        )
        
        # 在迷宫中分配内容
        await self._assign_content_to_maze(maze)
        
        return maze
    
    async def _generate_nutrition_garden(
        self,
        user_id: str,
        size_x: int,
        size_y: int,
        difficulty: int,
        health_attributes: Dict[str, str]
    ) -> Maze:
        """生成营养花园迷宫"""
        logger.info(f"生成营养花园迷宫，大小: {size_x}x{size_y}")
        
        cells = await self._generate_maze_grid(size_x, size_y, difficulty)
        knowledge_nodes = await self._get_nutrition_knowledge_nodes(health_attributes, difficulty)
        challenges = await self._generate_nutrition_challenges(difficulty)
        
        maze = Maze(
            maze_id=str(uuid.uuid4()),
            user_id=user_id,
            maze_type="nutrition_garden",
            size_x=size_x,
            size_y=size_y,
            cells=cells,
            start_position={"x": 0, "y": 0},
            goal_position={"x": size_x - 1, "y": size_y - 1},
            knowledge_nodes=knowledge_nodes,
            challenges=challenges,
            created_at=datetime.now(),
            difficulty=difficulty,
            status="ACTIVE",
            description="探索营养科学的奥秘花园",
            tags=["营养", "饮食", "健康"]
        )
        
        await self._assign_content_to_maze(maze)
        return maze
    
    async def _generate_tcm_journey(
        self,
        user_id: str,
        size_x: int,
        size_y: int,
        difficulty: int,
        health_attributes: Dict[str, str]
    ) -> Maze:
        """生成中医之旅迷宫"""
        logger.info(f"生成中医之旅迷宫，大小: {size_x}x{size_y}")
        
        cells = await self._generate_maze_grid(size_x, size_y, difficulty)
        knowledge_nodes = await self._get_tcm_knowledge_nodes(health_attributes, difficulty)
        challenges = await self._generate_tcm_challenges(difficulty)
        
        maze = Maze(
            maze_id=str(uuid.uuid4()),
            user_id=user_id,
            maze_type="tcm_journey",
            size_x=size_x,
            size_y=size_y,
            cells=cells,
            start_position={"x": 0, "y": 0},
            goal_position={"x": size_x - 1, "y": size_y - 1},
            knowledge_nodes=knowledge_nodes,
            challenges=challenges,
            created_at=datetime.now(),
            difficulty=difficulty,
            status="ACTIVE",
            description="传统中医智慧的探索之旅",
            tags=["中医", "传统医学", "辨证论治"]
        )
        
        await self._assign_content_to_maze(maze)
        return maze
    
    async def _generate_balanced_life(
        self,
        user_id: str,
        size_x: int,
        size_y: int,
        difficulty: int,
        health_attributes: Dict[str, str]
    ) -> Maze:
        """生成平衡生活迷宫"""
        logger.info(f"生成平衡生活迷宫，大小: {size_x}x{size_y}")
        
        cells = await self._generate_maze_grid(size_x, size_y, difficulty)
        knowledge_nodes = await self._get_balanced_life_knowledge_nodes(health_attributes, difficulty)
        challenges = await self._generate_balanced_life_challenges(difficulty)
        
        maze = Maze(
            maze_id=str(uuid.uuid4()),
            user_id=user_id,
            maze_type="balanced_life",
            size_x=size_x,
            size_y=size_y,
            cells=cells,
            start_position={"x": 0, "y": 0},
            goal_position={"x": size_x - 1, "y": size_y - 1},
            knowledge_nodes=knowledge_nodes,
            challenges=challenges,
            created_at=datetime.now(),
            difficulty=difficulty,
            status="ACTIVE",
            description="寻找生活平衡的智慧之路",
            tags=["平衡", "生活方式", "身心健康"]
        )
        
        await self._assign_content_to_maze(maze)
        return maze
    
    async def _generate_maze_grid(self, width: int, height: int, difficulty: int) -> List[List[Cell]]:
        """
        使用深度优先搜索算法生成迷宫网格
        
        Args:
            width: 迷宫宽度
            height: 迷宫高度
            difficulty: 难度级别，影响迷宫复杂度
            
        Returns:
            List[List[Cell]]: 迷宫单元格网格
        """
        # 初始化所有单元格，所有墙都关闭
        cells = [[{"walls": {"north": True, "east": True, "south": True, "west": True}, "content": None} 
                 for _ in range(width)] for _ in range(height)]
        
        # 使用深度优先搜索生成迷宫
        visited = [[False for _ in range(width)] for _ in range(height)]
        stack = [(0, 0)]
        visited[0][0] = True
        
        directions = [("north", 0, -1), ("east", 1, 0), ("south", 0, 1), ("west", -1, 0)]
        opposite = {"north": "south", "east": "west", "south": "north", "west": "east"}
        
        while stack:
            current_x, current_y = stack[-1]
            
            # 获取未访问的邻居
            neighbors = []
            for direction, dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                    neighbors.append((direction, nx, ny))
            
            if neighbors:
                # 随机选择一个邻居
                direction, nx, ny = random.choice(neighbors)
                
                # 移除当前单元格和邻居之间的墙
                cells[current_y][current_x]["walls"][direction] = False
                cells[ny][nx]["walls"][opposite[direction]] = False
                
                # 标记邻居为已访问并加入栈
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                # 回溯
                stack.pop()
        
        # 根据难度添加额外的路径
        if difficulty > 1:
            extra_paths = difficulty * 2
            for _ in range(extra_paths):
                x, y = random.randint(0, width - 1), random.randint(0, height - 1)
                direction = random.choice(["north", "east", "south", "west"])
                
                dx, dy = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}[direction]
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < width and 0 <= ny < height:
                    cells[y][x]["walls"][direction] = False
                    cells[ny][nx]["walls"][opposite[direction]] = False
        
        return cells
    
    async def _get_health_knowledge_nodes(self, health_attributes: Dict[str, str], difficulty: int) -> List[KnowledgeNode]:
        """获取健康相关的知识节点"""
        base_nodes = [
            {
                "title": "每日饮水量",
                "content": "成年人每天应该饮用1.5-2升水，有助于维持身体正常代谢。",
                "type": "health_tip"
            },
            {
                "title": "适量运动",
                "content": "每周至少150分钟中等强度运动，或75分钟高强度运动。",
                "type": "health_tip"
            },
            {
                "title": "充足睡眠",
                "content": "成年人每晚需要7-9小时的优质睡眠，有助于身体恢复和免疫力提升。",
                "type": "health_tip"
            }
        ]
        
        # 根据难度和健康属性选择节点
        selected_nodes = base_nodes[:min(len(base_nodes), difficulty + 1)]
        
        knowledge_nodes = []
        for i, node_data in enumerate(selected_nodes):
            knowledge_nodes.append(KnowledgeNode(
                node_id=str(uuid.uuid4()),
                title=node_data["title"],
                content=node_data["content"],
                type=node_data["type"],
                position={"x": 0, "y": 0},  # 位置稍后分配
                is_visited=False
            ))
        
        return knowledge_nodes
    
    async def _get_nutrition_knowledge_nodes(self, health_attributes: Dict[str, str], difficulty: int) -> List[KnowledgeNode]:
        """获取营养相关的知识节点"""
        base_nodes = [
            {
                "title": "五色搭配",
                "content": "每餐应包含不同颜色的蔬菜水果，确保营养素的多样性。",
                "type": "nutrition_fact"
            },
            {
                "title": "蛋白质摄入",
                "content": "成年人每公斤体重需要0.8-1.2克蛋白质，可从肉类、豆类、坚果中获取。",
                "type": "nutrition_fact"
            }
        ]
        
        selected_nodes = base_nodes[:min(len(base_nodes), difficulty + 1)]
        
        knowledge_nodes = []
        for node_data in selected_nodes:
            knowledge_nodes.append(KnowledgeNode(
                node_id=str(uuid.uuid4()),
                title=node_data["title"],
                content=node_data["content"],
                type=node_data["type"],
                position={"x": 0, "y": 0},
                is_visited=False
            ))
        
        return knowledge_nodes
    
    async def _get_tcm_knowledge_nodes(self, health_attributes: Dict[str, str], difficulty: int) -> List[KnowledgeNode]:
        """获取中医相关的知识节点"""
        base_nodes = [
            {
                "title": "五行理论",
                "content": "木、火、土、金、水五行相生相克，对应人体五脏六腑的平衡。",
                "type": "tcm_wisdom"
            },
            {
                "title": "经络养生",
                "content": "人体有十二正经和奇经八脉，通过按摩穴位可以调理气血。",
                "type": "tcm_wisdom"
            }
        ]
        
        selected_nodes = base_nodes[:min(len(base_nodes), difficulty + 1)]
        
        knowledge_nodes = []
        for node_data in selected_nodes:
            knowledge_nodes.append(KnowledgeNode(
                node_id=str(uuid.uuid4()),
                title=node_data["title"],
                content=node_data["content"],
                type=node_data["type"],
                position={"x": 0, "y": 0},
                is_visited=False
            ))
        
        return knowledge_nodes
    
    async def _get_balanced_life_knowledge_nodes(self, health_attributes: Dict[str, str], difficulty: int) -> List[KnowledgeNode]:
        """获取平衡生活相关的知识节点"""
        base_nodes = [
            {
                "title": "工作生活平衡",
                "content": "合理安排工作和休息时间，避免过度劳累，保持身心健康。",
                "type": "life_balance"
            },
            {
                "title": "情绪管理",
                "content": "学会识别和管理情绪，通过冥想、运动等方式缓解压力。",
                "type": "life_balance"
            }
        ]
        
        selected_nodes = base_nodes[:min(len(base_nodes), difficulty + 1)]
        
        knowledge_nodes = []
        for node_data in selected_nodes:
            knowledge_nodes.append(KnowledgeNode(
                node_id=str(uuid.uuid4()),
                title=node_data["title"],
                content=node_data["content"],
                type=node_data["type"],
                position={"x": 0, "y": 0},
                is_visited=False
            ))
        
        return knowledge_nodes
    
    async def _generate_health_challenges(self, difficulty: int) -> List[Challenge]:
        """生成健康相关的挑战"""
        base_challenges = [
            {
                "title": "健康知识问答",
                "description": "回答关于健康生活方式的问题",
                "type": "quiz",
                "reward_points": 10
            },
            {
                "title": "运动打卡",
                "description": "完成今日的运动目标",
                "type": "exercise",
                "reward_points": 15
            }
        ]
        
        selected_challenges = base_challenges[:min(len(base_challenges), max(1, difficulty - 1))]
        
        challenges = []
        for challenge_data in selected_challenges:
            challenges.append(Challenge(
                challenge_id=str(uuid.uuid4()),
                title=challenge_data["title"],
                description=challenge_data["description"],
                type=challenge_data["type"],
                difficulty=difficulty,
                reward_points=challenge_data["reward_points"],
                position={"x": 0, "y": 0},
                is_completed=False
            ))
        
        return challenges
    
    async def _generate_nutrition_challenges(self, difficulty: int) -> List[Challenge]:
        """生成营养相关的挑战"""
        base_challenges = [
            {
                "title": "营养搭配",
                "description": "设计一份营养均衡的餐单",
                "type": "nutrition_plan",
                "reward_points": 12
            }
        ]
        
        selected_challenges = base_challenges[:max(1, difficulty - 1)]
        
        challenges = []
        for challenge_data in selected_challenges:
            challenges.append(Challenge(
                challenge_id=str(uuid.uuid4()),
                title=challenge_data["title"],
                description=challenge_data["description"],
                type=challenge_data["type"],
                difficulty=difficulty,
                reward_points=challenge_data["reward_points"],
                position={"x": 0, "y": 0},
                is_completed=False
            ))
        
        return challenges
    
    async def _generate_tcm_challenges(self, difficulty: int) -> List[Challenge]:
        """生成中医相关的挑战"""
        base_challenges = [
            {
                "title": "穴位识别",
                "description": "识别常用的养生穴位",
                "type": "acupoint_quiz",
                "reward_points": 15
            }
        ]
        
        selected_challenges = base_challenges[:max(1, difficulty - 1)]
        
        challenges = []
        for challenge_data in selected_challenges:
            challenges.append(Challenge(
                challenge_id=str(uuid.uuid4()),
                title=challenge_data["title"],
                description=challenge_data["description"],
                type=challenge_data["type"],
                difficulty=difficulty,
                reward_points=challenge_data["reward_points"],
                position={"x": 0, "y": 0},
                is_completed=False
            ))
        
        return challenges
    
    async def _generate_balanced_life_challenges(self, difficulty: int) -> List[Challenge]:
        """生成平衡生活相关的挑战"""
        base_challenges = [
            {
                "title": "冥想练习",
                "description": "完成10分钟的正念冥想",
                "type": "meditation",
                "reward_points": 10
            }
        ]
        
        selected_challenges = base_challenges[:max(1, difficulty - 1)]
        
        challenges = []
        for challenge_data in selected_challenges:
            challenges.append(Challenge(
                challenge_id=str(uuid.uuid4()),
                title=challenge_data["title"],
                description=challenge_data["description"],
                type=challenge_data["type"],
                difficulty=difficulty,
                reward_points=challenge_data["reward_points"],
                position={"x": 0, "y": 0},
                is_completed=False
            ))
        
        return challenges
    
    async def _assign_content_to_maze(self, maze: Maze) -> None:
        """在迷宫中分配知识节点和挑战的位置"""
        # 获取可用位置（排除起点和终点）
        available_positions = []
        for y in range(maze.size_y):
            for x in range(maze.size_x):
                if (x, y) != (maze.start_position["x"], maze.start_position["y"]) and \
                   (x, y) != (maze.goal_position["x"], maze.goal_position["y"]):
                    available_positions.append((x, y))
        
        # 随机分配知识节点位置
        random.shuffle(available_positions)
        
        for i, node in enumerate(maze.knowledge_nodes):
            if i < len(available_positions):
                x, y = available_positions[i]
                node.position = {"x": x, "y": y}
        
        # 分配挑战位置
        challenge_start_idx = len(maze.knowledge_nodes)
        for i, challenge in enumerate(maze.challenges):
            pos_idx = challenge_start_idx + i
            if pos_idx < len(available_positions):
                x, y = available_positions[pos_idx]
                challenge.position = {"x": x, "y": y}
    
    async def _create_from_template(self, template: Dict[str, Any], user_id: str, health_attributes: Dict[str, str]) -> Maze:
        """从缓存的模板创建迷宫"""
        # 创建新的迷宫ID
        maze_id = str(uuid.uuid4())
        
        # 从模板复制数据并设置用户特定信息
        maze_data = template.copy()
        maze_data["maze_id"] = maze_id
        maze_data["user_id"] = user_id
        maze_data["created_at"] = datetime.now()
        
        return Maze.from_dict(maze_data)
    
    def _extract_template(self, maze: Maze) -> Dict[str, Any]:
        """从迷宫中提取模板（移除用户特定信息）"""
        template = maze.to_dict()
        # 移除用户特定信息
        template.pop("maze_id", None)
        template.pop("user_id", None)
        template.pop("created_at", None)
        return template