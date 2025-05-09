import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';

/// 症状严重程度枚举
enum SymptomSeverity {
  /// 无
  none,
  
  /// 轻微
  mild,
  
  /// 中等
  moderate,
  
  /// 严重
  severe,
}

/// 症状持续时间枚举
enum SymptomDuration {
  /// 新发（1-3天）
  recent,
  
  /// 短期（一周内）
  shortTerm,
  
  /// 中期（一个月内）
  mediumTerm,
  
  /// 长期（超过一个月）
  longTerm,
  
  /// 慢性（反复发作超过3个月）
  chronic,
}

/// 情绪状态枚举
enum EmotionalState {
  /// 平静
  calm,
  
  /// 焦虑
  anxious,
  
  /// 抑郁
  depressed,
  
  /// 易怒
  irritable,
  
  /// 情绪波动
  mood_swings,
}

/// 睡眠质量枚举
enum SleepQuality {
  /// 良好
  good,
  
  /// 一般
  average,
  
  /// 较差
  poor,
  
  /// 严重失眠
  insomnia,
}

/// 食欲状态枚举
enum AppetiteState {
  /// 正常
  normal,
  
  /// 食欲增加
  increased,
  
  /// 食欲减退
  decreased,
  
  /// 明显厌食
  poor,
}

/// 问诊数据模型
class InquiryData extends Equatable {
  /// 问诊ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 主要症状
  final List<String> mainSymptoms;
  
  /// 症状严重程度
  final SymptomSeverity severity;
  
  /// 症状持续时间
  final SymptomDuration duration;
  
  /// 伴随症状
  final List<String>? secondarySymptoms;
  
  /// 情绪状态
  final EmotionalState emotionalState;
  
  /// 睡眠质量
  final SleepQuality sleepQuality;
  
  /// 食欲状态
  final AppetiteState appetite;
  
  /// 饮水情况 (每日杯数)
  final int? waterIntake;
  
  /// 是否有规律运动
  final bool regularExercise;
  
  /// 饮食偏好 (例如：辛辣、寒凉等)
  final List<String>? dietaryPreferences;
  
  /// 过敏史
  final List<String>? allergies;
  
  /// 既往病史
  final List<String>? medicalHistory;
  
  /// 备注信息
  final String? notes;

  /// 构造函数
  const InquiryData({
    required this.id,
    required this.userId,
    required this.createdAt,
    required this.mainSymptoms,
    required this.severity,
    required this.duration,
    this.secondarySymptoms,
    required this.emotionalState,
    required this.sleepQuality,
    required this.appetite,
    this.waterIntake,
    required this.regularExercise,
    this.dietaryPreferences,
    this.allergies,
    this.medicalHistory,
    this.notes,
  });

  /// 创建新的问诊数据
  factory InquiryData.create({
    required String userId,
    required List<String> mainSymptoms,
    required SymptomSeverity severity,
    required SymptomDuration duration,
    List<String>? secondarySymptoms,
    required EmotionalState emotionalState,
    required SleepQuality sleepQuality,
    required AppetiteState appetite,
    int? waterIntake,
    required bool regularExercise,
    List<String>? dietaryPreferences,
    List<String>? allergies,
    List<String>? medicalHistory,
    String? notes,
  }) {
    return InquiryData(
      id: const Uuid().v4(),
      userId: userId,
      createdAt: DateTime.now(),
      mainSymptoms: mainSymptoms,
      severity: severity,
      duration: duration,
      secondarySymptoms: secondarySymptoms,
      emotionalState: emotionalState,
      sleepQuality: sleepQuality,
      appetite: appetite,
      waterIntake: waterIntake,
      regularExercise: regularExercise,
      dietaryPreferences: dietaryPreferences,
      allergies: allergies,
      medicalHistory: medicalHistory,
      notes: notes,
    );
  }
  
  /// 获取症状严重程度描述
  String get severityDescription {
    switch (severity) {
      case SymptomSeverity.none:
        return '无';
      case SymptomSeverity.mild:
        return '轻微';
      case SymptomSeverity.moderate:
        return '中等';
      case SymptomSeverity.severe:
        return '严重';
    }
  }
  
  /// 获取症状持续时间描述
  String get durationDescription {
    switch (duration) {
      case SymptomDuration.recent:
        return '新发（1-3天）';
      case SymptomDuration.shortTerm:
        return '短期（一周内）';
      case SymptomDuration.mediumTerm:
        return '中期（一个月内）';
      case SymptomDuration.longTerm:
        return '长期（超过一个月）';
      case SymptomDuration.chronic:
        return '慢性（反复发作超过3个月）';
    }
  }
  
