"""
索克生活事件类型定义
定义系统中所有的事件类型常量
"""

from enum import Enum
from typing import Dict, Any


class AgentCollaborationEvents:
    """智能体协同事件"""
    
    # 诊断流程事件
    DIAGNOSIS_STARTED = "diagnosis.started"
    DIAGNOSIS_COMPLETED = "diagnosis.completed"
    DIAGNOSIS_FAILED = "diagnosis.failed"
    
    # 小艾（望诊）事件
    XIAOAI_LOOK_STARTED = "xiaoai.look.started"
    XIAOAI_LOOK_COMPLETED = "xiaoai.look.completed"
    XIAOAI_LOOK_FAILED = "xiaoai.look.failed"
    XIAOAI_TONGUE_ANALYSIS_COMPLETED = "xiaoai.tongue_analysis.completed"
    XIAOAI_FACE_ANALYSIS_COMPLETED = "xiaoai.face_analysis.completed"
    
    # 小克（闻诊）事件
    XIAOKE_LISTEN_STARTED = "xiaoke.listen.started"
    XIAOKE_LISTEN_COMPLETED = "xiaoke.listen.completed"
    XIAOKE_LISTEN_FAILED = "xiaoke.listen.failed"
    XIAOKE_VOICE_ANALYSIS_COMPLETED = "xiaoke.voice_analysis.completed"
    XIAOKE_BREATH_ANALYSIS_COMPLETED = "xiaoke.breath_analysis.completed"
    
    # 老克（问诊）事件
    LAOKE_INQUIRY_STARTED = "laoke.inquiry.started"
    LAOKE_INQUIRY_COMPLETED = "laoke.inquiry.completed"
    LAOKE_INQUIRY_FAILED = "laoke.inquiry.failed"
    LAOKE_SYMPTOM_ANALYSIS_COMPLETED = "laoke.symptom_analysis.completed"
    LAOKE_MEDICAL_HISTORY_ANALYZED = "laoke.medical_history.analyzed"
    
    # 索儿（切诊）事件
    SOER_PALPATION_STARTED = "soer.palpation.started"
    SOER_PALPATION_COMPLETED = "soer.palpation.completed"
    SOER_PALPATION_FAILED = "soer.palpation.failed"
    SOER_PULSE_ANALYSIS_COMPLETED = "soer.pulse_analysis.completed"
    SOER_ACUPOINT_ANALYSIS_COMPLETED = "soer.acupoint_analysis.completed"
    
    # 综合诊断事件
    SYNDROME_DIFFERENTIATION_STARTED = "syndrome_differentiation.started"
    SYNDROME_DIFFERENTIATION_COMPLETED = "syndrome_differentiation.completed"
    TREATMENT_PLAN_GENERATED = "treatment_plan.generated"
    
    # 智能体协同决策事件
    AGENT_COLLABORATION_STARTED = "agent.collaboration.started"
    AGENT_COLLABORATION_COMPLETED = "agent.collaboration.completed"
    AGENT_CONSENSUS_REACHED = "agent.consensus.reached"
    AGENT_DISAGREEMENT_DETECTED = "agent.disagreement.detected"


