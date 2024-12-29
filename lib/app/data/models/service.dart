class Service {
  final String id;
  final String title;
  final String description;
  final String type;
  final String? imageUrl;
  final Map<String, dynamic>? config;

  Service({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    this.imageUrl,
    this.config,
  });

  factory Service.fromMap(Map<String, dynamic> map) {
    return Service(
      id: map['id'] as String,
      title: map['title'] as String,
      description: map['description'] as String,
      type: map['type'] as String,
      imageUrl: map['image_url'] as String?,
      config: map['config'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'type': type,
      'image_url': imageUrl,
      'config': config,
    };
  }
} 