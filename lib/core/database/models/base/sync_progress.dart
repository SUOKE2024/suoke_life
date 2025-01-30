class SyncProgress {
  final int total;
  final int current;
  final String stage;
  final double percentage;
  final String message;

  const SyncProgress({
    required this.total,
    required this.current,
    required this.stage,
    required this.percentage,
    required this.message,
  });

  factory SyncProgress.initial() {
    return const SyncProgress(
      total: 0,
      current: 0,
      stage: '准备同步',
      percentage: 0.0,
      message: '正在准备同步...',
    );
  }

  SyncProgress copyWith({
    int? total,
    int? current,
    String? stage,
    double? percentage,
    String? message,
  }) {
    return SyncProgress(
      total: total ?? this.total,
      current: current ?? this.current,
      stage: stage ?? this.stage,
      percentage: percentage ?? this.percentage,
      message: message ?? this.message,
    );
  }
} 