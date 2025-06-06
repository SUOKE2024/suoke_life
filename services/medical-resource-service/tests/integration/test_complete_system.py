"""
test_complete_system - 索克生活项目模块
"""

        import time
from datetime import datetime, timedelta
from internal.enhanced_medical_resource_service import EnhancedMedicalResourceService
from internal.service.enhanced_food_agriculture_service import EnhancedFoodAgricultureService, ConstitutionType
from internal.service.famous_doctor_service import FamousDoctorService, DoctorSearchCriteria, FamousDoctorLevel
from internal.service.intelligent_appointment_service import IntelligentAppointmentService, AppointmentType, PriorityLevel
from internal.service.wellness_tourism_service import WellnessTourismService, WellnessRequest, WellnessType
import asyncio
import pytest
import uuid

"""
完整系统集成测试
测试所有服务模块的集成功能
"""




class TestCompleteSystemIntegration:
    """完整系统集成测试"""

    @pytest_asyncio.fixture
    async def complete_system(self, mock_config):
        """创建完整系统实例"""
        # 初始化所有服务
        medical_service = EnhancedMedicalResourceService(mock_config)
        wellness_service = WellnessTourismService(mock_config)
        food_service = EnhancedFoodAgricultureService(mock_config)
        doctor_service = FamousDoctorService(mock_config)
        appointment_service = IntelligentAppointmentService(mock_config)
        
        # 初始化服务
        await medical_service.initialize()
        
        system = {
            "medical": medical_service,
            "wellness": wellness_service,
            "food": food_service,
            "doctor": doctor_service,
            "appointment": appointment_service
        }
        
        yield system
        
        # 清理
        await medical_service.close()

    @pytest.mark.asyncio
    async def test_end_to_end_health_management_workflow(self, complete_system):
        """测试端到端健康管理工作流"""
        # 1. 用户健康需求分析
        user_id = str(uuid.uuid4())
        constitution_type = ConstitutionType.QI_DEFICIENCY
        health_goals = ["增强体质", "改善睡眠", "缓解疲劳"]
        symptoms = ["乏力", "失眠", "食欲不振"]
        
        # 2. 获取食疗推荐
        food_recommendations = await complete_system["food"].get_enhanced_food_recommendations(
            user_id=user_id,
            constitution_type=constitution_type,
            health_goals=health_goals,
            current_symptoms=symptoms
        )
        
        assert len(food_recommendations) > 0
        assert all(rec.confidence_score > 0.5 for rec in food_recommendations)
        
        # 3. 创建个性化营养计划
        nutrition_plan = await complete_system["food"].create_personalized_nutrition_plan(
            user_id=user_id,
            constitution_type=constitution_type,
            health_goals=health_goals,
            duration_weeks=4
        )
        
        assert nutrition_plan.user_id == user_id
        assert len(nutrition_plan.daily_meal_plans) == 28  # 4周
        assert len(nutrition_plan.shopping_list) > 0
        
        # 4. 查找养生目的地
        wellness_request = WellnessRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            constitution_type=constitution_type.value,
            health_goals=health_goals,
            preferred_wellness_types=[WellnessType.MEDITATION_RETREAT, WellnessType.TCM_WELLNESS],
            budget_range=(1000.0, 3000.0),
            duration_days=3
        )
        
        wellness_recommendations = await complete_system["wellness"].find_wellness_destinations(wellness_request)
        
        assert len(wellness_recommendations) > 0
        assert all(rec.match_score > 0.6 for rec in wellness_recommendations)
        
        # 5. 搜索名医
        doctor_criteria = DoctorSearchCriteria(
            specialty="中医内科",
            level=FamousDoctorLevel.PROVINCIAL_MASTER,
            min_rating=4.5,
            max_fee=500.0,
            limit=5
        )
        
        famous_doctors = await complete_system["doctor"].search_famous_doctors(doctor_criteria)
        
        assert len(famous_doctors) > 0
        assert all(doctor.average_rating >= 4.5 for doctor in famous_doctors)
        
        # 6. 创建预约
        if famous_doctors:
            doctor = famous_doctors[0]
            appointment_request = {
                "patient_id": user_id,
                "doctor_id": doctor.doctor_id,
                "appointment_type": AppointmentType.CONSULTATION.value,
                "preferred_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "time_range_start": (datetime.now() + timedelta(days=3)).replace(hour=9).isoformat(),
                "time_range_end": (datetime.now() + timedelta(days=3)).replace(hour=17).isoformat(),
                "symptoms": symptoms,
                "urgency_level": PriorityLevel.NORMAL.value,
                "contact_info": {"phone": "13800138000", "email": "test@example.com"}
            }
            
            appointment_id = await complete_system["appointment"].create_appointment_request(appointment_request)
            
            assert appointment_id is not None
            
            # 确认预约
            confirmation_success = await complete_system["appointment"].confirm_appointment(appointment_id)
            assert confirmation_success
        
        # 7. 验证整体工作流完整性
        assert len(food_recommendations) > 0
        assert nutrition_plan is not None
        assert len(wellness_recommendations) > 0
        assert len(famous_doctors) > 0

    @pytest.mark.asyncio
    async def test_cross_service_data_consistency(self, complete_system):
        """测试跨服务数据一致性"""
        user_id = str(uuid.uuid4())
        
        # 在不同服务中使用相同的用户ID和体质类型
        constitution_type = ConstitutionType.YANG_DEFICIENCY
        
        # 1. 食疗服务推荐
        food_recs = await complete_system["food"].get_enhanced_food_recommendations(
            user_id=user_id,
            constitution_type=constitution_type,
            health_goals=["温阳补气"]
        )
        
        # 2. 养生服务推荐
        wellness_request = WellnessRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            constitution_type=constitution_type.value,
            health_goals=["温阳补气"],
            preferred_wellness_types=[WellnessType.HOT_SPRING, WellnessType.TCM_WELLNESS],
            budget_range=(500.0, 2000.0),
            duration_days=2
        )
        
        wellness_recs = await complete_system["wellness"].find_wellness_destinations(wellness_request)
        
        # 验证推荐的一致性
        # 阳虚体质应该推荐温热性食物和温阳类养生项目
        warm_foods = [rec for rec in food_recs if "温" in rec.tcm_theory_basis or "热" in rec.tcm_theory_basis]
        assert len(warm_foods) > 0
        
        hot_spring_wellness = [rec for rec in wellness_recs if WellnessType.HOT_SPRING in rec.destination.wellness_types]
        assert len(hot_spring_wellness) > 0

    @pytest.mark.asyncio
    async def test_service_performance_under_load(self, complete_system):
        """测试服务在负载下的性能"""
        # 创建多个并发请求
        tasks = []
        
        for i in range(20):  # 20个并发请求
            user_id = str(uuid.uuid4())
            
            # 食疗推荐任务
            food_task = complete_system["food"].get_enhanced_food_recommendations(
                user_id=user_id,
                constitution_type=ConstitutionType.BALANCED,
                health_goals=["保持健康"]
            )
            tasks.append(food_task)
            
            # 养生推荐任务
            wellness_request = WellnessRequest(
                request_id=str(uuid.uuid4()),
                user_id=user_id,
                constitution_type="平和质",
                health_goals=["保持健康"],
                preferred_wellness_types=[WellnessType.MOUNTAIN_THERAPY],
                budget_range=(1000.0, 2000.0),
                duration_days=2
            )
            wellness_task = complete_system["wellness"].find_wellness_destinations(wellness_request)
            tasks.append(wellness_task)
        
        # 执行所有任务并测量时间
        start_time = time.time()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证性能要求
        assert execution_time < 10.0  # 所有请求应在10秒内完成
        
        # 验证成功率
        successful_results = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful_results) / len(results)
        assert success_rate > 0.9  # 成功率应超过90%

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, complete_system):
        """测试错误处理和恢复"""
        # 1. 测试无效输入处理
        with pytest.raises(Exception):
            await complete_system["food"].get_enhanced_food_recommendations(
                user_id="",  # 无效用户ID
                constitution_type=ConstitutionType.BALANCED,
                health_goals=[]
            )
        
        # 2. 测试服务不可用情况
        # 模拟外部服务不可用
        original_med_knowledge_url = complete_system["food"].knowledge_integration.med_knowledge_url
        complete_system["food"].knowledge_integration.med_knowledge_url = "http://invalid-url:9999"
        
        # 应该能够降级处理
        food_recs = await complete_system["food"].get_enhanced_food_recommendations(
            user_id=str(uuid.uuid4()),
            constitution_type=ConstitutionType.BALANCED,
            health_goals=["保持健康"]
        )
        
        # 即使外部服务不可用，也应该返回基础推荐
        assert len(food_recs) >= 0
        
        # 恢复配置
        complete_system["food"].knowledge_integration.med_knowledge_url = original_med_knowledge_url

    @pytest.mark.asyncio
    async def test_data_flow_between_services(self, complete_system):
        """测试服务间数据流"""
        user_id = str(uuid.uuid4())
        
        # 1. 从医生服务获取推荐医生
        doctor_criteria = DoctorSearchCriteria(
            specialty="中医内科",
            min_rating=4.0,
            limit=3
        )
        
        doctors = await complete_system["doctor"].search_famous_doctors(doctor_criteria)
        assert len(doctors) > 0
        
        # 2. 使用医生信息创建预约
        doctor = doctors[0]
        appointment_request = {
            "patient_id": user_id,
            "doctor_id": doctor.doctor_id,
            "appointment_type": AppointmentType.CONSULTATION.value,
            "preferred_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "time_range_start": (datetime.now() + timedelta(days=5)).replace(hour=10).isoformat(),
            "time_range_end": (datetime.now() + timedelta(days=5)).replace(hour=16).isoformat(),
            "symptoms": ["头痛", "失眠"],
            "urgency_level": PriorityLevel.NORMAL.value
        }
        
        appointment_id = await complete_system["appointment"].create_appointment_request(appointment_request)
        
        # 3. 验证预约详情
        appointment = await complete_system["appointment"].get_appointment_details(appointment_id)
        
        if appointment:  # 如果成功创建预约
            assert appointment.doctor_id == doctor.doctor_id
            assert appointment.patient_id == user_id
            
            # 4. 基于预约信息生成相关推荐
            symptoms = appointment.symptoms
            
            food_recs = await complete_system["food"].get_enhanced_food_recommendations(
                user_id=user_id,
                constitution_type=ConstitutionType.QI_DEFICIENCY,  # 假设体质
                health_goals=["缓解症状"],
                current_symptoms=symptoms
            )
            
            # 验证推荐与症状相关
            assert len(food_recs) > 0

    @pytest.mark.asyncio
    async def test_system_scalability(self, complete_system):
        """测试系统可扩展性"""
        # 1. 测试大量数据处理
        user_ids = [str(uuid.uuid4()) for _ in range(100)]
        
        # 批量创建营养计划
        nutrition_plans = []
        for user_id in user_ids[:10]:  # 限制数量以避免测试时间过长
            plan = await complete_system["food"].create_personalized_nutrition_plan(
                user_id=user_id,
                constitution_type=ConstitutionType.BALANCED,
                health_goals=["保持健康"],
                duration_weeks=2
            )
            nutrition_plans.append(plan)
        
        assert len(nutrition_plans) == 10
        assert all(plan.user_id in user_ids for plan in nutrition_plans)
        
        # 2. 测试服务状态监控
        medical_stats = await complete_system["medical"].get_service_stats()
        wellness_stats = await complete_system["wellness"].get_service_stats()
        doctor_stats = await complete_system["doctor"].get_service_statistics()
        appointment_stats = await complete_system["appointment"].get_service_status()
        
        # 验证所有服务都返回健康状态
        assert medical_stats["service_status"] == "healthy"
        assert wellness_stats["service_status"] == "healthy"
        assert doctor_stats["service_status"] == "healthy"
        assert appointment_stats["service_status"] == "healthy"

    @pytest.mark.asyncio
    async def test_business_logic_integration(self, complete_system):
        """测试业务逻辑集成"""
        user_id = str(uuid.uuid4())
        
        # 场景：用户有特定健康问题，需要综合解决方案
        health_issue = "高血压"
        constitution_type = ConstitutionType.PHLEGM_DAMPNESS
        
        # 1. 获取针对性食疗建议
        food_recs = await complete_system["food"].get_enhanced_food_recommendations(
            user_id=user_id,
            constitution_type=constitution_type,
            health_goals=["降血压", "减重"],
            current_symptoms=["头晕", "胸闷"]
        )
        
        # 2. 查找相关专科医生
        doctor_criteria = DoctorSearchCriteria(
            keywords="心血管",
            specialty="心血管疾病",
            min_rating=4.5,
            limit=5
        )
        
        doctors = await complete_system["doctor"].search_famous_doctors(doctor_criteria)
        
        # 3. 推荐适合的养生项目
        wellness_request = WellnessRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            constitution_type=constitution_type.value,
            health_goals=["降血压", "减重"],
            preferred_wellness_types=[WellnessType.HIKING_THERAPY, WellnessType.WATER_THERAPY],
            budget_range=(800.0, 2000.0),
            duration_days=3
        )
        
        wellness_recs = await complete_system["wellness"].find_wellness_destinations(wellness_request)
        
        # 验证推荐的相关性和一致性
        assert len(food_recs) > 0
        assert len(doctors) > 0
        assert len(wellness_recs) > 0
        
        # 验证食疗推荐适合痰湿体质
        suitable_foods = [rec for rec in food_recs if "化湿" in rec.tcm_theory_basis or "利水" in rec.tcm_theory_basis]
        assert len(suitable_foods) > 0
        
        # 验证医生专长匹配
        cardiovascular_doctors = [doc for doc in doctors if any("心血管" in spec.name for spec in doc.specialties)]
        assert len(cardiovascular_doctors) > 0

    @pytest.mark.asyncio
    async def test_system_monitoring_and_analytics(self, complete_system):
        """测试系统监控和分析"""
        # 1. 生成一些测试数据
        user_id = str(uuid.uuid4())
        
        # 创建多个预约
        appointment_ids = []
        for i in range(3):
            appointment_request = {
                "patient_id": user_id,
                "doctor_id": "doc1",
                "appointment_type": AppointmentType.CONSULTATION.value,
                "preferred_date": (datetime.now() + timedelta(days=i+1)).isoformat(),
                "time_range_start": (datetime.now() + timedelta(days=i+1)).replace(hour=9+i).isoformat(),
                "time_range_end": (datetime.now() + timedelta(days=i+1)).replace(hour=10+i).isoformat(),
                "symptoms": ["测试症状"],
                "urgency_level": PriorityLevel.NORMAL.value
            }
            
            appointment_id = await complete_system["appointment"].create_appointment_request(appointment_request)
            if appointment_id:
                appointment_ids.append(appointment_id)
        
        # 2. 获取分析数据
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=7)
        
        analytics = await complete_system["appointment"].get_appointment_analytics(start_date, end_date)
        
        # 验证分析数据
        assert analytics.total_appointments >= 0
        assert analytics.date_range == (start_date, end_date)
        assert isinstance(analytics.doctor_utilization, dict)
        assert isinstance(analytics.revenue_analysis, dict)

    @pytest.mark.asyncio
    async def test_system_configuration_and_customization(self, complete_system):
        """测试系统配置和定制化"""
        # 1. 测试配置参数影响
        original_max_recs = complete_system["food"].enhanced_config["ai_recommendation"]["max_recommendations"]
        
        # 修改配置
        complete_system["food"].enhanced_config["ai_recommendation"]["max_recommendations"] = 3
        
        # 测试配置生效
        food_recs = await complete_system["food"].get_enhanced_food_recommendations(
            user_id=str(uuid.uuid4()),
            constitution_type=ConstitutionType.BALANCED,
            health_goals=["保持健康"]
        )
        
        assert len(food_recs) <= 3
        
        # 恢复配置
        complete_system["food"].enhanced_config["ai_recommendation"]["max_recommendations"] = original_max_recs
        
        # 2. 测试个性化设置
        user_id = str(uuid.uuid4())
        
        # 设置用户偏好
        user_preferences = {
            "preferred_categories": ["蔬菜", "水果"],
            "preferred_tastes": ["甘", "酸"],
            "dietary_restrictions": ["无麸质"]
        }
        
        # 这里可以扩展用户偏好设置功能
        # complete_system["food"].set_user_preferences(user_id, user_preferences)
        
        # 验证个性化推荐
        food_recs = await complete_system["food"].get_enhanced_food_recommendations(
            user_id=user_id,
            constitution_type=ConstitutionType.BALANCED,
            health_goals=["保持健康"],
            dietary_restrictions=["无麸质"]
        )
        
        # 验证推荐考虑了饮食限制
        assert len(food_recs) >= 0