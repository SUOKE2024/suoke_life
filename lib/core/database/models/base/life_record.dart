import 'package:injectable/injectable.dart';

enum RecordType {
  daily,
  health,
  event,
  note,
}

@injectable
class LifeRecord {
  final String id;
  final String title;
  final String content;
  final String type;
  final DateTime createdAt;

  const LifeRecord({
    required this.id,
    required this.title,
    required this.content,
    required this.type,
    required this.createdAt,
  });

  factory LifeRecord.fromJson(Map<String, dynamic> json) {
    return LifeRecord(
      id: json['id'] as String,
      title: json['title'] as String,
      content: json['content'] as String,
      type: json['type'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'type': type,
      'created_at': createdAt.toIso8601String(),
    };
  }
} 