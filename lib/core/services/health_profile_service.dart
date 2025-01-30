import 'package:suoke_life/lib/core/models/health_profile.dart';
import 'package:sqflite/sqflite.dart';

abstract class HealthProfileService {
  Future<HealthProfile?> getHealthProfile(String userId);
  Future<void> saveHealthProfile(HealthProfile healthProfile);
  // 可以根据需要添加更多健康画像相关操作接口
}

class HealthProfileServiceImpl implements HealthProfileService {
  //  这里假设 HealthProfile 数据存储在本地 sqflite 数据库中，您需要根据实际情况进行调整
  //  例如，可以使用 AgentMemoryService 或创建一个新的 DatabaseService 来操作 HealthProfile 数据表

  final DatabaseService _databaseService;
  final String _healthProfileTable;

  HealthProfileServiceImpl(this._databaseService, this._healthProfileTable);

  @override
  Future<HealthProfile?> getHealthProfile(String userId) async {
    try {
      // 从本地数据库获取用户健康画像数据
      final db = await _databaseService.database;
      final List<Map<String, dynamic>> maps = await db.query(
        _healthProfileTable,
        where: 'userId = ?',
        whereArgs: [userId],
      );

      if (maps.isNotEmpty) {
        return HealthProfile.fromMap(maps.first);
      } else {
        return null;
      }
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<void> saveHealthProfile(HealthProfile healthProfile) async {
    try {
      // 将用户健康画像数据保存到本地数据库
      final db = await _databaseService.database;
      await db.insert(
        _healthProfileTable,
        healthProfile.toMap(),
        conflictAlgorithm: ConflictAlgorithm.replace, // 如果已存在则替换
      );
    } catch (e) {
      rethrow;
    }
  }
} 