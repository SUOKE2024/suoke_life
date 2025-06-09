"""
索克生活智能体事件类型定义
基于四个智能体的具体功能职责
"""

from enum import Enum
from typing import Dict, Any, List


class XiaoaiEvents:
    """小艾智能体事件 - 首页聊天频道版主"""
    
    # 语音交互事件
    VOICE_INTERACTION_STARTED = "xiaoai.voice.interaction_started"
    VOICE_RECOGNITION_COMPLETED = "xiaoai.voice.recognition_completed"
    VOICE_SYNTHESIS_COMPLETED = "xiaoai.voice.synthesis_completed"
    MULTILINGUAL_TRANSLATION_COMPLETED = "xiaoai.voice.translation_completed"
    DIALECT_RECOGNITION_COMPLETED = "xiaoai.voice.dialect_recognized"
    
    # 中医望诊事件
    FACE_COLOR_ANALYSIS_STARTED = "xiaoai.look.face_color_started"
    FACE_COLOR_ANALYSIS_COMPLETED = "xiaoai.look.face_color_completed"
    TONGUE_DIAGNOSIS_STARTED = "xiaoai.look.tongue_diagnosis_started"
    TONGUE_DIAGNOSIS_COMPLETED = "xiaoai.look.tongue_diagnosis_completed"
    SPIRIT_ASSESSMENT_COMPLETED = "xiaoai.look.spirit_assessment_completed"
    BODY_SHAPE_ANALYSIS_COMPLETED = "xiaoai.look.body_shape_completed"
    
    # 智能问诊事件
    CONSTITUTION_SCREENING_STARTED = "xiaoai.inquiry.constitution_screening_started"
    CONSTITUTION_SCREENING_COMPLETED = "xiaoai.inquiry.constitution_screening_completed"
    SYMPTOM_ASSESSMENT_STARTED = "xiaoai.inquiry.symptom_assessment_started"
    SYMPTOM_ASSESSMENT_COMPLETED = "xiaoai.inquiry.symptom_assessment_completed"
    HEALTH_CONSULTATION_STARTED = "xiaoai.inquiry.health_consultation_started"
    HEALTH_CONSULTATION_COMPLETED = "xiaoai.inquiry.health_consultation_completed"
    
    # 医疗记录管理事件
    MEDICAL_RECORD_AUTO_ORGANIZED = "xiaoai.record.auto_organized"
    HEALTH_ARCHIVE_UPDATED = "xiaoai.record.health_archive_updated"
    MEDICAL_HISTORY_ANALYZED = "xiaoai.record.medical_history_analyzed"
    
    # 无障碍服务事件
    GUIDE_SERVICE_STARTED = "xiaoai.accessibility.guide_started"
    SIGN_LANGUAGE_RECOGNIZED = "xiaoai.accessibility.sign_language_recognized"
    ELDERLY_INTERFACE_ACTIVATED = "xiaoai.accessibility.elderly_interface_activated"
    BARRIER_FREE_NAVIGATION_STARTED = "xiaoai.accessibility.navigation_started"
    
    # 四诊合参统筹事件
    FOUR_DIAGNOSIS_COORDINATION_STARTED = "xiaoai.coordination.four_diagnosis_started"
    FOUR_DIAGNOSIS_COORDINATION_COMPLETED = "xiaoai.coordination.four_diagnosis_completed"
    DIAGNOSIS_WORKFLOW_ORCHESTRATED = "xiaoai.coordination.workflow_orchestrated"


