/// 用户个人资料
class UserProfile {
  /// 用户ID
  final String id;

  /// 用户名
  final String username;

  /// 邮箱
  final String email;

  /// 显示名称
  final String displayName;

  /// 头像URL
  final String? avatar;

  /// 手机号码
  final String? phoneNumber;

  /// 生日
  final DateTime? birthday;

  /// 性别
  final String? gender;

  /// 身高(cm)
  final double? height;

  /// 体重(kg)
  final double? weight;

  /// 创建时间
  final DateTime createdAt;

  /// 最后更新时间
  final DateTime updatedAt;

  /// 构造函数
  UserProfile({
    required this.id,
    required this.username,
    required this.email,
    required this.displayName,
    this.avatar,
    this.phoneNumber,
    this.birthday,
    this.gender,
    this.height,
    this.weight,
    required this.createdAt,
    required this.updatedAt,
  });

  /// 从JSON创建用户个人资料
  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String,
      displayName: json['display_name'] as String,
      avatar: json['avatar'] as String?,
      phoneNumber: json['phone_number'] as String?,
      birthday: json['birthday'] != null
          ? DateTime.parse(json['birthday'] as String)
          : null,
      gender: json['gender'] as String?,
      height:
          json['height'] != null ? (json['height'] as num).toDouble() : null,
      weight:
          json['weight'] != null ? (json['weight'] as num).toDouble() : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'display_name': displayName,
      'avatar': avatar,
      'phone_number': phoneNumber,
      'birthday': birthday?.toIso8601String(),
      'gender': gender,
      'height': height,
      'weight': weight,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// 创建用户个人资料副本
  UserProfile copyWith({
    String? id,
    String? username,
    String? email,
    String? displayName,
    String? avatar,
    String? phoneNumber,
    DateTime? birthday,
    String? gender,
    double? height,
    double? weight,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserProfile(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      displayName: displayName ?? this.displayName,
      avatar: avatar ?? this.avatar,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      birthday: birthday ?? this.birthday,
      gender: gender ?? this.gender,
      height: height ?? this.height,
      weight: weight ?? this.weight,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
