import 'dart:convert';
import 'package:suoke_life/domain/entities/user_preferences.dart';

/// 用户偏好设置模型类
class UserPreferencesModel extends UserPreferences {
  /// 构造函数
  const UserPreferencesModel({
    required String userId,
    required String themeMode,
    required String language,
    required bool notificationsEnabled,
    required bool dataCollectionConsent,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super(
          userId: userId,
          themeMode: themeMode,
          language: language,
          notificationsEnabled: notificationsEnabled,
          dataCollectionConsent: dataCollectionConsent,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// 从JSON映射创建UserPreferencesModel
  factory UserPreferencesModel.fromJson(Map<String, dynamic> json) {
    return UserPreferencesModel(
      userId: json['user_id'],
      themeMode: json['theme_mode'] ?? 'system',
      language: json['language'] ?? 'zh',
      notificationsEnabled: json['notifications_enabled'] ?? true,
      dataCollectionConsent: json['data_collection_consent'] ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
    );
  }

  /// 从JSON字符串创建模型
  factory UserPreferencesModel.fromJsonString(String jsonString) {
    return UserPreferencesModel.fromJson(json.decode(jsonString));
  }

  /// 转换为JSON映射
  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'theme_mode': themeMode,
      'language': language,
      'notifications_enabled': notificationsEnabled,
      'data_collection_consent': dataCollectionConsent,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// 转换为JSON字符串
  String toJsonString() {
    return json.encode(toJson());
  }

  /// 创建具有更新属性的UserPreferencesModel副本
  UserPreferencesModel copyWith({
    String? userId,
    String? themeMode,
    String? language,
    bool? notificationsEnabled,
    bool? dataCollectionConsent,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserPreferencesModel(
      userId: userId ?? this.userId,
      themeMode: themeMode ?? this.themeMode,
      language: language ?? this.language,
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      dataCollectionConsent: dataCollectionConsent ?? this.dataCollectionConsent,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  /// 从实体创建模型
  factory UserPreferencesModel.fromEntity(UserPreferences entity) {
    return UserPreferencesModel(
      userId: entity.userId,
      themeMode: entity.themeMode,
      language: entity.language,
      notificationsEnabled: entity.notificationsEnabled,
      dataCollectionConsent: entity.dataCollectionConsent,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }
  
  /// 转换为实体
  UserPreferences toEntity() {
    return UserPreferences(
      userId: userId,
      themeMode: themeMode,
      language: language,
      notificationsEnabled: notificationsEnabled,
      dataCollectionConsent: dataCollectionConsent,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }
} 