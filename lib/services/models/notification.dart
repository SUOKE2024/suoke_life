import 'package:uuid/uuid.dart';

class NotificationMessage {
  final String id;
  final String title;
  final String body;
  final DateTime timestamp;
  bool isRead;
  
  NotificationMessage({
    String? id,
    required this.title,
    required this.body,
    DateTime? timestamp,
    this.isRead = false,
  }) : id = id ?? const Uuid().v4(),
       timestamp = timestamp ?? DateTime.now();
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'body': body,
      'timestamp': timestamp.toIso8601String(),
      'isRead': isRead,
    };
  }
  
  factory NotificationMessage.fromJson(Map<String, dynamic> json) {
    return NotificationMessage(
      id: json['id'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      isRead: json['isRead'] as bool,
    );
  }
} 