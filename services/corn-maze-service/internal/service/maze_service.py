#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
迷宫服务 - 负责迷宫的生成和管理
"""

import uuid
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from internal.maze.generator import MazeGenerator
from internal.repository.maze_repository import MazeRepository
from internal.repository.template_repository import TemplateRepository
from internal.model.maze import Maze
from internal.model.template import MazeTemplate

logger = logging.getLogger(__name__)

class MazeService:
    """迷宫服务，负责迷宫的生成和管理"""
    
    def __init__(self):
        self.maze_repo = MazeRepository()
        self.template_repo = TemplateRepository()
        self.generator = MazeGenerator()
        logger.info("迷宫服务初始化完成")
    
    async def create_maze(
        self, 
        user_id: str, 
        maze_type: str, 
        difficulty: int, 
        health_attributes: Dict[str, str],
        use_template: bool = False,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建新迷宫
        
        Args:
            user_id: 用户ID
            maze_type: 迷宫类型（四季养生、五行平衡、经络调理等）
            difficulty: 难度级别（1-5）
            health_attributes: 用户健康属性
            use_template: 是否使用模板
            template_id: 模板ID（如果使用模板）
            
        Returns:
            Dict: 包含迷宫信息的字典
        """
        logger.info(f"为用户 {user_id} 创建 {maze_type} 类型、难度 {difficulty} 的迷宫")
        
        maze_id = str(uuid.uuid4())
        
        # 根据难度确定迷宫大小
        size_mapping = {
            1: (5, 5),
            2: (7, 7),
            3: (10, 10),
            4: (12, 12),
            5: (15, 15)
        }
        size_x, size_y = size_mapping.get(difficulty, (10, 10))
        
        # 使用模板或生成新迷宫
        if use_template and template_id:
            logger.info(f"使用模板 {template_id} 创建迷宫")
            template = await self.template_repo.get_template(template_id)
            if not template:
                raise ValueError(f"未找到ID为 {template_id} 的模板")
            
            # 从模板创建迷宫
            maze_data = await self.generator.create_from_template(
                template=template,
                user_id=user_id,
                health_attributes=health_attributes
            )
        else:
            logger.info(f"生成新迷宫，大小为 {size_x}x{size_y}")
            # 生成新迷宫
            maze_data = await self.generator.generate(
                maze_type=maze_type,
                size_x=size_x,
                size_y=size_y,
                difficulty=difficulty,
                health_attributes=health_attributes
            )
        
        # 创建迷宫对象
        maze = Maze(
            maze_id=maze_id,
            user_id=user_id,
            maze_type=maze_type,
            size_x=size_x,
            size_y=size_y,
            cells=maze_data["cells"],
            start_position=maze_data["start_position"],
            goal_position=maze_data["goal_position"],
            knowledge_nodes=maze_data["knowledge_nodes"],
            challenges=maze_data["challenges"],
            created_at=datetime.now(),
            difficulty=difficulty,
            status="AVAILABLE"
        )
        
        # 保存迷宫
        await self.maze_repo.save_maze(maze)
        
        return maze.to_dict()
    
    async def get_maze(self, maze_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取迷宫信息
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 迷宫信息或None（如果未找到）
        """
        logger.info(f"获取迷宫 {maze_id}")
        
        maze = await self.maze_repo.get_maze(maze_id)
        
        if not maze:
            logger.warning(f"未找到ID为 {maze_id} 的迷宫")
            return None
        
        # 如果迷宫不属于请求的用户，检查是否是公共迷宫
        if maze.user_id != user_id and not maze.is_public:
            logger.warning(f"用户 {user_id} 试图访问不属于他们的迷宫 {maze_id}")
            return None
        
        return maze.to_dict()
    
    async def list_templates(
        self, 
        maze_type: str = "", 
        difficulty: int = 0,
        page: int = 1, 
        page_size: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        列出迷宫模板
        
        Args:
            maze_type: 迷宫类型（可选筛选条件）
            difficulty: 难度级别（可选筛选条件）
            page: 页码
            page_size: 每页数量
            
        Returns:
            Tuple[List[Dict], int]: 模板列表和总数
        """
        logger.info(f"获取迷宫模板列表，类型: {maze_type}, 难度: {difficulty}")
        
        templates, total = await self.template_repo.list_templates(
            maze_type=maze_type,
            difficulty=difficulty,
            page=page,
            page_size=page_size
        )
        
        # 转换为字典列表
        template_dicts = [template.to_dict() for template in templates]
        
        return template_dicts, total
    
    async def delete_maze(self, maze_id: str, user_id: str) -> bool:
        """
        删除迷宫
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID（用于验证权限）
            
        Returns:
            bool: 是否成功删除
        """
        logger.info(f"删除迷宫 {maze_id}")
        
        # 获取迷宫
        maze = await self.maze_repo.get_maze(maze_id)
        
        if not maze:
            logger.warning(f"未找到ID为 {maze_id} 的迷宫")
            return False
        
        # 检查权限
        if maze.user_id != user_id:
            logger.warning(f"用户 {user_id} 试图删除不属于他们的迷宫 {maze_id}")
            return False
        
        # 删除迷宫
        success = await self.maze_repo.delete_maze(maze_id)
        
        return success