import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/hive_type_ids.dart';

part 'sync_log.g.dart';

@HiveType(typeId: HiveTypeIds.syncLog)
class SyncLog extends HiveObject {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final DateTime time;

  @HiveField(2)
  final String type;

  @HiveField(3)
  final bool success;

  @HiveField(4)
  final String? error;

  @HiveField(5)
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