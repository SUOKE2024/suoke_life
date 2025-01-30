import '../base/entity.dart';
import 'dart:convert';

/// 健康数据实体
class HealthData extends Entity {
  final int? id;
  final String userId;
  final String type;
  final double value;
  final String unit;
  final int time;
  final String source;
  final String? notes;

  HealthData({
    this.id,
    required this.userId,
    required this.type,
    required this.value,
    required this.unit,
    required this.time,
    required this.source,
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
      'source': source,
      'notes': notes,
    };
  }

  factory HealthData.fromMap(Map<String, dynamic> map) {
    return HealthData(
      id: map['id'] as int?,
      userId: map['user_id'] as String,
      type: map['type'] as String,
      value: map['value'] as double,
      unit: map['unit'] as String,
      time: map['time'] as int,
      source: map['source'] as String,
      notes: map['notes'] as String?,
    );
  }

  static String get tableName => 'health_data';

  static String get createTableSql => '''
    CREATE TABLE IF NOT EXISTS health_data(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      type TEXT,
      value REAL,
      unit TEXT,
      time INTEGER,
      source TEXT,
      notes TEXT
    )
  ''';

  static List<String> get createIndexSql => [
    'CREATE INDEX idx_health_data_user_type ON health_data(user_id, type)',
    'CREATE INDEX idx_health_data_time ON health_data(time)',
  ];

  HealthData copyWith({
    int? id,
    String? userId,
    String? type,
    double? value,
    String? unit,
    int? time,
    String? source,
    String? notes,
  }) {
    return HealthData(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      type: type ?? this.type,
      value: value ?? this.value,
      unit: unit ?? this.unit,
      time: time ?? this.time,
      source: source ?? this.source,
      notes: notes ?? this.notes,
    );
  }

  @override
  String toString() {
    return 'HealthData(id: $id, userId: $userId, type: $type, value: $value, unit: $unit, time: $time, source: $source)';
  }

  /// 获取健康数据类型列表
  static List<String> get healthDataTypes => [
    'heart_rate',        // 心率
    'blood_pressure',    // 血压
    'blood_sugar',       // 血糖
    'body_temperature',  // 体温
    'weight',           // 体重
    'height',           // 身高
    'steps',            // 步数
    'sleep',            // 睡眠
    'oxygen',           // 血氧
    'calories',         // 卡路里
    'water',            // 饮水量
    'exercise',         // 运动时长
  ];

  /// 获取健康数据单位映射
  static Map<String, String> get healthDataUnits => {
    'heart_rate': 'bpm',
    'blood_pressure': 'mmHg',
    'blood_sugar': 'mmol/L',
    'body_temperature': '°C',
    'weight': 'kg',
    'height': 'cm',
    'steps': 'steps',
    'sleep': 'hours',
    'oxygen': '%',
    'calories': 'kcal',
    'water': 'ml',
    'exercise': 'minutes',
  };

  /// 获取健康数据正常范围
  static Map<String, Map<String, double>> get healthDataRanges => {
    'heart_rate': {'min': 60, 'max': 100},
    'blood_pressure': {'min': 90, 'max': 140},
    'blood_sugar': {'min': 3.9, 'max': 7.8},
    'body_temperature': {'min': 36.1, 'max': 37.2},
    'oxygen': {'min': 95, 'max': 100},
  };
} 