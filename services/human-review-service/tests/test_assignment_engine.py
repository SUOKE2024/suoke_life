"""
任务分配引擎测试
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from human_review_service.core.assignment_engine import AssignmentEngine
from human_review_service.core.models import ReviewerDB, ReviewerStatus, ReviewPriority, ReviewType


class TestAssignmentEngine:
    """任务分配引擎测试类"""

    @pytest.fixture
    def engine(self):
        """创建任务分配引擎实例"""
        return AssignmentEngine()

    @pytest.fixture
    def mock_session(self):
        """创建模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_reviewer(self):
        """创建示例审核员"""
        reviewer = Mock(spec=ReviewerDB)
        reviewer.reviewer_id = "reviewer_001"
        reviewer.name = "张医生"
        reviewer.specialties = ["中医诊断", "内科"]
        reviewer.status = ReviewerStatus.ACTIVE
        reviewer.is_available = True
        reviewer.current_task_count = 2
        reviewer.max_concurrent_tasks = 5
        reviewer.average_review_time = 30.0
        reviewer.accuracy_rate = 0.95
        reviewer.total_reviews = 100
        reviewer.priority_preference = ReviewPriority.HIGH
        reviewer.experience_level = "senior"
        # 添加缺失的属性，设置为实际数值
        reviewer.quality_score = 0.9
        reviewer.completion_rate = 0.95
        return reviewer

    def test_init(self, engine):
        """测试初始化"""
        assert engine.specialty_mapping is not None
        assert "medical_diagnosis" in engine.specialty_mapping
        assert "treatment_plan" in engine.specialty_mapping
        assert "medication_review" in engine.specialty_mapping

    @pytest.mark.asyncio
    async def test_find_best_reviewer_success(self, engine, mock_session, sample_reviewer):
        """测试成功找到最佳审核员"""
        # 模拟获取候选审核员
        with patch.object(engine, '_get_candidate_reviewers', return_value=[sample_reviewer]):
            with patch.object(engine, '_calculate_assignment_score', return_value=85.0):
                result = await engine.find_best_reviewer(
                    ReviewType.MEDICAL_DIAGNOSIS,
                    ReviewPriority.HIGH,
                    0.7,
                    mock_session
                )
                
                assert result == "reviewer_001"

    @pytest.mark.asyncio
    async def test_find_best_reviewer_no_candidates(self, engine, mock_session):
        """测试没有候选审核员的情况"""
        with patch.object(engine, '_get_candidate_reviewers', return_value=[]):
            result = await engine.find_best_reviewer(
                ReviewType.MEDICAL_DIAGNOSIS,
                ReviewPriority.HIGH,
                0.7,
                mock_session
            )
            
            assert result is None

    @pytest.mark.asyncio
    async def test_find_best_reviewer_with_exclusions(self, engine, mock_session, sample_reviewer):
        """测试排除特定审核员"""
        excluded_reviewers = ["reviewer_002", "reviewer_003"]
        
        with patch.object(engine, '_get_candidate_reviewers', return_value=[sample_reviewer]) as mock_get:
            with patch.object(engine, '_calculate_assignment_score', return_value=85.0):
                await engine.find_best_reviewer(
                    ReviewType.MEDICAL_DIAGNOSIS,
                    ReviewPriority.HIGH,
                    0.7,
                    mock_session,
                    excluded_reviewers
                )
                
                # 验证排除列表被传递
                mock_get.assert_called_once_with(
                    ReviewType.MEDICAL_DIAGNOSIS,
                    mock_session,
                    excluded_reviewers
                )

    @pytest.mark.asyncio
    async def test_find_best_reviewer_multiple_candidates(self, engine, mock_session):
        """测试多个候选审核员的情况"""
        # 创建多个审核员
        reviewer1 = Mock(spec=ReviewerDB)
        reviewer1.reviewer_id = "reviewer_001"
        reviewer1.name = "张医生"
        
        reviewer2 = Mock(spec=ReviewerDB)
        reviewer2.reviewer_id = "reviewer_002"
        reviewer2.name = "李医生"
        
        reviewer3 = Mock(spec=ReviewerDB)
        reviewer3.reviewer_id = "reviewer_003"
        reviewer3.name = "王医生"
        
        candidates = [reviewer1, reviewer2, reviewer3]
        
        # 模拟不同的评分
        def mock_score(reviewer, *args):
            scores = {
                "reviewer_001": 75.0,
                "reviewer_002": 90.0,  # 最高分
                "reviewer_003": 80.0
            }
            return scores[reviewer.reviewer_id]
        
        with patch.object(engine, '_get_candidate_reviewers', return_value=candidates):
            with patch.object(engine, '_calculate_assignment_score', side_effect=mock_score):
                result = await engine.find_best_reviewer(
                    ReviewType.MEDICAL_DIAGNOSIS,
                    ReviewPriority.HIGH,
                    0.7,
                    mock_session
                )
                
                # 应该选择评分最高的审核员
                assert result == "reviewer_002"

    @pytest.mark.asyncio
    async def test_find_best_reviewer_exception(self, engine, mock_session):
        """测试异常处理"""
        with patch.object(engine, '_get_candidate_reviewers', side_effect=Exception("Database error")):
            result = await engine.find_best_reviewer(
                ReviewType.MEDICAL_DIAGNOSIS,
                ReviewPriority.HIGH,
                0.7,
                mock_session
            )
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_candidate_reviewers_basic(self, engine, mock_session):
        """测试获取候选审核员基础功能"""
        # 这个测试需要模拟数据库查询
        mock_result = Mock()
        mock_result.scalars.return_value = []  # 直接返回空列表
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        candidates = await engine._get_candidate_reviewers(
            ReviewType.MEDICAL_DIAGNOSIS,
            mock_session
        )
        
        assert isinstance(candidates, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_candidate_reviewers_with_exclusions(self, engine, mock_session):
        """测试排除特定审核员的候选审核员获取"""
        mock_result = Mock()
        mock_result.scalars.return_value = []  # 直接返回空列表
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        excluded_reviewers = ["reviewer_001", "reviewer_002"]
        
        candidates = await engine._get_candidate_reviewers(
            ReviewType.MEDICAL_DIAGNOSIS,
            mock_session,
            excluded_reviewers
        )
        
        assert isinstance(candidates, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_assignment_score(self, engine, sample_reviewer, mock_session):
        """测试分配评分计算"""
        score = await engine._calculate_assignment_score(
            sample_reviewer,
            ReviewType.MEDICAL_DIAGNOSIS,
            ReviewPriority.HIGH,
            0.7,
            mock_session
        )
        
        assert isinstance(score, float)
        assert score >= 0.0

    def test_calculate_specialty_score_perfect_match(self, engine, sample_reviewer):
        """测试专业完全匹配的评分"""
        # 设置审核员专业与任务需求完全匹配
        sample_reviewer.specialties = ["中医诊断", "西医诊断", "内科", "全科"]
        
        score = engine._calculate_specialty_score(sample_reviewer, ReviewType.MEDICAL_DIAGNOSIS)
        
        # 完全匹配应该得到满分
        assert score == 40.0

    def test_calculate_specialty_score_partial_match(self, engine, sample_reviewer):
        """测试专业部分匹配的评分"""
        # 设置审核员专业与任务需求部分匹配
        sample_reviewer.specialties = ["中医诊断", "其他专业"]
        
        score = engine._calculate_specialty_score(sample_reviewer, ReviewType.MEDICAL_DIAGNOSIS)
        
        # 部分匹配应该得到部分分数
        assert 0.0 < score < 40.0

    def test_calculate_specialty_score_no_match(self, engine, sample_reviewer):
        """测试专业不匹配的评分"""
        # 设置审核员专业与任务需求不匹配
        sample_reviewer.specialties = ["皮肤科", "眼科"]
        
        score = engine._calculate_specialty_score(sample_reviewer, ReviewType.MEDICAL_DIAGNOSIS)
        
        # 不匹配应该得到0分
        assert score == 0.0

    def test_calculate_specialty_score_no_requirements(self, engine, sample_reviewer):
        """测试没有专业要求的评分"""
        # 创建一个不在映射中的任务类型的Mock对象
        unknown_type = Mock()
        unknown_type.value = "unknown_type"
        
        score = engine._calculate_specialty_score(sample_reviewer, unknown_type)
        
        # 没有特定要求应该得到中等分数
        assert score == 20.0

    def test_calculate_workload_score_low_load(self, engine, sample_reviewer):
        """测试低工作负载的评分"""
        sample_reviewer.current_task_count = 1
        sample_reviewer.max_concurrent_tasks = 10
        
        score = engine._calculate_workload_score(sample_reviewer)
        
        # 低负载应该得到高分
        assert score > 20.0

    def test_calculate_workload_score_high_load(self, engine, sample_reviewer):
        """测试高工作负载的评分"""
        sample_reviewer.current_task_count = 9
        sample_reviewer.max_concurrent_tasks = 10
        
        score = engine._calculate_workload_score(sample_reviewer)
        
        # 高负载应该得到低分
        assert score < 5.0

    def test_calculate_performance_score_high_performance(self, engine, sample_reviewer):
        """测试高绩效的评分"""
        sample_reviewer.accuracy_rate = 0.98
        sample_reviewer.average_review_time = 20.0
        sample_reviewer.total_reviews = 200
        # 设置实际的数值属性
        sample_reviewer.quality_score = 0.95
        sample_reviewer.completion_rate = 0.98
        
        score = engine._calculate_performance_score(sample_reviewer)
        
        # 高绩效应该得到高分
        assert score > 15.0

    def test_calculate_performance_score_low_performance(self, engine, sample_reviewer):
        """测试低绩效的评分"""
        sample_reviewer.accuracy_rate = 0.70
        sample_reviewer.average_review_time = 120.0
        sample_reviewer.total_reviews = 10
        # 设置实际的数值属性，使用更低的值
        sample_reviewer.quality_score = 0.60
        sample_reviewer.completion_rate = 0.65
        
        score = engine._calculate_performance_score(sample_reviewer)
        
        # 低绩效应该得到低分 (0.60 * 0.7 + 0.65 * 0.3) * 20 = 12.3
        assert score < 15.0

    def test_calculate_priority_score_matching_preference(self, engine, sample_reviewer):
        """测试优先级偏好匹配的评分"""
        sample_reviewer.priority_preference = ReviewPriority.HIGH
        
        score = engine._calculate_priority_score(sample_reviewer, ReviewPriority.HIGH)
        
        # HIGH优先级对于senior审核员应该得到8.0分
        assert score == 8.0

    def test_calculate_priority_score_non_matching_preference(self, engine, sample_reviewer):
        """测试优先级偏好不匹配的评分"""
        sample_reviewer.priority_preference = ReviewPriority.LOW
        
        score = engine._calculate_priority_score(sample_reviewer, ReviewPriority.HIGH)
        
        # 偏好不匹配应该得到较低分数
        assert score < 10.0

    def test_calculate_complexity_score_senior_high_complexity(self, engine, sample_reviewer):
        """测试资深审核员处理高复杂度任务的评分"""
        sample_reviewer.experience_level = "senior"
        
        score = engine._calculate_complexity_score(sample_reviewer, 0.9)
        
        # 资深审核员处理高复杂度任务应该得到高分
        assert score > 3.0

    def test_calculate_complexity_score_junior_high_complexity(self, engine, sample_reviewer):
        """测试初级审核员处理高复杂度任务的评分"""
        sample_reviewer.experience_level = "junior"
        
        score = engine._calculate_complexity_score(sample_reviewer, 0.9)
        
        # 初级审核员处理高复杂度任务应该得到低分
        assert score < 2.0

    def test_calculate_complexity_score_junior_low_complexity(self, engine, sample_reviewer):
        """测试初级审核员处理低复杂度任务的评分"""
        sample_reviewer.experience_level = "junior"
        
        score = engine._calculate_complexity_score(sample_reviewer, 0.2)
        
        # 初级审核员处理低复杂度任务应该得到较高分
        assert score > 2.0

    def test_specialty_mapping_completeness(self, engine):
        """测试专业映射的完整性"""
        expected_types = [
            "medical_diagnosis",
            "treatment_plan", 
            "medication_review",
            "nutrition_advice",
            "lifestyle_recommendation",
            "emergency_assessment"
        ]
        
        for task_type in expected_types:
            assert task_type in engine.specialty_mapping
            assert isinstance(engine.specialty_mapping[task_type], list)
            assert len(engine.specialty_mapping[task_type]) > 0

    @pytest.mark.asyncio
    async def test_concurrent_assignment_requests(self, engine, mock_session):
        """测试并发分配请求"""
        import asyncio
        
        # 模拟多个并发请求
        tasks = []
        for i in range(5):
            task = engine.find_best_reviewer(
                ReviewType.MEDICAL_DIAGNOSIS,
                ReviewPriority.HIGH,
                0.7,
                mock_session
            )
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证所有请求都能正常处理（即使返回None）
        assert len(results) == 5
        for result in results:
            assert not isinstance(result, Exception)

    def test_edge_case_empty_specialties(self, engine):
        """测试空专业列表的边界情况"""
        reviewer = Mock(spec=ReviewerDB)
        reviewer.specialties = []
        
        score = engine._calculate_specialty_score(reviewer, ReviewType.MEDICAL_DIAGNOSIS)
        
        # 空专业列表应该得到0分
        assert score == 0.0

    def test_edge_case_none_specialties(self, engine):
        """测试None专业列表的边界情况"""
        reviewer = Mock(spec=ReviewerDB)
        reviewer.specialties = None
        
        score = engine._calculate_specialty_score(reviewer, ReviewType.MEDICAL_DIAGNOSIS)
        
        # None专业列表应该得到0分
        assert score == 0.0 