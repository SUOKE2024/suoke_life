class SyncConflict {
  final String id;
  final String title;
  final String description;
  final String type;
  final Map<String, dynamic> localData;
  final Map<String, dynamic> remoteData;
  final DateTime? timestamp;

  const SyncConflict({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.localData,
    required this.remoteData,
    this.timestamp,
  });

  factory SyncConflict.fromJson(Map<String, dynamic> json) => SyncConflict(
    id: json['id'],
    title: json['title'],
    description: json['description'],
    type: json['type'],
    localData: Map<String, dynamic>.from(json['local_data']),
    remoteData: Map<String, dynamic>.from(json['remote_data']),
    timestamp: json['timestamp'] != null
      ? DateTime.parse(json['timestamp'])
      : null,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'description': description,
    'type': type,
    'local_data': localData,
    'remote_data': remoteData,
    'timestamp': timestamp?.toIso8601String(),
  };
} 