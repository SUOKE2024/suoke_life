import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../core/agent_base.dart';
import '../core/agent_event.dart';
import '../core/agent_factory.dart';
import '../models/learning_data.dart';
import '../models/security_audit.dart';
import '../registry/agent_registry.dart';
import 'health_management_agent.dart';
import 'nutrition_balance_agent.dart';

/// 运动类型枚举
enum ExerciseType {
  aerobic,         // 有氧运动，如跑步、游泳
  strength,        // 力量训练，如举重
  flexibility,     // 柔韧性训练，如瑜伽、拉伸
  balance,         // 平衡训练，如太极
  coordination,    // 协调性训练，如舞蹈
  hiit,            // 高强度间歇训练
  functional,      // 功能性训练
  rehabilitative,  // 康复训练
  traditional,     // 传统运动(太极、气功等)
  team,            // 团队运动
  outdoor,         // 户外运动
}

/// 运动强度级别
enum ExerciseIntensity {
  veryLight,   // 很轻松，几乎没有感觉
  light,       // 轻松，呼吸轻微加快
  moderate,    // 中等，呼吸加快但能说完整句子
  vigorous,    // 剧烈，呼吸较重，只能说几个词
  maximal,     // 极限，无法说话
}

/// 运动经验级别
enum ExperienceLevel {
  beginner,    // 初学者
  intermediate, // 中级
  advanced,    // 高级
  professional, // 专业
}

/// 运动计划类型
enum ExercisePlanType {
  generalFitness,      // 一般健身
  weightLoss,          // 减肥
  muscleGain,          // 增肌
  enduranceBuilding,   // 耐力提升
  flexibility,         // 柔韧性提升
  rehabilitation,      // 康复训练
  seniorFitness,       // 老年健身
  childFitness,        // 儿童健身
  prenatal,            // 孕期训练
  postnatal,           // 产后训练
  sportSpecific,       // 特定运动训练
  stressReduction,     // 减压
  balanceImprovement,  // 平衡改善
  tcmPractice,         // 中医传统锻炼
}

/// 运动频率类型
enum ExerciseFrequency {
  daily,               // 每天
  alternateDays,       // 隔天
  threeTimesPerWeek,   // 每周三次
  fourTimesPerWeek,    // 每周四次
  fiveTimesPerWeek,    // 每周五次
  weekends,            // 仅周末
  customSchedule,      // 自定义计划
}

/// 运动约束或禁忌
class ExerciseContraindication {
  final String id;
  final String condition; // 疾病或身体状况
  final List<ExerciseType> restrictedTypes; // 受限的运动类型
  final String description; // 描述为什么受限
  final List<String> recommendations; // 替代建议

  ExerciseContraindication({
    required this.id,
    required this.condition,
    required this.restrictedTypes,
    required this.description,
    required this.recommendations,
  });

  factory ExerciseContraindication.fromJson(Map<String, dynamic> json) {
    return ExerciseContraindication(
      id: json['id'] as String,
      condition: json['condition'] as String,
      restrictedTypes: (json['restrictedTypes'] as List)
          .map((e) => ExerciseType.values.firstWhere(
                (type) => type.toString() == 'ExerciseType.${e}',
              ))
          .toList(),
      description: json['description'] as String,
      recommendations: List<String>.from(json['recommendations']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'condition': condition,
      'restrictedTypes': restrictedTypes
          .map((type) => type.toString().split('.').last)
          .toList(),
      'description': description,
      'recommendations': recommendations,
    };
  }
}

/// 运动会话记录
class ExerciseSession {
  final String id;
  final String userId;
  final String name;
  final ExerciseType type;
  final DateTime startTime;
  final DateTime endTime;
  final ExerciseIntensity intensity;
  final int caloriesBurned;
  final double distance; // 以公里为单位，如果适用
  final int steps; // 如果适用
  final double duration; // 以分钟为单位
  final double avgHeartRate; // 平均心率
  final double maxHeartRate; // 最大心率
  final Map<String, dynamic> additionalData; // 特定运动的额外数据
  final String? notes;
  final bool completed;
  final double completionPercentage; // 完成百分比

  ExerciseSession({
    required this.id,
    required this.userId,
    required this.name,
    required this.type,
    required this.startTime,
    required this.endTime,
    required this.intensity,
    required this.caloriesBurned,
    this.distance = 0.0,
    this.steps = 0,
    required this.duration,
    this.avgHeartRate = 0.0,
    this.maxHeartRate = 0.0,
    this.additionalData = const {},
    this.notes,
    this.completed = true,
    this.completionPercentage = 100.0,
  });

  factory ExerciseSession.fromJson(Map<String, dynamic> json) {
    return ExerciseSession(
      id: json['id'] as String,
      userId: json['userId'] as String,
      name: json['name'] as String,
      type: ExerciseType.values.firstWhere(
          (e) => e.toString() == 'ExerciseType.${json['type']}'),
      startTime: DateTime.parse(json['startTime'] as String),
      endTime: DateTime.parse(json['endTime'] as String),
      intensity: ExerciseIntensity.values.firstWhere(
          (e) => e.toString() == 'ExerciseIntensity.${json['intensity']}'),
      caloriesBurned: json['caloriesBurned'] as int,
      distance: (json['distance'] as num?)?.toDouble() ?? 0.0,
      steps: (json['steps'] as int?) ?? 0,
      duration: (json['duration'] as num).toDouble(),
      avgHeartRate: (json['avgHeartRate'] as num?)?.toDouble() ?? 0.0,
      maxHeartRate: (json['maxHeartRate'] as num?)?.toDouble() ?? 0.0,
      additionalData: json['additionalData'] as Map<String, dynamic>? ?? {},
      notes: json['notes'] as String?,
      completed: json['completed'] as bool? ?? true,
      completionPercentage:
          (json['completionPercentage'] as num?)?.toDouble() ?? 100.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'name': name,
      'type': type.toString().split('.').last,
      'startTime': startTime.toIso8601String(),
      'endTime': endTime.toIso8601String(),
      'intensity': intensity.toString().split('.').last,
      'caloriesBurned': caloriesBurned,
      'distance': distance,
      'steps': steps,
      'duration': duration,
      'avgHeartRate': avgHeartRate,
      'maxHeartRate': maxHeartRate,
      'additionalData': additionalData,
      'notes': notes,
      'completed': completed,
      'completionPercentage': completionPercentage,
    };
  }
}

/// 定义运动活动
class ExerciseActivity {
  final String id;
  final String name;
  final ExerciseType type;
  final ExerciseIntensity intensity;
  final double duration; // 以分钟为单位
  final int caloriesPerMinute; // 基于平均体重的估计
  final List<String> muscleGroups; // 涉及的肌肉群
  final String? instructions; // 运动指导
  final List<String>? modifications; // 可能的修改方案
  final ExperienceLevel recommendedLevel; // 推荐经验级别
  final List<String>? equipment; // 所需设备
  final Map<String, dynamic> tcmProperties; // 中医相关属性
  final List<ExerciseContraindication>? contraindications; // 禁忌

  ExerciseActivity({
    required this.id,
    required this.name,
    required this.type,
    required this.intensity,
    required this.duration,
    required this.caloriesPerMinute,
    this.muscleGroups = const [],
    this.instructions,
    this.modifications,
    required this.recommendedLevel,
    this.equipment,
    this.tcmProperties = const {},
    this.contraindications,
  });

  factory ExerciseActivity.fromJson(Map<String, dynamic> json) {
    return ExerciseActivity(
      id: json['id'] as String,
      name: json['name'] as String,
      type: ExerciseType.values.firstWhere(
          (e) => e.toString() == 'ExerciseType.${json['type']}'),
      intensity: ExerciseIntensity.values.firstWhere(
          (e) => e.toString() == 'ExerciseIntensity.${json['intensity']}'),
      duration: (json['duration'] as num).toDouble(),
      caloriesPerMinute: json['caloriesPerMinute'] as int,
      muscleGroups: json['muscleGroups'] != null
          ? List<String>.from(json['muscleGroups'])
          : [],
      instructions: json['instructions'] as String?,
      modifications: json['modifications'] != null
          ? List<String>.from(json['modifications'])
          : null,
      recommendedLevel: ExperienceLevel.values.firstWhere((e) =>
          e.toString() == 'ExperienceLevel.${json['recommendedLevel']}'),
      equipment: json['equipment'] != null
          ? List<String>.from(json['equipment'])
          : null,
      tcmProperties: json['tcmProperties'] as Map<String, dynamic>? ?? {},
      contraindications: json['contraindications'] != null
          ? (json['contraindications'] as List)
              .map((e) => ExerciseContraindication.fromJson(e))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type.toString().split('.').last,
      'intensity': intensity.toString().split('.').last,
      'duration': duration,
      'caloriesPerMinute': caloriesPerMinute,
      'muscleGroups': muscleGroups,
      'instructions': instructions,
      'modifications': modifications,
      'recommendedLevel': recommendedLevel.toString().split('.').last,
      'equipment': equipment,
      'tcmProperties': tcmProperties,
      'contraindications': contraindications?.map((e) => e.toJson()).toList(),
    };
  }
}

/// 每日运动计划
class DailyExercisePlan {
  final String id;
  final DateTime date;
  final List<ExerciseActivity> activities;
  final int totalCaloriesBurned; // 预计总消耗
  final double totalDuration; // 总持续时间(分钟)
  final String? warmupInstructions; // 热身指导
  final String? cooldownInstructions; // 冷却指导
  final String? notes; // 额外注释
  final bool completed;
  final double completionPercentage; // 完成百分比

  DailyExercisePlan({
    required this.id,
    required this.date,
    required this.activities,
    required this.totalCaloriesBurned,
    required this.totalDuration,
    this.warmupInstructions,
    this.cooldownInstructions,
    this.notes,
    this.completed = false,
    this.completionPercentage = 0.0,
  });

