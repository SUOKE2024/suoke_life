#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from internal.model.treatment import (
    TreatmentPlan, TreatmentPlanStatus, TCMTreatment, WesternTreatment,
    LifestyleAdjustment, FollowUpPlan, HerbalPrescription, HerbalComponent,
    AcupunctureTreatment, TuinaTreatment, OtherTCMTherapy, MedicationPrescription,
    MedicalProcedure, TestPlan, Referral, DietaryRecommendation, ExerciseRecommendation,
    SleepRecommendation, StressManagement, FollowUpAppointment
)

logger = logging.getLogger(__name__)


class TreatmentRepository:
    """治疗方案仓库实现"""
    
    def __init__(self, db_config):
        """
        初始化治疗方案仓库
        
        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        self._init_db()
    
    def _get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(
            host=self.db_config.host,
            port=self.db_config.port,
            user=self.db_config.user,
            password=self.db_config.password,
            dbname=self.db_config.dbname
        )
    
    def _init_db(self):
        """初始化数据库表"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # 创建治疗方案表
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS treatment_plans (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        diagnosis_id VARCHAR(36) NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        tcm_treatment JSONB,
                        western_treatment JSONB,
                        lifestyle_adjustment JSONB,
                        follow_up_plan JSONB
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_treatment_plans_user_id ON treatment_plans(user_id);
                    CREATE INDEX IF NOT EXISTS idx_treatment_plans_diagnosis_id ON treatment_plans(diagnosis_id);
                    CREATE INDEX IF NOT EXISTS idx_treatment_plans_status ON treatment_plans(status);
                    ''')
                conn.commit()
                logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def create(self, treatment_plan: TreatmentPlan) -> TreatmentPlan:
        """
        创建治疗方案
        
        Args:
            treatment_plan: 治疗方案
            
        Returns:
            TreatmentPlan: 创建的治疗方案
        """
        try:
            # 将TCM治疗方案转换为JSON
            tcm_treatment_json = None
            if treatment_plan.tcm_treatment:
                # 处理中药处方
                herbal_prescriptions = []
                for prescription in treatment_plan.tcm_treatment.herbal_prescriptions:
                    components = []
                    for component in prescription.components:
                        components.append(vars(component))
                    
                    herbal_prescriptions.append({
                        "name": prescription.name,
                        "components": components,
                        "preparation_method": prescription.preparation_method,
                        "dosage_instruction": prescription.dosage_instruction,
                        "duration": prescription.duration,
                        "precautions": prescription.precautions
                    })
                
                # 处理针灸治疗
                acupuncture_treatments = []
                for treatment in treatment_plan.tcm_treatment.acupuncture_treatments:
                    acupuncture_treatments.append(vars(treatment))
                
                # 处理推拿治疗
                tuina_treatments = []
                for treatment in treatment_plan.tcm_treatment.tuina_treatments:
                    tuina_treatments.append(vars(treatment))
                
                # 处理其他中医疗法
                other_therapies = []
                for therapy in treatment_plan.tcm_treatment.other_therapies:
                    other_therapies.append(vars(therapy))
                
                tcm_treatment_json = {
                    "herbal_prescriptions": herbal_prescriptions,
                    "acupuncture_treatments": acupuncture_treatments,
                    "tuina_treatments": tuina_treatments,
                    "other_therapies": other_therapies
                }
            
            # 将Western治疗方案转换为JSON
            western_treatment_json = None
            if treatment_plan.western_treatment:
                # 处理药物治疗
                medications = []
                for medication in treatment_plan.western_treatment.medications:
                    medications.append(vars(medication))
                
                # 处理医疗程序
                procedures = []
                for procedure in treatment_plan.western_treatment.procedures:
                    procedure_dict = vars(procedure).copy()
                    if procedure.scheduled_time:
                        procedure_dict["scheduled_time"] = procedure.scheduled_time.isoformat()
                    procedures.append(procedure_dict)
                
                # 处理检测计划
                tests = []
                for test in treatment_plan.western_treatment.tests:
                    test_dict = vars(test).copy()
                    if test.scheduled_time:
                        test_dict["scheduled_time"] = test.scheduled_time.isoformat()
                    tests.append(test_dict)
                
                # 处理转诊建议
                referrals = []
                for referral in treatment_plan.western_treatment.referrals:
                    referrals.append(vars(referral))
                
                western_treatment_json = {
                    "medications": medications,
                    "procedures": procedures,
                    "tests": tests,
                    "referrals": referrals
                }
            
            # 将生活方式调整建议转换为JSON
            lifestyle_adjustment_json = None
            if treatment_plan.lifestyle_adjustment:
                # 处理饮食建议
                dietary = []
                for recommendation in treatment_plan.lifestyle_adjustment.dietary:
                    dietary.append(vars(recommendation))
                
                # 处理运动建议
                exercise = vars(treatment_plan.lifestyle_adjustment.exercise) if treatment_plan.lifestyle_adjustment.exercise else None
                
                # 处理睡眠建议
                sleep = vars(treatment_plan.lifestyle_adjustment.sleep) if treatment_plan.lifestyle_adjustment.sleep else None
                
                # 处理压力管理
                stress_management = vars(treatment_plan.lifestyle_adjustment.stress_management) if treatment_plan.lifestyle_adjustment.stress_management else None
                
                lifestyle_adjustment_json = {
                    "dietary": dietary,
                    "exercise": exercise,
                    "sleep": sleep,
                    "stress_management": stress_management,
                    "other_recommendations": treatment_plan.lifestyle_adjustment.other_recommendations
                }
            
            # 将随访计划转换为JSON
            follow_up_plan_json = None
            if treatment_plan.follow_up_plan:
                # 处理随访预约
                appointments = []
                for appointment in treatment_plan.follow_up_plan.appointments:
                    appointment_dict = vars(appointment).copy()
                    if appointment.scheduled_time:
                        appointment_dict["scheduled_time"] = appointment.scheduled_time.isoformat()
                    appointments.append(appointment_dict)
                
                follow_up_plan_json = {
                    "appointments": appointments,
                    "monitoring_parameters": treatment_plan.follow_up_plan.monitoring_parameters,
                    "self_assessment_guide": treatment_plan.follow_up_plan.self_assessment_guide,
                    "warning_signs": treatment_plan.follow_up_plan.warning_signs
                }
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    INSERT INTO treatment_plans (
                        id, user_id, diagnosis_id, created_at, updated_at, status,
                        tcm_treatment, western_treatment, lifestyle_adjustment, follow_up_plan
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    ''', (
                        treatment_plan.id, treatment_plan.user_id, treatment_plan.diagnosis_id,
                        treatment_plan.created_at, treatment_plan.updated_at, treatment_plan.status.value,
                        json.dumps(tcm_treatment_json) if tcm_treatment_json else None,
                        json.dumps(western_treatment_json) if western_treatment_json else None,
                        json.dumps(lifestyle_adjustment_json) if lifestyle_adjustment_json else None,
                        json.dumps(follow_up_plan_json) if follow_up_plan_json else None
                    ))
                    result = cursor.fetchone()
                conn.commit()
            
            return treatment_plan
        except Exception as e:
            logger.error(f"Error creating treatment plan: {str(e)}")
            raise
    
    def get_by_id(self, plan_id: str) -> Optional[TreatmentPlan]:
        """
        通过ID获取治疗方案
        
        Args:
            plan_id: 方案ID
            
        Returns:
            Optional[TreatmentPlan]: 治疗方案，如果不存在则返回None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('SELECT * FROM treatment_plans WHERE id = %s', (plan_id,))
                    result = cursor.fetchone()
                    
                    if not result:
                        return None
                    
                    return self._map_to_entity(result)
        except Exception as e:
            logger.error(f"Error getting treatment plan by ID: {str(e)}")
            raise
    
    def update(self, treatment_plan: TreatmentPlan) -> TreatmentPlan:
        """
        更新治疗方案
        
        Args:
            treatment_plan: 治疗方案
            
        Returns:
            TreatmentPlan: 更新后的治疗方案
        """
        try:
            # 将TCM治疗方案转换为JSON
            tcm_treatment_json = None
            if treatment_plan.tcm_treatment:
                # 处理中药处方
                herbal_prescriptions = []
                for prescription in treatment_plan.tcm_treatment.herbal_prescriptions:
                    components = []
                    for component in prescription.components:
                        components.append(vars(component))
                    
                    herbal_prescriptions.append({
                        "name": prescription.name,
                        "components": components,
                        "preparation_method": prescription.preparation_method,
                        "dosage_instruction": prescription.dosage_instruction,
                        "duration": prescription.duration,
                        "precautions": prescription.precautions
                    })
                
                # 处理针灸治疗
                acupuncture_treatments = []
                for treatment in treatment_plan.tcm_treatment.acupuncture_treatments:
                    acupuncture_treatments.append(vars(treatment))
                
                # 处理推拿治疗
                tuina_treatments = []
                for treatment in treatment_plan.tcm_treatment.tuina_treatments:
                    tuina_treatments.append(vars(treatment))
                
                # 处理其他中医疗法
                other_therapies = []
                for therapy in treatment_plan.tcm_treatment.other_therapies:
                    other_therapies.append(vars(therapy))
                
                tcm_treatment_json = {
                    "herbal_prescriptions": herbal_prescriptions,
                    "acupuncture_treatments": acupuncture_treatments,
                    "tuina_treatments": tuina_treatments,
                    "other_therapies": other_therapies
                }
            
            # 将Western治疗方案转换为JSON
            western_treatment_json = None
            if treatment_plan.western_treatment:
                # 处理药物治疗
                medications = []
                for medication in treatment_plan.western_treatment.medications:
                    medications.append(vars(medication))
                
                # 处理医疗程序
                procedures = []
                for procedure in treatment_plan.western_treatment.procedures:
                    procedure_dict = vars(procedure).copy()
                    if procedure.scheduled_time:
                        procedure_dict["scheduled_time"] = procedure.scheduled_time.isoformat()
                    procedures.append(procedure_dict)
                
                # 处理检测计划
                tests = []
                for test in treatment_plan.western_treatment.tests:
                    test_dict = vars(test).copy()
                    if test.scheduled_time:
                        test_dict["scheduled_time"] = test.scheduled_time.isoformat()
                    tests.append(test_dict)
                
                # 处理转诊建议
                referrals = []
                for referral in treatment_plan.western_treatment.referrals:
                    referrals.append(vars(referral))
                
                western_treatment_json = {
                    "medications": medications,
                    "procedures": procedures,
                    "tests": tests,
                    "referrals": referrals
                }
            
            # 将生活方式调整建议转换为JSON
            lifestyle_adjustment_json = None
            if treatment_plan.lifestyle_adjustment:
                # 处理饮食建议
                dietary = []
                for recommendation in treatment_plan.lifestyle_adjustment.dietary:
                    dietary.append(vars(recommendation))
                
                # 处理运动建议
                exercise = vars(treatment_plan.lifestyle_adjustment.exercise) if treatment_plan.lifestyle_adjustment.exercise else None
                
                # 处理睡眠建议
                sleep = vars(treatment_plan.lifestyle_adjustment.sleep) if treatment_plan.lifestyle_adjustment.sleep else None
                
                # 处理压力管理
                stress_management = vars(treatment_plan.lifestyle_adjustment.stress_management) if treatment_plan.lifestyle_adjustment.stress_management else None
                
                lifestyle_adjustment_json = {
                    "dietary": dietary,
                    "exercise": exercise,
                    "sleep": sleep,
                    "stress_management": stress_management,
                    "other_recommendations": treatment_plan.lifestyle_adjustment.other_recommendations
                }
            
            # 将随访计划转换为JSON
            follow_up_plan_json = None
            if treatment_plan.follow_up_plan:
                # 处理随访预约
                appointments = []
                for appointment in treatment_plan.follow_up_plan.appointments:
                    appointment_dict = vars(appointment).copy()
                    if appointment.scheduled_time:
                        appointment_dict["scheduled_time"] = appointment.scheduled_time.isoformat()
                    appointments.append(appointment_dict)
                
                follow_up_plan_json = {
                    "appointments": appointments,
                    "monitoring_parameters": treatment_plan.follow_up_plan.monitoring_parameters,
                    "self_assessment_guide": treatment_plan.follow_up_plan.self_assessment_guide,
                    "warning_signs": treatment_plan.follow_up_plan.warning_signs
                }
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    UPDATE treatment_plans SET
                        updated_at = %s,
                        status = %s,
                        tcm_treatment = %s,
                        western_treatment = %s,
                        lifestyle_adjustment = %s,
                        follow_up_plan = %s
                    WHERE id = %s
                    RETURNING *
                    ''', (
                        treatment_plan.updated_at,
                        treatment_plan.status.value,
                        json.dumps(tcm_treatment_json) if tcm_treatment_json else None,
                        json.dumps(western_treatment_json) if western_treatment_json else None,
                        json.dumps(lifestyle_adjustment_json) if lifestyle_adjustment_json else None,
                        json.dumps(follow_up_plan_json) if follow_up_plan_json else None,
                        treatment_plan.id
                    ))
                    result = cursor.fetchone()
                    
                    if not result:
                        raise ValueError(f"Treatment plan with ID {treatment_plan.id} not found")
                    
                conn.commit()
            
            return treatment_plan
        except Exception as e:
            logger.error(f"Error updating treatment plan: {str(e)}")
            raise
    
    def list(self, filters: Dict[str, Any], page: int = 1, page_size: int = 10) -> Tuple[List[TreatmentPlan], int]:
        """
        列出治疗方案
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页记录数
            
        Returns:
            Tuple[List[TreatmentPlan], int]: 治疗方案列表和总记录数
        """
        try:
            query_conditions = []
            query_params = []
            
            # 处理过滤条件
            if "user_id" in filters:
                query_conditions.append("user_id = %s")
                query_params.append(filters["user_id"])
                
            if "diagnosis_id" in filters:
                query_conditions.append("diagnosis_id = %s")
                query_params.append(filters["diagnosis_id"])
                
            if "status" in filters:
                query_conditions.append("status = %s")
                status_value = filters["status"].value if isinstance(filters["status"], TreatmentPlanStatus) else filters["status"]
                query_params.append(status_value)
            
            # 构建查询条件
            where_clause = ""
            if query_conditions:
                where_clause = "WHERE " + " AND ".join(query_conditions)
            
            # 计算总记录数
            count_query = f"SELECT COUNT(*) as total FROM treatment_plans {where_clause}"
            
            # 查询分页数据
            offset = (page - 1) * page_size
            data_query = f'''
            SELECT * FROM treatment_plans
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            '''
            query_params.extend([page_size, offset])
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 获取总记录数
                    cursor.execute(count_query, query_params[:-2] if query_params else None)
                    total = cursor.fetchone()["total"]
                    
                    # 获取分页数据
                    cursor.execute(data_query, query_params)
                    results = cursor.fetchall()
                    
                    # 转换为领域模型
                    treatment_plans = []
                    for result in results:
                        treatment_plans.append(self._map_to_entity(result))
                    
                    return treatment_plans, total
        except Exception as e:
            logger.error(f"Error listing treatment plans: {str(e)}")
            raise
    
    def _map_to_entity(self, result: Dict[str, Any]) -> TreatmentPlan:
        """
        将数据库结果映射为治疗方案实体
        
        Args:
            result: 数据库结果
            
        Returns:
            TreatmentPlan: 治疗方案实体
        """
        # 解析状态
        status = TreatmentPlanStatus(result["status"])
        
        # 解析TCM治疗方案
        tcm_treatment = None
        if result["tcm_treatment"]:
            tcm_json = result["tcm_treatment"]
            
            # 解析中药处方
            herbal_prescriptions = []
            if "herbal_prescriptions" in tcm_json:
                for prescription_json in tcm_json["herbal_prescriptions"]:
                    components = []
                    for component_json in prescription_json["components"]:
                        components.append(HerbalComponent(
                            herb_name=component_json["herb_name"],
                            quantity=component_json["quantity"],
                            unit=component_json["unit"],
                            preparation=component_json.get("preparation")
                        ))
                    
                    herbal_prescriptions.append(HerbalPrescription(
                        name=prescription_json["name"],
                        components=components,
                        preparation_method=prescription_json.get("preparation_method"),
                        dosage_instruction=prescription_json.get("dosage_instruction"),
                        duration=prescription_json.get("duration"),
                        precautions=prescription_json.get("precautions", [])
                    ))
            
            # 解析针灸治疗
            acupuncture_treatments = []
            if "acupuncture_treatments" in tcm_json:
                for treatment_json in tcm_json["acupuncture_treatments"]:
                    acupuncture_treatments.append(AcupunctureTreatment(
                        acupoints=treatment_json.get("acupoints", []),
                        technique=treatment_json.get("technique"),
                        duration=treatment_json.get("duration"),
                        frequency=treatment_json.get("frequency"),
                        total_sessions=treatment_json.get("total_sessions", 0)
                    ))
            
            # 解析推拿治疗
            tuina_treatments = []
            if "tuina_treatments" in tcm_json:
                for treatment_json in tcm_json["tuina_treatments"]:
                    tuina_treatments.append(TuinaTreatment(
                        techniques=treatment_json.get("techniques", []),
                        target_areas=treatment_json.get("target_areas", []),
                        duration=treatment_json.get("duration"),
                        frequency=treatment_json.get("frequency"),
                        total_sessions=treatment_json.get("total_sessions", 0)
                    ))
            
            # 解析其他中医疗法
            other_therapies = []
            if "other_therapies" in tcm_json:
                for therapy_json in tcm_json["other_therapies"]:
                    other_therapies.append(OtherTCMTherapy(
                        therapy_name=therapy_json["therapy_name"],
                        description=therapy_json.get("description"),
                        application_method=therapy_json.get("application_method"),
                        duration=therapy_json.get("duration"),
                        frequency=therapy_json.get("frequency")
                    ))
            
            tcm_treatment = TCMTreatment(
                herbal_prescriptions=herbal_prescriptions,
                acupuncture_treatments=acupuncture_treatments,
                tuina_treatments=tuina_treatments,
                other_therapies=other_therapies
            )
        
        # 解析Western治疗方案
        western_treatment = None
        if result["western_treatment"]:
            western_json = result["western_treatment"]
            
            # 解析药物治疗
            medications = []
            if "medications" in western_json:
                for medication_json in western_json["medications"]:
                    medications.append(MedicationPrescription(
                        medication_name=medication_json["medication_name"],
                        dosage=medication_json["dosage"],
                        route=medication_json["route"],
                        frequency=medication_json["frequency"],
                        duration=medication_json["duration"],
                        side_effects=medication_json.get("side_effects", []),
                        precautions=medication_json.get("precautions", [])
                    ))
            
            # 解析医疗程序
            procedures = []
            if "procedures" in western_json:
                for procedure_json in western_json["procedures"]:
                    scheduled_time = None
                    if "scheduled_time" in procedure_json and procedure_json["scheduled_time"]:
                        scheduled_time = datetime.fromisoformat(procedure_json["scheduled_time"])
                    
                    procedures.append(MedicalProcedure(
                        procedure_name=procedure_json["procedure_name"],
                        description=procedure_json.get("description"),
                        location=procedure_json.get("location"),
                        scheduled_time=scheduled_time,
                        preparation=procedure_json.get("preparation"),
                        aftercare=procedure_json.get("aftercare")
                    ))
            
            # 解析检测计划
            tests = []
            if "tests" in western_json:
                for test_json in western_json["tests"]:
                    scheduled_time = None
                    if "scheduled_time" in test_json and test_json["scheduled_time"]:
                        scheduled_time = datetime.fromisoformat(test_json["scheduled_time"])
                    
                    tests.append(TestPlan(
                        test_name=test_json["test_name"],
                        purpose=test_json.get("purpose"),
                        facility=test_json.get("facility"),
                        scheduled_time=scheduled_time,
                        preparation=test_json.get("preparation")
                    ))
            
            # 解析转诊建议
            referrals = []
            if "referrals" in western_json:
                for referral_json in western_json["referrals"]:
                    referrals.append(Referral(
                        specialist_type=referral_json["specialist_type"],
                        reason=referral_json.get("reason"),
                        urgency=referral_json.get("urgency", "ROUTINE"),
                        preferred_facility=referral_json.get("preferred_facility")
                    ))
            
            western_treatment = WesternTreatment(
                medications=medications,
                procedures=procedures,
                tests=tests,
                referrals=referrals
            )
        
        # 解析生活方式调整建议
        lifestyle_adjustment = None
        if result["lifestyle_adjustment"]:
            lifestyle_json = result["lifestyle_adjustment"]
            
            # 解析饮食建议
            dietary = []
            if "dietary" in lifestyle_json:
                for dietary_json in lifestyle_json["dietary"]:
                    dietary.append(DietaryRecommendation(
                        foods_to_consume=dietary_json.get("foods_to_consume", []),
                        foods_to_avoid=dietary_json.get("foods_to_avoid", []),
                        meal_pattern=dietary_json.get("meal_pattern"),
                        dietary_principles=dietary_json.get("dietary_principles", []),
                        recipes=dietary_json.get("recipes", [])
                    ))
            
            # 解析运动建议
            exercise = None
            if "exercise" in lifestyle_json and lifestyle_json["exercise"]:
                exercise_json = lifestyle_json["exercise"]
                exercise = ExerciseRecommendation(
                    exercise_types=exercise_json.get("exercise_types", []),
                    intensity=exercise_json.get("intensity"),
                    duration=exercise_json.get("duration"),
                    frequency=exercise_json.get("frequency"),
                    precautions=exercise_json.get("precautions", [])
                )
            
            # 解析睡眠建议
            sleep = None
            if "sleep" in lifestyle_json and lifestyle_json["sleep"]:
                sleep_json = lifestyle_json["sleep"]
                sleep = SleepRecommendation(
                    recommended_sleep_duration=sleep_json.get("recommended_sleep_duration"),
                    sleep_hygiene_tips=sleep_json.get("sleep_hygiene_tips", []),
                    bedtime_routine=sleep_json.get("bedtime_routine")
                )
            
            # 解析压力管理
            stress_management = None
            if "stress_management" in lifestyle_json and lifestyle_json["stress_management"]:
                stress_json = lifestyle_json["stress_management"]
                stress_management = StressManagement(
                    relaxation_techniques=stress_json.get("relaxation_techniques", []),
                    mindfulness_practices=stress_json.get("mindfulness_practices", []),
                    daily_routine_adjustment=stress_json.get("daily_routine_adjustment")
                )
            
            lifestyle_adjustment = LifestyleAdjustment(
                dietary=dietary,
                exercise=exercise,
                sleep=sleep,
                stress_management=stress_management,
                other_recommendations=lifestyle_json.get("other_recommendations", [])
            )
        
        # 解析随访计划
        follow_up_plan = None
        if result["follow_up_plan"]:
            follow_up_json = result["follow_up_plan"]
            
            # 解析随访预约
            appointments = []
            if "appointments" in follow_up_json:
                for appointment_json in follow_up_json["appointments"]:
                    scheduled_time = None
                    if "scheduled_time" in appointment_json and appointment_json["scheduled_time"]:
                        scheduled_time = datetime.fromisoformat(appointment_json["scheduled_time"])
                    
                    appointments.append(FollowUpAppointment(
                        appointment_type=appointment_json["appointment_type"],
                        scheduled_time=scheduled_time,
                        provider=appointment_json.get("provider"),
                        purpose=appointment_json.get("purpose")
                    ))
            
            follow_up_plan = FollowUpPlan(
                appointments=appointments,
                monitoring_parameters=follow_up_json.get("monitoring_parameters", []),
                self_assessment_guide=follow_up_json.get("self_assessment_guide"),
                warning_signs=follow_up_json.get("warning_signs", [])
            )
        
        # 创建治疗方案
        return TreatmentPlan(
            id=result["id"],
            user_id=result["user_id"],
            diagnosis_id=result["diagnosis_id"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            status=status,
            tcm_treatment=tcm_treatment,
            western_treatment=western_treatment,
            lifestyle_adjustment=lifestyle_adjustment,
            follow_up_plan=follow_up_plan
        )