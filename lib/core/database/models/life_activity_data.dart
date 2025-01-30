import '../base/entity.dart';
import 'dart:convert';

/// 生活活动数据实体
class LifeActivityData extends Entity {
  final int? id;
  final String userId;
  final String type;
  final double value;
  final String unit;
  final int time;
  final int duration;
  final String? location;
  final String? notes;

  LifeActivityData({
    this.id,
    required this.userId,
    required this.type,
    required this.value,
    required this.unit,
    required this.time,
    required this.duration,
    this.location,
    this.notes,
  });

  @override
  int? get id => this.id;

  @override
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'user_id': userId,
      'type': type,
      'value': value,
      'unit': unit,
      'time': time,
      'duration': duration,
      'location': location,
      'notes': notes,
    };
  }

  factory LifeActivityData.fromMap(Map<String, dynamic> map) {
    return LifeActivityData(
      id: map['id'] as int?,
      userId: map['user_id'] as String,
      type: map['type'] as String,
      value: map['value'] as double,
      unit: map['unit'] as String,
      time: map['time'] as int,
      duration: map['duration'] as int,
      location: map['location'] as String?,
      notes: map['notes'] as String?,
    );
  }

  static String get tableName => 'life_activity_data';

  static String get createTableSql => '''
    CREATE TABLE IF NOT EXISTS life_activity_data(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      type TEXT,
      value REAL,
      unit TEXT,
      time INTEGER,
      duration INTEGER,
      location TEXT,
      notes TEXT
    )
  ''';

  static List<String> get createIndexSql => [
    'CREATE INDEX idx_life_activity_user_type ON life_activity_data(user_id, type)',
    'CREATE INDEX idx_life_activity_time ON life_activity_data(time)',
  ];

  LifeActivityData copyWith({
    int? id,
    String? userId,
    String? type,
    double? value,
    String? unit,
    int? time,
    int? duration,
    String? location,
    String? notes,
  }) {
    return LifeActivityData(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      type: type ?? this.type,
      value: value ?? this.value,
      unit: unit ?? this.unit,
      time: time ?? this.time,
      duration: duration ?? this.duration,
      location: location ?? this.location,
      notes: notes ?? this.notes,
    );
  }

  @override
  String toString() {
    return 'LifeActivityData(id: $id, userId: $userId, type: $type, value: $value, unit: $unit, time: $time, duration: $duration, location: $location)';
  }

  /// 获取生活活动类型列表
  static List<String> get activityTypes => [
    'walking',          // 步行
    'running',          // 跑步
    'cycling',          // 骑行
    'swimming',         // 游泳
    'yoga',            // 瑜伽
    'gym',             // 健身
    'meditation',      // 冥想
    'reading',         // 阅读
    'studying',        // 学习
    'working',         // 工作
    'entertainment',   // 娱乐
    'social',          // 社交
    'shopping',        // 购物
    'cooking',         // 烹饪
    'cleaning',        // 清洁
    'sleeping',        // 睡眠
  ];

  /// 获取生活活动单位映射
  static Map<String, String> get activityUnits => {
    'walking': 'steps',
    'running': 'km',
    'cycling': 'km',
    'swimming': 'm',
    'yoga': 'minutes',
    'gym': 'minutes',
    'meditation': 'minutes',
    'reading': 'minutes',
    'studying': 'minutes',
    'working': 'minutes',
    'entertainment': 'minutes',
    'social': 'minutes',
    'shopping': 'minutes',
    'cooking': 'minutes',
    'cleaning': 'minutes',
    'sleeping': 'hours',
  };

  /// 获取活动强度等级
  static Map<String, Map<String, int>> get activityIntensityLevels => {
    'walking': {'low': 2000, 'medium': 5000, 'high': 10000},
    'running': {'low': 2, 'medium': 5, 'high': 10},
    'cycling': {'low': 5, 'medium': 15, 'high': 30},
    'swimming': {'low': 500, 'medium': 1000, 'high': 2000},
    'gym': {'low': 30, 'medium': 60, 'high': 120},
  };

  /// 获取推荐的每日活动时长（分钟）
  static Map<String, int> get recommendedDailyDuration => {
    'walking': 30,
    'exercise': 60,
    'reading': 30,
    'studying': 120,
    'working': 480,
    'sleeping': 480,
  };
} 