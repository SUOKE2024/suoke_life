#!/usr/bin/env python3
"""
消息总线服务集成测试
"""
import os
import sys
import asyncio
import logging
import unittest
import json
from typing import Dict, Any, List, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pkg.client.message_bus_client import MessageBusClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试配置
TEST_ENDPOINT = os.getenv("TEST_ENDPOINT", "localhost:50051")
TEST_AUTH_TOKEN = os.getenv("TEST_AUTH_TOKEN", None)

class IntegrationTest(unittest.IsolatedAsyncioTestCase):
    """消息总线服务集成测试"""
    
    async def asyncSetUp(self):
        """测试准备"""
        self.client = MessageBusClient(
            endpoint=TEST_ENDPOINT,
            auth_token=TEST_AUTH_TOKEN,
            timeout=10
        )
        
        # 接收到的消息列表
        self.received_messages = []
        
        # 测试主题
        self.test_topic = f"integration-test-{int(asyncio.get_event_loop().time())}"
        
        # 创建测试主题
        try:
            topic_info = self.client.create_topic(
                name=self.test_topic,
                description="集成测试主题",
                partition_count=1,
                retention_hours=1
            )
            logger.info(f"创建测试主题: {topic_info['name']}")
        except Exception as e:
            logger.error(f"创建测试主题失败: {str(e)}")
            raise
    
    async def asyncTearDown(self):
        """测试清理"""
        # 删除测试主题
        try:
            if hasattr(self, 'test_topic'):
                success = self.client.delete_topic(self.test_topic)
                logger.info(f"删除测试主题: {self.test_topic}, 成功: {success}")
        except Exception as e:
            logger.warning(f"删除测试主题失败: {str(e)}")
        
        # 关闭客户端
        if hasattr(self, 'client'):
            self.client.close()
    
    async def message_handler(self, message: Dict[str, Any]):
        """消息处理回调"""
        logger.info(f"收到消息: {message['id']}")
        self.received_messages.append(message)
    
    async def test_publish_and_subscribe(self):
        """测试消息发布和订阅"""
        # 订阅主题
        subscription = self.client.subscribe(
            topic=self.test_topic,
            callback=self.message_handler
        )
        
        # 等待一下，确保订阅已建立
        await asyncio.sleep(1)
        
        # 发布测试消息
        test_payload = {"test": "data", "value": 123}
        test_attributes = {"priority": "high", "source": "integration-test"}
        
        # 发布消息
        result = self.client.publish(
            topic=self.test_topic,
            payload=test_payload,
            attributes=test_attributes
        )
        
        logger.info(f"发布消息: {result['message_id']}")
        
        # 等待接收消息
        retry_count = 0
        while len(self.received_messages) == 0 and retry_count < 10:
            await asyncio.sleep(1)
            retry_count += 1
        
        # 取消订阅
        subscription.unsubscribe()
        
        # 验证已接收到消息
        self.assertGreater(len(self.received_messages), 0, "未接收到消息")
        
        # 验证消息内容
        message = self.received_messages[0]
        payload = json.loads(message["payload"].decode('utf-8'))
        
        self.assertEqual(payload, test_payload, "消息内容不匹配")
        
        # 验证消息属性
        for key, value in test_attributes.items():
            self.assertEqual(message["attributes"].get(key), value, f"消息属性 {key} 不匹配")
    
    async def test_topic_management(self):
        """测试主题管理功能"""
        # 创建另一个测试主题
        test_topic2 = f"{self.test_topic}-2"
        
        # 创建主题
        topic_info = self.client.create_topic(
            name=test_topic2,
            description="另一个测试主题",
            properties={"purpose": "test"},
            partition_count=2,
            retention_hours=2
        )
        
        # 验证创建结果
        self.assertEqual(topic_info["name"], test_topic2)
        self.assertEqual(topic_info["description"], "另一个测试主题")
        self.assertEqual(topic_info["properties"], {"purpose": "test"})
        
        # 获取主题信息
        topic_info = self.client.get_topic(test_topic2)
        
        # 验证主题信息
        self.assertEqual(topic_info["name"], test_topic2)
        self.assertEqual(topic_info["partition_count"], 2)
        
        # 列出主题
        topics, next_page_token, total_count = self.client.list_topics()
        
        # 验证主题列表
        self.assertGreaterEqual(total_count, 2, "主题总数不正确")
        
        # 检查测试主题是否在列表中
        topic_names = [t["name"] for t in topics]
        self.assertIn(self.test_topic, topic_names)
        self.assertIn(test_topic2, topic_names)
        
        # 删除主题
        success = self.client.delete_topic(test_topic2)
        self.assertTrue(success)
        
        # 验证主题已删除
        with self.assertRaises(ValueError):
            self.client.get_topic(test_topic2)
    
    async def test_filtered_subscription(self):
        """测试消息过滤订阅"""
        # 订阅主题，设置过滤条件
        subscription = self.client.subscribe(
            topic=self.test_topic,
            callback=self.message_handler,
            filter_attributes={"priority": "high"}
        )
        
        # 等待订阅建立
        await asyncio.sleep(1)
        
        # 清空接收消息列表
        self.received_messages = []
        
        # 发布高优先级消息
        self.client.publish(
            topic=self.test_topic,
            payload={"type": "important"},
            attributes={"priority": "high"}
        )
        
        # 发布普通优先级消息
        self.client.publish(
            topic=self.test_topic,
            payload={"type": "normal"},
            attributes={"priority": "normal"}
        )
        
        # 等待接收消息
        await asyncio.sleep(3)
        
        # 取消订阅
        subscription.unsubscribe()
        
        # 验证只接收到高优先级消息
        self.assertEqual(len(self.received_messages), 1, "应该只接收一条消息")
        
        # 验证消息类型
        message = self.received_messages[0]
        payload = json.loads(message["payload"].decode('utf-8'))
        self.assertEqual(payload["type"], "important", "接收到的不是高优先级消息")
    
    async def test_health_check(self):
        """测试健康检查"""
        status = self.client.health_check()
        self.assertEqual(status, "SERVING", "服务健康状态不正常")

# 运行测试
if __name__ == "__main__":
    unittest.main() 