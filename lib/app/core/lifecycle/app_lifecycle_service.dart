import 'package:injectable/injectable.dart';
import 'package:flutter/widgets.dart';
import '../logger/logger.dart';
import '../analytics/analytics_service.dart';

@singleton
class AppLifecycleService with WidgetsBindingObserver {
  final AppLogger _logger;
  final AnalyticsService _analytics;
  bool _isInitialized = false;

  AppLifecycleService(this._logger, this._analytics);

  void init() {
    if (_isInitialized) return;
    WidgetsBinding.instance.addObserver(this);
    _isInitialized = true;
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    _logger.info('App lifecycle state changed: $state');
    
    switch (state) {
      case AppLifecycleState.resumed:
        _onResumed();
        break;
      case AppLifecycleState.inactive:
        _onInactive();
        break;
      case AppLifecycleState.paused:
        _onPaused();
        break;
      case AppLifecycleState.detached:
        _onDetached();
        break;
      case AppLifecycleState.hidden:
        _onHidden();
        break;
    }
  }

  void _onResumed() {
    _analytics.trackEvent('app_resumed', {
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void _onInactive() {
    _analytics.trackEvent('app_inactive', {
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void _onPaused() {
    _analytics.trackEvent('app_paused', {
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void _onDetached() {
    _analytics.trackEvent('app_detached', {
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void _onHidden() {
    _analytics.trackEvent('app_hidden', {
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void dispose() {
    if (_isInitialized) {
      WidgetsBinding.instance.removeObserver(this);
      _isInitialized = false;
    }
  }
} 