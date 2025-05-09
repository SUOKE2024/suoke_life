import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

/// AI智能体类型枚举
enum AgentType {
  /// 小艾 - 交互与四诊协调
  xiaoAi,
  
  /// 小克 - 服务资源管理
  xiaoKe,
  
  /// 老克 - 知识传播
  laoKe,
  
  /// 索儿 - 生活健康管理
  suoEr,
}

/// 智能体消息类型枚举
enum MessageType {
  /// 用户发送的消息
  user,
  
  /// 智能体发送的消息
  agent,
  
  /// 系统消息
  system,
}

/// 消息内容类型枚举
enum ContentType {
  /// 文本消息
  text,
  
  /// 图片消息
  image,
  
  /// 语音消息
  voice,
  
  /// 诊断结果
  diagnosis,
}

/// 智能体能力枚举
enum AgentCapability {
  /// 常规对话
  conversation,
  
  /// 四诊引导
  diagnosisGuidance,
  
  /// 健康教育
  healthEducation,
  
  /// 服务推荐
  serviceRecommendation,
  
  /// 知识传播
  knowledgeSharing,
  
  /// 生活管理
  lifestyleManagement,
}

/// AI智能体模型类
class Agent extends Equatable {
  /// 智能体ID
  final String id;
  
  /// 智能体名称
  final String name;
  
  /// 智能体类型
  final AgentType type;
  
  /// 智能体描述
  final String description;
  
  /// 智能体头像URL
  final String avatarUrl;
  
  /// 智能体是否可用
  final bool isAvailable;
  
  /// 智能体最后活跃时间
  final DateTime lastActiveTime;
  
  /// 智能体创建时间
  final DateTime createdAt;

  /// 智能体拥有的能力
  final List<AgentCapability> capabilities;

  /// 构造函数
  const Agent({
    required this.id,
    required this.name,
    required this.type,
    required this.description,
    required this.avatarUrl,
    this.isAvailable = true,
    required this.lastActiveTime,
    required this.createdAt,
    this.capabilities = const [],
  });

  /// 获取智能体类型对应的主题色
  Color get themeColor {
    switch (type) {
      case AgentType.xiaoAi:
        return const Color(0xFF5E72E4); // 蓝色
      case AgentType.xiaoKe:
        return const Color(0xFFFF9F43); // 橙色
      case AgentType.laoKe:
        return const Color(0xFF11CDEF); // 青色
      case AgentType.suoEr:
        return const Color(0xFF35BB78); // 绿色
    }
  }

  /// 检查智能体是否拥有特定能力
  bool hasCapability(AgentCapability capability) {
    return capabilities.contains(capability);
  }

  @override
  List<Object?> get props => [id, type];
  
  /// 复制智能体并修改部分属性
  Agent copyWith({
    String? id,
    String? name,
    AgentType? type,
    String? description,
    String? avatarUrl,
    bool? isAvailable,
    DateTime? lastActiveTime,
    DateTime? createdAt,
    List<AgentCapability>? capabilities,
  }) {
    return Agent(
      id: id ?? this.id,
      name: name ?? this.name,
      type: type ?? this.type,
      description: description ?? this.description,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      isAvailable: isAvailable ?? this.isAvailable,
      lastActiveTime: lastActiveTime ?? this.lastActiveTime,
      createdAt: createdAt ?? this.createdAt,
      capabilities: capabilities ?? this.capabilities,
    );
  }
}

/// 智能体消息模型类
class AgentMessage extends Equatable {
  /// 消息ID
  final String id;
  
  /// 消息所属会话ID
  final String conversationId;
  
  /// 发送者ID（用户ID或智能体ID）
  final String senderId;
  
  /// 消息类型
  final MessageType messageType;
  
  /// 内容类型
  final ContentType contentType;
  
  /// 消息内容
  final String content;
  
  /// 消息创建时间
  final DateTime createdAt;
  
  /// 额外数据（用于特殊消息类型，如诊断结果等）
  final Map<String, dynamic>? extraData;