  factory DailyExercisePlan.fromJson(Map<String, dynamic> json) {
    return DailyExercisePlan(
      id: json['id'] as String,
      date: DateTime.parse(json['date'] as String),
      activities: (json['activities'] as List)
          .map((e) => ExerciseActivity.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalCaloriesBurned: json['totalCaloriesBurned'] as int,
      totalDuration: (json['totalDuration'] as num).toDouble(),
      warmupInstructions: json['warmupInstructions'] as String?,
      cooldownInstructions: json['cooldownInstructions'] as String?,
      notes: json['notes'] as String?,
      completed: json['completed'] as bool? ?? false,
      completionPercentage:
          (json['completionPercentage'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date.toIso8601String(),
      'activities': activities.map((e) => e.toJson()).toList(),
      'totalCaloriesBurned': totalCaloriesBurned,
      'totalDuration': totalDuration,
      'warmupInstructions': warmupInstructions,
      'cooldownInstructions': cooldownInstructions,
      'notes': notes,
      'completed': completed,
      'completionPercentage': completionPercentage,
    };
  }
}

/// 周运动计划
class WeeklyExercisePlan {
  final String id;
  final String userId;
  final String name;
  final DateTime startDate;
  final DateTime endDate;
  final ExercisePlanType type;
  final ExperienceLevel level;
  final List<DailyExercisePlan> dailyPlans;
  final Map<String, dynamic> goals; // 计划目标
  final List<String>? focusAreas; // 重点关注区域
  final int totalPlannedCaloriesBurn; // 计划总消耗
  final List<String> notes; // 额外注释
  final bool active; // 是否是当前活跃计划
  final double completionPercentage; // 完成百分比

  WeeklyExercisePlan({
    required this.id,
    required this.userId,
    required this.name,
    required this.startDate,
    required this.endDate,
    required this.type,
    required this.level,
    required this.dailyPlans,
    this.goals = const {},
    this.focusAreas,
    required this.totalPlannedCaloriesBurn,
    this.notes = const [],
    this.active = true,
    this.completionPercentage = 0.0,
  });

  factory WeeklyExercisePlan.fromJson(Map<String, dynamic> json) {
    return WeeklyExercisePlan(
      id: json['id'] as String,
      userId: json['userId'] as String,
      name: json['name'] as String,
      startDate: DateTime.parse(json['startDate'] as String),
      endDate: DateTime.parse(json['endDate'] as String),
      type: ExercisePlanType.values.firstWhere(
          (e) => e.toString() == 'ExercisePlanType.${json['type']}'),
      level: ExperienceLevel.values.firstWhere(
          (e) => e.toString() == 'ExperienceLevel.${json['level']}'),
      dailyPlans: (json['dailyPlans'] as List)
          .map((e) => DailyExercisePlan.fromJson(e as Map<String, dynamic>))
          .toList(),
      goals: json['goals'] as Map<String, dynamic>? ?? {},
      focusAreas: json['focusAreas'] != null
          ? List<String>.from(json['focusAreas'])
          : null,
      totalPlannedCaloriesBurn: json['totalPlannedCaloriesBurn'] as int,
      notes: json['notes'] != null ? List<String>.from(json['notes']) : [],
      active: json['active'] as bool? ?? true,
      completionPercentage:
          (json['completionPercentage'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'name': name,
      'startDate': startDate.toIso8601String(),
      'endDate': endDate.toIso8601String(),
      'type': type.toString().split('.').last,
      'level': level.toString().split('.').last,
      'dailyPlans': dailyPlans.map((e) => e.toJson()).toList(),
      'goals': goals,
      'focusAreas': focusAreas,
      'totalPlannedCaloriesBurn': totalPlannedCaloriesBurn,
      'notes': notes,
      'active': active,
      'completionPercentage': completionPercentage,
    };
  }
}

/// 用户体能评估
class FitnessAssessment {
  final String id;
  final String userId;
  final DateTime assessmentDate;
  final double weight; // 体重(kg)
  final double height; // 身高(cm)
  final double bmi; // 体质指数
  final double? bodyFatPercentage; // 体脂率
  final double? restingHeartRate; // 静息心率
  final double? vo2Max; // 最大摄氧量
  final Map<String, double>? strengthTests; // 力量测试结果
  final Map<String, double>? flexibilityTests; // 柔韧性测试结果
  final Map<String, double>? enduranceTests; // 耐力测试结果
  final Map<String, double>? balanceTests; // 平衡测试结果
  final TraditionalChineseBodyType? bodyType; // 中医体质类型
  final List<String>? healthConditions; // 健康状况
  final List<ExerciseContraindication>? exerciseRestrictions; // 运动限制
  final String? overallAssessment; // 整体评估
  final List<String>? recommendations; // 建议

  FitnessAssessment({
    required this.id,
    required this.userId,
    required this.assessmentDate,
    required this.weight,
    required this.height,
    required this.bmi,
    this.bodyFatPercentage,
    this.restingHeartRate,
    this.vo2Max,
    this.strengthTests,
    this.flexibilityTests,
    this.enduranceTests,
    this.balanceTests,
    this.bodyType,
    this.healthConditions,
    this.exerciseRestrictions,
    this.overallAssessment,
    this.recommendations,
  });

  factory FitnessAssessment.fromJson(Map<String, dynamic> json) {
    return FitnessAssessment(
      id: json['id'] as String,
      userId: json['userId'] as String,
      assessmentDate: DateTime.parse(json['assessmentDate'] as String),
      weight: (json['weight'] as num).toDouble(),
      height: (json['height'] as num).toDouble(),
      bmi: (json['bmi'] as num).toDouble(),
      bodyFatPercentage: (json['bodyFatPercentage'] as num?)?.toDouble(),
      restingHeartRate: (json['restingHeartRate'] as num?)?.toDouble(),
      vo2Max: (json['vo2Max'] as num?)?.toDouble(),
      strengthTests: json['strengthTests'] != null
          ? Map<String, double>.from(json['strengthTests'])
          : null,
      flexibilityTests: json['flexibilityTests'] != null
          ? Map<String, double>.from(json['flexibilityTests'])
          : null,
      enduranceTests: json['enduranceTests'] != null
          ? Map<String, double>.from(json['enduranceTests'])
          : null,
      balanceTests: json['balanceTests'] != null
          ? Map<String, double>.from(json['balanceTests'])
          : null,
      bodyType: json['bodyType'] != null
          ? TraditionalChineseBodyType.values.firstWhere((e) =>
              e.toString() == 'TraditionalChineseBodyType.${json['bodyType']}')
          : null,
      healthConditions: json['healthConditions'] != null
          ? List<String>.from(json['healthConditions'])
          : null,
      exerciseRestrictions: json['exerciseRestrictions'] != null
          ? (json['exerciseRestrictions'] as List)
              .map((e) => ExerciseContraindication.fromJson(e))
              .toList()
          : null,
      overallAssessment: json['overallAssessment'] as String?,
      recommendations: json['recommendations'] != null
          ? List<String>.from(json['recommendations'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'assessmentDate': assessmentDate.toIso8601String(),
      'weight': weight,
      'height': height,
      'bmi': bmi,
      'bodyFatPercentage': bodyFatPercentage,
      'restingHeartRate': restingHeartRate,
      'vo2Max': vo2Max,
      'strengthTests': strengthTests,
      'flexibilityTests': flexibilityTests,
      'enduranceTests': enduranceTests,
      'balanceTests': balanceTests,
      'bodyType': bodyType?.toString().split('.').last,
      'healthConditions': healthConditions,
      'exerciseRestrictions':
          exerciseRestrictions?.map((e) => e.toJson()).toList(),
      'overallAssessment': overallAssessment,
      'recommendations': recommendations,
    };
  }
}

/// 运动进度报告
class ExerciseProgressReport {
  final String id;
  final String userId;
  final DateTime startDate;
  final DateTime endDate;
  final int totalSessionsCompleted;
  final double totalDuration; // 总时长(分钟)
  final int totalCaloriesBurned;
  final Map<ExerciseType, double> exerciseTypeDistribution; // 运动类型分布
  final Map<String, double> progressMetrics; // 进步指标
  final List<String> achievements; // 成就
  final List<String> challengesIdentified; // 识别的挑战
  final List<String> recommendations; // 建议
  final String? summary;

  ExerciseProgressReport({
    required this.id,
    required this.userId,
    required this.startDate,
    required this.endDate,
    required this.totalSessionsCompleted,
    required this.totalDuration,
    required this.totalCaloriesBurned,
    required this.exerciseTypeDistribution,
    required this.progressMetrics,
    this.achievements = const [],
    this.challengesIdentified = const [],
    this.recommendations = const [],
    this.summary,
  });

  factory ExerciseProgressReport.fromJson(Map<String, dynamic> json) {
    // 解析运动类型分布
    final typesMap = <ExerciseType, double>{};
    if (json['exerciseTypeDistribution'] != null) {
      (json['exerciseTypeDistribution'] as Map).forEach((key, value) {
        final type = ExerciseType.values.firstWhere(
            (e) => e.toString() == 'ExerciseType.$key');
        typesMap[type] = (value as num).toDouble();
      });
    }

    return ExerciseProgressReport(
      id: json['id'] as String,
      userId: json['userId'] as String,
      startDate: DateTime.parse(json['startDate'] as String),
      endDate: DateTime.parse(json['endDate'] as String),
      totalSessionsCompleted: json['totalSessionsCompleted'] as int,
      totalDuration: (json['totalDuration'] as num).toDouble(),
      totalCaloriesBurned: json['totalCaloriesBurned'] as int,
      exerciseTypeDistribution: typesMap,
      progressMetrics: json['progressMetrics'] != null
          ? Map<String, double>.from(json['progressMetrics'])
          : {},
      achievements: json['achievements'] != null
          ? List<String>.from(json['achievements'])
          : [],
      challengesIdentified: json['challengesIdentified'] != null
          ? List<String>.from(json['challengesIdentified'])
          : [],
      recommendations: json['recommendations'] != null
          ? List<String>.from(json['recommendations'])
          : [],
      summary: json['summary'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    // 转换运动类型分布
    final typesMap = <String, double>{};
    exerciseTypeDistribution.forEach((key, value) {
      typesMap[key.toString().split('.').last] = value;
    });

    return {
      'id': id,
      'userId': userId,
      'startDate': startDate.toIso8601String(),
      'endDate': endDate.toIso8601String(),
      'totalSessionsCompleted': totalSessionsCompleted,
      'totalDuration': totalDuration,
      'totalCaloriesBurned': totalCaloriesBurned,
      'exerciseTypeDistribution': typesMap,
      'progressMetrics': progressMetrics,
      'achievements': achievements,
      'challengesIdentified': challengesIdentified,
      'recommendations': recommendations,
      'summary': summary,
    };
  }
}

/// 运动搜索过滤器
class ExerciseSearchFilter {
  final List<ExerciseType>? types;
  final List<ExerciseIntensity>? intensities;
  final ExperienceLevel? maxLevel;
  final double? maxDuration;
  final List<String>? targetMuscleGroups;
  final List<String>? excludedEquipment;
  final TraditionalChineseBodyType? suitableForBodyType;
  final List<String>? healthConditions;

  ExerciseSearchFilter({
    this.types,
    this.intensities,
    this.maxLevel,
    this.maxDuration,
    this.targetMuscleGroups,
    this.excludedEquipment,
    this.suitableForBodyType,
    this.healthConditions,
  });

  Map<String, dynamic> toJson() {
    return {
      'types': types?.map((e) => e.toString().split('.').last).toList(),
      'intensities':
          intensities?.map((e) => e.toString().split('.').last).toList(),
      'maxLevel': maxLevel?.toString().split('.').last,
      'maxDuration': maxDuration,
      'targetMuscleGroups': targetMuscleGroups,
      'excludedEquipment': excludedEquipment,
      'suitableForBodyType': suitableForBodyType?.toString().split('.').last,
      'healthConditions': healthConditions,
    };
  }
}

/// 运动规划代理接口
abstract class ExercisePlanningAgent {
  String get id;

  /// 记录单次运动会话
  Future<String> recordExerciseSession(ExerciseSession session);

  /// 批量记录运动会话
  Future<List<String>> recordExerciseSessionBatch(List<ExerciseSession> sessions);

  /// 获取用户的运动会话记录
  Future<List<ExerciseSession>> getExerciseSessions(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    ExerciseType? type,
  });

  /// 创建体能评估
  Future<String> createFitnessAssessment(FitnessAssessment assessment);

  /// 获取最新的体能评估
  Future<FitnessAssessment?> getLatestFitnessAssessment(String userId);

  /// 获取体能评估历史
  Future<List<FitnessAssessment>> getFitnessAssessmentHistory(
    String userId, {
    int limit = 10,
  });

  /// 创建每周运动计划
  Future<String> createWeeklyExercisePlan(WeeklyExercisePlan plan);

  /// 获取用户的运动计划
  Future<List<WeeklyExercisePlan>> getUserExercisePlans(
    String userId, {
    bool? active,
  });

  /// 按日期获取每日运动计划
  Future<DailyExercisePlan?> getDailyExercisePlan(
    String userId,
    DateTime date,
  );

  /// 更新运动会话的完成状态
  Future<bool> updateExerciseSessionCompletion(
    String sessionId,
    bool completed, {
    double? completionPercentage,
  });

  /// 更新每日计划的完成状态
  Future<bool> updateDailyPlanCompletion(
    String planId,
    bool completed, {
    double? completionPercentage,
  });

  /// 搜索运动活动
  Future<List<ExerciseActivity>> searchExerciseActivities(
    ExerciseSearchFilter filter,
  );

  /// 获取适合特定体质的运动建议
  Future<List<ExerciseActivity>> getExercisesForBodyType(
    TraditionalChineseBodyType bodyType,
  );

  /// 生成运动进度报告
  Future<ExerciseProgressReport> generateProgressReport(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
  });

  /// 获取根据健康状况的运动建议
  Future<List<String>> getExerciseRecommendations(
    String userId, {
    List<String>? healthConditions,
    TraditionalChineseBodyType? bodyType,
  });

  /// 生成自定义锻炼计划
  Future<WeeklyExercisePlan> generateCustomExercisePlan(
    String userId, {
    ExercisePlanType? planType,
    ExperienceLevel? level,
    int? targetCaloriesBurn,
    List<String>? focusAreas,
    ExerciseFrequency? frequency,
    DateTime? startDate,
    int durationInWeeks = 1,
  });
}

/// 运动规划代理实现
class ExercisePlanningAgentImpl implements ExercisePlanningAgent {
  final AIAgent _agent;
  final AutonomousLearningSystem _learningSystem;
  final RAGService _ragService;
  final SecurityPrivacyFramework _securityFramework;
  final HealthManagementAgent _healthAgent;
  final NutritionBalanceAgent? _nutritionAgent;

  // 内部存储
  final Map<String, ExerciseSession> _sessions = {};
  final Map<String, FitnessAssessment> _assessments = {};
  final Map<String, WeeklyExercisePlan> _plans = {};
  final Map<String, List<ExerciseActivity>> _activityDatabase = {};

  ExercisePlanningAgentImpl({
    required AIAgent agent,
    required AutonomousLearningSystem learningSystem,
    required RAGService ragService,
    required SecurityPrivacyFramework securityFramework,
    required HealthManagementAgent healthAgent,
    NutritionBalanceAgent? nutritionAgent,
  })  : _agent = agent,
        _learningSystem = learningSystem,
        _ragService = ragService,
        _securityFramework = securityFramework,
        _healthAgent = healthAgent,
        _nutritionAgent = nutritionAgent {
    _initializeActivityDatabase();
  }

  @override
  String get id => _agent.id;

  /// 初始化运动活动数据库
  void _initializeActivityDatabase() {
    // 初始化一些基本运动类型
    _addActivitiesForType(ExerciseType.aerobic, [
      ExerciseActivity(
        id: const Uuid().v4(),
        name: '慢跑',
        type: ExerciseType.aerobic,
        intensity: ExerciseIntensity.moderate,
        duration: 30,
        caloriesPerMinute: 10,
        muscleGroups: ['腿部', '心肺'],
        recommendedLevel: ExperienceLevel.beginner,
        instructions: '保持适中速度，能够正常交谈的程度。',
        tcmProperties: {
          'meridians': ['肺经', '脾经'],
          'effects': ['行气活血', '健脾和胃'],
        },
      ),
      ExerciseActivity(
        id: const Uuid().v4(),
        name: '快走',
        type: ExerciseType.aerobic,
        intensity: ExerciseIntensity.light,
        duration: 45,
        caloriesPerMinute: 6,
        muscleGroups: ['腿部', '心肺'],
        recommendedLevel: ExperienceLevel.beginner,
        instructions: '保持较快的步频，手臂自然摆动。',
        tcmProperties: {
          'meridians': ['脾经', '胃经'],
          'effects': ['舒筋活络', '健脾益气'],
        },
      ),
    ]);

    _addActivitiesForType(ExerciseType.strength, [
      ExerciseActivity(
        id: const Uuid().v4(),
        name: '俯卧撑',
        type: ExerciseType.strength,
        intensity: ExerciseIntensity.moderate,
        duration: 15,
        caloriesPerMinute: 8,
        muscleGroups: ['胸部', '三头肌', '肩部', '核心'],
        recommendedLevel: ExperienceLevel.beginner,
        instructions: '保持身体成一直线，肘部弯曲至接近90度。',
        modifications: ['墙壁俯卧撑', '膝盖俯卧撑'],
        tcmProperties: {
          'meridians': ['肺经', '心包经'],
          'effects': ['强壮上肢', '振奋阳气'],
        },
      ),
      ExerciseActivity(
        id: const Uuid().v4(),
        name: '深蹲',
        type: ExerciseType.strength,
        intensity: ExerciseIntensity.moderate,
        duration: 15,
        caloriesPerMinute: 8,
        muscleGroups: ['大腿', '臀部', '核心'],
        recommendedLevel: ExperienceLevel.beginner,
        instructions: '保持背部挺直，下蹲时膝盖不超过脚尖。',
        modifications: ['扶椅深蹲', '半深蹲'],
        tcmProperties: {
          'meridians': ['肾经', '膀胱经'],
          'effects': ['强壮下肢', '补肾壮腰'],
        },
      ),
    ]);

    _addActivitiesForType(ExerciseType.flexibility, [
      ExerciseActivity(
        id: const Uuid().v4(),
        name: '坐姿前屈',
        type: ExerciseType.flexibility,
        intensity: ExerciseIntensity.light,
        duration: 10,
        caloriesPerMinute: 3,
        muscleGroups: ['腿筋', '下背部'],
        recommendedLevel: ExperienceLevel.beginner,
        instructions: '坐直，双腿伸直，上身慢慢向前弯曲，尽量触摸脚尖。',
        tcmProperties: {
          'meridians': ['膀胱经', '肾经'],
          'effects': ['舒展筋络', '活化肾气'],
        },
      ),
    ]);

    _addActivitiesForType(ExerciseType.balance, [
      ExerciseActivity(
        id: const Uuid().v4(),
        name: '单腿站立',
        type: ExerciseType.balance,
        intensity: ExerciseIntensity.light,
        duration: 5,
        caloriesPerMinute: 2,
        muscleGroups: ['核心', '腿部'],
        recommendedLevel: ExperienceLevel.beginner,
        instructions: '一只脚站立，另一只脚抬起，保持平衡。',
        tcmProperties: {
          'meridians': ['脾经', '肝经'],
          'effects': ['平衡阴阳', '健脾理气'],
        },
      ),
    ]);

    _addActivitiesForType(ExerciseType.traditional, [
      ExerciseActivity(
        id: const Uuid().v4(),
        name: '太极八式',
        type: ExerciseType.traditional,
        intensity: ExerciseIntensity.light,
        duration: 20,
        caloriesPerMinute: 4,
        muscleGroups: ['全身', '核心'],
        recommendedLevel: ExperienceLevel.beginner,
        instructions: '缓慢流畅地完成八个基本太极动作。',
        tcmProperties: {
          'meridians': ['任脉', '督脉'],
          'effects': ['调和阴阳', '行气活血', '宁心安神'],
        },
      ),
    ]);
  }

  void _addActivitiesForType(ExerciseType type, List<ExerciseActivity> activities) {
    if (!_activityDatabase.containsKey(type.toString())) {
      _activityDatabase[type.toString()] = [];
    }
    _activityDatabase[type.toString()]!.addAll(activities);
  }

  @override
  Future<String> recordExerciseSession(ExerciseSession session) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.write,
        'exercise_sessions',
        userId: session.userId,
      );

      // 存储会话记录
      _sessions[session.id] = session;

      // 收集学习数据
      await _learningSystem.collectLearningData(
        LearningData(
          agentId: id,
          dataType: LearningDataType.userBehavior,
          content: {
            'action': 'record_exercise_session',
            'exerciseType': session.type.toString(),
            'duration': session.duration,
            'intensity': session.intensity.toString(),
            'caloriesBurned': session.caloriesBurned,
          },
          timestamp: DateTime.now(),
        ),
      );

      // 发布代理事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataCreated,
        source: id,
        data: {
          'entityType': 'exercise_session',
          'entityId': session.id,
          'userId': session.userId,
        },
      ));

      // 向健康管理代理发送数据
      await _healthAgent.recordHealthData(HealthDataRecord(
        id: const Uuid().v4(),
        userId: session.userId,
        dataType: HealthDataType.exercise,
        value: session.caloriesBurned.toDouble(),
        unit: 'kcal',
        timestamp: session.endTime,
        source: id,
        notes: '${session.name} (${session.duration}分钟)',
      ));

      return session.id;
    } catch (e) {
      if (kDebugMode) {
        print('记录运动会话失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'recordExerciseSession',
          'error': e.toString(),
        },
      ));

      rethrow;
    }
  }

  @override
  Future<List<String>> recordExerciseSessionBatch(List<ExerciseSession> sessions) async {
    final recordedIds = <String>[];

    for (final session in sessions) {
      try {
        final id = await recordExerciseSession(session);
        recordedIds.add(id);
      } catch (e) {
        if (kDebugMode) {
          print('批量记录运动会话失败 (${session.id}): $e');
        }
      }
    }

    return recordedIds;
  }

  @override
  Future<List<ExerciseSession>> getExerciseSessions(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    ExerciseType? type,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.read,
        'exercise_sessions',
        userId: userId,
      );

      // 筛选用户的会话记录
      final userSessions = _sessions.values.where((session) => session.userId == userId);

      // 应用过滤条件
      return userSessions.where((session) {
        bool match = true;

        if (startDate != null) {
          match = match && session.startTime.isAfter(startDate) || session.startTime.isAtSameMomentAs(startDate);
        }

        if (endDate != null) {
          match = match && session.startTime.isBefore(endDate);
        }

        if (type != null) {
          match = match && session.type == type;
        }

        return match;
      }).toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取运动会话记录失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getExerciseSessions',
          'error': e.toString(),
        },
      ));

      return [];
    }
  }

  @override
  Future<String> createFitnessAssessment(FitnessAssessment assessment) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.write,
        'fitness_assessments',
        userId: assessment.userId,
      );

      // 存储评估记录
      _assessments[assessment.id] = assessment;

      // 收集学习数据
      await _learningSystem.collectLearningData(
        LearningData(
          agentId: id,
          dataType: LearningDataType.userProfile,
          content: {
            'action': 'create_fitness_assessment',
            'bmi': assessment.bmi,
            'bodyType': assessment.bodyType?.toString(),
            'healthConditions': assessment.healthConditions,
          },
          timestamp: DateTime.now(),
        ),
      );

      // 发布代理事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataCreated,
        source: id,
        data: {
          'entityType': 'fitness_assessment',
          'entityId': assessment.id,
          'userId': assessment.userId,
        },
      ));

      return assessment.id;
    } catch (e) {
      if (kDebugMode) {
        print('创建体能评估失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'createFitnessAssessment',
          'error': e.toString(),
        },
      ));

      rethrow;
    }
  }

  @override
  Future<FitnessAssessment?> getLatestFitnessAssessment(String userId) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.read,
        'fitness_assessments',
        userId: userId,
      );

      // 筛选用户的评估记录并按日期排序
      final userAssessments = _assessments.values
          .where((assessment) => assessment.userId == userId)
          .toList()
        ..sort((a, b) => b.assessmentDate.compareTo(a.assessmentDate));

      return userAssessments.isNotEmpty ? userAssessments.first : null;
    } catch (e) {
      if (kDebugMode) {
        print('获取最新体能评估失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getLatestFitnessAssessment',
          'error': e.toString(),
        },
      ));

      return null;
    }
  }

  @override
  Future<List<FitnessAssessment>> getFitnessAssessmentHistory(
    String userId, {
    int limit = 10,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.read,
        'fitness_assessments',
        userId: userId,
      );

      // 筛选用户的评估记录并按日期排序
      final userAssessments = _assessments.values
          .where((assessment) => assessment.userId == userId)
          .toList()
        ..sort((a, b) => b.assessmentDate.compareTo(a.assessmentDate));

      // 应用限制
      return userAssessments.take(limit).toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取体能评估历史失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getFitnessAssessmentHistory',
          'error': e.toString(),
        },
      ));

      return [];
    }
  }

  @override
  Future<String> createWeeklyExercisePlan(WeeklyExercisePlan plan) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.write,
        'exercise_plans',
        userId: plan.userId,
      );

      // 如果设置为活跃计划，将其他同类型计划设为非活跃
      if (plan.active) {
        final existingPlans = _plans.values
            .where((p) => p.userId == plan.userId && p.type == plan.type && p.active);

        for (final existingPlan in existingPlans) {
          final updatedPlan = WeeklyExercisePlan(
            id: existingPlan.id,
            userId: existingPlan.userId,
            name: existingPlan.name,
            startDate: existingPlan.startDate,
            endDate: existingPlan.endDate,
            type: existingPlan.type,
            level: existingPlan.level,
            dailyPlans: existingPlan.dailyPlans,
            goals: existingPlan.goals,
            focusAreas: existingPlan.focusAreas,
            totalPlannedCaloriesBurn: existingPlan.totalPlannedCaloriesBurn,
            notes: existingPlan.notes,
            active: false,
            completionPercentage: existingPlan.completionPercentage,
          );
          _plans[existingPlan.id] = updatedPlan;
        }
      }

      // 存储计划
      _plans[plan.id] = plan;

      // 收集学习数据
      await _learningSystem.collectLearningData(
        LearningData(
          agentId: id,
          dataType: LearningDataType.userPreference,
          content: {
            'action': 'create_exercise_plan',
            'planType': plan.type.toString(),
            'experienceLevel': plan.level.toString(),
            'focusAreas': plan.focusAreas,
          },
          timestamp: DateTime.now(),
        ),
      );

      // 发布代理事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataCreated,
        source: id,
        data: {
          'entityType': 'weekly_exercise_plan',
          'entityId': plan.id,
          'userId': plan.userId,
        },
      ));

      return plan.id;
    } catch (e) {
      if (kDebugMode) {
        print('创建每周运动计划失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'createWeeklyExercisePlan',
          'error': e.toString(),
        },
      ));

      rethrow;
    }
  }

  @override
  Future<List<WeeklyExercisePlan>> getUserExercisePlans(
    String userId, {
    bool? active,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.read,
        'exercise_plans',
        userId: userId,
      );

      // 筛选用户的计划
      final userPlans = _plans.values.where((plan) => plan.userId == userId);

      // 应用过滤条件
      if (active != null) {
        return userPlans.where((plan) => plan.active == active).toList();
      }

      return userPlans.toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取用户运动计划失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getUserExercisePlans',
          'error': e.toString(),
        },
      ));

      return [];
    }
  }

  @override
  Future<DailyExercisePlan?> getDailyExercisePlan(
    String userId,
    DateTime date,
  ) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.read,
        'exercise_plans',
        userId: userId,
      );

      // 获取活跃的周计划
      final activePlans = await getUserExercisePlans(userId, active: true);

      // 查找日期匹配的日计划
      for (final plan in activePlans) {
        for (final dailyPlan in plan.dailyPlans) {
          if (dailyPlan.date.year == date.year &&
              dailyPlan.date.month == date.month &&
              dailyPlan.date.day == date.day) {
            return dailyPlan;
          }
        }
      }

      // 如果没有找到匹配的日计划，则生成一个
      if (activePlans.isNotEmpty) {
        // 选择第一个活跃计划作为模板
        final templatePlan = activePlans.first;
        
        // 获取用户的健身评估，以便根据用户情况调整
        final assessment = await getLatestFitnessAssessment(userId);
        
        // 生成适合的日计划
        final dailyPlan = await _generateDailyPlan(
          userId,
          date,
          templatePlan.type,
          templatePlan.level,
          assessment?.bodyType,
          assessment?.healthConditions,
        );
        
        return dailyPlan;
      }

      return null;
    } catch (e) {
      if (kDebugMode) {
        print('获取每日运动计划失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getDailyExercisePlan',
          'error': e.toString(),
        },
      ));

      return null;
    }
  }

  @override
  Future<bool> updateExerciseSessionCompletion(
    String sessionId,
    bool completed, {
    double? completionPercentage,
  }) async {
    try {
      if (!_sessions.containsKey(sessionId)) {
        return false;
      }

      final session = _sessions[sessionId]!;

      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.update,
        'exercise_sessions',
        userId: session.userId,
      );

      // 更新会话完成状态
      final updatedSession = ExerciseSession(
        id: session.id,
        userId: session.userId,
        name: session.name,
        type: session.type,
        startTime: session.startTime,
        endTime: session.endTime,
        intensity: session.intensity,
        caloriesBurned: session.caloriesBurned,
        distance: session.distance,
        steps: session.steps,
        duration: session.duration,
        avgHeartRate: session.avgHeartRate,
        maxHeartRate: session.maxHeartRate,
        additionalData: session.additionalData,
        notes: session.notes,
        completed: completed,
        completionPercentage: completionPercentage ?? (completed ? 100.0 : 0.0),
      );

      _sessions[sessionId] = updatedSession;

      // 发布代理事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataUpdated,
        source: id,
        data: {
          'entityType': 'exercise_session',
          'entityId': sessionId,
          'userId': session.userId,
          'field': 'completion',
        },
      ));

      return true;
    } catch (e) {
      if (kDebugMode) {
        print('更新运动会话完成状态失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'updateExerciseSessionCompletion',
          'error': e.toString(),
        },
      ));

      return false;
    }
  }

  @override
  Future<bool> updateDailyPlanCompletion(
    String planId,
    bool completed, {
    double? completionPercentage,
  }) async {
    try {
      // 查找包含该日计划的周计划
      WeeklyExercisePlan? weeklyPlan;
      DailyExercisePlan? targetDailyPlan;

      for (final plan in _plans.values) {
        for (final dailyPlan in plan.dailyPlans) {
          if (dailyPlan.id == planId) {
            weeklyPlan = plan;
            targetDailyPlan = dailyPlan;
            break;
          }
        }
        if (weeklyPlan != null) break;
      }

      if (weeklyPlan == null || targetDailyPlan == null) {
        return false;
      }

      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.update,
        'exercise_plans',
        userId: weeklyPlan.userId,
      );

      // 更新日计划完成状态
      final updatedDailyPlan = DailyExercisePlan(
        id: targetDailyPlan.id,
        date: targetDailyPlan.date,
        activities: targetDailyPlan.activities,
        totalCaloriesBurned: targetDailyPlan.totalCaloriesBurned,
        totalDuration: targetDailyPlan.totalDuration,
        warmupInstructions: targetDailyPlan.warmupInstructions,
        cooldownInstructions: targetDailyPlan.cooldownInstructions,
        notes: targetDailyPlan.notes,
        completed: completed,
        completionPercentage: completionPercentage ?? (completed ? 100.0 : 0.0),
      );

      // 更新周计划中的日计划
      final updatedDailyPlans = weeklyPlan.dailyPlans
          .map((dp) => dp.id == planId ? updatedDailyPlan : dp)
          .toList();

      // 计算周计划总完成率
      double totalCompletion = 0.0;
      for (final dp in updatedDailyPlans) {
        totalCompletion += dp.completionPercentage;
      }
      final weeklyCompletionPercentage = totalCompletion / updatedDailyPlans.length;

      // 更新周计划
      final updatedWeeklyPlan = WeeklyExercisePlan(
        id: weeklyPlan.id,
        userId: weeklyPlan.userId,
        name: weeklyPlan.name,
        startDate: weeklyPlan.startDate,
        endDate: weeklyPlan.endDate,
        type: weeklyPlan.type,
        level: weeklyPlan.level,
        dailyPlans: updatedDailyPlans,
        goals: weeklyPlan.goals,
        focusAreas: weeklyPlan.focusAreas,
        totalPlannedCaloriesBurn: weeklyPlan.totalPlannedCaloriesBurn,
        notes: weeklyPlan.notes,
        active: weeklyPlan.active,
        completionPercentage: weeklyCompletionPercentage,
      );

      _plans[weeklyPlan.id] = updatedWeeklyPlan;

      // 发布代理事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataUpdated,
        source: id,
        data: {
          'entityType': 'daily_exercise_plan',
          'entityId': planId,
          'userId': weeklyPlan.userId,
          'field': 'completion',
        },
      ));

      return true;
    } catch (e) {
      if (kDebugMode) {
        print('更新每日计划完成状态失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'updateDailyPlanCompletion',
          'error': e.toString(),
        },
      ));

      return false;
    }
  }

  @override
  Future<List<ExerciseActivity>> searchExerciseActivities(
    ExerciseSearchFilter filter,
  ) async {
    try {
      // 收集所有活动
      List<ExerciseActivity> allActivities = [];
      _activityDatabase.values.forEach((activities) {
        allActivities.addAll(activities);
      });

      // 应用过滤条件
      return allActivities.where((activity) {
        bool match = true;

        // 类型过滤
        if (filter.types != null && filter.types!.isNotEmpty) {
          match = match && filter.types!.contains(activity.type);
        }

        // 强度过滤
        if (filter.intensities != null && filter.intensities!.isNotEmpty) {
          match = match && filter.intensities!.contains(activity.intensity);
        }

        // 经验级别过滤
        if (filter.maxLevel != null) {
          match = match && activity.recommendedLevel.index <= filter.maxLevel!.index;
        }

        // 时长过滤
        if (filter.maxDuration != null) {
          match = match && activity.duration <= filter.maxDuration!;
        }

        // 目标肌肉群过滤
        if (filter.targetMuscleGroups != null && filter.targetMuscleGroups!.isNotEmpty) {
          match = match && filter.targetMuscleGroups!.any((group) => activity.muscleGroups.contains(group));
        }

        // 排除设备过滤
        if (filter.excludedEquipment != null && filter.excludedEquipment!.isNotEmpty && activity.equipment != null) {
          match = match && !filter.excludedEquipment!.any((equip) => activity.equipment!.contains(equip));
        }

        // 中医体质过滤
        if (filter.suitableForBodyType != null) {
          // 简化的体质匹配逻辑，实际应用中需要更复杂的中医理论支持
          match = match && _isSuitableForBodyType(activity, filter.suitableForBodyType!);
        }

        // 健康状况过滤
        if (filter.healthConditions != null && filter.healthConditions!.isNotEmpty && activity.contraindications != null) {
          // 检查是否有任何健康状况与禁忌冲突
          for (final condition in filter.healthConditions!) {
            for (final contraindication in activity.contraindications!) {
              if (contraindication.condition.toLowerCase().contains(condition.toLowerCase())) {
                match = false;
                break;
              }
            }
            if (!match) break;
          }
        }

        return match;
      }).toList();
    } catch (e) {
      if (kDebugMode) {
        print('搜索运动活动失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'searchExerciseActivities',
          'error': e.toString(),
        },
      ));

      return [];
    }
  }

  @override
  Future<List<ExerciseActivity>> getExercisesForBodyType(
    TraditionalChineseBodyType bodyType,
  ) async {
    try {
      // 收集所有活动
      List<ExerciseActivity> allActivities = [];
      _activityDatabase.values.forEach((activities) {
        allActivities.addAll(activities);
      });

      // 筛选适合该体质的活动
      return allActivities.where((activity) => _isSuitableForBodyType(activity, bodyType)).toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取体质运动建议失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getExercisesForBodyType',
          'error': e.toString(),
        },
      ));

      return [];
    }
  }

  @override
  Future<ExerciseProgressReport> generateProgressReport(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.read,
        'exercise_sessions',
        userId: userId,
      );

      final now = DateTime.now();
      final effectiveStartDate = startDate ?? now.subtract(const Duration(days: 30));
      final effectiveEndDate = endDate ?? now;

      // 获取时间范围内的运动会话
      final sessions = await getExerciseSessions(
        userId,
        startDate: effectiveStartDate,
        endDate: effectiveEndDate,
      );

      if (sessions.isEmpty) {
        // 返回空报告
        return ExerciseProgressReport(
          id: const Uuid().v4(),
          userId: userId,
          startDate: effectiveStartDate,
          endDate: effectiveEndDate,
          totalSessionsCompleted: 0,
          totalDuration: 0,
          totalCaloriesBurned: 0,
          exerciseTypeDistribution: {},
          progressMetrics: {},
          summary: '在所选时间段内没有运动记录。',
        );
      }

      // 统计数据
      int totalSessionsCompleted = sessions.where((s) => s.completed).length;
      double totalDuration = 0;
      int totalCaloriesBurned = 0;
      Map<ExerciseType, double> exerciseTypeDistribution = {};

      for (final session in sessions) {
        if (session.completed) {
          totalDuration += session.duration;
          totalCaloriesBurned += session.caloriesBurned;

          // 更新运动类型分布
          exerciseTypeDistribution[session.type] =
              (exerciseTypeDistribution[session.type] ?? 0) + session.duration;
        }
      }

      // 计算进步指标
      Map<String, double> progressMetrics = await _calculateProgressMetrics(userId, sessions);

      // 识别成就
      List<String> achievements = _identifyAchievements(sessions);

      // 识别挑战
      List<String> challenges = _identifyChallenges(sessions);

      // 根据统计数据生成建议
      List<String> recommendations = await _generateRecommendations(
        userId,
        sessions,
        exerciseTypeDistribution,
        progressMetrics,
      );

      // 生成总结
      String summary = _generateReportSummary(
        totalSessionsCompleted,
        totalDuration,
        totalCaloriesBurned,
        exerciseTypeDistribution,
        progressMetrics,
        achievements,
        challenges,
      );

      // 创建报告
      final report = ExerciseProgressReport(
        id: const Uuid().v4(),
        userId: userId,
        startDate: effectiveStartDate,
        endDate: effectiveEndDate,
        totalSessionsCompleted: totalSessionsCompleted,
        totalDuration: totalDuration,
        totalCaloriesBurned: totalCaloriesBurned,
        exerciseTypeDistribution: exerciseTypeDistribution,
        progressMetrics: progressMetrics,
        achievements: achievements,
        challengesIdentified: challenges,
        recommendations: recommendations,
        summary: summary,
      );

      return report;
    } catch (e) {
      if (kDebugMode) {
        print('生成运动进度报告失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'generateProgressReport',
          'error': e.toString(),
        },
      ));

      // 返回基本报告
      return ExerciseProgressReport(
        id: const Uuid().v4(),
        userId: userId,
        startDate: startDate ?? DateTime.now().subtract(const Duration(days: 30)),
        endDate: endDate ?? DateTime.now(),
        totalSessionsCompleted: 0,
        totalDuration: 0,
        totalCaloriesBurned: 0,
        exerciseTypeDistribution: {},
        progressMetrics: {},
        summary: '生成报告时发生错误，请稍后重试。',
      );
    }
  }

  @override
  Future<List<String>> getExerciseRecommendations(
    String userId, {
    List<String>? healthConditions,
    TraditionalChineseBodyType? bodyType,
  }) async {
    try {
      // 获取用户的最新体能评估
      final assessment = await getLatestFitnessAssessment(userId);
      
      // 使用评估中的健康状况和体质（如果没有提供）
      final effectiveHealthConditions = healthConditions ?? assessment?.healthConditions ?? [];
      final effectiveBodyType = bodyType ?? assessment?.bodyType;
      
      final recommendations = <String>[];
      
      // 基于健康状况的建议
      if (effectiveHealthConditions.isNotEmpty) {
        for (final condition in effectiveHealthConditions) {
          recommendations.addAll(_getRecommendationsForHealthCondition(condition));
        }
      }
      
      // 基于体质的建议
      if (effectiveBodyType != null) {
        recommendations.addAll(_getRecommendationsForBodyType(effectiveBodyType));
      }
      
      // 通用建议
      recommendations.addAll([
        '每周至少进行150分钟中等强度有氧运动或75分钟高强度有氧运动',
        '每周至少两天进行全身主要肌肉群的力量训练',
        '适当进行柔韧性训练，提高关节活动度',
        '每天保持活跃，减少久坐时间',
      ]);
      
      return recommendations;
    } catch (e) {
      if (kDebugMode) {
        print('获取运动建议失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getExerciseRecommendations',
          'error': e.toString(),
        },
      ));

      // 返回基本建议
      return [
        '每周至少进行150分钟中等强度有氧运动',
        '每周至少两天进行力量训练',
        '保持规律运动习惯',
        '运动前充分热身，运动后适当拉伸',
      ];
    }
  }

  @override
  Future<WeeklyExercisePlan> generateCustomExercisePlan(
    String userId, {
    ExercisePlanType? planType,
    ExperienceLevel? level,
    int? targetCaloriesBurn,
    List<String>? focusAreas,
    ExerciseFrequency? frequency,
    DateTime? startDate,
    int durationInWeeks = 1,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAccess(
        id,
        SecurityOperationType.create,
        'exercise_plans',
        userId: userId,
      );

      // 获取用户的最新体能评估
      final assessment = await getLatestFitnessAssessment(userId);
      
      // 默认值
      final effectivePlanType = planType ?? ExercisePlanType.generalFitness;
      final effectiveLevel = level ?? (assessment != null ? _suggestExperienceLevel(assessment) : ExperienceLevel.beginner);
      final effectiveTargetCalories = targetCaloriesBurn ?? _suggestTargetCalories(effectivePlanType, assessment);
      final effectiveFocusAreas = focusAreas ?? [];
      final effectiveFrequency = frequency ?? ExerciseFrequency.threeTimesPerWeek;
      final effectiveStartDate = startDate ?? DateTime.now();
      
      // 计算结束日期
      final endDate = DateTime(
        effectiveStartDate.year,
        effectiveStartDate.month,
        effectiveStartDate.day + (durationInWeeks * 7) - 1,
      );
      
      // 生成每日计划
      final dailyPlans = <DailyExercisePlan>[];
      int dayCount = 0;
      int totalCaloriesBurn = 0;
      
      // 根据频率确定运动日
      List<bool> exerciseDays = _getExerciseDaysPattern(effectiveFrequency);
      
      // 生成每一天的计划
      for (int i = 0; i < durationInWeeks * 7; i++) {
        final date = DateTime(
          effectiveStartDate.year,
          effectiveStartDate.month,
          effectiveStartDate.day + i,
        );
        
        // 确定这一天是否为运动日
        final isExerciseDay = exerciseDays[i % 7];
        
        if (isExerciseDay) {
          // 生成运动日计划
          final dailyPlan = await _generateDailyPlan(
            userId,
            date,
            effectivePlanType,
            effectiveLevel,
            assessment?.bodyType,
            assessment?.healthConditions,
            focusAreas: effectiveFocusAreas,
          );
          
          dailyPlans.add(dailyPlan);
          totalCaloriesBurn += dailyPlan.totalCaloriesBurned;
          dayCount++;
        } else {
          // 生成休息日计划
          final restDayPlan = _generateRestDayPlan(userId, date);
          dailyPlans.add(restDayPlan);
        }
      }
      
      // 生成计划目标
      final goals = _generatePlanGoals(
        effectivePlanType,
        totalCaloriesBurn,
        dayCount,
        effectiveFocusAreas,
      );
      
      // 生成计划注释
      final notes = _generatePlanNotes(
        effectivePlanType,
        effectiveLevel,
        assessment?.bodyType,
      );
      
      // 创建周计划
      final weeklyPlan = WeeklyExercisePlan(
        id: const Uuid().v4(),
        userId: userId,
        name: _generatePlanName(effectivePlanType, assessment?.bodyType),
        startDate: effectiveStartDate,
        endDate: endDate,
        type: effectivePlanType,
        level: effectiveLevel,
        dailyPlans: dailyPlans,
        goals: goals,
        focusAreas: effectiveFocusAreas,
        totalPlannedCaloriesBurn: totalCaloriesBurn,
        notes: notes,
        active: true,
        completionPercentage: 0.0,
      );

      return weeklyPlan;
    } catch (e) {
      if (kDebugMode) {
        print('生成自定义锻炼计划失败: $e');
      }

      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'generateCustomExercisePlan',
          'error': e.toString(),
        },
      ));

      rethrow;
    }
  }

  /// 辅助方法
  
  /// 计算运动进步指标
  Future<Map<String, double>> _calculateProgressMetrics(String userId, List<ExerciseSession> sessions) async {
    final metrics = <String, double>{};
    
    if (sessions.isEmpty) {
      return metrics;
    }
    
    // 按时间排序
    sessions.sort((a, b) => a.startTime.compareTo(b.startTime));
    
    // 计算每周运动频率
    final firstSession = sessions.first.startTime;
    final lastSession = sessions.last.startTime;
    final totalWeeks = max(1, lastSession.difference(firstSession).inDays / 7);
    metrics['weeklyFrequency'] = sessions.length / totalWeeks;
    
    // 计算平均强度
    double avgIntensity = 0.0;
    for (final session in sessions) {
      avgIntensity += session.intensity.index;
    }
    metrics['averageIntensity'] = avgIntensity / sessions.length;
    
    // 计算平均持续时间
    double totalDuration = 0.0;
    for (final session in sessions) {
      totalDuration += session.duration;
    }
    metrics['averageDuration'] = totalDuration / sessions.length;
    
    // 计算平均心率和最大心率
    double totalAvgHeartRate = 0.0;
    double maxHR = 0.0;
    int heartRateSessionCount = 0;
    
    for (final session in sessions) {
      if (session.avgHeartRate > 0) {
        totalAvgHeartRate += session.avgHeartRate;
        heartRateSessionCount++;
      }
      
      if (session.maxHeartRate > maxHR) {
        maxHR = session.maxHeartRate;
      }
    }
    
    if (heartRateSessionCount > 0) {
      metrics['averageHeartRate'] = totalAvgHeartRate / heartRateSessionCount;
    }
    
    if (maxHR > 0) {
      metrics['maxHeartRate'] = maxHR;
    }
    
    // 计算趋势
    if (sessions.length >= 4) {
      // 将会话分成前半部分和后半部分
      final midpoint = sessions.length ~/ 2;
      final firstHalf = sessions.sublist(0, midpoint);
      final secondHalf = sessions.sublist(midpoint);
      
      // 计算持续时间趋势
      double firstHalfDuration = 0.0;
      for (final session in firstHalf) {
        firstHalfDuration += session.duration;
      }
      
      double secondHalfDuration = 0.0;
      for (final session in secondHalf) {
        secondHalfDuration += session.duration;
      }
      
      metrics['durationTrend'] = (secondHalfDuration / secondHalf.length) - 
          (firstHalfDuration / firstHalf.length);
      
      // 计算强度趋势
      double firstHalfIntensity = 0.0;
      for (final session in firstHalf) {
        firstHalfIntensity += session.intensity.index;
      }
      
      double secondHalfIntensity = 0.0;
      for (final session in secondHalf) {
        secondHalfIntensity += session.intensity.index;
      }
      
      metrics['intensityTrend'] = (secondHalfIntensity / secondHalf.length) - 
          (firstHalfIntensity / firstHalf.length);
    }
    
    return metrics;
  }
  
  /// 识别运动成就
  List<String> _identifyAchievements(List<ExerciseSession> sessions) {
    final achievements = <String>[];
    
    if (sessions.isEmpty) {
      return achievements;
    }
    
    // 计算总时长
    double totalDuration = 0.0;
    for (final session in sessions) {
      totalDuration += session.duration;
    }
    
    // 运动总时长成就
    if (totalDuration >= 1000) {
      achievements.add('千分钟运动达人：累计运动时间超过1000分钟');
    } else if (totalDuration >= 500) {
      achievements.add('五百分钟挑战者：累计运动时间超过500分钟');
    } else if (totalDuration >= 100) {
      achievements.add('百分钟健将：累计运动时间超过100分钟');
    }
    
    // 连续运动成就
    if (sessions.length >= 10) {
      achievements.add('坚持者：连续记录10次或以上的运动');
    } else if (sessions.length >= 5) {
      achievements.add('习惯养成：连续记录5次或以上的运动');
    }
    
    // 高强度运动成就
    int highIntensitySessions = 0;
    for (final session in sessions) {
      if (session.intensity == ExerciseIntensity.vigorous || 
          session.intensity == ExerciseIntensity.maximal) {
        highIntensitySessions++;
      }
    }
    
    if (highIntensitySessions >= 5) {
      achievements.add('高强度爱好者：完成5次或以上高强度训练');
    }
    
    // 多样性成就
    final exerciseTypes = <ExerciseType>{};
    for (final session in sessions) {
      exerciseTypes.add(session.type);
    }
    
    if (exerciseTypes.length >= 5) {
      achievements.add('多面手：尝试5种或以上不同类型的运动');
    } else if (exerciseTypes.length >= 3) {
      achievements.add('探索者：尝试3种或以上不同类型的运动');
    }
    
    return achievements;
  }
  
  /// 识别运动挑战
  List<String> _identifyChallenges(List<ExerciseSession> sessions) {
    final challenges = <String>[];
    
    if (sessions.isEmpty) {
      return ['尚未开始任何运动记录'];
    }
    
    // 按时间排序
    sessions.sort((a, b) => a.startTime.compareTo(b.startTime));
    
    // 检查运动频率
    final firstSession = sessions.first.startTime;
    final lastSession = sessions.last.startTime;
    final daysDifference = lastSession.difference(firstSession).inDays;
    
    if (daysDifference > 0) {
      final frequency = sessions.length / daysDifference;
      
      if (frequency < 0.2) { // 平均每5天不到1次
        challenges.add('运动频率较低，建议增加运动次数');
      }
    }
    
    // 检查最近是否运动
    final now = DateTime.now();
    final daysSinceLastSession = now.difference(lastSession).inDays;
    
    if (daysSinceLastSession > 7) {
      challenges.add('已有${daysSinceLastSession}天未进行运动，建议尽快恢复运动习惯');
    }
    
    // 检查运动强度
    int lowIntensitySessions = 0;
    for (final session in sessions) {
      if (session.intensity == ExerciseIntensity.veryLight || 
          session.intensity == ExerciseIntensity.light) {
        lowIntensitySessions++;
      }
    }
    
    if (lowIntensitySessions == sessions.length && sessions.length > 3) {
      challenges.add('所有运动均为低强度，可以尝试适当增加运动强度');
    }
    
    // 检查运动类型多样性
    final exerciseTypes = <ExerciseType>{};
    for (final session in sessions) {
      exerciseTypes.add(session.type);
    }
    
    if (exerciseTypes.length == 1 && sessions.length > 5) {
      challenges.add('运动类型单一，建议尝试不同种类的运动以全面锻炼身体');
    }
    
    // 检查运动时长
    double avgDuration = 0.0;
    for (final session in sessions) {
      avgDuration += session.duration;
    }
    avgDuration /= sessions.length;
    
    if (avgDuration < 20 && sessions.length > 3) {
      challenges.add('平均运动时长较短，建议适当延长单次运动时间');
    }
    
    return challenges;
  }
  
  /// 生成运动建议
  Future<List<String>> _generateRecommendations(
    String userId,
    List<ExerciseSession> sessions,
    Map<ExerciseType, double> typeDistribution,
    Map<String, double> metrics,
  ) async {
    final recommendations = <String>[];
    
    // 获取用户的最新体能评估
    final assessment = await getLatestFitnessAssessment(userId);
    
    // 根据运动类型分布提出建议
    if (typeDistribution.isEmpty) {
      recommendations.add('尝试进行有氧运动，如快走、慢跑或骑自行车，改善心肺功能');
      recommendations.add('加入力量训练，如俯卧撑、深蹲，增强肌肉力量和耐力');
    } else {
      // 检查是否缺少特定类型的运动
      bool hasAerobic = typeDistribution.containsKey(ExerciseType.aerobic);
      bool hasStrength = typeDistribution.containsKey(ExerciseType.strength);
      bool hasFlexibility = typeDistribution.containsKey(ExerciseType.flexibility);
      bool hasBalance = typeDistribution.containsKey(ExerciseType.balance);
      
      if (!hasAerobic) {
        recommendations.add('增加有氧运动，如快走、慢跑或骑自行车，改善心肺功能');
      }
      
      if (!hasStrength) {
        recommendations.add('加入力量训练，如俯卧撑、深蹲，增强肌肉力量和耐力');
      }
      
      if (!hasFlexibility) {
        recommendations.add('加入柔韧性训练，如瑜伽或拉伸，提高关节灵活性和预防受伤');
      }
      
      if (!hasBalance && (assessment?.age ?? 0) > 50) {
        recommendations.add('加入平衡训练，如太极或单腿站立，提高稳定性和预防跌倒');
      }
    }
    
    // 根据运动频率提出建议
    final frequency = metrics['weeklyFrequency'] ?? 0.0;
    if (frequency < 3) {
      recommendations.add('尝试增加每周运动次数，逐步达到每周3-5次');
    } else if (frequency > 6) {
      recommendations.add('注意合理安排休息日，避免过度训练');
    }
    
    // 根据运动强度提出建议
    final intensity = metrics['averageIntensity'] ?? 0.0;
    if (intensity < 1.5) { // 大多是很轻或轻度
      recommendations.add('适当增加运动强度，尝试进入中等强度区间（呼吸稍微急促但能正常交谈）');
    } else if (intensity > 3.5) { // 大多是剧烈或极限
      recommendations.add('注意监控身体反应，避免长期高强度训练导致疲劳或受伤');
    }
    
    // 根据体质提出建议
    if (assessment?.bodyType != null) {
      recommendations.addAll(_getRecommendationsForBodyType(assessment!.bodyType!));
    }
    
    // 根据健康状况提出建议
    if (assessment?.healthConditions != null && assessment!.healthConditions!.isNotEmpty) {
      for (final condition in assessment.healthConditions!) {
        recommendations.addAll(_getRecommendationsForHealthCondition(condition));
      }
    }
    
    // 通用建议
    recommendations.add('保持运动前的充分热身和运动后的拉伸，减少受伤风险');
    recommendations.add('关注运动中的姿势和技术，避免错误姿势导致伤害');
    recommendations.add('逐渐增加运动量，避免突然大幅提高强度或时长');
    
    return recommendations;
  }
  
  /// 生成报告总结
  String _generateReportSummary(
    int totalSessionsCompleted,
    double totalDuration,
    int totalCaloriesBurned,
    Map<ExerciseType, double> exerciseTypeDistribution,
    Map<String, double> progressMetrics,
    List<String> achievements,
    List<String> challenges,
  ) {
    final buffer = StringBuffer();
    
    buffer.writeln('在此期间，您共完成了$totalSessionsCompleted次运动，总时长${totalDuration.toStringAsFixed(0)}分钟，消耗约${totalCaloriesBurned}卡路里。');
    
    // 添加运动类型分布
    if (exerciseTypeDistribution.isNotEmpty) {
      buffer.writeln('您的运动类型分布为：');
      
      // 将类型按时间排序
      final sortedTypes = exerciseTypeDistribution.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
      
      for (final entry in sortedTypes.take(3)) {
        final typeStr = _exerciseTypeToString(entry.key);
        final percentage = (entry.value / totalDuration * 100).toStringAsFixed(1);
        buffer.writeln('- $typeStr：占总时间的$percentage%');
      }
    }
    
    // 添加进步趋势
    if (progressMetrics.containsKey('durationTrend')) {
      final trend = progressMetrics['durationTrend']!;
      if (trend > 5) {
        buffer.writeln('您的运动时长呈明显上升趋势，平均每次增加${trend.toStringAsFixed(1)}分钟。');
      } else if (trend < -5) {
        buffer.writeln('您的运动时长呈下降趋势，平均每次减少${(-trend).toStringAsFixed(1)}分钟。');
      }
    }
    
    if (progressMetrics.containsKey('intensityTrend')) {
      final trend = progressMetrics['intensityTrend']!;
      if (trend > 0.5) {
        buffer.writeln('您的运动强度呈上升趋势，正在逐步挑战自己。');
      }
    }
    
    // 添加成就
    if (achievements.isNotEmpty) {
      buffer.writeln('值得表扬的是：');
      for (final achievement in achievements.take(2)) {
        buffer.writeln('- $achievement');
      }
    }
    
    // 添加挑战
    if (challenges.isNotEmpty) {
      buffer.writeln('需要注意的是：');
      for (final challenge in challenges.take(2)) {
        buffer.writeln('- $challenge');
      }
    }
    
    // 总结
    buffer.writeln('继续保持规律的运动习惯，根据建议调整运动计划，将帮助您获得更好的健康状态。');
    
    return buffer.toString();
  }
  
  /// 判断运动是否适合特定体质
  bool _isSuitableForBodyType(ExerciseActivity activity, TraditionalChineseBodyType bodyType) {
    // 这是一个简化的匹配逻辑，实际应用中需要更复杂的中医理论支持
    switch (bodyType) {
      case TraditionalChineseBodyType.coldConstitution:
        // 寒性体质适合温热性运动
        return activity.tcmProperties.containsKey('effects') &&
            (activity.tcmProperties['effects'] as List).any((effect) => 
                effect.toString().contains('温') || 
                effect.toString().contains('热') ||
                effect.toString().contains('阳'));
        
      case TraditionalChineseBodyType.hotConstitution:
        // 热性体质适合凉性运动
        return activity.tcmProperties.containsKey('effects') &&
            (activity.tcmProperties['effects'] as List).any((effect) => 
                effect.toString().contains('凉') || 
                effect.toString().contains('清') ||
                effect.toString().contains('阴'));
        
      case TraditionalChineseBodyType.dampnessConstitution:
        // 湿性体质适合祛湿运动
        return activity.tcmProperties.containsKey('effects') &&
            (activity.tcmProperties['effects'] as List).any((effect) => 
                effect.toString().contains('燥') || 
                effect.toString().contains('祛湿') ||
                effect.toString().contains('健脾'));
        
      case TraditionalChineseBodyType.dryConstitution:
        // 燥性体质适合滋润运动
        return activity.tcmProperties.containsKey('effects') &&
            (activity.tcmProperties['effects'] as List).any((effect) => 
                effect.toString().contains('润') || 
                effect.toString().contains('滋') ||
                effect.toString().contains('阴'));
        
      default:
        // 默认匹配
        return true;
    }
  }
  
  /// 获取特定健康状况的运动建议
  List<String> _getRecommendationsForHealthCondition(String condition) {
    switch (condition.toLowerCase()) {
      case '高血压':
        return [
          '以中低强度有氧运动为主，每周进行150分钟中等强度活动',
          '避免高强度运动和重量训练，以防血压突然升高',
          '运动前后监测血压，了解身体反应',
          '避免憋气动作，保持自然呼吸',
        ];
        
      case '糖尿病':
        return [
          '结合有氧运动和阻力训练，帮助控制血糖',
          '每天进行至少30分钟中等强度活动',
          '运动前后监测血糖，避免低血糖',
          '运动时携带含糖食物以防低血糖',
        ];
        
      case '关节炎':
        return [
          '选择低冲击性运动，如游泳、骑自行车、椭圆机',
          '避免跳跃和快速转向等动作',
          '关注关节灵活性训练和周围肌肉力量',
          '疼痛时减少运动强度，不要忍痛锻炼',
        ];
        
      case '心脏病':
        return [
          '在医生指导下进行运动，注重心率监测',
          '以缓慢进阶的方式增加运动量',
          '注意运动中的不适症状，如胸痛、头晕、呼吸急促',
          '避免突然剧烈运动和极端温度环境',
        ];
        
      case '骨质疏松':
        return [
          '加入负重运动，如快走、爬楼梯，促进骨密度增加',
          '加强平衡训练，减少跌倒风险',
          '避免高冲击和扭转动作，防止骨折',
          '逐渐增加运动强度，避免过度负荷',
        ];
        
      case '肥胖':
        return [
          '结合有氧运动和力量训练，最大化热量消耗',
          '每周至少进行150-300分钟中等强度活动',
          '选择适合体重的低冲击运动，减轻关节压力',
          '逐步增加运动时间和强度，避免受伤',
        ];
        
      default:
        return [
          '咨询医疗专业人士获取针对您特定健康状况的运动建议',
          '根据身体感受调整运动强度，避免过度劳累',
          '注意监测相关症状和体征，确认运动安全性',
        ];
    }
  }
  
  /// 获取特定体质的运动建议
  List<String> _getRecommendationsForBodyType(TraditionalChineseBodyType bodyType) {
    switch (bodyType) {
      case TraditionalChineseBodyType.coldConstitution:
        return [
          '选择能够温阳散寒的运动，如快走、慢跑、太极和瑜伽中的阳性动作',
          '运动时注意保暖，避免在寒冷环境中长时间锻炼',
          '运动后避免立即饮用冷饮，以防寒气入侵',
          '可以在温暖的室内进行运动，如瑜伽或普拉提',
        ];
        
      case TraditionalChineseBodyType.hotConstitution:
        return [
          '选择可以清热泻火的运动，如游泳、慢跑、瑜伽中的阴性动作',
          '避免在炎热环境中进行高强度运动',
          '运动时补充足够的水分，防止体内热量积聚',
          '可以在清晨或傍晚较凉爽时段进行户外运动',
        ];
        
      case TraditionalChineseBodyType.dampnessConstitution:
        return [
          '选择有助于祛湿健脾的运动，如快走、爬楼梯、太极',
          '避免在潮湿环境中长时间运动',
          '运动后及时更换干燥衣物，避免湿气停留',
          '可以进行强度适中的有氧运动，促进水分代谢',
        ];
        
      case TraditionalChineseBodyType.deficiencyConstitution:
        return [
          '选择温和滋补的运动，如太极、八段锦、缓和瑜伽',
          '避免过度消耗能量的高强度运动',
          '运动时注意量力而行，循序渐进地增加运动量',
          '可以结合呼吸调息，增强内气',
        ];
        
      case TraditionalChineseBodyType.dryConstitution:
        return [
          '选择可以滋阴润燥的运动，如游泳、瑜伽中的柔和动作',
          '避免大量出汗的剧烈运动，防止津液过度消耗',
          '运动时补充足够的水分，保持体内湿度',
          '可以在湿度适宜的环境中进行运动',
        ];
        
      default:
        return [
          '根据个人体质特点和季节变化选择适宜的运动',
          '注意运动与休息的平衡，避免过度消耗',
          '结合中医理论，选择适合自身阴阳平衡的运动方式',
        ];
    }
  }
  
  /// 根据体能评估建议经验级别
  ExperienceLevel _suggestExperienceLevel(FitnessAssessment assessment) {
    // 这是一个简化的建议逻辑，实际应用中需要更复杂的评估
    
    // 如果用户有测试数据，根据测试评估
    if (assessment.strengthTests != null || 
        assessment.enduranceTests != null || 
        assessment.flexibilityTests != null) {
      // 检查各项测试成绩
      int advancedCount = 0;
      int intermediateCount = 0;
      int beginnerCount = 0;
      
      // 分析力量测试
      if (assessment.strengthTests != null) {
        for (final score in assessment.strengthTests!.values) {
          if (score > 80) {
            advancedCount++;
          } else if (score > 50) {
            intermediateCount++;
          } else {
            beginnerCount++;
          }
        }
      }
      
      // 分析耐力测试
      if (assessment.enduranceTests != null) {
        for (final score in assessment.enduranceTests!.values) {
          if (score > 80) {
            advancedCount++;
          } else if (score > 50) {
            intermediateCount++;
          } else {
            beginnerCount++;
          }
        }
      }
      
      // 决定级别
      if (advancedCount > (beginnerCount + intermediateCount)) {
        return ExperienceLevel.advanced;
      } else if (intermediateCount > beginnerCount) {
        return ExperienceLevel.intermediate;
      } else {
        return ExperienceLevel.beginner;
      }
    }
    
    // 如果没有测试数据，根据其他因素估计
    if (assessment.age != null) {
      // 年龄因素
      if (assessment.age > 65) {
        return ExperienceLevel.beginner; // 老年人默认从初级开始
      }
    }
    
    // 根据BMI估计
    if (assessment.bmi > 30 || assessment.bmi < 18.5) {
      return ExperienceLevel.beginner; // 体重过重或过轻者从初级开始
    }
    
    // 默认返回初级
    return ExperienceLevel.beginner;
  }
  
  /// 根据计划类型和体能评估建议目标热量消耗
  int _suggestTargetCalories(ExercisePlanType planType, FitnessAssessment? assessment) {
    // 这是一个简化的建议逻辑，实际应用中需要更复杂的评估
    
    // 基础每周目标热量消耗
    int baseWeeklyTarget = 1500; // 约300大卡/天
    
    // 根据计划类型调整
    switch (planType) {
      case ExercisePlanType.weightLoss:
        baseWeeklyTarget = 2500; // 约500大卡/天
        break;
      case ExercisePlanType.muscleGain:
        baseWeeklyTarget = 2000; // 约400大卡/天
        break;
      case ExercisePlanType.enduranceBuilding:
        baseWeeklyTarget = 3000; // 约600大卡/天
        break;
      case ExercisePlanType.generalFitness:
        baseWeeklyTarget = 1500; // 约300大卡/天
        break;
      default:
        baseWeeklyTarget = 1500; // 约300大卡/天
    }
    
    // 根据体能评估调整
    if (assessment != null) {
      // 根据年龄调整
      if (assessment.age != null) {
        if (assessment.age > 60) {
          baseWeeklyTarget = (baseWeeklyTarget * 0.8).toInt(); // 老年人降低目标
        } else if (assessment.age < 30) {
          baseWeeklyTarget = (baseWeeklyTarget * 1.2).toInt(); // 年轻人提高目标
        }
      }
      
      // 根据BMI调整
      if (assessment.bmi > 30) {
        baseWeeklyTarget = (baseWeeklyTarget * 0.9).toInt(); // 肥胖者降低强度
      } else if (assessment.bmi < 18.5) {
        baseWeeklyTarget = (baseWeeklyTarget * 0.85).toInt(); // 体重过轻者降低强度
      }
      
      // 根据健康状况调整
      if (assessment.healthConditions != null && assessment.healthConditions!.isNotEmpty) {
        // 如果有健康问题，适当降低目标
        baseWeeklyTarget = (baseWeeklyTarget * 0.85).toInt();
      }
    }
    
    return baseWeeklyTarget;
  }
  
  /// 获取根据频率的运动日模式
  List<bool> _getExerciseDaysPattern(ExerciseFrequency frequency) {
    switch (frequency) {
      case ExerciseFrequency.daily:
        return [true, true, true, true, true, true, true]; // 每天
        
      case ExerciseFrequency.alternateDays:
        return [true, false, true, false, true, false, true]; // 隔天
        
      case ExerciseFrequency.threeTimesPerWeek:
        return [true, false, true, false, true, false, false]; // 每周三次
        
      case ExerciseFrequency.fourTimesPerWeek:
        return [true, false, true, false, true, false, true]; // 每周四次
        
      case ExerciseFrequency.fiveTimesPerWeek:
        return [true, true, true, false, true, true, false]; // 每周五次
        
      case ExerciseFrequency.weekends:
        return [false, false, false, false, false, true, true]; // 仅周末
        
      case ExerciseFrequency.customSchedule:
        // 默认每周三次
        return [true, false, true, false, true, false, false];
        
      default:
        return [true, false, true, false, true, false, false]; // 默认每周三次
    }
  }
  
  /// 生成每日运动计划
  Future<DailyExercisePlan> _generateDailyPlan(
    String userId,
    DateTime date,
    ExercisePlanType planType,
    ExperienceLevel level,
    TraditionalChineseBodyType? bodyType,
    List<String>? healthConditions, {
    List<String>? focusAreas,
  }) async {
    try {
      // 合计所有活动
      List<ExerciseActivity> allActivities = [];
      _activityDatabase.values.forEach((activities) {
        allActivities.addAll(activities);
      });
      
      // 创建适当的过滤器
      final filter = ExerciseSearchFilter(
        maxLevel: level,
        suitableForBodyType: bodyType,
        healthConditions: healthConditions,
      );
      
      // 根据计划类型设置过滤器
      switch (planType) {
        case ExercisePlanType.weightLoss:
          filter.types = [ExerciseType.aerobic, ExerciseType.hiit];
          break;
        case ExercisePlanType.muscleGain:
          filter.types = [ExerciseType.strength, ExerciseType.functional];
          break;
        case ExercisePlanType.enduranceBuilding:
          filter.types = [ExerciseType.aerobic];
          break;
        case ExercisePlanType.flexibility:
          filter.types = [ExerciseType.flexibility, ExerciseType.balance];
          break;
        case ExercisePlanType.tcmPractice:
          filter.types = [ExerciseType.traditional, ExerciseType.balance];
          break;
        default:
          // 一般健身计划包含多种类型
          filter.types = null;
      }
      
      // 如果有重点区域，添加到过滤器
      if (focusAreas != null && focusAreas.isNotEmpty) {
        filter.targetMuscleGroups = focusAreas;
      }
      
      // 搜索匹配的活动
      final matchedActivities = await searchExerciseActivities(filter);
      
      if (matchedActivities.isEmpty) {
        // 如果没有匹配的活动，降低标准后再次搜索
        filter.maxLevel = null;
        filter.targetMuscleGroups = null;
        final fallbackActivities = await searchExerciseActivities(filter);
        
        if (fallbackActivities.isEmpty) {
          // 如果仍然没有匹配的活动，使用所有活动
          matchedActivities.addAll(allActivities.take(3));
        } else {
          matchedActivities.addAll(fallbackActivities.take(3));
        }
      }
      
      // 根据日期确定重点（简单的循环模式）
      final dayOfWeek = date.weekday;
      List<ExerciseActivity> selectedActivities = [];
      
      switch (planType) {
        case ExercisePlanType.generalFitness:
          // 一般健身：不同日期安排不同类型的训练
          if (dayOfWeek == 1 || dayOfWeek == 4) { // 周一、周四
            selectedActivities = matchedActivities
                .where((a) => a.type == ExerciseType.aerobic)
                .take(2)
                .toList();
          } else if (dayOfWeek == 2 || dayOfWeek == 5) { // 周二、周五
            selectedActivities = matchedActivities
                .where((a) => a.type == ExerciseType.strength)
                .take(2)
                .toList();
          } else { // 周三、周六、周日
            selectedActivities = matchedActivities
                .where((a) => a.type == ExerciseType.flexibility || 
                          a.type == ExerciseType.balance)
                .take(2)
                .toList();
          }
          break;
          
        case ExercisePlanType.weightLoss:
          // 减肥：以有氧和HIIT为主
          if (dayOfWeek % 2 == 0) { // 偶数日
            selectedActivities = matchedActivities
                .where((a) => a.type == ExerciseType.hiit)
                .take(1)
                .toList();
            selectedActivities.addAll(matchedActivities
                .where((a) => a.type == ExerciseType.aerobic)
                .take(1));
          } else { // 奇数日
            selectedActivities = matchedActivities
                .where((a) => a.type == ExerciseType.aerobic)
                .take(2)
                .toList();
          }
          break;
          
        case ExercisePlanType.muscleGain:
          // 增肌：分部位训练
          if (dayOfWeek == 1 || dayOfWeek == 5) { // 周一、周五
            selectedActivities = matchedActivities
                .where((a) => a.muscleGroups.contains('胸部') || 
                          a.muscleGroups.contains('肩部') ||
                          a.muscleGroups.contains('三头肌'))
                .take(2)
                .toList();
          } else if (dayOfWeek == 2 || dayOfWeek == 6) { // 周二、周六
            selectedActivities = matchedActivities
                .where((a) => a.muscleGroups.contains('背部') || 
                          a.muscleGroups.contains('二头肌'))
                .take(2)
                .toList();
          } else { // 其他日子
            selectedActivities = matchedActivities
                .where((a) => a.muscleGroups.contains('腿部') || 
                          a.muscleGroups.contains('臀部') ||
                          a.muscleGroups.contains('核心'))
                .take(2)
                .toList();
          }
          break;
          
        default:
          // 选择2-3个最匹配的活动
          selectedActivities = matchedActivities.take(3).toList();
      }
      
      // 如果选择的活动不足，添加一些备选活动
      if (selectedActivities.isEmpty || selectedActivities.length < 2) {
        // 添加一些基础活动填充
        selectedActivities.addAll(matchedActivities.take(2 - selectedActivities.length));
      }
      
      // 添加热身和冷却说明
      String? warmupInstructions;
      String? cooldownInstructions;
      
      if (level == ExperienceLevel.beginner) {
        warmupInstructions = '进行5-10分钟的轻度有氧活动（如快走、慢跑或原地踏步），然后进行基本的关节活动度练习。';
        cooldownInstructions = '进行5-10分钟的轻柔拉伸，包括四肢和躯干的主要肌肉群，每个拉伸动作保持15-30秒。';
      } else {
        warmupInstructions = '进行10分钟的热身活动，包括轻度有氧和动态拉伸，为主要运动做准备。';
        cooldownInstructions = '进行10-15分钟的拉伸放松，注意拉伸运动中使用的主要肌肉群。';
      }
      
      // 计算总热量消耗和总时长
      int totalCalories = 0;
      double totalDuration = 0;
      
      for (final activity in selectedActivities) {
        totalCalories += (activity.caloriesPerMinute * activity.duration).toInt();
        totalDuration += activity.duration;
      }
      
      // 创建每日计划
      return DailyExercisePlan(
        id: const Uuid().v4(),
        date: date,
        activities: selectedActivities,
        totalCaloriesBurned: totalCalories,
        totalDuration: totalDuration,
        warmupInstructions: warmupInstructions,
        cooldownInstructions: cooldownInstructions,
        notes: _getDailyExerciseNotes(planType, date, bodyType),
        completed: false,
        completionPercentage: 0.0,
      );
    } catch (e) {
      if (kDebugMode) {
        print('生成每日运动计划失败: $e');
      }
      
      // 返回一个简单的默认计划
      return _generateDefaultDailyPlan(userId, date);
    }
  }
  
  /// 获取每日运动注释
  String _getDailyExerciseNotes(ExercisePlanType planType, DateTime date, TraditionalChineseBodyType? bodyType) {
    // 根据星期几添加特定的说明
    final dayOfWeek = date.weekday;
    final dayNames = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    String notes = '${dayNames[dayOfWeek]}训练：';
    
    switch (planType) {
      case ExercisePlanType.weightLoss:
        notes += '专注于消耗热量和提高代谢率。';
        break;
      case ExercisePlanType.muscleGain:
        switch (dayOfWeek) {
          case 1:
          case 5:
            notes += '专注于上肢推力训练。';
            break;
          case 2:
          case 6:
            notes += '专注于上肢拉力训练。';
            break;
          default:
            notes += '专注于下肢和核心训练。';
        }
        break;
      case ExercisePlanType.enduranceBuilding:
        notes += '专注于心肺功能提升和耐力增强。';
        break;
      case ExercisePlanType.flexibility:
        notes += '专注于提高关节灵活度和肌肉柔韧性。';
        break;
      default:
        notes += '全面性训练，平衡发展各项体能素质。';
    }
    
    // 根据体质添加中医建议
    if (bodyType != null) {
      switch (bodyType) {
        case TraditionalChineseBodyType.coldConstitution:
          notes += '注意保持身体温暖，特别是颈部和腹部。训练后可饮用姜茶温补。';
          break;
        case TraditionalChineseBodyType.hotConstitution:
          notes += '避免过度出汗，训练后可饮用菊花茶或绿豆水清热。';
          break;
        case TraditionalChineseBodyType.dampnessConstitution:
          notes += '训练后及时更换干爽衣物，避免湿气滞留。';
          break;
        default:
          break;
      }
    }
    
    return notes;
  }
  
  /// 生成默认每日计划
  DailyExercisePlan _generateDefaultDailyPlan(String userId, DateTime date) {
    // 创建基础活动
    final walkingActivity = ExerciseActivity(
      id: const Uuid().v4(),
      name: '步行',
      type: ExerciseType.aerobic,
      intensity: ExerciseIntensity.light,
      duration: 30,
      caloriesPerMinute: 5,
      muscleGroups: ['腿部', '核心'],
      recommendedLevel: ExperienceLevel.beginner,
      instructions: '保持适中速度，手臂自然摆动。',
      tcmProperties: {
        'effects': ['行气活血', '舒筋活络'],
      },
    );
    
    final stretchingActivity = ExerciseActivity(
      id: const Uuid().v4(),
      name: '基础伸展',
      type: ExerciseType.flexibility,
      intensity: ExerciseIntensity.light,
      duration: 15,
      caloriesPerMinute: 3,
      muscleGroups: ['全身'],
      recommendedLevel: ExperienceLevel.beginner,
      instructions: '进行全身主要肌肉群的拉伸，每个动作保持15-30秒。',
      tcmProperties: {
        'effects': ['舒展筋络', '放松身心'],
      },
    );
    
    // 计算总热量消耗和总时长
    final totalCalories = (walkingActivity.caloriesPerMinute * walkingActivity.duration) +
        (stretchingActivity.caloriesPerMinute * stretchingActivity.duration);
    final totalDuration = walkingActivity.duration + stretchingActivity.duration;
    
    return DailyExercisePlan(
      id: const Uuid().v4(),
      date: date,
      activities: [walkingActivity, stretchingActivity],
      totalCaloriesBurned: totalCalories.toInt(),
      totalDuration: totalDuration,
      warmupInstructions: '进行5分钟的轻度活动，如原地踏步或缓慢扭动关节。',
      cooldownInstructions: '进行5分钟的轻柔拉伸，放松使用过的肌肉群。',
      notes: '这是一个基础训练计划，适合初学者和恢复期训练。根据个人感受调整强度和时长。',
      completed: false,
      completionPercentage: 0.0,
    );
  }
  
  /// 生成休息日计划
  DailyExercisePlan _generateRestDayPlan(String userId, DateTime date) {
    // 创建一个轻松的休息日计划，包含简单的伸展和放松活动
    final stretchingActivity = ExerciseActivity(
      id: const Uuid().v4(),
      name: '轻松伸展',
      type: ExerciseType.flexibility,
      intensity: ExerciseIntensity.veryLight,
      duration: 15,
      caloriesPerMinute: 2,
      muscleGroups: ['全身'],
      recommendedLevel: ExperienceLevel.beginner,
      instructions: '进行全身放松的伸展动作，每个动作保持15-30秒。',
      tcmProperties: {
        'effects': ['放松身心', '舒展筋络'],
      },
    );
    
    final walkingActivity = ExerciseActivity(
      id: const Uuid().v4(),
      name: '轻松散步',
      type: ExerciseType.aerobic,
      intensity: ExerciseIntensity.veryLight,
      duration: 20,
      caloriesPerMinute: 3,
      muscleGroups: ['腿部', '核心'],
      recommendedLevel: ExperienceLevel.beginner,
      instructions: '进行轻松的散步，呼吸自然，不需要刻意加快速度。',
      tcmProperties: {
        'effects': ['行气活血', '舒畅心情'],
      },
    );
    
    // 计算总热量消耗和总时长
    final totalCalories = (stretchingActivity.caloriesPerMinute * stretchingActivity.duration) +
        (walkingActivity.caloriesPerMinute * walkingActivity.duration);
    final totalDuration = stretchingActivity.duration + walkingActivity.duration;
    
    return DailyExercisePlan(
      id: const Uuid().v4(),
      date: date,
      activities: [stretchingActivity, walkingActivity],
      totalCaloriesBurned: totalCalories.toInt(),
      totalDuration: totalDuration,
      warmupInstructions: null,
      cooldownInstructions: null,
      notes: '休息日进行轻松的伸展和放松活动，帮助恢复和减轻肌肉疲劳。避免高强度训练。',
      completed: false,
      completionPercentage: 0.0,
    );
  }
  
  /// 生成计划目标
  Map<String, dynamic> _generatePlanGoals(
    ExercisePlanType planType,
    int totalCaloriesBurn,
    int dayCount,
    List<String>? focusAreas,
  ) {
    final goals = <String, dynamic>{};
    
    // 设置热量消耗目标
    goals['totalCaloriesBurn'] = totalCaloriesBurn;
    
    // 设置频率目标
    goals['sessionsPerWeek'] = dayCount / 7 * 7; // 转换为每周次数
    
    // 根据计划类型设置特定目标
    switch (planType) {
      case ExercisePlanType.weightLoss:
        goals['weightLossTarget'] = 0.5; // 目标每周减重0.5kg
        goals['primaryFocus'] = '通过有氧运动和适量力量训练创造热量赤字';
        break;
        
      case ExercisePlanType.muscleGain:
        goals['strengthIncreaseTarget'] = 10; // 目标力量提升10%
        goals['primaryFocus'] = '通过渐进式负重训练增加肌肉力量和体积';
        break;
        
      case ExercisePlanType.enduranceBuilding:
        goals['enduranceIncreaseTarget'] = 15; // 目标耐力提升15%
        goals['primaryFocus'] = '通过持续性有氧运动提高心肺功能和耐力';
        break;
        
      case ExercisePlanType.flexibility:
        goals['flexibilityIncreaseTarget'] = 20; // 目标柔韧性提升20%
        goals['primaryFocus'] = '通过拉伸和柔韧性训练增加关节活动范围';
        break;
        
      case ExercisePlanType.tcmPractice:
        goals['balanceImprovement'] = true;
        goals['primaryFocus'] = '通过传统中医运动调和阴阳，增强气血流通';
        break;
        
      default:
        goals['overallFitnessImprovement'] = true;
        goals['primaryFocus'] = '通过多样化运动提升整体健康水平';
        break;
    }
    
    // 添加重点区域
    if (focusAreas != null && focusAreas.isNotEmpty) {
      goals['focusAreas'] = focusAreas;
    }
    
    return goals;
  }
  
  /// 生成计划注释
  List<String> _generatePlanNotes(
    ExercisePlanType planType,
    ExperienceLevel level,
    TraditionalChineseBodyType? bodyType,
  ) {
    final notes = <String>[];
    
    // 通用注释
    notes.add('运动前进行5-10分钟热身，运动后进行5-10分钟拉伸');
    notes.add('注意保持水分摄入，特别是在高强度运动时');
    notes.add('保持正确的运动姿势，避免受伤');
    
    // 根据经验级别添加注释
    switch (level) {
      case ExperienceLevel.beginner:
        notes.add('循序渐进地增加运动强度和时长，不要急于求成');
        notes.add('如感到不适，立即停止运动并休息');
        notes.add('重点关注运动的正确形式和技术');
        break;
        
      case ExperienceLevel.intermediate:
        notes.add('可尝试增加运动强度或时长，但注意在舒适范围内');
        notes.add('适当引入间歇训练，提高训练效果');
        notes.add('关注运动计划的多样性，全面发展各项能力');
        break;
        
      case ExperienceLevel.advanced:
        notes.add('可考虑分阶段训练，如力量、速度和爆发力的针对性发展');
        notes.add('注意周期性调整训练强度，避免平台期');
        notes.add('加强对特定肌肉群的针对性训练');
        break;
        
      default:
        break;
    }
    
    // 根据计划类型添加注释
    switch (planType) {
      case ExercisePlanType.weightLoss:
        notes.add('配合合理的饮食计划，创造热量赤字');
        notes.add('高强度间歇训练特别有效于脂肪消耗');
        notes.add('保持较高的非运动活动量，如多走路、爬楼梯等');
        break;
        
      case ExercisePlanType.muscleGain:
        notes.add('确保充足的蛋白质摄入，支持肌肉生长');
        notes.add('保证足够的休息和恢复时间，尤其是力量训练后');
        notes.add('渐进式增加负重，避免长期使用相同重量');
        break;
        
      case ExercisePlanType.flexibility:
        notes.add('伸展动作保持舒适的拉伸感，不要过度拉伸导致疼痛');
        notes.add('每天花少量时间进行柔韧性训练，效果好于一次大量训练');
        notes.add('结合动态和静态拉伸，全面提高柔韧性');
        break;
        
      default:
        break;
    }
    
    // 根据体质添加中医建议
    if (bodyType != null) {
      notes.addAll(_getNotesForBodyType(bodyType));
    }
    
    return notes;
  }
  
  /// 获取特定体质的注释
  List<String> _getNotesForBodyType(TraditionalChineseBodyType bodyType) {
    switch (bodyType) {
      case TraditionalChineseBodyType.coldConstitution:
        return [
          '寒性体质应在运动前充分热身，避免着凉',
          '运动后注意保暖，特别是颈部和腹部',
          '可在运动前适量饮用姜茶，帮助提升阳气',
        ];
        
      case TraditionalChineseBodyType.hotConstitution:
        return [
          '热性体质应避免在炎热环境中进行高强度运动',
          '运动时注意补充凉性饮品，如菊花茶、绿豆水',
          '避免长时间暴露在阳光下运动',
        ];
        
      case TraditionalChineseBodyType.dampnessConstitution:
        return [
          '湿性体质应避免在潮湿环境中长时间运动',
          '运动后及时更换干爽衣物，防止湿气侵袭',
          '可在运动前服用薏米水或陈皮茶，有助祛湿',
        ];
        
      default:
        return [
          '根据个人体质特点和季节变化调整运动方式和强度',
          '结合中医养生原则，达到运动与调养的双重效果',
        ];
    }
  }
  
  /// 生成计划名称
  String _generatePlanName(ExercisePlanType planType, TraditionalChineseBodyType? bodyType) {
    String baseName;
    
    // 根据计划类型确定基础名称
    switch (planType) {
      case ExercisePlanType.weightLoss:
        baseName = '塑形减脂';
        break;
      case ExercisePlanType.muscleGain:
        baseName = '增肌塑形';
        break;
      case ExercisePlanType.enduranceBuilding:
        baseName = '耐力提升';
        break;
      case ExercisePlanType.flexibility:
        baseName = '柔韧性增强';
        break;
      case ExercisePlanType.tcmPractice:
        baseName = '中医养生';
        break;
      case ExercisePlanType.balanceImprovement:
        baseName = '平衡提升';
        break;
      case ExercisePlanType.stressReduction:
        baseName = '减压舒缓';
        break;
      default:
        baseName = '全面健身';
        break;
    }
    
    // 如果有体质信息，添加体质相关的名称
    if (bodyType != null) {
      String bodyTypeName;
      
      switch (bodyType) {
        case TraditionalChineseBodyType.coldConstitution:
          bodyTypeName = '温阳散寒';
          break;
        case TraditionalChineseBodyType.hotConstitution:
          bodyTypeName = '清热泻火';
          break;
        case TraditionalChineseBodyType.dampnessConstitution:
          bodyTypeName = '健脾祛湿';
          break;
        case TraditionalChineseBodyType.dryConstitution:
          bodyTypeName = '滋阴润燥';
          break;
        default:
          bodyTypeName = '调和体质';
          break;
      }
      
      
      return '$baseName·$bodyTypeName计划';
    }
    
    return '$baseName计划';
  }
  
  /// 将运动类型转换为字符串
  String _exerciseTypeToString(ExerciseType type) {
    switch (type) {
      case ExerciseType.aerobic:
        return '有氧运动';
      case ExerciseType.strength:
        return '力量训练';
      case ExerciseType.flexibility:
        return '柔韧性训练';
      case ExerciseType.balance:
        return '平衡训练';
      case ExerciseType.coordination:
        return '协调性训练';
      case ExerciseType.hiit:
        return '高强度间歇训练';
      case ExerciseType.functional:
        return '功能性训练';
      case ExerciseType.rehabilitative:
        return '康复训练';
      case ExerciseType.traditional:
        return '传统运动';
      case ExerciseType.team:
        return '团队运动';
      case ExerciseType.outdoor:
        return '户外运动';
      default:
        return '未知类型';
    }
  }
}

