#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Corn Maze Service gRPC服务实现
"""

import logging
import sys
import uuid
from datetime import datetime

import grpc

# 添加自动生成的gRPC代码路径
sys.path.append("api")

# 尝试导入自动生成的gRPC代码
try:
    from api import corn_maze_pb2, corn_maze_pb2_grpc
except ImportError:
    print("警告: 无法导入gRPC生成的代码，这在开发时可能是正常的")
    # 创建模拟的gRPC类，以便开发时不会报错
    class corn_maze_pb2_grpc:
        class CornMazeServiceServicer:
            pass

from internal.service.maze_service import MazeService
from internal.service.progress_service import ProgressService
from internal.service.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)

class CornMazeServicer(corn_maze_pb2_grpc.CornMazeServiceServicer):
    """Corn Maze Service的gRPC实现"""
    
    def __init__(self):
        self.maze_service = MazeService()
        self.progress_service = ProgressService()
        self.knowledge_service = KnowledgeService()
        logger.info("CornMazeServicer初始化完成")
    
    async def CreateMaze(self, request, context):
        """创建新迷宫"""
        try:
            logger.info(f"接收到创建迷宫请求，用户ID: {request.user_id}, 类型: {request.maze_type}")
            
            # 创建迷宫
            maze = await self.maze_service.create_maze(
                user_id=request.user_id,
                maze_type=request.maze_type,
                difficulty=request.difficulty,
                health_attributes=dict(request.health_attributes),
                use_template=request.use_template,
                template_id=request.template_id if request.use_template else None
            )
            
            # 构造响应
            return self._build_maze_response(maze)
        
        except Exception as e:
            logger.error(f"创建迷宫时出错: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"创建迷宫失败: {str(e)}")
            return corn_maze_pb2.MazeResponse()
    
    async def GetMaze(self, request, context):
        """获取迷宫信息"""
        try:
            logger.info(f"接收到获取迷宫请求，迷宫ID: {request.maze_id}")
            
            # 获取迷宫
            maze = await self.maze_service.get_maze(
                maze_id=request.maze_id,
                user_id=request.user_id
            )
            
            if not maze:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"未找到ID为{request.maze_id}的迷宫")
                return corn_maze_pb2.MazeResponse()
            
            # 构造响应
            return self._build_maze_response(maze)
        
        except Exception as e:
            logger.error(f"获取迷宫时出错: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取迷宫失败: {str(e)}")
            return corn_maze_pb2.MazeResponse()
    
    async def MoveInMaze(self, request, context):
        """用户在迷宫中移动"""
        try:
            logger.info(f"接收到移动请求，迷宫ID: {request.maze_id}, 用户ID: {request.user_id}, 方向: {request.direction}")
            
            # 执行移动
            result = await self.progress_service.move_user(
                maze_id=request.maze_id,
                user_id=request.user_id,
                direction=request.direction
            )
            
            # 构造响应
            response = corn_maze_pb2.MoveResponse(
                success=result["success"],
                new_position=corn_maze_pb2.Position(x=result["position"]["x"], y=result["position"]["y"]),
                event_type=result.get("event_type", "NONE"),
                event_id=result.get("event_id", ""),
                message=result.get("message", "")
            )
            
            return response
        
        except Exception as e:
            logger.error(f"移动时出错: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"移动失败: {str(e)}")
            return corn_maze_pb2.MoveResponse(success=False, message=f"移动失败: {str(e)}")
    
    async def GetUserProgress(self, request, context):
        """获取用户在迷宫中的进度"""
        try:
            logger.info(f"接收到获取用户进度请求，用户ID: {request.user_id}, 迷宫ID: {request.maze_id}")
            
            # 获取进度
            progress = await self.progress_service.get_user_progress(
                user_id=request.user_id,
                maze_id=request.maze_id
            )
            
            if not progress:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"未找到用户{request.user_id}在迷宫{request.maze_id}中的进度")
                return corn_maze_pb2.UserProgressResponse()
            
            # 构造响应
            response = corn_maze_pb2.UserProgressResponse(
                user_id=progress["user_id"],
                maze_id=progress["maze_id"],
                current_position=corn_maze_pb2.Position(
                    x=progress["current_position"]["x"],
                    y=progress["current_position"]["y"]
                ),
                visited_cells=progress["visited_cells"],
                completed_challenges=progress["completed_challenges"],
                acquired_knowledge=progress["acquired_knowledge"],
                completion_percentage=progress["completion_percentage"],
                status=progress["status"],
                steps_taken=progress["steps_taken"],
                start_time=progress["start_time"].isoformat(),
                last_active_time=progress["last_active_time"].isoformat()
            )
            
            return response
        
        except Exception as e:
            logger.error(f"获取用户进度时出错: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取用户进度失败: {str(e)}")
            return corn_maze_pb2.UserProgressResponse()
    
    async def ListMazeTemplates(self, request, context):
        """获取可用的迷宫模板"""
        try:
            logger.info(f"接收到获取迷宫模板列表请求，类型: {request.maze_type}, 难度: {request.difficulty}")
            
            # 获取模板列表
            templates, total = await self.maze_service.list_templates(
                maze_type=request.maze_type,
                difficulty=request.difficulty,
                page=request.page,
                page_size=request.page_size
            )
            
            # 构造响应
            response = corn_maze_pb2.ListMazeTemplatesResponse(
                total=total
            )
            
            # 添加模板
            for template in templates:
                template_pb = corn_maze_pb2.MazeTemplate(
                    template_id=template["template_id"],
                    name=template["name"],
                    description=template["description"],
                    maze_type=template["maze_type"],
                    difficulty=template["difficulty"],
                    preview_image_url=template["preview_image_url"],
                    size_x=template["size_x"],
                    size_y=template["size_y"],
                    knowledge_node_count=template["knowledge_node_count"],
                    challenge_count=template["challenge_count"]
                )
                response.templates.append(template_pb)
            
            return response
        
        except Exception as e:
            logger.error(f"获取迷宫模板列表时出错: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取迷宫模板列表失败: {str(e)}")
            return corn_maze_pb2.ListMazeTemplatesResponse()
    
    async def RecordMazeCompletion(self, request, context):
        """记录用户完成迷宫挑战"""
        try:
            logger.info(f"接收到记录迷宫完成请求，用户ID: {request.user_id}, 迷宫ID: {request.maze_id}")
            
            # 记录完成情况
            result = await self.progress_service.record_completion(
                user_id=request.user_id,
                maze_id=request.maze_id,
                steps_taken=request.steps_taken,
                time_spent_seconds=request.time_spent_seconds,
                knowledge_nodes_discovered=request.knowledge_nodes_discovered,
                challenges_completed=request.challenges_completed
            )
            
            # 构造响应
            response = corn_maze_pb2.RecordMazeCompletionResponse(
                success=result["success"],
                completion_id=result["completion_id"],
                points_earned=result["points_earned"],
                message=result["message"]
            )
            
            # 添加奖励
            for reward in result["rewards"]:
                reward_pb = corn_maze_pb2.Reward(
                    reward_id=reward["reward_id"],
                    reward_type=reward["reward_type"],
                    name=reward["name"],
                    description=reward["description"],
                    value=reward["value"]
                )
                response.rewards.append(reward_pb)
            
            return response
        
        except Exception as e:
            logger.error(f"记录迷宫完成时出错: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"记录迷宫完成失败: {str(e)}")
            return corn_maze_pb2.RecordMazeCompletionResponse(
                success=False,
                message=f"记录迷宫完成失败: {str(e)}"
            )
    
    async def GetKnowledgeNode(self, request, context):
        """获取健康知识节点"""
        try:
            logger.info(f"接收到获取知识节点请求，节点ID: {request.node_id}")
            
            # 获取知识节点
            node = await self.knowledge_service.get_knowledge_node(node_id=request.node_id)
            
            if not node:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"未找到ID为{request.node_id}的知识节点")
                return corn_maze_pb2.KnowledgeNodeResponse()
            
            # 构造响应
            knowledge_node = corn_maze_pb2.KnowledgeNode(
                node_id=node["node_id"],
                title=node["title"],
                content=node["content"],
                category=node["category"],
                difficulty_level=node["difficulty_level"]
            )
            
            # 添加标签
            for tag in node["related_tags"]:
                knowledge_node.related_tags.append(tag)
            
            return corn_maze_pb2.KnowledgeNodeResponse(node=knowledge_node)
        
        except Exception as e:
            logger.error(f"获取知识节点时出错: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取知识节点失败: {str(e)}")
            return corn_maze_pb2.KnowledgeNodeResponse()
    
    def _build_maze_response(self, maze):
        """构建迷宫响应对象"""
        response = corn_maze_pb2.MazeResponse(
            maze_id=maze["maze_id"],
            maze_type=maze["maze_type"],
            size_x=maze["size_x"],
            size_y=maze["size_y"],
            start_position=corn_maze_pb2.Position(
                x=maze["start_position"]["x"],
                y=maze["start_position"]["y"]
            ),
            goal_position=corn_maze_pb2.Position(
                x=maze["goal_position"]["x"],
                y=maze["goal_position"]["y"]
            ),
            created_at=maze["created_at"].isoformat(),
            difficulty=maze["difficulty"],
            status=maze["status"]
        )
        
        # 添加单元格
        for cell in maze["cells"]:
            cell_pb = corn_maze_pb2.MazeCell(
                x=cell["x"],
                y=cell["y"],
                type=getattr(corn_maze_pb2, cell["type"]),
                north_wall=cell["north_wall"],
                east_wall=cell["east_wall"],
                south_wall=cell["south_wall"],
                west_wall=cell["west_wall"],
                cell_id=cell["cell_id"],
                content_id=cell.get("content_id", "")
            )
            response.cells.append(cell_pb)
        
        # 添加知识节点
        for node in maze["knowledge_nodes"]:
            node_pb = corn_maze_pb2.KnowledgeNode(
                node_id=node["node_id"],
                title=node["title"],
                content=node["content"],
                category=node["category"],
                difficulty_level=node["difficulty_level"]
            )
            
            # 添加标签
            for tag in node["related_tags"]:
                node_pb.related_tags.append(tag)
                
            response.knowledge_nodes.append(node_pb)
        
        # 添加挑战
        for challenge in maze["challenges"]:
            challenge_pb = corn_maze_pb2.Challenge(
                challenge_id=challenge["challenge_id"],
                title=challenge["title"],
                description=challenge["description"],
                type=challenge["type"],
                difficulty_level=challenge["difficulty_level"],
                reward_description=challenge["reward_description"]
            )
            response.challenges.append(challenge_pb)
            
        return response