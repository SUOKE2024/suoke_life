import 'dart:async';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/security/security_framework.dart';
import '../../core/ai/agent.dart';
import '../../core/ai/agent_event.dart';
import '../../core/ai/learning_system.dart';
import '../knowledge_graph_agent.dart';
import 'health_management_agent.dart';

/// 情绪状态枚举
enum MoodState {
  veryHappy, // 非常开心
  happy,     // 开心
  content,   // 满足
  neutral,   // 平静
  tired,     // 疲惫
  stressed,  // 压力
  anxious,   // 焦虑
  sad,       // 悲伤
  angry,     // 愤怒
  depressed, // 抑郁
}

/// 压力级别枚举
enum StressLevel {
  none,       // 无压力
  minimal,    // 极小压力
  mild,       // 轻度压力
  moderate,   // 中度压力
  high,       // 高度压力
  severe,     // 严重压力
  extreme,    // 极端压力
}

/// 情绪触发因素类型
enum EmotionalTriggerType {
  work,           // 工作相关
  relationships,  // 人际关系
  health,         // 健康问题
  finances,       // 财务问题
  environment,    // 环境因素
  selfEsteem,     // 自尊问题
  pastExperience, // 过去经历
  future,         // 对未来的担忧
  socialMedia,    // 社交媒体
  news,           // 新闻事件
  other,          // 其他
}

/// 冥想活动类型
enum MeditationType {
  mindfulness,     // 正念冥想
  breathing,       // 呼吸冥想
  bodyAwareness,   // 身体觉察
  loving,          // 慈爱冥想
  visualization,   // 可视化冥想
  mantra,          // 咒语冥想
  transcendental,  // 超验冥想
  zen,             // 禅修
  qigong,          // 气功
  yoga,            // 瑜伽冥想
}

/// 认知行为活动类型
enum CognitiveActivityType {
  thoughtAwareness,      // 思维觉察
  thoughtChallenging,    // 挑战负面思维
  journaling,            // 日记书写
  gratitude,             // 感恩练习
  selfCompassion,        // 自我关怀
  behavioralActivation,  // 行为激活
  exposureExercise,      // 暴露练习
  rolePlay,              // 角色扮演
  relaxationTraining,    // 放松训练
  problemSolving,        // 问题解决训练
}

/// 心理健康活动的频率
enum MentalHealthActivityFrequency {
  daily,         // 每日
  weekdays,      // 工作日
  weekends,      // 周末
  twiceWeekly,   // 每周两次
  weekly,        // 每周一次
  biweekly,      // 每两周一次
  monthly,       // 每月一次
  asNeeded,      // 需要时
}

/// 心理健康目标类型
enum MentalHealthGoalType {
  reducingStress,      // 减轻压力
  improvingMood,       // 改善情绪
  managingAnxiety,     // 管理焦虑
  enhancingMindfulness, // 增强正念
  buildingResilience,  // 建立韧性
  improvingSleep,      // 改善睡眠
  enhancingRelationships, // 改善人际关系
  increasingSelfCompassion, // 增加自我关怀
  reducingRumination,  // 减少反刍思维
  improvingFocus,      // 提高专注力
}

/// 情绪记录类，用于记录用户的情绪状态
class MoodRecord {
  final String id;
  final String userId;
  final MoodState mood;
  final StressLevel stressLevel;
  final int intensityLevel; // 1-10的强度
  final DateTime timestamp;
  final String notes;
  final List<EmotionalTriggerType> triggers;
  final Map<String, dynamic>? additionalData;

  MoodRecord({
    required this.id,
    required this.userId,
    required this.mood,
    required this.stressLevel,
    required this.intensityLevel,
    required this.timestamp,
    this.notes = '',
    this.triggers = const [],
    this.additionalData,
  });

  MoodRecord copyWith({
    String? id,
    String? userId,
    MoodState? mood,
    StressLevel? stressLevel,
    int? intensityLevel,
    DateTime? timestamp,
    String? notes,
    List<EmotionalTriggerType>? triggers,
    Map<String, dynamic>? additionalData,
  }) {
    return MoodRecord(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      mood: mood ?? this.mood,
      stressLevel: stressLevel ?? this.stressLevel,
      intensityLevel: intensityLevel ?? this.intensityLevel,
      timestamp: timestamp ?? this.timestamp,
      notes: notes ?? this.notes,
      triggers: triggers ?? this.triggers,
      additionalData: additionalData ?? this.additionalData,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'mood': mood.index,
      'stressLevel': stressLevel.index,
      'intensityLevel': intensityLevel,
      'timestamp': timestamp.toIso8601String(),
      'notes': notes,
      'triggers': triggers.map((t) => t.index).toList(),
      'additionalData': additionalData,
    };
  }

  factory MoodRecord.fromJson(Map<String, dynamic> json) {
    return MoodRecord(
      id: json['id'],
      userId: json['userId'],
      mood: MoodState.values[json['mood']],
      stressLevel: StressLevel.values[json['stressLevel']],
      intensityLevel: json['intensityLevel'],
      timestamp: DateTime.parse(json['timestamp']),
      notes: json['notes'],
      triggers: (json['triggers'] as List<dynamic>)
          .map((t) => EmotionalTriggerType.values[t as int])
          .toList(),
      additionalData: json['additionalData'],
    );
  }
}

/// 冥想记录类，用于记录用户的冥想活动
class MeditationRecord {
  final String id;
  final String userId;
  final MeditationType type;
  final int durationMinutes;
  final DateTime timestamp;
  final int completionPercentage; // 0-100
  final MoodState? moodBefore;
  final MoodState? moodAfter;
  final String notes;
  final String? guidedMeditationId; // 引导冥想的ID
  final Map<String, dynamic>? additionalData;

  MeditationRecord({
    required this.id,
    required this.userId,
    required this.type,
    required this.durationMinutes,
    required this.timestamp,
    required this.completionPercentage,
    this.moodBefore,
    this.moodAfter,
    this.notes = '',
    this.guidedMeditationId,
    this.additionalData,
  });

  MeditationRecord copyWith({
    String? id,
    String? userId,
    MeditationType? type,
    int? durationMinutes,
    DateTime? timestamp,
    int? completionPercentage,
    MoodState? moodBefore,
    MoodState? moodAfter,
    String? notes,
    String? guidedMeditationId,
    Map<String, dynamic>? additionalData,
  }) {
    return MeditationRecord(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      type: type ?? this.type,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      timestamp: timestamp ?? this.timestamp,
      completionPercentage: completionPercentage ?? this.completionPercentage,
      moodBefore: moodBefore ?? this.moodBefore,
      moodAfter: moodAfter ?? this.moodAfter,
      notes: notes ?? this.notes,
      guidedMeditationId: guidedMeditationId ?? this.guidedMeditationId,
      additionalData: additionalData ?? this.additionalData,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'type': type.index,
      'durationMinutes': durationMinutes,
      'timestamp': timestamp.toIso8601String(),
      'completionPercentage': completionPercentage,
      'moodBefore': moodBefore?.index,
      'moodAfter': moodAfter?.index,
      'notes': notes,
      'guidedMeditationId': guidedMeditationId,
      'additionalData': additionalData,
    };
  }

  factory MeditationRecord.fromJson(Map<String, dynamic> json) {
    return MeditationRecord(
      id: json['id'],
      userId: json['userId'],
      type: MeditationType.values[json['type']],
      durationMinutes: json['durationMinutes'],
      timestamp: DateTime.parse(json['timestamp']),
      completionPercentage: json['completionPercentage'],
      moodBefore: json['moodBefore'] != null
          ? MoodState.values[json['moodBefore']]
          : null,
      moodAfter: json['moodAfter'] != null
          ? MoodState.values[json['moodAfter']]
          : null,
      notes: json['notes'],
      guidedMeditationId: json['guidedMeditationId'],
      additionalData: json['additionalData'],
    );
  }
}

/// 认知行为活动记录类，用于记录用户的认知行为活动
class CognitiveActivityRecord {
  final String id;
  final String userId;
  final CognitiveActivityType type;
  final DateTime timestamp;
  final int durationMinutes;
  final String content;
  final MoodState? moodBefore;
  final MoodState? moodAfter;
  final Map<String, dynamic>? additionalData;

  CognitiveActivityRecord({
    required this.id,
    required this.userId,
    required this.type,
    required this.timestamp,
    required this.durationMinutes,
    this.content = '',
    this.moodBefore,
    this.moodAfter,
    this.additionalData,
  });

  CognitiveActivityRecord copyWith({
    String? id,
    String? userId,
    CognitiveActivityType? type,
    DateTime? timestamp,
    int? durationMinutes,
    String? content,
    MoodState? moodBefore,
    MoodState? moodAfter,
    Map<String, dynamic>? additionalData,
  }) {
    return CognitiveActivityRecord(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      type: type ?? this.type,
      timestamp: timestamp ?? this.timestamp,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      content: content ?? this.content,
      moodBefore: moodBefore ?? this.moodBefore,
      moodAfter: moodAfter ?? this.moodAfter,
      additionalData: additionalData ?? this.additionalData,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'type': type.index,
      'timestamp': timestamp.toIso8601String(),
      'durationMinutes': durationMinutes,
      'content': content,
      'moodBefore': moodBefore?.index,
      'moodAfter': moodAfter?.index,
      'additionalData': additionalData,
    };
  }

  factory CognitiveActivityRecord.fromJson(Map<String, dynamic> json) {
    return CognitiveActivityRecord(
      id: json['id'],
      userId: json['userId'],
      type: CognitiveActivityType.values[json['type']],
      timestamp: DateTime.parse(json['timestamp']),
      durationMinutes: json['durationMinutes'],
      content: json['content'],
      moodBefore: json['moodBefore'] != null
          ? MoodState.values[json['moodBefore']]
          : null,
      moodAfter: json['moodAfter'] != null
          ? MoodState.values[json['moodAfter']]
          : null,
      additionalData: json['additionalData'],
    );
  }
}

/// 引导冥想类
class GuidedMeditation {
  final String id;
  final String title;
  final String description;
  final MeditationType type;
  final int durationMinutes;
  final String audioUrl;
  final String imageUrl;
  final String creator;
  final List<String> tags;
  final int difficulty; // 1-5
  final double rating; // 0-5
  final int ratingCount;
  final Map<String, dynamic>? additionalData;

  GuidedMeditation({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.durationMinutes,
    required this.audioUrl,
    required this.imageUrl,
    required this.creator,
    this.tags = const [],
    this.difficulty = 1,
    this.rating = 0,
    this.ratingCount = 0,
    this.additionalData,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'type': type.index,
      'durationMinutes': durationMinutes,
      'audioUrl': audioUrl,
      'imageUrl': imageUrl,
      'creator': creator,
      'tags': tags,
      'difficulty': difficulty,
      'rating': rating,
      'ratingCount': ratingCount,
      'additionalData': additionalData,
    };
  }

  factory GuidedMeditation.fromJson(Map<String, dynamic> json) {
    return GuidedMeditation(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      type: MeditationType.values[json['type']],
      durationMinutes: json['durationMinutes'],
      audioUrl: json['audioUrl'],
      imageUrl: json['imageUrl'],
      creator: json['creator'],
      tags: (json['tags'] as List<dynamic>).cast<String>(),
      difficulty: json['difficulty'],
      rating: json['rating'],
      ratingCount: json['ratingCount'],
      additionalData: json['additionalData'],
    );
  }
}

/// 心理健康活动
class MentalHealthActivity {
  final String id;
  final String title;
  final String description;
  final CognitiveActivityType type;
  final int estimatedMinutes;
  final MentalHealthActivityFrequency recommendedFrequency;
  final List<MentalHealthGoalType> targetGoals;
  final String instructions;
  final List<String> resources; // URLs或资源ID
  final int difficulty; // 1-5
  final List<String> tags;
  final Map<String, dynamic>? additionalData;

