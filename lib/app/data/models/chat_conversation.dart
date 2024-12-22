import 'package:json_annotation/json_annotation.dart';
import '../../core/config/doubao_config.dart';

class ChatConversation {
  int id;
  String title;
  String model;
  String avatar;
  String type;
  int unreadCount;
  DateTime lastMessageAt;
  DateTime createdAt;
  DateTime updatedAt;

  ChatConversation({
    required this.id,
    required this.title,
    required this.model,
    required this.avatar,
    this.type = 'ai',
    this.unreadCount = 0,
    DateTime? lastMessageAt,
    required this.createdAt,
    required this.updatedAt,
  }) : this.lastMessageAt = lastMessageAt ?? DateTime.now();

  set setModel(String value) => model = value;
  set setTitle(String value) => title = value;
  set setAvatar(String value) => avatar = value;
  set setUnreadCount(int value) => unreadCount = value;
  set setLastMessageAt(DateTime value) => lastMessageAt = value;

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