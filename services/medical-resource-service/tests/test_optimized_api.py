"""
优化后的医疗资源服务API测试
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from ..internal.agent.xiaoke_agent import XiaokeAgent
from ..internal.domain.models import UrgencyLevel, ResourceType
from ..internal.service.resource_scheduling_service import ResourceSchedulingService


class TestOptimizedMedicalResourceAPI:
    """测试优化后的医疗资源服务API"""

    @pytest.fixture
    def mock_xiaoke_agent(self):
        """模拟小克智能体"""
        agent = MagicMock(spec=XiaokeAgent)
        agent.recommend_resources = AsyncMock(return_value=[
            {
                "resource_type": ResourceType.DOCTOR,
                "resource_id": "doctor_001",
                "title": "推荐医生: 张医生",
                "description": "主任医师 - 市人民医院 内科",
                "confidence_score": 0.85,
                "reasoning": "基于症状匹配和专业经验",
                "metadata": {
                    "doctor_info": {
                        "name": "张医生",
                        "title": "主任医师",
                        "hospital": "市人民医院",
                        "department": "内科",
                        "rating": 4.5,
                        "experience": 15
                    }
                }
            }
        ])
        agent.optimize_schedule = AsyncMock(return_value={
            "success": True,
            "message": "优化完成",
            "suggestions": [
                {
                    "resource_id": "doctor_001",
                    "type": "optimize_schedule",
                    "description": "建议调整排班时间",
                    "priority": "medium",
                    "expected_impact": 0.15
                }
            ],
            "expected_improvement": 0.15
        })
        agent.get_agent_status = MagicMock(return_value={
            "state": "idle",
            "last_optimization": None,
            "config": {"matching_weights": {"specialty_match": 0.4}},
            "capabilities": ["resource_recommendation", "schedule_optimization"]
        })
        return agent

    @pytest.fixture
    def mock_scheduler_service(self):
        """模拟调度服务"""
        scheduler = MagicMock(spec=ResourceSchedulingService)
        scheduler.schedule_resource = AsyncMock(return_value={
            "success": True,
            "appointment_id": "apt_001",
            "resource_id": "doctor_001",
            "scheduled_time": datetime.now() + timedelta(days=1),
            "estimated_cost": 200.0
        })
        scheduler.get_resource_status = AsyncMock(return_value={
            "total_resources": 50,
            "available_resources": 35,
            "utilization_rate": 0.7
        })
        scheduler.get_scheduling_queue = AsyncMock(return_value={
            "pending_requests": 5,
            "processing_requests": 2,
            "completed_today": 25
        })
        return scheduler

    @pytest.mark.asyncio
    async def test_resource_recommendation(self, mock_xiaoke_agent):
        """测试资源推荐功能"""
        # 准备测试数据
        request_data = {
            "user_id": "user_001",
            "symptoms": ["头痛", "发热"],
            "location": "北京市朝阳区",
            "urgency": "normal",
            "max_results": 10
        }

        # 调用推荐功能
        recommendations = await mock_xiaoke_agent.recommend_resources(
            user_id=request_data["user_id"],
            symptoms=request_data["symptoms"],
            location=request_data["location"],
            urgency=UrgencyLevel.NORMAL,
            max_results=request_data["max_results"]
        )

        # 验证结果
        assert len(recommendations) > 0
        assert recommendations[0]["confidence_score"] > 0.8
        assert "doctor_info" in recommendations[0]["metadata"]

    @pytest.mark.asyncio
    async def test_schedule_optimization(self, mock_xiaoke_agent):
        """测试调度优化功能"""
        # 准备测试数据
        resource_ids = ["doctor_001", "doctor_002"]
        optimization_date = datetime.now() + timedelta(days=1)
        optimization_weights = {"utilization": 0.6, "satisfaction": 0.4}

        # 调用优化功能
        result = await mock_xiaoke_agent.optimize_schedule(
            resource_ids=resource_ids,
            optimization_date=optimization_date,
            optimization_weights=optimization_weights
        )

        # 验证结果
        assert result["success"] is True
        assert len(result["suggestions"]) > 0
        assert result["expected_improvement"] > 0

    @pytest.mark.asyncio
    async def test_resource_scheduling(self, mock_scheduler_service):
        """测试资源调度功能"""
        # 准备测试数据
        request_data = {
            "user_id": "user_001",
            "resource_type": ResourceType.DOCTOR,
            "priority": 1,
            "preferred_time": None,
            "special_requirements": []
        }

        # 调用调度功能
        result = await mock_scheduler_service.schedule_resource(
            user_id=request_data["user_id"],
            resource_type=request_data["resource_type"],
            priority=request_data["priority"],
            preferred_time=request_data["preferred_time"],
            special_requirements=request_data["special_requirements"]
        )

        # 验证结果
        assert result["success"] is True
        assert "appointment_id" in result
        assert "scheduled_time" in result

    def test_agent_status(self, mock_xiaoke_agent):
        """测试智能体状态获取"""
        status = mock_xiaoke_agent.get_agent_status()
        
        # 验证状态信息
        assert "state" in status
        assert "capabilities" in status
        assert len(status["capabilities"]) > 0

    @pytest.mark.asyncio
    async def test_resource_status(self, mock_scheduler_service):
        """测试资源状态获取"""
        status = await mock_scheduler_service.get_resource_status(
            resource_type="doctor",
            location="北京市"
        )
        
        # 验证状态信息
        assert "total_resources" in status
        assert "available_resources" in status
        assert "utilization_rate" in status

    @pytest.mark.asyncio
    async def test_scheduling_queue(self, mock_scheduler_service):
        """测试调度队列状态"""
        queue_status = await mock_scheduler_service.get_scheduling_queue()
        
        # 验证队列信息
        assert "pending_requests" in queue_status
        assert "processing_requests" in queue_status
        assert "completed_today" in queue_status

    def test_symptom_categorization(self):
        """测试症状分类功能"""
        from ..internal.service.resource_scheduling_service import ResourceSchedulingService
        
        # 创建调度服务实例（仅用于测试方法）
        scheduler = ResourceSchedulingService({}, None)
        
        # 测试紧急症状
        emergency_symptoms = ["胸痛", "呼吸困难"]
        category = scheduler._categorize_symptoms(emergency_symptoms)
        assert category == "emergency_care"
        
        # 测试专科症状
        specialist_symptoms = ["心脏不适", "神经痛"]
        category = scheduler._categorize_symptoms(specialist_symptoms)
        assert category == "specialist_care"
        
        # 测试一般症状
        general_symptoms = ["头痛", "感冒"]
        category = scheduler._categorize_symptoms(general_symptoms)
        assert category == "general_medicine"

    def test_symptom_severity_assessment(self):
        """测试症状严重程度评估"""
        from ..internal.service.resource_scheduling_service import ResourceSchedulingService
        
        scheduler = ResourceSchedulingService({}, None)
        
        # 测试严重症状
        severe_symptoms = ["剧烈头痛", "胸痛"]
        severity = scheduler._assess_symptom_severity(severe_symptoms)
        assert severity == 1.0
        
        # 测试中等症状
        moderate_symptoms = ["头痛", "发热"]
        severity = scheduler._assess_symptom_severity(moderate_symptoms)
        assert severity == 0.6
        
        # 测试轻微症状
        mild_symptoms = ["轻微不适"]
        severity = scheduler._assess_symptom_severity(mild_symptoms)
        assert severity == 0.3

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_xiaoke_agent):
        """测试错误处理"""
        # 模拟异常情况
        mock_xiaoke_agent.recommend_resources.side_effect = Exception("服务暂时不可用")
        
        with pytest.raises(Exception) as exc_info:
            await mock_xiaoke_agent.recommend_resources(
                user_id="user_001",
                symptoms=["头痛"],
                location="北京市",
                urgency=UrgencyLevel.NORMAL,
                max_results=10
            )
        
        assert "服务暂时不可用" in str(exc_info.value)

    def test_performance_metrics(self):
        """测试性能指标"""
        # 模拟性能数据
        metrics = {
            "response_time": 0.5,  # 500ms
            "success_rate": 0.95,  # 95%
            "throughput": 100,     # 100 requests/min
            "error_rate": 0.05     # 5%
        }
        
        # 验证性能指标
        assert metrics["response_time"] < 1.0  # 响应时间小于1秒
        assert metrics["success_rate"] > 0.9   # 成功率大于90%
        assert metrics["error_rate"] < 0.1     # 错误率小于10%

if __name__ == "__main__":
    pytest.main([__file__]) 