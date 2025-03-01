import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

/// AI代理类型
enum AIAgentType {
  /// 小艾 - 处理日常交互，健康建议
  xiaoai,
  
  /// 老克 - 处理知识图谱管理，健康知识库
  laoke,
  
  /// 小克 - 处理服务管理，生活记录
  xiaoke,
  
  /// 系统代理 - 处理系统级功能
  system,
}

/// AI代理能力
enum AIAgentCapability {
  /// 聊天交互
  chat,
  
  /// 健康建议
  healthAdvice,
  
  /// 知识图谱
  knowledgeGraph,
  
  /// 服务管理
  serviceManagement,
  
  /// 生活记录
  lifeRecording,
  
  /// 系统管理
  systemManagement,
  
  /// 多模态处理
  multiModal,
}

/// AI代理消息类型
enum AIMessageType {
  /// 文本消息
  text,
  
  /// 图片消息
  image,
  
  /// 音频消息
  audio,
  
  /// 视频消息
  video,
  
  /// 文件消息
  file,
  
  /// 卡片消息
  card,
  
  /// 知识图谱消息
  knowledgeGraph,
  
  /// 健康数据消息
  healthData,
}

/// AI代理模型
class AIAgent extends Equatable {
  /// 代理ID
  final String id;
  
  /// 代理名称
  final String name;
  
  /// 代理类型
  final AIAgentType type;
  
  /// 代理头像URL
  final String avatarUrl;
  
  /// 代理介绍
  final String description;
  
  /// 代理能力列表
  final List<AIAgentCapability> capabilities;
  
  /// 代理模型配置
  final Map<String, dynamic> modelConfig;
  
  /// 创建AI代理
  const AIAgent({
    required this.id,
    required this.name,
    required this.type,
    required this.avatarUrl,
    required this.description,
    required this.capabilities,
    required this.modelConfig,
  });
  
  /// 获取代理颜色
  Color get color {
    switch (type) {
      case AIAgentType.xiaoai:
        return AppColors.aiXiaoai;
      case AIAgentType.laoke:
        return AppColors.aiLaoke;
      case AIAgentType.xiaoke:
        return AppColors.aiXiaoke;
      case AIAgentType.system:
        return Colors.grey;
    }
  }
  
  /// 检查代理是否具有指定能力
  bool hasCapability(AIAgentCapability capability) {
    return capabilities.contains(capability);
  }
  
  /// 复制代理并修改部分属性
  AIAgent copyWith({
    String? id,
    String? name,
    AIAgentType? type,
    String? avatarUrl,
    String? description,
    List<AIAgentCapability>? capabilities,
    Map<String, dynamic>? modelConfig,
  }) {
    return AIAgent(
      id: id ?? this.id,
      name: name ?? this.name,
      type: type ?? this.type,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      description: description ?? this.description,
      capabilities: capabilities ?? this.capabilities,
      modelConfig: modelConfig ?? this.modelConfig,
    );
  }
  
  @override
  List<Object?> get props => [id, name, type, avatarUrl, description, capabilities, modelConfig];
  
  /// 小艾代理
  static AIAgent get xiaoai => AIAgent(
    id: 'agent_xiaoai',
    name: '小艾',
    type: AIAgentType.xiaoai,
    avatarUrl: 'assets/images/agent_xiaoai.png', // 实际应用中需要提供真实的头像图片
    description: '您的健康生活助手，可以提供健康建议和日常交流。',
    capabilities: [
      AIAgentCapability.chat,
      AIAgentCapability.healthAdvice,
      AIAgentCapability.multiModal,
    ],
    modelConfig: {
      'model_id': 'gpt-4-vision-preview',
      'temperature': 0.7,
      'max_tokens': 1024,
    },
  );
  
  /// 老克代理
  static AIAgent get laoke => AIAgent(
    id: 'agent_laoke',
    name: '老克',
    type: AIAgentType.laoke,
    avatarUrl: 'assets/images/agent_laoke.png', // 实际应用中需要提供真实的头像图片
    description: '您的健康知识管家，擅长知识图谱构建和健康知识解答。',
    capabilities: [
      AIAgentCapability.chat,
      AIAgentCapability.knowledgeGraph,
      AIAgentCapability.multiModal,
    ],
    modelConfig: {
      'model_id': 'claude-3-opus-20240229',
      'temperature': 0.5,
      'max_tokens': 2048,
    },
  );
  
  /// 小克代理
  static AIAgent get xiaoke => AIAgent(
    id: 'agent_xiaoke',
    name: '小克',
    type: AIAgentType.xiaoke,
    avatarUrl: 'assets/images/agent_xiaoke.png', // 实际应用中需要提供真实的头像图片
    description: '您的生活服务管家，负责服务管理和生活记录。',
    capabilities: [
      AIAgentCapability.chat,
      AIAgentCapability.serviceManagement,
      AIAgentCapability.lifeRecording,
      AIAgentCapability.multiModal,
    ],
    modelConfig: {
      'model_id': 'claude-3-sonnet-20240229',
      'temperature': 0.6,
      'max_tokens': 1536,
    },
  );
  
  /// 系统代理
  static AIAgent get system => AIAgent(
    id: 'agent_system',
    name: '系统',
    type: AIAgentType.system,
    avatarUrl: 'assets/images/agent_system.png', // 实际应用中需要提供真实的头像图片
    description: '系统管理代理，负责系统级功能和管理。',
    capabilities: [
      AIAgentCapability.systemManagement,
    ],
    modelConfig: {
      'model_id': 'system',
      'temperature': 0.0,
      'max_tokens': 256,
    },
  );
  
  /// 获取所有预设代理
  static List<AIAgent> get allAgents => [
    xiaoai,
    laoke,
    xiaoke,
    system,
  ];
} 