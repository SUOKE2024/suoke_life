import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/core/models/health_data.dart';
import 'package:suoke_life/core/repositories/health_data_repository.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart';

class HealthDataRepositoryImpl implements HealthDataRepository {
  final DatabaseService _databaseService;

  HealthDataRepositoryImpl(this._databaseService);

  @override
  Future<List<HealthData>> getHealthData(String userId) async {
    final result = await _databaseService.query('health_data', where: 'user_id = ?', whereArgs: [userId]);
    return result.map((e) => HealthData.fromJson(e)).toList();
  }

  @override
  Future<HealthData> addHealthData(HealthData healthData) async {
    final id = await _databaseService.insert('health_data', healthData.toJson());
    return healthData.copyWith(id: id);
  }

  @override
  Future<HealthData> updateHealthData(HealthData healthData) async {
    await _databaseService.update('health_data', healthData.toJson(), where: 'id = ?', whereArgs: [healthData.id]);
    return healthData;
  }

  @override
  Future<void> deleteHealthData(int id) async {
    await _databaseService.delete('health_data', where: 'id = ?', whereArgs: [id]);
  }
} 