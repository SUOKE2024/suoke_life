// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sync_request_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SyncRequestModel _$SyncRequestModelFromJson(Map<String, dynamic> json) =>
    SyncRequestModel(
      table: json['table'] as String,
      timestamp: json['timestamp'] as String,
      data: (json['data'] as List<dynamic>)
          .map((e) => e as Map<String, dynamic>)
          .toList(),
    );

Map<String, dynamic> _$SyncRequestModelToJson(SyncRequestModel instance) =>
    <String, dynamic>{
      'table': instance.table,
      'timestamp': instance.timestamp,
      'data': instance.data,
    };
