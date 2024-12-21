class AIModel {
  final String id;
  final Map<String, dynamic> config;
  final Map<String, dynamic>? metadata;

  const AIModel({
    required this.id,
    required this.config,
    this.metadata,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'config': config,
    'metadata': metadata,
  };

  factory AIModel.fromMap(Map<String, dynamic> map) => AIModel(
    id: map['id'],
    config: Map<String, dynamic>.from(map['config']),
    metadata: map['metadata'],
  );

  AIModel copyWith({
    Map<String, dynamic>? config,
    Map<String, dynamic>? metadata,
  }) => AIModel(
    id: id,
    config: config ?? this.config,
    metadata: metadata ?? this.metadata,
  );
}

class ModelStatus {
  final bool isHealthy;
  final String status;
  final String? message;
  final DateTime timestamp;
  final Map<String, dynamic>? details;

  const ModelStatus({
    required this.isHealthy,
    required this.status,
    this.message,
    DateTime? timestamp,
    this.details,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'is_healthy': isHealthy,
    'status': status,
    'message': message,
    'timestamp': timestamp.toIso8601String(),
    'details': details,
  };

  factory ModelStatus.fromMap(Map<String, dynamic> map) => ModelStatus(
    isHealthy: map['is_healthy'],
    status: map['status'],
    message: map['message'],
    timestamp: DateTime.parse(map['timestamp']),
    details: map['details'],
  );
} 