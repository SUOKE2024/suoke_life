class KnowledgeDocument {
  final String id;
  final String title;
  final String content;
  final String type;
  final String collectionId;
  final String userId;
  final List<String>? tags;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final Map<String, dynamic>? metadata;

  const KnowledgeDocument({
    required this.id,
    required this.title,
    required this.content,
    required this.type,
    required this.collectionId,
    required this.userId,
    this.tags,
    DateTime? createdAt,
    this.updatedAt,
    this.metadata,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'id': id,
    'title': title,
    'content': content,
    'type': type,
    'collection_id': collectionId,
    'user_id': userId,
    'tags': tags,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt?.toIso8601String(),
    'metadata': metadata,
  };

  factory KnowledgeDocument.fromMap(Map<String, dynamic> map) => KnowledgeDocument(
    id: map['id'],
    title: map['title'],
    content: map['content'],
    type: map['type'],
    collectionId: map['collection_id'],
    userId: map['user_id'],
    tags: map['tags'] != null ? List<String>.from(map['tags']) : null,
    createdAt: DateTime.parse(map['created_at']),
    updatedAt: map['updated_at'] != null ? 
      DateTime.parse(map['updated_at']) : null,
    metadata: map['metadata'],
  );

  KnowledgeDocument copyWith({
    String? title,
    String? content,
    String? type,
    List<String>? tags,
    Map<String, dynamic>? metadata,
  }) => KnowledgeDocument(
    id: id,
    title: title ?? this.title,
    content: content ?? this.content,
    type: type ?? this.type,
    collectionId: collectionId,
    userId: userId,
    tags: tags ?? this.tags,
    createdAt: createdAt,
    updatedAt: DateTime.now(),
    metadata: metadata ?? this.metadata,
  );
}

class KnowledgeCollection {
  final String id;
  final String name;
  final String description;
  final String userId;
  final List<String>? tags;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final Map<String, dynamic>? metadata;

  const KnowledgeCollection({
    required this.id,
    required this.name,
    required this.description,
    required this.userId,
    this.tags,
    DateTime? createdAt,
    this.updatedAt,
    this.metadata,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'id': id,
    'name': name,
    'description': description,
    'user_id': userId,
    'tags': tags,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt?.toIso8601String(),
    'metadata': metadata,
  };

  factory KnowledgeCollection.fromMap(Map<String, dynamic> map) => KnowledgeCollection(
    id: map['id'],
    name: map['name'],
    description: map['description'],
    userId: map['user_id'],
    tags: map['tags'] != null ? List<String>.from(map['tags']) : null,
    createdAt: DateTime.parse(map['created_at']),
    updatedAt: map['updated_at'] != null ? 
      DateTime.parse(map['updated_at']) : null,
    metadata: map['metadata'],
  );
}

class SearchOptions {
  final bool caseSensitive;
  final bool wholeWord;
  final bool useRegex;
  final int? limit;
  final String? sortBy;
  final bool? ascending;

  const SearchOptions({
    this.caseSensitive = false,
    this.wholeWord = false,
    this.useRegex = false,
    this.limit,
    this.sortBy,
    this.ascending,
  });
} 