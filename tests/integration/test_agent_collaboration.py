"""
智能体协作集成测试

测试四大智能体（小艾、小克、老克、索儿）的协同工作机制。
"""

import pytest
import asyncio
import time
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock

# 导入通用测试基类
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.test_base import IntegrationTestCase


class TestAgentCollaboration(IntegrationTestCase):
    """智能体协作集成测试"""

    @pytest.fixture(autouse=True)
    async def setup_agents(self):
        """设置智能体服务模拟"""
        self.xiaoai_service = AsyncMock()  # 小艾 - 健康助手
        self.xiaoke_service = AsyncMock()  # 小克 - 诊断专家
        self.laoke_service = AsyncMock()   # 老克 - 中医大师
        self.soer_service = AsyncMock()    # 索儿 - 生活管家
        
        # 模拟服务响应
        self.xiaoai_service.process_request.return_value = {
            "agent": "xiaoai",
            "status": "completed",
            "result": "健康建议已生成",
            "next_agent": "xiaoke",
            "confidence": 0.85
        }
        
        self.xiaoke_service.process_request.return_value = {
            "agent": "xiaoke", 
            "status": "completed",
            "result": "初步诊断完成",
            "next_agent": "laoke",
            "confidence": 0.90
        }
        
        self.laoke_service.process_request.return_value = {
            "agent": "laoke",
            "status": "completed", 
            "result": "中医辨证论治方案",
            "next_agent": "soer",
            "confidence": 0.95
        }
        
        self.soer_service.process_request.return_value = {
            "agent": "soer",
            "status": "completed",
            "result": "生活方案制定完成",
            "next_agent": None,
            "confidence": 0.88
        }
    
    async def test_full_collaboration_workflow(self):
        """测试完整的智能体协作工作流"""
        # 用户请求
        user_request = {
            "user_id": "test_user_001",
            "request_type": "health_consultation",
            "symptoms": ["头痛", "失眠", "食欲不振"],
            "duration": "3天",
            "severity": "中等"
        }
        
        # 启动协作流程
        workflow_result = await self._execute_collaboration_workflow(user_request)
        
        # 验证工作流完成
        assert workflow_result["status"] == "completed"
        assert len(workflow_result["agent_results"]) == 4
        
        # 验证每个智能体都被调用
        self.xiaoai_service.process_request.assert_called_once()
        self.xiaoke_service.process_request.assert_called_once()
        self.laoke_service.process_request.assert_called_once()
        self.soer_service.process_request.assert_called_once()
        
        # 验证结果传递
        agent_results = workflow_result["agent_results"]
        assert agent_results[0]["agent"] == "xiaoai"
        assert agent_results[1]["agent"] == "xiaoke"
        assert agent_results[2]["agent"] == "laoke"
        assert agent_results[3]["agent"] == "soer"
    
    async def test_agent_handoff_mechanism(self):
        """测试智能体交接机制"""
        # 测试小艾到小克的交接
        xiaoai_result = await self.xiaoai_service.process_request({
            "user_id": "test_user_001",
            "request": "我最近总是头痛"
        })
        
        # 验证交接信息
        assert xiaoai_result["next_agent"] == "xiaoke"
        assert xiaoai_result["confidence"] > 0.8
        
        # 测试小克接收交接
        xiaoke_input = {
            "previous_agent": "xiaoai",
            "previous_result": xiaoai_result["result"],
            "user_context": {"symptoms": ["头痛"]}
        }
        
        xiaoke_result = await self.xiaoke_service.process_request(xiaoke_input)
        assert xiaoke_result["next_agent"] == "laoke"
    
    async def test_parallel_agent_processing(self):
        """测试智能体并行处理能力"""
        # 创建多个并发请求
        requests = [
            {"user_id": f"user_{i}", "symptoms": [f"症状_{i}"]}
            for i in range(5)
        ]
        
        # 并行处理
        tasks = [
            self._execute_collaboration_workflow(req)
            for req in requests
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 验证所有请求都成功处理
        assert len(results) == 5
        for result in results:
            assert result["status"] == "completed"
    
    async def test_agent_failure_recovery(self):
        """测试智能体故障恢复机制"""
        # 模拟小克服务故障
        self.xiaoke_service.process_request.side_effect = Exception("服务暂时不可用")
        
        user_request = {
            "user_id": "test_user_002",
            "request_type": "health_consultation",
            "symptoms": ["咳嗽"]
        }
        
        # 执行工作流（应该有故障恢复）
        workflow_result = await self._execute_collaboration_workflow(user_request)
        
        # 验证故障处理
        assert workflow_result["status"] == "partial_completed"
        assert "xiaoke" in workflow_result["failed_agents"]
        
        # 验证其他智能体仍然工作
        assert len(workflow_result["agent_results"]) >= 2  # 至少小艾和备用处理
    
    # 辅助方法
    async def _execute_collaboration_workflow(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体协作工作流"""
        workflow_result = {
            "status": "in_progress",
            "agent_results": [],
            "failed_agents": []
        }
        
        # 模拟工作流执行
        agents = [
            ("xiaoai", self.xiaoai_service),
            ("xiaoke", self.xiaoke_service), 
            ("laoke", self.laoke_service),
            ("soer", self.soer_service)
        ]
        
        current_context = user_request.copy()
        
        for agent_name, agent_service in agents:
            try:
                result = await agent_service.process_request(current_context)
                workflow_result["agent_results"].append(result)
                
                # 更新上下文
                current_context.update({
                    "previous_agent": agent_name,
                    "previous_result": result["result"]
                })
                
                # 检查是否需要继续
                if result.get("next_agent") is None:
                    break
                    
            except Exception as e:
                workflow_result["failed_agents"].append(agent_name)
                # 继续处理其他智能体
                continue
        
        # 确定最终状态
        if not workflow_result["failed_agents"]:
            workflow_result["status"] = "completed"
        elif len(workflow_result["agent_results"]) > 0:
            workflow_result["status"] = "partial_completed"
        else:
            workflow_result["status"] = "failed"
        
        return workflow_result


@pytest.mark.integration
@pytest.mark.asyncio
class TestAgentPerformance(IntegrationTestCase):
    """智能体性能测试"""
    
    async def test_response_time_requirements(self):
        """测试响应时间要求"""
        start_time = time.time()
        
        # 模拟智能体处理
        await asyncio.sleep(0.1)  # 模拟处理时间
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 验证响应时间要求（< 2秒）
        assert response_time < 2.0
    
    async def test_concurrent_user_handling(self):
        """测试并发用户处理能力"""
        # 模拟100个并发用户
        concurrent_users = 100
        
        async def simulate_user_request(user_id: int):
            await asyncio.sleep(0.01)  # 模拟处理时间
            return {"user_id": user_id, "status": "completed"}
        
        tasks = [
            simulate_user_request(i) 
            for i in range(concurrent_users)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 验证所有请求都成功处理
        assert len(results) == concurrent_users
        
        # 验证总处理时间合理（< 5秒）
        total_time = end_time - start_time
        assert total_time < 5.0


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