class Feedback {
  final String id;
  final String type;
  final String content;
  final String? contact;
  final List<String>? images;
  final DateTime time;
  final String status;

  Feedback({
    required this.id,
    required this.type,
    required this.content,
    this.contact,
    this.images,
    required this.time,
    this.status = 'pending',
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'type': type,
      'content': content,
      'contact': contact,
      'images': images,
      'time': time.toIso8601String(),
      'status': status,
    };
  }

  factory Feedback.fromMap(Map<String, dynamic> map) {
    return Feedback(
      id: map['id'],
      type: map['type'],
      content: map['content'],
      contact: map['contact'],
      images: map['images'] != null ? List<String>.from(map['images']) : null,
      time: DateTime.parse(map['time']),
      status: map['status'] ?? 'pending',
    );
  }
} 