import 'dart:convert';
import 'package:suoke_life/domain/entities/auth_token.dart';

/// 认证令牌模型类
class AuthTokenModel extends AuthToken {
  /// 构造函数
  const AuthTokenModel({
    required String accessToken,
    required String refreshToken,
    required int expiresIn,
    DateTime? expiresAt,
  }) : super(
          accessToken: accessToken,
          refreshToken: refreshToken,
          expiresIn: expiresIn,
          expiresAt: expiresAt,
        );

  /// 从JSON创建模型
  factory AuthTokenModel.fromJson(Map<String, dynamic> json) {
    return AuthTokenModel(
      accessToken: json['access_token'],
      refreshToken: json['refresh_token'],
      expiresIn: json['expires_in'],
      expiresAt: json['expires_at'] != null ? DateTime.parse(json['expires_at']) : null,
    );
  }

  /// 从JSON字符串创建模型
  factory AuthTokenModel.fromJsonString(String jsonString) {
    return AuthTokenModel.fromJson(json.decode(jsonString));
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'expires_in': expiresIn,
      'expires_at': expiresAt?.toIso8601String(),
    };
  }

  /// 转换为JSON字符串
  String toJsonString() {
    return json.encode(toJson());
  }

  /// 从实体创建模型
  factory AuthTokenModel.fromEntity(AuthToken entity) {
    return AuthTokenModel(
      accessToken: entity.accessToken,
      refreshToken: entity.refreshToken,
      expiresIn: entity.expiresIn,
      expiresAt: entity.expiresAt,
    );
  }
  
  /// 创建副本
  @override
  AuthTokenModel copyWith({
    String? accessToken,
    String? refreshToken,
    int? expiresIn,
    DateTime? expiresAt,
  }) {
    return AuthTokenModel(
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      expiresIn: expiresIn ?? this.expiresIn,
      expiresAt: expiresAt ?? this.expiresAt,
    );
  }
} 