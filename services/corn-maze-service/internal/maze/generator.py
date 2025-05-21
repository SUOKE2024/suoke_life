#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
迷宫生成模块
"""

import logging
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from internal.model.maze import Maze, Cell, KnowledgeNode, Challenge, Position
from pkg.utils.metrics import maze_generation_time

logger = logging.getLogger(__name__)

class MazeGenerator:
    """迷宫生成器，负责生成各种类型的迷宫"""
    
    MAZE_TYPES = ["health_path", "nutrition_garden", "tcm_journey", "balanced_life"]
    
    def __init__(self):
        """初始化迷宫生成器"""
        self.generators = {
            "health_path": self._generate_health_path,
            "nutrition_garden": self._generate_nutrition_garden,
            "tcm_journey": self._generate_tcm_journey,
            "balanced_life": self._generate_balanced_life,
        }
    
    @maze_generation_time
    async def generate_maze(
        self,
        user_id: str,
        maze_type: str,
        size_x: int = 10,
        size_y: int = 10,
        difficulty: int = 1
    ) -> Maze:
        """
        生成迷宫
        
        Args:
            user_id: 用户ID
            maze_type: 迷宫类型
            size_x: 迷宫宽度
            size_y: 迷宫高度
            difficulty: 难度级别(1-5)
            
        Returns:
            Maze: 生成的迷宫对象
            
        Raises:
            ValueError: 如果迷宫类型无效
        """
        if maze_type not in self.MAZE_TYPES:
            raise ValueError(f"无效的迷宫类型: {maze_type}，支持的类型: {', '.join(self.MAZE_TYPES)}")
        
        logger.info(f"为用户 {user_id} 生成迷宫，类型: {maze_type}, 大小: {size_x}x{size_y}, 难度: {difficulty}")
        
        # 调用对应类型的生成函数
        generator = self.generators.get(maze_type)
        
        if not generator:
            logger.error(f"找不到迷宫类型 {maze_type} 的生成器")
            raise ValueError(f"找不到迷宫类型 {maze_type} 的生成器")
        
        try:
            # 传入参数并生成迷宫
            maze = await generator(user_id, size_x, size_y, difficulty)
            logger.info(f"成功生成迷宫 {maze.maze_id}，类型: {maze_type}")
            return maze
        except Exception as e:
            logger.exception(f"生成迷宫时发生错误: {str(e)}")
            raise
    
    async def _generate_base_maze(
        self,
        user_id: str,
        maze_type: str,
        size_x: int,
        size_y: int,
        difficulty: int
    ) -> Maze:
        """
        生成基础迷宫结构
        
        Args:
            user_id: 用户ID
            maze_type: 迷宫类型
            size_x: 迷宫宽度
            size_y: 迷宫高度
            difficulty: 难度级别
            
        Returns:
            Maze: 基础迷宫对象
        """
        # 初始化单元格，所有墙都是关闭的
        cells = [[Cell(walls={"north": True, "east": True, "south": True, "west": True}) for _ in range(size_x)] for _ in range(size_y)]
        
        # 设置起点和终点
        start_position = {"x": 0, "y": 0}
        goal_position = {"x": size_x - 1, "y": size_y - 1}
        
        # 生成迷宫路径（使用深度优先搜索）
        self._generate_paths(cells, size_x, size_y, difficulty)
        
        # 创建迷宫对象
        # 获取迷宫的起点和终点
        start_x, start_y = 0, 0
        goal_x, goal_y = size_x - 1, size_y - 1
        
        # 根据难度确定知识点和挑战的数量
        knowledge_count = max(2, difficulty)
        challenge_count = max(1, difficulty - 1)
        
        # 获取相关的知识节点
        knowledge_nodes = await self._get_knowledge_nodes(maze_type, health_attributes, knowledge_count)
        
        # 生成挑战
        challenges = self._generate_challenges(maze_type, difficulty, challenge_count)
        
        # 在迷宫中分配知识点和挑战
        cells = self._assign_content_to_maze(
            cell_list, 
            knowledge_nodes, 
            challenges, 
            (start_x, start_y), 
            (goal_x, goal_y)
        )
        
        # 构造迷宫数据
        maze_data = {
            "cells": cells,
            "start_position": {"x": start_x, "y": start_y},
            "goal_position": {"x": goal_x, "y": goal_y},
            "knowledge_nodes": knowledge_nodes,
            "challenges": challenges
        }
        
        return maze_data
    
    async def create_from_template(
        self,
        template: MazeTemplate,
        user_id: str,
        health_attributes: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        基于模板创建迷宫
        
        Args:
            template: 迷宫模板
            user_id: 用户ID
            health_attributes: 用户健康属性
            
        Returns:
            Dict: 包含迷宫数据的字典
        """
        logger.info(f"基于模板 {template.template_id} 创建迷宫")
        
        # 获取相关的知识节点
        knowledge_nodes = await self._get_knowledge_nodes(
            template.maze_type, 
            health_attributes, 
            template.knowledge_node_count
        )
        
        # 生成挑战
        challenges = self._generate_challenges(
            template.maze_type, 
            template.difficulty, 
            template.challenge_count
        )
        
        # 在迷宫中分配知识点和挑战
        cells = self._assign_content_to_template(
            template.cells,
            knowledge_nodes,
            challenges,
            template.start_position,
            template.goal_position
        )
        
        # 构造迷宫数据
        maze_data = {
            "cells": cells,
            "start_position": template.start_position,
            "goal_position": template.goal_position,
            "knowledge_nodes": knowledge_nodes,
            "challenges": challenges
        }
        
        return maze_data
    
    def _generate_maze_grid(self, width: int, height: int) -> Tuple[List[List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """
        使用深度优先搜索算法生成迷宫网格
        
        Args:
            width: 迷宫宽度
            height: 迷宫高度
            
        Returns:
            Tuple[List[List[Dict]], List[Dict]]: 迷宫网格和单元格列表
        """
        # 创建一个无向图
        G = nx.grid_2d_graph(width, height)
        
        # 使用最小生成树算法(MST)生成迷宫
        T = nx.minimum_spanning_tree(G)
        
        # 初始化迷宫网格
        # 每个单元格初始时四面都有墙
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                cell = {
                    "x": x,
                    "y": y,
                    "north_wall": True,
                    "east_wall": True,
                    "south_wall": True,
                    "west_wall": True,
                    "cell_id": f"{x},{y}",
                    "type": "PATH"
                }
                row.append(cell)
            grid.append(row)
        
        # 根据最小生成树移除墙壁
        for (x1, y1), (x2, y2) in T.edges():
            # 确定两个单元格的相对位置
            if x1 == x2:  # 垂直相邻
                if y1 < y2:  # 第一个单元格在上
                    grid[y1][x1]["south_wall"] = False
                    grid[y2][x2]["north_wall"] = False
                else:  # 第一个单元格在下
                    grid[y1][x1]["north_wall"] = False
                    grid[y2][x2]["south_wall"] = False
            else:  # 水平相邻
                if x1 < x2:  # 第一个单元格在左
                    grid[y1][x1]["east_wall"] = False
                    grid[y2][x2]["west_wall"] = False
                else:  # 第一个单元格在右
                    grid[y1][x1]["west_wall"] = False
                    grid[y2][x2]["east_wall"] = False
        
        # 设置起点和终点
        grid[0][0]["type"] = "START"
        grid[height-1][width-1]["type"] = "GOAL"
        
        # 将二维网格转换为一维列表
        cell_list = []
        for row in grid:
            for cell in row:
                cell_list.append(cell)
        
        return grid, cell_list
    
    async def _get_knowledge_nodes(
        self,
        maze_type: str,
        health_attributes: Dict[str, str],
        count: int
    ) -> List[Dict[str, Any]]:
        """
        获取与迷宫类型和用户健康属性相关的知识节点
        
        Args:
            maze_type: 迷宫类型
            health_attributes: 用户健康属性
            count: 需要的知识节点数量
            
        Returns:
            List[Dict]: 知识节点列表
        """
        # 构建查询条件
        query_terms = [maze_type]
        
        # 添加健康属性关键词
        for key, value in health_attributes.items():
            if value and len(value) > 0:
                query_terms.append(value)
        
        # 获取知识节点
        nodes = await self.knowledge_repo.search_knowledge(query_terms, count * 2)
        
        # 如果节点不足，获取基础知识节点
        if len(nodes) < count:
            base_nodes = await self.knowledge_repo.get_knowledge_by_category(maze_type, count * 2)
            # 合并并去重
            seen_ids = {node.node_id for node in nodes}
            for node in base_nodes:
                if node.node_id not in seen_ids and len(nodes) < count * 2:
                    nodes.append(node)
                    seen_ids.add(node.node_id)
        
        # 随机选择所需数量的节点
        selected_nodes = random.sample(nodes, min(count, len(nodes)))
        
        # 转换为字典列表
        return [node.to_dict() for node in selected_nodes]
    
    def _generate_challenges(
        self,
        maze_type: str,
        difficulty: int,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        生成迷宫挑战
        
        Args:
            maze_type: 迷宫类型
            difficulty: 难度级别
            count: 需要的挑战数量
            
        Returns:
            List[Dict]: 挑战列表
        """
        challenge_templates = {
            "四季养生": [
                {"title": "春季养生问答", "description": "回答关于春季养生的问题", "type": "选择题"},
                {"title": "夏季食材配对", "description": "将夏季适宜食材与功效配对", "type": "配对题"},
                {"title": "秋季养生顺序", "description": "安排正确的秋季养生活动顺序", "type": "排序题"},
                {"title": "冬季保健知识", "description": "测试你的冬季保健知识", "type": "选择题"}
            ],
            "五行平衡": [
                {"title": "五行对应器官", "description": "将五行与对应的器官进行匹配", "type": "配对题"},
                {"title": "五行相生相克", "description": "判断五行之间的相生相克关系", "type": "选择题"},
                {"title": "五行与情志", "description": "分析五行与情志的关系", "type": "分析题"},
                {"title": "五行调和方案", "description": "为失衡的五行设计调和方案", "type": "创建题"}
            ],
            "经络调理": [
                {"title": "经络走向辨识", "description": "辨识特定经络的走向", "type": "选择题"},
                {"title": "穴位定位挑战", "description": "在人体图上定位重要穴位", "type": "定位题"},
                {"title": "经络功能匹配", "description": "将经络与其主要功能匹配", "type": "配对题"},
                {"title": "经络按摩顺序", "description": "安排正确的经络按摩顺序", "type": "排序题"}
            ]
        }
        
        # 获取当前迷宫类型的挑战模板
        templates = challenge_templates.get(maze_type, challenge_templates["四季养生"])
        
        # 随机选择挑战
        selected_templates = random.sample(templates, min(count, len(templates)))
        
        # 为每个挑战添加难度和奖励信息
        challenges = []
        for template in selected_templates:
            challenge_id = str(uuid.uuid4())
            reward_descriptions = [
                "获得养生积分",
                "解锁新的养生知识",
                "获得经络图鉴",
                "获得体质分析报告"
            ]
            
            challenge = {
                "challenge_id": challenge_id,
                "title": template["title"],
                "description": template["description"],
                "type": template["type"],
                "difficulty_level": str(difficulty),
                "reward_description": random.choice(reward_descriptions)
            }
            challenges.append(challenge)
        
        return challenges
    
    def _assign_content_to_maze(
        self,
        cells: List[Dict[str, Any]],
        knowledge_nodes: List[Dict[str, Any]],
        challenges: List[Dict[str, Any]],
        start_pos: Tuple[int, int],
        goal_pos: Tuple[int, int]
    ) -> List[Dict[str, Any]]:
        """
        将知识点和挑战分配到迷宫单元格中
        
        Args:
            cells: 迷宫单元格列表
            knowledge_nodes: 知识节点列表
            challenges: 挑战列表
            start_pos: 起点位置 (x, y)
            goal_pos: 终点位置 (x, y)
            
        Returns:
            List[Dict]: 更新后的单元格列表
        """
        # 过滤出可以分配内容的单元格（不包括起点和终点）
        available_cells = []
        for cell in cells:
            cell_pos = (cell["x"], cell["y"])
            if cell_pos != start_pos and cell_pos != goal_pos and cell["type"] == "PATH":
                available_cells.append(cell)
        
        # 随机打乱可用单元格顺序
        random.shuffle(available_cells)
        
        # 分配知识节点
        for i, node in enumerate(knowledge_nodes):
            if i < len(available_cells):
                available_cells[i]["type"] = "KNOWLEDGE"
                available_cells[i]["content_id"] = node["node_id"]
        
        # 分配挑战
        for i, challenge in enumerate(challenges):
            idx = i + len(knowledge_nodes)
            if idx < len(available_cells):
                available_cells[idx]["type"] = "CHALLENGE"
                available_cells[idx]["content_id"] = challenge["challenge_id"]
        
        return cells
    
    def _assign_content_to_template(
        self,
        template_cells: List[Dict[str, Any]],
        knowledge_nodes: List[Dict[str, Any]],
        challenges: List[Dict[str, Any]],
        start_pos: Dict[str, int],
        goal_pos: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        将知识点和挑战分配到模板单元格中
        
        Args:
            template_cells: 模板单元格列表
            knowledge_nodes: 知识节点列表
            challenges: 挑战列表
            start_pos: 起点位置 {x, y}
            goal_pos: 终点位置 {x, y}
            
        Returns:
            List[Dict]: 更新后的单元格列表
        """
        # 复制模板单元格列表，避免修改原始数据
        cells = template_cells.copy()
        
        # 找出模板中已标记为知识点和挑战的单元格
        knowledge_cells = []
        challenge_cells = []
        
        for cell in cells:
            cell_pos_x, cell_pos_y = cell["x"], cell["y"]
            if cell_pos_x == start_pos["x"] and cell_pos_y == start_pos["y"]:
                cell["type"] = "START"
            elif cell_pos_x == goal_pos["x"] and cell_pos_y == goal_pos["y"]:
                cell["type"] = "GOAL"
            elif cell.get("type") == "KNOWLEDGE":
                knowledge_cells.append(cell)
            elif cell.get("type") == "CHALLENGE":
                challenge_cells.append(cell)
        
        # 随机打乱单元格列表
        random.shuffle(knowledge_cells)
        random.shuffle(challenge_cells)
        
        # 分配知识节点
        for i, node in enumerate(knowledge_nodes):
            if i < len(knowledge_cells):
                knowledge_cells[i]["content_id"] = node["node_id"]
        
        # 分配挑战
        for i, challenge in enumerate(challenges):
            if i < len(challenge_cells):
                challenge_cells[i]["content_id"] = challenge["challenge_id"]
        
        return cells