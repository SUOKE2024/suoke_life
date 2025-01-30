import 'package:injectable/injectable.dart';
import '../network/network_service.dart';
import '../logger/logger.dart';
import '../storage/local_storage.dart';

@singleton
class TCMService {
  final NetworkService _network;
  final LocalStorage _storage;
  final AppLogger _logger;

  TCMService(this._network, this._storage, this._logger);

  Future<Map<String, dynamic>> analyzeConstitution(
    Map<String, dynamic> answers,
  ) async {
    try {
      final response = await _network.post('/health/tcm/analyze', answers);
      await _storage.setObject('tcm_result', response);
      return response;
    } catch (e, stack) {
      _logger.error('Error analyzing TCM constitution', e, stack);
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getRecommendations(String userId) async {
    try {
      final response = await _network.get('/health/tcm/recommendations/$userId');
      return List<Map<String, dynamic>>.from(response['recommendations']);
    } catch (e, stack) {
      _logger.error('Error getting TCM recommendations', e, stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getDietPlan(String userId) async {
    try {
      final response = await _network.get('/health/tcm/diet/$userId');
      return response;
    } catch (e, stack) {
      _logger.error('Error getting TCM diet plan', e, stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getLifestyleAdvice(String userId) async {
    try {
      final response = await _network.get('/health/tcm/lifestyle/$userId');
      return response;
    } catch (e, stack) {
      _logger.error('Error getting TCM lifestyle advice', e, stack);
      rethrow;
    }
  }
} 