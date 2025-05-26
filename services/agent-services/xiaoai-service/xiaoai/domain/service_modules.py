#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体服务模块定义
负责定义小艾智能体的功能领域和能力模块
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Set, Any

# 日志配置
logger = logging.getLogger(__name__)

class ServiceCategory(str, Enum):
    """服务类别枚举"""
    CORE = "core"                     # 核心服务
    DIAGNOSTIC = "diagnostic"         # 诊断服务 
    ANALYSIS = "analysis"             # 分析服务
    COORDINATION = "coordination"     # 协调服务
    INTEGRATION = "integration"       # 集成服务
    ACCESSIBILITY = "accessibility"   # 无障碍服务

class ServiceStatus(str, Enum):
    """服务状态枚举"""
    ACTIVE = "active"                 # 激活状态
    INACTIVE = "inactive"             # 未激活
    DEPRECATED = "deprecated"         # 已废弃
    EXPERIMENTAL = "experimental"     # 实验性
    PLANNED = "planned"               # 计划中

class ServiceModule:
    """服务模块基类"""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        category: ServiceCategory,
        status: ServiceStatus = ServiceStatus.ACTIVE,
        capabilities: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        api_endpoints: Optional[List[str]] = None,
        required_services: Optional[List[str]] = None,
        required_models: Optional[List[str]] = None,
        required_integrations: Optional[List[str]] = None,
        config_keys: Optional[List[str]] = None
    ):
        """
        初始化服务模块
        
        Args:
            id: 模块唯一标识符
            name: 模块名称
            description: 模块描述
            category: 服务类别
            status: 服务状态
            capabilities: 模块能力列表
            depends_on: 依赖的其他模块
            api_endpoints: 关联的API端点
            required_services: 依赖的微服务
            required_models: 依赖的模型
            required_integrations: 依赖的集成
            config_keys: 相关配置项
        """
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.status = status
        self.capabilities = capabilities or []
        self.depends_on = depends_on or []
        self.api_endpoints = api_endpoints or []
        self.required_services = required_services or []
        self.required_models = required_models or []
        self.required_integrations = required_integrations or []
        self.config_keys = config_keys or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "capabilities": self.capabilities,
            "depends_on": self.depends_on,
            "api_endpoints": self.api_endpoints,
            "required_services": self.required_services,
            "required_models": self.required_models,
            "required_integrations": self.required_integrations,
            "config_keys": self.config_keys
        }

