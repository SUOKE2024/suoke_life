import 'package:json_annotation/json_annotation.dart';

part 'chat_message.g.dart';

@JsonSerializable()
class ChatMessage {
  final String id;
  final String content;
  final String senderId;
  final DateTime timestamp;
  final bool isRead;

  const ChatMessage({
    required this.id,
    required this.content,
    required this.senderId,
    required this.timestamp,
    this.isRead = false,
  });

  ChatMessage copyWith({
    String? id,
    String? content,
    String? senderId,
    DateTime? timestamp,
    bool? isRead,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      content: content ?? this.content,
      senderId: senderId ?? this.senderId,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
    );
  }

  factory ChatMessage.fromJson(Map<String, dynamic> json) => 
      _$ChatMessageFromJson(json);

  Map<String, dynamic> toJson() => _$ChatMessageToJson(this);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ChatMessage &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          content == other.content &&
          senderId == other.senderId &&
          timestamp == other.timestamp &&
          isRead == other.isRead;

  @override
  int get hashCode =>
      id.hashCode ^
      content.hashCode ^
      senderId.hashCode ^
      timestamp.hashCode ^
      isRead.hashCode;
} 