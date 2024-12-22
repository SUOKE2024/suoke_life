class ExploreItem {
  final String id;
  final String title;
  final String subtitle;
  final String? imageUrl;
  final String type;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;

  ExploreItem({
    required this.id,
    required this.title,
    required this.subtitle,
    this.imageUrl,
    required this.type,
    this.metadata,
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'subtitle': subtitle,
      'image_url': imageUrl,
      'type': type,
      'metadata': metadata,
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory ExploreItem.fromMap(Map<String, dynamic> map) {
    return ExploreItem(
      id: map['id'],
      title: map['title'],
      subtitle: map['subtitle'],
      imageUrl: map['image_url'],
      type: map['type'],
      metadata: map['metadata'],
      createdAt: DateTime.parse(map['created_at']),
    );
  }
} 