class XiaokeEvents:
    """小克智能体事件 - SUOKE频道版主"""
    
    # 服务订阅事件
    SERVICE_SUBSCRIPTION_REQUESTED = "xiaoke.subscription.service_requested"
    SERVICE_SUBSCRIPTION_COMPLETED = "xiaoke.subscription.service_completed"
    SUBSCRIPTION_RENEWAL_REMINDER = "xiaoke.subscription.renewal_reminder"
    PERSONALIZED_RECOMMENDATION_GENERATED = "xiaoke.subscription.recommendation_generated"
    
    # 名医资源管理事件
    DOCTOR_MATCHING_STARTED = "xiaoke.doctor.matching_started"
    DOCTOR_MATCHING_COMPLETED = "xiaoke.doctor.matching_completed"
    APPOINTMENT_SCHEDULED = "xiaoke.doctor.appointment_scheduled"
    APPOINTMENT_REMINDER_SENT = "xiaoke.doctor.appointment_reminder"
    DOCTOR_AVAILABILITY_UPDATED = "xiaoke.doctor.availability_updated"
    
    # 农产品管理事件
    AGRICULTURAL_PRODUCT_CUSTOMIZED = "xiaoke.agriculture.product_customized"
    PRODUCT_TRACEABILITY_VERIFIED = "xiaoke.agriculture.traceability_verified"
    SUPPLY_CHAIN_OPTIMIZED = "xiaoke.agriculture.supply_chain_optimized"
    DELIVERY_SCHEDULED = "xiaoke.agriculture.delivery_scheduled"
    QUALITY_INSPECTION_COMPLETED = "xiaoke.agriculture.quality_inspection_completed"
    
    # 农事活动体验事件
    FARM_ACTIVITY_RECOMMENDED = "xiaoke.farm.activity_recommended"
    FARM_EXPERIENCE_BOOKED = "xiaoke.farm.experience_booked"
    SEASONAL_ACTIVITY_NOTIFIED = "xiaoke.farm.seasonal_activity_notified"
    
    # 第三方API集成事件
    THIRD_PARTY_API_INTEGRATED = "xiaoke.api.third_party_integrated"
    INSURANCE_SERVICE_CONNECTED = "xiaoke.api.insurance_connected"
    PAYMENT_SERVICE_PROCESSED = "xiaoke.api.payment_processed"
    LOGISTICS_SERVICE_TRACKED = "xiaoke.api.logistics_tracked"
    
    # 店铺管理事件
    STORE_PRODUCT_RECOMMENDED = "xiaoke.store.product_recommended"
    INVENTORY_MANAGEMENT_UPDATED = "xiaoke.store.inventory_updated"
    HEALTH_PRODUCT_CURATED = "xiaoke.store.health_product_curated"
    ORDER_PROCESSING_COMPLETED = "xiaoke.store.order_processed"


class LaokeEvents:
    """老克智能体事件 - 探索频道版主"""
    
    # 知识传播事件
    KNOWLEDGE_SEARCH_REQUESTED = "laoke.knowledge.search_requested"
    KNOWLEDGE_SEARCH_COMPLETED = "laoke.knowledge.search_completed"
    PERSONALIZED_LEARNING_PATH_GENERATED = "laoke.knowledge.learning_path_generated"
    KNOWLEDGE_RECOMMENDATION_SENT = "laoke.knowledge.recommendation_sent"
    
    # 知识培训事件
    TRAINING_COURSE_STARTED = "laoke.training.course_started"
    TRAINING_PROGRESS_TRACKED = "laoke.training.progress_tracked"
    CERTIFICATION_EXAM_COMPLETED = "laoke.training.certification_completed"
    LEARNING_ACHIEVEMENT_UNLOCKED = "laoke.training.achievement_unlocked"
    
    # 社区内容管理事件
    COMMUNITY_CONTENT_MODERATED = "laoke.community.content_moderated"
    KNOWLEDGE_CONTRIBUTION_REWARDED = "laoke.community.contribution_rewarded"
    CONTENT_QUALITY_ASSESSED = "laoke.community.quality_assessed"
    EXPERT_VERIFICATION_COMPLETED = "laoke.community.expert_verified"
    
    # 游戏NPC事件
    MAZE_GAME_STARTED = "laoke.game.maze_started"
    NPC_INTERACTION_INITIATED = "laoke.game.npc_interaction_initiated"
    GAME_GUIDANCE_PROVIDED = "laoke.game.guidance_provided"
    GAME_ACHIEVEMENT_EARNED = "laoke.game.achievement_earned"
    AR_VR_EXPERIENCE_LAUNCHED = "laoke.game.ar_vr_launched"
    
    # 博客管理事件
    BLOG_CONTENT_REVIEWED = "laoke.blog.content_reviewed"
    BLOG_QUALITY_VERIFIED = "laoke.blog.quality_verified"
    BLOG_RECOMMENDATION_GENERATED = "laoke.blog.recommendation_generated"
    CONTENT_SAFETY_CHECKED = "laoke.blog.safety_checked"


