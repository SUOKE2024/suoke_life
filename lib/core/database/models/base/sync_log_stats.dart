class SyncLogStats {
  final int totalCount;
  final int successCount;
  final int failureCount;
  final int cancelCount;
  final Map<String, int> typeStats;
  final int totalRecords;
  final double successRate;

  const SyncLogStats({
    required this.totalCount,
    required this.successCount,
    required this.failureCount,
    required this.cancelCount,
    required this.typeStats,
    required this.totalRecords,
    required this.successRate,
  });

  factory SyncLogStats.fromLogs(List<SyncLog> logs) {
    int success = 0;
    int failure = 0;
    int cancel = 0;
    int records = 0;
    final types = <String, int>{};

    for (final log in logs) {
      switch (log.status) {
        case '成功':
          success++;
          break;
        case '失败':
          failure++;
          break;
        case '取消':
          cancel++;
          break;
      }

      records += log.recordCount;
      types[log.type] = (types[log.type] ?? 0) + 1;
    }

    return SyncLogStats(
      totalCount: logs.length,
      successCount: success,
      failureCount: failure,
      cancelCount: cancel,
      typeStats: types,
      totalRecords: records,
      successRate: logs.isEmpty ? 0 : success / logs.length,
    );
  }
} 