class SyncSettings {
  final bool autoSync;
  final String interval;
  final String range;
  final String conflictStrategy;

  const SyncSettings({
    required this.autoSync,
    required this.interval,
    required this.range,
    required this.conflictStrategy,
  });

  factory SyncSettings.fromJson(Map<String, dynamic> json) {
    return SyncSettings(
      autoSync: json['auto_sync'] ?? false,
      interval: json['interval'] ?? '每天',
      range: json['range'] ?? '最近7天',
      conflictStrategy: json['conflict_strategy'] ?? '手动处理',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'auto_sync': autoSync,
      'interval': interval,
      'range': range,
      'conflict_strategy': conflictStrategy,
    };
  }

  SyncSettings copyWith({
    bool? autoSync,
    String? interval,
    String? range,
    String? conflictStrategy,
  }) {
    return SyncSettings(
      autoSync: autoSync ?? this.autoSync,
      interval: interval ?? this.interval,
      range: range ?? this.range,
      conflictStrategy: conflictStrategy ?? this.conflictStrategy,
    );
  }
} 