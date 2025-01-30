class KnowledgeNode {
  final String id;
  final String title;
  final String content;
  final String type;
  final List<String> relatedIds;
  final Map<String, dynamic>? metadata;

  KnowledgeNode({
    required this.id,
    required this.title,
    required this.content,
    required this.type,
    this.relatedIds = const [],
    this.metadata,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'title': title,
    'content': content,
    'type': type,
    'relatedIds': relatedIds,
    'metadata': metadata,
  };

  factory KnowledgeNode.fromMap(Map<String, dynamic> map) => KnowledgeNode(
    id: map['id'],
    title: map['title'],
    content: map['content'],
    type: map['type'],
    relatedIds: List<String>.from(map['relatedIds'] ?? []),
    metadata: map['metadata'],
  );
} 