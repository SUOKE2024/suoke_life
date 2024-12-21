import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/hive_type_ids.dart';

part 'sync_config.g.dart';

@HiveType(typeId: HiveTypeIds.syncConfig)
class SyncConfig extends HiveObject {
  @HiveField(0)
  final bool autoSync;

  @HiveField(1)
  final bool wifiOnlySync;

  @HiveField(2)
  final List<String> syncRanges;

  @HiveField(3)
  final DateTime? lastSyncTime;

  SyncConfig({
    this.autoSync = false,
    this.wifiOnlySync = true,
    this.syncRanges = const [],
    this.lastSyncTime,
  });

  SyncConfig copyWith({
    bool? autoSync,
    bool? wifiOnlySync,
    List<String>? syncRanges,
    DateTime? lastSyncTime,
  }) {
    return SyncConfig(
      autoSync: autoSync ?? this.autoSync,
      wifiOnlySync: wifiOnlySync ?? this.wifiOnlySync,
      syncRanges: syncRanges ?? this.syncRanges,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
    );
  }
} 