class SoerEvents:
    """索儿智能体事件 - LIFE频道版主"""
    
    # 健康生活管理事件
    LIFESTYLE_HABIT_ANALYZED = "soer.lifestyle.habit_analyzed"
    BEHAVIOR_INTERVENTION_TRIGGERED = "soer.lifestyle.intervention_triggered"
    DIET_PLAN_GENERATED = "soer.lifestyle.diet_plan_generated"
    EXERCISE_PLAN_CREATED = "soer.lifestyle.exercise_plan_created"
    SLEEP_PATTERN_ANALYZED = "soer.lifestyle.sleep_analyzed"
    
    # 多设备数据整合事件
    SENSOR_DATA_COLLECTED = "soer.sensor.data_collected"
    MULTI_DEVICE_DATA_SYNCHRONIZED = "soer.sensor.data_synchronized"
    HEALTH_TREND_ANALYZED = "soer.sensor.trend_analyzed"
    DEVICE_CONNECTIVITY_VERIFIED = "soer.sensor.connectivity_verified"
    DATA_QUALITY_VALIDATED = "soer.sensor.data_quality_validated"
    
    # 环境感知事件
    ENVIRONMENT_CONDITION_DETECTED = "soer.environment.condition_detected"
    EMOTIONAL_STATE_RECOGNIZED = "soer.environment.emotion_recognized"
    DYNAMIC_HEALTH_ADVICE_GENERATED = "soer.environment.advice_generated"
    STRESS_LEVEL_MONITORED = "soer.environment.stress_monitored"
    
    # 个性化养生事件
    PERSONALIZED_WELLNESS_PLAN_CREATED = "soer.wellness.plan_created"
    WELLNESS_PLAN_EXECUTED = "soer.wellness.plan_executed"
    WELLNESS_PROGRESS_TRACKED = "soer.wellness.progress_tracked"
    WELLNESS_PLAN_ADJUSTED = "soer.wellness.plan_adjusted"
    
    # 情感陪伴事件
    EMOTIONAL_SUPPORT_PROVIDED = "soer.emotion.support_provided"
    STRESS_MANAGEMENT_INITIATED = "soer.emotion.stress_management_initiated"
    MOOD_COUNSELING_STARTED = "soer.emotion.counseling_started"
    COMPANIONSHIP_SESSION_STARTED = "soer.emotion.companionship_started"
    MENTAL_HEALTH_ASSESSED = "soer.emotion.mental_health_assessed"


class AgentCollaborationEvents:
    """智能体协同事件"""
    
    # 跨智能体协同事件
    MULTI_AGENT_CONSULTATION_STARTED = "collaboration.multi_agent_consultation_started"
    MULTI_AGENT_CONSULTATION_COMPLETED = "collaboration.multi_agent_consultation_completed"
    AGENT_HANDOFF_INITIATED = "collaboration.agent_handoff_initiated"
    AGENT_HANDOFF_COMPLETED = "collaboration.agent_handoff_completed"
    
    # 综合服务协同事件
    COMPREHENSIVE_HEALTH_SERVICE_STARTED = "collaboration.comprehensive_service_started"
    HEALTH_KNOWLEDGE_SERVICE_INTEGRATED = "collaboration.health_knowledge_integrated"
    LIFESTYLE_MEDICAL_SERVICE_COORDINATED = "collaboration.lifestyle_medical_coordinated"
    
    # 用户体验协同事件
    SEAMLESS_USER_EXPERIENCE_ORCHESTRATED = "collaboration.seamless_experience_orchestrated"
    CROSS_CHANNEL_CONSISTENCY_MAINTAINED = "collaboration.cross_channel_consistency"
    UNIFIED_USER_PROFILE_UPDATED = "collaboration.unified_profile_updated"
    
    # 数据共享协同事件
    AGENT_DATA_SHARING_INITIATED = "collaboration.data_sharing_initiated"
    CROSS_AGENT_INSIGHTS_GENERATED = "collaboration.cross_insights_generated"
    HOLISTIC_USER_UNDERSTANDING_ACHIEVED = "collaboration.holistic_understanding_achieved"


class ChannelEvents:
    """频道管理事件"""
    
    # 首页聊天频道事件
    CHAT_CHANNEL_MESSAGE_RECEIVED = "channel.chat.message_received"
    CHAT_CHANNEL_USER_JOINED = "channel.chat.user_joined"
    CHAT_CHANNEL_CONVERSATION_STARTED = "channel.chat.conversation_started"
    
    # SUOKE频道事件
    SUOKE_CHANNEL_SERVICE_BROWSED = "channel.suoke.service_browsed"
    SUOKE_CHANNEL_PRODUCT_VIEWED = "channel.suoke.product_viewed"
    SUOKE_CHANNEL_ORDER_PLACED = "channel.suoke.order_placed"
    
    # 探索频道事件
    EXPLORE_CHANNEL_CONTENT_ACCESSED = "channel.explore.content_accessed"
    EXPLORE_CHANNEL_LEARNING_STARTED = "channel.explore.learning_started"
    EXPLORE_CHANNEL_GAME_LAUNCHED = "channel.explore.game_launched"
    
    # LIFE频道事件
    LIFE_CHANNEL_HEALTH_DATA_VIEWED = "channel.life.health_data_viewed"
    LIFE_CHANNEL_WELLNESS_PLAN_ACCESSED = "channel.life.wellness_plan_accessed"
    LIFE_CHANNEL_COMPANION_CHAT_STARTED = "channel.life.companion_chat_started"


