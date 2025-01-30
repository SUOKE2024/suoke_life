import 'package:injectable/injectable.dart';
import '../../domain/services/health_service.dart';
import '../../domain/models/health/health_data.dart';
import '../providers/database_provider.dart';

@LazySingleton(as: HealthService)
class HealthServiceImpl implements HealthService {
  final DatabaseProvider _db;

  const HealthServiceImpl(this._db);

  @override
  Future<void> initialize() async {
    // 实现初始化逻辑
  }

  @override
  Future<HealthData?> getUserHealth(String userId) async {
    final results = await _db.query(
      'user_health',
      where: 'user_id = ?',
      whereArgs: [userId],
      limit: 1,
    );
    return results.isEmpty ? null : HealthData.fromJson(results.first);
  }

  @override
  Future<void> updateUserHealth(String userId, HealthData data) async {
    await _db.update(
      'user_health',
      data.toJson(),
      where: 'user_id = ?',
      whereArgs: [userId],
    );
  }
} 