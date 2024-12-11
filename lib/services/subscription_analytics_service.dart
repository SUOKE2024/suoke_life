import 'dart:async';
import 'package:shared_preferences.dart';
import 'subscription_service.dart';

class SubscriptionEvent {
  final String type;
  final String planId;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  SubscriptionEvent({
    required this.type,
    required this.planId,
    required this.timestamp,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'type': type,
    'planId': planId,
    'timestamp': timestamp.toIso8601String(),
    'metadata': metadata,
  };

  factory SubscriptionEvent.fromJson(Map<String, dynamic> json) {
    return SubscriptionEvent(
      type: json['type'],
      planId: json['planId'],
      timestamp: DateTime.parse(json['timestamp']),
      metadata: json['metadata'],
    );
  }
}

class SubscriptionAnalytics {
  final int totalSubscriptions;
  final int activeSubscriptions;
  final int monthlySubscriptions;
  final int yearlySubscriptions;
  final double conversionRate;
  final Map<String, int> planDistribution;
  final Map<String, double> revenueByPlan;
  final List<SubscriptionEvent> recentEvents;

  SubscriptionAnalytics({
    required this.totalSubscriptions,
    required this.activeSubscriptions,
    required this.monthlySubscriptions,
    required this.yearlySubscriptions,
    required this.conversionRate,
    required this.planDistribution,
    required this.revenueByPlan,
    required this.recentEvents,
  });
}

class SubscriptionAnalyticsService {
  static const String _eventsKey = 'subscription_events';
  final SharedPreferences _prefs;
  final SubscriptionService _subscriptionService;
  final _analyticsController = StreamController<SubscriptionAnalytics>.broadcast();
  List<SubscriptionEvent> _events = [];
  Timer? _analysisTimer;

  SubscriptionAnalyticsService(this._prefs, this._subscriptionService) {
    _init();
  }

  Future<void> _init() async {
    await _loadEvents();
    _subscribeToEvents();
    _startPeriodicAnalysis();
  }

  Future<void> _loadEvents() async {
    final String? eventsJson = _prefs.getString(_eventsKey);
    if (eventsJson != null) {
      final List<dynamic> eventsList = json.decode(eventsJson);
      _events = eventsList.map((e) => SubscriptionEvent.fromJson(e)).toList();
    }
  }

  void _subscribeToEvents() {
    _subscriptionService.statusStream.listen((status) {
      if (status == SubscriptionStatus.active) {
        _trackEvent(
          'subscription_activated',
          _subscriptionService.currentPlan.toString(),
        );
      } else if (status == SubscriptionStatus.expired) {
        _trackEvent(
          'subscription_expired',
          _subscriptionService.currentPlan.toString(),
        );
      }
    });
  }

  void _startPeriodicAnalysis() {
    _analysisTimer?.cancel();
    _analysisTimer = Timer.periodic(
      const Duration(hours: 1),
      (_) => _performAnalysis(),
    );
    _performAnalysis();
  }

  Future<void> _trackEvent(String type, String planId, [Map<String, dynamic>? metadata]) async {
    final event = SubscriptionEvent(
      type: type,
      planId: planId,
      timestamp: DateTime.now(),
      metadata: metadata,
    );
    _events.add(event);
    await _saveEvents();
    _performAnalysis();
  }

  Future<void> _saveEvents() async {
    final eventsJson = json.encode(_events.map((e) => e.toJson()).toList());
    await _prefs.setString(_eventsKey, eventsJson);
  }

  void _performAnalysis() {
    final now = DateTime.now();
    final thirtyDaysAgo = now.subtract(const Duration(days: 30));
    
    // 过滤最近30天的事件
    final recentEvents = _events.where((e) => e.timestamp.isAfter(thirtyDaysAgo)).toList();
    
    // 计算各种统计数据
    final activations = recentEvents.where((e) => e.type == 'subscription_activated').length;
    final expirations = recentEvents.where((e) => e.type == 'subscription_expired').length;
    final activeSubscriptions = activations - expirations;
    
    // 计算月度和年度订阅数量
    final monthlySubscriptions = recentEvents.where((e) => 
      e.type == 'subscription_activated' && e.planId.contains('monthly')
    ).length;
    final yearlySubscriptions = recentEvents.where((e) => 
      e.type == 'subscription_activated' && e.planId.contains('yearly')
    ).length;
    
    // 计算转化率
    final trials = recentEvents.where((e) => e.type == 'trial_started').length;
    final conversions = recentEvents.where((e) => 
      e.type == 'subscription_activated' && e.metadata?['from_trial'] == true
    ).length;
    final conversionRate = trials > 0 ? conversions / trials : 0.0;
    
    // 计算计划分布
    final planDistribution = <String, int>{};
    for (var plan in SubscriptionPlan.values) {
      planDistribution[plan.toString()] = recentEvents.where((e) => 
        e.type == 'subscription_activated' && e.planId.contains(plan.toString().split('.').last)
      ).length;
    }
    
    // 计算每个计划的收入
    final revenueByPlan = <String, double>{};
    for (var plan in SubscriptionPlan.values) {
      final planEvents = recentEvents.where((e) => 
        e.type == 'subscription_activated' && e.planId.contains(plan.toString().split('.').last)
      );
      double revenue = 0;
      for (var event in planEvents) {
        revenue += event.metadata?['price'] ?? 0;
      }
      revenueByPlan[plan.toString()] = revenue;
    }

    final analytics = SubscriptionAnalytics(
      totalSubscriptions: activations,
      activeSubscriptions: activeSubscriptions,
      monthlySubscriptions: monthlySubscriptions,
      yearlySubscriptions: yearlySubscriptions,
      conversionRate: conversionRate,
      planDistribution: planDistribution,
      revenueByPlan: revenueByPlan,
      recentEvents: recentEvents,
    );

    _analyticsController.add(analytics);
  }

  Future<void> trackSubscriptionStarted(String planId, double price) async {
    await _trackEvent(
      'subscription_activated',
      planId,
      {'price': price},
    );
  }

  Future<void> trackSubscriptionRenewed(String planId, double price) async {
    await _trackEvent(
      'subscription_renewed',
      planId,
      {'price': price},
    );
  }

  Future<void> trackSubscriptionCanceled(String planId) async {
    await _trackEvent(
      'subscription_canceled',
      planId,
    );
  }

  Future<void> trackTrialStarted(String planId) async {
    await _trackEvent(
      'trial_started',
      planId,
    );
  }

  Future<void> trackTrialConverted(String planId, double price) async {
    await _trackEvent(
      'subscription_activated',
      planId,
      {
        'from_trial': true,
        'price': price,
      },
    );
  }

  Stream<SubscriptionAnalytics> get analyticsStream => _analyticsController.stream;

  void dispose() {
    _analysisTimer?.cancel();
    _analyticsController.close();
  }
} 