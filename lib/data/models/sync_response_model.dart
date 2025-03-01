import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'sync_response_model.g.dart';

/// 同步响应模型
@JsonSerializable()
class SyncResponseModel extends Equatable {
  /// 成功同步的数据
  final List<Map<String, dynamic>> successful;
  
  /// 同步失败的数据
  final List<Map<String, dynamic>> failed;
  
  /// 存在冲突的数据
  final List<Map<String, dynamic>> conflicts;
  
  /// 时间戳
  final String timestamp;
  
  /// 构造函数
  const SyncResponseModel({
    required this.successful,
    required this.failed,
    required this.conflicts,
    required this.timestamp,
  });
  
  /// 从JSON创建实例
  factory SyncResponseModel.fromJson(Map<String, dynamic> json) => 
      _$SyncResponseModelFromJson(json);
  
  /// 转换为JSON
  Map<String, dynamic> toJson() => _$SyncResponseModelToJson(this);
  
  @override
  List<Object?> get props => [successful, failed, conflicts, timestamp];
} 