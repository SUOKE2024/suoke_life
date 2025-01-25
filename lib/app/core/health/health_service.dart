import 'package:injectable/injectable.dart';
import '../network/network_service.dart';
import '../logger/logger.dart';
import '../storage/local_storage.dart';

@singleton
class HealthService {
  final NetworkService _network;
  final LocalStorage _storage;
  final AppLogger _logger;

  HealthService(this._network, this._storage, this._logger);

  Future<Map<String, dynamic>> getUserHealthProfile(String userId) async {
    try {
      final response = await _network.get('/health/profile/$userId');
      return response;
    } catch (e, stack) {
      _logger.error('Error getting health profile', e, stack);
      rethrow;
    }
  }

  Future<void> updateHealthData(Map<String, dynamic> data) async {
    try {
      await _network.post('/health/update', data);
      await _storage.setObject('health_data', data);
    } catch (e, stack) {
      _logger.error('Error updating health data', e, stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> analyzeTCMConstitution(
    Map<String, dynamic> answers,
  ) async {
    try {
      final response = await _network.post('/health/tcm/analyze', answers);
      return response;
    } catch (e, stack) {
      _logger.error('Error analyzing TCM constitution', e, stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getVitalSigns(String userId) async {
    try {
      final response = await _network.get('/health/vitals/$userId');
      return response;
    } catch (e, stack) {
      _logger.error('Error getting vital signs', e, stack);
      rethrow;
    }
  }
} 