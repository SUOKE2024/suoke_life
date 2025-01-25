import 'package:json_annotation/json_annotation.dart';

part 'chat_message.g.dart';

@JsonSerializable()
class ChatMessage {
  final String id;
  final String content;
  final String senderId;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.content,
    required this.senderId,
    required this.timestamp,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) => 
      _$ChatMessageFromJson(json);

  Map<String, dynamic> toJson() => _$ChatMessageToJson(this);
} 