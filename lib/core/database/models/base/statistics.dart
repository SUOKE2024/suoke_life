class Statistics {
  final int totalRecords;
  final int todayRecords;
  final int streakDays;
  final double completionRate;
  final Map<String, dynamic>? metadata;

  const Statistics({
    required this.totalRecords,
    required this.todayRecords,
    required this.streakDays,
    required this.completionRate,
    this.metadata,
  });

  factory Statistics.empty() => const Statistics(
    totalRecords: 0,
    todayRecords: 0,
    streakDays: 0,
    completionRate: 0.0,
  );

  factory Statistics.fromMap(Map<String, dynamic> map) => Statistics(
    totalRecords: map['total_records'] ?? 0,
    todayRecords: map['today_records'] ?? 0,
    streakDays: map['streak_days'] ?? 0,
    completionRate: map['completion_rate']?.toDouble() ?? 0.0,
    metadata: map['metadata'],
  );

  Map<String, dynamic> toMap() => {
    'total_records': totalRecords,
    'today_records': todayRecords,
    'streak_days': streakDays,
    'completion_rate': completionRate,
    'metadata': metadata,
  };

  Statistics copyWith({
    int? totalRecords,
    int? todayRecords,
    int? streakDays,
    double? completionRate,
    Map<String, dynamic>? metadata,
  }) => Statistics(
    totalRecords: totalRecords ?? this.totalRecords,
    todayRecords: todayRecords ?? this.todayRecords,
    streakDays: streakDays ?? this.streakDays,
    completionRate: completionRate ?? this.completionRate,
    metadata: metadata ?? this.metadata,
  );
} 