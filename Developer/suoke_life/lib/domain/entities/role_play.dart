import 'package:freezed_annotation/freezed_annotation.dart';

part 'role_play.freezed.dart';

@freezed
class RolePlay with _$RolePlay {
  const factory RolePlay({
    required String id,
    required String name,
    required String description,
    required int unlockPoints,
    required String iconUrl,
    required int level,
    required int currentExp,
    required int requiredExpForNextLevel,
    required List<String> privileges,
    required bool isUnlocked,
    DateTime? unlockedAt,
    Map<String, dynamic>? metadata,
  }) = _RolePlay;

  const RolePlay._();

  double get progressToNextLevel {
    if (requiredExpForNextLevel <= 0) return 1.0;
    return currentExp / requiredExpForNextLevel;
  }
}

@freezed
class RolePlayProgress with _$RolePlayProgress {
  const factory RolePlayProgress({
    required String userId,
    required String currentRoleId,
    required int totalExp,
    required int level,
    required int levelExp,
    required int requiredExpForNextLevel,
    required List<String> unlockedRoles,
    required Map<String, int> roleExperience,
    required Map<String, int> roleLevels,
  }) = _RolePlayProgress;

  const RolePlayProgress._();

  double get progressToNextLevel {
    if (requiredExpForNextLevel <= 0) return 1.0;
    return levelExp / requiredExpForNextLevel;
  }
} 