#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
迷宫服务 - 负责迷宫的生成和管理 - 优化版本
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
from internal.service.knowledge_service import KnowledgeService
from internal.service.progress_service import ProgressService
from pkg.utils.cache import CacheManager
from pkg.utils.metrics import record_maze_operation, record_maze_error

logger = logging.getLogger(__name__)

class MazeService:
    """迷宫服务，负责迷宫的生成和管理"""
    
    def __init__(
        self,
        maze_repository: Optional[MazeRepository] = None,
        maze_generator: Optional[MazeGenerator] = None,
        knowledge_service: Optional[KnowledgeService] = None,
        progress_service: Optional[ProgressService] = None,
        cache_manager: Optional[CacheManager] = None
    ):
        """
        初始化迷宫服务
        
        Args:
            maze_repository: 迷宫存储库
            maze_generator: 迷宫生成器
            knowledge_service: 知识服务
            progress_service: 进度服务
            cache_manager: 缓存管理器
        """
        # 初始化缓存管理器（优先级最高，其他服务可能依赖它）
        self.cache_manager = cache_manager or CacheManager()
        
        # 初始化其他服务
        self.maze_repo = maze_repository or MazeRepository()
        self.template_repo = TemplateRepository()
        self.generator = maze_generator or MazeGenerator(self.cache_manager)
        self.knowledge_service = knowledge_service or KnowledgeService()
        self.progress_service = progress_service or ProgressService()
        
        logger.info("迷宫服务初始化完成")
    
    async def create_maze(
        self, 
        user_id: str, 
        maze_type: str, 
        difficulty: int, 
        health_attributes: Optional[Dict[str, str]] = None,
        use_template: bool = False,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建新迷宫
        
        Args:
            user_id: 用户ID
            maze_type: 迷宫类型（health_path, nutrition_garden, tcm_journey, balanced_life）
            difficulty: 难度级别（1-5）
            health_attributes: 用户健康属性
            use_template: 是否使用模板
            template_id: 模板ID（如果使用模板）
            
        Returns:
            Dict: 包含迷宫信息的字典
            
        Raises:
            ValueError: 参数无效时
            Exception: 创建失败时
        """
        try:
            logger.info(f"为用户 {user_id} 创建 {maze_type} 类型、难度 {difficulty} 的迷宫")
            
            # 参数验证
            if not user_id or not maze_type:
                raise ValueError("用户ID和迷宫类型不能为空")
            
            if difficulty < 1 or difficulty > 5:
                raise ValueError("难度级别必须在1-5之间")
            
            if maze_type not in MazeGenerator.MAZE_TYPES:
                raise ValueError(f"无效的迷宫类型: {maze_type}")
            
            # 检查用户是否已有相同类型的活跃迷宫
            existing_mazes = await self.maze_repo.get_mazes_by_user(user_id, limit=50)
            active_same_type = [m for m in existing_mazes if m.maze_type == maze_type and m.status == "ACTIVE"]
            
            if len(active_same_type) >= 3:  # 限制每种类型最多3个活跃迷宫
                logger.warning(f"用户 {user_id} 已有过多 {maze_type} 类型的活跃迷宫")
                raise ValueError(f"您已有过多 {maze_type} 类型的活跃迷宫，请先完成现有迷宫")
            
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
                maze = await self.generator.create_from_template(
                    template=template,
                    user_id=user_id,
                    health_attributes=health_attributes or {}
                )
            else:
                logger.info(f"生成新迷宫，大小为 {size_x}x{size_y}")
                # 生成新迷宫 - 修复方法调用
                maze = await self.generator.generate_maze(
                    user_id=user_id,
                    maze_type=maze_type,
                    size_x=size_x,
                    size_y=size_y,
                    difficulty=difficulty,
                    health_attributes=health_attributes or {}
                )
            
            # 保存迷宫
            saved_maze = await self.maze_repo.save_maze(maze)
            
            # 记录指标
            record_maze_operation("create", maze_type, difficulty)
            
            # 缓存迷宫信息
            cache_key = f"maze:{saved_maze.maze_id}"
            await self.cache_manager.set(cache_key, saved_maze.to_dict(), ttl=1800)  # 缓存30分钟
            
            logger.info(f"成功创建迷宫 {saved_maze.maze_id}")
            return saved_maze.to_dict()
            
        except ValueError as e:
            logger.warning(f"创建迷宫参数错误: {str(e)}")
            record_maze_error("create", "validation_error")
            raise
        except Exception as e:
            logger.exception(f"创建迷宫时发生错误: {str(e)}")
            record_maze_error("create", "creation_failed")
            raise Exception(f"创建迷宫失败: {str(e)}")
    
    async def get_maze(self, maze_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取迷宫信息
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 迷宫信息或None（如果未找到）
        """
        try:
            logger.info(f"获取迷宫 {maze_id}")
            
            if not maze_id or not user_id:
                raise ValueError("迷宫ID和用户ID不能为空")
            
            # 先从缓存获取
            cache_key = f"maze:{maze_id}"
            cached_maze = await self.cache_manager.get(cache_key)
            
            if cached_maze:
                logger.info(f"从缓存获取迷宫 {maze_id}")
                # 验证权限
                if cached_maze.get("user_id") != user_id and not cached_maze.get("is_public", False):
                    logger.warning(f"用户 {user_id} 试图访问不属于他们的迷宫 {maze_id}")
                    return None
                record_maze_operation("get", cached_maze.get("maze_type", "unknown"), 0)
                return cached_maze
            
            # 从数据库获取
            maze = await self.maze_repo.get_maze(maze_id)
            
            if not maze:
                logger.warning(f"未找到ID为 {maze_id} 的迷宫")
                return None
            
            # 检查权限
            if maze.user_id != user_id and not maze.is_public:
                logger.warning(f"用户 {user_id} 试图访问不属于他们的迷宫 {maze_id}")
                return None
            
            maze_dict = maze.to_dict()
            
            # 缓存结果
            await self.cache_manager.set(cache_key, maze_dict, ttl=1800)
            
            record_maze_operation("get", maze.maze_type, maze.difficulty)
            return maze_dict
            
        except ValueError as e:
            logger.warning(f"获取迷宫参数错误: {str(e)}")
            record_maze_error("get", "validation_error")
            raise
        except Exception as e:
            logger.exception(f"获取迷宫时发生错误: {str(e)}")
            record_maze_error("get", "retrieval_failed")
            raise Exception(f"获取迷宫失败: {str(e)}")
    
    async def get_user_mazes(
        self,
        user_id: str,
        maze_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取用户的迷宫列表
        
        Args:
            user_id: 用户ID
            maze_type: 迷宫类型筛选（可选）
            status: 状态筛选（可选）
            page: 页码
            page_size: 每页数量
            
        Returns:
            Tuple[List[Dict], int]: 迷宫列表和总数
        """
        try:
            logger.info(f"获取用户 {user_id} 的迷宫列表")
            
            if not user_id:
                raise ValueError("用户ID不能为空")
            
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # 构建缓存键
            cache_key = f"user_mazes:{user_id}:{maze_type or 'all'}:{status or 'all'}:{page}:{page_size}"
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result:
                logger.info(f"从缓存获取用户迷宫列表: {user_id}")
                return cached_result["mazes"], cached_result["total"]
            
            # 从数据库获取
            offset = (page - 1) * page_size
            mazes = await self.maze_repo.get_mazes_by_user(user_id, limit=page_size, offset=offset)
            
            # 应用筛选条件
            if maze_type:
                mazes = [m for m in mazes if m.maze_type == maze_type]
            if status:
                mazes = [m for m in mazes if m.status == status]
            
            # 转换为字典列表
            maze_dicts = [maze.to_dict() for maze in mazes]
            
            # 获取总数（简化版本，实际应该在数据库层面实现）
            total = len(maze_dicts)
            
            # 缓存结果
            result = {"mazes": maze_dicts, "total": total}
            await self.cache_manager.set(cache_key, result, ttl=300)  # 缓存5分钟
            
            record_maze_operation("list", maze_type or "all", 0)
            return maze_dicts, total
            
        except ValueError as e:
            logger.warning(f"获取用户迷宫列表参数错误: {str(e)}")
            record_maze_error("list", "validation_error")
            raise
        except Exception as e:
            logger.exception(f"获取用户迷宫列表时发生错误: {str(e)}")
            record_maze_error("list", "retrieval_failed")
            raise Exception(f"获取迷宫列表失败: {str(e)}")
    
    async def update_maze(
        self,
        maze_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新迷宫信息
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID（用于验证权限）
            updates: 要更新的字段
            
        Returns:
            Optional[Dict]: 更新后的迷宫信息
        """
        try:
            logger.info(f"更新迷宫 {maze_id}")
            
            if not maze_id or not user_id:
                raise ValueError("迷宫ID和用户ID不能为空")
            
            # 获取现有迷宫
            maze = await self.maze_repo.get_maze(maze_id)
            if not maze:
                logger.warning(f"未找到ID为 {maze_id} 的迷宫")
                return None
            
            # 检查权限
            if maze.user_id != user_id:
                logger.warning(f"用户 {user_id} 试图更新不属于他们的迷宫 {maze_id}")
                raise ValueError("无权限更新此迷宫")
            
            # 允许更新的字段
            allowed_fields = {"description", "tags", "is_public", "status"}
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                logger.warning("没有有效的更新字段")
                return maze.to_dict()
            
            # 应用更新
            for field, value in filtered_updates.items():
                setattr(maze, field, value)
            
            # 保存更新
            updated_maze = await self.maze_repo.save_maze(maze)
            
            # 清除相关缓存
            cache_keys = [
                f"maze:{maze_id}",
                f"user_mazes:{user_id}:*"  # 清除用户迷宫列表缓存
            ]
            for key in cache_keys:
                await self.cache_manager.delete(key)
            
            record_maze_operation("update", maze.maze_type, maze.difficulty)
            logger.info(f"成功更新迷宫 {maze_id}")
            return updated_maze.to_dict()
            
        except ValueError as e:
            logger.warning(f"更新迷宫参数错误: {str(e)}")
            record_maze_error("update", "validation_error")
            raise
        except Exception as e:
            logger.exception(f"更新迷宫时发生错误: {str(e)}")
            record_maze_error("update", "update_failed")
            raise Exception(f"更新迷宫失败: {str(e)}")
    
    async def delete_maze(self, maze_id: str, user_id: str) -> bool:
        """
        删除迷宫
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID（用于验证权限）
            
        Returns:
            bool: 是否成功删除
        """
        try:
            logger.info(f"删除迷宫 {maze_id}")
            
            if not maze_id or not user_id:
                raise ValueError("迷宫ID和用户ID不能为空")
            
            # 获取迷宫
            maze = await self.maze_repo.get_maze(maze_id)
            
            if not maze:
                logger.warning(f"未找到ID为 {maze_id} 的迷宫")
                return False
            
            # 检查权限
            if maze.user_id != user_id:
                logger.warning(f"用户 {user_id} 试图删除不属于他们的迷宫 {maze_id}")
                raise ValueError("无权限删除此迷宫")
            
            # 删除迷宫
            success = await self.maze_repo.delete_maze(maze_id)
            
            if success:
                # 清除相关缓存
                cache_keys = [
                    f"maze:{maze_id}",
                    f"user_mazes:{user_id}:*"  # 清除用户迷宫列表缓存
                ]
                for key in cache_keys:
                    await self.cache_manager.delete(key)
                
                record_maze_operation("delete", maze.maze_type, maze.difficulty)
                logger.info(f"成功删除迷宫 {maze_id}")
            else:
                logger.error(f"删除迷宫 {maze_id} 失败")
                record_maze_error("delete", "deletion_failed")
            
            return success
            
        except ValueError as e:
            logger.warning(f"删除迷宫参数错误: {str(e)}")
            record_maze_error("delete", "validation_error")
            raise
        except Exception as e:
            logger.exception(f"删除迷宫时发生错误: {str(e)}")
            record_maze_error("delete", "deletion_failed")
            raise Exception(f"删除迷宫失败: {str(e)}")
    
    async def search_mazes(
        self,
        query: str,
        user_id: Optional[str] = None,
        maze_type: Optional[str] = None,
        difficulty: Optional[int] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        搜索迷宫
        
        Args:
            query: 搜索关键词
            user_id: 用户ID（可选，用于个性化搜索）
            maze_type: 迷宫类型筛选（可选）
            difficulty: 难度筛选（可选）
            page: 页码
            page_size: 每页数量
            
        Returns:
            Tuple[List[Dict], int]: 搜索结果和总数
        """
        try:
            logger.info(f"搜索迷宫，关键词: {query}")
            
            if not query or len(query.strip()) < 2:
                raise ValueError("搜索关键词至少需要2个字符")
            
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 50:
                page_size = 10
            
            # 构建缓存键
            cache_key = f"search:{hash(query)}:{maze_type or 'all'}:{difficulty or 'all'}:{page}:{page_size}"
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result:
                logger.info(f"从缓存获取搜索结果: {query}")
                return cached_result["mazes"], cached_result["total"]
            
            # 从数据库搜索
            offset = (page - 1) * page_size
            mazes, total = await self.maze_repo.search_mazes(
                query=query,
                maze_type=maze_type,
                difficulty=difficulty,
                limit=page_size,
                offset=offset
            )
            
            # 转换为字典列表
            maze_dicts = [maze.to_dict() for maze in mazes]
            
            # 缓存结果
            result = {"mazes": maze_dicts, "total": total}
            await self.cache_manager.set(cache_key, result, ttl=600)  # 缓存10分钟
            
            record_maze_operation("search", maze_type or "all", 0)
            return maze_dicts, total
            
        except ValueError as e:
            logger.warning(f"搜索迷宫参数错误: {str(e)}")
            record_maze_error("search", "validation_error")
            raise
        except Exception as e:
            logger.exception(f"搜索迷宫时发生错误: {str(e)}")
            record_maze_error("search", "search_failed")
            raise Exception(f"搜索迷宫失败: {str(e)}")
    
    async def get_maze_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取迷宫统计信息
        
        Args:
            user_id: 用户ID（可选，如果提供则返回用户特定统计）
            
        Returns:
            Dict: 统计信息
        """
        try:
            logger.info(f"获取迷宫统计信息，用户: {user_id or '全局'}")
            
            # 构建缓存键
            cache_key = f"maze_stats:{user_id or 'global'}"
            cached_stats = await self.cache_manager.get(cache_key)
            
            if cached_stats:
                logger.info("从缓存获取统计信息")
                return cached_stats
            
            if user_id:
                # 用户特定统计
                user_mazes = await self.maze_repo.get_mazes_by_user(user_id, limit=1000)
                
                stats = {
                    "total_mazes": len(user_mazes),
                    "active_mazes": len([m for m in user_mazes if m.status == "ACTIVE"]),
                    "completed_mazes": len([m for m in user_mazes if m.status == "COMPLETED"]),
                    "by_type": {},
                    "by_difficulty": {},
                    "average_difficulty": 0
                }
                
                # 按类型统计
                for maze_type in MazeGenerator.MAZE_TYPES:
                    type_mazes = [m for m in user_mazes if m.maze_type == maze_type]
                    stats["by_type"][maze_type] = len(type_mazes)
                
                # 按难度统计
                for difficulty in range(1, 6):
                    diff_mazes = [m for m in user_mazes if m.difficulty == difficulty]
                    stats["by_difficulty"][str(difficulty)] = len(diff_mazes)
                
                # 平均难度
                if user_mazes:
                    stats["average_difficulty"] = sum(m.difficulty for m in user_mazes) / len(user_mazes)
            else:
                # 全局统计
                total_count = await self.maze_repo.count_active_mazes()
                type_counts = await self.maze_repo.get_maze_types_count()
                
                stats = {
                    "total_active_mazes": total_count,
                    "by_type": type_counts,
                    "popular_types": sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                }
            
            # 缓存结果
            await self.cache_manager.set(cache_key, stats, ttl=1800)  # 缓存30分钟
            
            return stats
            
        except Exception as e:
            logger.exception(f"获取迷宫统计信息时发生错误: {str(e)}")
            record_maze_error("stats", "stats_failed")
            raise Exception(f"获取统计信息失败: {str(e)}")
    
    async def complete_maze(
        self,
        maze_id: str,
        user_id: str,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        完成迷宫
        
        Args:
            maze_id: 迷宫ID
            user_id: 用户ID
            completion_data: 完成数据（时间、步数等）
            
        Returns:
            Dict: 完成奖励信息
        """
        try:
            logger.info(f"用户 {user_id} 完成迷宫 {maze_id}")
            
            if not maze_id or not user_id:
                raise ValueError("迷宫ID和用户ID不能为空")
            
            # 获取迷宫
            maze = await self.maze_repo.get_maze(maze_id)
            if not maze:
                raise ValueError("迷宫不存在")
            
            if maze.user_id != user_id:
                raise ValueError("无权限操作此迷宫")
            
            if maze.status == "COMPLETED":
                logger.warning(f"迷宫 {maze_id} 已经完成")
                return {"message": "迷宫已经完成", "rewards": {}}
            
            # 更新迷宫状态
            maze.status = "COMPLETED"
            await self.maze_repo.save_maze(maze)
            
            # 计算奖励
            base_points = maze.difficulty * 10
            time_bonus = max(0, 100 - completion_data.get("time_spent", 0) // 60)  # 时间奖励
            step_bonus = max(0, 50 - completion_data.get("steps_taken", 0) // 10)  # 步数奖励
            
            rewards = {
                "experience_points": base_points + time_bonus + step_bonus,
                "health_points": maze.difficulty * 5,
                "knowledge_points": len(maze.knowledge_nodes) * 2,
                "completion_time": completion_data.get("time_spent", 0),
                "steps_taken": completion_data.get("steps_taken", 0)
            }
            
            # 清除相关缓存
            cache_keys = [
                f"maze:{maze_id}",
                f"user_mazes:{user_id}:*",
                f"maze_stats:{user_id}"
            ]
            for key in cache_keys:
                await self.cache_manager.delete(key)
            
            record_maze_operation("complete", maze.maze_type, maze.difficulty)
            logger.info(f"用户 {user_id} 成功完成迷宫 {maze_id}，获得奖励: {rewards}")
            
            return {
                "message": "恭喜完成迷宫！",
                "rewards": rewards,
                "maze_type": maze.maze_type,
                "difficulty": maze.difficulty
            }
            
        except ValueError as e:
            logger.warning(f"完成迷宫参数错误: {str(e)}")
            record_maze_error("complete", "validation_error")
            raise
        except Exception as e:
            logger.exception(f"完成迷宫时发生错误: {str(e)}")
            record_maze_error("complete", "completion_failed")
            raise Exception(f"完成迷宫失败: {str(e)}")