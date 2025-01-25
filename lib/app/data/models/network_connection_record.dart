class NetworkConnectionRecord {
  final String id;
  final DateTime timestamp;
  final String type;
  final bool isConnected;
  final String? errorMessage;
  final Map<String, dynamic>? metadata;

  const NetworkConnectionRecord({
    required this.id,
    required this.timestamp,
    required this.type,
    required this.isConnected,
    this.errorMessage,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'timestamp': timestamp.toIso8601String(),
    'type': type,
    'is_connected': isConnected,
    'error_message': errorMessage,
    'metadata': metadata,
  };

  factory NetworkConnectionRecord.fromJson(Map<String, dynamic> json) => 
    NetworkConnectionRecord(
      id: json['id'],
      timestamp: DateTime.parse(json['timestamp']),
      type: json['type'],
      isConnected: json['is_connected'],
      errorMessage: json['error_message'],
      metadata: json['metadata'],
    );
} 