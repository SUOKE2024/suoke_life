/// 用户实体类
class User {
  /// 用户ID
  final String id;

  /// 用户名
  final String username;

  /// 电子邮件
  final String email;

  /// 电话号码
  final String? phoneNumber;

  /// 显示名称
  final String? displayName;

  /// 头像URL
  final String? avatarUrl;

  /// 个人简介
  final String? bio;

  /// 用户角色
  final String? role;

  /// 创建时间
  final DateTime? createdAt;

  /// 更新时间
  final DateTime? updatedAt;

  const User({
    this.id = '',
    this.username = '',
    this.email = '',
    this.phoneNumber,
    this.displayName,
    this.avatarUrl,
    this.bio,
    this.role,
    this.createdAt,
    this.updatedAt,
  });

  /// 创建副本并更新字段
  User copyWith({
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
    return User(
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

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is User &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          username == other.username &&
          email == other.email;

  @override
  int get hashCode => id.hashCode ^ username.hashCode ^ email.hashCode;

  @override
  String toString() {
    return 'User{id: $id, username: $username, email: $email, displayName: $displayName}';
  }
}
