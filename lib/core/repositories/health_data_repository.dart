import 'package:suoke_life/core/models/health_data.dart';

abstract class HealthDataRepository {
  Future<List<HealthData>> getHealthData(String userId);
  Future<HealthData> addHealthData(HealthData healthData);
  Future<HealthData> updateHealthData(HealthData healthData);
  Future<void> deleteHealthData(int id);
} 