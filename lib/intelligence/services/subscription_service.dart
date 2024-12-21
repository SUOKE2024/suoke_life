class SubscriptionService extends GetxService {
  final StorageService _storageService;
  final EventTrackingService _eventTracking;
  final SecurityManagerService _securityManager;
  
  // 订阅计划配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _planConfig = {
    SubscriptionPlan.basic: {
      'price': 0,
      'name': '基础版',
      'description': '适合个人用户的基础AI助手功能',
      'features': {
        'max_sessions': 1,
        'max_messages_per_day': 50,
        'max_tokens': 1000,
        'priority_response': false,
        'advanced_analysis': false,
        'custom_prompts': false,
      },
    },
    SubscriptionPlan.pro: {
      'price': 29.99,
      'name': '专业版',
      'description': '适合专业用户的进阶AI助手功能',
      'features': {
        'max_sessions': 3,
        'max_messages_per_day': 200,
        'max_tokens': 4000,
        'priority_response': true,
        'advanced_analysis': true,
        'custom_prompts': false,
      },
    },
    SubscriptionPlan.premium: {
      'price': 99.99,
      'name': '尊享版',
      'description': '适合企业用户的全功能AI助手',
      'features': {
        'max_sessions': -1,  // 无限制
        'max_messages_per_day': -1,
        'max_tokens': -1,
        'priority_response': true,
        'advanced_analysis': true,
        'custom_prompts': true,
      },
    },
  };
  
  // 当前订阅状态
  final Rx<SubscriptionPlan> _currentPlan = SubscriptionPlan.basic.obs;
  final Rx<DateTime?> _expiryDate = Rx<DateTime?>(null);
  final RxBool _autoRenew = false.obs;
  
  SubscriptionService({
    required StorageService storageService,
    required EventTrackingService eventTracking,
    required SecurityManagerService securityManager,
  })  : _storageService = storageService,
        _eventTracking = eventTracking,
        _securityManager = securityManager;

  @override
  Future<void> onInit() async {
    super.onInit();
    await _loadSubscriptionState();
  }

  Future<void> _loadSubscriptionState() async {
    try {
      final state = await _storageService.getSubscriptionState();
      if (state != null) {
        _currentPlan.value = state.plan;
        _expiryDate.value = state.expiryDate;
        _autoRenew.value = state.autoRenew;
      }
    } catch (e) {
      debugPrint('加载订阅状态失败: $e');
    }
  }

  Future<void> upgradePlan(
    SubscriptionPlan plan, {
    required String userId,
    required String paymentMethod,
    bool autoRenew = false,
  }) async {
    try {
      // 验证支付
      final paymentResult = await _processPayment(
        plan,
        userId,
        paymentMethod,
      );

      if (!paymentResult['success']) {
        throw AIException(
          '支付失败',
          code: 'PAYMENT_FAILED',
          details: paymentResult['error'],
        );
      }

      // 更新订阅状态
      final oldPlan = _currentPlan.value;
      _currentPlan.value = plan;
      _autoRenew.value = autoRenew;
      _expiryDate.value = DateTime.now().add(Duration(days: 30));

      // 保存状态
      await _saveSubscriptionState();

      // 记录事件
      await _trackSubscriptionEvent(
        'plan_upgraded',
        userId,
        oldPlan: oldPlan,
        newPlan: plan,
        paymentMethod: paymentMethod,
      );
    } catch (e) {
      throw AIException(
        '升级订阅失败',
        code: 'UPGRADE_FAILED',
        details: e,
      );
    }
  }

  Future<void> cancelSubscription(String userId) async {
    try {
      final oldPlan = _currentPlan.value;
      
      // 更新状态
      _currentPlan.value = SubscriptionPlan.basic;
      _autoRenew.value = false;
      
      // 保存状态
      await _saveSubscriptionState();

      // 记录事件
      await _trackSubscriptionEvent(
        'subscription_cancelled',
        userId,
        oldPlan: oldPlan,
        newPlan: SubscriptionPlan.basic,
      );
    } catch (e) {
      throw AIException(
        '取消订阅失败',
        code: 'CANCEL_FAILED',
        details: e,
      );
    }
  }

  Future<void> updateAutoRenew(
    bool enabled, {
    required String userId,
  }) async {
    try {
      _autoRenew.value = enabled;
      await _saveSubscriptionState();

      // 记录事件
      await _trackSubscriptionEvent(
        'auto_renew_updated',
        userId,
        metadata: {'enabled': enabled},
      );
    } catch (e) {
      throw AIException(
        '更新自动续订失败',
        code: 'UPDATE_AUTO_RENEW_FAILED',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> getSubscriptionDetails(String userId) async {
    final plan = _currentPlan.value;
    final config = _planConfig[plan]!;
    
    return {
      'plan': plan.toString(),
      'name': config['name'],
      'description': config['description'],
      'price': config['price'],
      'features': config['features'],
      'expiry_date': _expiryDate.value?.toIso8601String(),
      'auto_renew': _autoRenew.value,
    };
  }

  Future<Map<String, dynamic>> _processPayment(
    SubscriptionPlan plan,
    String userId,
    String paymentMethod,
  ) async {
    // TODO: 实现支付处理逻辑
    return {
      'success': true,
      'transaction_id': 'test_transaction',
    };
  }

  Future<void> _saveSubscriptionState() async {
    final state = SubscriptionState(
      plan: _currentPlan.value,
      expiryDate: _expiryDate.value,
      autoRenew: _autoRenew.value,
    );
    
    await _storageService.saveSubscriptionState(state);
  }

  Future<void> _trackSubscriptionEvent(
    String action,
    String userId, {
    SubscriptionPlan? oldPlan,
    SubscriptionPlan? newPlan,
    String? paymentMethod,
    Map<String, dynamic>? metadata,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'subscription_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      assistantName: 'system',
      type: AIEventType.subscription,
      data: {
        'action': action,
        'old_plan': oldPlan?.toString(),
        'new_plan': newPlan?.toString(),
        'payment_method': paymentMethod,
        'metadata': metadata,
      },
    ));
  }

  // Getters
  SubscriptionPlan get currentPlan => _currentPlan.value;
  DateTime? get expiryDate => _expiryDate.value;
  bool get autoRenew => _autoRenew.value;
  Map<String, dynamic> get currentFeatures => 
    _planConfig[_currentPlan.value]!['features'] as Map<String, dynamic>;
} 