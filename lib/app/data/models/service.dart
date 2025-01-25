import 'package:injectable/injectable.dart';

@injectable
class Service {
  final String id;
  final String title;
  final String description;
  final String? imageUrl;
  final String type;
  final Map<String, dynamic>? metadata;

  const Service({
    required this.id,
    required this.title,
    required this.description,
    this.imageUrl,
    required this.type,
    this.metadata,
  });

  factory Service.fromJson(Map<String, dynamic> json) {
    return Service(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      imageUrl: json['image_url'] as String?,
      type: json['type'] as String,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'image_url': imageUrl,
      'type': type,
      'metadata': metadata,
    };
  }
} 