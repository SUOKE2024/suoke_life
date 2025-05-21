#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小克智能体功能模块定义
这个文件定义了小克智能体的所有核心功能模块和能力域
"""

import enum
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field

class ModuleStatus(enum.Enum):
    """功能模块状态枚举"""
    ACTIVE = "active"           # 已激活，可正常使用
    EXPERIMENTAL = "experimental"  # 实验性功能，可能不稳定
    DEPRECATED = "deprecated"   # 已弃用，保留但不推荐使用
    DISABLED = "disabled"       # 已禁用，不可使用
    PLANNED = "planned"         # 计划中，尚未实现

@dataclass
class Capability:
    """能力定义"""
    id: str                     # 能力ID
    name: str                   # 能力名称
    description: str            # 能力描述
    status: ModuleStatus        # 能力状态
    llm_prompt_key: str         # 与该能力关联的提示语模板关键字
    required_integrations: List[str] = field(default_factory=list)  # 所需集成
    dependencies: List[str] = field(default_factory=list)  # 依赖的其他能力
    models: List[str] = field(default_factory=list)  # 支持的模型列表
    metrics: List[str] = field(default_factory=list)  # 相关指标
    
    def is_available(self, available_integrations: Set[str]) -> bool:
        """检查该能力是否可用"""
        if self.status in (ModuleStatus.DISABLED, ModuleStatus.PLANNED):
            return False
            
        # 检查所需集成是否都可用
        for integration in self.required_integrations:
            if integration not in available_integrations:
                return False
                
        return True

@dataclass
class ServiceModule:
    """服务模块定义"""
    id: str                     # 模块ID
    name: str                   # 模块名称
    description: str            # 模块描述
    capabilities: List[Capability] = field(default_factory=list)  # 能力列表
    status: ModuleStatus = ModuleStatus.ACTIVE  # 模块状态
    
    def get_capability(self, capability_id: str) -> Optional[Capability]:
        """获取指定ID的能力"""
        for capability in self.capabilities:
            if capability.id == capability_id:
                return capability
        return None
    
    def get_available_capabilities(self, available_integrations: Set[str]) -> List[Capability]:
        """获取可用的能力列表"""
        if self.status in (ModuleStatus.DISABLED, ModuleStatus.PLANNED):
            return []
            
        return [cap for cap in self.capabilities if cap.is_available(available_integrations)]

# 定义小克智能体的所有功能模块
XIAOKE_MODULES = [
    # 1. 医疗资源调度模块
    ServiceModule(
        id="medical_resource_scheduling",
        name="医疗资源调度",
        description="管理医疗资源分配、匹配最佳医疗机构和专家，并协调预约流程",
        capabilities=[
            Capability(
                id="resource_allocation",
                name="资源分配",
                description="根据用户需求、疾病严重程度和地理位置分配医疗资源",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="resource_allocation_prompt",
                required_integrations=["med-knowledge", "geo-service"],
                models=["gpt-4o-mini", "gpt-4o"],
                metrics=["allocation_accuracy", "response_time"]
            ),
            Capability(
                id="expert_matching",
                name="专家匹配",
                description="匹配合适的医疗专家，包括中医和西医",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="expert_matching_prompt",
                required_integrations=["user-service", "med-knowledge"],
                models=["gpt-4o-mini", "gpt-4o"],
                metrics=["match_satisfaction", "expert_availability"]
            ),
            Capability(
                id="appointment_scheduling",
                name="预约调度",
                description="管理预约流程，包括创建、修改和取消预约",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="appointment_scheduling_prompt",
                required_integrations=["calendar-service"],
                metrics=["booking_success_rate", "reschedule_rate"]
            ),
            Capability(
                id="emergency_coordination",
                name="紧急协调",
                description="紧急情况下的资源快速协调和应急响应",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="emergency_coordination_prompt",
                required_integrations=["emergency-service", "geo-service"],
                models=["gpt-4o"],
                metrics=["response_time", "coordination_effectiveness"]
            ),
        ]
    ),
    
    # 2. 治疗方案管理模块
    ServiceModule(
        id="treatment_planning",
        name="治疗方案管理",
        description="生成和管理个性化治疗方案，包括中医和西医治疗选项",
        capabilities=[
            Capability(
                id="plan_generation",
                name="方案生成",
                description="基于诊断和用户情况生成个性化治疗方案",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="treatment_plan_generation_prompt",
                required_integrations=["med-knowledge", "xiaoai-service"],
                models=["gpt-4o"],
                metrics=["plan_effectiveness", "personalization_score"]
            ),
            Capability(
                id="tcm_western_integration",
                name="中西医结合",
                description="生成整合中医和西医的联合治疗方案",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="tcm_western_integration_prompt",
                required_integrations=["med-knowledge"],
                models=["gpt-4o"],
                metrics=["integration_effectiveness"]
            ),
            Capability(
                id="treatment_monitoring",
                name="治疗监测",
                description="跟踪治疗效果并提供进度报告",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="treatment_monitoring_prompt",
                required_integrations=["user-service"],
                models=["gpt-4o-mini"],
                metrics=["monitoring_accuracy", "followup_rate"]
            ),
            Capability(
                id="treatment_adjustment",
                name="方案调整",
                description="根据治疗效果调整治疗方案",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="treatment_adjustment_prompt",
                required_integrations=["xiaoai-service", "med-knowledge"],
                models=["gpt-4o"],
                metrics=["adjustment_effectiveness"]
            ),
        ]
    ),
    
    # 3. 药品管理模块
    ServiceModule(
        id="medicine_management",
        name="药品管理",
        description="提供药品信息、管理药品库存和协调药品配送",
        capabilities=[
            Capability(
                id="medicine_information",
                name="药品信息",
                description="提供详细的药品信息，包括用法、副作用和禁忌",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="medicine_information_prompt",
                required_integrations=["med-knowledge"],
                models=["gpt-4o-mini", "gpt-4o"],
                metrics=["information_accuracy", "query_success_rate"]
            ),
            Capability(
                id="drug_interaction_check",
                name="药物相互作用检查",
                description="检查多种药物之间的潜在相互作用",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="drug_interaction_prompt",
                required_integrations=["med-knowledge"],
                models=["gpt-4o"],
                metrics=["interaction_detection_rate"]
            ),
            Capability(
                id="prescription_management",
                name="处方管理",
                description="管理电子处方的开具、验证和发送",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="prescription_management_prompt",
                required_integrations=["pharmacy-service", "user-service"],
                models=["gpt-4o-mini"],
                metrics=["prescription_accuracy", "processing_time"]
            ),
            Capability(
                id="medicine_delivery",
                name="药品配送",
                description="协调药品配送服务",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="medicine_delivery_prompt",
                required_integrations=["logistics-service", "pharmacy-service"],
                metrics=["delivery_success_rate", "delivery_time"]
            ),
        ]
    ),
    
    # 4. 农产品服务模块
    ServiceModule(
        id="agricultural_products",
        name="农产品服务",
        description="根据用户体质和健康需求管理优质农产品定制、供应链协调和溯源服务",
        capabilities=[
            Capability(
                id="product_customization",
                name="产品定制",
                description="基于用户体质特点定制农产品组合",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="product_customization_prompt",
                required_integrations=["xiaoai-service", "inventory-service"],
                models=["gpt-4o"],
                metrics=["customization_satisfaction", "health_improvement_rate"]
            ),
            Capability(
                id="supply_chain_management",
                name="供应链管理",
                description="协调从农场到用户的完整供应链",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="supply_chain_prompt",
                required_integrations=["logistics-service", "inventory-service"],
                metrics=["delivery_time", "product_freshness"]
            ),
            Capability(
                id="product_traceability",
                name="产品溯源",
                description="利用区块链技术提供农产品完整溯源信息",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="product_traceability_prompt",
                required_integrations=["blockchain-service"],
                models=["gpt-4o-mini"],
                metrics=["traceability_completeness", "verification_success_rate"]
            ),
            Capability(
                id="seasonal_recommendation",
                name="时令推荐",
                description="根据季节和用户需求推荐最佳农产品",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="seasonal_recommendation_prompt",
                required_integrations=["inventory-service", "xiaoai-service"],
                models=["gpt-4o-mini"],
                metrics=["recommendation_relevance", "seasonal_accuracy"]
            ),
        ]
    ),
    
    # 5. 农事活动模块
    ServiceModule(
        id="farming_activities",
        name="农事活动",
        description="组织和管理各类线上线下农事活动和体验",
        capabilities=[
            Capability(
                id="activity_planning",
                name="活动策划",
                description="策划各类农事体验活动",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="activity_planning_prompt",
                required_integrations=["calendar-service", "geo-service"],
                models=["gpt-4o-mini", "gpt-4o"],
                metrics=["participant_satisfaction", "activity_diversity"]
            ),
            Capability(
                id="registration_management",
                name="报名管理",
                description="管理活动报名流程",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="registration_management_prompt",
                required_integrations=["user-service", "payment-gateway"],
                metrics=["registration_completion_rate", "processing_time"]
            ),
            Capability(
                id="resource_coordination",
                name="资源协调",
                description="协调活动所需的场地、设备和人员",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="resource_coordination_prompt",
                required_integrations=["inventory-service", "logistics-service"],
                models=["gpt-4o-mini"],
                metrics=["resource_availability", "coordination_efficiency"]
            ),
            Capability(
                id="health_education",
                name="健康教育",
                description="在农事活动中融入健康知识教育",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="health_education_prompt",
                required_integrations=["laoke-service", "med-knowledge"],
                models=["gpt-4o"],
                metrics=["knowledge_retention", "participant_feedback"]
            ),
        ]
    ),
    
    # 6. 商店管理模块
    ServiceModule(
        id="store_management",
        name="商店管理",
        description="管理索克生活APP电子商务模块，提供商品推荐和交易服务",
        capabilities=[
            Capability(
                id="product_recommendation",
                name="商品推荐",
                description="基于用户体质和需求推荐健康商品",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="product_recommendation_prompt",
                required_integrations=["xiaoai-service", "inventory-service"],
                models=["gpt-4o-mini", "gpt-4o"],
                metrics=["recommendation_click_rate", "purchase_conversion_rate"]
            ),
            Capability(
                id="order_processing",
                name="订单处理",
                description="管理订单创建、支付和履行流程",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="order_processing_prompt",
                required_integrations=["payment-gateway", "inventory-service"],
                metrics=["processing_speed", "order_accuracy"]
            ),
            Capability(
                id="subscription_management",
                name="订阅管理",
                description="管理健康服务和产品订阅",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="subscription_management_prompt",
                required_integrations=["payment-gateway", "user-service"],
                models=["gpt-4o-mini"],
                metrics=["retention_rate", "subscription_value"]
            ),
            Capability(
                id="customer_support",
                name="客户支持",
                description="提供智能客服支持",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="customer_support_prompt",
                required_integrations=["user-service"],
                models=["gpt-4o-mini", "gpt-4o"],
                metrics=["resolution_rate", "customer_satisfaction"]
            ),
        ]
    ),
    
    # 7. 第三方API集成模块
    ServiceModule(
        id="third_party_integration",
        name="第三方集成",
        description="管理与外部服务的集成，包括支付、物流和医疗平台",
        capabilities=[
            Capability(
                id="payment_gateway",
                name="支付网关",
                description="集成多种支付方式",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="payment_gateway_prompt",
                required_integrations=["payment-gateway"],
                metrics=["transaction_success_rate", "processing_time"]
            ),
            Capability(
                id="logistics_integration",
                name="物流集成",
                description="集成物流服务，跟踪配送状态",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="logistics_integration_prompt",
                required_integrations=["logistics-service", "geo-service"],
                metrics=["tracking_accuracy", "delivery_timeliness"]
            ),
            Capability(
                id="ehr_integration",
                name="电子健康记录集成",
                description="与医疗机构的电子健康记录系统集成",
                status=ModuleStatus.EXPERIMENTAL,
                llm_prompt_key="ehr_integration_prompt",
                required_integrations=["med-knowledge", "auth-service"],
                metrics=["data_synchronization_rate", "integration_reliability"]
            ),
            Capability(
                id="insurance_coordination",
                name="保险协调",
                description="协调医疗保险服务和报销流程",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="insurance_coordination_prompt",
                required_integrations=["payment-gateway"],
                models=["gpt-4o-mini"],
                metrics=["claim_success_rate", "processing_time"]
            ),
        ]
    ),
    
    # 8. 食疗方案模块
    ServiceModule(
        id="diet_therapy",
        name="食疗方案",
        description="根据用户体质和健康状况提供个性化食疗方案",
        capabilities=[
            Capability(
                id="diet_plan_generation",
                name="食疗方案生成",
                description="生成体质匹配的食疗方案",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="diet_plan_generation_prompt",
                required_integrations=["xiaoai-service", "med-knowledge"],
                models=["gpt-4o"],
                metrics=["plan_effectiveness", "user_satisfaction"]
            ),
            Capability(
                id="food_medicine_pairing",
                name="食药配伍",
                description="提供食物与药物的合理搭配建议",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="food_medicine_pairing_prompt",
                required_integrations=["med-knowledge"],
                models=["gpt-4o"],
                metrics=["pairing_safety", "effectiveness_rating"]
            ),
            Capability(
                id="seasonal_diet_adjustment",
                name="时令食疗调整",
                description="根据季节变化调整食疗建议",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="seasonal_diet_adjustment_prompt",
                required_integrations=["med-knowledge"],
                models=["gpt-4o-mini"],
                metrics=["seasonal_relevance", "adaptation_effectiveness"]
            ),
            Capability(
                id="recipe_recommendation",
                name="食谱推荐",
                description="推荐适合用户体质的健康食谱",
                status=ModuleStatus.ACTIVE,
                llm_prompt_key="recipe_recommendation_prompt",
                required_integrations=["med-knowledge"],
                models=["gpt-4o-mini", "gpt-4o"],
                metrics=["recipe_relevance", "user_engagement"]
            ),
        ]
    ),
]

def get_module_by_id(module_id: str) -> Optional[ServiceModule]:
    """根据ID获取模块"""
    for module in XIAOKE_MODULES:
        if module.id == module_id:
            return module
    return None

def get_capability_by_id(capability_id: str) -> Optional[Tuple[ServiceModule, Capability]]:
    """根据ID获取能力及其所属模块"""
    for module in XIAOKE_MODULES:
        for capability in module.capabilities:
            if capability.id == capability_id:
                return module, capability
    return None

def get_available_modules(available_integrations: Set[str]) -> List[ServiceModule]:
    """获取当前可用的模块列表"""
    result = []
    for module in XIAOKE_MODULES:
        if module.status in (ModuleStatus.DISABLED, ModuleStatus.PLANNED):
            continue
            
        available_capabilities = module.get_available_capabilities(available_integrations)
        if available_capabilities:
            result.append(module)
            
    return result 