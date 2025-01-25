import 'dart:convert';

class SyncConfig {
  final String id;
  final bool autoSync;
  final bool wifiOnlySync;
  final List<String> syncRanges;
  final DateTime? lastSyncTime;

  SyncConfig({
    required this.id,
    required this.autoSync,
    required this.wifiOnlySync,
    required this.syncRanges,
    this.lastSyncTime,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'auto_sync': autoSync ? 1 : 0,
    'wifi_only_sync': wifiOnlySync ? 1 : 0,
    'sync_ranges': json.encode(syncRanges),
    'last_sync_time': lastSyncTime?.toIso8601String(),
  };

  factory SyncConfig.fromMap(Map<String, dynamic> map) => SyncConfig(
    id: map['id'],
    autoSync: map['auto_sync'] == 1,
    wifiOnlySync: map['wifi_only_sync'] == 1,
    syncRanges: List<String>.from(json.decode(map['sync_ranges'])),
    lastSyncTime: map['last_sync_time'] != null 
        ? DateTime.parse(map['last_sync_time'])
        : null,
  );
} 