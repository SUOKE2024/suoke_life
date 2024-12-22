import 'package:json_annotation/json_annotation.dart';

part 'ai_chat.g.dart';

@JsonSerializable()
class AiChat {
  final String id;
  final String userId;
  final String assistantType;
  final String message;
  final DateTime createdAt;

  AiChat({
    required this.id,
    required this.userId,
    required this.assistantType,
    required this.message,
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'user_id': userId,
      'assistant_type': assistantType,
      'message': message,
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory AiChat.fromMap(Map<String, dynamic> map) {
    return AiChat(
      id: map['id'],
      userId: map['user_id'],
      assistantType: map['assistant_type'],
      message: map['message'],
      createdAt: DateTime.parse(map['created_at']),
    );
  }
} 