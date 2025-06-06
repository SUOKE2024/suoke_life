"""
community_service - 索克生活项目模块
"""

from datetime import datetime
from internal.repository.community_repository import CommunityRepository
from loguru import logger
from pkg.utils.metrics import get_metrics_collector
from typing import Any
import uuid

#!/usr/bin/env python

"""
老克智能体服务 - 社区服务
提供社区内容管理功能
"""




metrics = get_metrics_collector()

class CommunityService:
    """社区服务，提供社区内容管理功能"""

    def __init__(self, repository: CommunityRepository):
        """
        初始化社区服务

        Args:
            repository: 社区内容存储库
        """
        self.repository = repository
        logger.info("社区服务已初始化")

    @metrics.measure_execution_time("community_service_get_featured_posts")
    async def get_featured_posts(self, limit: int = 5, offset: int = 0) -> list[dict[str, Any]]:
        """
        获取精选社区帖子

        Args:
            limit: 返回记录数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 精选帖子列表
        """
        logger.debug(f"获取精选社区帖子，limit={limit}, offset={offset}")

        try:
            posts = await self.repository.find_featured_posts(limit, offset)
            return posts
        except Exception as e:
            logger.error(f"获取精选社区帖子失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "get_featured_posts"})
            return []

    @metrics.measure_execution_time("community_service_get_posts")
    async def get_posts(self,
                        category: str | None = None,
                        tags: list[str] | None = None,
                        author_id: str | None = None,
                        limit: int = 10,
                        offset: int = 0,
                        sort_by: str = "created_at",
                        sort_order: str = "desc") -> list[dict[str, Any]]:
        """
        获取社区帖子列表

        Args:
            category: 过滤的分类名称
            tags: 过滤的标签列表
            author_id: 筛选特定作者的帖子
            limit: 返回记录数量限制
            offset: 分页偏移量
            sort_by: 排序字段
            sort_order: 排序顺序 (asc 或 desc)

        Returns:
            List[Dict[str, Any]]: 社区帖子列表
        """
        logger.debug(f"获取社区帖子，category={category}, tags={tags}, author_id={author_id}, limit={limit}, offset={offset}")

        try:
            posts = await self.repository.find_posts(
                category=category,
                tags=tags,
                author_id=author_id,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
            return posts
        except Exception as e:
            logger.error(f"获取社区帖子失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "get_posts"})
            return []

    @metrics.measure_execution_time("community_service_get_post_by_id")
    async def get_post_by_id(self, post_id: str) -> dict[str, Any] | None:
        """
        根据ID获取社区帖子详情

        Args:
            post_id: 帖子ID

        Returns:
            Optional[Dict[str, Any]]: 帖子详情，未找到时返回None
        """
        logger.debug(f"获取社区帖子详情，post_id={post_id}")

        try:
            post = await self.repository.find_post_by_id(post_id)
            return post
        except Exception as e:
            logger.error(f"获取社区帖子详情失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "get_post_by_id"})
            return None

    @metrics.measure_execution_time("community_service_create_post")
    async def create_post(self,
                          title: str,
                          content: str,
                          author_id: str,
                          category: str,
                          tags: list[str] | None = None) -> dict[str, Any] | None:
        """
        创建社区帖子

        Args:
            title: 帖子标题
            content: 帖子内容
            author_id: 作者用户ID
            category: 帖子分类
            tags: 帖子标签列表

        Returns:
            Optional[Dict[str, Any]]: 创建成功的帖子详情，失败时返回None
        """
        logger.debug(f"创建社区帖子，author_id={author_id}, title={title}, category={category}")

        try:
            # 创建帖子数据
            post_data = {
                "title": title,
                "content": content,
                "author_id": author_id,
                "category": category,
                "tags": tags or [],
                "created_at": datetime.utcnow().isoformat(),
                "like_count": 0,
                "comment_count": 0,
                "comments": [],
                "is_featured": False
            }

            # 保存帖子
            post_id = await self.repository.create_post(post_data)

            if post_id:
                # 获取完整的帖子信息
                return await self.get_post_by_id(post_id)

            return None
        except Exception as e:
            logger.error(f"创建社区帖子失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "create_post"})
            return None

    @metrics.measure_execution_time("community_service_update_post")
    async def update_post(self,
                          post_id: str,
                          title: str | None = None,
                          content: str | None = None,
                          category: str | None = None,
                          tags: list[str] | None = None,
                          is_featured: bool | None = None) -> dict[str, Any] | None:
        """
        更新社区帖子

        Args:
            post_id: 帖子ID
            title: 更新的标题
            content: 更新的内容
            category: 更新的分类
            tags: 更新的标签列表
            is_featured: 是否设为精选

        Returns:
            Optional[Dict[str, Any]]: 更新后的帖子详情，失败时返回None
        """
        logger.debug(f"更新社区帖子，post_id={post_id}")

        try:
            # 获取当前帖子
            post = await self.repository.find_post_by_id(post_id)
            if not post:
                logger.warning(f"未找到要更新的帖子: {post_id}")
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
            if is_featured is not None:
                update_data["is_featured"] = is_featured

            if not update_data:
                logger.debug("无需更新的字段，返回原帖子")
                return post

            # 更新帖子
            success = await self.repository.update_post(post_id, update_data)

            if success:
                # 获取更新后的帖子信息
                return await self.get_post_by_id(post_id)

            return None
        except Exception as e:
            logger.error(f"更新社区帖子失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "update_post"})
            return None

    @metrics.measure_execution_time("community_service_delete_post")
    async def delete_post(self, post_id: str) -> bool:
        """
        删除社区帖子

        Args:
            post_id: 帖子ID

        Returns:
            bool: 是否删除成功
        """
        logger.debug(f"删除社区帖子，post_id={post_id}")

        try:
            # 删除帖子
            success = await self.repository.delete_post(post_id)
            return success
        except Exception as e:
            logger.error(f"删除社区帖子失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "delete_post"})
            return False

    @metrics.measure_execution_time("community_service_add_comment")
    async def add_comment(self,
                          post_id: str,
                          author_id: str,
                          content: str) -> tuple[bool, dict[str, Any] | None]:
        """
        添加评论到社区帖子

        Args:
            post_id: 帖子ID
            author_id: 评论作者用户ID
            content: 评论内容

        Returns:
            Tuple[bool, Optional[Dict[str, Any]]]:
                - 是否添加成功
                - 添加的评论信息，失败时为None
        """
        logger.debug(f"添加评论，post_id={post_id}, author_id={author_id}")

        try:
            # 获取当前帖子
            post = await self.repository.find_post_by_id(post_id)
            if not post:
                logger.warning(f"未找到要评论的帖子: {post_id}")
                return False, None

            # 创建评论数据
            comment = {
                "id": str(uuid.uuid4()),
                "author_id": author_id,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
                "like_count": 0
            }

            # 添加评论
            success = await self.repository.add_comment(post_id, comment)

            if success:
                # 更新评论计数
                await self.repository.update_post(
                    post_id,
                    {"comment_count": post.get("comment_count", 0) + 1}
                )
                return True, comment

            return False, None
        except Exception as e:
            logger.error(f"添加评论失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "add_comment"})
            return False, None

    @metrics.measure_execution_time("community_service_like_post")
    async def like_post(self, post_id: str, user_id: str) -> bool:
        """
        点赞社区帖子

        Args:
            post_id: 帖子ID
            user_id: 点赞用户ID

        Returns:
            bool: 是否点赞成功
        """
        logger.debug(f"点赞帖子，post_id={post_id}, user_id={user_id}")

        try:
            # 获取当前帖子
            post = await self.repository.find_post_by_id(post_id)
            if not post:
                logger.warning(f"未找到要点赞的帖子: {post_id}")
                return False

            # 记录点赞并更新计数
            success = await self.repository.add_like(post_id, user_id)

            if success:
                # 增加点赞计数
                await self.repository.update_post(
                    post_id,
                    {"like_count": post.get("like_count", 0) + 1}
                )

            return success
        except Exception as e:
            logger.error(f"点赞帖子失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "like_post"})
            return False

    @metrics.measure_execution_time("community_service_get_categories")
    async def get_categories(self) -> list[str]:
        """
        获取所有社区帖子分类

        Returns:
            List[str]: 分类列表
        """
        logger.debug("获取社区帖子分类")

        try:
            categories = await self.repository.get_categories()
            return categories
        except Exception as e:
            logger.error(f"获取社区帖子分类失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "get_categories"})
            return []

    @metrics.measure_execution_time("community_service_get_popular_tags")
    async def get_popular_tags(self, limit: int = 20) -> list[dict[str, Any]]:
        """
        获取热门标签

        Args:
            limit: 返回标签数量

        Returns:
            List[Dict[str, Any]]: 标签列表，包含标签名和使用计数
        """
        logger.debug(f"获取热门标签，limit={limit}")

        try:
            tags = await self.repository.get_popular_tags(limit)
            return tags
        except Exception as e:
            logger.error(f"获取热门标签失败: {str(e)}")
            metrics.increment_counter("community_service_errors", {"method": "get_popular_tags"})
            return []
