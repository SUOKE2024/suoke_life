// 智能体接口定义
// 定义了智能体的基本接口和对话上下文管理

import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:equatable/equatable.dart';

import 'package:suoke_life/ai_agents/models/agent_message.dart';
import 'package:suoke_life/ai_agents/tools/tool_interface.dart';

/// 智能体状态枚举
enum AgentStatus {
  /// 空闲状态
  idle,
  
  /// 思考中
  thinking,
  
  /// 执行工具
  executingTool,
  
  /// 回复中
  responding,
  
  /// 出错
  error
}

/// 智能体配置
class AgentConfig {
  /// 系统提示词
  final String systemPrompt;
  
  /// 温度参数
  final double temperature;
  
  /// 使用的模型名称
  final String modelName;
  
  /// 最大回复长度
  final int maxResponseTokens;
  
  /// 最大对话轮次
  final int maxConversationTurns;
  
  /// 启用的工具列表
  final List<String> enabledTools;
  
  /// 是否开启流式响应
  final bool streamResponse;
  
  /// 是否开启记忆功能
  final bool enableMemory;
  
  /// 是否可以上传文件
  final bool canUploadFiles;
  
  /// 是否应用OpenAI Assistants API风格
  final bool useAssistantsApiStyle;
  
  /// 构造函数
  const AgentConfig({
    required this.systemPrompt,
    this.temperature = 0.7,
    this.modelName = 'gpt-4o',
    this.maxResponseTokens = 1024,
    this.maxConversationTurns = 10,
    this.enabledTools = const [],
    this.streamResponse = true,
    this.enableMemory = true,
    this.canUploadFiles = false,
    this.useAssistantsApiStyle = true,
  });
  
  /// 复制并修改配置
  AgentConfig copyWith({
    String? systemPrompt,
    double? temperature,
    String? modelName,
    int? maxResponseTokens,
    int? maxConversationTurns,
    List<String>? enabledTools,
    bool? streamResponse,
    bool? enableMemory,
    bool? canUploadFiles,
    bool? useAssistantsApiStyle,
  }) {
    return AgentConfig(
      systemPrompt: systemPrompt ?? this.systemPrompt,
      temperature: temperature ?? this.temperature,
      modelName: modelName ?? this.modelName,
      maxResponseTokens: maxResponseTokens ?? this.maxResponseTokens,
      maxConversationTurns: maxConversationTurns ?? this.maxConversationTurns,
      enabledTools: enabledTools ?? this.enabledTools,
      streamResponse: streamResponse ?? this.streamResponse,
      enableMemory: enableMemory ?? this.enableMemory,
      canUploadFiles: canUploadFiles ?? this.canUploadFiles,
      useAssistantsApiStyle: useAssistantsApiStyle ?? this.useAssistantsApiStyle,
    );
  }
}

/// 对话消息类型
enum MessageType {
  /// 系统消息
  system,
  
  /// 用户消息
  user,
  
  /// 助手消息
  assistant,
  
  /// 工具消息
  tool,
  
  /// 文件消息
  file
}

/// 对话消息
class Message extends Equatable {
  /// 消息ID
  final String id;
  
  /// 消息类型
  final MessageType type;
  
  /// 消息内容
  final String content;
  
  /// 消息创建时间
  final DateTime createdAt;
  
  /// 工具调用
  final List<ToolCall>? toolCalls;
  
  /// 附加元数据
  final Map<String, dynamic>? metadata;
  
  /// 文件ID列表
  final List<String>? fileIds;

  /// 构造函数
  const Message({
    required this.id,
    required this.type,
    required this.content,
    required this.createdAt,
    this.toolCalls,
    this.metadata,
    this.fileIds,
  });

