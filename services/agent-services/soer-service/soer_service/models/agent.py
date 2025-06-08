"""
agent - 索克生活项目模块
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any

"""
智能体相关数据模型

定义智能体消息、响应、对话历史等数据结构
"""




class MessageType(str, Enum):
    """消息类型枚举"""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    HEALTH_DATA = "health_data"
    NUTRITION_DATA = "nutrition_data"
    EXERCISE_DATA = "exercise_data"


class MessageRole(str, Enum):
    """消息角色枚举"""

    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class AgentPersonality(str, Enum):
    """智能体个性枚举"""

    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    EMPATHETIC = "empathetic"
    MOTIVATIONAL = "motivational"


class ExpertiseLevel(str, Enum):
    """专业水平枚举"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AgentMessage(BaseModel):
    """智能体消息模型"""

    message_id: str = Field(..., description = "消息ID")
    conversation_id: str = Field(..., description = "对话ID")
    user_id: str = Field(..., description = "用户ID")

    # 消息内容
    role: MessageRole = Field(..., description = "消息角色")
    message_type: MessageType = Field(..., description = "消息类型")
    content: str = Field(..., description = "消息内容")
    metadata: dict[str, Any] = Field(default_factory = dict, description = "消息元数据")

    # 时间信息
    timestamp: datetime = Field(default_factory = datetime.now, description = "消息时间")

    # 上下文信息
    context: dict[str, Any] = Field(default_factory = dict, description = "上下文信息")
    intent: str | None = Field(None, description = "用户意图")
    entities: list[dict[str, Any]] = Field(default_factory = list, description = "实体信息")

    # 处理状态
    is_processed: bool = Field(default = False, description = "是否已处理")
    processing_time: float | None = Field(None, description = "处理时间(秒)")


class AgentResponse(BaseModel):
    """智能体响应模型"""

    response_id: str = Field(..., description = "响应ID")
    message_id: str = Field(..., description = "对应消息ID")
    conversation_id: str = Field(..., description = "对话ID")
    user_id: str = Field(..., description = "用户ID")

    # 响应内容
    content: str = Field(..., description = "响应内容")
    response_type: MessageType = Field(default = MessageType.TEXT, description = "响应类型")

    # 智能体信息
    agent_name: str = Field(default = "索儿", description = "智能体名称")
    agent_personality: AgentPersonality = Field(
        default = AgentPersonality.FRIENDLY, description = "智能体个性"
    )
    confidence_score: float = Field(..., description = "置信度评分")

    # 响应特性
    suggestions: list[str] = Field(default_factory = list, description = "建议列表")
    quick_replies: list[str] = Field(default_factory = list, description = "快速回复选项")
    actions: list[dict[str, Any]] = Field(
        default_factory = list, description = "可执行动作"
    )

    # 时间信息
    timestamp: datetime = Field(default_factory = datetime.now, description = "响应时间")

    # 个性化信息
    personalization_factors: dict[str, Any] = Field(
        default_factory = dict, description = "个性化因素"
    )

    # 中医相关
    tcm_insights: dict[str, Any] | None = Field(None, description = "中医见解")


class ConversationHistory(BaseModel):
    """对话历史模型"""

    conversation_id: str = Field(..., description = "对话ID")
    user_id: str = Field(..., description = "用户ID")

    # 对话信息
    title: str = Field(..., description = "对话标题")
    start_time: datetime = Field(..., description = "开始时间")
    last_activity: datetime = Field(..., description = "最后活动时间")

    # 对话内容
    messages: list[AgentMessage] = Field(default_factory = list, description = "消息列表")
    message_count: int = Field(default = 0, description = "消息数量")

    # 对话状态
    status: str = Field(default = "active", description = "对话状态")
    is_archived: bool = Field(default = False, description = "是否已归档")

    # 对话分析
    topics: list[str] = Field(default_factory = list, description = "讨论话题")
    sentiment_analysis: dict[str, float] = Field(
        default_factory = dict, description = "情感分析"
    )
    user_satisfaction: int | None = Field(None, description = "用户满意度(1 - 5)")

    # 智能体配置
    agent_config: dict[str, Any] = Field(default_factory = dict, description = "智能体配置")


