import 'package:get/get.dart';
import '../data/repositories/api_client.dart';
import '../core/config/api_config.dart';

class HealthService extends GetxService {
  final ApiClient _apiClient;

  HealthService(this._apiClient);

  Future<Map<String, dynamic>> getUserHealth(String userId) async {
    try {
      final response = await _apiClient.get(
        '${ApiConfig.endpoints['health']}/users/$userId',
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> updateHealthData(String userId, Map<String, dynamic> data) async {
    try {
      await _apiClient.put(
        '${ApiConfig.endpoints['health']}/users/$userId',
        data: data,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getHealthAdvices(String userId) async {
    try {
      final response = await _apiClient.get(
        '${ApiConfig.endpoints['health']}/users/$userId/advices',
      );
      return List<Map<String, dynamic>>.from(response.data['advices']);
    } catch (e) {
      rethrow;
    }
  }
} 