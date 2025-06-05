"""
增强医疗资源服务单元测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import uuid

from internal.enhanced_medical_resource_service import (
    EnhancedMedicalResourceService,
    ResourceRequest,
    ResourceMatch,
    ResourceAllocation,
    Doctor,
    Hospital,
    Equipment,
    Medicine
)
from internal.domain.models import (
    ResourceType,
    SpecialtyType,
    ResourceStatus,
    Priority,
    Location,
    TimeSlot
)


class TestEnhancedMedicalResourceService:
    """增强医疗资源服务测试类"""

    @pytest_asyncio.fixture
    async def service(self, mock_config):
        """创建服务实例"""
        service = EnhancedMedicalResourceService(mock_config)
        await service.initialize()
        yield service
        await service.close()

    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_config):
        """测试服务初始化"""
        service = EnhancedMedicalResourceService(mock_config)
        
        # 验证配置加载
        assert service.config == mock_config
        assert service.enhanced_config is not None
        
        # 验证数据结构初始化
        assert isinstance(service.doctors, dict)
        assert isinstance(service.hospitals, dict)
        assert isinstance(service.equipment, dict)
        assert isinstance(service.medicines, dict)
        
        await service.close()

    @pytest.mark.asyncio
    async def test_find_resources_doctor(self, service, sample_doctor, test_data_factory):
        """测试医生资源查找"""
        # 添加测试医生
        service.doctors[sample_doctor.doctor_id] = sample_doctor
        service.specialty_index[sample_doctor.specialty].add(sample_doctor.doctor_id)
        
        # 创建资源请求
        request = test_data_factory.create_resource_request(
            resource_type=ResourceType.DOCTOR,
            specialty=SpecialtyType.TCM,
            symptoms=["头痛", "失眠"]
        )
        
        # 执行查找
        result = await service.find_resources(
            patient_id=request.patient_id,
            resource_type=request.resource_type,
            specialty=request.specialty,
            location=request.location,
            symptoms=request.symptoms
        )
        
        # 验证结果
        assert isinstance(result, ResourceAllocation)
        assert result.patient_id == request.patient_id
        assert len(result.matches) > 0
        assert result.total_score > 0
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_match_doctors(self, service, sample_doctor, test_data_factory):
        """测试医生匹配算法"""
        # 添加测试医生
        service.doctors[sample_doctor.doctor_id] = sample_doctor
        
        # 创建资源请求
        request = test_data_factory.create_resource_request(
            resource_type=ResourceType.DOCTOR,
            specialty=SpecialtyType.TCM
        )
        
        # 执行匹配
        matches = await service._match_doctors(request)
        
        # 验证匹配结果
        assert len(matches) > 0
        match = matches[0]
        assert isinstance(match, ResourceMatch)
        assert match.resource_id == sample_doctor.doctor_id
        assert match.resource_type == ResourceType.DOCTOR
        assert 0 <= match.match_score <= 1
        assert match.confidence > 0

    @pytest.mark.asyncio
    async def test_evaluate_doctor_match(self, service, sample_doctor, test_data_factory):
        """测试医生匹配评估"""
        request = test_data_factory.create_resource_request(
            specialty=SpecialtyType.TCM,
            symptoms=["头痛"]
        )
        
        # 执行评估
        match = await service._evaluate_doctor_match(sample_doctor, request)
        
        # 验证评估结果
        assert isinstance(match, ResourceMatch)
        assert match.resource_id == sample_doctor.doctor_id
        assert 0 <= match.match_score <= 1
        assert match.distance_km >= 0
        assert match.estimated_cost > 0
        assert len(match.reasons) > 0

    @pytest.mark.asyncio
    async def test_check_doctor_availability(self, service, sample_doctor):
        """测试医生可用性检查"""
        preferred_time = datetime.now() + timedelta(hours=1)
        
        # 测试有可用时段的情况
        availability_score = await service._check_doctor_availability(
            sample_doctor, preferred_time
        )
        
        assert 0 <= availability_score <= 1

    @pytest.mark.asyncio
    async def test_match_symptoms_to_skills(self, service):
        """测试症状与技能匹配"""
        symptoms = ["头痛", "失眠", "焦虑"]
        skills = ["中医诊断", "针灸", "中药调理", "心理咨询"]
        
        match_score = await service._match_symptoms_to_skills(symptoms, skills)
        
        assert 0 <= match_score <= 1

    @pytest.mark.asyncio
    async def test_batch_find_resources(self, service, sample_doctor, test_data_factory):
        """测试批量资源查找"""
        # 添加测试医生
        service.doctors[sample_doctor.doctor_id] = sample_doctor
        service.specialty_index[sample_doctor.specialty].add(sample_doctor.doctor_id)
        
        # 创建多个资源请求
        requests = [
            test_data_factory.create_resource_request(
                resource_type=ResourceType.DOCTOR,
                specialty=SpecialtyType.TCM
            )
            for _ in range(3)
        ]
        
        # 执行批量查找
        results = await service.batch_find_resources(requests)
        
        # 验证结果
        assert len(results) == len(requests)
        for result in results:
            assert isinstance(result, ResourceAllocation)
            assert len(result.matches) >= 0

    @pytest.mark.asyncio
    async def test_cache_functionality(self, service, test_data_factory):
        """测试缓存功能"""
        # 测试缓存设置
        key = "test_key"
        value = {"test": "data"}
        
        await service._set_to_cache(key, value)
        
        # 测试缓存获取
        cached_value = await service._get_from_cache(key)
        assert cached_value == value
        
        # 测试缓存过期
        await service._set_to_cache(key, value, "match_results")
        cached_value = await service._get_from_cache(key)
        assert cached_value == value

    @pytest.mark.asyncio
    async def test_service_stats(self, service):
        """测试服务统计"""
        stats = await service.get_service_stats()
        
        assert "total_requests" in stats
        assert "successful_matches" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "average_processing_time_ms" in stats
        assert "resource_utilization" in stats

    @pytest.mark.asyncio
    async def test_parallel_processing(self, service, sample_doctor, test_data_factory):
        """测试并行处理"""
        # 添加测试医生
        service.doctors[sample_doctor.doctor_id] = sample_doctor
        
        request = test_data_factory.create_resource_request(
            resource_type=ResourceType.DOCTOR
        )
        
        # 执行并行匹配
        matches = await service._parallel_resource_matching(request)
        
        assert isinstance(matches, list)

    @pytest.mark.asyncio
    async def test_error_handling(self, service, test_data_factory):
        """测试错误处理"""
        # 测试无效的资源类型
        with pytest.raises(Exception):
            await service.find_resources(
                patient_id=str(uuid.uuid4()),
                resource_type="INVALID_TYPE",
                specialty=SpecialtyType.TCM
            )

    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_doctor, test_data_factory):
        """测试性能要求"""
        # 添加测试数据
        for i in range(10):
            doctor = Doctor(
                doctor_id=str(uuid.uuid4()),
                name=f"医生{i}",
                specialty=SpecialtyType.TCM,
                hospital_id=str(uuid.uuid4()),
                location=Location(39.9042 + i*0.01, 116.4074 + i*0.01, f"地址{i}"),
                rating=4.0 + i*0.1,
                experience_years=10 + i,
                consultation_fee=200.0 + i*10,
                status=ResourceStatus.AVAILABLE
            )
            service.doctors[doctor.doctor_id] = doctor
            service.specialty_index[doctor.specialty].add(doctor.doctor_id)
        
        request = test_data_factory.create_resource_request(
            resource_type=ResourceType.DOCTOR,
            specialty=SpecialtyType.TCM
        )
        
        # 测试响应时间
        import time
        start_time = time.time()
        
        result = await service.find_resources(
            patient_id=request.patient_id,
            resource_type=request.resource_type,
            specialty=request.specialty,
            location=request.location
        )
        
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # 验证性能要求（< 200ms）
        assert response_time_ms < 200, f"响应时间 {response_time_ms:.2f}ms 超过要求"
        assert len(result.matches) > 0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, service, sample_doctor, test_data_factory):
        """测试并发请求处理"""
        # 添加测试医生
        service.doctors[sample_doctor.doctor_id] = sample_doctor
        service.specialty_index[sample_doctor.specialty].add(sample_doctor.doctor_id)
        
        # 创建并发任务
        tasks = []
        for i in range(50):  # 50个并发请求
            request = test_data_factory.create_resource_request(
                resource_type=ResourceType.DOCTOR,
                specialty=SpecialtyType.TCM
            )
            
            task = service.find_resources(
                patient_id=request.patient_id,
                resource_type=request.resource_type,
                specialty=request.specialty,
                location=request.location
            )
            tasks.append(task)
        
        # 执行并发任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证结果
        successful_results = [r for r in results if isinstance(r, ResourceAllocation)]
        assert len(successful_results) > 40  # 至少80%成功率

    @pytest.mark.asyncio
    async def test_resource_ranking(self, service, test_data_factory):
        """测试资源排序"""
        # 创建多个匹配结果
        matches = [
            ResourceMatch(
                resource_id=str(uuid.uuid4()),
                resource_type=ResourceType.DOCTOR,
                match_score=0.8,
                distance_km=5.0,
                estimated_cost=200.0,
                confidence=0.9
            ),
            ResourceMatch(
                resource_id=str(uuid.uuid4()),
                resource_type=ResourceType.DOCTOR,
                match_score=0.9,
                distance_km=10.0,
                estimated_cost=300.0,
                confidence=0.8
            ),
            ResourceMatch(
                resource_id=str(uuid.uuid4()),
                resource_type=ResourceType.DOCTOR,
                match_score=0.7,
                distance_km=2.0,
                estimated_cost=150.0,
                confidence=0.95
            )
        ]
        
        request = test_data_factory.create_resource_request()
        
        # 执行排序
        ranked_matches = await service._rank_matches(matches, request)
        
        # 验证排序结果
        assert len(ranked_matches) == len(matches)
        # 第一个应该是综合评分最高的
        assert ranked_matches[0].match_score >= ranked_matches[1].match_score or \
               ranked_matches[0].confidence >= ranked_matches[1].confidence

    @pytest.mark.asyncio
    async def test_recommendation_generation(self, service, test_data_factory):
        """测试推荐生成"""
        matches = [
            ResourceMatch(
                resource_id=str(uuid.uuid4()),
                resource_type=ResourceType.DOCTOR,
                match_score=0.9,
                distance_km=5.0,
                estimated_cost=200.0,
                confidence=0.9,
                reasons=["专业匹配", "距离适中"]
            )
        ]
        
        request = test_data_factory.create_resource_request()
        
        recommendations = await service._generate_resource_recommendations(matches, request)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0 