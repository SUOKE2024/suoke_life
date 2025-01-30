import 'package:get/get.dart';

enum MessageType {
  text,
  image,
  voice,
  video,
  file,
  system,
}

class Message {
  final String id;
  final String content;
  final String sender;
  final DateTime timestamp;
  final MessageType type;
  final bool isRead;
  final Map<String, dynamic>? metadata;

  Message({
    required this.id,
    required this.content,
    required this.sender,
    required this.timestamp,
    this.type = MessageType.text,
    this.isRead = false,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'content': content,
    'sender': sender,
    'timestamp': timestamp.toIso8601String(),
    'type': type.index,
    'isRead': isRead,
    'metadata': metadata,
  };

  factory Message.fromJson(Map<String, dynamic> json) => Message(
    id: json['id'],
    content: json['content'],
    sender: json['sender'],
    timestamp: DateTime.parse(json['timestamp']),
    type: MessageType.values[json['type'] ?? 0],
    isRead: json['isRead'] ?? false,
    metadata: json['metadata'],
  );

  Message copyWith({
    String? content,
    bool? isRead,
    Map<String, dynamic>? metadata,
  }) => Message(
    id: id,
    content: content ?? this.content,
    sender: sender,
    timestamp: timestamp,
    type: type,
    isRead: isRead ?? this.isRead,
    metadata: metadata ?? this.metadata,
  );
} 