  MentalHealthActivity({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.estimatedMinutes,
    required this.recommendedFrequency,
    required this.targetGoals,
    required this.instructions,
    this.resources = const [],
    this.difficulty = 1,
    this.tags = const [],
    this.additionalData,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'type': type.index,
      'estimatedMinutes': estimatedMinutes,
      'recommendedFrequency': recommendedFrequency.index,
      'targetGoals': targetGoals.map((g) => g.index).toList(),
      'instructions': instructions,
      'resources': resources,
      'difficulty': difficulty,
      'tags': tags,
      'additionalData': additionalData,
    };
  }

  factory MentalHealthActivity.fromJson(Map<String, dynamic> json) {
    return MentalHealthActivity(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      type: CognitiveActivityType.values[json['type']],
      estimatedMinutes: json['estimatedMinutes'],
      recommendedFrequency: MentalHealthActivityFrequency.values[json['recommendedFrequency']],
      targetGoals: (json['targetGoals'] as List<dynamic>)
          .map((g) => MentalHealthGoalType.values[g as int])
          .toList(),
      instructions: json['instructions'],
      resources: (json['resources'] as List<dynamic>).cast<String>(),
      difficulty: json['difficulty'],
      tags: (json['tags'] as List<dynamic>).cast<String>(),
      additionalData: json['additionalData'],
    );
  }
}

/// 心理健康目标
class MentalHealthGoal {
  final String id;
  final String userId;
  final String title;
  final String description;
  final MentalHealthGoalType type;
  final DateTime startDate;
  final DateTime targetCompletionDate;
  final DateTime? completedDate;
  final double progress; // 0-100
  final bool active;
  final List<String> relatedActivityIds;
  final List<String> milestones;
  final Map<String, dynamic>? additionalData;

  MentalHealthGoal({
    required this.id,
    required this.userId,
    required this.title,
    required this.description,
    required this.type,
    required this.startDate,
    required this.targetCompletionDate,
    this.completedDate,
    this.progress = 0,
    this.active = true,
    this.relatedActivityIds = const [],
    this.milestones = const [],
    this.additionalData,
  });

  MentalHealthGoal copyWith({
    String? id,
    String? userId,
    String? title,
    String? description,
    MentalHealthGoalType? type,
    DateTime? startDate,
    DateTime? targetCompletionDate,
    DateTime? completedDate,
    double? progress,
    bool? active,
    List<String>? relatedActivityIds,
    List<String>? milestones,
    Map<String, dynamic>? additionalData,
  }) {
    return MentalHealthGoal(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      title: title ?? this.title,
      description: description ?? this.description,
      type: type ?? this.type,
      startDate: startDate ?? this.startDate,
      targetCompletionDate: targetCompletionDate ?? this.targetCompletionDate,
      completedDate: completedDate ?? this.completedDate,
      progress: progress ?? this.progress,
      active: active ?? this.active,
      relatedActivityIds: relatedActivityIds ?? this.relatedActivityIds,
      milestones: milestones ?? this.milestones,
      additionalData: additionalData ?? this.additionalData,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'title': title,
      'description': description,
      'type': type.index,
      'startDate': startDate.toIso8601String(),
      'targetCompletionDate': targetCompletionDate.toIso8601String(),
      'completedDate': completedDate?.toIso8601String(),
      'progress': progress,
      'active': active,
      'relatedActivityIds': relatedActivityIds,
      'milestones': milestones,
      'additionalData': additionalData,
    };
  }

  factory MentalHealthGoal.fromJson(Map<String, dynamic> json) {
    return MentalHealthGoal(
      id: json['id'],
      userId: json['userId'],
      title: json['title'],
      description: json['description'],
      type: MentalHealthGoalType.values[json['type']],
      startDate: DateTime.parse(json['startDate']),
      targetCompletionDate: DateTime.parse(json['targetCompletionDate']),
      completedDate: json['completedDate'] != null
          ? DateTime.parse(json['completedDate'])
          : null,
      progress: json['progress'],
      active: json['active'],
      relatedActivityIds: (json['relatedActivityIds'] as List<dynamic>).cast<String>(),
      milestones: (json['milestones'] as List<dynamic>).cast<String>(),
      additionalData: json['additionalData'],
    );
  }
}

/// 情绪概要，用于分析和展示一段时间内的情绪状态
class MoodSummary {
  final String id;
  final String userId;
  final DateTime startDate;
  final DateTime endDate;
  final Map<MoodState, int> moodDistribution;
  final Map<StressLevel, int> stressDistribution;
  final List<MoodState> mostFrequentMoods;
  final List<EmotionalTriggerType> mostCommonTriggers;
  final Map<String, dynamic> trends;
  final List<String> insights;
  final String summary;
  final Map<String, dynamic>? additionalData;

  MoodSummary({
    required this.id,
    required this.userId,
    required this.startDate,
    required this.endDate,
    required this.moodDistribution,
    required this.stressDistribution,
    required this.mostFrequentMoods,
    required this.mostCommonTriggers,
    required this.trends,
    required this.insights,
    required this.summary,
    this.additionalData,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'startDate': startDate.toIso8601String(),
      'endDate': endDate.toIso8601String(),
      'moodDistribution': moodDistribution.map((k, v) => MapEntry(k.index.toString(), v)),
      'stressDistribution': stressDistribution.map((k, v) => MapEntry(k.index.toString(), v)),
      'mostFrequentMoods': mostFrequentMoods.map((m) => m.index).toList(),
      'mostCommonTriggers': mostCommonTriggers.map((t) => t.index).toList(),
      'trends': trends,
      'insights': insights,
      'summary': summary,
      'additionalData': additionalData,
    };
  }

  factory MoodSummary.fromJson(Map<String, dynamic> json) {
    return MoodSummary(
      id: json['id'],
      userId: json['userId'],
      startDate: DateTime.parse(json['startDate']),
      endDate: DateTime.parse(json['endDate']),
      moodDistribution: (json['moodDistribution'] as Map<String, dynamic>).map(
        (k, v) => MapEntry(MoodState.values[int.parse(k)], v as int),
      ),
      stressDistribution: (json['stressDistribution'] as Map<String, dynamic>).map(
        (k, v) => MapEntry(StressLevel.values[int.parse(k)], v as int),
      ),
      mostFrequentMoods: (json['mostFrequentMoods'] as List<dynamic>)
          .map((m) => MoodState.values[m as int])
          .toList(),
      mostCommonTriggers: (json['mostCommonTriggers'] as List<dynamic>)
          .map((t) => EmotionalTriggerType.values[t as int])
          .toList(),
      trends: json['trends'] as Map<String, dynamic>,
      insights: (json['insights'] as List<dynamic>).cast<String>(),
      summary: json['summary'],
      additionalData: json['additionalData'],
    );
  }
}

/// 活动效果分析，用于评估心理健康活动的效果
class ActivityEffectivenessAnalysis {
  final String id;
  final String userId;
  final String activityId;
  final CognitiveActivityType activityType;
  final DateTime startDate;
  final DateTime endDate;
  final int sessionCount;
  final double averageDurationMinutes;
  final Map<MoodState, double> moodBeforeDistribution;
  final Map<MoodState, double> moodAfterDistribution;
  final double moodImprovement; // 平均情绪改善百分比
  final List<String> observations;
  final String summary;
  final Map<String, dynamic>? additionalData;

  ActivityEffectivenessAnalysis({
    required this.id,
    required this.userId,
    required this.activityId,
    required this.activityType,
    required this.startDate,
    required this.endDate,
    required this.sessionCount,
    required this.averageDurationMinutes,
    required this.moodBeforeDistribution,
    required this.moodAfterDistribution,
    required this.moodImprovement,
    required this.observations,
    required this.summary,
    this.additionalData,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'activityId': activityId,
      'activityType': activityType.index,
      'startDate': startDate.toIso8601String(),
      'endDate': endDate.toIso8601String(),
      'sessionCount': sessionCount,
      'averageDurationMinutes': averageDurationMinutes,
      'moodBeforeDistribution': moodBeforeDistribution.map((k, v) => MapEntry(k.index.toString(), v)),
      'moodAfterDistribution': moodAfterDistribution.map((k, v) => MapEntry(k.index.toString(), v)),
      'moodImprovement': moodImprovement,
      'observations': observations,
      'summary': summary,
      'additionalData': additionalData,
    };
  }

  factory ActivityEffectivenessAnalysis.fromJson(Map<String, dynamic> json) {
    return ActivityEffectivenessAnalysis(
      id: json['id'],
      userId: json['userId'],
      activityId: json['activityId'],
      activityType: CognitiveActivityType.values[json['activityType']],
      startDate: DateTime.parse(json['startDate']),
      endDate: DateTime.parse(json['endDate']),
      sessionCount: json['sessionCount'],
      averageDurationMinutes: json['averageDurationMinutes'],
      moodBeforeDistribution: (json['moodBeforeDistribution'] as Map<String, dynamic>).map(
        (k, v) => MapEntry(MoodState.values[int.parse(k)], v as double),
      ),
      moodAfterDistribution: (json['moodAfterDistribution'] as Map<String, dynamic>).map(
        (k, v) => MapEntry(MoodState.values[int.parse(k)], v as double),
      ),
      moodImprovement: json['moodImprovement'],
      observations: (json['observations'] as List<dynamic>).cast<String>(),
      summary: json['summary'],
      additionalData: json['additionalData'],
    );
  }
}

/// 个性化推荐，用于推荐心理健康活动
class MentalHealthRecommendation {
  final String id;
  final String userId;
  final String title;
  final String description;
  final CognitiveActivityType recommendedActivityType;
  final List<MentalHealthGoalType> relevantGoals;
  final String? recommendedActivityId;
  final String? recommendedGuidedMeditationId;
  final double relevanceScore; // 0-1
  final List<EmotionalTriggerType> targetTriggers;
  final DateTime createdAt;
  final bool completed;
  final Map<String, dynamic>? additionalData;

  MentalHealthRecommendation({
    required this.id,
    required this.userId,
    required this.title,
    required this.description,
    required this.recommendedActivityType,
    required this.relevantGoals,
    this.recommendedActivityId,
    this.recommendedGuidedMeditationId,
    required this.relevanceScore,
    required this.targetTriggers,
    required this.createdAt,
    this.completed = false,
    this.additionalData,
  });

  MentalHealthRecommendation copyWith({
    String? id,
    String? userId,
    String? title,
    String? description,
    CognitiveActivityType? recommendedActivityType,
    List<MentalHealthGoalType>? relevantGoals,
    String? recommendedActivityId,
    String? recommendedGuidedMeditationId,
    double? relevanceScore,
    List<EmotionalTriggerType>? targetTriggers,
    DateTime? createdAt,
    bool? completed,
    Map<String, dynamic>? additionalData,
  }) {
    return MentalHealthRecommendation(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      title: title ?? this.title,
      description: description ?? this.description,
      recommendedActivityType: recommendedActivityType ?? this.recommendedActivityType,
      relevantGoals: relevantGoals ?? this.relevantGoals,
      recommendedActivityId: recommendedActivityId ?? this.recommendedActivityId,
      recommendedGuidedMeditationId: recommendedGuidedMeditationId ?? this.recommendedGuidedMeditationId,
      relevanceScore: relevanceScore ?? this.relevanceScore,
      targetTriggers: targetTriggers ?? this.targetTriggers,
      createdAt: createdAt ?? this.createdAt,
      completed: completed ?? this.completed,
      additionalData: additionalData ?? this.additionalData,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'title': title,
      'description': description,
      'recommendedActivityType': recommendedActivityType.index,
      'relevantGoals': relevantGoals.map((g) => g.index).toList(),
      'recommendedActivityId': recommendedActivityId,
      'recommendedGuidedMeditationId': recommendedGuidedMeditationId,
      'relevanceScore': relevanceScore,
      'targetTriggers': targetTriggers.map((t) => t.index).toList(),
      'createdAt': createdAt.toIso8601String(),
      'completed': completed,
      'additionalData': additionalData,
    };
  }

