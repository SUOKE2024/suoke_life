class QuotaManagerService extends GetxService {
  final SubscriptionService _subscriptionService;
  final DataStorageService _storageService;
  final EventTrackingService _eventTracking;
  
  // 配额缓存
  final Map<String, int> _dailyUsage = {};
  final Map<String, int> _monthlyUsage = {};
  
  // 配额限制
  static const Map<SubscriptionPlan, Map<String, int>> _quotaLimits = {
    SubscriptionPlan.basic: {
      'daily': 50,
      'monthly': 1000,
      'concurrent': 1,
    },
    SubscriptionPlan.pro: {
      'daily': 200,
      'monthly': 5000,
      'concurrent': 3,
    },
    SubscriptionPlan.premium: {
      'daily': -1,  // 无限制
      'monthly': -1,
      'concurrent': 10,
    },
  };
  
  QuotaManagerService({
    required SubscriptionService subscriptionService,
    required DataStorageService storageService,
    required EventTrackingService eventTracking,
  })  : _subscriptionService = subscriptionService,
        _storageService = storageService,
        _eventTracking = eventTracking {
    _startDailyReset();
    _startMonthlyReset();
  }

  Future<bool> checkQuota(String userId, String assistantName) async {
    try {
      final plan = _subscriptionService.currentPlan;
      final limits = _quotaLimits[plan]!;
      
      // 获取使用量
      final dailyKey = _getDailyKey(userId);
      final monthlyKey = _getMonthlyKey(userId);
      
      final dailyUsage = _dailyUsage[dailyKey] ?? 0;
      final monthlyUsage = _monthlyUsage[monthlyKey] ?? 0;
      
      // 检查限制
      if (limits['daily'] != -1 && dailyUsage >= limits['daily']) {
        await _notifyQuotaExceeded(userId, 'daily');
        return false;
      }
      
      if (limits['monthly'] != -1 && monthlyUsage >= limits['monthly']) {
        await _notifyQuotaExceeded(userId, 'monthly');
        return false;
      }
      
      return true;
    } catch (e) {
      debugPrint('配额检查失败: $e');
      return false;
    }
  }

  Future<void> incrementUsage(String userId, String assistantName) async {
    try {
      final dailyKey = _getDailyKey(userId);
      final monthlyKey = _getMonthlyKey(userId);
      
      // 增加使用量
      _dailyUsage[dailyKey] = (_dailyUsage[dailyKey] ?? 0) + 1;
      _monthlyUsage[monthlyKey] = (_monthlyUsage[monthlyKey] ?? 0) + 1;
      
      // 保存使用记录
      await _saveUsageRecord(userId, assistantName);
      
      // 检查是否接近限制
      await _checkQuotaWarning(userId);
    } catch (e) {
      debugPrint('增加使用量失败: $e');
    }
  }

  Future<Map<String, dynamic>> getQuotaStatus(String userId) async {
    try {
      final plan = _subscriptionService.currentPlan;
      final limits = _quotaLimits[plan]!;
      
      final dailyKey = _getDailyKey(userId);
      final monthlyKey = _getMonthlyKey(userId);
      
      final dailyUsage = _dailyUsage[dailyKey] ?? 0;
      final monthlyUsage = _monthlyUsage[monthlyKey] ?? 0;
      
      return {
        'plan': plan.toString(),
        'daily': {
          'used': dailyUsage,
          'limit': limits['daily'],
          'remaining': limits['daily'] == -1 ? -1 : limits['daily'] - dailyUsage,
        },
        'monthly': {
          'used': monthlyUsage,
          'limit': limits['monthly'],
          'remaining': limits['monthly'] == -1 ? -1 : limits['monthly'] - monthlyUsage,
        },
        'concurrent': {
          'limit': limits['concurrent'],
        },
      };
    } catch (e) {
      throw AIException(
        '获取配额状态失败',
        code: 'GET_QUOTA_STATUS_ERROR',
        details: e,
      );
    }
  }

  Future<void> _saveUsageRecord(String userId, String assistantName) async {
    try {
      final record = {
        'user_id': userId,
        'assistant_name': assistantName,
        'timestamp': DateTime.now().toIso8601String(),
        'plan': _subscriptionService.currentPlan.toString(),
      };
      
      await _storageService.saveQuotaUsage(record);
    } catch (e) {
      debugPrint('保存使用记录失败: $e');
    }
  }

  Future<void> _checkQuotaWarning(String userId) async {
    try {
      final status = await getQuotaStatus(userId);
      final dailyRemaining = status['daily']['remaining'];
      final monthlyRemaining = status['monthly']['remaining'];
      
      // 检查是否需要发出警告
      if (dailyRemaining != -1 && dailyRemaining < 10) {
        await _notifyQuotaWarning(userId, 'daily', dailyRemaining);
      }
      
      if (monthlyRemaining != -1 && monthlyRemaining < 100) {
        await _notifyQuotaWarning(userId, 'monthly', monthlyRemaining);
      }
    } catch (e) {
      debugPrint('检查配额警告失败: $e');
    }
  }

  Future<void> _notifyQuotaWarning(
    String userId,
    String type,
    int remaining,
  ) async {
    try {
      await _eventTracking.trackEvent(AIEvent(
        id: 'quota_warning_${DateTime.now().millisecondsSinceEpoch}',
        userId: userId,
        assistantName: 'system',
        type: AIEventType.quotaWarning,
        data: {
          'type': type,
          'remaining': remaining,
          'timestamp': DateTime.now().toIso8601String(),
        },
      ));
    } catch (e) {
      debugPrint('配额警告通知失败: $e');
    }
  }

  Future<void> _notifyQuotaExceeded(String userId, String type) async {
    try {
      await _eventTracking.trackEvent(AIEvent(
        id: 'quota_exceeded_${DateTime.now().millisecondsSinceEpoch}',
        userId: userId,
        assistantName: 'system',
        type: AIEventType.quotaExceeded,
        data: {
          'type': type,
          'timestamp': DateTime.now().toIso8601String(),
        },
      ));
    } catch (e) {
      debugPrint('配额超限通知失败: $e');
    }
  }

  String _getDailyKey(String userId) =>
    '${userId}_${DateTime.now().toIso8601String().split('T')[0]}';

  String _getMonthlyKey(String userId) =>
    '${userId}_${DateTime.now().toIso8601String().substring(0, 7)}';

  void _startDailyReset() {
    Timer.periodic(Duration(hours: 1), (_) {
      final now = DateTime.now();
      if (now.hour == 0) {  // 每天0点重置
        _dailyUsage.clear();
      }
    });
  }

  void _startMonthlyReset() {
    Timer.periodic(Duration(hours: 1), (_) {
      final now = DateTime.now();
      if (now.day == 1 && now.hour == 0) {  // 每月1日0点重置
        _monthlyUsage.clear();
      }
    });
  }

  @override
  void onClose() {
    // 保存使���记录
    _saveAllUsageRecords();
    super.onClose();
  }

  Future<void> _saveAllUsageRecords() async {
    try {
      final records = {
        'daily': _dailyUsage,
        'monthly': _monthlyUsage,
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      await _storageService.saveQuotaSnapshot(records);
    } catch (e) {
      debugPrint('保存配额快照失败: $e');
    }
  }
} 