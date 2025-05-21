#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from internal.model.treatment import (
    TreatmentPlan, TreatmentPlanStatus, TCMTreatment, WesternTreatment,
    LifestyleAdjustment, FollowUpPlan, HerbalPrescription, HerbalComponent,
    AcupunctureTreatment, TuinaTreatment, OtherTCMTherapy, MedicationPrescription,
    MedicalProcedure, TestPlan, Referral, DietaryRecommendation, ExerciseRecommendation,
    SleepRecommendation, StressManagement, FollowUpAppointment
)
from pkg.utils.observability import trace_method, measure_time

logger = logging.getLogger(__name__)


class TreatmentService:
    """治疗方案服务实现"""
    
    def __init__(self, repository, service_config):
        """
        初始化治疗方案服务
        
        Args:
            repository: 治疗方案仓库
            service_config: 服务配置，包含依赖服务的配置
        """
        self.repository = repository
        self.service_config = service_config
    
    @trace_method
    def generate_treatment_plan(self, user_id: str, diagnosis_id: str,
                             treatment_preferences: Optional[List[str]] = None,
                             include_western_medicine: bool = True,
                             include_tcm: bool = True) -> TreatmentPlan:
        """
        生成治疗方案
        
        Args:
            user_id: 用户ID
            diagnosis_id: 诊断ID
            treatment_preferences: 治疗偏好
            include_western_medicine: 是否包含西医治疗
            include_tcm: 是否包含中医治疗
            
        Returns:
            TreatmentPlan: 生成的治疗方案
        """
        with measure_time("生成治疗方案"):
            logger.info(f"为用户 {user_id} 生成治疗方案，基于诊断 {diagnosis_id}")
            
            # 创建基本治疗方案
            treatment_plan = TreatmentPlan.create(user_id, diagnosis_id)
            
            # 根据用户偏好生成中医治疗方案
            if include_tcm:
                tcm_treatment = self._generate_tcm_treatment(treatment_preferences)
                treatment_plan.update_tcm_treatment(tcm_treatment)
            
            # 根据用户偏好生成西医治疗方案
            if include_western_medicine:
                western_treatment = self._generate_western_treatment(treatment_preferences)
                treatment_plan.update_western_treatment(western_treatment)
            
            # 生成生活方式调整建议
            lifestyle_adjustment = self._generate_lifestyle_adjustment(include_tcm, include_western_medicine)
            treatment_plan.update_lifestyle_adjustment(lifestyle_adjustment)
            
            # 生成随访计划
            follow_up_plan = self._generate_follow_up_plan()
            treatment_plan.update_follow_up_plan(follow_up_plan)
            
            # 保存治疗方案
            saved_plan = self.repository.create(treatment_plan)
            logger.info(f"已生成治疗方案，ID: {saved_plan.id}")
            
            return saved_plan
    
    @trace_method
    def get_treatment_plan(self, plan_id: str) -> Optional[TreatmentPlan]:
        """
        获取治疗方案
        
        Args:
            plan_id: 方案ID
            
        Returns:
            Optional[TreatmentPlan]: 治疗方案，如果不存在则返回None
        """
        logger.info(f"获取治疗方案 {plan_id}")
        return self.repository.get_by_id(plan_id)
    
    @trace_method
    def update_treatment_plan_status(self, plan_id: str, status: TreatmentPlanStatus) -> Optional[TreatmentPlan]:
        """
        更新治疗方案状态
        
        Args:
            plan_id: 方案ID
            status: 新状态
            
        Returns:
            Optional[TreatmentPlan]: 更新后的治疗方案，如果不存在则返回None
        """
        logger.info(f"更新治疗方案 {plan_id} 的状态为 {status}")
        
        # 获取现有治疗方案
        treatment_plan = self.repository.get_by_id(plan_id)
        if not treatment_plan:
            logger.warning(f"治疗方案 {plan_id} 不存在")
            return None
        
        # 更新状态
        treatment_plan.update_status(status)
        
        # 保存更新后的方案
        updated_plan = self.repository.update(treatment_plan)
        logger.info(f"治疗方案 {plan_id} 状态已更新为 {status}")
        
        return updated_plan
    
    @trace_method
    def list_treatment_plans(self, user_id: str, page: int = 1, page_size: int = 10) -> tuple[List[TreatmentPlan], int]:
        """
        列出用户的治疗方案
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页记录数
            
        Returns:
            Tuple[List[TreatmentPlan], int]: 治疗方案列表和总记录数
        """
        logger.info(f"列出用户 {user_id} 的治疗方案")
        
        filters = {
            "user_id": user_id
        }
        
        return self.repository.list(filters, page, page_size)
    
    def _generate_tcm_treatment(self, treatment_preferences: Optional[List[str]] = None) -> TCMTreatment:
        """
        生成中医治疗方案
        
        Args:
            treatment_preferences: 治疗偏好
            
        Returns:
            TCMTreatment: 中医治疗方案
        """
        # 默认包含中药处方
        herbal_prescriptions = [
            HerbalPrescription(
                name="补气养阴方",
                components=[
                    HerbalComponent(
                        herb_name="黄芪",
                        quantity="30",
                        unit="克",
                        preparation="蜜炙"
                    ),
                    HerbalComponent(
                        herb_name="党参",
                        quantity="15",
                        unit="克"
                    ),
                    HerbalComponent(
                        herb_name="白术",
                        quantity="10",
                        unit="克",
                        preparation="炒"
                    ),
                    HerbalComponent(
                        herb_name="茯苓",
                        quantity="15",
                        unit="克"
                    ),
                    HerbalComponent(
                        herb_name="当归",
                        quantity="10",
                        unit="克"
                    ),
                    HerbalComponent(
                        herb_name="麦冬",
                        quantity="15",
                        unit="克"
                    ),
                    HerbalComponent(
                        herb_name="五味子",
                        quantity="6",
                        unit="克"
                    ),
                    HerbalComponent(
                        herb_name="甘草",
                        quantity="6",
                        unit="克",
                        preparation="炙"
                    )
                ],
                preparation_method="水煎服",
                dosage_instruction="每日一剂，早晚分服",
                duration="2周",
                precautions=["忌生冷", "忌辛辣"]
            )
        ]
        
        # 如果治疗偏好包含针灸
        acupuncture_treatments = []
        if treatment_preferences and "针灸" in treatment_preferences:
            acupuncture_treatments.append(
                AcupunctureTreatment(
                    acupoints=["足三里", "气海", "关元", "百会", "三阴交", "太溪"],
                    technique="平补平泻",
                    duration="30分钟",
                    frequency="每周2次",
                    total_sessions=10
                )
            )
        
        # 如果治疗偏好包含推拿
        tuina_treatments = []
        if treatment_preferences and "推拿" in treatment_preferences:
            tuina_treatments.append(
                TuinaTreatment(
                    techniques=["一指禅推法", "滚法", "揉法", "按法"],
                    target_areas=["背部", "腰部", "足部"],
                    duration="45分钟",
                    frequency="每周1次",
                    total_sessions=6
                )
            )
        
        # 其他中医疗法
        other_therapies = [
            OtherTCMTherapy(
                therapy_name="艾灸",
                description="温经散寒，调理气血",
                application_method="隔姜灸足三里、关元",
                duration="每次30分钟",
                frequency="每周2次"
            )
        ]
        
        return TCMTreatment(
            herbal_prescriptions=herbal_prescriptions,
            acupuncture_treatments=acupuncture_treatments,
            tuina_treatments=tuina_treatments,
            other_therapies=other_therapies
        )
    
    def _generate_western_treatment(self, treatment_preferences: Optional[List[str]] = None) -> WesternTreatment:
        """
        生成西医治疗方案
        
        Args:
            treatment_preferences: 治疗偏好
            
        Returns:
            WesternTreatment: 西医治疗方案
        """
        # 药物治疗
        medications = [
            MedicationPrescription(
                medication_name="维生素B族",
                dosage="1片",
                route="口服",
                frequency="每日一次",
                duration="1个月",
                side_effects=["轻微胃部不适"],
                precautions=["饭后服用"]
            ),
            MedicationPrescription(
                medication_name="辅酶Q10",
                dosage="100mg",
                route="口服",
                frequency="每日一次",
                duration="1个月",
                side_effects=[],
                precautions=["早餐后服用"]
            )
        ]
        
        # 治疗程序
        procedures = []
        if treatment_preferences and "心理治疗" in treatment_preferences:
            procedures.append(
                MedicalProcedure(
                    procedure_name="认知行为疗法",
                    description="帮助识别并改变消极思维模式",
                    location="心理咨询中心",
                    scheduled_time=datetime.now() + timedelta(days=7),
                    preparation="携带个人健康档案",
                    aftercare="记录每日情绪变化"
                )
            )
        
        # 检测计划
        tests = [
            TestPlan(
                test_name="全血细胞计数",
                purpose="监测血细胞水平",
                facility="中心实验室",
                scheduled_time=datetime.now() + timedelta(days=14),
                preparation="检查前禁食8小时"
            ),
            TestPlan(
                test_name="甲状腺功能检查",
                purpose="排除甲状腺功能异常",
                facility="中心实验室",
                scheduled_time=datetime.now() + timedelta(days=14),
                preparation="无特殊准备"
            )
        ]
        
        # 转诊建议
        referrals = []
        if treatment_preferences and "专家咨询" in treatment_preferences:
            referrals.append(
                Referral(
                    specialist_type="内分泌专家",
                    reason="进一步评估代谢功能",
                    urgency="ROUTINE",
                    preferred_facility="市中心医院"
                )
            )
        
        return WesternTreatment(
            medications=medications,
            procedures=procedures,
            tests=tests,
            referrals=referrals
        )
    
    def _generate_lifestyle_adjustment(self, include_tcm: bool, include_western_medicine: bool) -> LifestyleAdjustment:
        """
        生成生活方式调整建议
        
        Args:
            include_tcm: 是否包含中医建议
            include_western_medicine: 是否包含西医建议
            
        Returns:
            LifestyleAdjustment: 生活方式调整建议
        """
        # 饮食建议
        dietary = [
            DietaryRecommendation(
                foods_to_consume=["全谷类", "瘦肉", "深色蔬菜", "水果", "坚果", "豆类"],
                foods_to_avoid=["油炸食品", "加工肉类", "精制糖", "高盐食品"],
                meal_pattern="少量多餐，定时定量",
                dietary_principles=["平衡饮食", "注意食物多样性"],
                recipes=["燕麦牛奶早餐", "蒸鱼配菜午餐", "清炖鸡汤晚餐"]
            )
        ]
        
        # 如果包含中医建议
        if include_tcm:
            dietary.append(
                DietaryRecommendation(
                    foods_to_consume=["山药", "莲子", "枸杞", "黑芝麻", "桂圆", "红枣"],
                    foods_to_avoid=["生冷食物", "辛辣刺激食物"],
                    meal_pattern="早餐丰盛，晚餐少量",
                    dietary_principles=["食疗养生", "根据体质调整饮食"],
                    recipes=["黑芝麻糊", "山药莲子粥", "枸杞红枣茶"]
                )
            )
        
        # 运动建议
        exercise = ExerciseRecommendation(
            exercise_types=["散步", "太极", "八段锦", "游泳", "瑜伽"],
            intensity="中低强度",
            duration="每次30-45分钟",
            frequency="每周4-5次",
            precautions=["循序渐进", "避免过度劳累", "注意保暖"]
        )
        
        # 睡眠建议
        sleep = SleepRecommendation(
            recommended_sleep_duration="7-8小时",
            sleep_hygiene_tips=[
                "保持规律的作息时间",
                "睡前1小时关闭电子设备",
                "保持卧室安静、黑暗和凉爽",
                "睡前避免咖啡因和酒精",
                "建立睡前放松仪式如冥想或热水浴"
            ],
            bedtime_routine="睡前泡脚，按摩头部和脚底"
        )
        
        # 压力管理
        stress_management = StressManagement(
            relaxation_techniques=["深呼吸练习", "渐进性肌肉放松", "冥想"],
            mindfulness_practices=["正念呼吸", "行走冥想", "感恩日记"],
            daily_routine_adjustment="合理安排工作和休息，避免过度使用电子设备"
        )
        
        # 其他生活方式建议
        other_recommendations = [
            "保持良好的社交关系，定期与亲友交流",
            "培养兴趣爱好，增加生活乐趣",
            "适当接触阳光，增加维生素D的合成",
            "保持积极乐观的心态面对生活"
        ]
        
        return LifestyleAdjustment(
            dietary=dietary,
            exercise=exercise,
            sleep=sleep,
            stress_management=stress_management,
            other_recommendations=other_recommendations
        )
    
    def _generate_follow_up_plan(self) -> FollowUpPlan:
        """
        生成随访计划
        
        Returns:
            FollowUpPlan: 随访计划
        """
        now = datetime.now()
        
        # 随访预约
        appointments = [
            FollowUpAppointment(
                appointment_type="中医复诊",
                scheduled_time=now + timedelta(days=14),
                provider="中医师",
                purpose="评估中药治疗效果，调整处方"
            ),
            FollowUpAppointment(
                appointment_type="化验检查",
                scheduled_time=now + timedelta(days=30),
                provider="医学实验室",
                purpose="复查血常规和甲状腺功能"
            ),
            FollowUpAppointment(
                appointment_type="综合评估",
                scheduled_time=now + timedelta(days=45),
                provider="综合医师",
                purpose="评估整体治疗效果，制定下一阶段方案"
            )
        ]
        
        # 监测参数
        monitoring_parameters = [
            "日常能量水平（1-10分）",
            "睡眠质量（入睡时间，醒来次数，总睡眠时间）",
            "情绪状态（焦虑、抑郁、平静等）",
            "症状变化（种类、频率、强度）",
            "治疗依从性（用药、锻炼等）"
        ]
        
        # 自我评估指南
        self_assessment_guide = """
        1. 每日记录能量水平，用1-10分表示
        2. 每日记录睡眠质量和时长
        3. 记录任何不适症状及其变化
        4. 记录治疗方案执行情况
        5. 每周进行一次总结，评估整体状况变化
        """
        
        # 警示信号
        warning_signs = [
            "持续性严重疲劳，影响日常活动",
            "睡眠问题加重",
            "情绪显著恶化，出现明显焦虑或抑郁",
            "出现新的不明原因症状",
            "治疗后症状加重",
            "新出现的过敏反应或药物不良反应"
        ]
        
        return FollowUpPlan(
            appointments=appointments,
            monitoring_parameters=monitoring_parameters,
            self_assessment_guide=self_assessment_guide,
            warning_signs=warning_signs
        )