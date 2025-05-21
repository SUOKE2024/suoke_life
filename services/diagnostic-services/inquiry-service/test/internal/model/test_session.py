#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
会话模型单元测试
"""

import time
import unittest
from typing import List, Dict, Any

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from internal.model.session import InquirySession, Message, MessageRole, SessionStatus


class TestMessage(unittest.TestCase):
    """测试消息模型"""
    
    def test_create_message(self):
        """测试创建消息"""
        message = Message(role=MessageRole.USER, content="测试消息")
        
        self.assertEqual(message.role, MessageRole.USER)
        self.assertEqual(message.content, "测试消息")
        self.assertIsNotNone(message.timestamp)
        self.assertIsNotNone(message.message_id)
        self.assertEqual(message.metadata, {})
    
    def test_message_with_metadata(self):
        """测试带元数据的消息"""
        metadata = {"source": "test", "important": True}
        message = Message(
            role=MessageRole.ASSISTANT, 
            content="回复消息",
            metadata=metadata
        )
        
        self.assertEqual(message.role, MessageRole.ASSISTANT)
        self.assertEqual(message.content, "回复消息")
        self.assertEqual(message.metadata, metadata)


class TestInquirySession(unittest.TestCase):
    """测试问诊会话模型"""
    
    def setUp(self):
        """测试前准备"""
        self.session = InquirySession(
            session_id="test-session-123",
            user_id="user-456",
            status=SessionStatus.PENDING
        )
    
    def test_create_session(self):
        """测试创建会话"""
        self.assertEqual(self.session.session_id, "test-session-123")
        self.assertEqual(self.session.user_id, "user-456")
        self.assertEqual(self.session.status, SessionStatus.PENDING)
        self.assertEqual(len(self.session.messages), 0)
        self.assertIsNone(self.session.expires_at)
    
    def test_add_message(self):
        """测试添加消息"""
        # 添加用户消息
        user_message = self.session.add_message(
            role=MessageRole.USER,
            content="用户问题"
        )
        
        self.assertEqual(len(self.session.messages), 1)
        self.assertEqual(self.session.messages[0].role, MessageRole.USER)
        self.assertEqual(self.session.messages[0].content, "用户问题")
        self.assertEqual(user_message.role, MessageRole.USER)
        
        # 添加助手消息
        assistant_message = self.session.add_message(
            role=MessageRole.ASSISTANT,
            content="助手回复",
            metadata={"confidence": 0.95}
        )
        
        self.assertEqual(len(self.session.messages), 2)
        self.assertEqual(self.session.messages[1].role, MessageRole.ASSISTANT)
        self.assertEqual(self.session.messages[1].content, "助手回复")
        self.assertEqual(assistant_message.metadata["confidence"], 0.95)
    
    def test_get_conversation_history(self):
        """测试获取对话历史"""
        # 添加多条消息
        self.session.add_message(MessageRole.SYSTEM, "系统指令")
        self.session.add_message(MessageRole.USER, "用户问题1")
        self.session.add_message(MessageRole.ASSISTANT, "助手回复1")
        self.session.add_message(MessageRole.USER, "用户问题2")
        self.session.add_message(MessageRole.ASSISTANT, "助手回复2")
        
        # 获取完整历史
        history = self.session.get_conversation_history()
        self.assertEqual(len(history), 5)
        
        # 获取最近3条消息
        recent_history = self.session.get_conversation_history(max_messages=3)
        self.assertEqual(len(recent_history), 3)
        self.assertEqual(recent_history[0]["content"], "用户问题2")
        self.assertEqual(recent_history[1]["content"], "助手回复2")
        
        # 检查格式
        self.assertIn("role", recent_history[0])
        self.assertIn("content", recent_history[0])
    
    def test_update_status(self):
        """测试更新会话状态"""
        # 初始状态
        self.assertEqual(self.session.status, SessionStatus.PENDING)
        
        # 更新为进行中
        self.session.update_status(SessionStatus.ACTIVE)
        self.assertEqual(self.session.status, SessionStatus.ACTIVE)
        self.assertIsNone(self.session.expires_at)
        
        # 更新为已完成，应设置过期时间
        self.session.update_status(SessionStatus.COMPLETED)
        self.assertEqual(self.session.status, SessionStatus.COMPLETED)
        self.assertIsNotNone(self.session.expires_at)
        self.assertGreater(self.session.expires_at, time.time())
    
    def test_is_expired(self):
        """测试会话过期检查"""
        # 初始未设置过期时间
        self.assertFalse(self.session.is_expired())
        
        # 设置为未来过期
        self.session.expires_at = time.time() + 3600  # 1小时后过期
        self.assertFalse(self.session.is_expired())
        
        # 设置为已过期
        self.session.expires_at = time.time() - 3600  # 1小时前过期
        self.assertTrue(self.session.is_expired())
    
    def test_to_dict(self):
        """测试转换为字典"""
        # 添加消息
        self.session.add_message(MessageRole.USER, "用户问题")
        self.session.add_message(MessageRole.ASSISTANT, "助手回复")
        
        # 添加症状和证型
        self.session.extracted_symptoms = [{"name": "头痛"}]
        self.session.tcm_patterns = [{"name": "肝阳上亢"}]
        
        # 转换为字典
        session_dict = self.session.to_dict()
        
        # 验证字段
        self.assertEqual(session_dict["session_id"], "test-session-123")
        self.assertEqual(session_dict["user_id"], "user-456")
        self.assertEqual(session_dict["status"], "pending")
        self.assertEqual(len(session_dict["messages"]), 2)
        self.assertEqual(session_dict["extracted_symptoms"], [{"name": "头痛"}])
        self.assertEqual(session_dict["tcm_patterns"], [{"name": "肝阳上亢"}])
    
    def test_from_dict(self):
        """测试从字典创建会话"""
        # 准备会话字典
        session_data = {
            "session_id": "new-session-789",
            "user_id": "user-123",
            "status": "active",
            "messages": [
                {
                    "role": "user",
                    "content": "问题内容",
                    "timestamp": time.time(),
                    "message_id": "msg-1",
                    "metadata": {}
                },
                {
                    "role": "assistant",
                    "content": "回复内容",
                    "timestamp": time.time(),
                    "message_id": "msg-2",
                    "metadata": {"confidence": 0.9}
                }
            ],
            "created_at": time.time() - 3600,
            "updated_at": time.time() - 1800,
            "expires_at": time.time() + 7200,
            "metadata": {"important": True},
            "extracted_symptoms": [{"name": "咳嗽", "severity": "moderate"}],
            "tcm_patterns": [{"name": "风寒感冒", "confidence": 0.8}],
            "summary": "会话摘要",
            "conclusion": "结论建议"
        }
        
        # 从字典创建会话
        session = InquirySession.from_dict(session_data)
        
        # 验证属性
        self.assertEqual(session.session_id, "new-session-789")
        self.assertEqual(session.user_id, "user-123")
        self.assertEqual(session.status, SessionStatus.ACTIVE)
        self.assertEqual(len(session.messages), 2)
        self.assertEqual(session.messages[0].role, MessageRole.USER)
        self.assertEqual(session.messages[1].content, "回复内容")
        self.assertEqual(session.messages[1].metadata["confidence"], 0.9)
        self.assertEqual(session.metadata["important"], True)
        self.assertEqual(session.extracted_symptoms[0]["name"], "咳嗽")
        self.assertEqual(session.tcm_patterns[0]["name"], "风寒感冒")
        self.assertEqual(session.summary, "会话摘要")
        self.assertEqual(session.conclusion, "结论建议")


if __name__ == "__main__":
    unittest.main()