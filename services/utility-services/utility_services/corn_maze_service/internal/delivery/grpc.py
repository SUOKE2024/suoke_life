
"""
grpc - 索克生活项目模块
"""

import logging

import grpc
from grpc import aio

from api import corn_maze_pb2, corn_maze_pb2_grpc
from corn_maze_service.config import get_settings

"""
gRPC 交付层

提供 gRPC 接口。
"""




logger = logging.getLogger(__name__)


class CornMazeServicer(corn_maze_pb2_grpc.CornMazeServiceServicer):
    """Corn Maze gRPC 服务实现"""

    async def CreateMaze(
        self,
        request: corn_maze_pb2.CreateMazeRequest,
        context: grpc.aio.ServicerContext
    ) -> corn_maze_pb2.MazeResponse:
        """创建迷宫"""
        logger.info("gRPC CreateMaze called: user_id = %s, type = %s",
                request.user_id, request.maze_type)

        # 这里应该调用业务逻辑层
        # 目前返回一个示例响应
        return corn_maze_pb2.MazeResponse(
            maze_id = "grpc - maze - 001",
            size_x = 10,
            size_y = 10,
            theme = request.maze_type,
            difficulty = request.difficulty,
            status = "CREATED"
        )

    async def GetMaze(
        self,
        request: corn_maze_pb2.GetMazeRequest,
        context: grpc.aio.ServicerContext
    ) -> corn_maze_pb2.MazeResponse:
        """获取迷宫"""
        logger.info("gRPC GetMaze called: maze_id = %s", request.maze_id)

        return corn_maze_pb2.MazeResponse(
            maze_id = request.maze_id,
            size_x = 10,
            size_y = 10,
            theme = "health",
            difficulty = 1,
            status = "ACTIVE"
        )

    async def MoveInMaze(
        self,
        request: corn_maze_pb2.MoveRequest,
        context: grpc.aio.ServicerContext
    ) -> corn_maze_pb2.MoveResponse:
        """在迷宫中移动"""
        logger.info("gRPC MoveInMaze called: maze_id = %s, direction = %d",
                request.maze_id, request.direction)

        return corn_maze_pb2.MoveResponse(
            success = True,
            new_position = corn_maze_pb2.Position(x = 1, y = 1),
            event_type = "KNOWLEDGE",
            event_id = "knowledge - 001",
            message = "发现健康知识点！"
        )

    async def GetUserProgress(
        self,
        request: corn_maze_pb2.UserProgressRequest,
        context: grpc.aio.ServicerContext
    ) -> corn_maze_pb2.UserProgressResponse:
        """获取用户进度"""
        logger.info("gRPC GetUserProgress called: user_id = %s, maze_id = %s",
                request.user_id, request.maze_id)

        return corn_maze_pb2.UserProgressResponse(
            user_id = request.user_id,
            maze_id = request.maze_id,
            current_position = corn_maze_pb2.Position(x = 1, y = 1),
            completion_percentage = 25.0,
            status = "IN_PROGRESS",
            steps_taken = 10
        )

    async def ListMazeTemplates(
        self,
        request: corn_maze_pb2.ListMazeTemplatesRequest,
        context: grpc.aio.ServicerContext
    ) -> corn_maze_pb2.ListMazeTemplatesResponse:
        """列出迷宫模板"""
        logger.info("gRPC ListMazeTemplates called")

        # 示例模板
        template = corn_maze_pb2.MazeTemplate(
            template_id = "template - 001",
            name = "春季养生迷宫",
            maze_type = "health",
            difficulty = 1,
            description = "适合春季的健康养生迷宫"
        )

        return corn_maze_pb2.ListMazeTemplatesResponse(
            templates = [template],
            total = 1,
            page = request.page,
            page_size = request.page_size
        )

    async def GetKnowledgeNode(
        self,
        request: corn_maze_pb2.KnowledgeNodeRequest,
        context: grpc.aio.ServicerContext
    ) -> corn_maze_pb2.KnowledgeNodeResponse:
        """获取知识节点"""
        logger.info("gRPC GetKnowledgeNode called: node_id = %s", request.node_id)

        return corn_maze_pb2.KnowledgeNodeResponse(
            node_id = request.node_id,
            title = "春季养生知识",
            content = "春季是万物复苏的季节，适合进行户外运动...",
            node_type = "HEALTH_TIP",
            difficulty = 1
        )


async def create_grpc_server(settings = None) -> aio.Server:
    """创建 gRPC 服务器"""
    if settings is None:
        settings = get_settings()

    server = aio.server()

    # 添加服务
    corn_maze_pb2_grpc.add_CornMazeServiceServicer_to_server(
        CornMazeServicer(), server
    )

    # 配置监听地址
    listen_addr = f"[::]:{settings.grpc.port}"
    server.add_insecure_port(listen_addr)

    logger.info("gRPC server configured on %s", listen_addr)
    return server
