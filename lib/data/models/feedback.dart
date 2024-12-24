

class FeedbackRecord extends HiveObject {
  final String id;

  final String type;

  final String content;

  final String? contact;

  final List<String>? images;

  final String time;

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
} 