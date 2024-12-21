import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/hive_type_ids.dart';

part 'sync_conflict.g.dart';

@HiveType(typeId: HiveTypeIds.syncConflict)
class SyncConflict extends HiveObject {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String type;

  @HiveField(2)
  final DateTime localTime;

  @HiveField(3)
  final DateTime serverTime;

  @HiveField(4)
  final Map<String, dynamic> localData;

  @HiveField(5)
  final Map<String, dynamic> serverData;

  @HiveField(6)
  final bool resolved;

  @HiveField(7)
  final String? resolution;

  SyncConflict({
    required this.id,
    required this.type,
    required this.localTime,
    required this.serverTime,
    required this.localData,
    required this.serverData,
    this.resolved = false,
    this.resolution,
  });

  SyncConflict copyWith({
    bool? resolved,
    String? resolution,
  }) {
    return SyncConflict(
      id: id,
      type: type,
      localTime: localTime,
      serverTime: serverTime,
      localData: localData,
      serverData: serverData,
      resolved: resolved ?? this.resolved,
      resolution: resolution ?? this.resolution,
    );
  }
} 