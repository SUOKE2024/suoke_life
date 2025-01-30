import 'package:json_annotation/json_annotation.dart';

part 'ai_service_response.g.dart';

@JsonSerializable()
class AIServiceResponse {
  final String id;
  final String content;
  final Map<String, dynamic>? metadata;
  final DateTime timestamp;
  
  const AIServiceResponse({
    required this.id,
    required this.content,
    this.metadata,
    required this.timestamp,
  });
  
  factory AIServiceResponse.fromJson(Map<String, dynamic> json) => 
      _$AIServiceResponseFromJson(json);
      
  Map<String, dynamic> toJson() => _$AIServiceResponseToJson(this);
} 