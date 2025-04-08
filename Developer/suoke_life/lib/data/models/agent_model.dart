import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:flutter/foundation.dart';

part 'agent_model.freezed.dart';
part 'agent_model.g.dart';

/// 智能体模型
@freezed
class AgentModel with _$AgentModel {
  const factory AgentModel({
    required String id,
    required String name,
    required String description,
    required String avatarUrl,
    required String type,
    required Map<String, dynamic> capabilities,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _AgentModel;

  factory AgentModel.fromJson(Map<String, dynamic> json) => _$AgentModelFromJson(json);
} 