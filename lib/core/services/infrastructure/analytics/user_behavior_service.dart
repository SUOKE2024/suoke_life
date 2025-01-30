import '../logger/logger.dart';
import 'analytics_processor.dart';
import '../storage/local_storage.dart';

@singleton
class UserBehaviorService {
  final AnalyticsProcessor _processor;
  final LocalStorage _storage;
  final AppLogger _logger;

  UserBehaviorService(this._processor, this._storage, this._logger);

  Future<void> trackPageView(String pageName, {Map<String, dynamic>? params}) async {
    try {
      await _processor.processUserBehavior({
        'type': 'page_view',
        'page_name': pageName,
        'params': params,
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e, stack) {
      _logger.error('Error tracking page view', e, stack);
    }
  }

  Future<void> trackAction(
    String action,
    String category, {
    Map<String, dynamic>? data,
  }) async {
    try {
      await _processor.processUserBehavior({
        'type': 'user_action',
        'action': action,
        'category': category,
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e, stack) {
      _logger.error('Error tracking user action', e, stack);
    }
  }

  Future<void> trackFeatureUsage(String featureId, {
    Duration? duration,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      await _processor.processUserBehavior({
        'type': 'feature_usage',
        'feature_id': featureId,
        'duration': duration?.inSeconds,
        'metadata': metadata,
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e, stack) {
      _logger.error('Error tracking feature usage', e, stack);
    }
  }

  Future<void> trackError(
    String error,
    String source, {
    Map<String, dynamic>? context,
  }) async {
    try {
      await _processor.processUserBehavior({
        'type': 'error',
        'error': error,
        'source': source,
        'context': context,
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e, stack) {
      _logger.error('Error tracking error event', e, stack);
    }
  }
} 