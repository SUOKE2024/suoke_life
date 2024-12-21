import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:in_app_purchase_android/in_app_purchase_android.dart';
import 'package:in_app_purchase_storekit/in_app_purchase_storekit.dart';
import 'package:shared_preferences.dart';

enum SubscriptionPlan {
  basic,     // 免费版
  pro,       // 专业版
  premium    // 会员版
}

enum BillingPeriod {
  monthly,
  yearly
}

enum SubscriptionStatus {
  active,
  expired,
  pending,
  error,
  canceled
}

class SubscriptionError {
  final String code;
  final String message;
  final dynamic details;

  SubscriptionError(this.code, this.message, [this.details]);
}

class SubscriptionFeatures {
  final int dailyAIQuota;        // AI对话次数限制
  final bool videoConsultation;  // 视频会诊
  final bool expertMatching;     // 专家匹配
  final bool customService;      // 定制服务

  const SubscriptionFeatures({
    required this.dailyAIQuota,
    required this.videoConsultation,
    required this.expertMatching,
    required this.customService,
  });
}

class SubscriptionService extends GetxService {
  static const String _kProMonthlyId = 'pro_subscription_monthly';
  static const String _kProYearlyId = 'pro_subscription_yearly';
  static const String _kPremiumMonthlyId = 'premium_subscription_monthly';
  static const String _kPremiumYearlyId = 'premium_subscription_yearly';
  
  final InAppPurchase _inAppPurchase = InAppPurchase.instance;
  StreamSubscription<List<PurchaseDetails>>? _subscription;
  List<ProductDetails> _products = [];
  SubscriptionPlan _currentPlan = SubscriptionPlan.basic;
  DateTime? _expiryDate;
  bool _isLoading = true;
  SharedPreferences? _prefs;
  int _usedQuota = 0;
  SubscriptionStatus _status = SubscriptionStatus.active;
  SubscriptionError? _lastError;
  Timer? _autoRenewalCheckTimer;
  final _statusController = StreamController<SubscriptionStatus>.broadcast();

  static const Map<SubscriptionPlan, SubscriptionFeatures> planFeatures = {
    SubscriptionPlan.basic: SubscriptionFeatures(
      dailyAIQuota: 10,
      videoConsultation: false,
      expertMatching: false,
      customService: false,
    ),
    SubscriptionPlan.pro: SubscriptionFeatures(
      dailyAIQuota: 100,
      videoConsultation: true,
      expertMatching: true,
      customService: false,
    ),
    SubscriptionPlan.premium: SubscriptionFeatures(
      dailyAIQuota: -1,
      videoConsultation: true,
      expertMatching: true,
      customService: true,
    ),
  };

  static const Map<SubscriptionPlan, Map<String, dynamic>> _planConfig = {
    SubscriptionPlan.basic: {
      'price': 0,
      'name': '基础版',
      'description': '适合个人用户的基础AI助手功能',
      'features': {
        'max_sessions': 1,
        'max_messages_per_day': 50,
        'max_tokens': 1000,
        // ... 其他特性
      },
    },
    // ... 其他计划
  };

  SubscriptionService() {
    _init();
  }

  Future<void> _init() async {
    try {
      _prefs = await SharedPreferences.getInstance();
      await _loadSavedState();
      
      final bool available = await _inAppPurchase.isAvailable();
      if (!available) {
        _setError('STORE_UNAVAILABLE', '应用内购买服务不可用');
        _isLoading = false;
        update();
        return;
      }

      if (Platform.isIOS) {
        final InAppPurchaseStoreKitPlatformAddition iosPlatformAddition =
            _inAppPurchase.getPlatformAddition<InAppPurchaseStoreKitPlatformAddition>();
        await iosPlatformAddition.setDelegate(null);
      }

      _subscription = _inAppPurchase.purchaseStream.listen(
        _handlePurchaseUpdate,
        onDone: () => _subscription?.cancel(),
        onError: (error) => _setError('PURCHASE_STREAM_ERROR', '订阅监听错误', error),
      );

      await _loadProducts();
      await _checkSubscriptionStatus();
      _startAutoRenewalCheck();
    } catch (e) {
      _setError('INIT_ERROR', '初始化失败', e);
      _isLoading = false;
      update();
    }
  }

