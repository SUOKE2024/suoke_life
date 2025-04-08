import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:flutter/foundation.dart';

part 'session_model.freezed.dart';
part 'session_model.g.dart';

/// 会话模型
@freezed
class SessionModel with _$SessionModel {
  const factory SessionModel({
    required String id,
    required String userId,
    required String title,
    required String agentId,
    required DateTime createdAt,
    required DateTime updatedAt,
    required List<MessageModel> messages,
    Map<String, dynamic>? metadata,
  }) = _SessionModel;

  factory SessionModel.fromJson(Map<String, dynamic> json) => _$SessionModelFromJson(json);
}

/// 消息模型
@freezed
class MessageModel with _$MessageModel {
  const factory MessageModel({
    required String id,
    required String content,
    required String role, // user, assistant, system
    required DateTime timestamp,
    Map<String, dynamic>? metadata,
  }) = _MessageModel;

  factory MessageModel.fromJson(Map<String, dynamic> json) => _$MessageModelFromJson(json);
} 