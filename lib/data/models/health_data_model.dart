import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';
import '../../domain/entities/health_data.dart';

part 'health_data_model.g.dart';

/// 健康数据模型
/// 用于处理API响应和本地存储的健康数据
@JsonSerializable()
class HealthDataModel extends Equatable {
  final String id;
  final String userId;
  @JsonKey(unknownEnumValue: HealthDataType.steps)
  final HealthDataType type;
  final num value;
  @JsonKey(unknownEnumValue: HealthUnit.count)
  final HealthUnit unit;
  final DateTime timestamp;
  @JsonKey(unknownEnumValue: HealthDataSource.manual)
  final HealthDataSource source;
  final Map<String, dynamic>? metadata;
  final String? notes;

  const HealthDataModel({
    required this.id,
    required this.userId,
    required this.type,
    required this.value,
    required this.unit,
    required this.timestamp,
    required this.source,
    this.metadata,
    this.notes,
  });

  /// 从JSON数据创建健康数据模型
  factory HealthDataModel.fromJson(Map<String, dynamic> json) =>
      _$HealthDataModelFromJson(json);

  /// 将健康数据模型转换为JSON数据
  Map<String, dynamic> toJson() => _$HealthDataModelToJson(this);

  /// 将数据模型转换为领域实体
  HealthData toEntity() => HealthData(
        id: id,
        userId: userId,
        type: type,
        value: value,
        unit: unit,
        timestamp: timestamp,
        source: source,
        metadata: metadata,
        notes: notes,
      );

  /// 从领域实体创建数据模型
  factory HealthDataModel.fromEntity(HealthData healthData) => HealthDataModel(
        id: healthData.id,
        userId: healthData.userId,
        type: healthData.type,
        value: healthData.value,
        unit: healthData.unit,
        timestamp: healthData.timestamp,
        source: healthData.source,
        metadata: healthData.metadata,
        notes: healthData.notes,
      );

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
        notes,
      ];
} 