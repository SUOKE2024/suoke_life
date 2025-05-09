import 'package:equatable/equatable.dart';

/// 用户信息模型
class User extends Equatable {
  final String id;
  final String username;
  final String? nickname;
  final String? avatarUrl;
  final String? phone;
  final String? email;
  final DateTime? birthday;
  final int? gender; // 0: 未知, 1: 男, 2: 女
  final DateTime createdAt;
  final DateTime updatedAt;

  const User({
    required this.id,
    required this.username,
    this.nickname,
    this.avatarUrl,
    this.phone,
    this.email,
    this.birthday,
    this.gender,
    required this.createdAt,
    required this.updatedAt,
  });

  /// 从JSON转换为用户对象
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      nickname: json['nickname'],
      avatarUrl: json['avatar_url'],
      phone: json['phone'],
      email: json['email'],
      birthday:
          json['birthday'] != null ? DateTime.parse(json['birthday']) : null,
      gender: json['gender'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'nickname': nickname,
      'avatar_url': avatarUrl,
      'phone': phone,
      'email': email,
      'birthday': birthday?.toIso8601String(),
      'gender': gender,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// 创建更新后的用户对象
  User copyWith({
    String? id,
    String? username,
    String? nickname,
    String? avatarUrl,
    String? phone,
    String? email,
    DateTime? birthday,
    int? gender,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      nickname: nickname ?? this.nickname,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      phone: phone ?? this.phone,
      email: email ?? this.email,
      birthday: birthday ?? this.birthday,
      gender: gender ?? this.gender,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  /// 用于相等性比较
  @override
  List<Object?> get props => [
        id,
        username,
        nickname,
        avatarUrl,
        phone,
        email,
        birthday,
        gender,
        createdAt,
        updatedAt,
      ];
}
