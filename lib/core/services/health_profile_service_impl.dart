import 'dart:convert';
import 'package:suoke_life/core/models/health_profile.dart';
import 'package:suoke_life/core/services/health_profile_service.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart'; // 导入 DatabaseService

class HealthProfileServiceImpl implements HealthProfileService {
  final DatabaseService _databaseService;
  static const String _healthProfileTable = 'health_profiles';

  HealthProfileServiceImpl(this._databaseService);

  @override
  Future<HealthProfile?> getHealthProfile(String userId) async {
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
  }

  @override
  Future<void> saveHealthProfile(HealthProfile healthProfile) async {
    final db = await _databaseService.database;
    await db.insert(
      _healthProfileTable,
      healthProfile.toMap(),
      conflictAlgorithm: ConflictAlgorithm.replace, //  如果已存在则替换
    );
  }
} 