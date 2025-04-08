import 'package:equatable/equatable.dart';

/// 健康数据实体类
class HealthData extends Equatable {
  /// 用户ID
  final String userId;
  
  /// 记录ID
  final String recordId;
  
  /// 记录日期
  final DateTime recordDate;
  
  /// 生命体征数据
  /// 包含如血压、心率、体温等指标
  final Map<String, dynamic> vitalSigns;
  
  /// 活动数据
  /// 包含步数、运动量、活动时长等
  final Map<String, dynamic> activityData;
  
  /// 睡眠数据
  /// 包含睡眠时长、睡眠质量、睡眠阶段等
  final Map<String, dynamic> sleepData;
  
  /// 营养数据
  /// 包含摄入卡路里、营养素、饮食记录等
  final Map<String, dynamic> nutritionData;
  
  /// 中医指标数据
  /// 包含舌象、脉象、体质评估等TCM特色指标
  final Map<String, dynamic> tcmIndicators;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;

  /// 构造函数
  const HealthData({
    required this.userId,
    required this.recordId,
    required this.recordDate,
    required this.vitalSigns,
    required this.activityData,
    required this.sleepData,
    required this.nutritionData,
    required this.tcmIndicators,
    required this.createdAt,
    required this.updatedAt,
  });

  @override
  List<Object?> get props => [
        userId,
        recordId,
        recordDate,
        vitalSigns,
        activityData,
        sleepData,
        nutritionData,
        tcmIndicators,
        createdAt,
        updatedAt,
      ];

  @override
  String toString() {
    return 'HealthData(userId: $userId, recordId: $recordId, recordDate: $recordDate, vitalSigns: $vitalSigns, activityData: $activityData, sleepData: $sleepData, nutritionData: $nutritionData, tcmIndicators: $tcmIndicators)';
  }

  /// 创建副本
  HealthData copyWith({
    String? userId,
    String? recordId,
    DateTime? recordDate,
    Map<String, dynamic>? vitalSigns,
    Map<String, dynamic>? activityData,
    Map<String, dynamic>? sleepData,
    Map<String, dynamic>? nutritionData,
    Map<String, dynamic>? tcmIndicators,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return HealthData(
      userId: userId ?? this.userId,
      recordId: recordId ?? this.recordId,
      recordDate: recordDate ?? this.recordDate,
      vitalSigns: vitalSigns ?? this.vitalSigns,
      activityData: activityData ?? this.activityData,
      sleepData: sleepData ?? this.sleepData,
      nutritionData: nutritionData ?? this.nutritionData,
      tcmIndicators: tcmIndicators ?? this.tcmIndicators,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// 健康活动实体类
class HealthActivity {
  /// 活动类型
  final String type;
  
  /// 开始时间
  final DateTime startTime;
  
  /// 结束时间
  final DateTime endTime;
  
  /// 活动数据
  final Map<String, dynamic> data;
  
  /// 构造函数
  const HealthActivity({
    required this.type,
    required this.startTime,
    required this.endTime,
    required this.data,
  });
  
  /// 创建副本并更新字段
  HealthActivity copyWith({
    String? type,
    DateTime? startTime,
    DateTime? endTime,
    Map<String, dynamic>? data,
  }) {
    return HealthActivity(
      type: type ?? this.type,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      data: data ?? this.data,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is HealthActivity &&
          runtimeType == other.runtimeType &&
          type == other.type &&
          startTime == other.startTime &&
          endTime == other.endTime;

  @override
  int get hashCode => type.hashCode ^ startTime.hashCode ^ endTime.hashCode;

  @override
  String toString() {
    return 'HealthActivity{type: $type, startTime: $startTime, endTime: $endTime}';
  }
} 