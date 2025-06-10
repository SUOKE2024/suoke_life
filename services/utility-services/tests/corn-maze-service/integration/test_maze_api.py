from typing import Dict, List, Any, Optional, Union

"""
test_maze_api - 索克生活项目模块
"""

from concurrent import futures
from internal.delivery.grpc.server import setup_grpc_server
from internal.maze.generator import MazeGenerator
from internal.repository.maze_repository import MazeRepository
from internal.service.knowledge_service import KnowledgeService
from internal.service.maze_service import MazeService
from internal.service.progress_service import ProgressService
from pathlib import Path
import grpc
import logging
import os
import pytest
import sys
import unittest
import uuid

#! / usr / bin / env python3

"""
迷宫服务API集成测试
"""



# 添加项目根目录到路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))


logger = logging.getLogger(__name__)

@pytest.mark.integration
class TestMazeAPIIntegration(unittest.TestCase):
    """迷宫服务API集成测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 设置日志
        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 配置测试环境
        os.environ["APP_ENV"] = "test"

        # 创建内存数据库连接
        cls.db_path = ":memory:"

        # 创建仓库实例
        cls.maze_repository = MazeRepository()

        # 创建服务实例
        cls.maze_generator = MazeGenerator()
        cls.knowledge_service = KnowledgeService()
        cls.progress_service = ProgressService()

        cls.maze_service = MazeService(
            maze_repository = cls.maze_repository,
            maze_generator = cls.maze_generator,
            knowledge_service = cls.knowledge_service,
            progress_service = cls.progress_service
        )

        # 启动测试服务器
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
        setup_grpc_server(cls.server, cls.maze_service)
        cls.port = 50057
        cls.server.add_insecure_port(f'[::]:{cls.port}')
        cls.server.start()

        # 创建gRPC客户端
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = pb2_grpc.MazeServiceStub(cls.channel)

        logger.info("测试服务器已启动")

    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        cls.channel.close()
        cls.server.stop(0)
        logger.info("测试服务器已关闭")

    def setUp(self) -> None:
        """每个测试前的准备工作"""
        self.user_id = str(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_maze(self) -> None:
        """测试创建迷宫"""
        # 创建迷宫请求
        request = pb2.CreateMazeRequest(
            user_id = self.user_id,
            maze_type = "health_path",
            size_x = 10,
            size_y = 10,
            difficulty = 3
        )

        # 调用gRPC方法
        response = self.stub.CreateMaze(request)

        # 验证响应
        self.assertEqual(response.success, True)
        self.assertIsNotNone(response.maze.maze_id)
        self.assertEqual(response.maze.user_id, self.user_id)
        self.assertEqual(response.maze.maze_type, "health_path")
        self.assertEqual(response.maze.size_x, 10)
        self.assertEqual(response.maze.size_y, 10)
        self.assertEqual(response.maze.difficulty, 3)

        # 验证知识节点和挑战
        self.assertGreater(len(response.maze.knowledge_nodes), 0)
        self.assertGreater(len(response.maze.challenges), 0)

        # 保存迷宫ID用于后续测试
        self.maze_id = response.maze.maze_id

    @pytest.mark.asyncio
    async def test_get_maze(self) -> None:
        """测试获取迷宫"""
        # 首先创建一个迷宫
        create_request = pb2.CreateMazeRequest(
            user_id = self.user_id,
            maze_type = "nutrition_garden",
            size_x = 8,
            size_y = 8,
            difficulty = 2
        )
        create_response = self.stub.CreateMaze(create_request)
        maze_id = create_response.maze.maze_id

        # 然后获取这个迷宫
        get_request = pb2.GetMazeRequest(
            maze_id = maze_id
        )
        get_response = self.stub.GetMaze(get_request)

        # 验证响应
        self.assertEqual(get_response.success, True)
        self.assertEqual(get_response.maze.maze_id, maze_id)
        self.assertEqual(get_response.maze.user_id, self.user_id)
        self.assertEqual(get_response.maze.maze_type, "nutrition_garden")
        self.assertEqual(get_response.maze.size_x, 8)
        self.assertEqual(get_response.maze.size_y, 8)
        self.assertEqual(get_response.maze.difficulty, 2)

    @pytest.mark.asyncio
    async def test_get_nonexistent_maze(self) -> None:
        """测试获取不存在的迷宫"""
        request = pb2.GetMazeRequest(
            maze_id = "nonexistent - maze - id"
        )
        response = self.stub.GetMaze(request)

        # 验证响应
        self.assertEqual(response.success, False)
        self.assertEqual(response.error_message, "未找到指定的迷宫")

    @pytest.mark.asyncio
    async def test_get_user_mazes(self) -> None:
        """测试获取用户的迷宫列表"""
        # 为用户创建多个迷宫
        maze_types = ["health_path", "nutrition_garden", "tcm_journey"]
        for maze_type in maze_types:
            create_request = pb2.CreateMazeRequest(
                user_id = self.user_id,
                maze_type = maze_type,
                size_x = 10,
                size_y = 10,
                difficulty = 3
            )
            self.stub.CreateMaze(create_request)

        # 获取用户的迷宫列表
        request = pb2.GetUserMazesRequest(
            user_id = self.user_id,
            limit = 10,
            offset = 0
        )
        response = self.stub.GetUserMazes(request)

        # 验证响应
        self.assertEqual(response.success, True)
        self.assertGreaterEqual(len(response.mazes), len(maze_types))

        # 验证迷宫类型
        maze_types_found = [maze.maze_type for maze in response.mazes]
        for maze_type in maze_types:
            self.assertIn(maze_type, maze_types_found)

    @pytest.mark.asyncio
    async def test_search_mazes(self) -> None:
        """测试搜索迷宫"""
        # 创建一些公开迷宫
        public_maze_types = ["health_path", "tcm_journey"]
        for maze_type in public_maze_types:
            create_request = pb2.CreateMazeRequest(
                user_id = self.user_id,
                maze_type = maze_type,
                size_x = 10,
                size_y = 10,
                difficulty = 3
            )
            response = self.stub.CreateMaze(create_request)

            # 将迷宫设为公开
            maze_id = response.maze.maze_id
            update_request = pb2.UpdateMazeRequest(
                maze_id = maze_id,
                is_public = True
            )
            self.stub.UpdateMaze(update_request)

        # 搜索迷宫
        request = pb2.SearchMazesRequest(
            query = "health",
            limit = 10,
            offset = 0
        )
        response = self.stub.SearchMazes(request)

        # 验证响应
        self.assertEqual(response.success, True)
        self.assertGreaterEqual(len(response.mazes), 1)

        # 验证至少有一个健康路径迷宫
        health_mazes = [maze for maze in response.mazes if maze.maze_type == "health_path"]
        self.assertGreaterEqual(len(health_mazes), 1)

    @pytest.mark.asyncio
    async def test_update_maze(self) -> None:
        """测试更新迷宫"""
        # 首先创建一个迷宫
        create_request = pb2.CreateMazeRequest(
            user_id = self.user_id,
            maze_type = "balanced_life",
            size_x = 12,
            size_y = 12,
            difficulty = 4
        )
        create_response = self.stub.CreateMaze(create_request)
        maze_id = create_response.maze.maze_id

        # 更新迷宫
        new_description = "更新后的平衡生活迷宫"
        update_request = pb2.UpdateMazeRequest(
            maze_id = maze_id,
            description = new_description,
            is_public = True
        )
        update_response = self.stub.UpdateMaze(update_request)

        # 验证响应
        self.assertEqual(update_response.success, True)

        # 获取更新后的迷宫
        get_request = pb2.GetMazeRequest(
            maze_id = maze_id
        )
        get_response = self.stub.GetMaze(get_request)

        # 验证更新是否生效
        self.assertEqual(get_response.maze.description, new_description)
        self.assertEqual(get_response.maze.is_public, True)

    @pytest.mark.asyncio
    async def test_delete_maze(self) -> None:
        """测试删除迷宫"""
        # 首先创建一个迷宫
        create_request = pb2.CreateMazeRequest(
            user_id = self.user_id,
            maze_type = "health_path",
            size_x = 10,
            size_y = 10,
            difficulty = 3
        )
        create_response = self.stub.CreateMaze(create_request)
        maze_id = create_response.maze.maze_id

        # 删除迷宫
        delete_request = pb2.DeleteMazeRequest(
            maze_id = maze_id
        )
        delete_response = self.stub.DeleteMaze(delete_request)

        # 验证响应
        self.assertEqual(delete_response.success, True)

        # 尝试获取已删除的迷宫
        get_request = pb2.GetMazeRequest(
            maze_id = maze_id
        )
        get_response = self.stub.GetMaze(get_request)

        # 验证迷宫已被删除
        self.assertEqual(get_response.success, False)

    @pytest.mark.asyncio
    async def test_update_user_progress(self) -> None:
        """测试更新用户进度"""
        # 首先创建一个迷宫
        create_request = pb2.CreateMazeRequest(
            user_id = self.user_id,
            maze_type = "health_path",
            size_x = 10,
            size_y = 10,
            difficulty = 3
        )
        create_response = self.stub.CreateMaze(create_request)
        maze_id = create_response.maze.maze_id

        # 更新用户进度
        progress_request = pb2.UpdateProgressRequest(
            user_id = self.user_id,
            maze_id = maze_id,
            current_position = {
                "x": 5,
                "y": 5
            },
            completed_challenges = ["challenge - 0"],
            visited_nodes = ["health - 0", "health - 1"]
        )
        progress_response = self.stub.UpdateProgress(progress_request)

        # 验证响应
        self.assertEqual(progress_response.success, True)

        # 获取用户进度
        get_progress_request = pb2.GetProgressRequest(
            user_id = self.user_id,
            maze_id = maze_id
        )
        get_progress_response = self.stub.GetProgress(get_progress_request)

        # 验证进度是否正确
        self.assertEqual(get_progress_response.success, True)
        self.assertEqual(get_progress_response.progress.current_position.x, 5)
        self.assertEqual(get_progress_response.progress.current_position.y, 5)
        self.assertEqual(len(get_progress_response.progress.completed_challenges), 1)
        self.assertEqual(len(get_progress_response.progress.visited_nodes), 2)

    @pytest.mark.asyncio
    async def test_complete_maze(self) -> None:
        """测试完成迷宫"""
        # 首先创建一个迷宫
        create_request = pb2.CreateMazeRequest(
            user_id = self.user_id,
            maze_type = "health_path",
            size_x = 10,
            size_y = 10,
            difficulty = 3
        )
        create_response = self.stub.CreateMaze(create_request)
        maze_id = create_response.maze.maze_id

        # 完成迷宫
        complete_request = pb2.CompleteMazeRequest(
            user_id = self.user_id,
            maze_id = maze_id,
            time_spent_seconds = 300,
            challenges_completed = 2,
            knowledge_nodes_visited = 3
        )
        complete_response = self.stub.CompleteMaze(complete_request)

        # 验证响应
        self.assertEqual(complete_response.success, True)
        self.assertGreater(complete_response.rewards.experience_points, 0)

        # 获取迷宫，检查状态
        get_request = pb2.GetMazeRequest(
            maze_id = maze_id
        )
        get_response = self.stub.GetMaze(get_request)

        # 验证迷宫状态
        self.assertEqual(get_response.maze.status, "COMPLETED")

if __name__ == "__main__":
    unittest.main()
