import 'dart:convert';

class SyncLog {
  final String id;
  final DateTime timestamp;
  final String type;
  final String status;
  final String details;
  final int recordCount;

  const SyncLog({
    required this.id,
    required this.timestamp,
    required this.type,
    required this.status,
    required this.details,
    required this.recordCount,
  });

  factory SyncLog.fromJson(Map<String, dynamic> json) {
    return SyncLog(
      id: json['id'],
      timestamp: DateTime.parse(json['timestamp']),
      type: json['type'],
      status: json['status'],
      details: json['details'],
      recordCount: json['record_count'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'timestamp': timestamp.toIso8601String(),
      'type': type,
      'status': status,
      'details': details,
      'record_count': recordCount,
    };
  }

  @override
  String toString() {
    return const JsonEncoder.withIndent('  ').convert(toJson());
  }
} 