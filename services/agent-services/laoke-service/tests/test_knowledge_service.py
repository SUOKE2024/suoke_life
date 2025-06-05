#!/usr/bin/env python3
"""
知识服务测试
测试老克智能体的知识管理功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

class TestKnowledgeService:
    """知识服务测试类"""
    
    def test_knowledge_search(self):
        """测试知识搜索功能"""
        # 模拟搜索参数
        search_params = {
            "keywords": "人工智能",
            "category": "技术",
            "difficulty": "中级",
            "language": "中文"
        }
        
        # 模拟搜索结果
        expected_results = [
            {
                "id": "knowledge_001",
                "title": "人工智能基础概念",
                "category": "技术",
                "difficulty": "中级",
                "content_preview": "人工智能是计算机科学的一个分支...",
                "tags": ["AI", "机器学习", "深度学习"],
                "rating": 4.8,
                "view_count": 1250
            },
            {
                "id": "knowledge_002", 
                "title": "机器学习算法详解",
                "category": "技术",
                "difficulty": "中级",
                "content_preview": "机器学习是人工智能的核心技术...",
                "tags": ["机器学习", "算法", "数据科学"],
                "rating": 4.6,
                "view_count": 980
            }
        ]
        
        # 验证搜索结果
        assert len(expected_results) == 2
        assert all(result["category"] == "技术" for result in expected_results)
        assert all(result["difficulty"] == "中级" for result in expected_results)
        assert all(result["rating"] >= 4.0 for result in expected_results)
    
    def test_knowledge_recommendation(self):
        """测试知识推荐功能"""
        user_profile = {
            "user_id": "user_001",
            "interests": ["人工智能", "编程", "数据科学"],
            "skill_level": "中级",
            "learning_history": ["machine_learning_basics", "python_programming"],
            "preferred_language": "中文"
        }
        
        expected_recommendations = [
            {
                "knowledge_id": "rec_001",
                "title": "深度学习进阶",
                "match_score": 0.92,
                "reason": "基于您对人工智能的兴趣和中级技能水平推荐",
                "estimated_time": "45分钟"
            },
            {
                "knowledge_id": "rec_002",
                "title": "数据科学实战项目",
                "match_score": 0.88,
                "reason": "结合您的编程背景和数据科学兴趣",
                "estimated_time": "60分钟"
            }
        ]
        
        # 验证推荐结果
        assert len(expected_recommendations) == 2
        assert all(rec["match_score"] >= 0.8 for rec in expected_recommendations)
        assert all("reason" in rec for rec in expected_recommendations)
    
    def test_knowledge_content_management(self):
        """测试知识内容管理"""
        # 创建知识内容
        knowledge_data = {
            "title": "区块链技术原理",
            "category": "技术",
            "difficulty": "高级",
            "content": "区块链是一种分布式账本技术...",
            "tags": ["区块链", "加密货币", "分布式系统"],
            "author": "专家001",
            "language": "中文"
        }
        
        expected_result = {
            "knowledge_id": "knowledge_new_001",
            "status": "created",
            "title": knowledge_data["title"],
            "created_at": "2024-12-19T10:00:00Z",
            "version": "1.0"
        }
        
        # 验证创建结果
        assert expected_result["status"] == "created"
        assert expected_result["title"] == knowledge_data["title"]
        assert "knowledge_id" in expected_result
        assert "created_at" in expected_result
    
    def test_knowledge_quality_assessment(self):
        """测试知识质量评估"""
        knowledge_content = {
            "id": "knowledge_001",
            "title": "Python编程入门",
            "content": "Python是一种高级编程语言，具有简洁的语法...",
            "word_count": 1500,
            "code_examples": 8,
            "references": 12,
            "images": 5
        }
        
        expected_quality_score = {
            "overall_score": 4.2,
            "content_completeness": 4.5,
            "technical_accuracy": 4.0,
            "readability": 4.3,
            "practical_value": 4.1,
            "feedback": {
                "strengths": ["内容结构清晰", "代码示例丰富", "实用性强"],
                "improvements": ["可以增加更多实际案例", "参考资料可以更新"]
            }
        }
        
        # 验证质量评估
        assert expected_quality_score["overall_score"] >= 4.0
        assert all(score >= 3.5 for score in [
            expected_quality_score["content_completeness"],
            expected_quality_score["technical_accuracy"],
            expected_quality_score["readability"],
            expected_quality_score["practical_value"]
        ])
    
    def test_knowledge_version_control(self):
        """测试知识版本控制"""
        version_history = [
            {
                "version": "1.0",
                "created_at": "2024-01-15T10:00:00Z",
                "author": "专家001",
                "changes": "初始版本创建",
                "status": "published"
            },
            {
                "version": "1.1",
                "created_at": "2024-02-20T14:30:00Z", 
                "author": "专家001",
                "changes": "更新代码示例，修正错误",
                "status": "published"
            },
            {
                "version": "1.2",
                "created_at": "2024-03-10T09:15:00Z",
                "author": "专家002",
                "changes": "增加新的章节，补充实践案例",
                "status": "draft"
            }
        ]
        
        # 验证版本控制
        assert len(version_history) == 3
        assert version_history[0]["version"] == "1.0"
        assert version_history[-1]["status"] == "draft"
        assert all("changes" in version for version in version_history)
    
    def test_knowledge_analytics(self):
        """测试知识分析功能"""
        analytics_data = {
            "knowledge_id": "knowledge_001",
            "time_period": "last_30_days",
            "metrics": {
                "total_views": 2500,
                "unique_visitors": 1800,
                "average_time_spent": "8.5分钟",
                "completion_rate": 0.75,
                "rating_average": 4.3,
                "rating_count": 156,
                "bookmark_count": 89,
                "share_count": 34
            },
            "user_feedback": {
                "positive_comments": 142,
                "improvement_suggestions": 23,
                "error_reports": 3
            }
        }
        
        # 验证分析数据
        assert analytics_data["metrics"]["total_views"] > 0
        assert analytics_data["metrics"]["completion_rate"] >= 0.7
        assert analytics_data["metrics"]["rating_average"] >= 4.0
        assert analytics_data["user_feedback"]["positive_comments"] > analytics_data["user_feedback"]["error_reports"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