# 小艾智能体核心能力定义
XIAOAI_SERVICE_MODULES = [
    # 1. 四诊协调引擎 - 核心功能模块
    ServiceModule(
        id="four_diagnosis_coordinator",
        name="四诊协调引擎",
        description="整合望诊、闻诊、问诊和切诊数据，实现四诊合参，生成综合分析结果",
        category=ServiceCategory.COORDINATION,
        capabilities=[
            "协调四诊微服务调用顺序与优先级",
            "处理四诊数据的异步收集",
            "管理四诊会话状态与上下文",
            "数据流动协调与异常处理",
            "智能推荐后续诊断路径",
            "综合评估四诊完整性",
            "实现四诊数据存储与追踪"
        ],
        required_services=[
            "look-service",
            "listen-service", 
            "inquiry-service",
            "palpation-service"
        ],
        api_endpoints=[
            "/v1/diagnosis/coordinate",
            "/v1/diagnosis/session"
        ],
        config_keys=[
            "coordinator.mode",
            "coordinator.timeout",
            "coordinator.priority_weights"
        ]
    ),
    
    # 2. 多模态诊断分析 - 分析服务
    ServiceModule(
        id="multimodal_diagnosis_analysis",
        name="多模态诊断分析",
        description="对四诊采集的多模态数据进行专业分析，提取健康特征与诊断信息",
        category=ServiceCategory.ANALYSIS,
        capabilities=[
            "舌象特征分析与分类",
            "面诊特征提取与解读",
            "语音健康标记物识别",
            "脉象波形特征分析",
            "问诊数据结构化与要点提取",
            "多模态特征融合",
            "生物标记物关联分析",
            "异常模式检测与预警"
        ],
        depends_on=["four_diagnosis_coordinator"],
        required_models=[
            "tongue_analysis_model",
            "face_analysis_model",
            "voice_analysis_model",
            "pulse_analysis_model",
            "multimodal_fusion_model"
        ],
        config_keys=[
            "analysis.feature_extraction.sensitivity",
            "analysis.anomaly_detection.threshold"
        ]
    ),
    
    # 3. 中医辨证引擎 - 核心分析服务
    ServiceModule(
        id="tcm_syndrome_differentiation",
        name="中医辨证引擎",
        description="基于四诊分析结果进行中医辨证论治，生成证型分析和体质评估",
        category=ServiceCategory.ANALYSIS,
        capabilities=[
            "八纲辨证（寒热虚实表里阴阳）",
            "气血津液辨证",
            "脏腑辨证",
            "经络辨证",
            "卫气营血辨证",
            "六经辨证",
            "三焦辨证",
            "体质辨析（九种体质）",
            "证候推理与确认",
            "中西医结合分析"
        ],
        depends_on=[
            "four_diagnosis_coordinator",
            "multimodal_diagnosis_analysis"
        ],
        required_models=[
            "syndrome_differentiation_model",
            "constitution_assessment_model",
            "llm_reasoning_model"
        ],
        required_services=[
            "med-knowledge"
        ],
        config_keys=[
            "differentiation.rules_version",
            "differentiation.confidence_threshold",
            "differentiation.evidence_requirements"
        ]
    ),
    
    # 4. 健康分析与建议 - 分析服务
    ServiceModule(
        id="health_analysis_recommendation",
        name="健康分析与建议",
        description="基于辨证结果生成健康状态分析和个性化调理建议",
        category=ServiceCategory.ANALYSIS,
        capabilities=[
            "整体健康状态评估",
            "亚健康风险分析",
            "潜在健康问题预警",
            "体质偏颇调理建议",
            "饮食调养建议",
            "起居养生指导",
            "情志调理建议",
            "运动处方生成",
            "外治法推荐",
            "穴位按摩指导",
            "中医养生保健方案",
            "专业就医建议与提醒"
        ],
        depends_on=[
            "tcm_syndrome_differentiation"
        ],
        required_models=[
            "health_recommendation_model",
            "risk_assessment_model"
        ],
        required_services=[
            "med-knowledge",
            "soer-service"
        ],
        config_keys=[
            "recommendation.personalization_level",
            "recommendation.risk_threshold",
            "recommendation.suggestion_categories"
        ]
    ),
    
    # 5. 智能诊间助手 - 对话服务
    ServiceModule(
        id="intelligent_diagnosis_assistant",
        name="智能诊间助手",
        description="提供智能问答和交互式健康咨询，辅助四诊数据收集与解读",
        category=ServiceCategory.DIAGNOSTIC,
        capabilities=[
            "主诉引导与症状询问",
            "病史采集与整理",
            "症状详情探询",
            "生活习惯评估",
            "健康信息科普",
            "诊断解释与疑问解答",
            "四诊结果通俗解读",
            "健康教育与宣导",
            "用户问题分类与处理",
            "情感支持与心理疏导"
        ],
        depends_on=[
            "multimodal_diagnosis_analysis",
            "tcm_syndrome_differentiation"
        ],
        required_models=[
            "dialogue_management_model",
            "medical_qa_model",
            "llm_chat_model"
        ],
        api_endpoints=[
            "/v1/chat/message",
            "/v1/chat/stream"
        ],
        config_keys=[
            "assistant.conversation_context_length",
            "assistant.sensitivity_level",
            "assistant.education_content_sources"
        ]
    ),
    
    # 6. 四诊多模态设备集成 - 集成服务
    ServiceModule(
        id="multimodal_device_integration",
        name="四诊多模态设备集成",
        description="与多种生物传感器和医疗设备集成，实现四诊数据的标准化采集",
        category=ServiceCategory.INTEGRATION,
        capabilities=[
            "舌诊数据采集设备集成",
            "面诊图像采集设备集成",
            "听诊设备集成",
            "脉诊设备数据接入",
            "可穿戴设备数据集成",
            "移动设备传感器接入",
            "第三方健康设备互操作",
            "设备数据校准与标准化",
            "多设备数据同步与关联",
            "远程设备状态监控"
        ],
        required_services=[
            "look-service",
            "listen-service",
            "palpation-service"
        ],
        api_endpoints=[
            "/v1/devices/register",
            "/v1/devices/data",
            "/v1/devices/calibrate"
        ],
        config_keys=[
            "devices.supported_types",
            "devices.data_standards",
            "devices.connection_timeout"
        ]
    ),
    
    # 7. 智能体协作引擎 - 核心服务
    ServiceModule(
        id="agent_collaboration_engine",
        name="智能体协作引擎",
        description="管理小艾与其他智能体（小克、老克、索儿）的协作交互",
        category=ServiceCategory.CORE,
        capabilities=[
            "智能体间消息路由",
            "协作任务分配与跟踪",
            "跨智能体知识共享",
            "协作上下文管理",
            "分布式决策协调",
            "任务完成度监控",
            "冲突处理与协商",
            "多智能体并行协作",
            "协作能力动态发现"
        ],
        required_integrations=[
            "xiaoke-service",
            "laoke-service",
            "soer-service",
            "message-bus-service"
        ],
        api_endpoints=[
            "/v1/collaboration/task",
            "/v1/collaboration/message"
        ],
        config_keys=[
            "collaboration.routing_rules",
            "collaboration.capability_registry",
            "collaboration.task_timeout"
        ]
    ),
    
    # 8. 无障碍健康服务 - 无障碍服务
    ServiceModule(
        id="accessible_health_services",
        name="无障碍健康服务",
        description="为听障、视障、语障等特殊人群提供定制化健康服务",
        category=ServiceCategory.ACCESSIBILITY,
        capabilities=[
            "手语识别与翻译",
            "语音到文本转换与增强",
            "文本到语音转换优化",
            "盲文健康信息转换",
            "触觉反馈健康提示",
            "简化健康信息呈现",
            "图像内容口述描述",
            "认知障碍适配服务",
            "老年人友好界面适配",
            "特殊人群专属诊断流程"
        ],
        required_services=[
            "accessibility-service"
        ],
        required_models=[
            "sign_language_model",
            "speech_to_text_enhanced_model",
            "text_to_speech_adaptive_model",
            "image_description_model"
        ],
        api_endpoints=[
            "/v1/accessibility/translate",
            "/v1/accessibility/describe",
            "/v1/accessibility/adapt"
        ],
        config_keys=[
            "accessibility.enabled_features",
            "accessibility.adaptation_level",
            "accessibility.alternative_formats"
        ]
    ),
    
    # 9. 医疗知识库增强 - 集成服务
    ServiceModule(
        id="medical_knowledge_enhancement",
        name="医疗知识库增强",
        description="集成中西医结合知识库，支持四诊分析、辨证和健康建议的知识支持",
        category=ServiceCategory.INTEGRATION,
        capabilities=[
            "中医典籍知识库接入",
            "西医医学知识整合",
            "药食配伍知识管理",
            "证型治法知识库",
            "辨证规则库维护",
            "体质类型特征库",
            "经络穴位知识图谱",
            "健康生活方式指南",
            "医学研究文献接入",
            "知识实时更新与验证"
        ],
        required_services=[
            "med-knowledge",
            "rag-service"
        ],
        api_endpoints=[
            "/v1/knowledge/query",
            "/v1/knowledge/retrieve"
        ],
        config_keys=[
            "knowledge.sources",
            "knowledge.update_frequency",
            "knowledge.retrieval_strategy"
        ]
    ),
    
    # 10. 健康数据分析引擎 - 分析服务
    ServiceModule(
        id="health_data_analytics",
        name="健康数据分析引擎",
        description="分析用户历史健康数据，发现模式与趋势，支持长期健康管理",
        category=ServiceCategory.ANALYSIS,
        capabilities=[
            "纵向健康数据分析",
            "健康趋势预测",
            "体质变化追踪",
            "健康干预效果评估",
            "季节性健康变化分析",
            "生活方式影响评估",
            "健康风险预警模型",
            "用药效果分析",
            "诊疗记录结构化",
            "健康数据可视化",
            "个人健康指数计算"
        ],
        depends_on=[
            "tcm_syndrome_differentiation",
            "health_analysis_recommendation"
        ],
        required_models=[
            "time_series_analysis_model",
            "health_trend_prediction_model",
            "risk_stratification_model"
        ],
        api_endpoints=[
            "/v1/analytics/trends",
            "/v1/analytics/risk",
            "/v1/analytics/effectiveness"
        ],
        config_keys=[
            "analytics.time_horizon",
            "analytics.prediction_confidence",
            "analytics.minimum_data_points"
        ]
    ),
]

