class ExploreItem {
  final String id;
  final String title;
  final String content;
  final String? imageUrl;
  final String? type;
  final DateTime createdAt;

  ExploreItem({
    required this.id,
    required this.title,
    required this.content,
    this.imageUrl,
    this.type,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory ExploreItem.fromMap(Map<String, dynamic> map) {
    return ExploreItem(
      id: map['id'] as String,
      title: map['title'] as String,
      content: map['content'] as String,
      imageUrl: map['image_url'] as String?,
      type: map['type'] as String?,
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] as int),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'image_url': imageUrl,
      'type': type,
      'created_at': createdAt.millisecondsSinceEpoch,
    };
  }
} 