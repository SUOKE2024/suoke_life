// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sync_response_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SyncResponseModel _$SyncResponseModelFromJson(Map<String, dynamic> json) =>
    SyncResponseModel(
      successful: (json['successful'] as List<dynamic>)
          .map((e) => e as Map<String, dynamic>)
          .toList(),
      failed: (json['failed'] as List<dynamic>)
          .map((e) => e as Map<String, dynamic>)
          .toList(),
      conflicts: (json['conflicts'] as List<dynamic>)
          .map((e) => e as Map<String, dynamic>)
          .toList(),
      timestamp: json['timestamp'] as String,
    );

Map<String, dynamic> _$SyncResponseModelToJson(SyncResponseModel instance) =>
    <String, dynamic>{
      'successful': instance.successful,
      'failed': instance.failed,
      'conflicts': instance.conflicts,
      'timestamp': instance.timestamp,
    };
