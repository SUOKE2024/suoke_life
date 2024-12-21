class FeedbackRecord {
  final String id;
  final String type;
  final String content;
  final String? contact;
  final List<String> images;
  final String time;
  final String? reply;
  final String? replyTime;
  final String status;

  FeedbackRecord({
    required this.id,
    required this.type,
    required this.content,
    this.contact,
    this.images = const [],
    required this.time,
    this.reply,
    this.replyTime,
    this.status = 'pending',
  });

  factory FeedbackRecord.fromJson(Map<String, dynamic> json) {
    return FeedbackRecord(
      id: json['id'],
      type: json['type'],
      content: json['content'],
      contact: json['contact'],
      images: List<String>.from(json['images'] ?? []),
      time: json['time'],
      reply: json['reply'],
      replyTime: json['reply_time'],
      status: json['status'] ?? 'pending',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'content': content,
      'contact': contact,
      'images': images,
      'time': time,
      'reply': reply,
      'reply_time': replyTime,
      'status': status,
    };
  }
} 