// Riverpod Provider 定义

/// 提供运动规划代理实例
final exercisePlanningAgentProvider = Provider<ExercisePlanningAgent>((ref) {
  final agent = ref.watch(aiAgentProvider('exercise_planning_agent'));
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);
  final securityFramework = ref.watch(securityPrivacyFrameworkProvider);
  final healthAgent = ref.watch(healthManagementAgentProvider);
  final nutritionAgent = ref.watch(nutritionBalanceAgentProvider);
  
  return ExercisePlanningAgentImpl(
    agent: agent,
    learningSystem: learningSystem,
    ragService: ragService,
    securityFramework: securityFramework,
    healthAgent: healthAgent,
    nutritionAgent: nutritionAgent,
  );
});

/// 用户运动会话状态提供者
final userExerciseSessionsProvider = FutureProvider.family<List<ExerciseSession>, Map<String, dynamic>>((ref, params) async {
  final userId = params['userId'] as String;
  final startDate = params['startDate'] as DateTime?;
  final endDate = params['endDate'] as DateTime?;
  final type = params['type'] as ExerciseType?;
  
  final exerciseAgent = ref.watch(exercisePlanningAgentProvider);
  
  try {
    return await exerciseAgent.getExerciseSessions(
      userId,
      startDate: startDate,
      endDate: endDate,
      type: type,
    );
  } catch (e) {
    if (kDebugMode) {
      print('获取用户运动会话失败: $e');
    }
    return [];
  }
});

