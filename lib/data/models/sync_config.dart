

class SyncConfig extends HiveObject {
  final bool autoSync;

  final bool wifiOnlySync;

  final List<String> syncRanges;

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