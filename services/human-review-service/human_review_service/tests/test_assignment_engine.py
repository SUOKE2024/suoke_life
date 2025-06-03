"""
任务分配引擎测试
Assignment Engine Tests

测试任务分配引擎的各种功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from human_review_service.core.assignment_engine import (
    AssignmentEngine,
    AssignmentStrategy,
    LoadBalancer,
    AssignmentResult,
)
from human_review_service.core.models import (
    ReviewerDB,
    ReviewTaskDB,
    ReviewerStatus,
    ReviewStatus,
    ReviewType,
    ReviewPriority,
)


class TestAssignmentEngine:
    """任务分配引擎测试"""

    def test_init_engine(self):
        """测试初始化分配引擎"""
        engine = AssignmentEngine()
        assert engine is not None
        assert hasattr(engine, 'assign_task')

    @pytest.mark.asyncio
    async def test_round_robin_assignment(self):
        """测试轮询分配策略"""
        engine = AssignmentEngine()
        
        # 创建模拟审核员
        reviewers = [
            ReviewerDB(
                reviewer_id=f"reviewer_{i}",
                name=f"医生{i}",
                email=f"doctor{i}@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=0,
                status=ReviewerStatus.ACTIVE
            )
            for i in range(3)
        ]
        
        # 创建模拟任务
        task = ReviewTaskDB(
            task_id="test_task_001",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "data"},
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=3.5
        )
        
        # 模拟数据库会话
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.ROUND_ROBIN,
            session=mock_session
        )
        
        assert isinstance(result, AssignmentResult)
        assert result.assigned_reviewer_id in [r.reviewer_id for r in reviewers]
        assert result.success is True

    @pytest.mark.asyncio
    async def test_load_balanced_assignment(self):
        """测试负载均衡分配策略"""
        engine = AssignmentEngine()
        
        # 创建不同负载的审核员
        reviewers = [
            ReviewerDB(
                reviewer_id="reviewer_low_load",
                name="低负载医生",
                email="low@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=1,  # 低负载
                status=ReviewerStatus.ACTIVE
            ),
            ReviewerDB(
                reviewer_id="reviewer_high_load",
                name="高负载医生",
                email="high@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=4,  # 高负载
                status=ReviewerStatus.ACTIVE
            ),
        ]
        
        task = ReviewTaskDB(
            task_id="test_task_002",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "data"},
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=3.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.LOAD_BALANCED,
            session=mock_session
        )
        
        # 应该分配给低负载的审核员
        assert result.assigned_reviewer_id == "reviewer_low_load"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_specialty_based_assignment(self):
        """测试基于专业的分配策略"""
        engine = AssignmentEngine()
        
        # 创建不同专业的审核员
        reviewers = [
            ReviewerDB(
                reviewer_id="reviewer_tcm",
                name="中医医生",
                email="tcm@example.com",
                specialties=["中医诊断", "方剂学"],
                max_concurrent_tasks=5,
                current_tasks=2,
                status=ReviewerStatus.ACTIVE
            ),
            ReviewerDB(
                reviewer_id="reviewer_western",
                name="西医医生",
                email="western@example.com",
                specialties=["内科", "外科"],
                max_concurrent_tasks=5,
                current_tasks=2,
                status=ReviewerStatus.ACTIVE
            ),
        ]
        
        # 中医相关任务
        tcm_task = ReviewTaskDB(
            task_id="test_tcm_task",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={
                "diagnosis": "脾胃虚弱",
                "treatment": "健脾益气汤"
            },
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=3.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=tcm_task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.SPECIALTY_BASED,
            session=mock_session
        )
        
        # 应该分配给中医医生
        assert result.assigned_reviewer_id == "reviewer_tcm"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_priority_based_assignment(self):
        """测试基于优先级的分配策略"""
        engine = AssignmentEngine()
        
        # 创建不同经验的审核员
        reviewers = [
            ReviewerDB(
                reviewer_id="reviewer_junior",
                name="初级医生",
                email="junior@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=2,
                status=ReviewerStatus.ACTIVE,
                experience_years=2
            ),
            ReviewerDB(
                reviewer_id="reviewer_senior",
                name="资深医生",
                email="senior@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=2,
                status=ReviewerStatus.ACTIVE,
                experience_years=10
            ),
        ]
        
        # 高优先级任务
        urgent_task = ReviewTaskDB(
            task_id="test_urgent_task",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.URGENT,
            content={"urgent": "case"},
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=8.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=urgent_task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.PRIORITY_BASED,
            session=mock_session
        )
        
        # 高优先级任务应该分配给资深医生
        assert result.assigned_reviewer_id == "reviewer_senior"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_no_available_reviewers(self):
        """测试没有可用审核员的情况"""
        engine = AssignmentEngine()
        
        task = ReviewTaskDB(
            task_id="test_task_no_reviewers",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "data"},
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=3.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=task,
            available_reviewers=[],
            strategy=AssignmentStrategy.LOAD_BALANCED,
            session=mock_session
        )
        
        assert result.success is False
        assert result.assigned_reviewer_id is None
        assert "No available reviewers" in result.reason

    @pytest.mark.asyncio
    async def test_all_reviewers_at_capacity(self):
        """测试所有审核员都达到容量上限的情况"""
        engine = AssignmentEngine()
        
        # 创建已达到容量上限的审核员
        reviewers = [
            ReviewerDB(
                reviewer_id=f"reviewer_full_{i}",
                name=f"满负荷医生{i}",
                email=f"full{i}@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=3,
                current_tasks=3,  # 已达到上限
                status=ReviewerStatus.ACTIVE
            )
            for i in range(2)
        ]
        
        task = ReviewTaskDB(
            task_id="test_task_full_capacity",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "data"},
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=3.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.LOAD_BALANCED,
            session=mock_session
        )
        
        assert result.success is False
        assert "All reviewers at capacity" in result.reason

    @pytest.mark.asyncio
    async def test_inactive_reviewers_filtered(self):
        """测试过滤非活跃审核员"""
        engine = AssignmentEngine()
        
        # 创建包含非活跃审核员的列表
        reviewers = [
            ReviewerDB(
                reviewer_id="reviewer_active",
                name="活跃医生",
                email="active@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=2,
                status=ReviewerStatus.ACTIVE
            ),
            ReviewerDB(
                reviewer_id="reviewer_inactive",
                name="非活跃医生",
                email="inactive@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=1,
                status=ReviewerStatus.INACTIVE
            ),
        ]
        
        task = ReviewTaskDB(
            task_id="test_task_filter",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "data"},
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=3.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.LOAD_BALANCED,
            session=mock_session
        )
        
        # 应该只分配给活跃的审核员
        assert result.assigned_reviewer_id == "reviewer_active"
        assert result.success is True

    def test_load_balancer_calculate_load(self):
        """测试负载均衡器的负载计算"""
        load_balancer = LoadBalancer()
        
        reviewer = ReviewerDB(
            reviewer_id="test_reviewer",
            name="测试医生",
            email="test@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
            current_tasks=2,
            status=ReviewerStatus.ACTIVE
        )
        
        load = load_balancer.calculate_load(reviewer)
        expected_load = 2 / 5  # current_tasks / max_concurrent_tasks
        
        assert load == expected_load

    def test_load_balancer_find_least_loaded(self):
        """测试找到负载最低的审核员"""
        load_balancer = LoadBalancer()
        
        reviewers = [
            ReviewerDB(
                reviewer_id="reviewer_1",
                name="医生1",
                email="doctor1@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=3,  # 负载 60%
                status=ReviewerStatus.ACTIVE
            ),
            ReviewerDB(
                reviewer_id="reviewer_2",
                name="医生2",
                email="doctor2@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=1,  # 负载 20%
                status=ReviewerStatus.ACTIVE
            ),
        ]
        
        least_loaded = load_balancer.find_least_loaded_reviewer(reviewers)
        
        assert least_loaded.reviewer_id == "reviewer_2"

    @pytest.mark.asyncio
    async def test_assignment_with_specialty_matching(self):
        """测试专业匹配的分配"""
        engine = AssignmentEngine()
        
        reviewers = [
            ReviewerDB(
                reviewer_id="reviewer_cardiology",
                name="心脏科医生",
                email="cardio@example.com",
                specialties=["心血管内科", "心电图"],
                max_concurrent_tasks=5,
                current_tasks=2,
                status=ReviewerStatus.ACTIVE
            ),
            ReviewerDB(
                reviewer_id="reviewer_general",
                name="全科医生",
                email="general@example.com",
                specialties=["全科医学"],
                max_concurrent_tasks=5,
                current_tasks=1,
                status=ReviewerStatus.ACTIVE
            ),
        ]
        
        # 心血管相关任务
        cardio_task = ReviewTaskDB(
            task_id="test_cardio_task",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={
                "symptoms": ["胸痛", "心悸"],
                "diagnosis": "心律不齐",
                "treatment": "心电图检查"
            },
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=6.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=cardio_task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.SPECIALTY_BASED,
            session=mock_session
        )
        
        # 应该分配给心脏科医生
        assert result.assigned_reviewer_id == "reviewer_cardiology"

    @pytest.mark.asyncio
    async def test_assignment_result_properties(self):
        """测试分配结果的属性"""
        engine = AssignmentEngine()
        
        reviewers = [
            ReviewerDB(
                reviewer_id="test_reviewer",
                name="测试医生",
                email="test@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
                current_tasks=2,
                status=ReviewerStatus.ACTIVE
            )
        ]
        
        task = ReviewTaskDB(
            task_id="test_task_properties",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "data"},
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=3.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.LOAD_BALANCED,
            session=mock_session
        )
        
        # 检查结果属性
        assert hasattr(result, 'success')
        assert hasattr(result, 'assigned_reviewer_id')
        assert hasattr(result, 'assignment_time')
        assert hasattr(result, 'strategy_used')
        assert hasattr(result, 'reason')
        
        assert isinstance(result.success, bool)
        assert result.strategy_used == AssignmentStrategy.LOAD_BALANCED

    @pytest.mark.asyncio
    async def test_concurrent_assignments(self):
        """测试并发分配"""
        import asyncio
        
        engine = AssignmentEngine()
        
        reviewers = [
            ReviewerDB(
                reviewer_id=f"reviewer_{i}",
                name=f"医生{i}",
                email=f"doctor{i}@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=10,
                current_tasks=0,
                status=ReviewerStatus.ACTIVE
            )
            for i in range(3)
        ]
        
        async def assign_task_async(task_id):
            task = ReviewTaskDB(
                task_id=task_id,
                review_type=ReviewType.MEDICAL_DIAGNOSIS,
                priority=ReviewPriority.NORMAL,
                content={"test": f"data_{task_id}"},
                user_id="user_123",
                agent_id="xiaoai_agent",
                status=ReviewStatus.PENDING,
                risk_score=3.5
            )
            
            mock_session = AsyncMock()
            
            return await engine.assign_task(
                task=task,
                available_reviewers=reviewers,
                strategy=AssignmentStrategy.ROUND_ROBIN,
                session=mock_session
            )
        
        # 并发分配多个任务
        tasks = [assign_task_async(f"task_{i}") for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # 检查所有分配都成功
        assert len(results) == 5
        for result in results:
            assert result.success is True
            assert result.assigned_reviewer_id is not None

    @pytest.mark.asyncio
    async def test_assignment_strategy_fallback(self):
        """测试分配策略回退"""
        engine = AssignmentEngine()
        
        # 创建没有匹配专业的审核员
        reviewers = [
            ReviewerDB(
                reviewer_id="reviewer_different_specialty",
                name="不同专业医生",
                email="different@example.com",
                specialties=["皮肤科"],  # 不匹配的专业
                max_concurrent_tasks=5,
                current_tasks=2,
                status=ReviewerStatus.ACTIVE
            )
        ]
        
        # 中医相关任务
        tcm_task = ReviewTaskDB(
            task_id="test_fallback_task",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={
                "diagnosis": "脾胃虚弱",
                "treatment": "健脾益气汤"
            },
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=3.5
        )
        
        mock_session = AsyncMock()
        
        result = await engine.assign_task(
            task=tcm_task,
            available_reviewers=reviewers,
            strategy=AssignmentStrategy.SPECIALTY_BASED,
            session=mock_session
        )
        
        # 即使专业不匹配，也应该能分配（回退到负载均衡）
        assert result.success is True
        assert result.assigned_reviewer_id == "reviewer_different_specialty" 