  void _startAutoRenewalCheck() {
    _autoRenewalCheckTimer?.cancel();
    _autoRenewalCheckTimer = Timer.periodic(
      const Duration(hours: 1),
      (_) => _checkSubscriptionStatus(),
    );
  }

  void _setError(String code, String message, [dynamic details]) {
    _lastError = SubscriptionError(code, message, details);
    _status = SubscriptionStatus.error;
    _statusController.add(_status);
    update();
  }

  Future<void> _loadSavedState() async {
    try {
      final String? planStr = _prefs?.getString('currentPlan');
      if (planStr != null) {
        _currentPlan = SubscriptionPlan.values.firstWhere(
          (e) => e.toString() == planStr,
          orElse: () => SubscriptionPlan.basic,
        );
      }

      final String? expiryStr = _prefs?.getString('expiryDate');
      if (expiryStr != null) {
        _expiryDate = DateTime.tryParse(expiryStr);
      }

      final String? statusStr = _prefs?.getString('subscriptionStatus');
      if (statusStr != null) {
        _status = SubscriptionStatus.values.firstWhere(
          (e) => e.toString() == statusStr,
          orElse: () => SubscriptionStatus.active,
        );
      }

      _usedQuota = _prefs?.getInt('dailyQuota_${DateTime.now().toIso8601String().split('T')[0]}') ?? 0;
    } catch (e) {
      _setError('LOAD_STATE_ERROR', '加载保存的状态失败', e);
    }
  }

  Future<void> _saveState() async {
    try {
      await _prefs?.setString('currentPlan', _currentPlan.toString());
      await _prefs?.setString('subscriptionStatus', _status.toString());
      if (_expiryDate != null) {
        await _prefs?.setString('expiryDate', _expiryDate!.toIso8601String());
      }
    } catch (e) {
      _setError('SAVE_STATE_ERROR', '保存状态失败', e);
    }
  }

  Future<void> _checkSubscriptionStatus() async {
    try {
      if (_expiryDate != null && DateTime.now().isAfter(_expiryDate!)) {
        _currentPlan = SubscriptionPlan.basic;
        _expiryDate = null;
        _status = SubscriptionStatus.expired;
        await _saveState();
        _statusController.add(_status);
        update();
      }
    } catch (e) {
      _setError('CHECK_STATUS_ERROR', '检查订阅状态失败', e);
    }
  }

  Future<void> _loadProducts() async {
    try {
      final Set<String> ids = <String>{
        _kProMonthlyId,
        _kProYearlyId,
        _kPremiumMonthlyId,
        _kPremiumYearlyId,
      };

      final ProductDetailsResponse response = 
          await _inAppPurchase.queryProductDetails(ids);

      if (response.notFoundIDs.isNotEmpty) {
        print('未找到的产品ID: ${response.notFoundIDs}');
      }

      if (response.error != null) {
        _setError('LOAD_PRODUCTS_ERROR', '加载产品信息失败', response.error);
        return;
      }

      _products = response.productDetails;
      _isLoading = false;
      update();
    } catch (e) {
      _setError('LOAD_PRODUCTS_ERROR', '加载产品信息失败', e);
    }
  }

  Future<void> _handlePurchaseUpdate(List<PurchaseDetails> purchaseDetailsList) async {
    for (final PurchaseDetails purchaseDetails in purchaseDetailsList) {
      if (purchaseDetails.status == PurchaseStatus.pending) {
        _status = SubscriptionStatus.pending;
        _statusController.add(_status);
        update();
      } else if (purchaseDetails.status == PurchaseStatus.error) {
        _setError('PURCHASE_ERROR', '购买失败', purchaseDetails.error);
      } else if (purchaseDetails.status == PurchaseStatus.purchased ||
                 purchaseDetails.status == PurchaseStatus.restored) {
        await _verifyPurchase(purchaseDetails);
      } else if (purchaseDetails.status == PurchaseStatus.canceled) {
        _status = SubscriptionStatus.canceled;
        _statusController.add(_status);
        update();
      }

      if (purchaseDetails.pendingCompletePurchase) {
        await _inAppPurchase.completePurchase(purchaseDetails);
      }
    }
  }

