import 'package:injectable/injectable.dart';
import '../network/network_service.dart';
import '../logger/logger.dart';

@singleton
class PlantingPlanService {
  final NetworkService _network;
  final AppLogger _logger;

  PlantingPlanService(this._network, this._logger);

  Future<Map<String, dynamic>> createPlan({
    required String userId,
    required Map<String, dynamic> planData,
  }) async {
    try {
      final response = await _network.post(
        '/agriculture/plans',
        {
          'user_id': userId,
          ...planData,
        },
      );
      return response;
    } catch (e, stack) {
      _logger.error('Error creating planting plan', e, stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getPlanDetails(String planId) async {
    try {
      final response = await _network.get('/agriculture/plans/$planId');
      return response;
    } catch (e, stack) {
      _logger.error('Error getting plan details', e, stack);
      rethrow;
    }
  }

  Future<void> updatePlanProgress(
    String planId,
    Map<String, dynamic> progress,
  ) async {
    try {
      await _network.post(
        '/agriculture/plans/$planId/progress',
        progress,
      );
    } catch (e, stack) {
      _logger.error('Error updating plan progress', e, stack);
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getScheduledTasks(
    String planId, {
    DateTime? start,
    DateTime? end,
  }) async {
    try {
      final response = await _network.get(
        '/agriculture/plans/$planId/tasks',
        params: {
          if (start != null) 'start': start.toIso8601String(),
          if (end != null) 'end': end.toIso8601String(),
        },
      );
      return List<Map<String, dynamic>>.from(response['tasks']);
    } catch (e, stack) {
      _logger.error('Error getting scheduled tasks', e, stack);
      rethrow;
    }
  }

  Future<void> setTaskReminders(
    String planId,
    List<Map<String, dynamic>> reminders,
  ) async {
    try {
      await _network.post(
        '/agriculture/plans/$planId/reminders',
        {'reminders': reminders},
      );
    } catch (e, stack) {
      _logger.error('Error setting task reminders', e, stack);
      rethrow;
    }
  }
} 