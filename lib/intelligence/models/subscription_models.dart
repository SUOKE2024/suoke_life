enum SubscriptionPlan {
  basic,
  pro,
  premium,
}

class SubscriptionState {
  final SubscriptionPlan plan;
  final DateTime? expiryDate;
  final bool autoRenew;

  const SubscriptionState({
    required this.plan,
    this.expiryDate,
    this.autoRenew = false,
  });

  Map<String, dynamic> toMap() => {
    'plan': plan.toString(),
    'expiry_date': expiryDate?.toIso8601String(),
    'auto_renew': autoRenew,
  };

  factory SubscriptionState.fromMap(Map<String, dynamic> map) => SubscriptionState(
    plan: SubscriptionPlan.values.firstWhere(
      (e) => e.toString() == map['plan'],
      orElse: () => SubscriptionPlan.basic,
    ),
    expiryDate: map['expiry_date'] != null ? 
      DateTime.parse(map['expiry_date']) : null,
    autoRenew: map['auto_renew'] ?? false,
  );
}

class SubscriptionFeatures {
  final int maxSessions;
  final int maxMessagesPerDay;
  final int maxTokens;
  final bool priorityResponse;
  final bool advancedAnalysis;
  final bool customPrompts;

  const SubscriptionFeatures({
    required this.maxSessions,
    required this.maxMessagesPerDay,
    required this.maxTokens,
    required this.priorityResponse,
    required this.advancedAnalysis,
    required this.customPrompts,
  });

  Map<String, dynamic> toMap() => {
    'max_sessions': maxSessions,
    'max_messages_per_day': maxMessagesPerDay,
    'max_tokens': maxTokens,
    'priority_response': priorityResponse,
    'advanced_analysis': advancedAnalysis,
    'custom_prompts': customPrompts,
  };

  factory SubscriptionFeatures.fromMap(Map<String, dynamic> map) => SubscriptionFeatures(
    maxSessions: map['max_sessions'] ?? 1,
    maxMessagesPerDay: map['max_messages_per_day'] ?? 50,
    maxTokens: map['max_tokens'] ?? 1000,
    priorityResponse: map['priority_response'] ?? false,
    advancedAnalysis: map['advanced_analysis'] ?? false,
    customPrompts: map['custom_prompts'] ?? false,
  );
} 