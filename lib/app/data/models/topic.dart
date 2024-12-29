class Topic {
  final String id;
  final String title;
  final String description;
  final String? imageUrl;
  final List<String> tags;

  Topic({
    required this.id,
    required this.title,
    required this.description,
    this.imageUrl,
    this.tags = const [],
  });

  factory Topic.fromMap(Map<String, dynamic> map) {
    return Topic(
      id: map['id'] as String,
      title: map['title'] as String,
      description: map['description'] as String,
      imageUrl: map['image_url'] as String?,
      tags: List<String>.from(map['tags'] ?? []),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'image_url': imageUrl,
      'tags': tags,
    };
  }
} 