  factory MentalHealthRecommendation.fromJson(Map<String, dynamic> json) {
    return MentalHealthRecommendation(
      id: json['id'],
      userId: json['userId'],
      title: json['title'],
      description: json['description'],
      recommendedActivityType: CognitiveActivityType.values[json['recommendedActivityType']],
      relevantGoals: (json['relevantGoals'] as List<dynamic>)
          .map((g) => MentalHealthGoalType.values[g as int])
          .toList(),
      recommendedActivityId: json['recommendedActivityId'],
      recommendedGuidedMeditationId: json['recommendedGuidedMeditationId'],
      relevanceScore: json['relevanceScore'],
      targetTriggers: (json['targetTriggers'] as List<dynamic>)
          .map((t) => EmotionalTriggerType.values[t as int])
          .toList(),
      createdAt: DateTime.parse(json['createdAt']),
      completed: json['completed'],
      additionalData: json['additionalData'],
    );
  }
}

/// 心理健康代理接口
abstract class MentalHealthAgent {
  /// 获取代理ID
  String get id;
  
  /// 获取代理名称
  String get name;
  
  /// 获取代理事件流
  Stream<AgentEvent> get events;
  
  /// 记录用户情绪状态
  Future<String> recordMood({
    required String userId,
    required MoodState mood,
    required StressLevel stressLevel,
    required int intensityLevel,
    String notes = '',
    List<EmotionalTriggerType> triggers = const [],
    Map<String, dynamic>? additionalData,
  });
  
  /// 批量记录用户情绪状态
  Future<List<String>> recordMoodBatch(List<MoodRecord> records);
  
  /// 获取用户情绪记录
  Future<List<MoodRecord>> getMoodRecords(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
  });
  
  /// 根据ID获取特定情绪记录
  Future<MoodRecord?> getMoodRecordById(String recordId);
  
  /// 生成情绪概要分析
  Future<MoodSummary> generateMoodSummary(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
  });
  
  /// 记录用户冥想活动
  Future<String> recordMeditation({
    required String userId,
    required MeditationType type,
    required int durationMinutes,
    required int completionPercentage,
    MoodState? moodBefore,
    MoodState? moodAfter,
    String notes = '',
    String? guidedMeditationId,
    Map<String, dynamic>? additionalData,
  });
  
  /// 获取用户冥想记录
  Future<List<MeditationRecord>> getMeditationRecords(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    MeditationType? type,
    int? limit,
  });
  
  /// 记录认知行为活动
  Future<String> recordCognitiveActivity({
    required String userId,
    required CognitiveActivityType type,
    required int durationMinutes,
    String content = '',
    MoodState? moodBefore,
    MoodState? moodAfter,
    Map<String, dynamic>? additionalData,
  });
  
  /// 获取用户认知行为活动记录
  Future<List<CognitiveActivityRecord>> getCognitiveActivityRecords(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    CognitiveActivityType? type,
    int? limit,
  });
  
  /// 获取引导冥想列表
  Future<List<GuidedMeditation>> getGuidedMeditations({
    MeditationType? type,
    int? durationMaxMinutes,
    int? difficultyMax,
    List<String>? tags,
    int? limit,
  });
  
  /// 根据ID获取特定引导冥想
  Future<GuidedMeditation?> getGuidedMeditationById(String meditationId);
  
  /// 获取心理健康活动列表
  Future<List<MentalHealthActivity>> getMentalHealthActivities({
    CognitiveActivityType? type,
    MentalHealthGoalType? targetGoal,
    int? difficultyMax,
    List<String>? tags,
    int? limit,
  });
  
  /// 根据ID获取特定心理健康活动
  Future<MentalHealthActivity?> getMentalHealthActivityById(String activityId);
  
  /// 创建心理健康目标
  Future<String> createMentalHealthGoal({
    required String userId,
    required String title,
    required String description,
    required MentalHealthGoalType type,
    required DateTime targetCompletionDate,
    List<String> relatedActivityIds = const [],
    List<String> milestones = const [],
    Map<String, dynamic>? additionalData,
  });
  
  /// 更新心理健康目标进度
  Future<void> updateGoalProgress(String goalId, double progress);
  
  /// 完成心理健康目标
  Future<void> completeGoal(String goalId);
  
  /// 获取用户心理健康目标列表
  Future<List<MentalHealthGoal>> getMentalHealthGoals(
    String userId, {
    bool? active,
    MentalHealthGoalType? type,
  });
  
  /// 根据ID获取特定心理健康目标
  Future<MentalHealthGoal?> getMentalHealthGoalById(String goalId);
  
  /// 分析活动效果
  Future<ActivityEffectivenessAnalysis> analyzeActivityEffectiveness(
    String userId,
    String activityId,
    CognitiveActivityType activityType, {
    DateTime? startDate,
    DateTime? endDate,
  });
  
  /// 获取个性化心理健康推荐
  Future<List<MentalHealthRecommendation>> getMentalHealthRecommendations(
    String userId, {
    List<MentalHealthGoalType>? relevantGoals,
    List<EmotionalTriggerType>? targetTriggers,
    int limit = 5,
  });
  
  /// 根据情绪状态获取推荐活动
  Future<List<MentalHealthRecommendation>> getRecommendationsForMood(
    String userId,
    MoodState mood,
    StressLevel stressLevel, {
    List<EmotionalTriggerType>? triggers,
    int limit = 3,
  });
  
  /// 标记推荐为已完成
  Future<void> markRecommendationAsCompleted(String recommendationId);
  
  /// 获取中医情绪健康分析
  Future<Map<String, dynamic>> getTCMMentalHealthAnalysis(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
  });
}

/// 心理健康代理实现类
class MentalHealthAgentImpl implements MentalHealthAgent {
  final SecurityFramework _securityFramework;
  final LearningSystem _learningSystem;
  final Agent _agent;
  final HealthManagementAgent _healthAgent;
  final KnowledgeGraphAgent _knowledgeAgent;
  
  // 内部存储
  final Map<String, MoodRecord> _moodRecords = {};
  final Map<String, MeditationRecord> _meditationRecords = {};
  final Map<String, CognitiveActivityRecord> _cognitiveActivityRecords = {};
  final Map<String, GuidedMeditation> _guidedMeditations = {};
  final Map<String, MentalHealthActivity> _mentalHealthActivities = {};
  final Map<String, MentalHealthGoal> _mentalHealthGoals = {};
  final Map<String, MoodSummary> _moodSummaries = {};
  final Map<String, ActivityEffectivenessAnalysis> _activityAnalyses = {};
  final Map<String, MentalHealthRecommendation> _recommendations = {};
  
  // 事件控制器
  final _eventController = StreamController<AgentEvent>.broadcast();
  
  MentalHealthAgentImpl({
    required SecurityFramework securityFramework,
    required LearningSystem learningSystem,
    required HealthManagementAgent healthAgent,
    required KnowledgeGraphAgent knowledgeAgent,
  }) : _securityFramework = securityFramework,
       _learningSystem = learningSystem,
       _healthAgent = healthAgent,
       _knowledgeAgent = knowledgeAgent,
       _agent = Agent(id: 'mental_health_agent', name: '心理健康代理') {
    _initializeData();
  }
  
  void _initializeData() {
    // 初始化引导冥想数据
    _initializeGuidedMeditations();
    
    // 初始化心理健康活动
    _initializeMentalHealthActivities();
  }
  
  void _initializeGuidedMeditations() {
    final meditations = [
      GuidedMeditation(
        id: '1',
        title: '正念呼吸冥想',
        description: '专注于呼吸的基础正念冥想，适合初学者。',
        type: MeditationType.breathing,
        durationMinutes: 10,
        audioUrl: 'assets/audio/mindful_breathing.mp3',
        imageUrl: 'assets/images/mindful_breathing.jpg',
        creator: '索克冥想',
        tags: ['初学者', '呼吸', '放松'],
        difficulty: 1,
        rating: 4.8,
        ratingCount: 156,
      ),
      GuidedMeditation(
        id: '2',
        title: '身体扫描冥想',
        description: '通过关注身体不同部位的感觉，增强身体觉察。',
        type: MeditationType.bodyAwareness,
        durationMinutes: 15,
        audioUrl: 'assets/audio/body_scan.mp3',
        imageUrl: 'assets/images/body_scan.jpg',
        creator: '索克冥想',
        tags: ['身体觉察', '放松', '睡前'],
        difficulty: 2,
        rating: 4.6,
        ratingCount: 124,
      ),
      GuidedMeditation(
        id: '3',
        title: '慈爱冥想',
        description: '培养对自己和他人的慈爱和善意。',
        type: MeditationType.loving,
        durationMinutes: 20,
        audioUrl: 'assets/audio/loving_kindness.mp3',
        imageUrl: 'assets/images/loving_kindness.jpg',
        creator: '索克冥想',
        tags: ['慈爱', '正念', '中级'],
        difficulty: 3,
        rating: 4.7,
        ratingCount: 98,
      ),
      GuidedMeditation(
        id: '4',
        title: '五行气功冥想',
        description: '结合传统五行理论的气功冥想，调和身心能量。',
        type: MeditationType.qigong,
        durationMinutes: 25,
        audioUrl: 'assets/audio/five_elements_qigong.mp3',
        imageUrl: 'assets/images/five_elements_qigong.jpg',
        creator: '索克气功',
        tags: ['气功', '五行', '能量平衡', '中级'],
        difficulty: 3,
        rating: 4.9,
        ratingCount: 78,
      ),
    ];
    
    for (final meditation in meditations) {
      _guidedMeditations[meditation.id] = meditation;
    }
  }
  
  void _initializeMentalHealthActivities() {
    final activities = [
      MentalHealthActivity(
        id: '1',
        title: '感恩日记',
        description: '每天记录3件你感恩的事情，培养积极的心态。',
        type: CognitiveActivityType.gratitude,
        estimatedMinutes: 10,
        recommendedFrequency: MentalHealthActivityFrequency.daily,
        targetGoals: [
          MentalHealthGoalType.improvingMood,
          MentalHealthGoalType.buildingResilience,
        ],
        instructions: '1. 找一个安静的地方，拿出笔记本或使用应用\n'
            '2. 思考今天发生的事情\n'
            '3. 写下3件你感恩的事情，无论大小\n'
            '4. 对每件事，写下为什么你对它心怀感激',
        resources: ['articles/gratitude_journal.pdf'],
        difficulty: 1,
        tags: ['日记', '积极心理学', '初学者'],
      ),
      MentalHealthActivity(
        id: '2',
        title: '认知重构练习',
        description: '识别和挑战负面自动化思维，建立更健康的思维模式。',
        type: CognitiveActivityType.thoughtChallenging,
        estimatedMinutes: 15,
        recommendedFrequency: MentalHealthActivityFrequency.weekly,
        targetGoals: [
          MentalHealthGoalType.reducingStress,
          MentalHealthGoalType.managingAnxiety,
          MentalHealthGoalType.reducingRumination,
        ],
        instructions: '1. 识别触发你不适情绪的情境\n'
            '2. 注意这种情境下出现的自动化思维\n'
            '3. 找出这些思维中的认知偏差\n'
            '4. 挑战这些偏差，提出更平衡的思维\n'
            '5. 记录新的、更有帮助的思维方式',
        resources: ['articles/cognitive_restructuring.pdf'],
        difficulty: 3,
        tags: ['认知疗法', '思维模式', '中级'],
      ),
      MentalHealthActivity(
        id: '3',
        title: '自我关怀练习',
        description: '通过温和和同情的方式对待自己，培养自我接纳。',
        type: CognitiveActivityType.selfCompassion,
        estimatedMinutes: 10,
        recommendedFrequency: MentalHealthActivityFrequency.daily,
        targetGoals: [
          MentalHealthGoalType.increasingSelfCompassion,
          MentalHealthGoalType.improvingMood,
        ],
        instructions: '1. 找一个安静的地方，闭上眼睛\n'
            '2. 将手轻轻放在心脏部位\n'
            '3. 深呼吸三次\n'
            '4. 对自己说三句自我关怀的话，如"愿我安好"、"我值得幸福"、"我接受自己的不完美"\n'
            '5. 允许自己感受自我关怀的温暖',
        resources: ['articles/self_compassion.pdf'],
        difficulty: 2,
        tags: ['自我关怀', '冥想', '初级'],
      ),
    ];
    
    for (final activity in activities) {
      _mentalHealthActivities[activity.id] = activity;
    }
  }
  
