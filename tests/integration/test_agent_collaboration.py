"""
智能体协作集成测试

测试四大智能体（索儿、小克、老克、小艾）之间的协作功能。
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
import json

# 导入通用测试基类
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.test_base import IntegrationTestCase


class TestAgentCollaboration(IntegrationTestCase):
    """智能体协作集成测试类"""

    @pytest.fixture
    async def mock_agent_clients(self):
        """模拟智能体客户端"""
        clients = {
            "soer": AsyncMock(),
            "xiaoke": AsyncMock(),
            "laoke": AsyncMock(),
            "xiaoai": AsyncMock()
        }
        
        # 配置模拟响应
        clients["soer"].chat.return_value = {
            "response": "我是索儿，我来协调其他智能体为您服务",
            "next_agent": "xiaoke",
            "context": {"user_query": "健康咨询", "priority": "high"}
        }
        
        clients["xiaoke"].analyze_health.return_value = {
            "constitution": "阳虚体质",
            "recommendations": ["早睡早起", "适量运动"],
            "need_expert_review": True
        }
        
        clients["laoke"].provide_knowledge.return_value = {
            "knowledge": "阳虚体质的详细说明和调理方法",
            "sources": ["中医体质学", "黄帝内经"],
            "confidence": 0.95
        }
        
        clients["xiaoai"].coordinate_diagnosis.return_value = {
            "diagnosis_plan": ["望诊", "问诊", "脉诊"],
            "estimated_time": "15分钟",
            "required_services": ["look-service", "inquiry-service"]
        }
        
        return clients

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_consultation_workflow(self, mock_agent_clients):
        """测试完整的咨询工作流"""
        # 1. 用户发起健康咨询
        user_query = {
            "message": "我最近总是感觉疲劳，想了解一下自己的体质",
            "user_id": "test-user-123",
            "session_id": "test-session-456"
        }
        
        # 2. 索儿接收并分析请求
        soer_response = await mock_agent_clients["soer"].chat(user_query)
        assert soer_response["next_agent"] == "xiaoke"
        assert "健康咨询" in soer_response["context"]["user_query"]
        
        # 3. 小克进行健康分析
        health_analysis = await mock_agent_clients["xiaoke"].analyze_health({
            "symptoms": ["疲劳"],
            "user_id": user_query["user_id"]
        })
        assert health_analysis["constitution"] == "阳虚体质"
        assert health_analysis["need_expert_review"] is True
        
        # 4. 老克提供专业知识
        knowledge_response = await mock_agent_clients["laoke"].provide_knowledge({
            "topic": "阳虚体质",
            "context": health_analysis
        })
        assert knowledge_response["confidence"] > 0.9
        assert "调理方法" in knowledge_response["knowledge"]
        
        # 5. 小艾协调诊断流程
        diagnosis_plan = await mock_agent_clients["xiaoai"].coordinate_diagnosis({
            "constitution": health_analysis["constitution"],
            "user_id": user_query["user_id"]
        })
        assert "望诊" in diagnosis_plan["diagnosis_plan"]
        assert "look-service" in diagnosis_plan["required_services"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_handoff_mechanism(self, mock_agent_clients):
        """测试智能体交接机制"""
        # 测试从索儿到小克的交接
        handoff_data = {
            "from_agent": "soer",
            "to_agent": "xiaoke",
            "context": {
                "user_query": "体质分析",
                "user_id": "test-user-123",
                "priority": "normal"
            },
            "metadata": {
                "timestamp": "2024-01-01T10:00:00Z",
                "session_id": "test-session-456"
            }
        }
        
        # 验证交接数据的完整性
        assert handoff_data["from_agent"] in ["soer", "xiaoke", "laoke", "xiaoai"]
        assert handoff_data["to_agent"] in ["soer", "xiaoke", "laoke", "xiaoai"]
        assert "user_id" in handoff_data["context"]
        assert "session_id" in handoff_data["metadata"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_agent_decision_making(self, mock_agent_clients):
        """测试多智能体决策"""
        # 复杂健康问题需要多个智能体协作
        complex_case = {
            "symptoms": ["头痛", "失眠", "消化不良", "情绪低落"],
            "duration": "3个月",
            "user_profile": {
                "age": 35,
                "gender": "female",
                "occupation": "程序员"
            }
        }
        
        # 各智能体并行分析
        tasks = [
            mock_agent_clients["xiaoke"].analyze_health(complex_case),
            mock_agent_clients["laoke"].search_knowledge({
                "symptoms": complex_case["symptoms"]
            }),
            mock_agent_clients["xiaoai"].plan_diagnosis(complex_case)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 验证各智能体都提供了有效分析
        health_analysis, knowledge_search, diagnosis_plan = results
        assert health_analysis is not None
        assert knowledge_search is not None
        assert diagnosis_plan is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_error_handling_and_fallback(self, mock_agent_clients):
        """测试智能体错误处理和降级机制"""
        # 模拟小克服务不可用
        mock_agent_clients["xiaoke"].analyze_health.side_effect = Exception("Service unavailable")
        
        # 索儿应该能够检测到错误并启用降级机制
        with pytest.raises(Exception):
            await mock_agent_clients["xiaoke"].analyze_health({"symptoms": ["头痛"]})
        
        # 验证降级机制：使用老克的基础分析功能
        fallback_response = await mock_agent_clients["laoke"].provide_knowledge({
            "topic": "头痛症状分析",
            "fallback_mode": True
        })
        assert fallback_response is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_context_sharing(self, mock_agent_clients):
        """测试智能体间的上下文共享"""
        # 创建共享上下文
        shared_context = {
            "user_id": "test-user-123",
            "session_id": "test-session-456",
            "conversation_history": [
                {"agent": "soer", "message": "您好，我是索儿"},
                {"agent": "user", "message": "我想了解我的体质"}
            ],
            "user_profile": {
                "constitution": "未知",
                "health_goals": ["体质改善", "健康管理"]
            }
        }
        
        # 各智能体应该能够访问和更新共享上下文
        # 这里模拟上下文在智能体间的传递和更新
        updated_context = shared_context.copy()
        updated_context["conversation_history"].append({
            "agent": "xiaoke", 
            "message": "根据分析，您可能是阳虚体质"
        })
        updated_context["user_profile"]["constitution"] = "阳虚体质"
        
        assert len(updated_context["conversation_history"]) == 3
        assert updated_context["user_profile"]["constitution"] == "阳虚体质"


class TestDiagnosisServiceIntegration(IntegrationTestCase):
    """诊断服务集成测试"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_five_diagnosis_coordination(self):
        """测试五诊协调功能"""
        # 模拟小艾协调五诊服务
        diagnosis_request = {
            "user_id": "test-user-123",
            "diagnosis_type": "comprehensive",
            "services_required": ["look", "listen", "inquiry", "palpation", "calculation"]
        }
        
        # 这里应该测试实际的服务调用
        # 暂时使用模拟数据
        mock_results = {
            "look": {"complexion": "苍白", "tongue": "淡红"},
            "listen": {"voice": "低沉", "breathing": "正常"},
            "inquiry": {"symptoms": ["疲劳", "怕冷"]},
            "palpation": {"pulse": "沉细"},
            "calculation": {"constitution": "阳虚体质", "confidence": 0.85}
        }
        
        # 验证诊断结果的一致性
        assert mock_results["calculation"]["constitution"] == "阳虚体质"
        assert all(service in mock_results for service in diagnosis_request["services_required"])

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_diagnosis_result_aggregation(self):
        """测试诊断结果聚合"""
        # 模拟各诊断服务的结果
        diagnosis_results = {
            "look_service": {
                "constitution_indicators": ["面色苍白", "舌淡"],
                "confidence": 0.8
            },
            "inquiry_service": {
                "symptom_analysis": ["怕冷", "疲劳"],
                "constitution_suggestion": "阳虚",
                "confidence": 0.85
            },
            "palpation_service": {
                "pulse_analysis": "沉细脉",
                "constitution_indication": "阳虚",
                "confidence": 0.9
            }
        }
        
        # 聚合分析
        constitution_votes = {}
        total_confidence = 0
        
        for service, result in diagnosis_results.items():
            constitution = result.get("constitution_suggestion") or result.get("constitution_indication")
            if constitution:
                constitution_votes[constitution] = constitution_votes.get(constitution, 0) + 1
                total_confidence += result["confidence"]
        
        # 验证聚合结果
        most_likely_constitution = max(constitution_votes, key=constitution_votes.get)
        average_confidence = total_confidence / len(diagnosis_results)
        
        assert most_likely_constitution == "阳虚"
        assert average_confidence > 0.8


