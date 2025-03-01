import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'sync_request_model.g.dart';

/// 同步请求模型
@JsonSerializable()
class SyncRequestModel extends Equatable {
  /// 表名
  final String table;
  
  /// 时间戳
  final String timestamp;
  
  /// 需要同步的数据
  final List<Map<String, dynamic>> data;
  
  /// 构造函数
  const SyncRequestModel({
    required this.table,
    required this.timestamp,
    required this.data,
  });
  
  /// 从JSON创建实例
  factory SyncRequestModel.fromJson(Map<String, dynamic> json) => 
      _$SyncRequestModelFromJson(json);
  
  /// 转换为JSON
  Map<String, dynamic> toJson() => _$SyncRequestModelToJson(this);
  
  @override
  List<Object?> get props => [table, timestamp, data];
}