import 'package:suoke_life/lib/core/models/life_activity_data.dart';
import 'package:suoke_life/lib/core/services/network_service.dart';

class LifeServiceClient {
  final NetworkService _networkService;

  LifeServiceClient(this._networkService);

  Future<List<LifeActivityData>> getLifeActivityData(String userId) async {
    final response = await _networkService.get('/users/$userId/life_activity_data');
    if (response is List) {
      return response.map((e) => LifeActivityData.fromJson(e)).toList();
    } else {
      throw Exception('Invalid response format');
    }
  }

  Future<LifeActivityData> addLifeActivityData(LifeActivityData lifeActivityData) async {
    final response = await _networkService.post('/life_activity_data', lifeActivityData.toJson());
    return LifeActivityData.fromJson(response);
  }

  Future<LifeActivityData> updateLifeActivityData(LifeActivityData lifeActivityData) async {
    final response = await _networkService.put('/life_activity_data/${lifeActivityData.id}', lifeActivityData.toJson());
    return LifeActivityData.fromJson(response);
  }

  Future<void> deleteLifeActivityData(int id) async {
    await _networkService.delete('/life_activity_data/$id');
  }
} 