  /// 获取情绪状态描述
  String get emotionalStateDescription {
    switch (emotionalState) {
      case EmotionalState.calm:
        return '平静';
      case EmotionalState.anxious:
        return '焦虑';
      case EmotionalState.depressed:
        return '抑郁';
      case EmotionalState.irritable:
        return '易怒';
      case EmotionalState.mood_swings:
        return '情绪波动';
    }
  }
  
  /// 获取睡眠质量描述
  String get sleepQualityDescription {
    switch (sleepQuality) {
      case SleepQuality.good:
        return '良好';
      case SleepQuality.average:
        return '一般';
      case SleepQuality.poor:
        return '较差';
      case SleepQuality.insomnia:
        return '严重失眠';
    }
  }
  
  /// 获取食欲状态描述
  String get appetiteDescription {
    switch (appetite) {
      case AppetiteState.normal:
        return '正常';
      case AppetiteState.increased:
        return '食欲增加';
      case AppetiteState.decreased:
        return '食欲减退';
      case AppetiteState.poor:
        return '明显厌食';
    }
  }

  /// 从JSON创建问诊数据
  factory InquiryData.fromJson(Map<String, dynamic> json) {
    return InquiryData(
      id: json['id'],
      userId: json['user_id'],
      createdAt: DateTime.parse(json['created_at']),
      mainSymptoms: List<String>.from(json['main_symptoms']),
      severity: SymptomSeverity.values.byName(json['severity']),
      duration: SymptomDuration.values.byName(json['duration']),
      secondarySymptoms: json['secondary_symptoms'] != null
          ? List<String>.from(json['secondary_symptoms'])
          : null,
      emotionalState: EmotionalState.values.byName(json['emotional_state']),
      sleepQuality: SleepQuality.values.byName(json['sleep_quality']),
      appetite: AppetiteState.values.byName(json['appetite']),
      waterIntake: json['water_intake'],
      regularExercise: json['regular_exercise'],
      dietaryPreferences: json['dietary_preferences'] != null
          ? List<String>.from(json['dietary_preferences'])
          : null,
      allergies: json['allergies'] != null
          ? List<String>.from(json['allergies'])
          : null,
      medicalHistory: json['medical_history'] != null
          ? List<String>.from(json['medical_history'])
          : null,
      notes: json['notes'],
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'created_at': createdAt.toIso8601String(),
      'main_symptoms': mainSymptoms,
      'severity': severity.name,
      'duration': duration.name,
      'secondary_symptoms': secondarySymptoms,
      'emotional_state': emotionalState.name,
      'sleep_quality': sleepQuality.name,
      'appetite': appetite.name,
      'water_intake': waterIntake,
      'regular_exercise': regularExercise,
      'dietary_preferences': dietaryPreferences,
      'allergies': allergies,
      'medical_history': medicalHistory,
      'notes': notes,
    };
  }
  
  /// 复制问诊数据并修改部分属性
  InquiryData copyWith({
    String? id,
    String? userId,
    DateTime? createdAt,
    List<String>? mainSymptoms,
    SymptomSeverity? severity,
    SymptomDuration? duration,
    List<String>? secondarySymptoms,
    EmotionalState? emotionalState,
    SleepQuality? sleepQuality,
    AppetiteState? appetite,
    int? waterIntake,
    bool? regularExercise,
    List<String>? dietaryPreferences,
    List<String>? allergies,
    List<String>? medicalHistory,
    String? notes,
  }) {
    return InquiryData(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      createdAt: createdAt ?? this.createdAt,
      mainSymptoms: mainSymptoms ?? this.mainSymptoms,
      severity: severity ?? this.severity,
      duration: duration ?? this.duration,
      secondarySymptoms: secondarySymptoms ?? this.secondarySymptoms,
      emotionalState: emotionalState ?? this.emotionalState,
      sleepQuality: sleepQuality ?? this.sleepQuality,
      appetite: appetite ?? this.appetite,
      waterIntake: waterIntake ?? this.waterIntake,
      regularExercise: regularExercise ?? this.regularExercise,
      dietaryPreferences: dietaryPreferences ?? this.dietaryPreferences,
      allergies: allergies ?? this.allergies,
      medicalHistory: medicalHistory ?? this.medicalHistory,
      notes: notes ?? this.notes,
    );
  }

  @override
  List<Object?> get props => [
    id,
    userId,
    createdAt,
    mainSymptoms,
    severity,
    duration,
    secondarySymptoms,
    emotionalState,
    sleepQuality,
    appetite,
    waterIntake,
    regularExercise,
    dietaryPreferences,
    allergies,
    medicalHistory,
    notes,
  ];
} 