import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';
import '../../domain/entities/user.dart';

part 'user_model.g.dart';

/// 用户数据模型
/// 用于处理API响应和本地存储的用户数据
@JsonSerializable()
class UserModel extends Equatable {
  /// 用户ID
  final String id;
  
  /// 用户名
  final String username;
  
  /// 邮箱地址
  final String? email;
  
  /// 手机号码
  final String? phone;
  
  /// 头像URL
  final String? avatarUrl;
  
  /// 创建时间
  final int createdAt;
  
  /// 更新时间
  final int updatedAt;
  
  /// 最后登录时间
  final int? lastLogin;
  
  /// 账户类型
  final String accountType;
  
  /// 同步状态
  @JsonKey(name: 'sync_status')
  final String? syncStatus;
  
  /// 构造函数
  const UserModel({
    required this.id,
    required this.username,
    this.email,
    this.phone,
    this.avatarUrl,
    required this.createdAt,
    required this.updatedAt,
    this.lastLogin,
    required this.accountType,
    this.syncStatus = 'pending',
  });
  
  /// 从JSON创建实例
  factory UserModel.fromJson(Map<String, dynamic> json) => 
      _$UserModelFromJson(json);
  
  /// 转换为JSON
  Map<String, dynamic> toJson() => _$UserModelToJson(this);
  
  /// 创建副本并更新字段
  UserModel copyWith({
    String? id,
    String? username,
    String? email,
    String? phone,
    String? avatarUrl,
    int? createdAt,
    int? updatedAt,
    int? lastLogin,
    String? accountType,
    String? syncStatus,
  }) {
    return UserModel(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastLogin: lastLogin ?? this.lastLogin,
      accountType: accountType ?? this.accountType,
      syncStatus: syncStatus ?? this.syncStatus,
    );
  }
  
  /// 将数据模型转换为领域实体
  User toEntity() => User(
        id: id,
        username: username,
        email: email,
        phoneNumber: phone,
        avatarUrl: avatarUrl,
        createdAt: DateTime.fromMillisecondsSinceEpoch(createdAt),
        lastLoginAt: lastLogin != null ? DateTime.fromMillisecondsSinceEpoch(lastLogin!) : null,
        accountType: accountType,
        syncStatus: syncStatus,
      );

  /// 从领域实体创建数据模型
  factory UserModel.fromEntity(User user) => UserModel(
        id: user.id,
        username: user.username,
        email: user.email,
        phone: user.phoneNumber,
        avatarUrl: user.avatarUrl,
        createdAt: user.createdAt.millisecondsSinceEpoch,
        updatedAt: user.updatedAt?.millisecondsSinceEpoch ?? 0,
        lastLogin: user.lastLoginAt?.millisecondsSinceEpoch,
        accountType: user.accountType,
        syncStatus: user.syncStatus,
      );

  @override
  List<Object?> get props => [
    id, 
    username, 
    email, 
    phone, 
    avatarUrl, 
    createdAt, 
    updatedAt, 
    lastLogin, 
    accountType,
    syncStatus,
  ];
} 