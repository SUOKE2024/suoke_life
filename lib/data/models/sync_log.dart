

class SyncLog extends HiveObject {
  final String id;

  final DateTime time;

  final String type;

  final bool success;

  final String? error;

  final Map<String, dynamic>? details;

  SyncLog({
    required this.id,
    required this.time,
    required this.type,
    required this.success,
    this.error,
    this.details,
  });
} 