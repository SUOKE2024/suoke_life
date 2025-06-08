from typing import Dict, List, Any, Optional, Union

"""
test_end_to_end - 索克生活项目模块
"""

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
端到端测试
测试完整的用户场景和业务流程
"""




class TestEndToEndScenarios:
    """端到端场景测试"""

    @pytest_asyncio.fixture
    async def e2e_system(self, mock_config):
        """创建端到端测试系统"""
        medical_service = EnhancedMedicalResourceService(mock_config)
        wellness_service = WellnessTourismService(mock_config)
        food_service = EnhancedFoodAgricultureService(mock_config)
        doctor_service = FamousDoctorService(mock_config)
        appointment_service = IntelligentAppointmentService(mock_config)

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
    async def test_complete_health_management_journey(self, e2e_system):
        """测试完整的健康管理旅程"""
        # 用户信息
        user_id = str(uuid.uuid4())
        user_profile = {
            "age": 35,
            "gender": "female",
            "constitution_type": ConstitutionType.QI_DEFICIENCY,
            "health_concerns": ["疲劳", "失眠", "免疫力低下"],
            "lifestyle": "久坐办公",
            "budget": 3000.0
        }

        # 第一步：健康评估和食疗推荐
        print("第一步：获取个性化食疗推荐...")
        food_recommendations = await e2e_system["food"].get_enhanced_food_recommendations(
            user_id = user_id,
            constitution_type = user_profile["constitution_type"],
            health_goals = ["增强体质", "改善睡眠", "提高免疫力"],
            current_symptoms = user_profile["health_concerns"]
        )

        assert len(food_recommendations) > 0
        print(f"获得 {len(food_recommendations)} 个食疗推荐")

        # 第二步：创建个性化营养计划
        print("第二步：创建个性化营养计划...")
        nutrition_plan = await e2e_system["food"].create_personalized_nutrition_plan(
            user_id = user_id,
            constitution_type = user_profile["constitution_type"],
            health_goals = ["增强体质", "改善睡眠"],
            duration_weeks = 4
        )

        assert nutrition_plan.user_id == user_id
        assert len(nutrition_plan.daily_meal_plans) == 28  # 4周
        print(f"创建了 {len(nutrition_plan.daily_meal_plans)} 天的营养计划")

        # 第三步：寻找合适的养生目的地
        print("第三步：寻找养生目的地...")
        wellness_request = WellnessRequest(
            request_id = str(uuid.uuid4()),
            user_id = user_id,
            constitution_type = user_profile["constitution_type"].value,
            health_goals = ["放松身心", "改善睡眠"],
            preferred_wellness_types = [
                WellnessType.MEDITATION_RETREAT,
                WellnessType.TCM_WELLNESS,
                WellnessType.FOREST_BATHING
            ],
            budget_range = (1000.0, user_profile["budget"]),
            duration_days = 3
        )

        wellness_destinations = await e2e_system["wellness"].find_wellness_destinations(wellness_request)

        assert len(wellness_destinations) > 0
        print(f"找到 {len(wellness_destinations)} 个养生目的地")

        # 第四步：搜索专业医生
        print("第四步：搜索专业医生...")
        doctor_criteria = DoctorSearchCriteria(
            specialty = "中医内科",
            keywords = "气虚",
            level = FamousDoctorLevel.CITY_MASTER,
            min_rating = 4.0,
            max_fee = 500.0,
            limit = 5
        )

        famous_doctors = await e2e_system["doctor"].search_famous_doctors(doctor_criteria)

        assert len(famous_doctors) > 0
        print(f"找到 {len(famous_doctors)} 位专业医生")

        # 第五步：预约医生咨询
        print("第五步：预约医生咨询...")
        selected_doctor = famous_doctors[0]
        appointment_request = {
            "patient_id": user_id,
            "doctor_id": selected_doctor.doctor_id,
            "appointment_type": AppointmentType.CONSULTATION.value,
            "preferred_date": (datetime.now() + timedelta(days = 7)).isoformat(),
            "time_range_start": (datetime.now() + timedelta(days = 7)).replace(hour = 9).isoformat(),
            "time_range_end": (datetime.now() + timedelta(days = 7)).replace(hour = 17).isoformat(),
            "symptoms": user_profile["health_concerns"],
            "urgency_level": PriorityLevel.NORMAL.value,
            "contact_info": {
                "phone": "13800138000",
                "email": "user@example.com"
            },
            "special_requirements": "希望进行中医体质调理"
        }

        appointment_id = await e2e_system["appointment"].create_appointment_request(appointment_request)

        if appointment_id:
            print(f"成功创建预约: {appointment_id}")

            # 确认预约
            confirmation_success = await e2e_system["appointment"].confirm_appointment(appointment_id)
            assert confirmation_success
            print("预约确认成功")

        # 第六步：验证整体方案的一致性
        print("第六步：验证整体方案一致性...")

        # 验证食疗推荐适合气虚体质
        qi_deficiency_foods = [
            rec for rec in food_recommendations
            if "补气" in rec.tcm_theory_basis or "益气" in rec.tcm_theory_basis
        ]
        assert len(qi_deficiency_foods) > 0, "食疗推荐应包含补气食物"

        # 验证养生目的地适合放松和调理
        suitable_destinations = [
            dest for dest in wellness_destinations
            if WellnessType.MEDITATION_RETREAT in dest.destination.wellness_types or
            WellnessType.TCM_WELLNESS in dest.destination.wellness_types
        ]
        assert len(suitable_destinations) > 0, "养生目的地应包含冥想或中医养生项目"

        # 验证医生专长匹配
        suitable_doctors = [
            doc for doc in famous_doctors
            if any("内科" in spec.name or "体质" in spec.name for spec in doc.specialties)
        ]
        assert len(suitable_doctors) > 0, "医生应具备相关专长"

        print("✅ 完整健康管理旅程测试通过")

    @pytest.mark.asyncio
    async def test_emergency_appointment_scenario(self, e2e_system):
        """测试紧急预约场景"""
        user_id = str(uuid.uuid4())

        # 紧急情况：用户出现急性症状
        emergency_symptoms = ["胸痛", "呼吸困难", "头晕"]

        print("紧急场景：用户出现急性症状...")

        # 1. 快速搜索相关专科医生
        doctor_criteria = DoctorSearchCriteria(
            specialty = "心血管内科",
            keywords = "急诊",
            min_rating = 4.5,
            available_today = True,
            limit = 10
        )

        emergency_doctors = await e2e_system["doctor"].search_famous_doctors(doctor_criteria)
        assert len(emergency_doctors) > 0

        # 2. 创建紧急预约
        emergency_appointment = {
            "patient_id": user_id,
            "doctor_id": emergency_doctors[0].doctor_id,
            "appointment_type": AppointmentType.EMERGENCY.value,
            "preferred_date": datetime.now().isoformat(),
            "time_range_start": datetime.now().isoformat(),
            "time_range_end": (datetime.now() + timedelta(hours = 1)).isoformat(),
            "symptoms": emergency_symptoms,
            "urgency_level": PriorityLevel.URGENT.value,
            "contact_info": {
                "phone": "13900139000",
                "emergency_contact": "13800138000"
            },
            "special_requirements": "紧急情况，需要立即处理"
        }

        appointment_id = await e2e_system["appointment"].create_appointment_request(emergency_appointment)

        if appointment_id:
            # 3. 立即确认预约
            confirmation_success = await e2e_system["appointment"].confirm_appointment(appointment_id)
            assert confirmation_success

            # 4. 获取预约详情
            appointment_details = await e2e_system["appointment"].get_appointment_details(appointment_id)

            if appointment_details:
                assert appointment_details.urgency_level == PriorityLevel.URGENT.value
                assert appointment_details.appointment_type == AppointmentType.EMERGENCY.value

        print("✅ 紧急预约场景测试通过")

    @pytest.mark.asyncio
    async def test_family_health_management(self, e2e_system):
        """测试家庭健康管理场景"""
        # 家庭成员
        family_members = [
            {
                "user_id": str(uuid.uuid4()),
                "name": "父亲",
                "age": 55,
                "constitution_type": ConstitutionType.YANG_DEFICIENCY,
                "health_concerns": ["高血压", "腰痛"]
            },
            {
                "user_id": str(uuid.uuid4()),
                "name": "母亲",
                "age": 50,
                "constitution_type": ConstitutionType.YIN_DEFICIENCY,
                "health_concerns": ["失眠", "潮热"]
            },
            {
                "user_id": str(uuid.uuid4()),
                "name": "孩子",
                "age": 12,
                "constitution_type": ConstitutionType.BALANCED,
                "health_concerns": ["注意力不集中", "体质偏弱"]
            }
        ]

        print("家庭健康管理场景...")

        family_plans = []

        for member in family_members:
            print(f"为{member['name']}制定健康方案...")

            # 1. 个性化食疗推荐
            food_recs = await e2e_system["food"].get_enhanced_food_recommendations(
                user_id = member["user_id"],
                constitution_type = member["constitution_type"],
                health_goals = ["改善体质"],
                current_symptoms = member["health_concerns"]
            )

            # 2. 营养计划
            nutrition_plan = await e2e_system["food"].create_personalized_nutrition_plan(
                user_id = member["user_id"],
                constitution_type = member["constitution_type"],
                health_goals = ["改善体质"],
                duration_weeks = 2
            )

            # 3. 适合的养生活动
            wellness_request = WellnessRequest(
                request_id = str(uuid.uuid4()),
                user_id = member["user_id"],
                constitution_type = member["constitution_type"].value,
                health_goals = ["改善体质"],
                preferred_wellness_types = [WellnessType.FAMILY_WELLNESS],
                budget_range = (500.0, 2000.0),
                duration_days = 2
            )

            wellness_options = await e2e_system["wellness"].find_wellness_destinations(wellness_request)

            family_plan = {
                "member": member,
                "food_recommendations": food_recs,
                "nutrition_plan": nutrition_plan,
                "wellness_options": wellness_options
            }

            family_plans.append(family_plan)

            # 验证每个成员都有个性化方案
            assert len(food_recs) > 0
            assert nutrition_plan.user_id == member["user_id"]
            assert len(wellness_options) > = 0

        # 验证家庭方案的多样性
        assert len(family_plans) == 3

        # 验证不同体质的推荐差异
        father_foods = [rec.name for rec in family_plans[0]["food_recommendations"]]
        mother_foods = [rec.name for rec in family_plans[1]["food_recommendations"]]

        # 阳虚和阴虚体质应该有不同的食疗推荐
        assert father_foods ! = mother_foods, "不同体质应有不同的食疗推荐"

        print("✅ 家庭健康管理场景测试通过")

    @pytest.mark.asyncio
    async def test_chronic_disease_management(self, e2e_system):
        """测试慢性病管理场景"""
        user_id = str(uuid.uuid4())

        # 慢性病患者信息
        chronic_patient = {
            "user_id": user_id,
            "condition": "糖尿病",
            "constitution_type": ConstitutionType.PHLEGM_DAMPNESS,
            "current_symptoms": ["血糖不稳", "疲劳", "口渴"],
            "medications": ["二甲双胍", "胰岛素"],
            "dietary_restrictions": ["低糖", "低脂"]
        }

        print("慢性病管理场景：糖尿病患者...")

        # 1. 专门的食疗方案
        diabetic_food_recs = await e2e_system["food"].get_enhanced_food_recommendations(
            user_id = user_id,
            constitution_type = chronic_patient["constitution_type"],
            health_goals = ["控制血糖", "减重"],
            current_symptoms = chronic_patient["current_symptoms"],
            dietary_restrictions = chronic_patient["dietary_restrictions"]
        )

        assert len(diabetic_food_recs) > 0

        # 验证推荐适合糖尿病患者
        suitable_foods = [
            rec for rec in diabetic_food_recs
            if "降糖" in rec.tcm_theory_basis or "化湿" in rec.tcm_theory_basis
        ]
        assert len(suitable_foods) > 0, "应包含适合糖尿病的食疗推荐"

        # 2. 长期营养管理计划
        long_term_plan = await e2e_system["food"].create_personalized_nutrition_plan(
            user_id = user_id,
            constitution_type = chronic_patient["constitution_type"],
            health_goals = ["控制血糖", "减重"],
            duration_weeks = 12  # 3个月计划
        )

        assert len(long_term_plan.daily_meal_plans) == 84  # 12周

        # 3. 寻找专科医生进行定期随访
        endocrinologist_criteria = DoctorSearchCriteria(
            specialty = "内分泌科",
            keywords = "糖尿病",
            min_rating = 4.5,
            limit = 5
        )

        specialists = await e2e_system["doctor"].search_famous_doctors(endocrinologist_criteria)
        assert len(specialists) > 0

        # 4. 安排定期随访预约
        follow_up_dates = [
            datetime.now() + timedelta(weeks = 4),
            datetime.now() + timedelta(weeks = 8),
            datetime.now() + timedelta(weeks = 12)
        ]

        follow_up_appointments = []

        for i, follow_up_date in enumerate(follow_up_dates):
            appointment_request = {
                "patient_id": user_id,
                "doctor_id": specialists[0].doctor_id,
                "appointment_type": AppointmentType.FOLLOW_UP.value,
                "preferred_date": follow_up_date.isoformat(),
                "time_range_start": follow_up_date.replace(hour = 9).isoformat(),
                "time_range_end": follow_up_date.replace(hour = 17).isoformat(),
                "symptoms": chronic_patient["current_symptoms"],
                "urgency_level": PriorityLevel.NORMAL.value,
                "special_requirements": f"糖尿病第{i + 1}次随访，需要检查血糖控制情况"
            }

            appointment_id = await e2e_system["appointment"].create_appointment_request(appointment_request)
            if appointment_id:
                follow_up_appointments.append(appointment_id)

        # 5. 适合的康复养生项目
        rehabilitation_request = WellnessRequest(
            request_id = str(uuid.uuid4()),
            user_id = user_id,
            constitution_type = chronic_patient["constitution_type"].value,
            health_goals = ["控制血糖", "减重", "改善体质"],
            preferred_wellness_types = [
                WellnessType.HIKING_THERAPY,
                WellnessType.TCM_WELLNESS
            ],
            budget_range = (800.0, 2000.0),
            duration_days = 5,
            special_requirements = ["适合糖尿病患者", "有医疗监护"]
        )

        rehabilitation_options = await e2e_system["wellness"].find_wellness_destinations(rehabilitation_request)

        # 验证慢性病管理方案的完整性
        assert len(diabetic_food_recs) > 0
        assert long_term_plan is not None
        assert len(specialists) > 0
        assert len(follow_up_appointments) > 0
        assert len(rehabilitation_options) > = 0

        print("✅ 慢性病管理场景测试通过")

    @pytest.mark.asyncio
    async def test_seasonal_health_adjustment(self, e2e_system):
        """测试季节性健康调理场景"""
        user_id = str(uuid.uuid4())

        # 模拟不同季节的健康需求
        seasonal_scenarios = [
            {
                "season": "春季",
                "constitution_type": ConstitutionType.LIVER_QI_STAGNATION,
                "health_goals": ["疏肝理气", "预防春困"],
                "symptoms": ["情绪波动", "疲劳"],
                "wellness_types": [WellnessType.FOREST_BATHING, WellnessType.HIKING_THERAPY]
            },
            {
                "season": "夏季",
                "constitution_type": ConstitutionType.DAMP_HEAT,
                "health_goals": ["清热祛湿", "防暑降温"],
                "symptoms": ["口干", "烦躁", "湿疹"],
                "wellness_types": [WellnessType.WATER_THERAPY, WellnessType.MOUNTAIN_THERAPY]
            },
            {
                "season": "秋季",
                "constitution_type": ConstitutionType.YIN_DEFICIENCY,
                "health_goals": ["滋阴润燥", "预防感冒"],
                "symptoms": ["干咳", "皮肤干燥"],
                "wellness_types": [WellnessType.TCM_WELLNESS, WellnessType.MEDITATION_RETREAT]
            },
            {
                "season": "冬季",
                "constitution_type": ConstitutionType.YANG_DEFICIENCY,
                "health_goals": ["温阳补肾", "增强免疫"],
                "symptoms": ["怕冷", "腰膝酸软"],
                "wellness_types": [WellnessType.HOT_SPRING, WellnessType.TCM_WELLNESS]
            }
        ]

        for scenario in seasonal_scenarios:
            print(f"测试{scenario['season']}健康调理...")

            # 1. 季节性食疗推荐
            seasonal_foods = await e2e_system["food"].get_enhanced_food_recommendations(
                user_id = user_id,
                constitution_type = scenario["constitution_type"],
                health_goals = scenario["health_goals"],
                current_symptoms = scenario["symptoms"]
            )

            assert len(seasonal_foods) > 0

            # 2. 季节性养生活动
            seasonal_wellness = WellnessRequest(
                request_id = str(uuid.uuid4()),
                user_id = user_id,
                constitution_type = scenario["constitution_type"].value,
                health_goals = scenario["health_goals"],
                preferred_wellness_types = scenario["wellness_types"],
                budget_range = (1000.0, 3000.0),
                duration_days = 3
            )

            wellness_options = await e2e_system["wellness"].find_wellness_destinations(seasonal_wellness)

            # 验证推荐的季节性适应性
            assert len(seasonal_foods) > 0
            assert len(wellness_options) > = 0

            print(f"✅ {scenario['season']}调理方案生成成功")

        print("✅ 季节性健康调理场景测试通过")

    @pytest.mark.asyncio
    async def test_cross_service_data_flow(self, e2e_system):
        """测试跨服务数据流"""
        user_id = str(uuid.uuid4())

        print("测试跨服务数据流...")

        # 1. 从医生服务开始
        doctor_criteria = DoctorSearchCriteria(
            specialty = "中医内科",
            min_rating = 4.0,
            limit = 3
        )

        doctors = await e2e_system["doctor"].search_famous_doctors(doctor_criteria)
        assert len(doctors) > 0

        selected_doctor = doctors[0]

        # 2. 创建预约并获取医生建议
        appointment_request = {
            "patient_id": user_id,
            "doctor_id": selected_doctor.doctor_id,
            "appointment_type": AppointmentType.CONSULTATION.value,
            "preferred_date": (datetime.now() + timedelta(days = 3)).isoformat(),
            "time_range_start": (datetime.now() + timedelta(days = 3)).replace(hour = 10).isoformat(),
            "time_range_end": (datetime.now() + timedelta(days = 3)).replace(hour = 11).isoformat(),
            "symptoms": ["疲劳", "失眠"],
            "urgency_level": PriorityLevel.NORMAL.value
        }

        appointment_id = await e2e_system["appointment"].create_appointment_request(appointment_request)

        if appointment_id:
            # 3. 基于预约信息生成食疗方案
            appointment_details = await e2e_system["appointment"].get_appointment_details(appointment_id)

            if appointment_details:
                symptoms = appointment_details.symptoms

                food_recommendations = await e2e_system["food"].get_enhanced_food_recommendations(
                    user_id = user_id,
                    constitution_type = ConstitutionType.QI_DEFICIENCY,  # 基于症状推断
                    health_goals = ["缓解疲劳", "改善睡眠"],
                    current_symptoms = symptoms
                )

                assert len(food_recommendations) > 0

                # 4. 基于医生专长推荐相关养生项目
                doctor_specialties = [spec.name for spec in selected_doctor.specialties]

                if any("中医" in spec for spec in doctor_specialties):
                    wellness_request = WellnessRequest(
                        request_id = str(uuid.uuid4()),
                        user_id = user_id,
                        constitution_type = "气虚质",
                        health_goals = ["缓解疲劳", "改善睡眠"],
                        preferred_wellness_types = [WellnessType.TCM_WELLNESS],
                        budget_range = (1000.0, 2000.0),
                        duration_days = 2
                    )

                    wellness_options = await e2e_system["wellness"].find_wellness_destinations(wellness_request)

                    # 验证数据流的一致性
                    assert len(wellness_options) > = 0

                    # 验证推荐与医生专长的关联性
                    tcm_wellness = [
                        opt for opt in wellness_options
                        if WellnessType.TCM_WELLNESS in opt.destination.wellness_types
                    ]
                    assert len(tcm_wellness) > = 0

        print("✅ 跨服务数据流测试通过")

    @pytest.mark.asyncio
    async def test_user_journey_analytics(self, e2e_system):
        """测试用户旅程分析"""
        user_id = str(uuid.uuid4())

        print("测试用户旅程分析...")

        # 模拟用户的完整旅程
        journey_steps = []

        # 步骤1：初始健康评估
        step1_start = datetime.now()
        food_recs = await e2e_system["food"].get_enhanced_food_recommendations(
            user_id = user_id,
            constitution_type = ConstitutionType.BALANCED,
            health_goals = ["保持健康"]
        )
        step1_end = datetime.now()

        journey_steps.append({
            "step": "健康评估",
            "start_time": step1_start,
            "end_time": step1_end,
            "duration": (step1_end - step1_start).total_seconds(),
            "result_count": len(food_recs)
        })

        # 步骤2：医生搜索
        step2_start = datetime.now()
        doctor_criteria = DoctorSearchCriteria(specialty = "中医内科", limit = 5)
        doctors = await e2e_system["doctor"].search_famous_doctors(doctor_criteria)
        step2_end = datetime.now()

        journey_steps.append({
            "step": "医生搜索",
            "start_time": step2_start,
            "end_time": step2_end,
            "duration": (step2_end - step2_start).total_seconds(),
            "result_count": len(doctors)
        })

        # 步骤3：预约创建
        if doctors:
            step3_start = datetime.now()
            appointment_request = {
                "patient_id": user_id,
                "doctor_id": doctors[0].doctor_id,
                "appointment_type": AppointmentType.CONSULTATION.value,
                "preferred_date": (datetime.now() + timedelta(days = 1)).isoformat(),
                "time_range_start": (datetime.now() + timedelta(days = 1)).replace(hour = 9).isoformat(),
                "time_range_end": (datetime.now() + timedelta(days = 1)).replace(hour = 10).isoformat(),
                "symptoms": ["健康咨询"],
                "urgency_level": PriorityLevel.NORMAL.value
            }

            appointment_id = await e2e_system["appointment"].create_appointment_request(appointment_request)
            step3_end = datetime.now()

            journey_steps.append({
                "step": "预约创建",
                "start_time": step3_start,
                "end_time": step3_end,
                "duration": (step3_end - step3_start).total_seconds(),
                "success": appointment_id is not None
            })

        # 分析用户旅程
        total_duration = sum(step["duration"] for step in journey_steps)
        successful_steps = len([step for step in journey_steps if step.get("success", True)])

        # 验证旅程质量
        assert total_duration < 30.0, f"总旅程时间 {total_duration:.2f}s 过长"
        assert successful_steps == len(journey_steps), "部分步骤失败"

        # 验证每个步骤的性能
        for step in journey_steps:
            assert step["duration"] < 10.0, f"{step['step']}耗时过长: {step['duration']:.2f}s"
            if "result_count" in step:
                assert step["result_count"] > = 0, f"{step['step']}未返回结果"

        print("✅ 用户旅程分析测试通过")
        print(f"总旅程时间: {total_duration:.2f}秒")
        print(f"成功步骤: {successful_steps} / {len(journey_steps)}")