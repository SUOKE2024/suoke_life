import 'package:freezed_annotation/freezed_annotation.dart';

part 'points.freezed.dart';

@freezed
class PointsBalance with _$PointsBalance {
  const factory PointsBalance({
    required String userId,
    required int sokelifePoints,
    required int sokelifeCoins,
    required DateTime lastUpdated,
    @Default(0) int pendingPoints,
    @Default(0) int pendingCoins,
    Map<String, int>? categoryPoints,
  }) = _PointsBalance;
}

@freezed
class PointsTransaction with _$PointsTransaction {
  const factory PointsTransaction({
    required String id,
    required String userId,
    required String description,
    required int amount,
    required PointsType type,
    required TransactionType transactionType,
    required DateTime timestamp,
    String? categoryId,
    String? referenceId,
    Map<String, dynamic>? metadata,
  }) = _PointsTransaction;
}

@freezed
class Voucher with _$Voucher {
  const factory Voucher({
    required String id,
    required String userId,
    required String name,
    required String description,
    required VoucherType type,
    required DateTime createdAt,
    required DateTime expiresAt,
    required bool isRedeemed,
    DateTime? redeemedAt,
    String? code,
    String? qrCode,
    @Default(false) bool requiresReservation,
    Map<String, dynamic>? discountInfo,
    Map<String, dynamic>? metadata,
  }) = _Voucher;

  const Voucher._();

  bool get isExpired => DateTime.now().isAfter(expiresAt);
  bool get isValid => !isRedeemed && !isExpired;
  int get daysUntilExpiration {
    return expiresAt.difference(DateTime.now()).inDays;
  }
}

@freezed
class Achievement with _$Achievement {
  const factory Achievement({
    required String id,
    required String name,
    required String description,
    required String category,
    required AchievementLevel level,
    required String iconUrl,
    required int pointsReward,
    required int coinsReward,
    required Map<String, dynamic> criteria,
    @Default(false) bool isSecret,
    @Default({}) Map<String, dynamic> metadata,
  }) = _Achievement;
}

@freezed
class UserAchievement with _$UserAchievement {
  const factory UserAchievement({
    required String userId,
    required String achievementId,
    required DateTime unlockedAt,
    required bool rewardClaimed,
    DateTime? rewardClaimedAt,
    @Default(false) bool isShared,
    Map<String, dynamic>? progressData,
  }) = _UserAchievement;
}

enum PointsType {
  sokelifePoints,
  sokelifeCoins
}

enum TransactionType {
  earn,
  spend,
  refund,
  expire,
  admin
}

enum VoucherType {
  physicalService,
  productDiscount,
  experienceTicket
}

enum AchievementLevel {
  bronze,
  silver,
  gold,
  platinum
} 