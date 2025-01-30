class HealthAdvice {
  final String id;
  final String title;
  final String description;
  final String imageUrl;
  final String type;
  final bool isPremium;
  final Map<String, dynamic>? metadata;

  const HealthAdvice({
    required this.id,
    required this.title,
    required this.description,
    required this.imageUrl,
    required this.type,
    this.isPremium = false,
    this.metadata,
  });

  factory HealthAdvice.fromMap(Map<String, dynamic> map) => HealthAdvice(
    id: map['id'],
    title: map['title'],
    description: map['description'],
    imageUrl: map['image_url'],
    type: map['type'],
    isPremium: map['is_premium'] ?? false,
    metadata: map['metadata'],
  );

  Map<String, dynamic> toMap() => {
    'id': id,
    'title': title,
    'description': description,
    'image_url': imageUrl,
    'type': type,
    'is_premium': isPremium,
    'metadata': metadata,
  };
} 