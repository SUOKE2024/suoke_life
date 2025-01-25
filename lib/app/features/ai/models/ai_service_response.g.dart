// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ai_service_response.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AIServiceResponse _$AIServiceResponseFromJson(Map<String, dynamic> json) =>
    AIServiceResponse(
      id: json['id'] as String,
      content: json['content'] as String,
      metadata: json['metadata'] as Map<String, dynamic>?,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );

Map<String, dynamic> _$AIServiceResponseToJson(AIServiceResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'content': instance.content,
      'metadata': instance.metadata,
      'timestamp': instance.timestamp.toIso8601String(),
    };
