import 'package:json_annotation/json_annotation.dart';
import '../../core/config/doubao_config.dart';

class ChatConversation {
  final int id;
  final String title;
  final String model;
  final String avatar;
  final DateTime createdAt;
  final DateTime updatedAt;

  ChatConversation({
    required this.id,
    required this.title,
    required this.model,
    required this.avatar,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ChatConversation.fromJson(Map<String, dynamic> json) {
    return ChatConversation(
      id: json['id'],
      title: json['title'],
      model: json['model'] ?? DouBaoConfig.defaultModel,
      avatar: json['avatar'] ?? 'https://via.placeholder.com/100',
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'model': model,
      'avatar': avatar,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
} 