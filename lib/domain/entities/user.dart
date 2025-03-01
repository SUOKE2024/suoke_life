import 'package:equatable/equatable.dart';

/// 用户实体类
/// 定义应用中用户的核心属性和行为
class User extends Equatable {
  final String id;
  final String username;
  final String? email;
  final String? phoneNumber;
  final String? avatarUrl;
  final DateTime? createdAt;
  final DateTime? lastLoginAt;
  final Map<String, dynamic>? preferences;
  final List<String>? roles;
  final bool isVerified;

  const User({
    required this.id,
    required this.username,
    this.email,
    this.phoneNumber,
    this.avatarUrl,
    this.createdAt,
    this.lastLoginAt,
    this.preferences,
    this.roles,
    this.isVerified = false,
  });

  /// 创建具有匿名身份的用户
  factory User.anonymous() => User(
        id: 'anonymous',
        username: '游客',
        isVerified: false,
      );

  /// 检查用户是否具有特定角色
  bool hasRole(String role) => roles?.contains(role) ?? false;

  /// 检查用户是否为管理员
  bool get isAdmin => hasRole('admin');

  /// 创建带有更新字段的新用户实例
  User copyWith({
    String? id,
    String? username,
    String? email,
    String? phoneNumber,
    String? avatarUrl,
    DateTime? createdAt,
    DateTime? lastLoginAt,
    Map<String, dynamic>? preferences,
    List<String>? roles,
    bool? isVerified,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      createdAt: createdAt ?? this.createdAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
      preferences: preferences ?? this.preferences,
      roles: roles ?? this.roles,
      isVerified: isVerified ?? this.isVerified,
    );
  }

  @override
  List<Object?> get props => [
        id,
        username,
        email,
        phoneNumber,
        avatarUrl,
        createdAt,
        lastLoginAt,
        preferences,
        roles,
        isVerified,
      ];
} 