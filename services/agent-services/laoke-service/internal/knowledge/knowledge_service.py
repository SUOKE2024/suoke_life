#!/usr/bin/env python

"""
老克智能体服务 - 知识服务
提供知识内容管理和学习路径功能
"""

import logging
from datetime import datetime
from typing import Any

from internal.repository.knowledge_repository import KnowledgeRepository
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

class KnowledgeService:
    """知识服务，提供知识内容管理和学习路径功能"""

    def __init__(self, repository: KnowledgeRepository):
        """
        初始化知识服务

        Args:
            repository: 知识内容存储库
        """
        self.repository = repository
        logger.info("知识服务已初始化")

    @metrics.measure_execution_time("knowledge_service_get_article")
    async def get_article(self, article_id: str) -> dict[str, Any] | None:
        """
        获取知识文章详情

        Args:
            article_id: 文章ID

        Returns:
            Optional[Dict[str, Any]]: 文章详情，未找到时返回None
        """
        logger.debug(f"获取知识文章，article_id={article_id}")

        try:
            article = await self.repository.find_article_by_id(article_id)
            # 增加浏览次数
            if article:
                await self.repository.increment_article_view_count(article_id)
            return article
        except Exception as e:
            logger.error(f"获取知识文章失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "get_article"})
            return None

    @metrics.measure_execution_time("knowledge_service_get_articles")
    async def get_articles(self,
                           category: str | None = None,
                           tags: list[str] | None = None,
                           difficulty: str | None = None,
                           limit: int = 10,
                           offset: int = 0,
                           sort_by: str = "created_at",
                           sort_order: str = "desc") -> list[dict[str, Any]]:
        """
        获取知识文章列表

        Args:
            category: 过滤的分类名称
            tags: 过滤的标签列表
            difficulty: 难度级别
            limit: 返回记录数量限制
            offset: 分页偏移量
            sort_by: 排序字段
            sort_order: 排序顺序 (asc 或 desc)

        Returns:
            List[Dict[str, Any]]: 知识文章列表
        """
        logger.debug(f"获取知识文章列表，category={category}, tags={tags}, difficulty={difficulty}")

        try:
            articles = await self.repository.find_articles(
                category=category,
                tags=tags,
                difficulty=difficulty,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
            return articles
        except Exception as e:
            logger.error(f"获取知识文章列表失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "get_articles"})
            return []

    @metrics.measure_execution_time("knowledge_service_search_articles")
    async def search_articles(self, query: str, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """
        搜索知识文章

        Args:
            query: 搜索查询文本
            limit: 返回记录数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 符合搜索条件的文章列表
        """
        logger.debug(f"搜索知识文章，query={query}")

        try:
            articles = await self.repository.search_articles(
                query=query,
                limit=limit,
                offset=offset
            )
            return articles
        except Exception as e:
            logger.error(f"搜索知识文章失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "search_articles"})
            return []

    @metrics.measure_execution_time("knowledge_service_get_related_articles")
    async def get_related_articles(self, article_id: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        获取相关文章

        Args:
            article_id: 文章ID
            limit: 返回记录数量限制

        Returns:
            List[Dict[str, Any]]: 相关文章列表
        """
        logger.debug(f"获取相关文章，article_id={article_id}")

        try:
            # 获取当前文章
            article = await self.repository.find_article_by_id(article_id)
            if not article:
                return []

            # 获取相关文章
            related_articles = await self.repository.find_related_articles(
                article_id=article_id,
                tags=article.get("tags", []),
                category=article.get("category"),
                limit=limit
            )
            return related_articles
        except Exception as e:
            logger.error(f"获取相关文章失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "get_related_articles"})
            return []

    @metrics.measure_execution_time("knowledge_service_create_article")
    async def create_article(self,
                            title: str,
                            content: str,
                            category: str,
                            author_id: str,
                            tags: list[str] | None = None,
                            difficulty: str = "INTERMEDIATE",
                            resources: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
        """
        创建知识文章

        Args:
            title: 文章标题
            content: 文章内容
            category: 文章分类
            author_id: 作者ID
            tags: 标签列表
            difficulty: 难度级别
            resources: 相关资源列表

        Returns:
            Optional[Dict[str, Any]]: 创建成功的文章详情，失败时返回None
        """
        logger.debug(f"创建知识文章，title={title}, category={category}")

        try:
            # 创建文章数据
            article_data = {
                "title": title,
                "content": content,
                "category": category,
                "author_id": author_id,
                "tags": tags or [],
                "difficulty": difficulty,
                "resources": resources or [],
                "created_at": datetime.utcnow().isoformat(),
                "view_count": 0,
                "rating": 0,
                "rating_count": 0
            }

            # 保存文章
            article_id = await self.repository.create_article(article_data)

            if article_id:
                # 获取完整的文章信息
                return await self.get_article(article_id)

            return None
        except Exception as e:
            logger.error(f"创建知识文章失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "create_article"})
            return None

    @metrics.measure_execution_time("knowledge_service_update_article")
    async def update_article(self,
                            article_id: str,
                            title: str | None = None,
                            content: str | None = None,
                            category: str | None = None,
                            tags: list[str] | None = None,
                            difficulty: str | None = None,
                            resources: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
        """
        更新知识文章

        Args:
            article_id: 文章ID
            title: 更新的标题
            content: 更新的内容
            category: 更新的分类
            tags: 更新的标签列表
            difficulty: 更新的难度级别
            resources: 更新的相关资源列表

        Returns:
            Optional[Dict[str, Any]]: 更新后的文章详情，失败时返回None
        """
        logger.debug(f"更新知识文章，article_id={article_id}")

        try:
            # 获取当前文章
            article = await self.repository.find_article_by_id(article_id)
            if not article:
                logger.warning(f"未找到要更新的文章: {article_id}")
                return None

            # 准备更新数据
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if content is not None:
                update_data["content"] = content
            if category is not None:
                update_data["category"] = category
            if tags is not None:
                update_data["tags"] = tags
            if difficulty is not None:
                update_data["difficulty"] = difficulty
            if resources is not None:
                update_data["resources"] = resources

            if not update_data:
                logger.debug("无需更新的字段，返回原文章")
                return article

            # 更新文章
            success = await self.repository.update_article(article_id, update_data)

            if success:
                # 获取更新后的文章信息
                return await self.get_article(article_id)

            return None
        except Exception as e:
            logger.error(f"更新知识文章失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "update_article"})
            return None

    @metrics.measure_execution_time("knowledge_service_rate_article")
    async def rate_article(self, article_id: str, rating: float) -> bool:
        """
        对文章进行评分

        Args:
            article_id: 文章ID
            rating: 评分 (1-5)

        Returns:
            bool: 是否评分成功
        """
        logger.debug(f"对知识文章评分，article_id={article_id}, rating={rating}")

        try:
            # 验证评分范围
            if rating < 1 or rating > 5:
                logger.warning(f"评分超出范围 (1-5): {rating}")
                return False

            # 获取当前文章
            article = await self.repository.find_article_by_id(article_id)
            if not article:
                logger.warning(f"未找到要评分的文章: {article_id}")
                return False

            # 计算新的平均评分
            current_rating = article.get("rating", 0)
            current_count = article.get("rating_count", 0)

            new_count = current_count + 1
            new_rating = ((current_rating * current_count) + rating) / new_count

            # 更新评分
            update_data = {
                "rating": round(new_rating, 2),
                "rating_count": new_count
            }

            # 保存更新
            success = await self.repository.update_article(article_id, update_data)
            return success
        except Exception as e:
            logger.error(f"对文章评分失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "rate_article"})
            return False

    @metrics.measure_execution_time("knowledge_service_get_learning_path")
    async def get_learning_path(self, path_id: str) -> dict[str, Any] | None:
        """
        获取学习路径详情

        Args:
            path_id: 学习路径ID

        Returns:
            Optional[Dict[str, Any]]: 学习路径详情，未找到时返回None
        """
        logger.debug(f"获取学习路径，path_id={path_id}")

        try:
            path = await self.repository.find_learning_path_by_id(path_id)
            return path
        except Exception as e:
            logger.error(f"获取学习路径失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "get_learning_path"})
            return None

    @metrics.measure_execution_time("knowledge_service_get_learning_paths")
    async def get_learning_paths(self,
                                category: str | None = None,
                                level: str | None = None,
                                limit: int = 10,
                                offset: int = 0) -> list[dict[str, Any]]:
        """
        获取学习路径列表

        Args:
            category: 过滤的分类名称
            level: 过滤的难度级别
            limit: 返回记录数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 学习路径列表
        """
        logger.debug(f"获取学习路径列表，category={category}, level={level}")

        try:
            paths = await self.repository.find_learning_paths(
                category=category,
                level=level,
                limit=limit,
                offset=offset
            )
            return paths
        except Exception as e:
            logger.error(f"获取学习路径列表失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "get_learning_paths"})
            return []

    @metrics.measure_execution_time("knowledge_service_get_user_progress")
    async def get_user_progress(self, user_id: str, path_id: str) -> dict[str, Any]:
        """
        获取用户在特定学习路径上的进度

        Args:
            user_id: 用户ID
            path_id: 学习路径ID

        Returns:
            Dict[str, Any]: 用户进度信息
        """
        logger.debug(f"获取用户学习进度，user_id={user_id}, path_id={path_id}")

        try:
            progress = await self.repository.get_user_learning_progress(user_id, path_id)
            return progress
        except Exception as e:
            logger.error(f"获取用户学习进度失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "get_user_progress"})
            return {
                "user_id": user_id,
                "path_id": path_id,
                "completed_modules": [],
                "current_module_id": None,
                "progress_percentage": 0,
                "started_at": None,
                "last_activity_at": None
            }

    @metrics.measure_execution_time("knowledge_service_update_user_progress")
    async def update_user_progress(self,
                                 user_id: str,
                                 path_id: str,
                                 module_id: str,
                                 completed: bool) -> bool:
        """
        更新用户在特定学习路径上的进度

        Args:
            user_id: 用户ID
            path_id: 学习路径ID
            module_id: 模块ID
            completed: 是否已完成该模块

        Returns:
            bool: 是否更新成功
        """
        logger.debug(f"更新用户学习进度，user_id={user_id}, path_id={path_id}, module_id={module_id}, completed={completed}")

        try:
            # 获取学习路径信息
            path = await self.repository.find_learning_path_by_id(path_id)
            if not path:
                logger.warning(f"未找到学习路径: {path_id}")
                return False

            # 验证模块是否存在
            module_exists = False
            modules = path.get("modules", [])
            for module in modules:
                if module.get("id") == module_id:
                    module_exists = True
                    break

            if not module_exists:
                logger.warning(f"未找到模块: {module_id} in path {path_id}")
                return False

            # 获取当前用户进度
            progress = await self.repository.get_user_learning_progress(user_id, path_id)

            # 准备更新数据
            now = datetime.utcnow().isoformat()

            # 如果是新的进度记录
            if not progress or not progress.get("started_at"):
                progress = {
                    "user_id": user_id,
                    "path_id": path_id,
                    "completed_modules": [module_id] if completed else [],
                    "current_module_id": module_id,
                    "progress_percentage": (1 / len(modules) * 100) if completed else 0,
                    "started_at": now,
                    "last_activity_at": now
                }
            else:
                # 更新已有进度记录
                completed_modules = progress.get("completed_modules", [])

                # 如果模块完成，添加到已完成列表
                if completed and module_id not in completed_modules:
                    completed_modules.append(module_id)
                # 如果模块未完成，从已完成列表中移除
                elif not completed and module_id in completed_modules:
                    completed_modules.remove(module_id)

                # 更新进度百分比
                progress_percentage = (len(completed_modules) / len(modules) * 100)

                # 确定当前模块
                current_module_id = module_id
                if len(completed_modules) == len(modules):
                    # 全部完成
                    current_module_id = None
                elif not completed and len(modules) > 0:
                    # 未完成的情况，使用当前模块
                    current_module_id = module_id
                else:
                    # 完成部分模块，找出下一个未完成的模块
                    for _i, module in enumerate(modules):
                        if module.get("id") not in completed_modules:
                            current_module_id = module.get("id")
                            break

                # 更新数据
                progress = {
                    "completed_modules": completed_modules,
                    "current_module_id": current_module_id,
                    "progress_percentage": round(progress_percentage, 2),
                    "last_activity_at": now
                }

            # 保存进度
            success = await self.repository.update_user_learning_progress(user_id, path_id, progress)

            # 更新学习路径统计
            if success:
                # 计算完成率变化
                await self._update_learning_path_stats(path_id)

            return success
        except Exception as e:
            logger.error(f"更新用户学习进度失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "update_user_progress"})
            return False

    async def _update_learning_path_stats(self, path_id: str) -> None:
        """
        更新学习路径统计信息

        Args:
            path_id: 学习路径ID
        """
        try:
            # 获取该路径的所有用户进度
            all_progress = await self.repository.get_all_user_progress_for_path(path_id)

            # 计算完成率
            completed_count = 0
            total_count = len(all_progress)

            for progress in all_progress:
                if progress.get("progress_percentage", 0) >= 100:
                    completed_count += 1

            # 计算完成率
            completion_rate = 0 if total_count == 0 else (completed_count / total_count)

            # 更新学习路径统计
            stats_update = {
                "enrolled_users": total_count,
                "completion_rate": round(completion_rate, 2)
            }

            # 保存统计
            await self.repository.update_learning_path(path_id, stats_update)
        except Exception as e:
            logger.error(f"更新学习路径统计失败: {str(e)}")
            metrics.increment_counter("knowledge_service_errors", {"method": "_update_learning_path_stats"})