  /// 构造函数
  const AgentMessage({
    required this.id,
    required this.conversationId,
    required this.senderId,
    required this.messageType,
    required this.contentType,
    required this.content,
    required this.createdAt,
    this.extraData,
  });

  @override
  List<Object?> get props => [id, conversationId, senderId, messageType, contentType, createdAt];
  
  /// 复制消息并修改部分属性
  AgentMessage copyWith({
    String? id,
    String? conversationId,
    String? senderId,
    MessageType? messageType,
    ContentType? contentType,
    String? content,
    DateTime? createdAt,
    Map<String, dynamic>? extraData,
  }) {
    return AgentMessage(
      id: id ?? this.id,
      conversationId: conversationId ?? this.conversationId,
      senderId: senderId ?? this.senderId,
      messageType: messageType ?? this.messageType,
      contentType: contentType ?? this.contentType,
      content: content ?? this.content,
      createdAt: createdAt ?? this.createdAt,
      extraData: extraData ?? this.extraData,
    );
  }
}

/// 智能体会话模型类
class AgentConversation extends Equatable {
  /// 会话ID
  final String id;
  
  /// 会话标题
  final String title;
  
  /// 智能体ID
  final String agentId;
  
  /// 用户ID
  final String userId;
  
  /// 会话创建时间
  final DateTime createdAt;
  
  /// 最后消息时间
  final DateTime lastMessageTime;
  
  /// 是否为活跃会话
  final bool isActive;

  /// 构造函数
  const AgentConversation({
    required this.id,
    required this.title,
    required this.agentId,
    required this.userId,
    required this.createdAt,
    required this.lastMessageTime,
    this.isActive = true,
  });

  @override
  List<Object?> get props => [id, agentId, userId];
  
  /// 复制会话并修改部分属性
  AgentConversation copyWith({
    String? id,
    String? title,
    String? agentId,
    String? userId,
    DateTime? createdAt,
    DateTime? lastMessageTime,
    bool? isActive,
  }) {
    return AgentConversation(
      id: id ?? this.id,
      title: title ?? this.title,
      agentId: agentId ?? this.agentId,
      userId: userId ?? this.userId,
      createdAt: createdAt ?? this.createdAt,
      lastMessageTime: lastMessageTime ?? this.lastMessageTime,
      isActive: isActive ?? this.isActive,
    );
  }
}

/// 用户与智能体的交互历史记录模型
class UserInteraction extends Equatable {
  /// 交互ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 智能体类型
  final AgentType agentType;
  
  /// 会话ID
  final String conversationId;
  
  /// 交互主题或摘要
  final String topic;
  
  /// 交互发生时间
  final DateTime timestamp;
  
  /// 构造函数
  const UserInteraction({
    required this.id,
    required this.userId,
    required this.agentType,
    required this.conversationId,
    required this.topic,
    required this.timestamp,
  });
  
  @override
  List<Object?> get props => [id, userId, agentType, conversationId];
  
  /// 复制交互记录并修改部分属性
  UserInteraction copyWith({
    String? id,
    String? userId,
    AgentType? agentType,
    String? conversationId,
    String? topic,
    DateTime? timestamp,
  }) {
    return UserInteraction(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      agentType: agentType ?? this.agentType,
      conversationId: conversationId ?? this.conversationId,
      topic: topic ?? this.topic,
      timestamp: timestamp ?? this.timestamp,
    );
  }
}

/// 四诊引导状态枚举
enum DiagnosisGuidanceState {
  /// 未激活
  inactive,
  
  /// 准备中
  preparing,
  
  /// 引导中
  guiding,
  
  /// 分析中
  analyzing,
  
  /// 已完成
  completed,
}

/// 引导消息模型
class GuidanceMessage extends AgentMessage {
  /// 引导类型
  final String guidanceType;
  
  /// 引导步骤
  final int step;
  
  /// 期望的用户反馈类型
  final String expectedFeedbackType;
  
