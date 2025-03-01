import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/agent_microkernel.dart';
import '../core/autonomous_learning_system.dart';
import '../core/security_privacy_framework.dart';
import '../models/ai_agent.dart';
import '../rag/rag_service.dart';
import '../../core/models/user.dart';
import '../../core/repositories/user_repository.dart';
import '../../core/utils/logger.dart';

/// 交互复杂度级别
enum InteractionComplexityLevel {
  /// 简单 - 适合初学者或认知负担高的场景
  simple,
  
  /// 标准 - 默认交互复杂度
  standard,
  
  /// 高级 - 适合专业用户
  advanced,
  
  /// 专家 - 最复杂的交互模式
  expert,
}

/// 交互风格
enum InteractionStyle {
  /// 简洁 - 无额外装饰的界面
  minimal,
  
  /// 详细 - 提供丰富的信息和解释
  detailed,
  
  /// 视觉化 - 偏好图表和可视化表示
  visual,
  
  /// 文本化 - 偏好文本描述
  textual,
  
  /// 互动性 - 强调用户参与
  interactive,
}

/// 认知负荷级别
enum CognitiveLoadLevel {
  /// 低 - 用户可以轻松处理更多信息
  low,
  
  /// 中等 - 默认认知负荷级别
  medium,
  
  /// 高 - 用户当前认知负荷较高
  high,
  
  /// 超高 - 用户处于认知过载状态
  overloaded,
}

/// 情感状态类型
enum EmotionalStateType {
  /// 积极
  positive,
  
  /// 中性
  neutral,
  
  /// 消极
  negative,
  
  /// 专注
  focused,
  
  /// 困惑
  confused,
  
  /// 疲惫
  tired,
  
  /// 焦虑
  anxious,
}

/// 用户画像
class UserProfile {
  /// 用户ID
  final String userId;
  
  /// 用户偏好的交互复杂度
  final InteractionComplexityLevel preferredComplexity;
  
  /// 用户偏好的交互风格
  final InteractionStyle preferredStyle;
  
  /// 用户的学习曲线
  final Map<String, double> learningCurves;
  
  /// 用户的主题兴趣
  final Map<String, double> topicInterests;
  
  /// 用户的活跃时间模式
  final Map<String, List<TimeOfDay>> activityPatterns;
  
  /// 用户的健康目标
  final List<String> healthGoals;
  
  /// 用户创建时间
  final DateTime createdAt;
  
  /// 最后更新时间
  final DateTime updatedAt;

  /// 构造函数
  UserProfile({
    required this.userId,
    this.preferredComplexity = InteractionComplexityLevel.standard,
    this.preferredStyle = InteractionStyle.detailed,
    Map<String, double>? learningCurves,
    Map<String, double>? topicInterests,
    Map<String, List<TimeOfDay>>? activityPatterns,
    List<String>? healthGoals,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : 
    this.learningCurves = learningCurves ?? {},
    this.topicInterests = topicInterests ?? {},
    this.activityPatterns = activityPatterns ?? {},
    this.healthGoals = healthGoals ?? [],
    this.createdAt = createdAt ?? DateTime.now(),
    this.updatedAt = updatedAt ?? DateTime.now();
  
  /// 从JSON创建
  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      userId: json['userId'] as String,
      preferredComplexity: InteractionComplexityLevel.values.firstWhere(
        (e) => e.toString() == json['preferredComplexity'],
        orElse: () => InteractionComplexityLevel.standard,
      ),
      preferredStyle: InteractionStyle.values.firstWhere(
        (e) => e.toString() == json['preferredStyle'],
        orElse: () => InteractionStyle.detailed,
      ),
      learningCurves: (json['learningCurves'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, v as double),
      ) ?? {},
      topicInterests: (json['topicInterests'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, v as double),
      ) ?? {},
      activityPatterns: (json['activityPatterns'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(
          k, 
          (v as List).map((time) => TimeOfDay(
            hour: time['hour'] as int,
            minute: time['minute'] as int,
          )).toList(),
        ),
      ) ?? {},
      healthGoals: (json['healthGoals'] as List?)?.cast<String>() ?? [],
      createdAt: json['createdAt'] != null 
        ? DateTime.parse(json['createdAt'] as String)
        : DateTime.now(),
      updatedAt: json['updatedAt'] != null
        ? DateTime.parse(json['updatedAt'] as String)
        : DateTime.now(),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'preferredComplexity': preferredComplexity.toString(),
      'preferredStyle': preferredStyle.toString(),
      'learningCurves': learningCurves,
      'topicInterests': topicInterests,
      'activityPatterns': activityPatterns.map(
        (k, v) => MapEntry(
          k, 
          v.map((time) => {
            'hour': time.hour,
            'minute': time.minute,
          }).toList(),
        ),
      ),
      'healthGoals': healthGoals,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
    };
  }
  
  /// 创建更新后的用户画像
  UserProfile copyWith({
    InteractionComplexityLevel? preferredComplexity,
    InteractionStyle? preferredStyle,
    Map<String, double>? learningCurves,
    Map<String, double>? topicInterests,
    Map<String, List<TimeOfDay>>? activityPatterns,
    List<String>? healthGoals,
  }) {
    return UserProfile(
      userId: this.userId,
      preferredComplexity: preferredComplexity ?? this.preferredComplexity,
      preferredStyle: preferredStyle ?? this.preferredStyle,
      learningCurves: learningCurves ?? Map.from(this.learningCurves),
      topicInterests: topicInterests ?? Map.from(this.topicInterests),
      activityPatterns: activityPatterns ?? Map.from(this.activityPatterns),
      healthGoals: healthGoals ?? List.from(this.healthGoals),
      createdAt: this.createdAt,
      updatedAt: DateTime.now(),
    );
  }
}

/// 时间段
class TimeOfDay {
  /// 小时 (0-23)
  final int hour;
  