class HealthDataEvents:
    """健康数据事件"""
    
    # 数据收集事件
    HEALTH_DATA_RECEIVED = "health.data.received"
    HEALTH_DATA_VALIDATED = "health.data.validated"
    HEALTH_DATA_STORED = "health.data.stored"
    HEALTH_DATA_UPDATED = "health.data.updated"
    HEALTH_DATA_DELETED = "health.data.deleted"
    
    # 生命体征事件
    VITAL_SIGNS_UPDATED = "health.vital_signs.updated"
    VITAL_SIGNS_ABNORMAL = "health.vital_signs.abnormal"
    VITAL_SIGNS_CRITICAL = "health.vital_signs.critical"
    HEART_RATE_ANOMALY = "health.heart_rate.anomaly"
    BLOOD_PRESSURE_ABNORMAL = "health.blood_pressure.abnormal"
    TEMPERATURE_FEVER = "health.temperature.fever"
    
    # 诊断数据事件
    DIAGNOSTIC_DATA_RECEIVED = "health.diagnostic.received"
    DIAGNOSTIC_RESULT_GENERATED = "health.diagnostic.result_generated"
    DIAGNOSTIC_CONFIDENCE_LOW = "health.diagnostic.confidence_low"
    
    # 中医数据事件
    TCM_DATA_RECEIVED = "health.tcm.data_received"
    TCM_CONSTITUTION_ANALYZED = "health.tcm.constitution_analyzed"
    TCM_SYNDROME_IDENTIFIED = "health.tcm.syndrome_identified"
    
    # 数据同步事件
    DATA_SYNC_STARTED = "health.data_sync.started"
    DATA_SYNC_COMPLETED = "health.data_sync.completed"
    DATA_SYNC_FAILED = "health.data_sync.failed"
    
    # 数据质量事件
    DATA_QUALITY_CHECK_STARTED = "health.data_quality.check_started"
    DATA_QUALITY_ISSUE_DETECTED = "health.data_quality.issue_detected"
    DATA_VALIDATION_FAILED = "health.data_validation.failed"


class UserInteractionEvents:
    """用户交互事件"""
    
    # 用户会话事件
    USER_SESSION_STARTED = "user.session.started"
    USER_SESSION_ENDED = "user.session.ended"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    
    # 用户查询事件
    USER_QUESTION_RECEIVED = "user.question.received"
    USER_QUESTION_PROCESSED = "user.question.processed"
    USER_QUERY_COMPLEX = "user.query.complex"
    
    # 智能体响应事件
    AGENT_RESPONSE_GENERATED = "agent.response.generated"
    AGENT_RESPONSE_SENT = "agent.response.sent"
    AGENT_CLARIFICATION_REQUESTED = "agent.clarification.requested"
    
    # 用户反馈事件
    USER_FEEDBACK_RECEIVED = "user.feedback.received"
    USER_SATISFACTION_RATED = "user.satisfaction.rated"
    USER_COMPLAINT_RECEIVED = "user.complaint.received"
    
    # 推荐事件
    RECOMMENDATION_GENERATED = "recommendation.generated"
    RECOMMENDATION_ACCEPTED = "recommendation.accepted"
    RECOMMENDATION_REJECTED = "recommendation.rejected"


class SystemEvents:
    """系统事件"""
    
    # 服务生命周期事件
    SERVICE_STARTED = "system.service.started"
    SERVICE_STOPPED = "system.service.stopped"
    SERVICE_HEALTH_CHECK = "system.service.health_check"
    SERVICE_ERROR = "system.service.error"
    
    # 性能监控事件
    PERFORMANCE_THRESHOLD_EXCEEDED = "system.performance.threshold_exceeded"
    MEMORY_USAGE_HIGH = "system.memory.usage_high"
    CPU_USAGE_HIGH = "system.cpu.usage_high"
    
    # 安全事件
    SECURITY_BREACH_DETECTED = "system.security.breach_detected"
    UNAUTHORIZED_ACCESS_ATTEMPT = "system.security.unauthorized_access"
    DATA_ENCRYPTION_FAILED = "system.security.encryption_failed"
    
    # 数据库事件
    DATABASE_CONNECTION_LOST = "system.database.connection_lost"
    DATABASE_QUERY_SLOW = "system.database.query_slow"
    DATABASE_BACKUP_COMPLETED = "system.database.backup_completed"


class BlockchainEvents:
    """区块链事件"""
    
    # 数据上链事件
    DATA_BLOCKCHAIN_UPLOAD_STARTED = "blockchain.data_upload.started"
    DATA_BLOCKCHAIN_UPLOAD_COMPLETED = "blockchain.data_upload.completed"
    DATA_BLOCKCHAIN_UPLOAD_FAILED = "blockchain.data_upload.failed"
    
    # 隐私保护事件
    PRIVACY_ENCRYPTION_COMPLETED = "blockchain.privacy.encryption_completed"
    ZERO_KNOWLEDGE_PROOF_GENERATED = "blockchain.zkp.generated"
    DATA_ANONYMIZATION_COMPLETED = "blockchain.anonymization.completed"
    
    # 智能合约事件
    SMART_CONTRACT_EXECUTED = "blockchain.contract.executed"
    SMART_CONTRACT_FAILED = "blockchain.contract.failed"
    
    # 数据验证事件
    DATA_INTEGRITY_VERIFIED = "blockchain.data_integrity.verified"
    DATA_TAMPERING_DETECTED = "blockchain.data_tampering.detected"


