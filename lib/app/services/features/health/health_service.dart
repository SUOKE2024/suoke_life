import 'package:injectable/injectable.dart';
import '../../../core/network/network_service.dart';
import '../../../core/storage/local_storage.dart';
import '../../../core/logger/app_logger.dart';

@singleton
class HealthService {
  final NetworkService _network;
  final LocalStorage _storage;
  final AppLogger _logger;

  HealthService(this._network, this._storage, this._logger);

  Future<Map<String, dynamic>> getHealthMetrics() async {
    try {
      final cached = await _storage.get('health_metrics');
      if (cached != null) {
        return cached;
      }

      final response = await _network.get('/api/health/metrics');
      await _storage.set('health_metrics', response.data);
      return response.data;
    } catch (e, stack) {
      _logger.error('Failed to get health metrics', e, stack);
      rethrow;
    }
  }

  Future<void> updateHealthMetrics(Map<String, dynamic> metrics) async {
    try {
      await _network.post('/api/health/metrics', metrics);
    } catch (e) {
      _logger.error('Failed to update health metrics', e);
      rethrow;
    }
  }
} 