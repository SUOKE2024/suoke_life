enum AIAssistantLevel {
  basic,    // 基础版：有限的对话次数
  pro,      // 专业版：更多功能和对话次数
  premium   // 会员版：无限制使用
}

class AIFeatureAccess {
  final int dailyQuota;
  final bool advancedAnalysis;
  final bool customPrompts;
  final bool priorityResponse;
  
  const AIFeatureAccess({
    required this.dailyQuota,
    required this.advancedAnalysis,
    required this.customPrompts,
    required this.priorityResponse,
  });
} 