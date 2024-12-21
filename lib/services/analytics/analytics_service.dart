import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:get/get.dart';

class AnalyticsService extends GetxService {
  final FirebaseAnalytics _analytics;
  
  AnalyticsService() : _analytics = FirebaseAnalytics.instance;

  Future<void> logEvent({
    required String name,
    Map<String, dynamic>? parameters,
  }) async {
    await _analytics.logEvent(
      name: name,
      parameters: parameters,
    );
  }

  Future<void> setUserProperties({
    required String userId,
    String? userRole,
    String? userPlan,
  }) async {
    await _analytics.setUserId(id: userId);
    
    if (userRole != null) {
      await _analytics.setUserProperty(
        name: 'user_role',
        value: userRole,
      );
    }
    
    if (userPlan != null) {
      await _analytics.setUserProperty(
        name: 'user_plan',
        value: userPlan,
      );
    }
  }

  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
  }) async {
    await _analytics.logScreenView(
      screenName: screenName,
      screenClass: screenClass,
    );
  }

  Future<void> logChatMessage({
    required String chatId,
    required String messageType,
    required bool isFromUser,
  }) async {
    await logEvent(
      name: 'chat_message',
      parameters: {
        'chat_id': chatId,
        'message_type': messageType,
        'is_from_user': isFromUser,
      },
    );
  }

  Future<void> logHealthAnalysis({
    required String analysisType,
    required bool hasWarnings,
  }) async {
    await logEvent(
      name: 'health_analysis',
      parameters: {
        'analysis_type': analysisType,
        'has_warnings': hasWarnings,
      },
    );
  }
} 