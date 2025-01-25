import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'analytics_manager.dart';

class AnalyticsRouteObserver extends GetObserver {
  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPush(route, previousRoute);
    if (route.settings.name != null) {
      AnalyticsManager.instance.trackEvent('screen_view', parameters: {
        'screen_name': route.settings.name!,
        'previous_screen': previousRoute?.settings.name
      });
    }
  }
} 