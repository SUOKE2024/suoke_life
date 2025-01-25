import 'package:suoke_life/core/models/health_data.dart';
import 'package:suoke_life/core/services/network_service.dart';

class HealthServiceClient {
  final NetworkService _networkService;

  HealthServiceClient(this._networkService);

  Future<List<HealthData>> getHealthData(String userId) async {
    final response = await _networkService.get('/users/$userId/health_data');
    if (response is List) {
      return response.map((e) => HealthData.fromJson(e)).toList();
    } else {
      throw Exception('Invalid response format');
    }
  }

  Future<HealthData> addHealthData(HealthData healthData) async {
    final response = await _networkService.post('/health_data', healthData.toJson());
    return HealthData.fromJson(response);
  }

  Future<HealthData> updateHealthData(HealthData healthData) async {
    final response = await _networkService.put('/health_data/${healthData.id}', healthData.toJson());
    return HealthData.fromJson(response);
  }

  Future<void> deleteHealthData(int id) async {
    await _networkService.delete('/health_data/$id');
  }
} 