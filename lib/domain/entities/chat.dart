import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';
import 'message.dart';

/// 聊天类型枚举
enum ChatType {
  direct,
  group,
  ai,
  system,
}

/// 聊天会话实体类
/// 定义应用中聊天会话的核心属性和行为
class Chat extends Equatable {
  final String id;
  final String title;
  final List<String> participantIds;
  final ChatType type;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final Message? lastMessage;
  final Map<String, dynamic>? metadata;
  final bool isPinned;
  final bool isMuted;
  final bool isArchived;

  const Chat({
    required this.id,
    required this.title,
    required this.participantIds,
    required this.type,
    required this.createdAt,
    this.updatedAt,
    this.lastMessage,
    this.metadata,
    this.isPinned = false,
    this.isMuted = false,
    this.isArchived = false,
  });

  /// 创建新的AI聊天会话
  factory Chat.ai({
    required String userId,
    String? title,
    Map<String, dynamic>? metadata,
  }) {
    return Chat(
      id: const Uuid().v4(),
      title: title ?? '新的AI助手对话',
      participantIds: [userId, 'ai_assistant'],
      type: ChatType.ai,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      metadata: metadata,
    );
  }

  /// 创建新的直接聊天会话
  factory Chat.direct({
    required String userId,
    required String otherUserId,
    required String otherUserName,
    Map<String, dynamic>? metadata,
  }) {
    return Chat(
      id: const Uuid().v4(),
      title: otherUserName,
      participantIds: [userId, otherUserId],
      type: ChatType.direct,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      metadata: metadata,
    );
  }

  /// 创建新的群组聊天会话
  factory Chat.group({
    required String title,
    required List<String> memberIds,
    Map<String, dynamic>? metadata,
  }) {
    return Chat(
      id: const Uuid().v4(),
      title: title,
      participantIds: memberIds,
      type: ChatType.group,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      metadata: metadata,
    );
  }

  /// 创建带有更新字段的新聊天会话实例
  Chat copyWith({
    String? id,
    String? title,
    List<String>? participantIds,
    ChatType? type,
    DateTime? createdAt,
    DateTime? updatedAt,
    Message? lastMessage,
    Map<String, dynamic>? metadata,
    bool? isPinned,
    bool? isMuted,
    bool? isArchived,
  }) {
    return Chat(
      id: id ?? this.id,
      title: title ?? this.title,
      participantIds: participantIds ?? this.participantIds,
      type: type ?? this.type,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastMessage: lastMessage ?? this.lastMessage,
      metadata: metadata ?? this.metadata,
      isPinned: isPinned ?? this.isPinned,
      isMuted: isMuted ?? this.isMuted,
      isArchived: isArchived ?? this.isArchived,
    );
  }

  /// 更新最后一条消息和更新时间
  Chat updateLastMessage(Message message) {
    return copyWith(
      lastMessage: message,
      updatedAt: DateTime.now(),
    );
  }

  @override
  List<Object?> get props => [
        id,
        title,
        participantIds,
        type,
        createdAt,
        updatedAt,
        lastMessage,
        metadata,
        isPinned,
        isMuted,
        isArchived,
      ];
} 