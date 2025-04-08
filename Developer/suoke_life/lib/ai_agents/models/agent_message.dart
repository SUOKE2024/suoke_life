// 智能体消息模型
// 用于表示智能体对话中的消息

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

/// 智能体消息角色
enum AgentMessageRole {
  /// 系统消息
  system,
  
  /// 用户消息
  user,
  
  /// 助手消息
  assistant,
  
  /// 工具消息
  tool,
}

/// 智能体消息状态
enum AgentMessageStatus {
  /// 成功
  success,
  
  /// 错误
  error,
  
  /// 流式传输中
  streaming,
}

/// 智能体工具调用
class AgentToolCall {
  /// 调用ID
  final String id;
  
  /// 工具名称
  final String name;
  
  /// 工具参数（JSON字符串）
  final String arguments;
  
  /// 构造函数
  AgentToolCall({
    String? id,
    required this.name,
    required this.arguments,
  }) : id = id ?? const Uuid().v4();
  
  /// 从JSON创建
  factory AgentToolCall.fromJson(Map<String, dynamic> json) {
    return AgentToolCall(
      id: json['id'] as String? ?? const Uuid().v4(),
      name: json['name'] as String,
      arguments: json['arguments'] as String,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'arguments': arguments,
    };
  }
}

/// 智能体消息
class AgentMessage {
  /// 消息ID
  final String id;
  
  /// 消息角色
  final AgentMessageRole role;
  
  /// 消息内容
  String content;
  
  /// 消息状态
  AgentMessageStatus status;
  
  /// 工具调用ID (用于工具响应消息)
  String? toolCallId;
  
  /// 工具名称 (用于工具响应消息)
  String? name;
  
  /// 工具调用列表 (用于助手消息)
  List<AgentToolCall>? toolCalls;
  
  /// 时间戳
  final DateTime timestamp;
  
  /// 构造函数
  AgentMessage({
    String? id,
    required this.role,
    required this.content,
    this.status = AgentMessageStatus.success,
    this.toolCallId,
    this.name,
    this.toolCalls,
    DateTime? timestamp,
  }) : 
    id = id ?? const Uuid().v4(),
    timestamp = timestamp ?? DateTime.now();
  
  /// 创建系统消息
  factory AgentMessage.system({
    required String content,
    String? id,
  }) {
    return AgentMessage(
      id: id,
      role: AgentMessageRole.system,
      content: content,
    );
  }
  
  /// 创建用户消息
  factory AgentMessage.user({
    required String content,
    String? id,
  }) {
    return AgentMessage(
      id: id,
      role: AgentMessageRole.user,
      content: content,
    );
  }
  
  /// 创建助手消息
  factory AgentMessage.assistant({
    required String content,
    List<AgentToolCall>? toolCalls,
    AgentMessageStatus status = AgentMessageStatus.success,
    String? id,
  }) {
    return AgentMessage(
      id: id,
      role: AgentMessageRole.assistant,
      content: content,
      toolCalls: toolCalls,
      status: status,
    );
  }
  
  /// 创建工具结果消息
  factory AgentMessage.toolResult({
    required String content,
    required String toolCallId,
    String? name,
    AgentMessageStatus status = AgentMessageStatus.success,
    String? id,
  }) {
    return AgentMessage(
      id: id,
      role: AgentMessageRole.tool,
      content: content,
      toolCallId: toolCallId,
      name: name,
      status: status,
    );
  }
  
  /// 从JSON创建
  factory AgentMessage.fromJson(Map<String, dynamic> json) {
    return AgentMessage(
      id: json['id'] as String? ?? const Uuid().v4(),
      role: _roleFromString(json['role'] as String),
      content: json['content'] as String? ?? '',
      status: _statusFromString(json['status'] as String? ?? 'success'),
      toolCallId: json['tool_call_id'] as String?,
      name: json['name'] as String?,
      toolCalls: json['tool_calls'] != null
          ? (json['tool_calls'] as List)
              .map((tc) => AgentToolCall.fromJson(tc as Map<String, dynamic>))
              .toList()
          : null,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    final result = <String, dynamic>{
      'id': id,
      'role': _roleToString(role),
      'content': content,
      'status': _statusToString(status),
      'timestamp': timestamp.toIso8601String(),
    };
    
    if (toolCallId != null) {
      result['tool_call_id'] = toolCallId;
    }
    
    if (name != null) {
      result['name'] = name;
    }
    
    if (toolCalls != null && toolCalls!.isNotEmpty) {
      result['tool_calls'] = toolCalls!.map((tc) => tc.toJson()).toList();
    }
    
    return result;
  }
  
  /// 转换为模型消息格式
  Map<String, dynamic> toMap() {
    final result = <String, dynamic>{
      'role': _roleToString(role),
      'content': content,
    };
    
    if (role == AgentMessageRole.tool) {
      // 工具响应消息格式
      result['tool_call_id'] = toolCallId;
      if (name != null) {
        result['name'] = name;
      }
    } else if (role == AgentMessageRole.assistant && toolCalls != null) {
      // 助手消息带工具调用
      result['tool_calls'] = toolCalls!.map((tc) => tc.toJson()).toList();
    }
    
    return result;
  }
  
  /// 更新内容
  void updateContent(String newContent) {
    content = newContent;
  }
  
  /// 更新工具调用
  void updateWithToolCalls(List<AgentToolCall> newToolCalls) {
    toolCalls = newToolCalls;
  }
  
  /// 完成流式传输
  void completeStreaming() {
    if (status == AgentMessageStatus.streaming) {
      status = AgentMessageStatus.success;
    }
  }
  
  /// 角色转字符串
  static String _roleToString(AgentMessageRole role) {
    switch (role) {
      case AgentMessageRole.system:
        return 'system';
      case AgentMessageRole.user:
        return 'user';
      case AgentMessageRole.assistant:
        return 'assistant';
      case AgentMessageRole.tool:
        return 'tool';
    }
  }
  
  /// 字符串转角色
  static AgentMessageRole _roleFromString(String role) {
    switch (role.toLowerCase()) {
      case 'system':
        return AgentMessageRole.system;
      case 'user':
        return AgentMessageRole.user;
      case 'assistant':
        return AgentMessageRole.assistant;
      case 'tool':
        return AgentMessageRole.tool;
      default:
        return AgentMessageRole.user;
    }
  }
  
  /// 状态转字符串
  static String _statusToString(AgentMessageStatus status) {
    switch (status) {
      case AgentMessageStatus.success:
        return 'success';
      case AgentMessageStatus.error:
        return 'error';
      case AgentMessageStatus.streaming:
        return 'streaming';
    }
  }
  
  /// 字符串转状态
  static AgentMessageStatus _statusFromString(String status) {
    switch (status.toLowerCase()) {
      case 'success':
        return AgentMessageStatus.success;
      case 'error':
        return AgentMessageStatus.error;
      case 'streaming':
        return AgentMessageStatus.streaming;
      default:
        return AgentMessageStatus.success;
    }
  }
} 