class SyncConflict {
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

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type,
    'localTime': localTime.toIso8601String(),
    'serverTime': serverTime.toIso8601String(),
    'localData': localData,
    'serverData': serverData,
    'resolved': resolved,
    'resolution': resolution,
  };

  factory SyncConflict.fromJson(Map<String, dynamic> json) => SyncConflict(
    id: json['id'],
    type: json['type'],
    localTime: DateTime.parse(json['localTime']),
    serverTime: DateTime.parse(json['serverTime']), 
    localData: json['localData'],
    serverData: json['serverData'],
    resolved: json['resolved'] ?? false,
    resolution: json['resolution'],
  );

  SyncConflict copyWith({
    String? id,
    String? type,
    DateTime? localTime,
    DateTime? serverTime,
    Map<String, dynamic>? localData,
    Map<String, dynamic>? serverData,
    bool? resolved,
    String? resolution,
  }) {
    return SyncConflict(
      id: id ?? this.id,
      type: type ?? this.type,
      localTime: localTime ?? this.localTime,
      serverTime: serverTime ?? this.serverTime,
      localData: localData ?? this.localData,
      serverData: serverData ?? this.serverData,
      resolved: resolved ?? this.resolved,
      resolution: resolution ?? this.resolution,
    );
  }
} 