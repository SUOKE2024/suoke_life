

class SyncConflict extends HiveObject {
  final String id;

  final String type;

  final DateTime localTime;

  final DateTime serverTime;

  final Map<String, dynamic> localData;

  final Map<String, dynamic> serverData;

  final bool resolved;

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