  Future<void> _verifyPurchase(PurchaseDetails purchaseDetails) async {
    try {
      // TODO: 实现服务器端验证
      final bool isYearly = purchaseDetails.productID.contains('yearly');
      final duration = isYearly ? const Duration(days: 365) : const Duration(days: 30);
      
      if (purchaseDetails.productID.contains('pro')) {
        _currentPlan = SubscriptionPlan.pro;
      } else if (purchaseDetails.productID.contains('premium')) {
        _currentPlan = SubscriptionPlan.premium;
      }

      _expiryDate = DateTime.now().add(duration);
      _status = SubscriptionStatus.active;
      await _saveState();
      _statusController.add(_status);
      update();
    } catch (e) {
      _setError('VERIFY_PURCHASE_ERROR', '验证购买失败', e);
    }
  }

  Future<bool> incrementQuota() async {
    try {
      final String today = DateTime.now().toIso8601String().split('T')[0];
      final int currentQuota = _usedQuota;
      final int maxQuota = currentFeatures.dailyAIQuota;

      if (maxQuota == -1 || currentQuota < maxQuota) {
        _usedQuota++;
        await _prefs?.setInt('dailyQuota_$today', _usedQuota);
        return true;
      }
      return false;
    } catch (e) {
      _setError('INCREMENT_QUOTA_ERROR', '增加使用配额失败', e);
      return false;
    }
  }

  Future<void> resetDailyQuota() async {
    try {
      _usedQuota = 0;
      final String today = DateTime.now().toIso8601String().split('T')[0];
      await _prefs?.setInt('dailyQuota_$today', 0);
    } catch (e) {
      _setError('RESET_QUOTA_ERROR', '重置使用配额失败', e);
    }
  }

  Future<void> subscribe(SubscriptionPlan plan, {BillingPeriod period = BillingPeriod.monthly}) async {
    if (_isLoading) return;

    try {
      final String productId;
      switch (plan) {
        case SubscriptionPlan.pro:
          productId = period == BillingPeriod.monthly ? _kProMonthlyId : _kProYearlyId;
          break;
        case SubscriptionPlan.premium:
          productId = period == BillingPeriod.monthly ? _kPremiumMonthlyId : _kPremiumYearlyId;
          break;
        default:
          return;
      }

      final ProductDetails? product = 
          _products.firstWhere((p) => p.id == productId);

      if (product == null) {
        throw Exception('未找到订阅产品');
      }

      final PurchaseParam purchaseParam = PurchaseParam(
        productDetails: product,
        applicationUserName: null,
      );

      await _inAppPurchase.buyNonConsumable(purchaseParam: purchaseParam);
    } catch (e) {
      _setError('SUBSCRIBE_ERROR', '订阅失败', e);
      rethrow;
    }
  }

  Future<void> restorePurchases() async {
    try {
      await _inAppPurchase.restorePurchases();
    } catch (e) {
      _setError('RESTORE_PURCHASES_ERROR', '恢复购买失败', e);
    }
  }

  bool canAccessFeature(String featureKey) {
    if (_status != SubscriptionStatus.active) {
      return false;
    }

    if (_expiryDate != null && DateTime.now().isAfter(_expiryDate!)) {
      _currentPlan = SubscriptionPlan.basic;
      _expiryDate = null;
      _status = SubscriptionStatus.expired;
      _saveState();
      _statusController.add(_status);
      update();
      return false;
    }

    final features = currentFeatures;
    switch (featureKey) {
      case 'videoConsultation':
        return features.videoConsultation;
      case 'expertMatching':
        return features.expertMatching;
      case 'customService':
        return features.customService;
      default:
        return false;
    }
  }

  Future<void> clearError() async {
    _lastError = null;
    update();
  }

  // Getters
  SubscriptionPlan get currentPlan => _currentPlan;
  SubscriptionFeatures get currentFeatures => planFeatures[_currentPlan]!;
  List<ProductDetails> get products => _products;
  bool get isLoading => _isLoading;
  DateTime? get expiryDate => _expiryDate;
  int get remainingQuota => currentFeatures.dailyAIQuota == -1 ? 
      -1 : currentFeatures.dailyAIQuota - _usedQuota;
  SubscriptionStatus get status => _status;
  SubscriptionError? get lastError => _lastError;
  Stream<SubscriptionStatus> get statusStream => _statusController.stream;

  @override
  void dispose() {
    _subscription?.cancel();
    _autoRenewalCheckTimer?.cancel();
    _statusController.close();
    super.dispose();
  }
} 