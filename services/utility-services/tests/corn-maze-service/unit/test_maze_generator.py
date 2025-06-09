from typing import Dict, List, Any, Optional, Union

"""
test_maze_generator - 索克生活项目模块
"""

from internal.maze.generator import MazeGenerator
import pytest
import unittest

#! / usr / bin / env python3

"""
迷宫生成器单元测试
"""





class TestMazeGenerator(unittest.TestCase):
    """测试迷宫生成器"""

    def setUp(self) - > None:
        """测试前准备"""
        self.generator = MazeGenerator()
        self.user_id = "test - user - 123"

    @pytest.mark.asyncio
    async def test_generate_maze_health_path(self) - > None:
        """测试生成健康路径迷宫"""
        maze = await self.generator.generate_maze(
            self.user_id,
            "health_path",
            10, 10, 3
        )

        # 验证迷宫基本属性
        self.assertEqual(maze.user_id, self.user_id)
        self.assertEqual(maze.maze_type, "health_path")
        self.assertEqual(maze.size_x, 10)
        self.assertEqual(maze.size_y, 10)
        self.assertEqual(maze.difficulty, 3)
        self.assertEqual(maze.status, "ACTIVE")

        # 验证单元格数量
        self.assertEqual(len(maze.cells), 10)
        self.assertEqual(len(maze.cells[0]), 10)

        # 验证知识节点和挑战
        self.assertGreaterEqual(len(maze.knowledge_nodes), 3)
        self.assertGreaterEqual(len(maze.challenges), 2)

    @pytest.mark.asyncio
    async def test_generate_maze_nutrition_garden(self) - > None:
        """测试生成营养花园迷宫"""
        maze = await self.generator.generate_maze(
            self.user_id,
            "nutrition_garden",
            8, 8, 2
        )

        # 验证迷宫基本属性
        self.assertEqual(maze.user_id, self.user_id)
        self.assertEqual(maze.maze_type, "nutrition_garden")
        self.assertEqual(maze.size_x, 8)
        self.assertEqual(maze.size_y, 8)
        self.assertEqual(maze.difficulty, 2)

        # 验证知识节点和挑战
        self.assertGreaterEqual(len(maze.knowledge_nodes), 3)
        self.assertGreaterEqual(len(maze.challenges), 2)

        # 验证描述包含营养花园
        self.assertIn("营养花园", maze.description)

    @pytest.mark.asyncio
    async def test_generate_maze_tcm_journey(self) - > None:
        """测试生成中医之旅迷宫"""
        maze = await self.generator.generate_maze(
            self.user_id,
            "tcm_journey",
            12, 12, 4
        )

        # 验证迷宫基本属性
        self.assertEqual(maze.user_id, self.user_id)
        self.assertEqual(maze.maze_type, "tcm_journey")
        self.assertEqual(maze.size_x, 12)
        self.assertEqual(maze.size_y, 12)
        self.assertEqual(maze.difficulty, 4)

        # 验证知识节点和挑战
        self.assertGreaterEqual(len(maze.knowledge_nodes), 6)
        self.assertGreaterEqual(len(maze.challenges), 3)

        # 验证描述包含中医之旅
        self.assertIn("中医之旅", maze.description)

    @pytest.mark.asyncio
    async def test_generate_maze_balanced_life(self) - > None:
        """测试生成平衡生活迷宫"""
        maze = await self.generator.generate_maze(
            self.user_id,
            "balanced_life",
            15, 15, 5
        )

        # 验证迷宫基本属性
        self.assertEqual(maze.user_id, self.user_id)
        self.assertEqual(maze.maze_type, "balanced_life")
        self.assertEqual(maze.size_x, 15)
        self.assertEqual(maze.size_y, 15)
        self.assertEqual(maze.difficulty, 5)

        # 验证知识节点和挑战
        self.assertGreaterEqual(len(maze.knowledge_nodes), 8)
        self.assertGreaterEqual(len(maze.challenges), 4)

        # 验证描述包含平衡生活
        self.assertIn("平衡生活", maze.description)

    @pytest.mark.asyncio
    async def test_invalid_maze_type(self) - > None:
        """测试无效的迷宫类型"""
        with self.assertRaises(ValueError):
            await self.generator.generate_maze(
                self.user_id,
                "invalid_type",
                10, 10, 3
            )

    @pytest.mark.asyncio
    async def test_maze_path_connectivity(self) - > None:
        """测试迷宫路径连通性"""
        maze = await self.generator.generate_maze(
            self.user_id,
            "health_path",
            8, 8, 3
        )

        # 测试路径是否可以从起点到达终点
        visited = [[False for _ in range(maze.size_x)] for _ in range(maze.size_y)]

        # DFS搜索路径
        stack = [(0, 0)]  # 起点
        visited[0][0] = True

        while stack:
            x, y = stack.pop()

            # 如果到达终点，测试通过
            if x == maze.size_x - 1 and y == maze.size_y - 1:
                break

            # 检查四个方向
            # 北
            if not maze.cells[y][x]["walls"]["north"] and y > 0 and not visited[y - 1][x]:
                stack.append((x, y - 1))
                visited[y - 1][x] = True
            # 东
            if not maze.cells[y][x]["walls"]["east"] and x < maze.size_x - 1 and not visited[y][x + 1]:
                stack.append((x + 1, y))
                visited[y][x + 1] = True
            # 南
            if not maze.cells[y][x]["walls"]["south"] and y < maze.size_y - 1 and not visited[y + 1][x]:
                stack.append((x, y + 1))
                visited[y + 1][x] = True
            # 西
            if not maze.cells[y][x]["walls"]["west"] and x > 0 and not visited[y][x - 1]:
                stack.append((x - 1, y))
                visited[y][x - 1] = True

        # 检查是否访问了终点
        self.assertTrue(visited[maze.size_y - 1][maze.size_x - 1], "无法从起点到达终点")

    @pytest.mark.asyncio
    async def test_knowledge_nodes_positions(self) - > None:
        """测试知识节点位置的有效性"""
        maze = await self.generator.generate_maze(
            self.user_id,
            "tcm_journey",
            10, 10, 3
        )

        for node in maze.knowledge_nodes:
            # 检查位置是否在迷宫范围内
            self.assertGreaterEqual(node.position["x"], 0)
            self.assertLess(node.position["x"], maze.size_x)
            self.assertGreaterEqual(node.position["y"], 0)
            self.assertLess(node.position["y"], maze.size_y)

    @pytest.mark.asyncio
    async def test_challenge_positions(self) - > None:
        """测试挑战位置的有效性"""
        maze = await self.generator.generate_maze(
            self.user_id,
            "nutrition_garden",
            10, 10, 3
        )

        for challenge in maze.challenges:
            # 检查位置是否在迷宫范围内
            self.assertGreaterEqual(challenge.position["x"], 0)
            self.assertLess(challenge.position["x"], maze.size_x)
            self.assertGreaterEqual(challenge.position["y"], 0)
            self.assertLess(challenge.position["y"], maze.size_y)

    @pytest.mark.asyncio
    async def test_difficulty_affects_maze_structure(self) - > None:
        """测试难度如何影响迷宫结构"""
        # 生成不同难度的迷宫
        easy_maze = await self.generator.generate_maze(
            self.user_id,
            "health_path",
            10, 10, 1
        )

        hard_maze = await self.generator.generate_maze(
            self.user_id,
            "health_path",
            10, 10, 5
        )

        # 计算每个迷宫的开放通道数量
        def count_open_walls(maze):
            """TODO: 添加文档字符串"""
            count = 0
            for y in range(maze.size_y):
                for x in range(maze.size_x):
                    for direction in ["north", "east", "south", "west"]:
                        if not maze.cells[y][x]["walls"][direction]:
                            count + = 1
            return count

        easy_count = count_open_walls(easy_maze)
        hard_count = count_open_walls(hard_maze)

        # 难度低的迷宫应该有更多的通道
        self.assertGreater(easy_count, hard_count)

if __name__ == "__main__":
    unittest.main()
