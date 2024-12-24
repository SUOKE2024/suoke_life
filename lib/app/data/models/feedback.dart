import 'dart:convert';

class FeedbackRecord {
  final String id;
  final String type;
  final String content;
  final String? contact;
  final List<String>? images;
  final DateTime time;
  final String status;

  FeedbackRecord({
    required this.id,
    required this.type,
    required this.content,
    this.contact,
    this.images,
    required this.time,
    this.status = '待处理',
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'type': type,
    'content': content,
    'contact': contact,
    'images': images != null ? json.encode(images) : null,
    'time': time.toIso8601String(),
    'status': status,
  };

  factory FeedbackRecord.fromMap(Map<String, dynamic> map) => FeedbackRecord(
    id: map['id'],
    type: map['type'],
    content: map['content'],
    contact: map['contact'],
    images: map['images'] != null ? List<String>.from(json.decode(map['images'])) : null,
    time: DateTime.parse(map['time']),
    status: map['status'] ?? '待处理',
  );
} 