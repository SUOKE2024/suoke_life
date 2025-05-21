#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from internal.model.health_risk import (
    HealthRiskAssessment, HealthRiskAssessmentRequest,
    DiseaseRisk, ConstitutionRisk, RiskLevel
)
from pkg.utils.observability import trace_method, measure_time

logger = logging.getLogger(__name__)


class HealthRiskService:
    """健康风险评估服务实现"""
    
    def __init__(self, repository, service_config):
        """
        初始化健康风险评估服务
        
        Args:
            repository: 健康风险评估仓库
            service_config: 服务配置，包含依赖服务的配置
        """
        self.repository = repository
        self.service_config = service_config
    
    @trace_method
    def assess_health_risk(self, user_id: str, health_data: Optional[Dict[str, str]] = None,
                         family_history: Optional[List[str]] = None,
                         lifestyle_factors: Optional[Dict[str, str]] = None,
                         environmental_factors: Optional[List[str]] = None,
                         include_genetic_analysis: bool = False) -> HealthRiskAssessment:
        """
        评估健康风险
        
        Args:
            user_id: 用户ID
            health_data: 健康数据
            family_history: 家族病史
            lifestyle_factors: 生活方式因素
            environmental_factors: 环境因素
            include_genetic_analysis: 是否包含基因分析
            
        Returns:
            HealthRiskAssessment: 健康风险评估结果
        """
        with measure_time("评估健康风险"):
            logger.info(f"为用户 {user_id} 评估健康风险")
            
            # 创建评估请求
            risk_request = HealthRiskAssessmentRequest.create(
                user_id=user_id,
                health_data=health_data,
                family_history=family_history,
                lifestyle_factors=lifestyle_factors,
                environmental_factors=environmental_factors,
                include_genetic_analysis=include_genetic_analysis
            )
            
            # 保存请求
            self.repository.save_request(risk_request)
            
            # 计算总体风险分数和等级
            overall_risk_score = self._calculate_overall_risk_score(
                health_data, family_history, lifestyle_factors, environmental_factors
            )
            risk_level = self._determine_risk_level(overall_risk_score)
            
            # 创建风险评估结果
            assessment = HealthRiskAssessment.create(
                user_id=user_id,
                overall_risk_score=overall_risk_score,
                risk_level=risk_level
            )
            
            # 添加疾病风险
            disease_risks = self._analyze_disease_risks(
                health_data, family_history, lifestyle_factors, environmental_factors
            )
            for disease_risk in disease_risks:
                assessment.add_disease_risk(disease_risk)
            
            # 添加体质风险（中医视角）
            constitution_risk = self._analyze_constitution_risk(
                health_data, family_history, lifestyle_factors
            )
            assessment.update_constitution_risk(constitution_risk)
            
            # 添加预防建议
            prevention_recommendations = self._generate_prevention_recommendations(
                disease_risks, constitution_risk
            )
            for recommendation in prevention_recommendations:
                assessment.add_prevention_recommendation(recommendation)
            
            # 添加生活方式建议
            lifestyle_recommendations = self._generate_lifestyle_recommendations(
                disease_risks, constitution_risk, lifestyle_factors
            )
            for recommendation in lifestyle_recommendations:
                assessment.add_lifestyle_recommendation(recommendation)
            
            # 添加建议筛查
            recommended_screenings = self._generate_recommended_screenings(
                disease_risks, constitution_risk, health_data, family_history
            )
            for screening in recommended_screenings:
                assessment.add_recommended_screening(screening)
            
            # 保存评估结果
            saved_assessment = self.repository.save_assessment(assessment)
            logger.info(f"已完成健康风险评估，ID: {saved_assessment.id}")
            
            return saved_assessment
    
    @trace_method
    def get_health_risk_assessment(self, assessment_id: str) -> Optional[HealthRiskAssessment]:
        """
        获取健康风险评估结果
        
        Args:
            assessment_id: 评估ID
            
        Returns:
            Optional[HealthRiskAssessment]: 健康风险评估结果，如果不存在则返回None
        """
        logger.info(f"获取健康风险评估 {assessment_id}")
        return self.repository.get_assessment_by_id(assessment_id)
    
    @trace_method
    def list_health_risk_assessments(self, user_id: str, page: int = 1, page_size: int = 10) -> tuple[List[HealthRiskAssessment], int]:
        """
        列出用户的健康风险评估
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页记录数
            
        Returns:
            Tuple[List[HealthRiskAssessment], int]: 健康风险评估列表和总记录数
        """
        logger.info(f"列出用户 {user_id} 的健康风险评估")
        
        filters = {
            "user_id": user_id
        }
        
        return self.repository.list_assessments(filters, page, page_size)
    
    def _calculate_overall_risk_score(self, health_data: Optional[Dict[str, str]] = None,
                                   family_history: Optional[List[str]] = None,
                                   lifestyle_factors: Optional[Dict[str, str]] = None,
                                   environmental_factors: Optional[List[str]] = None) -> int:
        """
        计算总体风险分数
        
        Args:
            health_data: 健康数据
            family_history: 家族病史
            lifestyle_factors: 生活方式因素
            environmental_factors: 环境因素
            
        Returns:
            int: 风险分数（0-100）
        """
        base_score = 30  # 基础分数
        health_score = 0
        family_score = 0
        lifestyle_score = 0
        environmental_score = 0
        
        # 计算健康数据分数
        if health_data:
            # 高血压风险
            if "blood_pressure" in health_data:
                bp_value = health_data["blood_pressure"]
                systolic, diastolic = map(int, bp_value.split("/"))
                if systolic >= 140 or diastolic >= 90:
                    health_score += 10
                elif systolic >= 130 or diastolic >= 85:
                    health_score += 5
            
            # BMI风险
            if "height" in health_data and "weight" in health_data:
                height_m = float(health_data["height"]) / 100  # 厘米转米
                weight_kg = float(health_data["weight"])
                bmi = weight_kg / (height_m * height_m)
                if bmi >= 30:
                    health_score += 10
                elif bmi >= 25:
                    health_score += 5
                elif bmi < 18.5:
                    health_score += 3
            
            # 血糖风险
            if "blood_glucose" in health_data:
                glucose = float(health_data["blood_glucose"])
                if glucose >= 7.0:
                    health_score += 10
                elif glucose >= 6.1:
                    health_score += 5
        
        # 计算家族病史分数
        if family_history:
            family_conditions = set(family_history)
            high_risk_conditions = {"心脏病", "糖尿病", "中风", "癌症", "高血压", "痴呆"}
            overlap = family_conditions.intersection(high_risk_conditions)
            family_score = min(15, len(overlap) * 5)  # 最高15分
        
        # 计算生活方式分数
        if lifestyle_factors:
            # 吸烟
            if lifestyle_factors.get("smoking") == "yes":
                lifestyle_score += 10
            elif lifestyle_factors.get("smoking") == "former":
                lifestyle_score += 5
            
            # 饮酒
            if lifestyle_factors.get("alcohol") == "heavy":
                lifestyle_score += 10
            elif lifestyle_factors.get("alcohol") == "moderate":
                lifestyle_score += 5
            
            # 运动
            if lifestyle_factors.get("exercise") == "none":
                lifestyle_score += 10
            elif lifestyle_factors.get("exercise") == "light":
                lifestyle_score += 5
            
            # 饮食
            if lifestyle_factors.get("diet") == "poor":
                lifestyle_score += 10
            elif lifestyle_factors.get("diet") == "average":
                lifestyle_score += 5
        
        # 计算环境因素分数
        if environmental_factors:
            risk_environments = {"空气污染", "水污染", "噪音污染", "接触有害化学物质", "职业暴露"}
            overlap = set(environmental_factors).intersection(risk_environments)
            environmental_score = min(10, len(overlap) * 2)  # 最高10分
        
        # 计算总分
        total_score = base_score + health_score + family_score + lifestyle_score + environmental_score
        
        # 确保分数在0-100范围内
        return min(100, max(0, total_score))
    
    def _determine_risk_level(self, risk_score: int) -> RiskLevel:
        """
        根据风险分数确定风险等级
        
        Args:
            risk_score: 风险分数
            
        Returns:
            RiskLevel: 风险等级
        """
        if risk_score >= 70:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _analyze_disease_risks(self, health_data: Optional[Dict[str, str]] = None,
                             family_history: Optional[List[str]] = None,
                             lifestyle_factors: Optional[Dict[str, str]] = None,
                             environmental_factors: Optional[List[str]] = None) -> List[DiseaseRisk]:
        """
        分析疾病风险
        
        Args:
            health_data: 健康数据
            family_history: 家族病史
            lifestyle_factors: 生活方式因素
            environmental_factors: 环境因素
            
        Returns:
            List[DiseaseRisk]: 疾病风险列表
        """
        disease_risks = []
        
        # 心血管疾病风险
        cardiovascular_risk_score = 0
        cardiovascular_risk_factors = []
        
        if health_data:
            if "blood_pressure" in health_data:
                bp_value = health_data["blood_pressure"]
                systolic, diastolic = map(int, bp_value.split("/"))
                if systolic >= 140 or diastolic >= 90:
                    cardiovascular_risk_score += 20
                    cardiovascular_risk_factors.append("高血压")
                elif systolic >= 130 or diastolic >= 85:
                    cardiovascular_risk_score += 10
                    cardiovascular_risk_factors.append("血压偏高")
            
            if "cholesterol" in health_data:
                cholesterol = float(health_data["cholesterol"])
                if cholesterol >= 6.2:
                    cardiovascular_risk_score += 20
                    cardiovascular_risk_factors.append("高胆固醇")
                elif cholesterol >= 5.2:
                    cardiovascular_risk_score += 10
                    cardiovascular_risk_factors.append("胆固醇偏高")
        
        if family_history and any(condition in ["心脏病", "中风", "高血压"] for condition in family_history):
            cardiovascular_risk_score += 15
            cardiovascular_risk_factors.append("心血管疾病家族史")
        
        if lifestyle_factors:
            if lifestyle_factors.get("smoking") == "yes":
                cardiovascular_risk_score += 15
                cardiovascular_risk_factors.append("吸烟")
            
            if lifestyle_factors.get("exercise") == "none":
                cardiovascular_risk_score += 10
                cardiovascular_risk_factors.append("缺乏运动")
            
            if lifestyle_factors.get("diet") == "poor":
                cardiovascular_risk_score += 10
                cardiovascular_risk_factors.append("不健康饮食")
        
        # 确定风险等级
        cardiovascular_risk_level = self._determine_risk_level(cardiovascular_risk_score)
        
        # 预防措施
        cardiovascular_preventive_measures = [
            "定期监测血压和血脂",
            "健康饮食，减少盐和饱和脂肪摄入",
            "规律运动，每周至少150分钟中等强度运动",
            "保持健康体重",
            "不吸烟，限制酒精摄入",
            "控制压力"
        ]
        
        # 添加心血管疾病风险
        disease_risks.append(
            DiseaseRisk(
                disease_name="心血管疾病",
                risk_score=cardiovascular_risk_score,
                risk_level=cardiovascular_risk_level,
                risk_factors=cardiovascular_risk_factors,
                preventive_measures=cardiovascular_preventive_measures
            )
        )
        
        # 糖尿病风险
        diabetes_risk_score = 0
        diabetes_risk_factors = []
        
        if health_data:
            if "blood_glucose" in health_data:
                glucose = float(health_data["blood_glucose"])
                if glucose >= 7.0:
                    diabetes_risk_score += 30
                    diabetes_risk_factors.append("空腹血糖升高")
                elif glucose >= 6.1:
                    diabetes_risk_score += 15
                    diabetes_risk_factors.append("空腹血糖受损")
            
            if "height" in health_data and "weight" in health_data:
                height_m = float(health_data["height"]) / 100  # 厘米转米
                weight_kg = float(health_data["weight"])
                bmi = weight_kg / (height_m * height_m)
                if bmi >= 30:
                    diabetes_risk_score += 15
                    diabetes_risk_factors.append("肥胖")
                elif bmi >= 25:
                    diabetes_risk_score += 10
                    diabetes_risk_factors.append("超重")
        
        if family_history and "糖尿病" in family_history:
            diabetes_risk_score += 15
            diabetes_risk_factors.append("糖尿病家族史")
        
        if lifestyle_factors:
            if lifestyle_factors.get("exercise") == "none":
                diabetes_risk_score += 10
                diabetes_risk_factors.append("缺乏运动")
            
            if lifestyle_factors.get("diet") == "poor":
                diabetes_risk_score += 10
                diabetes_risk_factors.append("不健康饮食")
        
        # 确定风险等级
        diabetes_risk_level = self._determine_risk_level(diabetes_risk_score)
        
        # 预防措施
        diabetes_preventive_measures = [
            "定期检测血糖水平",
            "控制体重，保持健康体重",
            "健康饮食，减少精制碳水化合物和糖的摄入",
            "规律运动，每周至少150分钟有氧运动",
            "避免久坐不动的生活方式",
            "定期进行健康检查"
        ]
        
        # 添加糖尿病风险
        disease_risks.append(
            DiseaseRisk(
                disease_name="糖尿病",
                risk_score=diabetes_risk_score,
                risk_level=diabetes_risk_level,
                risk_factors=diabetes_risk_factors,
                preventive_measures=diabetes_preventive_measures
            )
        )
        
        return disease_risks
    
    def _analyze_constitution_risk(self, health_data: Optional[Dict[str, str]] = None,
                                 family_history: Optional[List[str]] = None,
                                 lifestyle_factors: Optional[Dict[str, str]] = None) -> ConstitutionRisk:
        """
        分析体质风险（中医视角）
        
        Args:
            health_data: 健康数据
            family_history: 家族病史
            lifestyle_factors: 生活方式因素
            
        Returns:
            ConstitutionRisk: 体质风险
        """
        # 根据输入数据推断体质类型
        # 在实际应用中，这应该基于更复杂的算法和数据分析
        constitution_type = "气虚质"
        imbalances = ["气虚", "阴虚"]
        vulnerable_systems = ["脾胃系统", "肺系统"]
        protective_measures = [
            "食补养气，如山药、大枣、黑芝麻等",
            "适当运动，如太极、八段锦等",
            "注意保暖，避免受寒",
            "定期艾灸足三里、关元等穴位",
            "保持情绪稳定，避免过度劳累",
            "保证充足睡眠，早睡早起"
        ]
        
        return ConstitutionRisk(
            constitution_type=constitution_type,
            imbalances=imbalances,
            vulnerable_systems=vulnerable_systems,
            protective_measures=protective_measures
        )
    
    def _generate_prevention_recommendations(self, disease_risks: List[DiseaseRisk],
                                          constitution_risk: ConstitutionRisk) -> List[str]:
        """
        生成预防建议
        
        Args:
            disease_risks: 疾病风险
            constitution_risk: 体质风险
            
        Returns:
            List[str]: 预防建议列表
        """
        recommendations = []
        
        # 根据疾病风险添加建议
        for risk in disease_risks:
            if risk.risk_level == RiskLevel.HIGH:
                recommendations.append(f"高度关注 {risk.disease_name} 风险，建议咨询专业医生")
            
            # 添加该疾病的预防措施
            for measure in risk.preventive_measures:
                if measure not in recommendations:
                    recommendations.append(measure)
        
        # 根据体质风险添加建议
        for measure in constitution_risk.protective_measures:
            if measure not in recommendations:
                recommendations.append(measure)
        
        # 添加通用预防建议
        general_recommendations = [
            "定期体检，建立健康档案",
            "保持健康的生活方式，包括均衡饮食和适当运动",
            "避免过度劳累，保持充足的睡眠",
            "保持良好的心理状态，学习应对压力"
        ]
        
        for recommendation in general_recommendations:
            if recommendation not in recommendations:
                recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_lifestyle_recommendations(self, disease_risks: List[DiseaseRisk],
                                          constitution_risk: ConstitutionRisk,
                                          lifestyle_factors: Optional[Dict[str, str]] = None) -> List[str]:
        """
        生成生活方式建议
        
        Args:
            disease_risks: 疾病风险
            constitution_risk: 体质风险
            lifestyle_factors: 生活方式因素
            
        Returns:
            List[str]: 生活方式建议列表
        """
        recommendations = []
        
        # 饮食建议
        diet_recommendations = [
            "均衡饮食，确保摄入足够的蔬菜、水果、全谷物和优质蛋白",
            "限制盐和添加糖的摄入",
            "避免过多摄入加工食品和饱和脂肪"
        ]
        
        # 根据体质类型调整饮食建议
        if constitution_risk.constitution_type == "气虚质":
            diet_recommendations.extend([
                "多食用温补食物，如山药、大枣、黑芝麻等",
                "避免生冷食物，以温热食物为主",
                "少量多餐，避免过度饥饿"
            ])
        elif constitution_risk.constitution_type == "阴虚质":
            diet_recommendations.extend([
                "多食用滋阴食物，如百合、银耳、梨等",
                "避免辛辣刺激性食物",
                "保持充足的水分摄入"
            ])
        
        # 运动建议
        exercise_recommendations = [
            "每周至少150分钟中等强度有氧运动",
            "每周进行2次以上肌肉强化训练",
            "避免长时间久坐，每小时起身活动几分钟"
        ]
        
        # 根据体质类型调整运动建议
        if constitution_risk.constitution_type == "气虚质":
            exercise_recommendations = [
                "选择温和的运动方式，如散步、太极、八段锦",
                "避免过度消耗体力的运动",
                "运动时间宜短，循序渐进增加强度"
            ]
        
        # 睡眠建议
        sleep_recommendations = [
            "保持规律的作息时间，尽量每天同一时间睡觉和起床",
            "确保睡眠环境舒适，保持安静、黑暗和适宜温度",
            "避免睡前使用电子设备和摄入咖啡因",
            "白天适当运动有助于晚间睡眠"
        ]
        
        # 压力管理
        stress_recommendations = [
            "学习并实践深呼吸、冥想等放松技巧",
            "培养兴趣爱好，增加生活乐趣",
            "保持良好的社交关系",
            "必要时寻求专业心理咨询"
        ]
        
        # 根据现有生活方式调整建议
        if lifestyle_factors:
            if lifestyle_factors.get("smoking") == "yes":
                recommendations.append("戒烟，或寻求专业戒烟支持")
            
            if lifestyle_factors.get("alcohol") in ["moderate", "heavy"]:
                recommendations.append("限制酒精摄入，男性每日不超过2个标准杯，女性每日不超过1个标准杯")
        
        # 整合所有建议
        recommendations.extend(diet_recommendations)
        recommendations.extend(exercise_recommendations)
        recommendations.extend(sleep_recommendations)
        recommendations.extend(stress_recommendations)
        
        return recommendations
    
    def _generate_recommended_screenings(self, disease_risks: List[DiseaseRisk],
                                       constitution_risk: ConstitutionRisk,
                                       health_data: Optional[Dict[str, str]] = None,
                                       family_history: Optional[List[str]] = None) -> List[str]:
        """
        生成建议筛查
        
        Args:
            disease_risks: 疾病风险
            constitution_risk: 体质风险
            health_data: 健康数据
            family_history: 家族病史
            
        Returns:
            List[str]: 建议筛查列表
        """
        screenings = [
            "常规体检（每年）：包括血压、体重、体质指数（BMI）等",
            "血脂检查（每年）：总胆固醇、高密度脂蛋白胆固醇、低密度脂蛋白胆固醇、甘油三酯",
            "血糖检查（每年）：空腹血糖、糖化血红蛋白"
        ]
        
        # 根据疾病风险添加筛查
        for risk in disease_risks:
            if risk.disease_name == "心血管疾病" and risk.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH]:
                screenings.extend([
                    "心电图检查（每年）",
                    "心脏超声检查（根据医生建议）"
                ])
            
            if risk.disease_name == "糖尿病" and risk.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH]:
                screenings.extend([
                    "口服葡萄糖耐量试验（每1-2年）",
                    "尿微量白蛋白检测（每年）"
                ])
        
        # 根据家族史添加筛查
        if family_history:
            if "癌症" in family_history:
                screenings.append("根据家族史中具体癌症类型，咨询医生进行针对性筛查")
            
            if "骨质疏松" in family_history:
                screenings.append("骨密度检查（根据医生建议）")
        
        # 根据体质风险添加中医体质评估
        screenings.append("中医体质评估（每年）：包括望、闻、问、切四诊")
        
        return screenings