class ServiceIntegrationEvents:
    """服务集成事件"""
    
    # 四诊合参集成事件
    FOUR_DIAGNOSIS_INTEGRATION_STARTED = "integration.four_diagnosis_started"
    LOOK_LISTEN_INQUIRY_PALPATION_COORDINATED = "integration.four_diagnosis_coordinated"
    TCM_MODERN_MEDICINE_INTEGRATED = "integration.tcm_modern_integrated"
    
    # 健康服务集成事件
    HEALTH_SERVICE_ECOSYSTEM_ACTIVATED = "integration.health_ecosystem_activated"
    MEDICAL_AGRICULTURAL_SERVICE_LINKED = "integration.medical_agricultural_linked"
    KNOWLEDGE_PRACTICE_INTEGRATED = "integration.knowledge_practice_integrated"
    
    # 技术服务集成事件
    MULTIMODAL_AI_SERVICE_INTEGRATED = "integration.multimodal_ai_integrated"
    BLOCKCHAIN_HEALTH_DATA_SECURED = "integration.blockchain_secured"
    EDGE_COMPUTING_PRIVACY_PROTECTED = "integration.edge_privacy_protected"


# 事件优先级映射
EVENT_PRIORITY_MAP = {
    # 高优先级事件（健康相关、紧急情况）
    XiaoaiEvents.HEALTH_CONSULTATION_STARTED: "high",
    SoerEvents.STRESS_LEVEL_MONITORED: "high",
    SoerEvents.MENTAL_HEALTH_ASSESSED: "high",
    
    # 中等优先级事件（服务协同）
    AgentCollaborationEvents.MULTI_AGENT_CONSULTATION_STARTED: "normal",
    XiaokeEvents.DOCTOR_MATCHING_STARTED: "normal",
    
    # 低优先级事件（内容管理、游戏）
    LaokeEvents.BLOG_CONTENT_REVIEWED: "low",
    LaokeEvents.MAZE_GAME_STARTED: "low",
}

# 智能体能力映射
AGENT_CAPABILITIES = {
    "xiaoai": {
        "primary_functions": [
            "voice_interaction", "multilingual_support", "tcm_look_diagnosis",
            "intelligent_inquiry", "accessibility_services", "four_diagnosis_coordination"
        ],
        "technologies": [
            "multimodal_llm", "lightweight_local_model", "computer_vision",
            "speech_recognition", "natural_language_processing"
        ],
        "channels": ["chat"],
        "specialties": ["中医望诊", "语音交互", "无障碍服务", "四诊统筹"]
    },
    "xiaoke": {
        "primary_functions": [
            "service_subscription", "doctor_matching", "agricultural_products",
            "third_party_integration", "store_management", "supply_chain"
        ],
        "technologies": [
            "recommendation_algorithms", "blockchain_traceability", "api_gateway",
            "rcm_system", "supply_chain_optimization"
        ],
        "channels": ["suoke"],
        "specialties": ["服务订阅", "名医匹配", "农产品管理", "第三方集成"]
    },
    "laoke": {
        "primary_functions": [
            "knowledge_dissemination", "training_management", "community_moderation",
            "game_npc", "blog_management", "content_curation"
        ],
        "technologies": [
            "knowledge_graph", "rag_system", "ar_vr_generation", "content_moderation",
            "learning_analytics", "gamification"
        ],
        "channels": ["explore"],
        "specialties": ["知识传播", "培训管理", "社区内容", "游戏NPC"]
    },
    "soer": {
        "primary_functions": [
            "lifestyle_management", "multi_device_integration", "emotional_support",
            "personalized_wellness", "environmental_sensing", "health_companionship"
        ],
        "technologies": [
            "multi_source_data_fusion", "edge_computing", "reinforcement_learning",
            "emotion_computing", "sensor_integration", "privacy_protection"
        ],
        "channels": ["life"],
        "specialties": ["生活管理", "设备整合", "情感陪伴", "个性化养生"]
    }
}

# 协同场景定义
COLLABORATION_SCENARIOS = {
    "comprehensive_health_diagnosis": {
        "description": "综合健康诊断场景",
        "participating_agents": ["xiaoai", "xiaoke", "laoke", "soer"],
        "workflow": [
            "xiaoai.四诊合参统筹",
            "soer.生活数据分析",
            "xiaoke.名医资源匹配",
            "laoke.知识支持提供"
        ]
    },
    "personalized_wellness_plan": {
        "description": "个性化养生方案场景",
        "participating_agents": ["soer", "xiaoai", "xiaoke"],
        "workflow": [
            "soer.个性化方案生成",
            "xiaoai.中医体质分析",
            "xiaoke.相关产品推荐"
        ]
    },
    "health_education_journey": {
        "description": "健康教育学习场景",
        "participating_agents": ["laoke", "xiaoai", "soer"],
        "workflow": [
            "laoke.知识内容推荐",
            "xiaoai.互动式学习",
            "soer.实践指导跟踪"
        ]
    },
    "emergency_health_support": {
        "description": "紧急健康支持场景",
        "participating_agents": ["xiaoai", "xiaoke", "soer"],
        "workflow": [
            "soer.异常状态检测",
            "xiaoai.紧急评估处理",
            "xiaoke.医疗资源调度"
        ]
    }
} 