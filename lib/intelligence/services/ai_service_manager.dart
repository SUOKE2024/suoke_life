class AIServiceManager extends GetxService {
  final SubscriptionService _subscriptionService;
  final AIAssistantService _assistantService;
  
  AIServiceManager({
    required SubscriptionService subscriptionService,
    required AIAssistantService assistantService,
  }) : _subscriptionService = subscriptionService,
       _assistantService = assistantService;

  Future<String> chat(String assistantName, String message) async {
    // 检查订阅状态和配额
    if (!await _checkAccess(assistantName)) {
      throw AIAccessException('需要升级订阅以使用此功能');
    }
    
    // 增加使用配额
    if (!await _subscriptionService.incrementQuota()) {
      throw AIQuotaException('今日对话次数已达上限');
    }
    
    // 获取当前访问级别的特性
    final access = _getFeatureAccess();
    
    // 调用助手服务
    return await _assistantService.chat(
      assistantName, 
      message,
      access: access,
    );
  }

  AIFeatureAccess _getFeatureAccess() {
    final plan = _subscriptionService.currentPlan;
    switch (plan) {
      case SubscriptionPlan.premium:
        return const AIFeatureAccess(
          dailyQuota: -1,
          advancedAnalysis: true,
          customPrompts: true,
          priorityResponse: true,
        );
      case SubscriptionPlan.pro:
        return const AIFeatureAccess(
          dailyQuota: 100,
          advancedAnalysis: true,
          customPrompts: true,
          priorityResponse: false,
        );
      default:
        return const AIFeatureAccess(
          dailyQuota: 10,
          advancedAnalysis: false,
          customPrompts: false,
          priorityResponse: false,
        );
    }
  }

  Future<bool> _checkAccess(String assistantName) async {
    final assistant = _assistantService.getAssistant(assistantName);
    final currentLevel = _getCurrentLevel();
    return _hasRequiredLevel(currentLevel, assistant.minimumLevel);
  }

  AIAssistantLevel _getCurrentLevel() {
    switch (_subscriptionService.currentPlan) {
      case SubscriptionPlan.premium:
        return AIAssistantLevel.premium;
      case SubscriptionPlan.pro:
        return AIAssistantLevel.pro;
      default:
        return AIAssistantLevel.basic;
    }
  }

  bool _hasRequiredLevel(
    AIAssistantLevel currentLevel, 
    AIAssistantLevel requiredLevel
  ) {
    return currentLevel.index >= requiredLevel.index;
  }
} 