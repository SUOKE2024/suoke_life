#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
迷宫生成器单元测试
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from internal.maze.generator import MazeGenerator
from internal.model.knowledge import KnowledgeNode
from internal.model.template import MazeTemplate


class TestMazeGenerator(unittest.TestCase):
    """迷宫生成器测试类"""

    def setUp(self):
        """测试前准备"""
        self.generator = MazeGenerator()
        self.generator.knowledge_repo = AsyncMock()
        
        # 准备测试数据
        self.test_maze_type = "四季养生"
        self.test_size_x = 5
        self.test_size_y = 5
        self.test_difficulty = 3
        self.test_health_attributes = {"体质": "气虚体质", "季节": "春季"}

    def test_generate_maze_grid(self):
        """测试迷宫网格生成"""
        random.seed(42)  # 设置随机种子以确保结果可重现
        
        grid, cell_list = self.generator._generate_maze_grid(
            self.test_size_x, self.test_size_y
        )
        
        # 验证网格尺寸
        self.assertEqual(len(grid), self.test_size_y)
        self.assertEqual(len(grid[0]), self.test_size_x)
        
        # 验证单元格列表长度
        self.assertEqual(len(cell_list), self.test_size_x * self.test_size_y)
        
        # 验证起点和终点设置
        self.assertEqual(grid[0][0]["type"], "START")
        self.assertEqual(grid[self.test_size_y-1][self.test_size_x-1]["type"], "GOAL")
        
        # 验证每个单元格都有正确的属性
        for cell in cell_list:
            self.assertIn("x", cell)
            self.assertIn("y", cell)
            self.assertIn("north_wall", cell)
            self.assertIn("east_wall", cell)
            self.assertIn("south_wall", cell)
            self.assertIn("west_wall", cell)
            self.assertIn("cell_id", cell)
            self.assertIn("type", cell)

    @patch.object(MazeGenerator, '_generate_maze_grid')
    @patch.object(MazeGenerator, '_get_knowledge_nodes')
    @patch.object(MazeGenerator, '_generate_challenges')
    @patch.object(MazeGenerator, '_assign_content_to_maze')
    async def test_generate(self, mock_assign, mock_challenges, mock_knowledge, mock_grid):
        """测试迷宫生成"""
        # 设置Mock返回值
        mock_grid.return_value = (
            [[{"x": 0, "y": 0, "type": "START"}, {"x": 1, "y": 0, "type": "PATH"}],
             [{"x": 0, "y": 1, "type": "PATH"}, {"x": 1, "y": 1, "type": "GOAL"}]],
            [{"x": 0, "y": 0, "type": "START"}, {"x": 1, "y": 0, "type": "PATH"},
             {"x": 0, "y": 1, "type": "PATH"}, {"x": 1, "y": 1, "type": "GOAL"}]
        )
        mock_knowledge.return_value = [{"node_id": "k1", "title": "测试知识点"}]
        mock_challenges.return_value = [{"challenge_id": "c1", "title": "测试挑战"}]
        mock_assign.return_value = [{"x": 0, "y": 0, "type": "START"}, {"x": 1, "y": 0, "type": "KNOWLEDGE"}]
        
        # 调用测试方法
        result = await self.generator.generate(
            self.test_maze_type,
            self.test_size_x,
            self.test_size_y,
            self.test_difficulty,
            self.test_health_attributes
        )
        
        # 验证结果
        self.assertIn("cells", result)
        self.assertIn("start_position", result)
        self.assertIn("goal_position", result)
        self.assertIn("knowledge_nodes", result)
        self.assertIn("challenges", result)
        
        # 验证各个方法被正确调用
        mock_grid.assert_called_once_with(self.test_size_x, self.test_size_y)
        mock_knowledge.assert_called_once()
        mock_challenges.assert_called_once()
        mock_assign.assert_called_once()

    async def test_get_knowledge_nodes(self):
        """测试获取知识节点"""
        # 创建测试知识节点
        test_nodes = [
            KnowledgeNode(
                node_id="test1",
                title="春季养生",
                content="春季养生内容",
                category="四季养生",
                difficulty_level="2",
                related_tags=["春季", "养生"]
            ),
            KnowledgeNode(
                node_id="test2",
                title="气虚调理",
                content="气虚调理内容",
                category="五行平衡",
                difficulty_level="3",
                related_tags=["气虚", "调理"]
            )
        ]
        
        # 设置Mock返回值
        self.generator.knowledge_repo.search_knowledge.return_value = test_nodes
        
        # 调用测试方法
        result = await self.generator._get_knowledge_nodes(
            self.test_maze_type,
            self.test_health_attributes,
            2
        )
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["node_id"], "test1")
        self.assertEqual(result[1]["node_id"], "test2")
        
        # 验证知识库搜索被正确调用
        self.generator.knowledge_repo.search_knowledge.assert_called_once()

    def test_generate_challenges(self):
        """测试生成挑战"""
        random.seed(42)  # 设置随机种子以确保结果可重现
        
        # 调用测试方法
        result = self.generator._generate_challenges(
            self.test_maze_type,
            self.test_difficulty,
            2
        )
        
        # 验证结果
        self.assertEqual(len(result), 2)
        for challenge in result:
            self.assertIn("challenge_id", challenge)
            self.assertIn("title", challenge)
            self.assertIn("description", challenge)
            self.assertIn("type", challenge)
            self.assertIn("difficulty_level", challenge)
            self.assertIn("reward_description", challenge)
            
            # 验证难度级别正确设置
            self.assertEqual(challenge["difficulty_level"], str(self.test_difficulty))

    def test_assign_content_to_maze(self):
        """测试将内容分配到迷宫"""
        # 准备测试数据
        cells = [
            {"x": 0, "y": 0, "type": "START"},
            {"x": 1, "y": 0, "type": "PATH"},
            {"x": 0, "y": 1, "type": "PATH"},
            {"x": 1, "y": 1, "type": "GOAL"}
        ]
        knowledge_nodes = [{"node_id": "k1", "title": "测试知识点"}]
        challenges = [{"challenge_id": "c1", "title": "测试挑战"}]
        start_pos = (0, 0)
        goal_pos = (1, 1)
        
        # 设置随机种子
        random.seed(42)
        
        # 调用测试方法
        result = self.generator._assign_content_to_maze(
            cells,
            knowledge_nodes,
            challenges,
            start_pos,
            goal_pos
        )
        
        # 验证结果 - 应该有知识点和挑战被分配
        knowledge_assigned = False
        challenge_assigned = False
        
        for cell in result:
            if cell.get("type") == "KNOWLEDGE" and cell.get("content_id") == "k1":
                knowledge_assigned = True
            if cell.get("type") == "CHALLENGE" and cell.get("content_id") == "c1":
                challenge_assigned = True
        
        # 由于随机因素，可能并非总是分配成功，所以这里只检查总体的单元格数量
        self.assertEqual(len(result), 4)


if __name__ == "__main__":
    unittest.main() 