import 'package:injectable/injectable.dart';
import '../database/database_service.dart';

@lazySingleton
class DataCleanupService {
  final DatabaseService _db;

  DataCleanupService(this._db);

  Future<void> cleanupOldData() async {
    final thirtyDaysAgo = DateTime.now().subtract(const Duration(days: 30));
    await _db.delete(
      'analytics_data',
      where: 'created_at < ?',
      whereArgs: [thirtyDaysAgo.millisecondsSinceEpoch],
    );
  }

  Future<void> cleanupCache() async {
    await _db.delete('cache');
  }
}
