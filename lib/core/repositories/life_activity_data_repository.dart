import 'package:suoke_life/lib/core/models/life_activity_data.dart';

abstract class LifeActivityDataRepository {
  Future<List<LifeActivityData>> getLifeActivityData(String userId);
  Future<LifeActivityData> addLifeActivityData(LifeActivityData lifeActivityData);
  Future<LifeActivityData> updateLifeActivityData(LifeActivityData lifeActivityData);
  Future<void> deleteLifeActivityData(int id);
} 