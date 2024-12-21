import 'package:get/get.dart';

enum MessageType {
  text,
  image,
  voice,
  video,
  file,
}

class Message {
  final String id;
  final MessageType type;
  final String content;
  final bool isFromUser;
  final DateTime timestamp;
  final int? duration; // 语音/视频时长(秒)
  final String? thumbnail; // 视频缩略图
  final Map<String, dynamic>? metadata; // 额外数据

  Message({
    required this.id,
    required this.type,
    required this.content,
    required this.isFromUser,
    required this.timestamp,
    this.duration,
    this.thumbnail,
    this.metadata,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      type: MessageType.values[json['type']],
      content: json['content'],
      isFromUser: json['isFromUser'],
      timestamp: DateTime.parse(json['timestamp']),
      duration: json['duration'],
      thumbnail: json['thumbnail'],
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type.index,
      'content': content,
      'isFromUser': isFromUser,
      'timestamp': timestamp.toIso8601String(),
      'duration': duration,
      'thumbnail': thumbnail,
      'metadata': metadata,
    };
  }
} 