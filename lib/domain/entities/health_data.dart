import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';

/// 健康数据类型枚举
enum HealthDataType {
  steps,
  sleep,
  heartRate,
  bloodPressure,
  bloodOxygen,
  temperature,
  weight,
  waterIntake,
  foodIntake,
  medication,
  mood,
  symptom,
  activity,
  meditation,
}

/// 健康数据来源枚举
enum HealthDataSource {
  manual,
  device,
  thirdPartyApp,
  calculation,
  aiInference,
}

/// 健康数据单位枚举
enum HealthUnit {
  count,
  minute,
  hour,
  step,
  kilometer,
  meter,
  kilogram,
  gram,
  liter,
  milliliter,
  kilocalorie,
  bpm,
  mmHg,
  celsius,
  fahrenheit,
  percent,
  point,
}

/// 健康数据实体
class HealthData extends Equatable {
  /// 数据ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 数据类型
  final String type;
  
  /// 数据值
  final double value;
  
  /// 单位
  final String unit;
  
  /// 时间戳
  final DateTime timestamp;
  
  /// 数据源
  final String? source;
  
  /// 元数据
  final Map<String, dynamic>? metadata;
  
  /// 标签
  final List<String>? tags;
  
  /// 备注
  final String? notes;
  
  /// 是否已同步
  final bool synced;
  
  /// 是否已删除
  final bool isDeleted;
  
  /// 构造函数
  const HealthData({
    required this.id,
    required this.userId,
    required this.type,
    required this.value,
    required this.unit,
    required this.timestamp,
    this.source,
    this.metadata,
    this.tags,
    this.notes,
    this.synced = false,
    this.isDeleted = false,
  });
  
  /// 创建副本并更新字段
  HealthData copyWith({
    String? id,
    String? userId,
    String? type,
    double? value,
    String? unit,
    DateTime? timestamp,
    String? source,
    Map<String, dynamic>? metadata,
    List<String>? tags,
    String? notes,
    bool? synced,
    bool? isDeleted,
  }) {
    return HealthData(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      type: type ?? this.type,
      value: value ?? this.value,
      unit: unit ?? this.unit,
      timestamp: timestamp ?? this.timestamp,
      source: source ?? this.source,
      metadata: metadata ?? this.metadata,
      tags: tags ?? this.tags,
      notes: notes ?? this.notes,
      synced: synced ?? this.synced,
      isDeleted: isDeleted ?? this.isDeleted,
    );
  }
  
  @override
  List<Object?> get props => [
    id, 
    userId, 
    type, 
    value, 
    unit, 
    timestamp, 
    source, 
    metadata, 
    tags, 
    notes, 
    synced, 
    isDeleted,
  ];
} 