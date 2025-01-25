import 'package:suoke_life/core/services/analytics_service.dart';

class AnalyticsServiceImpl implements AnalyticsService {
  @override
  Future<void> trackEvent(String eventName, Map<String, dynamic> parameters) async {
    // TODO: Implement analytics tracking logic
    print('Event tracked: $eventName, parameters: $parameters');
  }
} 