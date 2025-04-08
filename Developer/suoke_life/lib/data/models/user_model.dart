import 'dart:convert';
import '../../domain/entities/user.dart';

/// 用户数据模型
class UserModel extends User {
  const UserModel({
    required String id,
    required String username,
    required String email,
    String? phoneNumber,
    String? displayName,
    String? avatarUrl,
    String? bio,
    String? role,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : super(
          id: id,
          username: username,
          email: email,
          phoneNumber: phoneNumber,
          displayName: displayName,
          avatarUrl: avatarUrl,
          bio: bio,
          role: role,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// 从JSON映射创建用户模型
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      phoneNumber: json['phone_number'],
      displayName: json['display_name'],
      avatarUrl: json['avatar_url'],
      bio: json['bio'],
      role: json['role'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// 从JSON字符串创建用户模型
  factory UserModel.fromJsonString(String jsonString) {
    return UserModel.fromJson(json.decode(jsonString));
  }

  /// 转换为JSON映射
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'phone_number': phoneNumber,
      'display_name': displayName,
      'avatar_url': avatarUrl,
      'bio': bio,
      'role': role,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  /// 转换为JSON字符串
  String toJsonString() {
    return json.encode(toJson());
  }

  /// 创建具有更新字段的新实例
  @override
  UserModel copyWith({
    String? id,
    String? username,
    String? email,
    String? phoneNumber,
    String? displayName,
    String? avatarUrl,
    String? bio,
    String? role,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserModel(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      displayName: displayName ?? this.displayName,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      bio: bio ?? this.bio,
      role: role ?? this.role,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  /// 从实体对象创建模型
  factory UserModel.fromEntity(User entity) {
    return UserModel(
      id: entity.id,
      username: entity.username,
      email: entity.email,
      phoneNumber: entity.phoneNumber,
      displayName: entity.displayName,
      avatarUrl: entity.avatarUrl,
      bio: entity.bio,
      role: entity.role,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }
  
  /// 转换为实体对象
  User toEntity() {
    return User(
      id: id,
      username: username,
      email: email,
      phoneNumber: phoneNumber,
      displayName: displayName,
      avatarUrl: avatarUrl,
      bio: bio,
      role: role,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }
} 