  /// 分钟 (0-59)
  final int minute;
  
  /// 构造函数
  const TimeOfDay({
    required this.hour,
    required this.minute,
  });
  
  @override
  bool operator ==(Object other) =>
    other is TimeOfDay &&
    other.hour == hour &&
    other.minute == minute;
    
  @override
  int get hashCode => Object.hash(hour, minute);
  
  @override
  String toString() => '$hour:${minute.toString().padLeft(2, '0')}';
}

/// 交互事件类型
enum InteractionEventType {
  /// 点击
  tap,
  
  /// 长按
  longPress,
  
  /// 滚动
  scroll,
  
  /// 导航
  navigate,
  
  /// 输入
  input,
  
  /// 查询
  query,
  
  /// 选择
  select,
}

/// 交互事件
class InteractionEvent {
  /// 事件ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 事件类型
  final InteractionEventType type;
  
  /// 事件目标（例如，组件ID或路径）
  final String target;
  
  /// 事件数据
  final Map<String, dynamic> data;
  
  /// 事件发生时间
  final DateTime timestamp;
  
  /// 会话ID
  final String sessionId;
  
  /// 当前认知负荷估计
  final CognitiveLoadLevel? cognitiveLoadEstimate;
  
  /// 当前情感状态估计
  final EmotionalStateType? emotionalStateEstimate;

  /// 构造函数
  InteractionEvent({
    required this.id,
    required this.userId,
    required this.type,
    required this.target,
    required this.data,
    required this.sessionId,
    DateTime? timestamp,
    this.cognitiveLoadEstimate,
    this.emotionalStateEstimate,
  }) : this.timestamp = timestamp ?? DateTime.now();
  
  /// 从JSON创建
  factory InteractionEvent.fromJson(Map<String, dynamic> json) {
    return InteractionEvent(
      id: json['id'] as String,
      userId: json['userId'] as String,
      type: InteractionEventType.values.firstWhere(
        (e) => e.toString() == json['type'],
      ),
      target: json['target'] as String,
      data: json['data'] as Map<String, dynamic>,
      sessionId: json['sessionId'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      cognitiveLoadEstimate: json['cognitiveLoadEstimate'] != null
        ? CognitiveLoadLevel.values.firstWhere(
            (e) => e.toString() == json['cognitiveLoadEstimate'],
          )
        : null,
      emotionalStateEstimate: json['emotionalStateEstimate'] != null
        ? EmotionalStateType.values.firstWhere(
            (e) => e.toString() == json['emotionalStateEstimate'],
          )
        : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'type': type.toString(),
      'target': target,
      'data': data,
      'sessionId': sessionId,
      'timestamp': timestamp.toIso8601String(),
      'cognitiveLoadEstimate': cognitiveLoadEstimate?.toString(),
      'emotionalStateEstimate': emotionalStateEstimate?.toString(),
    };
  }
}

/// 认知负荷评估
class CognitiveLoadAssessment {
  /// 用户ID
  final String userId;
  
  /// 当前认知负荷级别
  final CognitiveLoadLevel currentLevel;
  
  /// 认知负荷分数 (0-100)
  final double score;
  
  /// 评估时间
  final DateTime timestamp;
  
  /// 评估数据
  final Map<String, dynamic> assessmentData;
  
  /// 构造函数
  CognitiveLoadAssessment({
    required this.userId,
    required this.currentLevel,
    required this.score,
    required this.assessmentData,
    DateTime? timestamp,
  }) : this.timestamp = timestamp ?? DateTime.now();
  
