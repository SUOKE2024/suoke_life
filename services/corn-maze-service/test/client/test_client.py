#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Corn Maze Service 测试客户端
"""

import sys
import os
import logging
import uuid
import argparse
import grpc
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 设置基本日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # 导入自动生成的gRPC代码
    from api import corn_maze_pb2, corn_maze_pb2_grpc
except ImportError:
    logger.error("无法导入gRPC生成的代码，请先运行生成脚本")
    sys.exit(1)

class CornMazeClient:
    """Corn Maze Service 测试客户端"""
    
    def __init__(self, host="localhost", port=50057):
        """
        初始化客户端
        
        Args:
            host: 服务器主机名
            port: 服务器端口
        """
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = corn_maze_pb2_grpc.CornMazeServiceStub(self.channel)
        logger.info(f"连接到 Corn Maze Service: {host}:{port}")
    
    def create_maze(self, user_id=None, maze_type="四季养生", difficulty=1):
        """
        创建迷宫
        
        Args:
            user_id: 用户ID（如果为None，则生成随机ID）
            maze_type: 迷宫类型
            difficulty: 难度级别
            
        Returns:
            corn_maze_pb2.MazeResponse: 迷宫响应
        """
        if user_id is None:
            user_id = str(uuid.uuid4())
        
        # 准备健康属性
        health_attributes = {
            "constitution": "平和质",
            "season": "春季",
            "age_group": "青年"
        }
        
        # 创建请求
        request = corn_maze_pb2.CreateMazeRequest(
            user_id=user_id,
            maze_type=maze_type,
            difficulty=difficulty,
            health_attributes=health_attributes,
            use_template=False
        )
        
        # 发送请求
        logger.info(f"创建迷宫，用户ID: {user_id}, 类型: {maze_type}, 难度: {difficulty}")
        response = self.stub.CreateMaze(request)
        
        logger.info(f"迷宫创建成功，ID: {response.maze_id}, 大小: {response.size_x}x{response.size_y}")
        return response
    
    def get_maze(self, maze_id, user_id):
        """
        获取迷宫信息
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID
            
        Returns:
            corn_maze_pb2.MazeResponse: 迷宫响应
        """
        # 创建请求
        request = corn_maze_pb2.GetMazeRequest(
            maze_id=maze_id,
            user_id=user_id
        )
        
        # 发送请求
        logger.info(f"获取迷宫，ID: {maze_id}")
        response = self.stub.GetMaze(request)
        
        logger.info(f"迷宫获取成功，ID: {response.maze_id}, 大小: {response.size_x}x{response.size_y}")
        return response
    
    def move_in_maze(self, maze_id, user_id, direction):
        """
        在迷宫中移动
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID
            direction: 移动方向（0-3，北东南西）
            
        Returns:
            corn_maze_pb2.MoveResponse: 移动响应
        """
        # 创建请求
        request = corn_maze_pb2.MoveRequest(
            maze_id=maze_id,
            user_id=user_id,
            direction=direction
        )
        
        # 方向名称
        direction_names = ["北", "东", "南", "西"]
        
        # 发送请求
        logger.info(f"在迷宫 {maze_id} 中向{direction_names[direction]}移动")
        response = self.stub.MoveInMaze(request)
        
        if response.success:
            logger.info(f"移动成功，新位置: ({response.new_position.x}, {response.new_position.y})")
            if response.event_type != "NONE":
                logger.info(f"触发事件: {response.event_type}, ID: {response.event_id}")
                logger.info(f"事件消息: {response.message}")
        else:
            logger.warning(f"移动失败: {response.message}")
        
        return response
    
    def get_user_progress(self, user_id, maze_id):
        """
        获取用户进度
        
        Args:
            user_id: 用户ID
            maze_id: 迷宫ID
            
        Returns:
            corn_maze_pb2.UserProgressResponse: 用户进度响应
        """
        # 创建请求
        request = corn_maze_pb2.UserProgressRequest(
            user_id=user_id,
            maze_id=maze_id
        )
        
        # 发送请求
        logger.info(f"获取用户 {user_id} 在迷宫 {maze_id} 中的进度")
        response = self.stub.GetUserProgress(request)
        
        logger.info(f"进度: {response.completion_percentage}%, 位置: ({response.current_position.x}, {response.current_position.y})")
        logger.info(f"状态: {response.status}, 步数: {response.steps_taken}")
        
        return response
    
    def list_maze_templates(self, maze_type="", difficulty=0, page=1, page_size=10):
        """
        获取迷宫模板列表
        
        Args:
            maze_type: 迷宫类型（可选）
            difficulty: 难度级别（可选）
            page: 页码
            page_size: 每页数量
            
        Returns:
            corn_maze_pb2.ListMazeTemplatesResponse: 模板列表响应
        """
        # 创建请求
        request = corn_maze_pb2.ListMazeTemplatesRequest(
            maze_type=maze_type,
            difficulty=difficulty,
            page=page,
            page_size=page_size
        )
        
        # 发送请求
        logger.info(f"获取迷宫模板列表，类型: {maze_type or '所有'}, 难度: {difficulty or '所有'}")
        response = self.stub.ListMazeTemplates(request)
        
        logger.info(f"共找到 {response.total} 个模板")
        for i, template in enumerate(response.templates):
            logger.info(f"模板 {i+1}: {template.name} - {template.maze_type} - 难度 {template.difficulty}")
        
        return response
    
    def get_knowledge_node(self, node_id):
        """
        获取知识节点
        
        Args:
            node_id: 知识节点ID
            
        Returns:
            corn_maze_pb2.KnowledgeNodeResponse: 知识节点响应
        """
        # 创建请求
        request = corn_maze_pb2.KnowledgeNodeRequest(
            node_id=node_id
        )
        
        # 发送请求
        logger.info(f"获取知识节点，ID: {node_id}")
        response = self.stub.GetKnowledgeNode(request)
        
        if response.node.node_id:
            logger.info(f"知识节点: {response.node.title}")
            logger.info(f"内容: {response.node.content}")
            logger.info(f"类别: {response.node.category}, 难度: {response.node.difficulty_level}")
        else:
            logger.warning(f"未找到ID为 {node_id} 的知识节点")
        
        return response
    
    def close(self):
        """关闭连接"""
        self.channel.close()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Corn Maze Service 测试客户端")
    parser.add_argument("--host", default="localhost", help="服务器主机名")
    parser.add_argument("--port", type=int, default=50057, help="服务器端口")
    parser.add_argument("--user-id", help="用户ID（默认生成随机ID）")
    parser.add_argument("--mode", choices=["create", "get", "move", "progress", "templates", "knowledge"],
                        default="create", help="操作模式")
    parser.add_argument("--maze-id", help="迷宫ID（对于get、move、progress模式必需）")
    parser.add_argument("--maze-type", default="四季养生", help="迷宫类型")
    parser.add_argument("--difficulty", type=int, default=1, help="难度级别")
    parser.add_argument("--direction", type=int, choices=[0, 1, 2, 3], default=1,
                        help="移动方向（0=北, 1=东, 2=南, 3=西）")
    parser.add_argument("--node-id", help="知识节点ID（对于knowledge模式必需）")
    
    args = parser.parse_args()
    
    # 创建客户端
    client = CornMazeClient(args.host, args.port)
    
    try:
        # 根据模式执行操作
        if args.mode == "create":
            maze = client.create_maze(args.user_id, args.maze_type, args.difficulty)
            print(f"\n创建的迷宫ID: {maze.maze_id}")
            print(f"用户ID: {args.user_id or '(已生成随机ID)'}")
            
        elif args.mode == "get":
            if not args.maze_id or not args.user_id:
                print("错误: 获取迷宫信息需要指定maze-id和user-id")
                return
            
            maze = client.get_maze(args.maze_id, args.user_id)
            
        elif args.mode == "move":
            if not args.maze_id or not args.user_id:
                print("错误: 在迷宫中移动需要指定maze-id和user-id")
                return
            
            move_response = client.move_in_maze(args.maze_id, args.user_id, args.direction)
            
        elif args.mode == "progress":
            if not args.maze_id or not args.user_id:
                print("错误: 获取进度需要指定maze-id和user-id")
                return
            
            progress = client.get_user_progress(args.user_id, args.maze_id)
            
        elif args.mode == "templates":
            templates = client.list_maze_templates(args.maze_type, args.difficulty)
            
        elif args.mode == "knowledge":
            if not args.node_id:
                print("错误: 获取知识节点需要指定node-id")
                return
            
            node = client.get_knowledge_node(args.node_id)
    
    except grpc.RpcError as e:
        logger.error(f"gRPC错误: {e.code()}: {e.details()}")
    
    finally:
        client.close()

if __name__ == "__main__":
    main()