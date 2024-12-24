

class Tag extends HiveObject {
  final String id;

  final String name;

  final DateTime createdAt;

  final DateTime? updatedAt;

  Tag({
    required this.id,
    required this.name,
    required this.createdAt,
    this.updatedAt,
  });

  factory Tag.fromJson(Map<String, dynamic> json) {
    return Tag(
      id: json['id'],
      name: json['name'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null 
          ? DateTime.parse(json['updatedAt'])
          : null,
    );
  }
} 