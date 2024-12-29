@singleton
class HealthService {
  final DatabaseService _db;
  final NetworkService _network;
  final SyncService _sync;

  HealthService(this._db, this._network, this._sync);

  Future<void> saveHealthRecord(HealthRecord record) async {
    // 本地存储
    await _db.insert('health_records', record.toMap());
    // 添加到同步队列
    await _sync.scheduleSync(SyncTask(
      type: SyncType.healthRecord,
      data: record.toMap(),
      priority: SyncPriority.high,
    ));
  }

  Future<List<HealthRecord>> getHealthRecords() async {
    final records = await _db.query('health_records');
    return records.map((r) => HealthRecord.fromMap(r)).toList();
  }
} 