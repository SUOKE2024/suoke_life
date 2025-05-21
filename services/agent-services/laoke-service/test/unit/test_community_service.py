#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
社区服务单元测试
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from datetime import datetime

# 添加项目根路径到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from internal.community.community_service import CommunityService


class TestCommunityService(unittest.TestCase):
    """社区服务单元测试类"""

    def setUp(self):
        """测试前初始化"""
        # 模拟配置
        self.mock_config = {
            'community': {
                'moderation': {
                    'enabled': True,
                    'auto_moderate': True,
                    'moderation_model': 'content-filter-alpha'
                },
                'post_types': ['article', 'question', 'discussion'],
                'content_categories': [
                    '中医基础',
                    '经络穴位',
                    '中药知识',
                    '食养食疗',
                    '四季养生'
                ]
            }
        }
        
        # 模拟存储库
        self.mock_repository = MagicMock()
        self.mock_repository.get_post_by_id = AsyncMock()
        self.mock_repository.get_posts = AsyncMock()
        self.mock_repository.create_post = AsyncMock()
        self.mock_repository.update_post = AsyncMock()
        self.mock_repository.add_comment = AsyncMock()
        self.mock_repository.get_trending_posts = AsyncMock()
        
        # 模拟内容审核器
        self.mock_moderator = MagicMock()
        self.mock_moderator.moderate_content = AsyncMock()
        
        # 初始化社区服务
        with patch('internal.community.community_service.Config', return_value=self.mock_config):
            self.community_service = CommunityService()
            self.community_service.repository = self.mock_repository
            self.community_service._content_moderator = self.mock_moderator

    @pytest.mark.asyncio
    async def test_get_post_by_id(self):
        """测试通过ID获取帖子"""
        # 设置模拟返回值
        mock_post = {
            'id': '123',
            'title': '分享我的艾灸经验',
            'content': '最近尝试了艾灸疗法，效果很好...',
            'author': {
                'id': 'user_1',
                'username': 'healthmaster',
                'displayName': '健康达人'
            },
            'category': '四季养生',
            'tags': ['艾灸', '经验分享', '冬季养生'],
            'created_at': '2023-11-10T08:15:30Z',
            'updated_at': None,
            'like_count': 24,
            'comment_count': 5
        }
        self.mock_repository.get_post_by_id.return_value = mock_post
        
        # 调用被测试的方法
        result = await self.community_service.get_post_by_id('123')
        
        # 断言
        assert result == mock_post
        self.mock_repository.get_post_by_id.assert_called_once_with('123')

    @pytest.mark.asyncio
    async def test_create_post_with_moderation(self):
        """测试创建带审核的帖子"""
        # 设置模拟数据
        post_data = {
            'title': '如何利用中医调理感冒',
            'content': '冬季感冒多发，可以采用以下中医方法调理...',
            'author_id': 'user_1',
            'category': '中医基础',
            'tags': ['感冒', '调理', '冬季']
        }
        
        # 模拟用户信息
        mock_author = {
            'id': 'user_1',
            'username': 'healthmaster',
            'displayName': '健康达人',
            'role': 'CONTRIBUTOR'
        }
        
        # 设置模拟返回值 - 获取用户
        mock_user_service = MagicMock()
        mock_user_service.get_user_by_id = AsyncMock(return_value=mock_author)
        self.community_service._user_service = mock_user_service
        
        # 设置模拟返回值 - 审核内容
        self.mock_moderator.moderate_content.return_value = {
            'is_approved': True,
            'violation_types': [],
            'moderation_level': 'auto_approved',
            'confidence_score': 0.95
        }
        
        # 设置模拟返回值 - 创建帖子
        mock_created_post = {
            'id': '456',
            'title': post_data['title'],
            'content': post_data['content'],
            'author': mock_author,
            'category': post_data['category'],
            'tags': post_data['tags'],
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'updated_at': None,
            'like_count': 0,
            'comment_count': 0,
            'is_featured': False,
            'moderation_status': 'approved'
        }
        self.mock_repository.create_post.return_value = mock_created_post
        
        # 调用被测试的方法
        result = await self.community_service.create_post(post_data)
        
        # 断言
        assert result['id'] == '456'
        assert result['title'] == '如何利用中医调理感冒'
        assert result['moderation_status'] == 'approved'
        self.mock_moderator.moderate_content.assert_called_once()
        self.mock_repository.create_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_post_rejected_by_moderation(self):
        """测试创建被审核拒绝的帖子"""
        # 设置模拟数据
        post_data = {
            'title': '问题标题',
            'content': '包含违规内容的帖子...',
            'author_id': 'user_1',
            'category': '中医基础',
            'tags': ['问题']
        }
        
        # 模拟用户信息
        mock_author = {
            'id': 'user_1',
            'username': 'healthmaster',
            'displayName': '健康达人',
            'role': 'CONTRIBUTOR'
        }
        
        # 设置模拟返回值 - 获取用户
        mock_user_service = MagicMock()
        mock_user_service.get_user_by_id = AsyncMock(return_value=mock_author)
        self.community_service._user_service = mock_user_service
        
        # 设置模拟返回值 - 审核内容
        self.mock_moderator.moderate_content.return_value = {
            'is_approved': False,
            'violation_types': ['inappropriate_content'],
            'moderation_level': 'auto_rejected',
            'confidence_score': 0.92
        }
        
        # 调用被测试的方法
        with pytest.raises(ValueError) as excinfo:
            await self.community_service.create_post(post_data)
        
        # 断言
        assert "内容未通过审核" in str(excinfo.value)
        self.mock_moderator.moderate_content.assert_called_once()
        self.mock_repository.create_post.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_comment(self):
        """测试添加评论"""
        # 设置模拟数据
        post_id = "123"
        comment_data = {
            'content': '这篇文章很有帮助，谢谢分享！',
            'author_id': 'user_2'
        }
        
        # 模拟帖子和用户
        mock_post = {
            'id': '123',
            'title': '分享我的艾灸经验',
            'comment_count': 5
        }
        
        mock_author = {
            'id': 'user_2',
            'username': 'tcm_lover',
            'displayName': '中医爱好者'
        }
        
        # 设置模拟返回值
        self.mock_repository.get_post_by_id.return_value = mock_post
        
        mock_user_service = MagicMock()
        mock_user_service.get_user_by_id = AsyncMock(return_value=mock_author)
        self.community_service._user_service = mock_user_service
        
        # 模拟审核
        self.mock_moderator.moderate_content.return_value = {
            'is_approved': True,
            'violation_types': [],
            'moderation_level': 'auto_approved',
            'confidence_score': 0.98
        }
        
        # 模拟创建评论
        mock_comment = {
            'id': 'comment_1',
            'content': comment_data['content'],
            'author': mock_author,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'like_count': 0
        }
        self.mock_repository.add_comment.return_value = mock_comment
        
        # 调用被测试的方法
        result = await self.community_service.add_comment(post_id, comment_data)
        
        # 断言
        assert result['id'] == 'comment_1'
        assert result['content'] == '这篇文章很有帮助，谢谢分享！'
        self.mock_repository.get_post_by_id.assert_called_once_with(post_id)
        self.mock_moderator.moderate_content.assert_called_once()
        self.mock_repository.add_comment.assert_called_once()
        self.mock_repository.update_post.assert_called_once()  # 更新评论计数

    @pytest.mark.asyncio
    async def test_get_trending_posts(self):
        """测试获取热门帖子"""
        # 设置模拟返回值
        mock_trending_posts = [
            {
                'id': '123',
                'title': '如何利用中医调理感冒',
                'category': '中医基础',
                'view_count': 320,
                'like_count': 45,
                'comment_count': 12,
                'trending_score': 0.95
            },
            {
                'id': '456',
                'title': '冬季养生指南',
                'category': '四季养生',
                'view_count': 280,
                'like_count': 39,
                'comment_count': 8,
                'trending_score': 0.85
            }
        ]
        self.mock_repository.get_trending_posts.return_value = mock_trending_posts
        
        # 调用被测试的方法
        results = await self.community_service.get_trending_posts(time_window_hours=24, limit=5)
        
        # 断言
        assert len(results) == 2
        assert results[0]['id'] == '123'
        assert results[0]['trending_score'] == 0.95
        assert results[1]['id'] == '456'
        self.mock_repository.get_trending_posts.assert_called_once_with(
            time_window_hours=24,
            limit=5,
            category=None
        )


if __name__ == '__main__':
    unittest.main() 