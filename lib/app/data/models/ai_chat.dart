import 'package:json_annotation/json_annotation.dart';

part 'ai_chat.g.dart';

@JsonSerializable()
class AiChat {
  final String id;
  final String userId;
  final String assistantType; // xiaoi, laoke, xiaoke
  final String message;
  final String? response;
  final DateTime createdAt;
  final bool isProcessed;

  AiChat({
    required this.id,
    required this.userId,
    required this.assistantType,
    required this.message,
    this.response,
    required this.createdAt,
    this.isProcessed = false,
  });

  factory AiChat.fromJson(Map<String, dynamic> json) => _$AiChatFromJson(json);
  Map<String, dynamic> toJson() => _$AiChatToJson(this);
} 