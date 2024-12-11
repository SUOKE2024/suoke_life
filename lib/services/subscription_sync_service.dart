import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'subscription_service.dart';
import 'subscription_analytics_service.dart';
import '../core/network/http_client.dart';
import '../core/error/app_error.dart';

class SubscriptionSyncService {
  final HttpClient _httpClient;
  final SubscriptionService _subscriptionService;
  final SubscriptionAnalyticsService _analyticsService;
  Timer? _syncTimer;
  bool _isSyncing = false;

  SubscriptionSyncService(
    this._httpClient,
    this._subscriptionService,
    this._analyticsService,
  ) {
    _init();
  }

  void _init() {
    // 每30分钟同步一次数据
    _syncTimer = Timer.periodic(
      const Duration(minutes: 30),
      (_) => syncData(),
    );
    
    // 监听订阅状态变化，立即同步
    _subscriptionService.statusStream.listen((_) {
      syncData();
    });
  }

  Future<void> syncData() async {
    if (_isSyncing) return;
    _isSyncing = true;

    try {
      // 同步订阅状态
      await _syncSubscriptionStatus();
      
      // 同步分析数据
      await _syncAnalyticsData();
      
      // 获取服务器端更新
      await _fetchServerUpdates();
    } catch (e) {
      print('同步失败: $e');
    } finally {
      _isSyncing = false;
    }
  }

  Future<void> _syncSubscriptionStatus() async {
    final status = {
      'plan': _subscriptionService.currentPlan.toString(),
      'expiryDate': _subscriptionService.expiryDate?.toIso8601String(),
      'status': _subscriptionService.status.toString(),
      'remainingQuota': _subscriptionService.remainingQuota,
    };

    try {
      final response = await _httpClient.post(
        '/api/subscription/sync',
        body: json.encode(status),
      );

      if (response.statusCode != 200) {
        throw AppError('SYNC_ERROR', '同步订阅状态失败');
      }
    } catch (e) {
      print('同步订阅状态失败: $e');
      rethrow;
    }
  }

  Future<void> _syncAnalyticsData() async {
    // 获取最近的分析数据
    final analyticsStream = _analyticsService.analyticsStream;
    final analytics = await analyticsStream.first;

    final data = {
      'totalSubscriptions': analytics.totalSubscriptions,
      'activeSubscriptions': analytics.activeSubscriptions,
      'monthlySubscriptions': analytics.monthlySubscriptions,
      'yearlySubscriptions': analytics.yearlySubscriptions,
      'conversionRate': analytics.conversionRate,
      'planDistribution': analytics.planDistribution,
      'revenueByPlan': analytics.revenueByPlan,
      'recentEvents': analytics.recentEvents.map((e) => e.toJson()).toList(),
    };

    try {
      final response = await _httpClient.post(
        '/api/subscription/analytics/sync',
        body: json.encode(data),
      );

      if (response.statusCode != 200) {
        throw AppError('SYNC_ERROR', '同步分析数据失败');
      }
    } catch (e) {
      print('同步分析数据失败: $e');
      rethrow;
    }
  }

  Future<void> _fetchServerUpdates() async {
    try {
      final response = await _httpClient.get('/api/subscription/updates');

      if (response.statusCode == 200) {
        final updates = json.decode(response.body);
        
        // 处理服务器端的更新
        if (updates['forceRefresh'] == true) {
          await _subscriptionService.checkSubscriptionStatus();
        }
        
        if (updates['quotaReset'] == true) {
          await _subscriptionService.resetDailyQuota();
        }
        
        // 处理价格更新
        if (updates['priceUpdates'] != null) {
          // TODO: 实现价格更新逻辑
        }
        
        // 处理功能更新
        if (updates['featureUpdates'] != null) {
          // TODO: 实现功能更新逻辑
        }
      }
    } catch (e) {
      print('获取服务器更新失败: $e');
      rethrow;
    }
  }

  Future<void> forceSyncNow() async {
    await syncData();
  }

  void dispose() {
    _syncTimer?.cancel();
  }
} 