def get_service_module_by_id(module_id: str) -> Optional[ServiceModule]:
    """
    通过ID获取服务模块
    
    Args:
        module_id: 模块ID
        
    Returns:
        ServiceModule或None（如果未找到）
    """
    for module in XIAOAI_SERVICE_MODULES:
        if module.id == module_id:
            return module
    return None

def get_service_modules_by_category(category: ServiceCategory) -> List[ServiceModule]:
    """
    获取特定类别的所有服务模块
    
    Args:
        category: 服务类别
        
    Returns:
        服务模块列表
    """
    return [module for module in XIAOAI_SERVICE_MODULES if module.category == category]

def get_service_modules_by_status(status: ServiceStatus) -> List[ServiceModule]:
    """
    获取特定状态的所有服务模块
    
    Args:
        status: 服务状态
        
    Returns:
        服务模块列表
    """
    return [module for module in XIAOAI_SERVICE_MODULES if module.status == status]

def get_all_capabilities() -> List[str]:
    """
    获取所有能力列表
    
    Returns:
        能力列表
    """
    capabilities = set()
    for module in XIAOAI_SERVICE_MODULES:
        capabilities.update(module.capabilities)
    return list(capabilities)

def get_service_module_dependencies(module_id: str) -> List[ServiceModule]:
    """
    获取指定模块的所有依赖模块
    
    Args:
        module_id: 模块ID
        
    Returns:
        依赖的服务模块列表
    """
    module = get_service_module_by_id(module_id)
    if not module:
        return []
    
    dependencies = []
    for dep_id in module.depends_on:
        dep_module = get_service_module_by_id(dep_id)
        if dep_module:
            dependencies.append(dep_module)
    
    return dependencies 