  @override
  String get id => _agent.id;
  
  @override
  String get name => _agent.name;
  
  @override
  Stream<AgentEvent> get events => _eventController.stream;
  
  @override
  Future<String> recordMood({
    required String userId,
    required MoodState mood,
    required StressLevel stressLevel,
    required int intensityLevel,
    String notes = '',
    List<EmotionalTriggerType> triggers = const [],
    Map<String, dynamic>? additionalData,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'record_mood',
        resource: 'mood_records',
        data: {
          'mood': mood.toString(),
          'stressLevel': stressLevel.toString(),
          'intensityLevel': intensityLevel,
        },
      );
      
      // 创建记录
      final record = MoodRecord(
        id: const Uuid().v4(),
        userId: userId,
        mood: mood,
        stressLevel: stressLevel,
        intensityLevel: intensityLevel,
        timestamp: DateTime.now(),
        notes: notes,
        triggers: triggers,
        additionalData: additionalData,
      );
      
      // 存储记录
      _moodRecords[record.id] = record;
      
      // 收集学习数据
      _learningSystem.collectData(
        source: id,
        dataType: 'mood_record',
        data: record.toJson(),
      );
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'recordMood',
          'recordId': record.id,
          'userId': userId,
          'dataType': 'moodRecords',
        },
      ));
      
      return record.id;
    } catch (e) {
      if (kDebugMode) {
        print('记录情绪失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'recordMood',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<String>> recordMoodBatch(List<MoodRecord> records) async {
    try {
      final recordIds = <String>[];
      
      for (final record in records) {
        // 安全审计
        await _securityFramework.auditAction(
          userId: record.userId,
          action: 'record_mood_batch',
          resource: 'mood_records',
          data: {
            'recordId': record.id,
          },
        );
        
        // 存储记录
        _moodRecords[record.id] = record;
        recordIds.add(record.id);
        
        // 收集学习数据
        _learningSystem.collectData(
          source: id,
          dataType: 'mood_record',
          data: record.toJson(),
        );
      }
      
      if (records.isNotEmpty) {
        // 发布批量事件
        _agent.publishEvent(AgentEvent(
          type: AgentEventType.dataChanged,
          source: id,
          data: {
            'operation': 'recordMoodBatch',
            'count': records.length,
            'userId': records.first.userId,
            'dataType': 'moodRecords',
          },
        ));
      }
      
      return recordIds;
    } catch (e) {
      if (kDebugMode) {
        print('批量记录情绪失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'recordMoodBatch',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<MoodRecord>> getMoodRecords(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'get_mood_records',
        resource: 'mood_records',
        data: {
          'startDate': startDate?.toIso8601String(),
          'endDate': endDate?.toIso8601String(),
          'limit': limit,
        },
      );
      
      // 筛选记录
      final records = _moodRecords.values
          .where((r) => r.userId == userId)
          .where((r) => startDate == null || r.timestamp.isAfter(startDate))
          .where((r) => endDate == null || r.timestamp.isBefore(endDate))
          .toList();
      
      // 按时间排序（最新的在前）
      records.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      
      // 限制记录数量
      if (limit != null && records.length > limit) {
        return records.sublist(0, limit);
      }
      
      return records;
    } catch (e) {
      if (kDebugMode) {
        print('获取情绪记录失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMoodRecords',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<MoodRecord?> getMoodRecordById(String recordId) async {
    try {
      final record = _moodRecords[recordId];
      
      if (record != null) {
        // 安全审计
        await _securityFramework.auditAction(
          userId: record.userId,
          action: 'get_mood_record_by_id',
          resource: 'mood_records',
          data: {
            'recordId': recordId,
          },
        );
      }
      
      return record;
    } catch (e) {
      if (kDebugMode) {
        print('获取情绪记录失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMoodRecordById',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<MoodSummary> generateMoodSummary(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'generate_mood_summary',
        resource: 'mood_summaries',
        data: {
          'startDate': startDate?.toIso8601String(),
          'endDate': endDate?.toIso8601String(),
        },
      );
      
      // 获取情绪记录
      final records = await getMoodRecords(
        userId,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (records.isEmpty) {
        throw Exception('没有足够的情绪记录来生成概要');
      }
      
      // 计算情绪分布
      final moodDistribution = <MoodState, int>{};
      for (final record in records) {
        moodDistribution[record.mood] = (moodDistribution[record.mood] ?? 0) + 1;
      }
      
      // 计算情绪百分比
      final moodPercentages = <MoodState, double>{};
      for (final entry in moodDistribution.entries) {
        moodPercentages[entry.key] = entry.value / records.length;
      }
      
      // 计算压力分布
      final stressDistribution = <StressLevel, int>{};
      for (final record in records) {
        stressDistribution[record.stressLevel] = (stressDistribution[record.stressLevel] ?? 0) + 1;
      }
      
      // 找出最常见的情绪状态
      final mostFrequentMoods = moodDistribution.entries
          .sorted((a, b) => b.value.compareTo(a.value))
          .take(3)
          .map((e) => e.key)
          .toList();
      
      // 找出最常见的触发因素
      final triggerCounts = <EmotionalTriggerType, int>{};
      for (final record in records) {
        for (final trigger in record.triggers) {
          triggerCounts[trigger] = (triggerCounts[trigger] ?? 0) + 1;
        }
      }
      
      final mostCommonTriggers = triggerCounts.entries
          .sorted((a, b) => b.value.compareTo(a.value))
          .take(3)
          .map((e) => e.key)
          .toList();
      
      // 分析情绪趋势
      final trends = _analyzeMoodTrends(records);
      
      // 生成洞察
      final insights = _generateMoodInsights(
        records,
        moodPercentages,
        mostFrequentMoods,
        mostCommonTriggers,
        trends,
      );
      
      // 生成总结
      final summary = _generateMoodSummary(
        records,
        moodPercentages,
        stressDistribution,
        mostFrequentMoods,
        mostCommonTriggers,
        insights,
      );
      
      // 创建情绪概要
      final moodSummary = MoodSummary(
        id: const Uuid().v4(),
        userId: userId,
        startDate: startDate ?? records.last.timestamp,
        endDate: endDate ?? records.first.timestamp,
        moodDistribution: moodPercentages,
        stressDistribution: stressDistribution.map((k, v) => MapEntry(k, v)),
        mostFrequentMoods: mostFrequentMoods,
        mostCommonTriggers: mostCommonTriggers,
        trends: trends,
        insights: insights,
        summary: summary,
      );
      
      // 存储概要
      _moodSummaries[moodSummary.id] = moodSummary;
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'generateMoodSummary',
          'summaryId': moodSummary.id,
          'userId': userId,
          'dataType': 'moodSummaries',
        },
      ));
      
      return moodSummary;
    } catch (e) {
      if (kDebugMode) {
        print('生成情绪概要失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'generateMoodSummary',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  Map<String, dynamic> _analyzeMoodTrends(List<MoodRecord> records) {
    if (records.length < 3) {
      return {'insufficient_data': true};
    }
    
    // 按日期排序
    records.sort((a, b) => a.timestamp.compareTo(b.timestamp));
    
    // 计算情绪状态随时间变化
    final moodTrend = <String, int>{};
    final stressTrend = <String, int>{};
    
    for (final record in records) {
      final dateStr = '${record.timestamp.year}-${record.timestamp.month.toString().padLeft(2, '0')}-${record.timestamp.day.toString().padLeft(2, '0')}';
      moodTrend[dateStr] = record.mood.index;
      stressTrend[dateStr] = record.stressLevel.index;
    }
    
    // 计算情绪变化趋势
    double? moodSlope;
    if (records.length >= 5) {
      final x = List<double>.generate(records.length, (i) => i.toDouble());
      final y = records.map((r) => r.mood.index.toDouble()).toList();
      moodSlope = _calculateLinearRegressionSlope(x, y);
    }
    
    // 计算压力变化趋势
    double? stressSlope;
    if (records.length >= 5) {
      final x = List<double>.generate(records.length, (i) => i.toDouble());
      final y = records.map((r) => r.stressLevel.index.toDouble()).toList();
      stressSlope = _calculateLinearRegressionSlope(x, y);
    }
    
    // 分析情绪波动
    double moodVariability = 0;
    if (records.length >= 3) {
      double sum = 0;
      for (int i = 1; i < records.length; i++) {
        sum += (records[i].mood.index - records[i - 1].mood.index).abs();
      }
      moodVariability = sum / (records.length - 1);
    }
    
    return {
      'moodTrend': moodTrend,
      'stressTrend': stressTrend,
      'moodSlope': moodSlope,
      'stressSlope': stressSlope,
      'moodVariability': moodVariability,
      'improvingMood': moodSlope != null && moodSlope < -0.1, // 情绪指数下降表示心情变好
      'worseningMood': moodSlope != null && moodSlope > 0.1,
      'decreasingStress': stressSlope != null && stressSlope < -0.1,
      'increasingStress': stressSlope != null && stressSlope > 0.1,
      'highVariability': moodVariability > 2.0,
    };
  }
  
  // 计算线性回归斜率
  double _calculateLinearRegressionSlope(List<double> x, List<double> y) {
    if (x.length != y.length || x.isEmpty) {
      return 0;
    }
    
    double sumX = 0;
    double sumY = 0;
    double sumXY = 0;
    double sumX2 = 0;
    
    for (int i = 0; i < x.length; i++) {
      sumX += x[i];
      sumY += y[i];
      sumXY += x[i] * y[i];
      sumX2 += x[i] * x[i];
    }
    
    final n = x.length.toDouble();
    return (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  }
  
  List<String> _generateMoodInsights(
    List<MoodRecord> records,
    Map<MoodState, double> moodPercentages,
    List<MoodState> mostFrequentMoods,
    List<EmotionalTriggerType> mostCommonTriggers,
    Map<String, dynamic> trends,
  ) {
    final insights = <String>[];
    
    // 分析情绪状态
    if (mostFrequentMoods.isNotEmpty) {
      final mainMood = mostFrequentMoods.first;
      final percentage = (moodPercentages[mainMood]! * 100).toStringAsFixed(0);
      
      if (mainMood == MoodState.veryHappy || mainMood == MoodState.happy) {
        insights.add('您有$percentage%的时间感到开心或非常开心，这反映了您整体积极的情绪状态。');
      } else if (mainMood == MoodState.content) {
        insights.add('您有$percentage%的时间感到满足，这表明您拥有健康平衡的情绪状态。');
      } else if (mainMood == MoodState.neutral) {
        insights.add('您有$percentage%的时间感到平静中性，这可能表明您处于情绪稳定期或需要更多情绪刺激。');
      } else if (mainMood == MoodState.stressed || mainMood == MoodState.anxious) {
        insights.add('您有$percentage%的时间感到压力或焦虑，这提示您可能需要更多的压力管理和放松技巧。');
      } else if (mainMood == MoodState.sad || mainMood == MoodState.depressed) {
        insights.add('您有$percentage%的时间感到悲伤或低落，这可能表明需要更多的社交支持和积极活动。');
      }
    }
    
    // 分析触发因素
    if (mostCommonTriggers.isNotEmpty) {
      final trigger = mostCommonTriggers.first;
      String triggerStr;
      
      switch (trigger) {
        case EmotionalTriggerType.work:
          triggerStr = '工作相关压力';
          insights.add('工作是影响您情绪的主要因素，考虑工作与生活的平衡和压力管理策略。');
          break;
        case EmotionalTriggerType.relationships:
          triggerStr = '人际关系';
          insights.add('人际关系是影响您情绪的主要因素，可能需要提高人际沟通技巧或设定健康边界。');
          break;
        case EmotionalTriggerType.health:
          triggerStr = '健康问题';
          insights.add('健康问题是影响您情绪的主要因素，关注自我照顾和健康管理是优先事项。');
          break;
        case EmotionalTriggerType.finances:
          triggerStr = '财务问题';
          insights.add('财务问题是影响您情绪的主要因素，考虑制定预算或寻求财务规划建议。');
          break;
        case EmotionalTriggerType.environment:
          triggerStr = '环境因素';
          insights.add('环境因素是影响您情绪的主要因素，可能需要创造更舒适和支持性的环境。');
          break;
        default:
          triggerStr = '其他因素';
          insights.add('您的情绪受多种因素影响，识别具体触发因素可能有助于情绪管理。');
          break;
      }
    }
    
    // 分析情绪趋势
    if (trends.containsKey('moodSlope') && trends['moodSlope'] != null) {
      if (trends['improvingMood'] == true) {
        insights.add('您的情绪状态呈现积极改善趋势，继续现有的积极活动和习惯。');
      } else if (trends['worseningMood'] == true) {
        insights.add('您的情绪状态近期有所下降，可能需要更多自我关注和支持。');
      }
      
      if (trends['decreasingStress'] == true) {
        insights.add('您的压力水平呈下降趋势，表明您的压力管理策略正在发挥作用。');
      } else if (trends['increasingStress'] == true) {
        insights.add('您的压力水平呈上升趋势，考虑增加放松活动和压力管理技巧。');
      }
      
      if (trends['highVariability'] == true) {
        insights.add('您的情绪波动较大，建立日常规律和自我调节技巧可能有助于稳定情绪。');
      }
    }
    
    // 根据情绪记录的时间分布
    final timeDistribution = _analyzeTimeDistribution(records);
    if (timeDistribution.containsKey('morningMood') && 
        timeDistribution.containsKey('eveningMood')) {
      final morningMood = timeDistribution['morningMood'] as double;
      final eveningMood = timeDistribution['eveningMood'] as double;
      
      if (morningMood - eveningMood > 1.0) {
        insights.add('您在早晨的情绪通常好于晚上，可能表明晚间活动或睡眠问题影响了情绪。');
      } else if (eveningMood - morningMood > 1.0) {
        insights.add('您在晚上的情绪通常好于早晨，可能需要调整早晨的唤醒和活动方式。');
      }
    }
    
    return insights;
  }
  
  Map<String, dynamic> _analyzeTimeDistribution(List<MoodRecord> records) {
    if (records.length < 5) {
      return {'insufficient_data': true};
    }
    
    // 按时段分类记录
    final morningRecords = records.where((r) => 
        r.timestamp.hour >= 5 && r.timestamp.hour < 12).toList();
    final afternoonRecords = records.where((r) => 
        r.timestamp.hour >= 12 && r.timestamp.hour < 18).toList();
    final eveningRecords = records.where((r) => 
        r.timestamp.hour >= 18 && r.timestamp.hour < 24).toList();
    final nightRecords = records.where((r) => 
        r.timestamp.hour >= 0 && r.timestamp.hour < 5).toList();
    
    // 计算各时段的平均情绪和压力
    double morningMood = 0;
    double afternoonMood = 0;
    double eveningMood = 0;
    double nightMood = 0;
    
    if (morningRecords.isNotEmpty) {
      morningMood = morningRecords
          .map((r) => r.mood.index)
          .reduce((a, b) => a + b) / morningRecords.length;
    }
    
    if (afternoonRecords.isNotEmpty) {
      afternoonMood = afternoonRecords
          .map((r) => r.mood.index)
          .reduce((a, b) => a + b) / afternoonRecords.length;
    }
    
    if (eveningRecords.isNotEmpty) {
      eveningMood = eveningRecords
          .map((r) => r.mood.index)
          .reduce((a, b) => a + b) / eveningRecords.length;
    }
    
    if (nightRecords.isNotEmpty) {
      nightMood = nightRecords
          .map((r) => r.mood.index)
          .reduce((a, b) => a + b) / nightRecords.length;
    }
    
    return {
      'morningMood': morningMood,
      'afternoonMood': afternoonMood,
      'eveningMood': eveningMood,
      'nightMood': nightMood,
      'bestTimeOfDay': _getBestTimeOfDay(morningMood, afternoonMood, eveningMood, nightMood),
      'worstTimeOfDay': _getWorstTimeOfDay(morningMood, afternoonMood, eveningMood, nightMood),
    };
  }
  
  String _getBestTimeOfDay(
    double morningMood, 
    double afternoonMood, 
    double eveningMood, 
    double nightMood
  ) {
    final moods = {
      '早晨': morningMood,
      '下午': afternoonMood,
      '晚上': eveningMood,
      '夜间': nightMood,
    };
    
    // 情绪值越低越好（0=veryHappy, 9=depressed）
    return moods.entries
        .where((e) => e.value > 0) // 过滤掉没有数据的时段
        .reduce((a, b) => a.value < b.value ? a : b)
        .key;
  }
  
  String _getWorstTimeOfDay(
    double morningMood, 
    double afternoonMood, 
    double eveningMood, 
    double nightMood
  ) {
    final moods = {
      '早晨': morningMood,
      '下午': afternoonMood,
      '晚上': eveningMood,
      '夜间': nightMood,
    };
    
    // 情绪值越高越差（0=veryHappy, 9=depressed）
    return moods.entries
        .where((e) => e.value > 0) // 过滤掉没有数据的时段
        .reduce((a, b) => a.value > b.value ? a : b)
        .key;
  }
  
  String _generateMoodSummary(
    List<MoodRecord> records,
    Map<MoodState, double> moodPercentages,
    Map<StressLevel, int> stressDistribution,
    List<MoodState> mostFrequentMoods,
    List<EmotionalTriggerType> mostCommonTriggers,
    List<String> insights,
  ) {
    final buffer = StringBuffer();
    
    // 总体情绪评估
    buffer.write('在记录期间，');
    
    if (mostFrequentMoods.isNotEmpty) {
      final mainMood = mostFrequentMoods.first;
      final percentage = (moodPercentages[mainMood]! * 100).toStringAsFixed(0);
      
      buffer.write('您的情绪状态主要是${_moodStateToString(mainMood)}，占比$percentage%。');
    }
    
    // 分析情绪趋势
    final moodTrends = _analyzeMoodTrends(records);
    if (moodTrends.containsKey('moodSlope') && moodTrends['moodSlope'] != null) {
      if (moodTrends['improvingMood'] == true) {
        buffer.write('您的情绪状态呈现积极改善趋势。');
      } else if (moodTrends['worseningMood'] == true) {
        buffer.write('您的情绪状态近期有所下降。');
      }
    }
    
    // 分析压力趋势
    if (moodTrends.containsKey('stressSlope') && moodTrends['stressSlope'] != null) {
      if (moodTrends['decreasingStress'] == true) {
        buffer.write('您的压力水平呈下降趋势。');
      } else if (moodTrends['increasingStress'] == true) {
        buffer.write('您的压力水平呈上升趋势。');
      }
    }
    
    // 分析情绪波动
    if (moodTrends.containsKey('moodVariability') && moodTrends['moodVariability'] != null) {
      if (moodTrends['highVariability'] == true) {
        buffer.write('您的情绪波动较大。');
      }
    }
    
    // 分析情绪分布
    buffer.write('您的情绪分布主要集中在以下状态：');
    for (final mood in mostFrequentMoods) {
      buffer.write('${_moodStateToString(mood)}，占比${(moodPercentages[mood]! * 100).toStringAsFixed(0)}%，');
    }
    
    // 分析压力分布
    buffer.write('您的压力分布主要集中在以下级别：');
    for (final stressEntry in stressDistribution.entries) {
      buffer.write('${_stressLevelToString(stressEntry.key)}，占比${(stressEntry.value / records.length * 100).toStringAsFixed(0)}%，');
    }
    
    // 分析情绪洞察
    buffer.write('以下是一些情绪洞察：');
    for (final insight in insights) {
      buffer.write('\n$insight');
    }
    
    return buffer.toString();
  }
  
  String _moodStateToString(MoodState mood) {
    switch (mood) {
      case MoodState.veryHappy:
        return '非常开心';
      case MoodState.happy:
        return '开心';
      case MoodState.content:
        return '满足';
      case MoodState.neutral:
        return '平静';
      case MoodState.tired:
        return '疲惫';
      case MoodState.stressed:
        return '压力';
      case MoodState.anxious:
        return '焦虑';
      case MoodState.sad:
        return '悲伤';
      case MoodState.angry:
        return '愤怒';
      case MoodState.depressed:
        return '抑郁';
    }
  }
  
  String _stressLevelToString(StressLevel stress) {
    switch (stress) {
      case StressLevel.none:
        return '无压力';
      case StressLevel.minimal:
        return '极小压力';
      case StressLevel.mild:
        return '轻度压力';
      case StressLevel.moderate:
        return '中度压力';
      case StressLevel.high:
        return '高度压力';
      case StressLevel.severe:
        return '严重压力';
      case StressLevel.extreme:
        return '极端压力';
    }
  }
  
  @override
  Future<String> recordMeditation({
    required String userId,
    required MeditationType type,
    required int durationMinutes,
    required int completionPercentage,
    MoodState? moodBefore,
    MoodState? moodAfter,
    String notes = '',
    String? guidedMeditationId,
    Map<String, dynamic>? additionalData,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'record_meditation',
        resource: 'meditation_records',
        data: {
          'type': type.toString(),
          'durationMinutes': durationMinutes,
          'completionPercentage': completionPercentage,
        },
      );
      
      // 创建记录
      final record = MeditationRecord(
        id: const Uuid().v4(),
        userId: userId,
        type: type,
        durationMinutes: durationMinutes,
        timestamp: DateTime.now(),
        completionPercentage: completionPercentage,
        moodBefore: moodBefore,
        moodAfter: moodAfter,
        notes: notes,
        guidedMeditationId: guidedMeditationId,
        additionalData: additionalData,
      );
      
      // 存储记录
      _meditationRecords[record.id] = record;
      
      // 收集学习数据
      _learningSystem.collectData(
        source: id,
        dataType: 'meditation_record',
        data: record.toJson(),
      );
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'recordMeditation',
          'recordId': record.id,
          'userId': userId,
          'dataType': 'meditationRecords',
        },
      ));
      
      return record.id;
    } catch (e) {
      if (kDebugMode) {
        print('记录冥想失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'recordMeditation',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<MeditationRecord>> getMeditationRecords(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    MeditationType? type,
    int? limit,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'get_meditation_records',
        resource: 'meditation_records',
        data: {
          'startDate': startDate?.toIso8601String(),
          'endDate': endDate?.toIso8601String(),
          'type': type?.toString(),
          'limit': limit,
        },
      );
      
      // 筛选记录
      final records = _meditationRecords.values
          .where((r) => r.userId == userId)
          .where((r) => startDate == null || r.timestamp.isAfter(startDate))
          .where((r) => endDate == null || r.timestamp.isBefore(endDate))
          .where((r) => type == null || r.type == type)
          .toList();
      
      // 按时间排序（最新的在前）
      records.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      
      // 限制记录数量
      if (limit != null && records.length > limit) {
        return records.sublist(0, limit);
      }
      
      return records;
    } catch (e) {
      if (kDebugMode) {
        print('获取冥想记录失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMeditationRecords',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<String> recordCognitiveActivity({
    required String userId,
    required CognitiveActivityType type,
    required int durationMinutes,
    String content = '',
    MoodState? moodBefore,
    MoodState? moodAfter,
    Map<String, dynamic>? additionalData,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'record_cognitive_activity',
        resource: 'cognitive_activity_records',
        data: {
          'type': type.toString(),
          'durationMinutes': durationMinutes,
        },
      );
      
      // 创建记录
      final record = CognitiveActivityRecord(
        id: const Uuid().v4(),
        userId: userId,
        type: type,
        timestamp: DateTime.now(),
        durationMinutes: durationMinutes,
        content: content,
        moodBefore: moodBefore,
        moodAfter: moodAfter,
        additionalData: additionalData,
      );
      
      // 存储记录
      _cognitiveActivityRecords[record.id] = record;
      
      // 收集学习数据
      _learningSystem.collectData(
        source: id,
        dataType: 'cognitive_activity_record',
        data: record.toJson(),
      );
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'recordCognitiveActivity',
          'recordId': record.id,
          'userId': userId,
          'dataType': 'cognitiveActivityRecords',
        },
      ));
      
      return record.id;
    } catch (e) {
      if (kDebugMode) {
        print('记录认知行为活动失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'recordCognitiveActivity',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<CognitiveActivityRecord>> getCognitiveActivityRecords(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    CognitiveActivityType? type,
    int? limit,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'get_cognitive_activity_records',
        resource: 'cognitive_activity_records',
        data: {
          'startDate': startDate?.toIso8601String(),
          'endDate': endDate?.toIso8601String(),
          'type': type?.toString(),
          'limit': limit,
        },
      );
      
      // 筛选记录
      final records = _cognitiveActivityRecords.values
          .where((r) => r.userId == userId)
          .where((r) => startDate == null || r.timestamp.isAfter(startDate))
          .where((r) => endDate == null || r.timestamp.isBefore(endDate))
          .where((r) => type == null || r.type == type)
          .toList();
      
      // 按时间排序（最新的在前）
      records.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      
      // 限制记录数量
      if (limit != null && records.length > limit) {
        return records.sublist(0, limit);
      }
      
      return records;
    } catch (e) {
      if (kDebugMode) {
        print('获取认知行为活动记录失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getCognitiveActivityRecords',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<GuidedMeditation>> getGuidedMeditations({
    MeditationType? type,
    int? durationMaxMinutes,
    int? difficultyMax,
    List<String>? tags,
    int? limit,
  }) async {
    try {
      // 筛选冥想
      final meditations = _guidedMeditations.values
          .where((m) => type == null || m.type == type)
          .where((m) => durationMaxMinutes == null || m.durationMinutes <= durationMaxMinutes)
          .where((m) => difficultyMax == null || m.difficulty <= difficultyMax)
          .where((m) => tags == null || tags.isEmpty || 
                      tags.any((tag) => m.tags.contains(tag)))
          .toList();
      
      // 按评分排序（高到低）
      meditations.sort((a, b) => b.rating.compareTo(a.rating));
      
      // 限制数量
      if (limit != null && meditations.length > limit) {
        return meditations.sublist(0, limit);
      }
      
      return meditations;
    } catch (e) {
      if (kDebugMode) {
        print('获取引导冥想失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getGuidedMeditations',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<GuidedMeditation?> getGuidedMeditationById(String meditationId) async {
    try {
      return _guidedMeditations[meditationId];
    } catch (e) {
      if (kDebugMode) {
        print('获取引导冥想失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getGuidedMeditationById',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<MentalHealthActivity>> getMentalHealthActivities({
    CognitiveActivityType? type,
    MentalHealthGoalType? targetGoal,
    int? difficultyMax,
    List<String>? tags,
    int? limit,
  }) async {
    try {
      // 筛选活动
      final activities = _mentalHealthActivities.values
          .where((a) => type == null || a.type == type)
          .where((a) => targetGoal == null || a.targetGoals.contains(targetGoal))
          .where((a) => difficultyMax == null || a.difficulty <= difficultyMax)
          .where((a) => tags == null || tags.isEmpty || 
                      tags.any((tag) => a.tags.contains(tag)))
          .toList();
      
      // 按难度排序（简单到复杂）
      activities.sort((a, b) => a.difficulty.compareTo(b.difficulty));
      
      // 限制数量
      if (limit != null && activities.length > limit) {
        return activities.sublist(0, limit);
      }
      
      return activities;
    } catch (e) {
      if (kDebugMode) {
        print('获取心理健康活动失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMentalHealthActivities',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<MentalHealthActivity?> getMentalHealthActivityById(String activityId) async {
    try {
      return _mentalHealthActivities[activityId];
    } catch (e) {
      if (kDebugMode) {
        print('获取心理健康活动失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMentalHealthActivityById',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<String> createMentalHealthGoal({
    required String userId,
    required String title,
    required String description,
    required MentalHealthGoalType type,
    required DateTime targetCompletionDate,
    List<String> relatedActivityIds = const [],
    List<String> milestones = const [],
    Map<String, dynamic>? additionalData,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'create_mental_health_goal',
        resource: 'mental_health_goals',
        data: {
          'title': title,
          'type': type.toString(),
          'targetCompletionDate': targetCompletionDate.toIso8601String(),
        },
      );
      
      // 创建目标
      final goal = MentalHealthGoal(
        id: const Uuid().v4(),
        userId: userId,
        title: title,
        description: description,
        type: type,
        startDate: DateTime.now(),
        targetCompletionDate: targetCompletionDate,
        progress: 0,
        active: true,
        relatedActivityIds: relatedActivityIds,
        milestones: milestones,
        additionalData: additionalData,
      );
      
      // 存储目标
      _mentalHealthGoals[goal.id] = goal;
      
      // 收集学习数据
      _learningSystem.collectData(
        source: id,
        dataType: 'mental_health_goal',
        data: goal.toJson(),
      );
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'createMentalHealthGoal',
          'goalId': goal.id,
          'userId': userId,
          'dataType': 'mentalHealthGoals',
        },
      ));
      
      return goal.id;
    } catch (e) {
      if (kDebugMode) {
        print('创建心理健康目标失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'createMentalHealthGoal',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<void> updateGoalProgress(String goalId, double progress) async {
    try {
      final goal = _mentalHealthGoals[goalId];
      
      if (goal == null) {
        throw Exception('目标不存在');
      }
      
      // 安全审计
      await _securityFramework.auditAction(
        userId: goal.userId,
        action: 'update_goal_progress',
        resource: 'mental_health_goals',
        data: {
          'goalId': goalId,
          'progress': progress,
        },
      );
      
      // 更新目标进度
      final updatedGoal = goal.copyWith(progress: progress);
      _mentalHealthGoals[goalId] = updatedGoal;
      
      // 收集学习数据
      _learningSystem.collectData(
        source: id,
        dataType: 'goal_progress_update',
        data: {
          'goalId': goalId,
          'userId': goal.userId,
          'oldProgress': goal.progress,
          'newProgress': progress,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'updateGoalProgress',
          'goalId': goalId,
          'userId': goal.userId,
          'dataType': 'mentalHealthGoals',
        },
      ));
    } catch (e) {
      if (kDebugMode) {
        print('更新目标进度失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'updateGoalProgress',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<void> completeGoal(String goalId) async {
    try {
      final goal = _mentalHealthGoals[goalId];
      
      if (goal == null) {
        throw Exception('目标不存在');
      }
      
      // 安全审计
      await _securityFramework.auditAction(
        userId: goal.userId,
        action: 'complete_goal',
        resource: 'mental_health_goals',
        data: {
          'goalId': goalId,
        },
      );
      
      // 更新目标状态
      final updatedGoal = goal.copyWith(
        completedDate: DateTime.now(),
        progress: 100,
        active: false,
      );
      _mentalHealthGoals[goalId] = updatedGoal;
      
      // 收集学习数据
      _learningSystem.collectData(
        source: id,
        dataType: 'goal_completion',
        data: {
          'goalId': goalId,
          'userId': goal.userId,
          'type': goal.type.toString(),
          'daysToComplete': updatedGoal.completedDate!
              .difference(goal.startDate)
              .inDays,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'completeGoal',
          'goalId': goalId,
          'userId': goal.userId,
          'dataType': 'mentalHealthGoals',
        },
      ));
    } catch (e) {
      if (kDebugMode) {
        print('完成目标失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'completeGoal',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<MentalHealthGoal>> getMentalHealthGoals(
    String userId, {
    bool? active,
    MentalHealthGoalType? type,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'get_mental_health_goals',
        resource: 'mental_health_goals',
        data: {
          'active': active,
          'type': type?.toString(),
        },
      );
      
      // 筛选目标
      final goals = _mentalHealthGoals.values
          .where((g) => g.userId == userId)
          .where((g) => active == null || g.active == active)
          .where((g) => type == null || g.type == type)
          .toList();
      
      // 按开始日期排序（最新的在前）
      goals.sort((a, b) => b.startDate.compareTo(a.startDate));
      
      return goals;
    } catch (e) {
      if (kDebugMode) {
        print('获取心理健康目标失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMentalHealthGoals',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<MentalHealthGoal?> getMentalHealthGoalById(String goalId) async {
    try {
      final goal = _mentalHealthGoals[goalId];
      
      if (goal != null) {
        // 安全审计
        await _securityFramework.auditAction(
          userId: goal.userId,
          action: 'get_mental_health_goal_by_id',
          resource: 'mental_health_goals',
          data: {
            'goalId': goalId,
          },
        );
      }
      
      return goal;
    } catch (e) {
      if (kDebugMode) {
        print('获取心理健康目标失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMentalHealthGoalById',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<ActivityEffectivenessAnalysis> analyzeActivityEffectiveness(
    String userId,
    String activityId,
    CognitiveActivityType activityType, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'analyze_activity_effectiveness',
        resource: 'activity_effectiveness_analysis',
        data: {
          'activityId': activityId,
          'activityType': activityType.toString(),
          'startDate': startDate?.toIso8601String(),
          'endDate': endDate?.toIso8601String(),
        },
      );
      
      // 获取认知活动记录
      final records = await getCognitiveActivityRecords(
        userId,
        startDate: startDate,
        endDate: endDate,
        type: activityType,
      );
      
      if (records.isEmpty) {
        throw Exception('没有足够的活动记录来分析效果');
      }
      
      // 计算会话次数和平均时长
      final sessionCount = records.length;
      final totalDuration = records
          .map((r) => r.durationMinutes)
          .reduce((a, b) => a + b);
      final averageDurationMinutes = totalDuration / sessionCount;
      
      // 分析情绪变化
      final moodBeforeDistribution = <MoodState, double>{};
      final moodAfterDistribution = <MoodState, double>{};
      double moodImprovement = 0;
      int validMoodPairs = 0;
      
      for (final record in records) {
        if (record.moodBefore != null) {
          moodBeforeDistribution[record.moodBefore!] = 
              (moodBeforeDistribution[record.moodBefore!] ?? 0) + 1;
        }
        
        if (record.moodAfter != null) {
          moodAfterDistribution[record.moodAfter!] = 
              (moodAfterDistribution[record.moodAfter!] ?? 0) + 1;
        }
        
        if (record.moodBefore != null && record.moodAfter != null) {
          // 情绪指数下降表示心情变好
          final improvement = record.moodBefore!.index - record.moodAfter!.index;
          moodImprovement += improvement;
          validMoodPairs++;
        }
      }
      
      // 归一化情绪分布
      for (final entry in moodBeforeDistribution.entries) {
        moodBeforeDistribution[entry.key] = entry.value / records.length;
      }
      
      for (final entry in moodAfterDistribution.entries) {
        moodAfterDistribution[entry.key] = entry.value / records.length;
      }
      
      // 计算平均情绪改善
      final avgMoodImprovement = validMoodPairs > 0 
          ? moodImprovement / validMoodPairs
          : 0;
      
      // 生成观察结果
      final observations = _generateActivityObservations(
        records,
        moodBeforeDistribution,
        moodAfterDistribution,
        avgMoodImprovement,
      );
      
      // 生成总结
      final summary = _generateActivityEffectivenessSummary(
        activityType,
        records,
        sessionCount,
        averageDurationMinutes,
        avgMoodImprovement,
        observations,
      );
      
      // 创建分析报告
      final analysis = ActivityEffectivenessAnalysis(
        id: const Uuid().v4(),
        userId: userId,
        activityId: activityId,
        activityType: activityType,
        startDate: startDate ?? records.last.timestamp,
        endDate: endDate ?? records.first.timestamp,
        sessionCount: sessionCount,
        averageDurationMinutes: averageDurationMinutes,
        moodBeforeDistribution: moodBeforeDistribution,
        moodAfterDistribution: moodAfterDistribution,
        moodImprovement: avgMoodImprovement,
        observations: observations,
        summary: summary,
      );
      
      // 存储分析
      _activityAnalyses[analysis.id] = analysis;
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'analyzeActivityEffectiveness',
          'analysisId': analysis.id,
          'userId': userId,
          'dataType': 'activityAnalyses',
        },
      ));
      
      return analysis;
    } catch (e) {
      if (kDebugMode) {
        print('分析活动效果失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'analyzeActivityEffectiveness',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  List<String> _generateActivityObservations(
    List<CognitiveActivityRecord> records,
    Map<MoodState, double> moodBeforeDistribution,
    Map<MoodState, double> moodAfterDistribution,
    double avgMoodImprovement,
  ) {
    final observations = <String>[];
    
    // 分析会话频率
    if (records.length >= 5) {
      final daysBetweenSessions = <int>[];
      for (int i = 1; i < records.length; i++) {
        final days = records[i-1].timestamp.difference(records[i].timestamp).inDays;
        daysBetweenSessions.add(days);
      }
      
      final avgDaysBetween = daysBetweenSessions.reduce((a, b) => a + b) / 
          daysBetweenSessions.length;
      
      if (avgDaysBetween < 2) {
        observations.add('您非常频繁地进行此活动，平均每天或隔天一次。');
      } else if (avgDaysBetween < 7) {
        observations.add('您每周多次进行此活动，显示了良好的坚持度。');
      } else {
        observations.add('您的活动频率较低，平均每${avgDaysBetween.toStringAsFixed(1)}天一次。增加频率可能会提高效果。');
      }
    }
    
    // 分析时长变化
    if (records.length >= 3) {
      final durationTrend = records
          .map((r) => r.durationMinutes.toDouble())
          .toList()
          .reversed
          .toList();
      
      final x = List<double>.generate(durationTrend.length, (i) => i.toDouble());
      final durationSlope = _calculateLinearRegressionSlope(x, durationTrend);
      
      if (durationSlope > 1.0) {
        observations.add('您的活动时长呈上升趋势，表明您对此活动的投入在增加。');
      } else if (durationSlope < -1.0) {
        observations.add('您的活动时长呈下降趋势，可能表明活动的难度或您的兴趣在变化。');
      } else {
        observations.add('您的活动时长保持相对稳定。');
      }
    }
    
    // 分析情绪改善
    if (avgMoodImprovement > 2.0) {
      observations.add('此活动对您的情绪有显著的积极影响，活动后情绪明显改善。');
    } else if (avgMoodImprovement > 0.5) {
      observations.add('此活动对您的情绪有适度的积极影响。');
    } else if (avgMoodImprovement > -0.5) {
      observations.add('此活动对您的情绪影响不明显，可能需要尝试其他类型的活动。');
    } else {
      observations.add('此活动似乎对您的情绪有负面影响，可能需要重新评估其适用性。');
    }
    
    // 分析活动内容
    if (records.isNotEmpty && !records.first.content.isEmpty) {
      final contentLengths = records
          .map((r) => r.content.length)
          .toList();
      
      final avgContentLength = contentLengths.reduce((a, b) => a + b) / 
          contentLengths.length;
      
      if (avgContentLength > 500) {
        observations.add('您在活动中投入了大量的内容和思考，表明深度参与这项活动。');
      } else if (avgContentLength > 100) {
        observations.add('您的活动内容适中，显示了一定程度的参与度。');
      } else {
        observations.add('您的活动内容相对简短，可以考虑增加详细程度以获得更好的效果。');
      }
    }
    
    return observations;
  }
  
  String _generateActivityEffectivenessSummary(
    CognitiveActivityType activityType,
    List<CognitiveActivityRecord> records,
    int sessionCount,
    double averageDurationMinutes,
    double avgMoodImprovement,
    List<String> observations,
  ) {
    final buffer = StringBuffer();
    
    // 活动类型描述
    buffer.write('${_cognitiveActivityTypeToString(activityType)}活动分析：');
    
    // 活动频率和持续时间
    buffer.write('在记录期间，您进行了$sessionCount次活动，平均每次持续${averageDurationMinutes.toStringAsFixed(1)}分钟。');
    
    // 情绪改善效果
    if (avgMoodImprovement > 0) {
      buffer.write('活动对您的情绪状态有${_getMoodImprovementLevel(avgMoodImprovement)}积极影响，平均情绪改善指数为${avgMoodImprovement.toStringAsFixed(1)}。');
    } else if (avgMoodImprovement < 0) {
      buffer.write('活动似乎对您的情绪状态有轻微负面影响，平均情绪变化指数为${avgMoodImprovement.toStringAsFixed(1)}。您可能需要调整活动方式或考虑其他类型的活动。');
    } else {
      buffer.write('活动对您的情绪状态影响不明显。您可能需要尝试不同的活动方式或结合其他类型的活动。');
    }
    
    // 添加观察结果
    buffer.write('\n\n主要观察：');
    for (final observation in observations) {
      buffer.write('\n- $observation');
    }
    
    // 建议
    buffer.write('\n\n建议：');
    if (avgMoodImprovement > 1.5) {
      buffer.write('\n- 考虑增加此活动的频率，它对您的情绪健康有明显的积极作用。');
      buffer.write('\n- 尝试在情绪低落时优先选择此活动。');
    } else if (avgMoodImprovement > 0) {
      buffer.write('\n- 保持当前的活动频率，并尝试延长每次活动的时间。');
      buffer.write('\n- 考虑结合其他类型的活动以获得更好的效果。');
    } else {
      buffer.write('\n- 考虑调整此活动的方式或尝试其他类型的活动。');
      buffer.write('\n- 咨询专业人士以获得更适合您的活动建议。');
    }
    
    return buffer.toString();
  }
  
  String _cognitiveActivityTypeToString(CognitiveActivityType type) {
    switch (type) {
      case CognitiveActivityType.thoughtAwareness:
        return '思维觉察';
      case CognitiveActivityType.thoughtChallenging:
        return '挑战负面思维';
      case CognitiveActivityType.journaling:
        return '日记书写';
      case CognitiveActivityType.gratitude:
        return '感恩练习';
      case CognitiveActivityType.selfCompassion:
        return '自我关怀';
      case CognitiveActivityType.behavioralActivation:
        return '行为激活';
      case CognitiveActivityType.exposureExercise:
        return '暴露练习';
      case CognitiveActivityType.rolePlay:
        return '角色扮演';
      case CognitiveActivityType.relaxationTraining:
        return '放松训练';
      case CognitiveActivityType.problemSolving:
        return '问题解决训练';
    }
  }
  
  String _getMoodImprovementLevel(double improvement) {
    if (improvement > 2.5) return '显著';
    if (improvement > 1.5) return '明显';
    if (improvement > 0.5) return '适度';
    return '轻微';
  }
  
  @override
  Future<List<MentalHealthRecommendation>> getMentalHealthRecommendations(
    String userId, {
    List<MentalHealthGoalType>? relevantGoals,
    List<EmotionalTriggerType>? targetTriggers,
    int limit = 5,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'get_mental_health_recommendations',
        resource: 'mental_health_recommendations',
        data: {
          'relevantGoals': relevantGoals?.map((g) => g.toString()).toList(),
          'targetTriggers': targetTriggers?.map((t) => t.toString()).toList(),
          'limit': limit,
        },
      );
      
      // 获取用户的情绪记录
      final moodRecords = await getMoodRecords(
        userId,
        limit: 20,
      );
      
      // 获取用户的目标
      final goals = await getMentalHealthGoals(
        userId,
        active: true,
      );
      
      // 如果没有指定目标类型，则使用用户的活动目标
      final targetGoalTypes = relevantGoals ?? 
          goals.map((g) => g.type).toList();
      
      // 如果没有指定触发因素，则从最近的情绪记录中提取
      final effectiveTriggers = targetTriggers ?? 
          _extractFrequentTriggers(moodRecords);
      
      // 获取用户可能需要的活动
      final activities = await getMentalHealthActivities(
        targetGoal: targetGoalTypes.isNotEmpty ? targetGoalTypes.first : null,
        limit: 20,
      );
      
      // 获取用户可能需要的冥想
      final meditations = await getGuidedMeditations(
        limit: 10,
      );
      
      // 生成推荐列表
      final recommendations = <MentalHealthRecommendation>[];
      
      // 创建针对目标的推荐
      for (final goalType in targetGoalTypes) {
        // 找到匹配目标的活动
        final matchingActivities = activities
            .where((a) => a.targetGoals.contains(goalType))
            .toList();
        
        if (matchingActivities.isNotEmpty) {
          // 计算每个活动的相关性得分
          final scoredActivities = matchingActivities
              .map((a) => MapEntry(a, _calculateActivityRelevanceScore(
                a, goalType, effectiveTriggers, moodRecords)))
              .toList();
          
          // 按相关性排序
          scoredActivities.sort((a, b) => b.value.compareTo(a.value));
          
          // 添加最相关的活动到推荐中
          final topActivity = scoredActivities.first;
          
          final recommendation = MentalHealthRecommendation(
            id: const Uuid().v4(),
            userId: userId,
            title: '${_mentalHealthGoalTypeToString(goalType)}活动推荐',
            description: '基于您的${_mentalHealthGoalTypeToString(goalType)}目标，推荐以下活动：${topActivity.key.title}',
            recommendedActivityType: topActivity.key.type,
            relevantGoals: [goalType],
            recommendedActivityId: topActivity.key.id,
            relevanceScore: topActivity.value,
            targetTriggers: effectiveTriggers,
            createdAt: DateTime.now(),
          );
          
          recommendations.add(recommendation);
        }
      }
      
      // 添加一些冥想推荐
      if (meditations.isNotEmpty && recommendations.length < limit) {
        // 根据用户最常见的情绪状态推荐冥想
        MeditationType recommendedType;
        String reasonDesc;
        
        if (moodRecords.isNotEmpty) {
          final mostFrequentMood = _findMostFrequentMood(moodRecords);
          
          if (mostFrequentMood == MoodState.stressed || 
              mostFrequentMood == MoodState.anxious) {
            recommendedType = MeditationType.breathing;
            reasonDesc = '帮助缓解压力和焦虑';
          } else if (mostFrequentMood == MoodState.sad || 
                    mostFrequentMood == MoodState.depressed) {
            recommendedType = MeditationType.loving;
            reasonDesc = '提升积极情绪和自我关怀';
          } else if (mostFrequentMood == MoodState.angry) {
            recommendedType = MeditationType.mindfulness;
            reasonDesc = '帮助平静心情，提高情绪觉察';
          } else if (mostFrequentMood == MoodState.tired) {
            recommendedType = MeditationType.qigong;
            reasonDesc = '恢复精力和活力';
          } else {
            recommendedType = MeditationType.mindfulness;
            reasonDesc = '维持平静和专注';
          }
        } else {
          recommendedType = MeditationType.mindfulness;
          reasonDesc = '培养日常正念习惯';
        }
        
        // 找到匹配类型的冥想
        final matchingMeditations = meditations
            .where((m) => m.type == recommendedType)
            .toList();
        
        if (matchingMeditations.isNotEmpty) {
          final bestMeditation = matchingMeditations.first;
          
          final recommendation = MentalHealthRecommendation(
            id: const Uuid().v4(),
            userId: userId,
            title: '推荐冥想活动',
            description: '${bestMeditation.title} - $reasonDesc',
            recommendedActivityType: CognitiveActivityType.selfCompassion,
            relevantGoals: [MentalHealthGoalType.enhancingMindfulness],
            recommendedGuidedMeditationId: bestMeditation.id,
            relevanceScore: 0.9,
            targetTriggers: effectiveTriggers,
            createdAt: DateTime.now(),
          );
          
          recommendations.add(recommendation);
        }
      }
      
      // 限制推荐数量
      if (recommendations.length > limit) {
        return recommendations.sublist(0, limit);
      }
      
      // 存储推荐
      for (final recommendation in recommendations) {
        _recommendations[recommendation.id] = recommendation;
      }
      
      // 发布事件
      if (recommendations.isNotEmpty) {
        _agent.publishEvent(AgentEvent(
          type: AgentEventType.dataChanged,
          source: id,
          data: {
            'operation': 'getMentalHealthRecommendations',
            'count': recommendations.length,
            'userId': userId,
            'dataType': 'recommendations',
          },
        ));
      }
      
      return recommendations;
    } catch (e) {
      if (kDebugMode) {
        print('获取心理健康推荐失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMentalHealthRecommendations',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  List<EmotionalTriggerType> _extractFrequentTriggers(List<MoodRecord> records) {
    if (records.isEmpty) {
      return [EmotionalTriggerType.work, EmotionalTriggerType.relationships];
    }
    
    final triggerCounts = <EmotionalTriggerType, int>{};
    
    for (final record in records) {
      for (final trigger in record.triggers) {
        triggerCounts[trigger] = (triggerCounts[trigger] ?? 0) + 1;
      }
    }
    
    if (triggerCounts.isEmpty) {
      return [EmotionalTriggerType.work, EmotionalTriggerType.relationships];
    }
    
    // 按频率排序
    final sortedTriggers = triggerCounts.entries
        .sorted((a, b) => b.value.compareTo(a.value))
        .take(3)
        .map((e) => e.key)
        .toList();
    
    return sortedTriggers;
  }
  
  MoodState _findMostFrequentMood(List<MoodRecord> records) {
    final moodCounts = <MoodState, int>{};
    
    for (final record in records) {
      moodCounts[record.mood] = (moodCounts[record.mood] ?? 0) + 1;
    }
    
    return moodCounts.entries
        .reduce((a, b) => a.value > b.value ? a : b)
        .key;
  }
  
  double _calculateActivityRelevanceScore(
    MentalHealthActivity activity,
    MentalHealthGoalType goalType,
    List<EmotionalTriggerType> triggers,
    List<MoodRecord> moodRecords,
  ) {
    double score = 0.0;
    
    // 目标匹配加分
    if (activity.targetGoals.contains(goalType)) {
      score += 0.5;
    }
    
    // 难度适中加分
    if (activity.difficulty >= 2 && activity.difficulty <= 3) {
      score += 0.2;
    }
    
    // 时长适中加分
    if (activity.estimatedMinutes >= 10 && activity.estimatedMinutes <= 20) {
      score += 0.1;
    }
    
    // 根据情绪记录匹配活动类型
    if (moodRecords.isNotEmpty) {
      final mostFrequentMood = _findMostFrequentMood(moodRecords);
      
      if ((mostFrequentMood == MoodState.anxious || 
          mostFrequentMood == MoodState.stressed) &&
          (activity.type == CognitiveActivityType.relaxationTraining ||
           activity.type == CognitiveActivityType.breathingExercise)) {
        score += 0.3;
      }
      
      if ((mostFrequentMood == MoodState.sad || 
          mostFrequentMood == MoodState.depressed) &&
          (activity.type == CognitiveActivityType.behavioralActivation ||
           activity.type == CognitiveActivityType.gratitude)) {
        score += 0.3;
      }
      
      if (mostFrequentMood == MoodState.angry &&
          (activity.type == CognitiveActivityType.thoughtChallenging ||
           activity.type == CognitiveActivityType.problemSolving)) {
        score += 0.3;
      }
    }
    
    // 限制分数范围
    return max(0.1, min(1.0, score));
  }
  
  String _mentalHealthGoalTypeToString(MentalHealthGoalType type) {
    switch (type) {
      case MentalHealthGoalType.reducingStress:
        return '减轻压力';
      case MentalHealthGoalType.improvingMood:
        return '改善情绪';
      case MentalHealthGoalType.managingAnxiety:
        return '管理焦虑';
      case MentalHealthGoalType.enhancingMindfulness:
        return '增强正念';
      case MentalHealthGoalType.buildingResilience:
        return '建立韧性';
      case MentalHealthGoalType.improvingSleep:
        return '改善睡眠';
      case MentalHealthGoalType.enhancingRelationships:
        return '改善人际关系';
      case MentalHealthGoalType.increasingSelfCompassion:
        return '增加自我关怀';
      case MentalHealthGoalType.reducingRumination:
        return '减少反刍思维';
      case MentalHealthGoalType.improvingFocus:
        return '提高专注力';
    }
  }
  
  @override
  Future<List<MentalHealthRecommendation>> getRecommendationsForMood(
    String userId,
    MoodState mood,
    StressLevel stressLevel, {
    List<EmotionalTriggerType>? triggers,
    int limit = 3,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'get_recommendations_for_mood',
        resource: 'mental_health_recommendations',
        data: {
          'mood': mood.toString(),
          'stressLevel': stressLevel.toString(),
          'triggers': triggers?.map((t) => t.toString()).toList(),
          'limit': limit,
        },
      );
      
      // 根据情绪和压力级别确定目标类型
      final targetGoalTypes = _determineGoalTypesForMood(mood, stressLevel);
      
      // 获取推荐
      return getMentalHealthRecommendations(
        userId,
        relevantGoals: targetGoalTypes,
        targetTriggers: triggers,
        limit: limit,
      );
    } catch (e) {
      if (kDebugMode) {
        print('获取情绪推荐失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getRecommendationsForMood',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  List<MentalHealthGoalType> _determineGoalTypesForMood(
    MoodState mood,
    StressLevel stressLevel,
  ) {
    final goalTypes = <MentalHealthGoalType>[];
    
    switch (mood) {
      case MoodState.veryHappy:
      case MoodState.happy:
      case MoodState.content:
        // 积极情绪，维持或增强
        goalTypes.add(MentalHealthGoalType.enhancingMindfulness);
        goalTypes.add(MentalHealthGoalType.buildingResilience);
        break;
        
      case MoodState.neutral:
        // 平静情绪，提升积极性
        goalTypes.add(MentalHealthGoalType.improvingMood);
        goalTypes.add(MentalHealthGoalType.enhancingMindfulness);
        break;
        
      case MoodState.tired:
        // 疲惫情绪，改善能量和睡眠
        goalTypes.add(MentalHealthGoalType.improvingSleep);
        goalTypes.add(MentalHealthGoalType.reducingStress);
        break;
        
      case MoodState.stressed:
        // 压力情绪，减轻压力
        goalTypes.add(MentalHealthGoalType.reducingStress);
        goalTypes.add(MentalHealthGoalType.enhancingMindfulness);
        break;
        
      case MoodState.anxious:
        // 焦虑情绪，管理焦虑
        goalTypes.add(MentalHealthGoalType.managingAnxiety);
        goalTypes.add(MentalHealthGoalType.reducingRumination);
        break;
        
      case MoodState.sad:
      case MoodState.depressed:
        // 悲伤或抑郁情绪，改善情绪
        goalTypes.add(MentalHealthGoalType.improvingMood);
        goalTypes.add(MentalHealthGoalType.increasingSelfCompassion);
        break;
        
      case MoodState.angry:
        // 愤怒情绪，改善情绪和关系
        goalTypes.add(MentalHealthGoalType.reducingStress);
        goalTypes.add(MentalHealthGoalType.enhancingRelationships);
        break;
    }
    
    // 根据压力级别添加额外目标
    if (stressLevel == StressLevel.high || 
        stressLevel == StressLevel.severe || 
        stressLevel == StressLevel.extreme) {
      goalTypes.add(MentalHealthGoalType.reducingStress);
    }
    
    return goalTypes;
  }
  
  @override
  Future<void> markRecommendationAsCompleted(String recommendationId) async {
    try {
      final recommendation = _recommendations[recommendationId];
      
      if (recommendation == null) {
        throw Exception('推荐不存在');
      }
      
      // 安全审计
      await _securityFramework.auditAction(
        userId: recommendation.userId,
        action: 'mark_recommendation_completed',
        resource: 'mental_health_recommendations',
        data: {
          'recommendationId': recommendationId,
        },
      );
      
      // 更新推荐状态
      final updatedRecommendation = recommendation.copyWith(
        completed: true,
      );
      _recommendations[recommendationId] = updatedRecommendation;
      
      // 收集学习数据
      _learningSystem.collectData(
        source: id,
        dataType: 'recommendation_completion',
        data: {
          'recommendationId': recommendationId,
          'userId': recommendation.userId,
          'title': recommendation.title,
          'relevanceScore': recommendation.relevanceScore,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'markRecommendationAsCompleted',
          'recommendationId': recommendationId,
          'userId': recommendation.userId,
          'dataType': 'recommendations',
        },
      ));
    } catch (e) {
      if (kDebugMode) {
        print('标记推荐为已完成失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'markRecommendationAsCompleted',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<Map<String, dynamic>> getTCMMentalHealthAnalysis(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      // 安全审计
      await _securityFramework.auditAction(
        userId: userId,
        action: 'get_tcm_mental_health_analysis',
        resource: 'tcm_mental_health_analysis',
        data: {
          'startDate': startDate?.toIso8601String(),
          'endDate': endDate?.toIso8601String(),
        },
      );
      
      // 获取情绪记录
      final moodRecords = await getMoodRecords(
        userId,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (moodRecords.isEmpty) {
        throw Exception('没有足够的情绪记录来生成中医分析');
      }
      
      // 调用知识图谱代理获取中医情绪分析
      final tcmAnalysis = await _knowledgeAgent.analyzeTCMEmotionalPattern(
        moodRecords
            .map((r) => {
                  'mood': r.mood.toString(),
                  'timestamp': r.timestamp.toIso8601String(),
                  'stressLevel': r.stressLevel.toString(),
                  'intensityLevel': r.intensityLevel,
                  'triggers': r.triggers
                      .map((t) => t.toString())
                      .toList(),
                })
            .toList(),
      );
      
      // 收集学习数据
      _learningSystem.collectData(
        source: id,
        dataType: 'tcm_mental_health_analysis',
        data: {
          'userId': userId,
          'analysis': tcmAnalysis,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      
      // 发布事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataChanged,
        source: id,
        data: {
          'operation': 'getTCMMentalHealthAnalysis',
          'userId': userId,
          'dataType': 'tcmAnalysis',
        },
      ));
      
      return tcmAnalysis;
    } catch (e) {
      if (kDebugMode) {
        print('获取中医情绪健康分析失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getTCMMentalHealthAnalysis',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
}

// Provider定义
final securityFrameworkProvider = Provider<SecurityFramework>((ref) {
  return SecurityFramework();
});

final learningSystemProvider = Provider<LearningSystem>((ref) {
  return LearningSystem();
});

final healthManagementAgentProvider = Provider<HealthManagementAgent>((ref) {
  final securityFramework = ref.watch(securityFrameworkProvider);
  final learningSystem = ref.watch(learningSystemProvider);
  return HealthManagementAgentImpl(
    securityFramework: securityFramework,
    learningSystem: learningSystem,
  );
});

final knowledgeGraphAgentProvider = Provider<KnowledgeGraphAgent>((ref) {
  final securityFramework = ref.watch(securityFrameworkProvider);
  final learningSystem = ref.watch(learningSystemProvider);
  return KnowledgeGraphAgentImpl(
    securityFramework: securityFramework,
    learningSystem: learningSystem,
  );
});

final mentalHealthAgentProvider = Provider<MentalHealthAgent>((ref) {
  final securityFramework = ref.watch(securityFrameworkProvider);
  final learningSystem = ref.watch(learningSystemProvider);
  final healthAgent = ref.watch(healthManagementAgentProvider);
  final knowledgeAgent = ref.watch(knowledgeGraphAgentProvider);
  
  return MentalHealthAgentImpl(
    securityFramework: securityFramework,
    learningSystem: learningSystem,
    healthAgent: healthAgent,
    knowledgeAgent: knowledgeAgent,
  );
});