  /// 从JSON创建消息
  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      type: MessageType.values.firstWhere(
        (e) => e.toString().split('.').last == json['type'],
        orElse: () => MessageType.user,
      ),
      content: json['content'],
      createdAt: DateTime.parse(json['created_at']),
      toolCalls: json['tool_calls'] != null
          ? (json['tool_calls'] as List)
              .map((e) => ToolCall.fromJson(e))
              .toList()
          : null,
      metadata: json['metadata'],
      fileIds: json['file_ids'] != null 
          ? List<String>.from(json['file_ids']) 
          : null,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type.toString().split('.').last,
      'content': content,
      'created_at': createdAt.toIso8601String(),
      if (toolCalls != null)
        'tool_calls': toolCalls!.map((e) => e.toJson()).toList(),
      if (metadata != null) 'metadata': metadata,
      if (fileIds != null) 'file_ids': fileIds,
    };
  }

  /// 创建系统消息
  factory Message.system({
    required String content,
    String? id,
    DateTime? createdAt,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id ?? _generateId(),
      type: MessageType.system,
      content: content,
      createdAt: createdAt ?? DateTime.now(),
      metadata: metadata,
    );
  }

  /// 创建用户消息
  factory Message.user({
    required String content,
    String? id,
    DateTime? createdAt,
    List<String>? fileIds,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id ?? _generateId(),
      type: MessageType.user,
      content: content,
      createdAt: createdAt ?? DateTime.now(),
      fileIds: fileIds,
      metadata: metadata,
    );
  }

  /// 创建助手消息
  factory Message.assistant({
    required String content,
    String? id,
    DateTime? createdAt,
    List<ToolCall>? toolCalls,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id ?? _generateId(),
      type: MessageType.assistant,
      content: content,
      createdAt: createdAt ?? DateTime.now(),
      toolCalls: toolCalls,
      metadata: metadata,
    );
  }

  /// 创建工具消息
  factory Message.tool({
    required String content,
    required String toolCallId,
    String? id,
    DateTime? createdAt,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id ?? _generateId(),
      type: MessageType.tool,
      content: content,
      createdAt: createdAt ?? DateTime.now(),
      metadata: {
        'tool_call_id': toolCallId,
        ...?metadata,
      },
    );
  }
  
  /// 创建文件消息
  factory Message.file({
    required List<String> fileIds,
    String? content,
    String? id,
    DateTime? createdAt,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id ?? _generateId(),
      type: MessageType.file,
      content: content ?? '已上传文件',
      createdAt: createdAt ?? DateTime.now(),
      fileIds: fileIds,
      metadata: metadata,
    );
  }

  /// 复制并修改消息
  Message copyWith({
    String? id,
    MessageType? type,
    String? content,
    DateTime? createdAt,
    List<ToolCall>? toolCalls,
    Map<String, dynamic>? metadata,
    List<String>? fileIds,
  }) {
    return Message(
      id: id ?? this.id,
      type: type ?? this.type,
      content: content ?? this.content,
      createdAt: createdAt ?? this.createdAt,
      toolCalls: toolCalls ?? this.toolCalls,
      metadata: metadata ?? this.metadata,
      fileIds: fileIds ?? this.fileIds,
    );
  }

  @override
  List<Object?> get props => [id, type, content, createdAt, toolCalls, metadata, fileIds];
  
  /// 生成唯一ID
  static String _generateId() {
    return DateTime.now().millisecondsSinceEpoch.toString();
  }
}

/// 工具调用类
class ToolCall extends Equatable {
  /// 工具调用ID
  final String id;
  
  /// 工具名称
  final String toolName;
  
  /// 参数
  final Map<String, dynamic> parameters;
  
  /// 调用状态
  final String status;

  /// 构造函数
  const ToolCall({
    required this.id,
    required this.toolName,
    required this.parameters,
    this.status = 'pending',
  });

  /// 从JSON创建
  factory ToolCall.fromJson(Map<String, dynamic> json) {
    return ToolCall(
      id: json['id'],
      toolName: json['tool_name'],
      parameters: json['parameters'],
      status: json['status'] ?? 'pending',
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tool_name': toolName,
      'parameters': parameters,
      'status': status,
    };
  }
  
  /// 标记为成功完成
  ToolCall markAsCompleted() {
    return ToolCall(
      id: id,
      toolName: toolName,
      parameters: parameters,
      status: 'completed',
    );
  }
  
  /// 标记为失败
  ToolCall markAsFailed() {
    return ToolCall(
      id: id,
      toolName: toolName,
      parameters: parameters,
      status: 'failed',
    );
  }

  @override
  List<Object?> get props => [id, toolName, parameters, status];
}

