import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';
import '../../domain/entities/message.dart';

part 'message_model.g.dart';

/// 消息数据模型
/// 用于处理API响应和本地存储的消息数据
@JsonSerializable()
class MessageModel extends Equatable {
  final String id;
  final String content;
  final DateTime timestamp;
  final String senderId;
  final String? receiverId;
  final String? chatId;
  @JsonKey(unknownEnumValue: MessageType.text)
  final MessageType type;
  @JsonKey(unknownEnumValue: MessageStatus.sent)
  final MessageStatus status;
  final Map<String, dynamic>? metadata;

  const MessageModel({
    required this.id,
    required this.content,
    required this.timestamp,
    required this.senderId,
    this.receiverId,
    this.chatId,
    this.type = MessageType.text,
    this.status = MessageStatus.sent,
    this.metadata,
  });

  /// 从JSON数据创建消息模型
  factory MessageModel.fromJson(Map<String, dynamic> json) =>
      _$MessageModelFromJson(json);

  /// 将消息模型转换为JSON数据
  Map<String, dynamic> toJson() => _$MessageModelToJson(this);

  /// 将数据模型转换为领域实体
  Message toEntity() => Message(
        id: id,
        content: content,
        timestamp: timestamp,
        senderId: senderId,
        receiverId: receiverId,
        chatId: chatId,
        type: type,
        status: status,
        metadata: metadata,
      );

  /// 从领域实体创建数据模型
  factory MessageModel.fromEntity(Message message) => MessageModel(
        id: message.id,
        content: message.content,
        timestamp: message.timestamp,
        senderId: message.senderId,
        receiverId: message.receiverId,
        chatId: message.chatId,
        type: message.type,
        status: message.status,
        metadata: message.metadata,
      );

  @override
  List<Object?> get props => [
        id,
        content,
        timestamp,
        senderId,
        receiverId,
        chatId,
        type,
        status,
        metadata,
      ];
} 