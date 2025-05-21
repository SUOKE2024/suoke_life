#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import unittest
import requests
import json
import grpc
from unittest.mock import patch

# 添加项目根目录到PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.grpc import medical_pb2
from api.grpc import medical_pb2_grpc

class TestMedicalQueryAPI(unittest.TestCase):
    """医疗查询API集成测试"""

    def setUp(self):
        """测试准备"""
        # 设置测试环境
        self.rest_base_url = os.environ.get('TEST_REST_URL', 'http://localhost:8080')
        self.grpc_host = os.environ.get('TEST_GRPC_HOST', 'localhost')
        self.grpc_port = int(os.environ.get('TEST_GRPC_PORT', '50051'))
        
        # 创建gRPC通道
        self.grpc_channel = grpc.insecure_channel(f'{self.grpc_host}:{self.grpc_port}')
        self.grpc_client = medical_pb2_grpc.MedicalServiceStub(self.grpc_channel)
        
        # 测试数据
        self.test_user_id = str(uuid.uuid4())
        self.test_query_text = "如何缓解偏头痛？"
        self.test_query_id = None  # 将在测试过程中设置

    def tearDown(self):
        """测试清理"""
        # 关闭gRPC通道
        self.grpc_channel.close()
        
        # 清理测试数据
        if self.test_query_id:
            try:
                # 尝试删除创建的测试查询
                requests.delete(f'{self.rest_base_url}/api/medical-queries/{self.test_query_id}')
            except:
                pass

    def test_rest_submit_medical_query(self):
        """测试REST API提交医疗查询"""
        # 构造请求
        payload = {
            'user_id': self.test_user_id,
            'query_text': self.test_query_text,
            'related_symptoms': ['头痛', '恶心'],
            'include_western_medicine': True,
            'include_tcm': True
        }
        
        # 发送请求
        response = requests.post(
            f'{self.rest_base_url}/api/medical-queries', 
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('response_id', data)
        self.assertEqual(data['query_text'], self.test_query_text)
        self.assertIn('answer', data)
        
        # 保存查询ID用于后续测试
        self.test_query_id = data['response_id']

    def test_rest_get_medical_query(self):
        """测试REST API获取医疗查询"""
        # 先创建一个查询
        payload = {
            'user_id': self.test_user_id,
            'query_text': self.test_query_text
        }
        create_response = requests.post(
            f'{self.rest_base_url}/api/medical-queries', 
            json=payload
        )
        self.assertEqual(create_response.status_code, 201)
        self.test_query_id = create_response.json()['response_id']
        
        # 获取查询
        response = requests.get(f'{self.rest_base_url}/api/medical-queries/{self.test_query_id}')
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['response_id'], self.test_query_id)
        self.assertEqual(data['query_text'], self.test_query_text)

    def test_rest_list_user_queries(self):
        """测试REST API获取用户查询列表"""
        # 先创建几个查询
        for i in range(3):
            payload = {
                'user_id': self.test_user_id,
                'query_text': f"测试查询 {i}"
            }
            requests.post(f'{self.rest_base_url}/api/medical-queries', json=payload)
        
        # 获取用户查询列表
        response = requests.get(
            f'{self.rest_base_url}/api/medical-queries/user/{self.test_user_id}',
            params={'page': 1, 'page_size': 10}
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('queries', data)
        self.assertIn('total', data)
        self.assertGreaterEqual(data['total'], 3)
        self.assertGreaterEqual(len(data['queries']), 3)

    def test_rest_delete_medical_query(self):
        """测试REST API删除医疗查询"""
        # 先创建一个查询
        payload = {
            'user_id': self.test_user_id,
            'query_text': self.test_query_text
        }
        create_response = requests.post(
            f'{self.rest_base_url}/api/medical-queries', 
            json=payload
        )
        self.assertEqual(create_response.status_code, 201)
        query_id = create_response.json()['response_id']
        
        # 删除查询
        response = requests.delete(f'{self.rest_base_url}/api/medical-queries/{query_id}')
        
        # 验证响应
        self.assertEqual(response.status_code, 204)
        
        # 验证查询已被删除
        get_response = requests.get(f'{self.rest_base_url}/api/medical-queries/{query_id}')
        self.assertEqual(get_response.status_code, 404)

    @patch('grpc._channel._MultiThreadedRendezvous.code')
    @patch('grpc._channel._MultiThreadedRendezvous.details')
    def test_grpc_submit_medical_query(self, mock_details, mock_code):
        """测试gRPC提交医疗查询"""
        # 配置模拟错误处理
        mock_code.return_value = grpc.StatusCode.OK
        mock_details.return_value = ""
        
        # 构造请求
        request = medical_pb2.SubmitMedicalQueryRequest(
            user_id=self.test_user_id,
            query_text=self.test_query_text,
            related_symptoms=['头痛', '恶心'],
            include_western_medicine=True,
            include_tcm=True
        )
        
        try:
            # 发送请求
            response = self.grpc_client.SubmitMedicalQuery(request)
            
            # 验证响应
            self.assertIsNotNone(response)
            self.assertIsNotNone(response.response_id)
            self.assertEqual(response.query_text, self.test_query_text)
            self.assertIsNotNone(response.answer)
            
            # 保存查询ID用于后续测试
            self.test_query_id = response.response_id
            
        except grpc.RpcError as e:
            self.fail(f"gRPC调用失败: {e.code()}: {e.details()}")

    @patch('grpc._channel._MultiThreadedRendezvous.code')
    @patch('grpc._channel._MultiThreadedRendezvous.details')
    def test_grpc_get_medical_query(self, mock_details, mock_code):
        """测试gRPC获取医疗查询"""
        # 配置模拟错误处理
        mock_code.return_value = grpc.StatusCode.OK
        mock_details.return_value = ""
        
        # 先创建一个查询
        create_request = medical_pb2.SubmitMedicalQueryRequest(
            user_id=self.test_user_id,
            query_text=self.test_query_text
        )
        
        try:
            create_response = self.grpc_client.SubmitMedicalQuery(create_request)
            self.test_query_id = create_response.response_id
            
            # 获取查询
            request = medical_pb2.GetMedicalQueryRequest(
                query_id=self.test_query_id
            )
            response = self.grpc_client.GetMedicalQuery(request)
            
            # 验证响应
            self.assertIsNotNone(response)
            self.assertEqual(response.response_id, self.test_query_id)
            self.assertEqual(response.query_text, self.test_query_text)
            
        except grpc.RpcError as e:
            self.fail(f"gRPC调用失败: {e.code()}: {e.details()}")

    @patch('grpc._channel._MultiThreadedRendezvous.code')
    @patch('grpc._channel._MultiThreadedRendezvous.details')
    def test_grpc_list_medical_queries(self, mock_details, mock_code):
        """测试gRPC获取用户查询列表"""
        # 配置模拟错误处理
        mock_code.return_value = grpc.StatusCode.OK
        mock_details.return_value = ""
        
        # 创建几个查询
        for i in range(3):
            create_request = medical_pb2.SubmitMedicalQueryRequest(
                user_id=self.test_user_id,
                query_text=f"测试查询 {i}"
            )
            self.grpc_client.SubmitMedicalQuery(create_request)
        
        try:
            # 获取用户查询列表
            request = medical_pb2.ListMedicalQueriesRequest(
                user_id=self.test_user_id,
                limit=10,
                offset=0
            )
            response = self.grpc_client.ListMedicalQueriesByUser(request)
            
            # 验证响应
            self.assertIsNotNone(response)
            self.assertGreaterEqual(response.total, 3)
            self.assertGreaterEqual(len(response.queries), 3)
            
        except grpc.RpcError as e:
            self.fail(f"gRPC调用失败: {e.code()}: {e.details()}")

    @patch('grpc._channel._MultiThreadedRendezvous.code')
    @patch('grpc._channel._MultiThreadedRendezvous.details')
    def test_grpc_delete_medical_query(self, mock_details, mock_code):
        """测试gRPC删除医疗查询"""
        # 配置模拟错误处理
        mock_code.return_value = grpc.StatusCode.OK
        mock_details.return_value = ""
        
        # 先创建一个查询
        create_request = medical_pb2.SubmitMedicalQueryRequest(
            user_id=self.test_user_id,
            query_text=self.test_query_text
        )
        
        try:
            create_response = self.grpc_client.SubmitMedicalQuery(create_request)
            query_id = create_response.response_id
            
            # 删除查询
            delete_request = medical_pb2.DeleteMedicalQueryRequest(
                query_id=query_id
            )
            delete_response = self.grpc_client.DeleteMedicalQuery(delete_request)
            
            # 验证响应
            self.assertTrue(delete_response.success)
            
            # 验证查询已被删除
            mock_code.return_value = grpc.StatusCode.NOT_FOUND
            get_request = medical_pb2.GetMedicalQueryRequest(
                query_id=query_id
            )
            with self.assertRaises(grpc.RpcError):
                self.grpc_client.GetMedicalQuery(get_request)
                
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.NOT_FOUND:
                self.fail(f"gRPC调用失败: {e.code()}: {e.details()}")


if __name__ == '__main__':
    unittest.main() 