/// 文件信息
class FileInfo extends Equatable {
  /// 文件ID
  final String id;
  
  /// 文件名
  final String filename;
  
  /// 文件类型
  final String contentType;
  
  /// 文件大小
  final int bytes;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 文件用途
  final String purpose;
  
  /// 元数据
  final Map<String, dynamic>? metadata;

  /// 构造函数
  const FileInfo({
    required this.id,
    required this.filename,
    required this.contentType,
    required this.bytes,
    required this.createdAt,
    required this.purpose,
    this.metadata,
  });
  
  /// 从JSON创建
  factory FileInfo.fromJson(Map<String, dynamic> json) {
    return FileInfo(
      id: json['id'],
      filename: json['filename'],
      contentType: json['content_type'],
      bytes: json['bytes'],
      createdAt: DateTime.parse(json['created_at']),
      purpose: json['purpose'],
      metadata: json['metadata'],
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'filename': filename,
      'content_type': contentType,
      'bytes': bytes,
      'created_at': createdAt.toIso8601String(),
      'purpose': purpose,
      if (metadata != null) 'metadata': metadata,
    };
  }

  @override
  List<Object?> get props => [id, filename, contentType, bytes, createdAt, purpose, metadata];
}

/// 智能体的流式响应监听器
typedef AgentStreamListener = void Function(String delta);

/// 智能体状态变化监听器
typedef AgentStatusListener = void Function(AgentStatus status);

/// 工具调用监听器
typedef ToolCallListener = void Function(ToolCall toolCall);

/// 工具调用结果监听器
typedef ToolResultListener = void Function(String toolCallId, ToolCallResult result);

/// 智能体接口 - 兼容OpenAI Assistants API风格
abstract class Agent {
  /// 智能体ID
  String get id;
  
  /// 智能体名称
  String get name;
  
  /// 智能体描述
  String get description;
  
  /// 智能体配置
  AgentConfig get config;
  
  /// 当前状态
  AgentStatus get status;
  
  /// 初始化智能体
  Future<void> initialize();
  
  /// 获取对话历史
  List<Message> getConversationHistory();
  
  /// 清空对话历史
  Future<void> clearConversation();
  
  /// 添加消息到对话历史
  void addMessage(Message message);
  
  /// 添加系统提示
  void addSystemPrompt(String content);
  
  /// 处理用户消息
  Future<Message> processUserMessage(String messageContent, {
    List<String>? fileIds,
    Map<String, dynamic>? metadata,
    AgentStreamListener? onStream,
  });
  
  /// 上传文件并返回文件ID
  Future<String> uploadFile(List<int> fileBytes, String filename, String contentType);
  
  /// 列出可用的文件
  Future<List<FileInfo>> listFiles();
  
  /// (异步)添加状态监听器
  void addStatusListener(AgentStatusListener listener);
  
  /// (异步)移除状态监听器
  void removeStatusListener(AgentStatusListener listener);
  
  /// (异步)添加工具调用监听器
  void addToolCallListener(ToolCallListener listener);
  
  /// (异步)移除工具调用监听器
  void removeToolCallListener(ToolCallListener listener);
  
  /// (异步)添加工具调用结果监听器
  void addToolResultListener(ToolResultListener listener);
  
  /// (异步)移除工具调用结果监听器
  void removeToolResultListener(ToolResultListener listener);
  
  /// 获取支持的工具列表
  List<Tool> getAvailableTools();
  
  /// 判断是否擅长特定任务
  bool isGoodAt(String task);
  
  /// 从另一个智能体接管对话
  Future<void> takeoverConversation(Agent otherAgent);
  
  /// 执行工具调用
  Future<ToolCallResult> executeToolCall(ToolCall toolCall);
  
  /// 中断响应
  Future<void> cancelResponse();
  
  /// 销毁智能体
  Future<void> dispose();
}

/// Agent工厂
abstract class AgentFactory {
  /// 创建智能体实例
  Future<Agent> createAgent(String agentId);
  
  /// 获取所有可用智能体ID
  List<String> getAvailableAgentIds();
  
  /// 获取智能体配置信息
  Map<String, dynamic> getAgentConfig(String agentId);
} 