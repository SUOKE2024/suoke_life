import '../models/health/health_data.dart';
import 'base_service.dart';

abstract class HealthService extends BaseService {
  Future<void> initialize();
  Future<HealthData?> getUserHealth(String userId);
  Future<void> updateUserHealth(String userId, HealthData data);
} 