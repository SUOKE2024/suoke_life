import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/core/models/life_activity_data.dart';
import 'package:suoke_life/core/repositories/life_activity_data_repository.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart';

class LifeActivityDataRepositoryImpl implements LifeActivityDataRepository {
  final DatabaseService _databaseService;

  LifeActivityDataRepositoryImpl(this._databaseService);

  @override
  Future<List<LifeActivityData>> getLifeActivityData(String userId) async {
    final result = await _databaseService.query('life_activity_data', where: 'user_id = ?', whereArgs: [userId]);
    return result.map((e) => LifeActivityData.fromJson(e)).toList();
  }

  @override
  Future<LifeActivityData> addLifeActivityData(LifeActivityData lifeActivityData) async {
    final id = await _databaseService.insert('life_activity_data', lifeActivityData.toJson());
    return lifeActivityData.copyWith(id: id);
  }

  @override
  Future<LifeActivityData> updateLifeActivityData(LifeActivityData lifeActivityData) async {
    await _databaseService.update('life_activity_data', lifeActivityData.toJson(), where: 'id = ?', whereArgs: [lifeActivityData.id]);
    return lifeActivityData;
  }

  @override
  Future<void> deleteLifeActivityData(int id) async {
    await _databaseService.delete('life_activity_data', where: 'id = ?', whereArgs: [id]);
  }
} 