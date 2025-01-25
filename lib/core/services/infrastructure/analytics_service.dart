abstract class AnalyticsService {
  Future<void> trackEvent(String eventName, Map<String, dynamic> parameters);
} 