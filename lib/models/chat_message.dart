import 'package:flutter/foundation.dart';

/// 消息角色枚举
enum MessageRole {
  user,     // 用户
  assistant, // AI助手
  system    // 系统
}

/// 聊天消息模型
class ChatMessage {
  final String id;           // 消息ID
  final String content;      // 消息内容
  final MessageRole role;    // 消息角色
  final DateTime timestamp;  // 时间戳
  final bool isError;        // 是否为错误消息
  final Map<String, dynamic>? metadata; // 元数据（如token使用情况等）

  const ChatMessage({
    required this.id,
    required this.content,
    required this.role,
    required this.timestamp,
    this.isError = false,
    this.metadata,
  });

  /// 从JSON创建消息
  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as String,
      content: json['content'] as String,
      role: MessageRole.values.firstWhere(
        (e) => e.toString() == 'MessageRole.${json['role']}',
        orElse: () => MessageRole.user,
      ),
      timestamp: DateTime.parse(json['timestamp'] as String),
      isError: json['isError'] as bool? ?? false,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'role': role.toString().split('.').last,
      'timestamp': timestamp.toIso8601String(),
      'isError': isError,
      if (metadata != null) 'metadata': metadata,
    };
  }

  /// 创建用户消息
  factory ChatMessage.user({
    required String content,
  }) {
    return ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      role: MessageRole.user,
      timestamp: DateTime.now(),
    );
  }

  /// 创建AI助手消息
  factory ChatMessage.assistant({
    required String content,
    Map<String, dynamic>? metadata,
  }) {
    return ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      role: MessageRole.assistant,
      timestamp: DateTime.now(),
      metadata: metadata,
    );
  }

  /// 创建系统消息
  factory ChatMessage.system({
    required String content,
  }) {
    return ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      role: MessageRole.system,
      timestamp: DateTime.now(),
    );
  }

  /// 创建错误消息
  factory ChatMessage.error({
    required String content,
    Map<String, dynamic>? metadata,
  }) {
    return ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      role: MessageRole.assistant,
      timestamp: DateTime.now(),
      isError: true,
      metadata: metadata,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ChatMessage &&
        other.id == id &&
        other.content == content &&
        other.role == role &&
        other.timestamp == timestamp &&
        other.isError == isError &&
        mapEquals(other.metadata, metadata);
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      content,
      role,
      timestamp,
      isError,
      metadata,
    );
  }
} 