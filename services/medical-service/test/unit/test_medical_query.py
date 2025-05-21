#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import uuid
from unittest.mock import MagicMock, patch
from datetime import datetime

from internal.model.medical_query import MedicalQuery, SourceReference
from internal.service.medical_query_service import MedicalQueryService
from internal.repository.medical_query_repository import MedicalQueryRepository


class TestMedicalQueryService(unittest.TestCase):
    """医疗查询服务的单元测试"""

    def setUp(self):
        """测试准备"""
        # 模拟依赖服务
        self.mock_rag_service = MagicMock()
        self.mock_med_knowledge_service = MagicMock()
        
        # 模拟存储库
        self.mock_repository = MagicMock(spec=MedicalQueryRepository)
        
        # 模拟服务配置
        self.services_config = {
            'rag': MagicMock(),
            'med_knowledge': MagicMock()
        }
        
        # 创建服务实例
        self.service = MedicalQueryService(self.mock_repository, self.services_config)
        
        # 模拟常用数据
        self.user_id = str(uuid.uuid4())
        self.query_id = str(uuid.uuid4())
        self.query_text = "如何缓解偏头痛？"

    def test_submit_medical_query(self):
        """测试提交医疗查询"""
        # 模拟RAG服务响应
        mock_response = {
            'answer': '偏头痛可以通过休息、按摩太阳穴、避免噪音和强光等方式缓解。如果情况严重，请咨询医生。',
            'sources': [
                {
                    'title': '偏头痛治疗指南',
                    'author': '中国医学会',
                    'publication': '医学杂志',
                    'url': 'https://example.com/migraine',
                    'citation': '《偏头痛治疗指南》，中国医学会，2022年'
                }
            ],
            'follow_up_questions': ['偏头痛的预防措施有哪些？', '什么时候需要就医？']
        }
        
        # 设置模拟行为
        self.mock_rag_service.search_and_generate.return_value = mock_response
        self.service._get_rag_client = MagicMock(return_value=self.mock_rag_service)
        
        # 模拟存储库行为
        self.mock_repository.save_query.return_value = self.query_id
        
        # 调用测试目标
        result = self.service.submit_medical_query(
            user_id=self.user_id,
            query_text=self.query_text,
            related_symptoms=['头痛', '恶心'],
            related_conditions=[''],
            include_western_medicine=True,
            include_tcm=True
        )
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result.query_text, self.query_text)
        self.assertEqual(result.answer, mock_response['answer'])
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(result.sources[0].title, mock_response['sources'][0]['title'])
        
        # 验证服务调用
        self.mock_rag_service.search_and_generate.assert_called_once()
        self.mock_repository.save_query.assert_called_once()

    def test_get_query_by_id(self):
        """测试根据ID获取查询记录"""
        # 创建模拟的医疗查询对象
        mock_query = MedicalQuery(
            id=self.query_id,
            user_id=self.user_id,
            query_text=self.query_text,
            answer="偏头痛可以通过休息、按摩太阳穴等方式缓解。",
            sources=[
                SourceReference(
                    title="偏头痛治疗指南",
                    author="中国医学会",
                    publication="医学杂志",
                    url="https://example.com/migraine",
                    citation="《偏头痛治疗指南》，中国医学会，2022年"
                )
            ],
            is_emergency_advice=False,
            disclaimer="本回答仅供参考，不构成医疗建议。",
            follow_up_questions=["偏头痛的预防措施有哪些？"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 设置模拟行为
        self.mock_repository.get_query_by_id.return_value = mock_query
        
        # 调用测试目标
        result = self.service.get_query_by_id(self.query_id)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.query_id)
        self.assertEqual(result.user_id, self.user_id)
        self.assertEqual(result.query_text, self.query_text)
        self.assertEqual(len(result.sources), 1)
        
        # 验证存储库调用
        self.mock_repository.get_query_by_id.assert_called_once_with(self.query_id)

    def test_get_query_by_id_not_found(self):
        """测试获取不存在的查询记录"""
        # 设置模拟行为
        self.mock_repository.get_query_by_id.return_value = None
        
        # 调用测试目标
        result = self.service.get_query_by_id(self.query_id)
        
        # 验证结果
        self.assertIsNone(result)
        
        # 验证存储库调用
        self.mock_repository.get_query_by_id.assert_called_once_with(self.query_id)

    def test_list_queries_by_user(self):
        """测试获取用户的查询历史记录"""
        # 创建模拟的医疗查询对象列表
        mock_queries = [
            MedicalQuery(
                id=str(uuid.uuid4()),
                user_id=self.user_id,
                query_text="如何缓解偏头痛？",
                answer="偏头痛可以通过休息、按摩太阳穴等方式缓解。",
                sources=[],
                is_emergency_advice=False,
                disclaimer="本回答仅供参考，不构成医疗建议。",
                follow_up_questions=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            MedicalQuery(
                id=str(uuid.uuid4()),
                user_id=self.user_id,
                query_text="感冒了怎么办？",
                answer="感冒可以多喝水，休息，如果有发热可以服用退烧药。",
                sources=[],
                is_emergency_advice=False,
                disclaimer="本回答仅供参考，不构成医疗建议。",
                follow_up_questions=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        # 设置模拟行为
        self.mock_repository.list_queries_by_user.return_value = mock_queries
        
        # 调用测试目标
        limit = 10
        offset = 0
        results = self.service.list_queries_by_user(self.user_id, limit, offset)
        
        # 验证结果
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].user_id, self.user_id)
        
        # 验证存储库调用
        self.mock_repository.list_queries_by_user.assert_called_once_with(self.user_id, limit, offset)

    def test_search_queries(self):
        """测试搜索用户的查询历史记录"""
        # 创建模拟的医疗查询对象列表
        mock_queries = [
            MedicalQuery(
                id=str(uuid.uuid4()),
                user_id=self.user_id,
                query_text="如何缓解偏头痛？",
                answer="偏头痛可以通过休息、按摩太阳穴等方式缓解。",
                sources=[],
                is_emergency_advice=False,
                disclaimer="本回答仅供参考，不构成医疗建议。",
                follow_up_questions=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        # 设置模拟行为
        self.mock_repository.search_queries.return_value = mock_queries
        
        # 调用测试目标
        keyword = "偏头痛"
        limit = 10
        offset = 0
        results = self.service.search_queries(self.user_id, keyword, limit, offset)
        
        # 验证结果
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 1)
        self.assertTrue("偏头痛" in results[0].query_text)
        
        # 验证存储库调用
        self.mock_repository.search_queries.assert_called_once_with(self.user_id, keyword, limit, offset)

    def test_delete_query(self):
        """测试删除查询记录"""
        # 设置模拟行为
        self.mock_repository.delete_query.return_value = True
        
        # 调用测试目标
        result = self.service.delete_query(self.query_id)
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证存储库调用
        self.mock_repository.delete_query.assert_called_once_with(self.query_id)

    def test_delete_query_not_found(self):
        """测试删除不存在的查询记录"""
        # 设置模拟行为
        self.mock_repository.delete_query.return_value = False
        
        # 调用测试目标
        result = self.service.delete_query(self.query_id)
        
        # 验证结果
        self.assertFalse(result)
        
        # 验证存储库调用
        self.mock_repository.delete_query.assert_called_once_with(self.query_id)

    def test_get_query_count_by_user(self):
        """测试获取用户的查询记录总数"""
        # 设置模拟行为
        expected_count = 5
        self.mock_repository.get_query_count_by_user.return_value = expected_count
        
        # 调用测试目标
        count = self.service.get_query_count_by_user(self.user_id)
        
        # 验证结果
        self.assertEqual(count, expected_count)
        
        # 验证存储库调用
        self.mock_repository.get_query_count_by_user.assert_called_once_with(self.user_id)


if __name__ == '__main__':
    unittest.main() 