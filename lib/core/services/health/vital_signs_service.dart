import 'package:injectable/injectable.dart';
import '../network/network_service.dart';
import '../logger/logger.dart';
import '../storage/local_storage.dart';

@singleton
class VitalSignsService {
  final NetworkService _network;
  final LocalStorage _storage;
  final AppLogger _logger;

  VitalSignsService(this._network, this._storage, this._logger);

  Future<void> recordVitalSigns(Map<String, dynamic> data) async {
    try {
      // 保存到本地
      await _storage.setObject(
        'vitals_${DateTime.now().toIso8601String()}',
        data,
      );

      // 上传到服务器
      await _network.post('/health/vitals/record', data);
    } catch (e, stack) {
      _logger.error('Error recording vital signs', e, stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> analyzeVitalSigns(String userId) async {
    try {
      final response = await _network.get('/health/vitals/analyze/$userId');
      return response;
    } catch (e, stack) {
      _logger.error('Error analyzing vital signs', e, stack);
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getVitalSignsHistory(
    String userId, {
    DateTime? start,
    DateTime? end,
  }) async {
    try {
      final response = await _network.get(
        '/health/vitals/history/$userId',
        params: {
          if (start != null) 'start': start.toIso8601String(),
          if (end != null) 'end': end.toIso8601String(),
        },
      );
      return List<Map<String, dynamic>>.from(response['history']);
    } catch (e, stack) {
      _logger.error('Error getting vital signs history', e, stack);
      rethrow;
    }
  }

  Future<void> setAlerts(String userId, Map<String, dynamic> alerts) async {
    try {
      await _network.post('/health/vitals/alerts/$userId', alerts);
    } catch (e, stack) {
      _logger.error('Error setting vital signs alerts', e, stack);
      rethrow;
    }
  }
} 