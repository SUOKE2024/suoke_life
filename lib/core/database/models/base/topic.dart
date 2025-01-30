import 'package:injectable/injectable.dart';

@injectable
class Topic {
  final String id;
  final String title;
  final String description;
  final String? imageUrl;
  final List<String> tags;

  const Topic({
    required this.id,
    required this.title,
    required this.description,
    this.imageUrl,
    this.tags = const [],
  });

  factory Topic.fromJson(Map<String, dynamic> json) {
    return Topic(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      imageUrl: json['image_url'] as String?,
      tags: List<String>.from(json['tags'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'image_url': imageUrl,
      'tags': tags,
    };
  }
} 