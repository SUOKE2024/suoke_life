class FeedbackRecord {
  final String id;
  final String type;
  final String status;
  final String content;
  final DateTime createdAt;
  final List<String> images;

  FeedbackRecord({
    required this.id,
    required this.type,
    required this.status,
    required this.content,
    required this.createdAt,
    required this.images,
  });

  factory FeedbackRecord.fromJson(Map<String, dynamic> json) {
    return FeedbackRecord(
      id: json['id'],
      type: json['type'],
      status: json['status'],
      content: json['content'],
      createdAt: DateTime.parse(json['created_at']),
      images: List<String>.from(json['images']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'status': status,
      'content': content,
      'created_at': createdAt.toIso8601String(),
      'images': images,
    };
  }
} 