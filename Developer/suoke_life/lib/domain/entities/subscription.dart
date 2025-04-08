import 'package:freezed_annotation/freezed_annotation.dart';

part 'subscription.freezed.dart';

@freezed
class Subscription with _$Subscription {
  const factory Subscription({
    required String id,
    required String userId,
    required String planId,
    required String planName,
    required SubscriptionStatus status,
    required DateTime startDate,
    required DateTime endDate,
    required bool autoRenew,
    required BillingCycle billingCycle,
    DateTime? lastBilledAt,
    DateTime? nextBillingDate,
    double? price,
    String? transactionId,
    String? paymentMethod,
    int? familyMembersCount,
    List<String>? familyMemberIds,
    Map<String, dynamic>? metadata,
  }) = _Subscription;

  const Subscription._();

  bool get isActive => status == SubscriptionStatus.active;
  bool get isExpired => DateTime.now().isAfter(endDate);
  bool get isInGracePeriod => 
      status == SubscriptionStatus.gracePeriod ||
      (isExpired && DateTime.now().difference(endDate).inDays <= 3);
  
  int get daysUntilRenewal {
    if (nextBillingDate == null) return 0;
    return nextBillingDate!.difference(DateTime.now()).inDays;
  }
  
  bool get willAutoRenew => autoRenew && status == SubscriptionStatus.active;
}

@freezed
class SubscriptionPlan with _$SubscriptionPlan {
  const factory SubscriptionPlan({
    required String id,
    required String name,
    required String description,
    required double price,
    required List<String> benefits,
    List<String>? limitations,
    List<BillingCycle>? availableBillingCycles,
    @Default(0) int yearlyDiscountPercentage,
    @Default(0) int maxFamilyMembers,
    @Default(false) bool isDefault,
    @Default(true) bool isPublic,
    Map<String, dynamic>? metadata,
  }) = _SubscriptionPlan;

  const SubscriptionPlan._();

  bool get isFree => price <= 0;
  bool get isFamilyPlan => maxFamilyMembers > 1;
  
  double getPriceForCycle(BillingCycle cycle) {
    switch (cycle) {
      case BillingCycle.monthly:
        return price;
      case BillingCycle.yearly:
        return price * 12 * (1 - yearlyDiscountPercentage / 100);
      default:
        return price;
    }
  }
}

enum SubscriptionStatus {
  active,
  cancelled,
  expired,
  trial,
  gracePeriod,
  paused,
  pastDue
}

enum BillingCycle {
  monthly,
  yearly
}