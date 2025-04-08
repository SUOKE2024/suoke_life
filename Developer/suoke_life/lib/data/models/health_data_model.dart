import 'dart:convert';
import 'package:suoke_life/domain/entities/health_data.dart';

/// 健康数据模型
class HealthDataModel extends HealthData {
  /// 构造函数
  const HealthDataModel({
    required String userId,
    required String recordId,
    required DateTime recordDate,
    required Map<String, dynamic> vitalSigns,
    required Map<String, dynamic> activityData,
    required Map<String, dynamic> sleepData,
    required Map<String, dynamic> nutritionData,
    required Map<String, dynamic> tcmIndicators,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super(
          userId: userId,
          recordId: recordId,
          recordDate: recordDate,
          vitalSigns: vitalSigns,
          activityData: activityData,
          sleepData: sleepData,
          nutritionData: nutritionData,
          tcmIndicators: tcmIndicators,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// 从JSON创建模型
  factory HealthDataModel.fromJson(Map<String, dynamic> json) {
    return HealthDataModel(
      userId: json['user_id'],
      recordId: json['record_id'],
      recordDate: DateTime.parse(json['record_date']),
      vitalSigns: json['vital_signs'],
      activityData: json['activity_data'],
      sleepData: json['sleep_data'],
      nutritionData: json['nutrition_data'],
      tcmIndicators: json['tcm_indicators'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  /// 从JSON字符串创建模型
  factory HealthDataModel.fromJsonString(String jsonString) {
    return HealthDataModel.fromJson(json.decode(jsonString));
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'record_id': recordId,
      'record_date': recordDate.toIso8601String(),
      'vital_signs': vitalSigns,
      'activity_data': activityData,
      'sleep_data': sleepData,
      'nutrition_data': nutritionData,
      'tcm_indicators': tcmIndicators,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// 转换为JSON字符串
  String toJsonString() {
    return json.encode(toJson());
  }

  /// 创建副本
  HealthDataModel copyWith({
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
    return HealthDataModel(
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

  /// 从实体创建模型
  factory HealthDataModel.fromEntity(HealthData entity) {
    return HealthDataModel(
      userId: entity.userId,
      recordId: entity.recordId,
      recordDate: entity.recordDate,
      vitalSigns: entity.vitalSigns,
      activityData: entity.activityData,
      sleepData: entity.sleepData,
      nutritionData: entity.nutritionData,
      tcmIndicators: entity.tcmIndicators,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }
  
  /// 转换为实体
  HealthData toEntity() {
    return HealthData(
      userId: userId,
      recordId: recordId,
      recordDate: recordDate,
      vitalSigns: vitalSigns,
      activityData: activityData,
      sleepData: sleepData,
      nutritionData: nutritionData,
      tcmIndicators: tcmIndicators,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }
}

/// 健康活动模型
class HealthActivityModel extends HealthActivity {
  /// 构造函数
  const HealthActivityModel({
    required String type,
    required DateTime startTime,
    required DateTime endTime,
    required Map<String, dynamic> data,
  }) : super(
          type: type,
          startTime: startTime,
          endTime: endTime,
          data: data,
        );

  /// 从JSON映射创建模型
  factory HealthActivityModel.fromJson(Map<String, dynamic> json) {
    return HealthActivityModel(
      type: json['type'],
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      data: json['data'] ?? {},
    );
  }

  /// 转换为JSON映射
  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime.toIso8601String(),
      'data': data,
    };
  }

  /// 创建具有更新字段的新实例
  HealthActivityModel copyWith({
    String? type,
    DateTime? startTime,
    DateTime? endTime,
    Map<String, dynamic>? data,
  }) {
    return HealthActivityModel(
      type: type ?? this.type,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      data: data ?? this.data,
    );
  }

  /// 从实体创建模型
  factory HealthActivityModel.fromEntity(HealthActivity entity) {
    return HealthActivityModel(
      type: entity.type,
      startTime: entity.startTime,
      endTime: entity.endTime,
      data: entity.data,
    );
  }
} 