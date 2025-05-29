#!/usr/bin/env python3

"""
模型单元测试
"""

from datetime import datetime
from pathlib import Path
import sys
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from internal.model.knowledge import KnowledgeNode
from internal.model.maze import Maze
from internal.model.progress import UserProgress
from internal.model.template import MazeTemplate


class TestModels(unittest.TestCase):
    """模型测试类"""

    def test_maze_model(self):
        """测试迷宫模型"""
        now = datetime.now()

        # 创建测试数据
        maze_data = {
            "maze_id": "test_maze_1",
            "user_id": "user123",
            "maze_type": "四季养生",
            "size_x": 5,
            "size_y": 5,
            "cells": [
                {"x": 0, "y": 0, "type": "START", "cell_id": "0,0"},
                {"x": 1, "y": 0, "type": "PATH", "cell_id": "1,0"}
            ],
            "start_position": {"x": 0, "y": 0},
            "goal_position": {"x": 4, "y": 4},
            "knowledge_nodes": [
                {"node_id": "k1", "title": "测试知识点"}
            ],
            "challenges": [
                {"challenge_id": "c1", "title": "测试挑战"}
            ],
            "created_at": now,
            "difficulty": 3,
            "status": "可用",
            "is_public": True,
            "description": "测试迷宫",
            "tags": ["测试", "养生"]
        }

        # 创建模型实例
        maze = Maze.from_dict(maze_data)

        # 验证属性
        self.assertEqual(maze.maze_id, "test_maze_1")
        self.assertEqual(maze.user_id, "user123")
        self.assertEqual(maze.maze_type, "四季养生")
        self.assertEqual(maze.size_x, 5)
        self.assertEqual(maze.size_y, 5)
        self.assertEqual(len(maze.cells), 2)
        self.assertEqual(maze.start_position["x"], 0)
        self.assertEqual(maze.goal_position["x"], 4)
        self.assertEqual(len(maze.knowledge_nodes), 1)
        self.assertEqual(len(maze.challenges), 1)
        self.assertEqual(maze.created_at, now)
        self.assertEqual(maze.difficulty, 3)
        self.assertEqual(maze.status, "可用")
        self.assertTrue(maze.is_public)
        self.assertEqual(maze.description, "测试迷宫")
        self.assertEqual(maze.tags, ["测试", "养生"])

        # 测试to_dict方法
        maze_dict = maze.to_dict()
        self.assertEqual(maze_dict["maze_id"], "test_maze_1")
        self.assertEqual(maze_dict["user_id"], "user123")
        self.assertEqual(maze_dict["size_x"], 5)
        self.assertEqual(maze_dict["is_public"], True)
        self.assertEqual(maze_dict["tags"], ["测试", "养生"])

    def test_knowledge_node_model(self):
        """测试知识节点模型"""
        # 创建测试数据
        node_data = {
            "node_id": "k1",
            "title": "春季养生",
            "content": "春季养生内容...",
            "category": "四季养生",
            "difficulty_level": "2",
            "related_tags": ["春季", "养生"]
        }

        # 创建模型实例
        node = KnowledgeNode(**node_data)

        # 验证属性
        self.assertEqual(node.node_id, "k1")
        self.assertEqual(node.title, "春季养生")
        self.assertEqual(node.content, "春季养生内容...")
        self.assertEqual(node.category, "四季养生")
        self.assertEqual(node.difficulty_level, "2")
        self.assertEqual(node.related_tags, ["春季", "养生"])

        # 测试to_dict方法
        node_dict = node.to_dict()
        self.assertEqual(node_dict["node_id"], "k1")
        self.assertEqual(node_dict["title"], "春季养生")
        self.assertEqual(node_dict["related_tags"], ["春季", "养生"])

    def test_user_progress_model(self):
        """测试用户进度模型"""
        now = datetime.now()

        # 创建测试数据
        progress_data = {
            "user_id": "user123",
            "maze_id": "maze123",
            "current_position": {"x": 2, "y": 3},
            "visited_cells": ["0,0", "1,0", "2,0", "2,1", "2,2", "2,3"],
            "completed_challenges": ["c1"],
            "acquired_knowledge": ["k1", "k2"],
            "status": "进行中",
            "steps_taken": 12,
            "start_time": now,
            "last_active_time": now,
            "score": 150
        }

        # 创建模型实例
        progress = UserProgress.from_dict(progress_data)

        # 验证属性
        self.assertEqual(progress.user_id, "user123")
        self.assertEqual(progress.maze_id, "maze123")
        self.assertEqual(progress.current_position["x"], 2)
        self.assertEqual(progress.current_position["y"], 3)
        self.assertEqual(len(progress.visited_cells), 6)
        self.assertEqual(len(progress.completed_challenges), 1)
        self.assertEqual(len(progress.acquired_knowledge), 2)
        self.assertEqual(progress.status, "进行中")
        self.assertEqual(progress.steps_taken, 12)
        self.assertEqual(progress.start_time, now)
        self.assertEqual(progress.last_active_time, now)
        self.assertEqual(progress.score, 150)

        # 测试to_dict方法
        progress_dict = progress.to_dict()
        self.assertEqual(progress_dict["user_id"], "user123")
        self.assertEqual(progress_dict["maze_id"], "maze123")
        self.assertEqual(progress_dict["steps_taken"], 12)
        self.assertEqual(progress_dict["completed_challenges"], ["c1"])

    def test_maze_template_model(self):
        """测试迷宫模板模型"""
        # 创建测试数据
        template_data = {
            "template_id": "t1",
            "name": "春季养生迷宫",
            "description": "这是一个春季养生主题的迷宫模板",
            "maze_type": "四季养生",
            "difficulty": 2,
            "size_x": 10,
            "size_y": 10,
            "cells": [
                {"x": 0, "y": 0, "type": "START", "cell_id": "0,0"},
                {"x": 9, "y": 9, "type": "GOAL", "cell_id": "9,9"}
            ],
            "start_position": {"x": 0, "y": 0},
            "goal_position": {"x": 9, "y": 9},
            "knowledge_node_count": 5,
            "challenge_count": 3,
            "tags": ["春季", "养生", "初级"],
            "preview_image_url": "http://example.com/preview.png"
        }

        # 创建模型实例
        template = MazeTemplate.from_dict(template_data)

        # 验证属性
        self.assertEqual(template.template_id, "t1")
        self.assertEqual(template.name, "春季养生迷宫")
        self.assertEqual(template.description, "这是一个春季养生主题的迷宫模板")
        self.assertEqual(template.maze_type, "四季养生")
        self.assertEqual(template.difficulty, 2)
        self.assertEqual(template.size_x, 10)
        self.assertEqual(template.size_y, 10)
        self.assertEqual(len(template.cells), 2)
        self.assertEqual(template.start_position["x"], 0)
        self.assertEqual(template.goal_position["y"], 9)
        self.assertEqual(template.knowledge_node_count, 5)
        self.assertEqual(template.challenge_count, 3)
        self.assertEqual(template.tags, ["春季", "养生", "初级"])
        self.assertEqual(template.preview_image_url, "http://example.com/preview.png")

        # 测试to_dict方法
        template_dict = template.to_dict()
        self.assertEqual(template_dict["template_id"], "t1")
        self.assertEqual(template_dict["name"], "春季养生迷宫")
        self.assertEqual(template_dict["knowledge_node_count"], 5)
        self.assertEqual(template_dict["tags"], ["春季", "养生", "初级"])


if __name__ == "__main__":
    unittest.main()
