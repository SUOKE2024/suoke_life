"""
性能和负载测试
测试系统在高并发和大数据量下的表现
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timedelta
import uuid
import psutil
import gc

from internal.enhanced_medical_resource_service import EnhancedMedicalResourceService
from internal.service.wellness_tourism_service import WellnessTourismService, WellnessRequest, WellnessType
from internal.service.enhanced_food_agriculture_service import EnhancedFoodAgricultureService, ConstitutionType
from internal.service.famous_doctor_service import FamousDoctorService, DoctorSearchCriteria
from internal.service.intelligent_appointment_service import IntelligentAppointmentService, AppointmentType, PriorityLevel


class TestPerformanceAndLoad:
    """性能和负载测试"""

    @pytest_asyncio.fixture
    async def performance_system(self, mock_config):
        """创建性能测试系统"""
        # 优化配置以提高性能
        perf_config = mock_config.copy()
        perf_config.update({
            "cache": {
                "enabled": True,
                "ttl_seconds": 600,
                "max_size": 10000
            },
            "database": {
                "pool_size": 20,
                "max_overflow": 30,
                "pool_timeout": 30
            },
            "performance": {
                "max_concurrent_requests": 100,
                "request_timeout": 30,
                "batch_size": 50
            }
        })
        
        medical_service = EnhancedMedicalResourceService(perf_config)
        wellness_service = WellnessTourismService(perf_config)
        food_service = EnhancedFoodAgricultureService(perf_config)
        doctor_service = FamousDoctorService(perf_config)
        appointment_service = IntelligentAppointmentService(perf_config)
        
        await medical_service.initialize()
        
        system = {
            "medical": medical_service,
            "wellness": wellness_service,
            "food": food_service,
            "doctor": doctor_service,
            "appointment": appointment_service
        }
        
        yield system
        
        await medical_service.close()

    @pytest.mark.asyncio
    async def test_concurrent_food_recommendations(self, performance_system):
        """测试并发食疗推荐性能"""
        concurrent_requests = 50
        tasks = []
        
        # 记录开始时间和内存使用
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        for i in range(concurrent_requests):
            user_id = str(uuid.uuid4())
            task = performance_system["food"].get_enhanced_food_recommendations(
                user_id=user_id,
                constitution_type=ConstitutionType.BALANCED,
                health_goals=["保持健康", "增强免疫力"],
                current_symptoms=["疲劳"] if i % 2 == 0 else ["失眠"]
            )
            tasks.append(task)
        
        # 执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 记录结束时间和内存使用
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 性能分析
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        successful_results = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful_results) / len(results)
        
        # 性能断言
        assert execution_time < 15.0, f"执行时间 {execution_time:.2f}s 超过15秒限制"
        assert success_rate > 0.95, f"成功率 {success_rate:.2%} 低于95%"
        assert memory_usage < 100, f"内存使用增长 {memory_usage:.2f}MB 超过100MB"
        
        # 验证结果质量
        valid_results = [r for r in successful_results if len(r) > 0]
        assert len(valid_results) > concurrent_requests * 0.9

    @pytest.mark.asyncio
    async def test_stress_testing(self, performance_system):
        """压力测试"""
        stress_duration = 30  # 30秒压力测试
        request_interval = 0.1  # 每100ms一个请求
        
        start_time = time.time()
        completed_requests = 0
        failed_requests = 0
        
        while time.time() - start_time < stress_duration:
            try:
                # 随机选择操作类型
                operation_type = completed_requests % 4
                
                if operation_type == 0:
                    # 食疗推荐
                    await performance_system["food"].get_enhanced_food_recommendations(
                        user_id=str(uuid.uuid4()),
                        constitution_type=ConstitutionType.BALANCED,
                        health_goals=["保持健康"]
                    )
                elif operation_type == 1:
                    # 医生搜索
                    criteria = DoctorSearchCriteria(specialty="中医内科", limit=3)
                    await performance_system["doctor"].search_famous_doctors(criteria)
                elif operation_type == 2:
                    # 养生推荐
                    wellness_request = WellnessRequest(
                        request_id=str(uuid.uuid4()),
                        user_id=str(uuid.uuid4()),
                        constitution_type="平和质",
                        health_goals=["放松"],
                        preferred_wellness_types=[WellnessType.MOUNTAIN_THERAPY],
                        budget_range=(1000.0, 2000.0),
                        duration_days=2
                    )
                    await performance_system["wellness"].find_wellness_destinations(wellness_request)
                else:
                    # 预约创建
                    appointment_request = {
                        "patient_id": str(uuid.uuid4()),
                        "doctor_id": "stress_test_doctor",
                        "appointment_type": AppointmentType.CONSULTATION.value,
                        "preferred_date": (datetime.now() + timedelta(days=1)).isoformat(),
                        "time_range_start": (datetime.now() + timedelta(days=1)).replace(hour=9).isoformat(),
                        "time_range_end": (datetime.now() + timedelta(days=1)).replace(hour=10).isoformat(),
                        "symptoms": ["压力测试"],
                        "urgency_level": PriorityLevel.NORMAL.value
                    }
                    await performance_system["appointment"].create_appointment_request(appointment_request)
                
                completed_requests += 1
                
            except Exception as e:
                failed_requests += 1
                print(f"压力测试请求失败: {e}")
            
            await asyncio.sleep(request_interval)
        
        total_requests = completed_requests + failed_requests
        success_rate = completed_requests / total_requests if total_requests > 0 else 0
        requests_per_second = completed_requests / stress_duration
        
        # 压力测试验证
        assert success_rate > 0.85, f"压力测试成功率 {success_rate:.2%} 低于85%"
        assert requests_per_second > 5, f"每秒处理请求数 {requests_per_second:.1f} 低于5个/秒"
        assert completed_requests > 100, f"完成请求数 {completed_requests} 少于100个"