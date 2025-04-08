import 'package:suoke_life/core/services/context_aware_sensing_service.dart';

/// 环境上下文
class EnvironmentContext {
  /// 环境类型
  final EnvironmentType type;

  /// 光线级别 (lux)
  final double lightLevel;

  /// 噪音级别 (dB)
  final double noiseLevel;

  /// 位置数据 (可选)
  final Map<String, dynamic>? location;

  /// 时间戳
  final DateTime timestamp;

  /// 构造函数
  EnvironmentContext({
    required this.type,
    required this.lightLevel,
    required this.noiseLevel,
    this.location,
    required this.timestamp,
  });

  /// 创建未知环境上下文
  static EnvironmentContext unknown() {
    return EnvironmentContext(
      type: EnvironmentType.unknown,
      lightLevel: 0.0,
      noiseLevel: 0.0,
      location: null,
      timestamp: DateTime.now(),
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'type': type.toString(),
      'lightLevel': lightLevel,
      'noiseLevel': noiseLevel,
      'location': location,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  /// 从JSON创建
  factory EnvironmentContext.fromJson(Map<String, dynamic> json) {
    return EnvironmentContext(
      type: _parseEnvironmentType(json['type']),
      lightLevel: json['lightLevel'] ?? 0.0,
      noiseLevel: json['noiseLevel'] ?? 0.0,
      location: json['location'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }

  /// 解析环境类型
  static EnvironmentType _parseEnvironmentType(String? typeStr) {
    if (typeStr == null) return EnvironmentType.unknown;

    for (final type in EnvironmentType.values) {
      if (typeStr.contains(type.toString())) {
        return type;
      }
    }

    return EnvironmentType.unknown;
  }
}

/// 活动上下文
class ActivityContext {
  /// 活动状态
  final ActivityState state;

  /// 置信度 (0-100)
  final int confidence;

  /// 持续时间 (秒)
  int duration;

  /// 时间戳
  final DateTime timestamp;

  /// 构造函数
  ActivityContext({
    required this.state,
    required this.confidence,
    required this.duration,
    required this.timestamp,
  });

  /// 创建未知活动上下文
  static ActivityContext unknown() {
    return ActivityContext(
      state: ActivityState.unknown,
      confidence: 0,
      duration: 0,
      timestamp: DateTime.now(),
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'state': state.toString(),
      'confidence': confidence,
      'duration': duration,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  /// 从JSON创建
  factory ActivityContext.fromJson(Map<String, dynamic> json) {
    return ActivityContext(
      state: _parseActivityState(json['state']),
      confidence: json['confidence'] ?? 0,
      duration: json['duration'] ?? 0,
      timestamp: DateTime.parse(json['timestamp']),
    );
  }

  /// 解析活动状态
  static ActivityState _parseActivityState(String? stateStr) {
    if (stateStr == null) return ActivityState.unknown;

    for (final state in ActivityState.values) {
      if (stateStr.contains(state.toString())) {
        return state;
      }
    }

    return ActivityState.unknown;
  }
}

/// 用户上下文
class UserContext {
  /// 活动上下文
  final ActivityContext activity;

  /// 环境上下文
  final EnvironmentContext environment;

  /// 推断的状态描述
  final String inferredState;

  /// 时间戳
  final DateTime timestamp;

  /// 构造函数
  UserContext({
    required this.activity,
    required this.environment,
    required this.inferredState,
    required this.timestamp,
  });

  /// 创建未知用户上下文
  static UserContext unknown() {
    return UserContext(
      activity: ActivityContext.unknown(),
      environment: EnvironmentContext.unknown(),
      inferredState: '未知状态',
      timestamp: DateTime.now(),
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'activity': activity.toJson(),
      'environment': environment.toJson(),
      'inferredState': inferredState,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  /// 从JSON创建
  factory UserContext.fromJson(Map<String, dynamic> json) {
    return UserContext(
      activity: ActivityContext.fromJson(json['activity']),
      environment: EnvironmentContext.fromJson(json['environment']),
      inferredState: json['inferredState'] ?? '未知状态',
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}