class AgentCapability(BaseModel):
    """智能体能力模型"""

    capability_id: str = Field(..., description = "能力ID")
    name: str = Field(..., description = "能力名称")
    description: str = Field(..., description = "能力描述")
    category: str = Field(..., description = "能力类别")

    # 能力特性
    is_enabled: bool = Field(default = True, description = "是否启用")
    confidence_threshold: float = Field(default = 0.7, description = "置信度阈值")

    # 使用统计
    usage_count: int = Field(default = 0, description = "使用次数")
    success_rate: float = Field(default = 0.0, description = "成功率")

    # 相关信息
    related_topics: list[str] = Field(default_factory = list, description = "相关话题")
    required_data: list[str] = Field(default_factory = list, description = "所需数据")


class AgentConfiguration(BaseModel):
    """智能体配置模型"""

    user_id: str = Field(..., description = "用户ID")

    # 个性化设置
    personality: AgentPersonality = Field(
        default = AgentPersonality.FRIENDLY, description = "个性类型"
    )
    expertise_level: ExpertiseLevel = Field(
        default = ExpertiseLevel.INTERMEDIATE, description = "专业水平"
    )
    language: str = Field(default = "zh - CN", description = "语言设置")

    # 交互偏好
    response_length: str = Field(default = "medium", description = "回复长度偏好")
    formality_level: str = Field(default = "casual", description = "正式程度")
    use_emojis: bool = Field(default = True, description = "是否使用表情符号")

    # 功能设置
    enabled_capabilities: list[str] = Field(
        default_factory = list, description = "启用的能力"
    )
    notification_preferences: dict[str, bool] = Field(
        default_factory = dict, description = "通知偏好"
    )

    # 隐私设置
    data_sharing_consent: bool = Field(default = False, description = "数据共享同意")
    analytics_consent: bool = Field(default = False, description = "分析同意")

    # 更新时间
    created_at: datetime = Field(default_factory = datetime.now, description = "创建时间")
    updated_at: datetime = Field(default_factory = datetime.now, description = "更新时间")


class ConversationFeedback(BaseModel):
    """对话反馈模型"""

    feedback_id: str = Field(..., description = "反馈ID")
    conversation_id: str = Field(..., description = "对话ID")
    user_id: str = Field(..., description = "用户ID")

    # 评分
    overall_rating: int = Field(..., description = "整体评分(1 - 5)")
    helpfulness: int = Field(..., description = "有用性(1 - 5)")
    accuracy: int = Field(..., description = "准确性(1 - 5)")
    friendliness: int = Field(..., description = "友好性(1 - 5)")

    # 反馈内容
    feedback_text: str | None = Field(None, description = "反馈文本")
    improvement_suggestions: list[str] = Field(
        default_factory = list, description = "改进建议"
    )

    # 问题分类
    issue_categories: list[str] = Field(default_factory = list, description = "问题类别")

    # 时间信息
    submitted_at: datetime = Field(default_factory = datetime.now, description = "提交时间")


class InteractionAnalytics(BaseModel):
    """交互分析模型"""

    user_id: str = Field(..., description = "用户ID")
    analysis_period: str = Field(..., description = "分析周期")
    start_date: datetime = Field(..., description = "开始日期")
    end_date: datetime = Field(..., description = "结束日期")

    # 使用统计
    total_conversations: int = Field(..., description = "总对话数")
    total_messages: int = Field(..., description = "总消息数")
    average_session_duration: float = Field(..., description = "平均会话时长(分钟)")

    # 话题分析
    top_topics: list[dict[str, Any]] = Field(
        default_factory = list, description = "热门话题"
    )
    topic_distribution: dict[str, float] = Field(
        default_factory = dict, description = "话题分布"
    )

    # 满意度分析
    average_satisfaction: float = Field(..., description = "平均满意度")
    satisfaction_trend: list[dict[str, Any]] = Field(
        default_factory = list, description = "满意度趋势"
    )

    # 使用模式
    peak_usage_hours: list[int] = Field(
        default_factory = list, description = "使用高峰时段"
    )
    usage_frequency: str = Field(..., description = "使用频率")

    # 改进建议
    improvement_areas: list[str] = Field(default_factory = list, description = "改进领域")
    feature_requests: list[str] = Field(default_factory = list, description = "功能请求")