  /// 构造函数
  const GuidanceMessage({
    required String id,
    required String conversationId,
    required String senderId,
    required MessageType messageType,
    required ContentType contentType,
    required String content,
    required DateTime createdAt,
    Map<String, dynamic>? extraData,
    required this.guidanceType,
    required this.step,
    required this.expectedFeedbackType,
  }) : super(
          id: id,
          conversationId: conversationId,
          senderId: senderId,
          messageType: messageType,
          contentType: contentType,
          content: content,
          createdAt: createdAt,
          extraData: extraData,
        );
  
  /// 从AgentMessage创建GuidanceMessage
  factory GuidanceMessage.fromAgentMessage(
    AgentMessage message, {
    required String guidanceType,
    required int step,
    required String expectedFeedbackType,
  }) {
    return GuidanceMessage(
      id: message.id,
      conversationId: message.conversationId,
      senderId: message.senderId,
      messageType: message.messageType,
      contentType: message.contentType,
      content: message.content,
      createdAt: message.createdAt,
      extraData: message.extraData,
      guidanceType: guidanceType,
      step: step,
      expectedFeedbackType: expectedFeedbackType,
    );
  }
  
  @override
  GuidanceMessage copyWith({
    String? id,
    String? conversationId,
    String? senderId,
    MessageType? messageType,
    ContentType? contentType,
    String? content,
    DateTime? createdAt,
    Map<String, dynamic>? extraData,
    String? guidanceType,
    int? step,
    String? expectedFeedbackType,
  }) {
    return GuidanceMessage(
      id: id ?? this.id,
      conversationId: conversationId ?? this.conversationId,
      senderId: senderId ?? this.senderId,
      messageType: messageType ?? this.messageType,
      contentType: contentType ?? this.contentType,
      content: content ?? this.content,
      createdAt: createdAt ?? this.createdAt,
      extraData: extraData ?? this.extraData,
      guidanceType: guidanceType ?? this.guidanceType,
      step: step ?? this.step,
      expectedFeedbackType: expectedFeedbackType ?? this.expectedFeedbackType,
    );
  }
}

/// 诊断结果消息模型
class DiagnosisResultMessage extends AgentMessage {
  /// 诊断类型
  final String diagnosisType;
  
  /// 诊断结果数据
  final Map<String, dynamic> resultData;
  
  /// 体质评估结果
  final List<String>? constitutionResults;
  
  /// 健康建议
  final String? healthSuggestion;
  
  /// 构造函数
  const DiagnosisResultMessage({
    required String id,
    required String conversationId,
    required String senderId,
    required String content,
    required DateTime createdAt,
    Map<String, dynamic>? extraData,
    required this.diagnosisType,
    required this.resultData,
    this.constitutionResults,
    this.healthSuggestion,
  }) : super(
          id: id,
          conversationId: conversationId,
          senderId: senderId,
          messageType: MessageType.agent,
          contentType: ContentType.diagnosis,
          content: content,
          createdAt: createdAt,
          extraData: extraData,
        );
  
  @override
  DiagnosisResultMessage copyWith({
    String? id,
    String? conversationId,
    String? senderId,
    MessageType? messageType,
    ContentType? contentType,
    String? content,
    DateTime? createdAt,
    Map<String, dynamic>? extraData,
    String? diagnosisType,
    Map<String, dynamic>? resultData,
    List<String>? constitutionResults,
    String? healthSuggestion,
  }) {
    return DiagnosisResultMessage(
      id: id ?? this.id,
      conversationId: conversationId ?? this.conversationId,
      senderId: senderId ?? this.senderId,
      content: content ?? this.content,
      createdAt: createdAt ?? this.createdAt,
      extraData: extraData ?? this.extraData,
      diagnosisType: diagnosisType ?? this.diagnosisType,
      resultData: resultData ?? this.resultData,
      constitutionResults: constitutionResults ?? this.constitutionResults,
      healthSuggestion: healthSuggestion ?? this.healthSuggestion,
    );
  }
}