class EventPriority(Enum):
    """事件优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventCategory(Enum):
    """事件分类"""
    AGENT_COLLABORATION = "agent_collaboration"
    HEALTH_DATA = "health_data"
    USER_INTERACTION = "user_interaction"
    SYSTEM = "system"
    BLOCKCHAIN = "blockchain"
    SECURITY = "security"
    PERFORMANCE = "performance"


# 事件类型到分类的映射
EVENT_TYPE_CATEGORY_MAP: Dict[str, EventCategory] = {
    # 智能体协同事件
    **{event: EventCategory.AGENT_COLLABORATION for event in [
        AgentCollaborationEvents.DIAGNOSIS_STARTED,
        AgentCollaborationEvents.DIAGNOSIS_COMPLETED,
        AgentCollaborationEvents.XIAOAI_LOOK_STARTED,
        AgentCollaborationEvents.XIAOKE_LISTEN_STARTED,
        AgentCollaborationEvents.LAOKE_INQUIRY_STARTED,
        AgentCollaborationEvents.SOER_PALPATION_STARTED,
    ]},
    
    # 健康数据事件
    **{event: EventCategory.HEALTH_DATA for event in [
        HealthDataEvents.HEALTH_DATA_RECEIVED,
        HealthDataEvents.VITAL_SIGNS_UPDATED,
        HealthDataEvents.DIAGNOSTIC_DATA_RECEIVED,
        HealthDataEvents.TCM_DATA_RECEIVED,
    ]},
    
    # 用户交互事件
    **{event: EventCategory.USER_INTERACTION for event in [
        UserInteractionEvents.USER_QUESTION_RECEIVED,
        UserInteractionEvents.AGENT_RESPONSE_GENERATED,
        UserInteractionEvents.USER_FEEDBACK_RECEIVED,
    ]},
    
    # 系统事件
    **{event: EventCategory.SYSTEM for event in [
        SystemEvents.SERVICE_STARTED,
        SystemEvents.SERVICE_ERROR,
        SystemEvents.DATABASE_CONNECTION_LOST,
    ]},
}


def get_event_category(event_type: str) -> EventCategory:
    """获取事件分类"""
    return EVENT_TYPE_CATEGORY_MAP.get(event_type, EventCategory.SYSTEM)


def get_event_priority(event_type: str) -> EventPriority:
    """根据事件类型获取优先级"""
    critical_events = [
        HealthDataEvents.VITAL_SIGNS_CRITICAL,
        SystemEvents.SECURITY_BREACH_DETECTED,
        SystemEvents.DATABASE_CONNECTION_LOST,
        BlockchainEvents.DATA_TAMPERING_DETECTED,
    ]
    
    high_priority_events = [
        HealthDataEvents.VITAL_SIGNS_ABNORMAL,
        AgentCollaborationEvents.DIAGNOSIS_FAILED,
        SystemEvents.SERVICE_ERROR,
        HealthDataEvents.DATA_VALIDATION_FAILED,
    ]
    
    if event_type in critical_events:
        return EventPriority.CRITICAL
    elif event_type in high_priority_events:
        return EventPriority.HIGH
    else:
        return EventPriority.NORMAL


# 事件模式定义（用于模式订阅）
class EventPatterns:
    """事件模式"""
    
    # 所有智能体事件
    ALL_AGENT_EVENTS = "*.agent.*"
    
    # 所有诊断事件
    ALL_DIAGNOSIS_EVENTS = "*.diagnosis.*"
    
    # 所有健康数据事件
    ALL_HEALTH_EVENTS = "health.*"
    
    # 所有系统事件
    ALL_SYSTEM_EVENTS = "system.*"
    
    # 所有错误事件
    ALL_ERROR_EVENTS = "*.*.failed"
    
    # 所有完成事件
    ALL_COMPLETED_EVENTS = "*.*.completed" 