  /// 从JSON创建
  factory CognitiveLoadAssessment.fromJson(Map<String, dynamic> json) {
    return CognitiveLoadAssessment(
      userId: json['userId'] as String,
      currentLevel: CognitiveLoadLevel.values.firstWhere(
        (e) => e.toString() == json['currentLevel'],
      ),
      score: json['score'] as double,
      assessmentData: json['assessmentData'] as Map<String, dynamic>,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'currentLevel': currentLevel.toString(),
      'score': score,
      'assessmentData': assessmentData,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

/// 情感状态评估
class EmotionalStateAssessment {
  /// 用户ID
  final String userId;
  
  /// 主要情感状态
  final EmotionalStateType primaryState;
  
  /// 情感强度 (0-100)
  final double intensity;
  
  /// 情感混合（次要情感状态及其强度）
  final Map<EmotionalStateType, double> mixedStates;
  
  /// 评估时间
  final DateTime timestamp;
  
  /// 评估数据
  final Map<String, dynamic> assessmentData;
  
  /// 构造函数
  EmotionalStateAssessment({
    required this.userId,
    required this.primaryState,
    required this.intensity,
    required this.assessmentData,
    Map<EmotionalStateType, double>? mixedStates,
    DateTime? timestamp,
  }) : 
    this.mixedStates = mixedStates ?? {},
    this.timestamp = timestamp ?? DateTime.now();
  
  /// 从JSON创建
  factory EmotionalStateAssessment.fromJson(Map<String, dynamic> json) {
    final mixedStatesMap = <EmotionalStateType, double>{};
    
    if (json['mixedStates'] != null) {
      (json['mixedStates'] as Map<String, dynamic>).forEach((key, value) {
        final emotionalState = EmotionalStateType.values.firstWhere(
          (e) => e.toString() == key,
          orElse: () => EmotionalStateType.neutral,
        );
        mixedStatesMap[emotionalState] = value as double;
      });
    }
    
    return EmotionalStateAssessment(
      userId: json['userId'] as String,
      primaryState: EmotionalStateType.values.firstWhere(
        (e) => e.toString() == json['primaryState'],
        orElse: () => EmotionalStateType.neutral,
      ),
      intensity: json['intensity'] as double,
      mixedStates: mixedStatesMap,
      assessmentData: json['assessmentData'] as Map<String, dynamic>,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    final mixedStatesJson = <String, double>{};
    
    mixedStates.forEach((key, value) {
      mixedStatesJson[key.toString()] = value;
    });
    
    return {
      'userId': userId,
      'primaryState': primaryState.toString(),
      'intensity': intensity,
      'mixedStates': mixedStatesJson,
      'assessmentData': assessmentData,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

/// 个性化建议
class PersonalizationRecommendation {
  /// 建议ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 建议类型
  final String type;
  
  /// 建议内容
  final Map<String, dynamic> content;
  
  /// 置信度 (0-100)
  final double confidence;
  
  /// 建议生成时间
  final DateTime timestamp;
  
  /// 建议是否已应用
  final bool applied;
  
  /// 应用后的反馈
  final Map<String, dynamic>? feedback;

  /// 构造函数
  PersonalizationRecommendation({
    required this.id,
    required this.userId,
    required this.type,
    required this.content,
    required this.confidence,
    this.applied = false,
    this.feedback,
    DateTime? timestamp,
  }) : this.timestamp = timestamp ?? DateTime.now();
  
  /// 从JSON创建
  factory PersonalizationRecommendation.fromJson(Map<String, dynamic> json) {
    return PersonalizationRecommendation(
      id: json['id'] as String,
      userId: json['userId'] as String,
      type: json['type'] as String,
      content: json['content'] as Map<String, dynamic>,
      confidence: json['confidence'] as double,
      applied: json['applied'] as bool? ?? false,
      feedback: json['feedback'] as Map<String, dynamic>?,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'type': type,
      'content': content,
      'confidence': confidence,
      'applied': applied,
      'feedback': feedback,
      'timestamp': timestamp.toIso8601String(),
    };
  }
  
  /// 创建应用后的建议
  PersonalizationRecommendation markAsApplied({
    Map<String, dynamic>? feedback,
  }) {
    return PersonalizationRecommendation(
      id: this.id,
      userId: this.userId,
      type: this.type,
      content: this.content,
      confidence: this.confidence,
      applied: true,
      feedback: feedback ?? this.feedback,
      timestamp: this.timestamp,
    );
  }
}

/// 个性化方案
class PersonalizationScheme {
  /// 方案ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 交互复杂度调整
  final InteractionComplexityLevel complexityLevel;
  
  /// 交互风格调整
  final InteractionStyle interactionStyle;
  
  /// 内容呈现调整
  final Map<String, dynamic> contentAdjustments;
  
  /// UI布局调整
  final Map<String, dynamic> layoutAdjustments;
  
  /// 导航调整
  final Map<String, dynamic> navigationAdjustments;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 上次应用时间
  final DateTime? lastApplied;

  /// 构造函数
  PersonalizationScheme({
    required this.id,
    required this.userId,
    required this.complexityLevel,
    required this.interactionStyle,
    required this.contentAdjustments,
    required this.layoutAdjustments,
    required this.navigationAdjustments,
    DateTime? createdAt,
    this.lastApplied,
  }) : this.createdAt = createdAt ?? DateTime.now();
  
  /// 从JSON创建
  factory PersonalizationScheme.fromJson(Map<String, dynamic> json) {
    return PersonalizationScheme(
      id: json['id'] as String,
      userId: json['userId'] as String,
      complexityLevel: InteractionComplexityLevel.values.firstWhere(
        (e) => e.toString() == json['complexityLevel'],
        orElse: () => InteractionComplexityLevel.standard,
      ),
      interactionStyle: InteractionStyle.values.firstWhere(
        (e) => e.toString() == json['interactionStyle'],
        orElse: () => InteractionStyle.detailed,
      ),
      contentAdjustments: json['contentAdjustments'] as Map<String, dynamic>,
      layoutAdjustments: json['layoutAdjustments'] as Map<String, dynamic>,
      navigationAdjustments: json['navigationAdjustments'] as Map<String, dynamic>,
      createdAt: DateTime.parse(json['createdAt'] as String),
      lastApplied: json['lastApplied'] != null 
        ? DateTime.parse(json['lastApplied'] as String)
        : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'complexityLevel': complexityLevel.toString(),
      'interactionStyle': interactionStyle.toString(),
      'contentAdjustments': contentAdjustments,
      'layoutAdjustments': layoutAdjustments,
      'navigationAdjustments': navigationAdjustments,
      'createdAt': createdAt.toIso8601String(),
      'lastApplied': lastApplied?.toIso8601String(),
    };
  }
  
  /// 创建更新后的方案
  PersonalizationScheme copyWith({
    InteractionComplexityLevel? complexityLevel,
    InteractionStyle? interactionStyle,
    Map<String, dynamic>? contentAdjustments,
    Map<String, dynamic>? layoutAdjustments,
    Map<String, dynamic>? navigationAdjustments,
    DateTime? lastApplied,
  }) {
    return PersonalizationScheme(
      id: this.id,
      userId: this.userId,
      complexityLevel: complexityLevel ?? this.complexityLevel,
      interactionStyle: interactionStyle ?? this.interactionStyle,
      contentAdjustments: contentAdjustments ?? Map.from(this.contentAdjustments),
      layoutAdjustments: layoutAdjustments ?? Map.from(this.layoutAdjustments),
      navigationAdjustments: navigationAdjustments ?? Map.from(this.navigationAdjustments),
      createdAt: this.createdAt,
      lastApplied: lastApplied ?? this.lastApplied,
    );
  }
  
  /// 标记为已应用
  PersonalizationScheme markAsApplied() {
    return copyWith(lastApplied: DateTime.now());
  }
}

/// 个性化适应系统接口
abstract class PersonalizationSystem {
  /// 获取系统ID
  String get id;
  
  /// 创建或更新用户画像
  Future<UserProfile> createOrUpdateUserProfile(UserProfile profile);
  
  /// 获取用户画像
  Future<UserProfile?> getUserProfile(String userId);
  
  /// 记录交互事件
  Future<void> recordInteractionEvent(InteractionEvent event);
  
  /// 获取用户交互事件
  Future<List<InteractionEvent>> getUserInteractionEvents(
    String userId, {
    DateTime? startTime,
    DateTime? endTime,
    int? limit,
    InteractionEventType? type,
  });
  
  /// 评估用户认知负荷
  Future<CognitiveLoadAssessment> assessCognitiveLoad(
    String userId, {
    List<InteractionEvent>? recentEvents,
  });
  
  /// 评估用户情感状态
  Future<EmotionalStateAssessment> assessEmotionalState(
    String userId, {
    List<InteractionEvent>? recentEvents,
  });
  
  /// 生成个性化建议
  Future<List<PersonalizationRecommendation>> generateRecommendations(
    String userId, {
    String? context,
    List<String>? types,
  });
  
  /// 记录建议反馈
  Future<PersonalizationRecommendation> recordRecommendationFeedback(
    String recommendationId,
    bool applied,
    Map<String, dynamic>? feedbackData,
  );
  
  /// 创建个性化方案
  Future<PersonalizationScheme> createPersonalizationScheme(
    String userId, {
    InteractionComplexityLevel? complexityLevel,
    InteractionStyle? interactionStyle,
    Map<String, dynamic>? contentAdjustments,
    Map<String, dynamic>? layoutAdjustments,
    Map<String, dynamic>? navigationAdjustments,
  });
  
  /// 获取当前个性化方案
  Future<PersonalizationScheme?> getCurrentScheme(String userId);
  
  /// 应用个性化方案
  Future<bool> applyScheme(String schemeId);
  
  /// 获取个性化方案历史
  Future<List<PersonalizationScheme>> getSchemeHistory(
    String userId, {
    int? limit,
    DateTime? startTime,
    DateTime? endTime,
  });
  
  /// 学习率统计
  Future<Map<String, double>> analyzeLearningRates(
    String userId, {
    List<String>? domains,
    DateTime? startTime,
    DateTime? endTime,
  });
  
  /// 更新交互偏好
  Future<UserProfile> updateInteractionPreferences(
    String userId, {
    InteractionComplexityLevel? preferredComplexity,
    InteractionStyle? preferredStyle,
  });
  
  /// 重置为默认设置
  Future<PersonalizationScheme> resetToDefaults(String userId);
}

/// 个性化适应系统实现
class PersonalizationSystemImpl implements PersonalizationSystem {
  final AIAgent _agent;
  final AutonomousLearningSystem _learningSystem;
  final SecurityPrivacyFramework _securityFramework;
  final RAGService _ragService;
  final UserRepository _userRepository;
  
  final Map<String, UserProfile> _userProfiles = {};
  final Map<String, List<InteractionEvent>> _interactionEvents = {};
  final Map<String, List<CognitiveLoadAssessment>> _cognitiveLoadHistory = {};
  final Map<String, List<EmotionalStateAssessment>> _emotionalStateHistory = {};
  final Map<String, List<PersonalizationRecommendation>> _recommendations = {};
  final Map<String, List<PersonalizationScheme>> _personalizationSchemes = {};
  
  /// 当前会话ID
  String? _currentSessionId;
  
  /// 构造函数
  PersonalizationSystemImpl({
    required AIAgent agent,
    required AutonomousLearningSystem learningSystem,
    required SecurityPrivacyFramework securityFramework,
    required RAGService ragService,
    required UserRepository userRepository,
  }) :
    _agent = agent,
    _learningSystem = learningSystem,
    _securityFramework = securityFramework,
    _ragService = ragService,
    _userRepository = userRepository {
    _initialize();
  }
  
  void _initialize() {
    // 初始化操作，可能包括加载预训练模型、连接数据库等
    Logger.d('PersonalizationSystem', 'Initializing...');
    _currentSessionId = 'session_${DateTime.now().millisecondsSinceEpoch}';
  }
  
  @override
  String get id => _agent.id;
  
  @override
  Future<UserProfile> createOrUpdateUserProfile(UserProfile profile) async {
    try {
      // 在实际应用中，这里应该与永久存储交互
      final existingProfile = _userProfiles[profile.userId];
      
      if (existingProfile != null) {
        // 更新现有画像
        final updatedProfile = UserProfile(
          userId: profile.userId,
          preferredComplexity: profile.preferredComplexity,
          preferredStyle: profile.preferredStyle,
          learningCurves: profile.learningCurves,
          topicInterests: profile.topicInterests,
          activityPatterns: profile.activityPatterns,
          healthGoals: profile.healthGoals,
          createdAt: existingProfile.createdAt,
          updatedAt: DateTime.now(),
        );
        
        _userProfiles[profile.userId] = updatedProfile;
        
        // 记录学习数据
        await _learningSystem.collectData(LearningDataItem(
          id: 'profile_update_${DateTime.now().millisecondsSinceEpoch}',
          type: LearningDataType.userProfile,
          source: LearningDataSource.personalizationSystem,
          content: {
            'userId': profile.userId,
            'action': 'update_profile',
            'changes': _detectProfileChanges(existingProfile, updatedProfile),
          },
          timestamp: DateTime.now(),
        ));
        
        return updatedProfile;
      } else {
        // 创建新画像
        final newProfile = UserProfile(
          userId: profile.userId,
          preferredComplexity: profile.preferredComplexity,
          preferredStyle: profile.preferredStyle,
          learningCurves: profile.learningCurves,
          topicInterests: profile.topicInterests,
          activityPatterns: profile.activityPatterns,
          healthGoals: profile.healthGoals,
        );
        
        _userProfiles[profile.userId] = newProfile;
        
        // 记录学习数据
        await _learningSystem.collectData(LearningDataItem(
          id: 'profile_create_${DateTime.now().millisecondsSinceEpoch}',
          type: LearningDataType.userProfile,
          source: LearningDataSource.personalizationSystem,
          content: {
            'userId': profile.userId,
            'action': 'create_profile',
          },
          timestamp: DateTime.now(),
        ));
        
        return newProfile;
      }
    } catch (e) {
      Logger.e('PersonalizationSystem', 'Error creating/updating user profile: $e');
      rethrow;
    }
  }
  
  /// 检测用户画像变化
  Map<String, dynamic> _detectProfileChanges(
    UserProfile oldProfile,
    UserProfile newProfile,
  ) {
    final changes = <String, dynamic>{};
    
    if (oldProfile.preferredComplexity != newProfile.preferredComplexity) {
      changes['preferredComplexity'] = {
        'from': oldProfile.preferredComplexity.toString(),
        'to': newProfile.preferredComplexity.toString(),
      };
    }
    
    if (oldProfile.preferredStyle != newProfile.preferredStyle) {
      changes['preferredStyle'] = {
        'from': oldProfile.preferredStyle.toString(),
        'to': newProfile.preferredStyle.toString(),
      };
    }
    
    // 检测学习曲线变化
    final learningCurveChanges = <String, Map<String, double>>{};
    for (final entry in newProfile.learningCurves.entries) {
      if (oldProfile.learningCurves[entry.key] != entry.value) {
        learningCurveChanges[entry.key] = {
          'from': oldProfile.learningCurves[entry.key] ?? 0.0,
          'to': entry.value,
        };
      }
    }
    
    if (learningCurveChanges.isNotEmpty) {
      changes['learningCurves'] = learningCurveChanges;
    }
    
    // 检测健康目标变化
    if (!listEquals(oldProfile.healthGoals, newProfile.healthGoals)) {
      changes['healthGoals'] = {
        'from': oldProfile.healthGoals,
        'to': newProfile.healthGoals,
      };
    }
    
    return changes;
  }
  
  @override
  Future<UserProfile?> getUserProfile(String userId) async {
    // 在实际应用中，这里应该查询永久存储
    return _userProfiles[userId];
  }
  
  @override
  Future<void> recordInteractionEvent(InteractionEvent event) async {
    try {
      // 在实际应用中，这里应该与永久存储交互
      _interactionEvents.putIfAbsent(event.userId, () => []);
      _interactionEvents[event.userId]!.add(event);
      
      // 记录学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: 'interaction_${DateTime.now().millisecondsSinceEpoch}',
        type: LearningDataType.userInteraction,
        source: LearningDataSource.personalizationSystem,
        content: {
          'userId': event.userId,
          'eventType': event.type.toString(),
          'target': event.target,
        },
        timestamp: DateTime.now(),
      ));
      
      // 当有一定数量的事件时，触发认知负荷和情感状态评估
      final recentEvents = _getRecentEvents(event.userId, limit: 10);
      if (recentEvents.length >= 5) {
        await assessCognitiveLoad(event.userId, recentEvents: recentEvents);
        await assessEmotionalState(event.userId, recentEvents: recentEvents);
      }
    } catch (e) {
      Logger.e('PersonalizationSystem', 'Error recording interaction event: $e');
      rethrow;
    }
  }
  
  /// 获取近期事件
  List<InteractionEvent> _getRecentEvents(String userId, {int limit = 10}) {
    final events = _interactionEvents[userId] ?? [];
    events.sort((a, b) => b.timestamp.compareTo(a.timestamp)); // 按时间降序排序
    return events.take(limit).toList();
  }
  
  @override
  Future<List<InteractionEvent>> getUserInteractionEvents(
    String userId, {
    DateTime? startTime,
    DateTime? endTime,
    int? limit,
    InteractionEventType? type,
  }) async {
    // 在实际应用中，这里应该查询永久存储
    var events = _interactionEvents[userId] ?? [];
    
    if (startTime != null) {
      events = events.where((e) => e.timestamp.isAfter(startTime)).toList();
    }
    
    if (endTime != null) {
      events = events.where((e) => e.timestamp.isBefore(endTime)).toList();
    }
    
    if (type != null) {
      events = events.where((e) => e.type == type).toList();
    }
    
    // 按时间降序排序
    events.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    
    if (limit != null && events.length > limit) {
      events = events.sublist(0, limit);
    }
    
    return events;
  }
  
  @override
  Future<CognitiveLoadAssessment> assessCognitiveLoad(
    String userId, {
    List<InteractionEvent>? recentEvents,
  }) async {
    try {
      // 获取最近的交互事件
      final events = recentEvents ?? await getUserInteractionEvents(
        userId,
        limit: 10,
      );
      
      if (events.isEmpty) {
        // 没有足够的数据进行评估，返回默认结果
        return CognitiveLoadAssessment(
          userId: userId,
          currentLevel: CognitiveLoadLevel.medium,
          score: 50.0,
          assessmentData: {'status': 'insufficient_data'},
        );
      }
      
      // 在实际应用中，这里应该使用复杂的评估算法
      // 这里使用简化的实现
      
      // 计算事件频率 (过去5分钟内的事件数)
      final now = DateTime.now();
      final fiveMinutesAgo = now.subtract(Duration(minutes: 5));
      final recentEventCount = events.where(
        (e) => e.timestamp.isAfter(fiveMinutesAgo)
      ).length;
      
      // 计算导航变化频率
      final navigationEvents = events.where((e) => e.type == InteractionEventType.navigate).length;
      
      // 计算输入事件比例
      final inputEvents = events.where(
        (e) => e.type == InteractionEventType.input || e.type == InteractionEventType.query
      ).length;
      
      final inputRatio = events.isEmpty ? 0.0 : inputEvents / events.length;
      
      // 结合指标计算认知负荷分数
      double score = 50.0; // 默认中等
      
      // 事件频率影响 (0-40)
      score += math.min(recentEventCount * 4.0, 40.0);
      
      // 导航变化影响 (0-30)
      score += math.min(navigationEvents * 3.0, 30.0);
      
      // 输入比例影响 (0-30)
      score += inputRatio * 30.0;
      
      // 规范分数到0-100范围
      score = math.min(math.max(0.0, score), 100.0);
      
      // 确定认知负荷级别
      CognitiveLoadLevel currentLevel;
      if (score < 30.0) {
        currentLevel = CognitiveLoadLevel.low;
      } else if (score < 60.0) {
        currentLevel = CognitiveLoadLevel.medium;
      } else if (score < 85.0) {
        currentLevel = CognitiveLoadLevel.high;
      } else {
        currentLevel = CognitiveLoadLevel.overloaded;
      }
      
      return CognitiveLoadAssessment(
        userId: userId,
        currentLevel: currentLevel,
        score: score,
        assessmentData: {'status': 'success'},
      );
    } catch (e) {
      Logger.e('PersonalizationSystem', 'Error assessing cognitive load: $e');
      rethrow;
    }
  }
  
  @override
  Future<EmotionalStateAssessment> assessEmotionalState(
    String userId, {
    List<InteractionEvent>? recentEvents,
  }) async {
    try {
      // 获取最近的交互事件
      final events = recentEvents ?? await getUserInteractionEvents(
        userId,
        limit: 10,
      );
      
      if (events.isEmpty) {
        // 没有足够的数据进行评估，返回默认结果
        return EmotionalStateAssessment(
          userId: userId,
          primaryState: EmotionalStateType.neutral,
          intensity: 50.0,
          assessmentData: {'status': 'insufficient_data'},
        );
      }
      
      // 在实际应用中，这里应该使用复杂的评估算法
      // 这里使用简化的实现
      
      // 计算情感强度
      double intensity = 50.0; // 默认中等
      
      // 事件影响
      for (final event in events) {
        if (event.emotionalStateEstimate != null) {
          intensity += 10.0; // 每次检测到情感状态时增加强度
        }
      }
      
      // 规范强度到0-100范围
      intensity = math.min(math.max(0.0, intensity), 100.0);
      
      // 确定主要情感状态 (简化实现，实际应用中应使用更复杂的算法)
      EmotionalStateType primaryState = EmotionalStateType.neutral;
      Map<EmotionalStateType, double> mixedStates = {};
      
      // 模拟情感状态检测
      final random = math.Random();
      final emotionalTypes = EmotionalStateType.values;
      primaryState = emotionalTypes[random.nextInt(emotionalTypes.length)];
      
      // 添加混合情感状态
      for (var i = 0; i < 2; i++) {
        final state = emotionalTypes[random.nextInt(emotionalTypes.length)];
        if (state != primaryState) {
          mixedStates[state] = (random.nextDouble() * 50.0); // 次要情感强度较低
        }
      }
      
      return EmotionalStateAssessment(
        userId: userId,
        primaryState: primaryState,
        intensity: intensity,
        mixedStates: mixedStates,
        assessmentData: {'status': 'success'},
      );
    } catch (e) {
      Logger.e('PersonalizationSystem', 'Error assessing emotional state: $e');
      rethrow;
    }
  }
  
  @override
  Future<List<PersonalizationRecommendation>> generateRecommendations(
    String userId, {
    String? context,
    List<String>? types,
  }) async {
    // 实现生成个性化建议的逻辑
    // 这里需要根据用户画像和上下文生成建议
    // 这里使用简化的实现，实际应用中应该根据更复杂的算法生成建议
    return [
      PersonalizationRecommendation(
        id: 'recommendation_${DateTime.now().millisecondsSinceEpoch}',
        userId: userId,
        type: 'general',
        content: {'message': 'Here is a general recommendation'},
        confidence: 80.0,
      ),
      PersonalizationRecommendation(
        id: 'recommendation_${DateTime.now().millisecondsSinceEpoch + 1}',
        userId: userId,
        type: 'specific',
        content: {'message': 'Here is a specific recommendation'},
        confidence: 90.0,
      ),
    ];
  }
  
  @override
  Future<PersonalizationRecommendation> recordRecommendationFeedback(
    String recommendationId,
    bool applied,
    Map<String, dynamic>? feedbackData,
  ) async {
    // 实现记录建议反馈的逻辑
    // 这里需要将反馈数据存储到永久存储中
    // 这里使用简化的实现，实际应用中应该根据更复杂的逻辑处理反馈
    return PersonalizationRecommendation(
      id: recommendationId,
      userId: 'user_${DateTime.now().millisecondsSinceEpoch}',
      type: 'general',
      content: {'message': 'Feedback received'},
      confidence: 50.0,
      applied: applied,
      feedback: feedbackData,
    );
  }
  
  @override
  Future<PersonalizationScheme> createPersonalizationScheme(
    String userId, {
    InteractionComplexityLevel? complexityLevel,
    InteractionStyle? interactionStyle,
    Map<String, dynamic>? contentAdjustments,
    Map<String, dynamic>? layoutAdjustments,
    Map<String, dynamic>? navigationAdjustments,
  }) async {
    // 实现创建个性化方案的逻辑
    // 这里需要根据用户画像和需求生成个性化方案
    // 这里使用简化的实现，实际应用中应该根据更复杂的逻辑生成方案
    return PersonalizationScheme(
      id: 'scheme_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      complexityLevel: complexityLevel ?? InteractionComplexityLevel.standard,
      interactionStyle: interactionStyle ?? InteractionStyle.detailed,
      contentAdjustments: contentAdjustments ?? {},
      layoutAdjustments: layoutAdjustments ?? {},
      navigationAdjustments: navigationAdjustments ?? {},
    );
  }
  
  @override
  Future<PersonalizationScheme?> getCurrentScheme(String userId) async {
    // 实现获取当前个性化方案的逻辑
    // 这里需要从永久存储中获取当前方案
    // 这里使用简化的实现，实际应用中应该根据更复杂的逻辑获取方案
    return _personalizationSchemes[userId]?.firstOrNull;
  }
  
  @override
  Future<bool> applyScheme(String schemeId) async {
    // 实现应用个性化方案的逻辑
    // 这里需要从永久存储中获取方案并应用
    // 这里使用简化的实现，实际应用中应该根据更复杂的逻辑应用方案
    final scheme = await getCurrentScheme('user_${DateTime.now().millisecondsSinceEpoch}');
    if (scheme != null) {
      // 应用方案逻辑
      return true;
    } else {
      throw Exception('Scheme not found');
    }
  }
  
  @override
  Future<List<PersonalizationScheme>> getSchemeHistory(
    String userId, {
    int? limit,
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    // 实现获取个性化方案历史的逻辑
    // 这里需要从永久存储中获取历史方案
    // 这里使用简化的实现，实际应用中应该根据更复杂的逻辑获取历史方案
    return _personalizationSchemes[userId]?.take(limit ?? 10).toList() ?? [];
  }
  
  @override
  Future<Map<String, double>> analyzeLearningRates(
    String userId, {
    List<String>? domains,
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    // 实现学习率统计的逻辑
    // 这里需要从永久存储中获取学习数据并分析学习率
    // 这里使用简化的实现，实际应用中应该根据更复杂的逻辑分析学习率
    return {'learning_rate': 0.0}; // 临时返回，实际应用中需要实现
  }
  
  @override
  Future<UserProfile> updateInteractionPreferences(
    String userId, {
    InteractionComplexityLevel? preferredComplexity,
    InteractionStyle? preferredStyle,
  }) async {
    // 实现更新交互偏好的逻辑
    // 这里需要从永久存储中获取用户画像并更新偏好
    // 这里使用简化的实现，实际应用中应该根据更复杂的逻辑更新偏好
    final profile = await getUserProfile(userId);
    if (profile != null) {
      return profile.copyWith(
        preferredComplexity: preferredComplexity ?? profile.preferredComplexity,
        preferredStyle: preferredStyle ?? profile.preferredStyle,
      );
    } else {
      throw Exception('User profile not found');
    }
  }
  
  @override
  Future<PersonalizationScheme> resetToDefaults(String userId) async {
    // 实现重置为默认设置的逻辑
    // 这里需要从永久存储中获取用户画像并重置为默认设置
    // 这里使用简化的实现，实际应用中应该根据更复杂的逻辑重置为默认设置
    final profile = await getUserProfile(userId);
    if (profile != null) {
      return PersonalizationScheme(
        id: 'default_scheme_${DateTime.now().millisecondsSinceEpoch}',
        userId: userId,
        complexityLevel: InteractionComplexityLevel.standard,
        interactionStyle: InteractionStyle.detailed,
        contentAdjustments: {},
        layoutAdjustments: {},
        navigationAdjustments: {},
      );
    } else {
      throw Exception('User profile not found');
    }
  }
}