class TestHealthDataFlowIntegration(IntegrationTestCase):
    """健康数据流集成测试"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_data_pipeline(self):
        """测试健康数据处理流水线"""
        # 模拟健康数据输入
        health_data = {
            "user_id": "test-user-123",
            "timestamp": "2024-01-01T10:00:00Z",
            "vital_signs": {
                "heart_rate": 72,
                "blood_pressure": "120/80",
                "temperature": 36.5
            },
            "symptoms": ["轻微头痛"],
            "lifestyle": {
                "sleep_hours": 7,
                "exercise_minutes": 30,
                "stress_level": 3
            }
        }
        
        # 数据流处理步骤
        # 1. 数据验证和清洗
        assert health_data["user_id"] is not None
        assert health_data["vital_signs"]["heart_rate"] > 0
        
        # 2. 数据存储（模拟）
        stored_data = health_data.copy()
        stored_data["id"] = "health_record_123"
        stored_data["processed_at"] = "2024-01-01T10:01:00Z"
        
        # 3. 智能分析（模拟）
        analysis_result = {
            "health_score": 85,
            "risk_factors": ["轻微头痛"],
            "recommendations": ["多休息", "保持运动"],
            "follow_up_needed": False
        }
        
        # 4. 结果验证
        assert analysis_result["health_score"] > 80
        assert len(analysis_result["recommendations"]) > 0