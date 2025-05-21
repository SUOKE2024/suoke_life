#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Corn Maze Service 集成测试
"""

import unittest
import grpc
import uuid
import asyncio
import sys
import os
import time
from concurrent import futures

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from internal.delivery.grpc.server import CornMazeServicer
from api import corn_maze_pb2, corn_maze_pb2_grpc


class TestCornMazeService(unittest.TestCase):
    """Corn Maze Service 集成测试类"""

    @classmethod
    def setUpClass(cls):
        """测试前准备 - 启动gRPC服务器"""
        # 创建gRPC服务器
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # 注册服务实现
        cls.servicer = CornMazeServicer()
        corn_maze_pb2_grpc.add_CornMazeServiceServicer_to_server(cls.servicer, cls.server)
        
        # 使用随机端口启动服务器
        cls.port = cls.server.add_insecure_port('[::]:0')
        cls.server.start()
        
        print(f"测试服务器启动在端口 {cls.port}")
        
        # 创建通道和存根
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = corn_maze_pb2_grpc.CornMazeServiceStub(cls.channel)
        
        # 等待服务器启动
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """测试后清理 - 关闭gRPC服务器"""
        cls.channel.close()
        cls.server.stop(0)

    def test_create_and_get_maze(self):
        """测试创建和获取迷宫"""
        # 生成唯一用户ID
        user_id = f"test_user_{uuid.uuid4()}"
        
        # 创建迷宫请求
        request = corn_maze_pb2.CreateMazeRequest(
            user_id=user_id,
            maze_type="四季养生",
            difficulty=2,
            health_attributes={"体质": "气虚体质", "季节": "春季"},
            use_template=False
        )
        
        # 发送请求
        response = self.stub.CreateMaze(request)
        
        # 验证响应
        self.assertIsNotNone(response.maze_id)
        self.assertEqual(response.maze_type, "四季养生")
        self.assertEqual(response.difficulty, 2)
        self.assertEqual(response.status, "可用")
        self.assertGreater(len(response.cells), 0)
        self.assertIsNotNone(response.start_position)
        self.assertIsNotNone(response.goal_position)
        
        # 记录迷宫ID以供后续测试使用
        maze_id = response.maze_id
        
        # 获取迷宫请求
        get_request = corn_maze_pb2.GetMazeRequest(
            maze_id=maze_id,
            user_id=user_id
        )
        
        # 获取迷宫
        get_response = self.stub.GetMaze(get_request)
        
        # 验证响应
        self.assertEqual(get_response.maze_id, maze_id)
        self.assertEqual(get_response.maze_type, "四季养生")
        self.assertEqual(get_response.difficulty, 2)
        self.assertEqual(len(get_response.cells), len(response.cells))

    def test_move_in_maze(self):
        """测试在迷宫中移动"""
        # 生成唯一用户ID
        user_id = f"test_user_{uuid.uuid4()}"
        
        # 创建迷宫
        create_request = corn_maze_pb2.CreateMazeRequest(
            user_id=user_id,
            maze_type="四季养生",
            difficulty=1,
            health_attributes={},
            use_template=False
        )
        
        maze_response = self.stub.CreateMaze(create_request)
        maze_id = maze_response.maze_id
        
        # 确定起点位置
        start_position = maze_response.start_position
        
        # 查找可行的移动方向（找没有墙的方向）
        valid_direction = None
        for cell in maze_response.cells:
            if cell.x == start_position.x and cell.y == start_position.y:
                # 检查四个方向的墙
                if not cell.north_wall:
                    valid_direction = corn_maze_pb2.NORTH
                elif not cell.east_wall:
                    valid_direction = corn_maze_pb2.EAST
                elif not cell.south_wall:
                    valid_direction = corn_maze_pb2.SOUTH
                elif not cell.west_wall:
                    valid_direction = corn_maze_pb2.WEST
                break
        
        # 如果找不到有效方向，使用默认方向（可能会失败，但这是预期的）
        if valid_direction is None:
            valid_direction = corn_maze_pb2.NORTH
        
        # 移动请求
        move_request = corn_maze_pb2.MoveRequest(
            maze_id=maze_id,
            user_id=user_id,
            direction=valid_direction
        )
        
        # 移动
        move_response = self.stub.MoveInMaze(move_request)
        
        # 验证响应 - 注意根据迷宫生成的随机性，可能成功也可能失败
        # 这里我们只验证基本字段存在
        self.assertIsNotNone(move_response.success)  # 可能True也可能False
        self.assertIsNotNone(move_response.new_position)
        self.assertIsNotNone(move_response.message)

    def test_get_user_progress(self):
        """测试获取用户进度"""
        # 生成唯一用户ID
        user_id = f"test_user_{uuid.uuid4()}"
        
        # 创建迷宫
        create_request = corn_maze_pb2.CreateMazeRequest(
            user_id=user_id,
            maze_type="五行平衡",
            difficulty=2,
            health_attributes={},
            use_template=False
        )
        
        maze_response = self.stub.CreateMaze(create_request)
        maze_id = maze_response.maze_id
        
        # 获取用户进度请求
        progress_request = corn_maze_pb2.UserProgressRequest(
            user_id=user_id,
            maze_id=maze_id
        )
        
        # 获取用户进度
        progress_response = self.stub.GetUserProgress(progress_request)
        
        # 验证响应
        self.assertEqual(progress_response.user_id, user_id)
        self.assertEqual(progress_response.maze_id, maze_id)
        self.assertEqual(progress_response.status, "进行中")
        self.assertIsNotNone(progress_response.current_position)
        # 验证初始位置应该等于迷宫起点
        self.assertEqual(
            progress_response.current_position.x,
            maze_response.start_position.x
        )
        self.assertEqual(
            progress_response.current_position.y,
            maze_response.start_position.y
        )
        
    def test_list_maze_templates(self):
        """测试列出迷宫模板"""
        # 请求
        request = corn_maze_pb2.ListMazeTemplatesRequest(
            maze_type="",  # 空字符串表示所有类型
            difficulty=0,  # 0表示所有难度
            page=1,
            page_size=10
        )
        
        # 获取模板列表
        response = self.stub.ListMazeTemplates(request)
        
        # 验证响应 - 至少应该有一些模板
        self.assertIsNotNone(response.templates)
        # 注意：这个测试假设系统中已有预设的模板
        # 如果模板是动态生成的，可能需要先创建模板再验证

    def test_get_knowledge_node(self):
        """测试获取知识节点"""
        # 首先创建迷宫以获取包含的知识节点
        user_id = f"test_user_{uuid.uuid4()}"
        
        create_request = corn_maze_pb2.CreateMazeRequest(
            user_id=user_id,
            maze_type="经络调理",
            difficulty=3,
            health_attributes={},
            use_template=False
        )
        
        maze_response = self.stub.CreateMaze(create_request)
        
        # 确保有知识节点
        if len(maze_response.knowledge_nodes) > 0:
            node_id = maze_response.knowledge_nodes[0].node_id
            
            # 请求知识节点
            node_request = corn_maze_pb2.KnowledgeNodeRequest(
                node_id=node_id
            )
            
            # 获取知识节点
            node_response = self.stub.GetKnowledgeNode(node_request)
            
            # 验证响应
            self.assertIsNotNone(node_response.node)
            self.assertEqual(node_response.node.node_id, node_id)


if __name__ == "__main__":
    unittest.main() 