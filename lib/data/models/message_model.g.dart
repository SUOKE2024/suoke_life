// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'message_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MessageModel _$MessageModelFromJson(Map<String, dynamic> json) => MessageModel(
      id: json['id'] as String,
      content: json['content'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      senderId: json['senderId'] as String,
      receiverId: json['receiverId'] as String?,
      chatId: json['chatId'] as String?,
      type: $enumDecodeNullable(_$MessageTypeEnumMap, json['type'],
              unknownValue: MessageType.text) ??
          MessageType.text,
      status: $enumDecodeNullable(_$MessageStatusEnumMap, json['status'],
              unknownValue: MessageStatus.sent) ??
          MessageStatus.sent,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$MessageModelToJson(MessageModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'content': instance.content,
      'timestamp': instance.timestamp.toIso8601String(),
      'senderId': instance.senderId,
      'receiverId': instance.receiverId,
      'chatId': instance.chatId,
      'type': _$MessageTypeEnumMap[instance.type]!,
      'status': _$MessageStatusEnumMap[instance.status]!,
      'metadata': instance.metadata,
    };

const _$MessageTypeEnumMap = {
  MessageType.text: 'text',
  MessageType.image: 'image',
  MessageType.audio: 'audio',
  MessageType.video: 'video',
  MessageType.file: 'file',
  MessageType.system: 'system',
};

const _$MessageStatusEnumMap = {
  MessageStatus.sending: 'sending',
  MessageStatus.sent: 'sent',
  MessageStatus.delivered: 'delivered',
  MessageStatus.read: 'read',
  MessageStatus.failed: 'failed',
};
