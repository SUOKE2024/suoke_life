import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';
import '../../domain/entities/chat.dart';
import 'message_model.dart';

part 'chat_model.g.dart';

/// 聊天会话数据模型
/// 用于处理API响应和本地存储的聊天会话数据
@JsonSerializable()
class ChatModel extends Equatable {
  final String id;
  final String title;
  final List<String> participantIds;
  @JsonKey(unknownEnumValue: ChatType.direct)
  final ChatType type;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final MessageModel? lastMessage;
  final Map<String, dynamic>? metadata;
  final bool isPinned;
  final bool isMuted;
  final bool isArchived;

  const ChatModel({
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

  /// 从JSON数据创建聊天会话模型
  factory ChatModel.fromJson(Map<String, dynamic> json) => _$ChatModelFromJson(json);

  /// 将聊天会话模型转换为JSON数据
  Map<String, dynamic> toJson() => _$ChatModelToJson(this);

  /// 将数据模型转换为领域实体
  Chat toEntity() => Chat(
        id: id,
        title: title,
        participantIds: participantIds,
        type: type,
        createdAt: createdAt,
        updatedAt: updatedAt,
        lastMessage: lastMessage?.toEntity(),
        metadata: metadata,
        isPinned: isPinned,
        isMuted: isMuted,
        isArchived: isArchived,
      );

  /// 从领域实体创建数据模型
  factory ChatModel.fromEntity(Chat chat) => ChatModel(
        id: chat.id,
        title: chat.title,
        participantIds: chat.participantIds,
        type: chat.type,
        createdAt: chat.createdAt,
        updatedAt: chat.updatedAt,
        lastMessage: chat.lastMessage != null
            ? MessageModel.fromEntity(chat.lastMessage!)
            : null,
        metadata: chat.metadata,
        isPinned: chat.isPinned,
        isMuted: chat.isMuted,
        isArchived: chat.isArchived,
      );

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