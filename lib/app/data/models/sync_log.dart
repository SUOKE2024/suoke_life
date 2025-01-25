import 'dart:convert';

class SyncLog {
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

  Map<String, dynamic> toMap() => {
    'id': id,
    'time': time.toIso8601String(),
    'type': type,
    'success': success ? 1 : 0,
    'error': error,
    'details': details != null ? json.encode(details) : null,
  };

  factory SyncLog.fromMap(Map<String, dynamic> map) => SyncLog(
    id: map['id'],
    time: DateTime.parse(map['time']),
    type: map['type'],
    success: map['success'] == 1,
    error: map['error'],
    details: map['details'] != null ? json.decode(map['details']) : null,
  );
} 