/// 用户运动计划状态提供者
final userExercisePlansProvider = FutureProvider.family<List<WeeklyExercisePlan>, String>((ref, userId) async {
  final exerciseAgent = ref.watch(exercisePlanningAgentProvider);
  
  try {
    return await exerciseAgent.getUserExercisePlans(userId, active: true);
  } catch (e) {
    if (kDebugMode) {
      print('获取用户运动计划失败: $e');
    }
    return [];
  }
});

/// 用户当日运动计划提供者
final dailyExercisePlanProvider = FutureProvider.family<DailyExercisePlan?, Map<String, dynamic>>((ref, params) async {
  final userId = params['userId'] as String;
  final date = params['date'] as DateTime? ?? DateTime.now();
  
  final exerciseAgent = ref.watch(exercisePlanningAgentProvider);
  
  try {
    return await exerciseAgent.getDailyExercisePlan(userId, date);
  } catch (e) {
    if (kDebugMode) {
      print('获取当日运动计划失败: $e');
    }
    return null;
  }
});

/// 用户体能评估提供者
final fitnessAssessmentProvider = FutureProvider.family<FitnessAssessment?, String>((ref, userId) async {
  final exerciseAgent = ref.watch(exercisePlanningAgentProvider);
  
  try {
    return await exerciseAgent.getLatestFitnessAssessment(userId);
  } catch (e) {
    if (kDebugMode) {
      print('获取用户体能评估失败: $e');
    }
    return null;
  }
});

/// 运动进度报告提供者
final exerciseProgressReportProvider = FutureProvider.family<ExerciseProgressReport?, Map<String, dynamic>>((ref, params) async {
  final userId = params['userId'] as String;
  final startDate = params['startDate'] as DateTime?;
  final endDate = params['endDate'] as DateTime?;
  
  final exerciseAgent = ref.watch(exercisePlanningAgentProvider);
  
  try {
    return await exerciseAgent.generateProgressReport(
      userId,
      startDate: startDate,
      endDate: endDate,
    );
  } catch (e) {
    if (kDebugMode) {
      print('生成运动进度报告失败: $e');
    }
    return null;
  }
});
