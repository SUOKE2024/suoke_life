class PhoneAuthRequest {
  final String phone;
  final String? verificationCode;
  final String? inviteCode;

  PhoneAuthRequest({
    required this.phone,
    this.verificationCode,
    this.inviteCode,
  });

  Map<String, dynamic> toJson() => {
    'phone': phone,
    if (verificationCode != null) 'code': verificationCode,
    if (inviteCode != null) 'inviteCode': inviteCode,
  };
}

class AuthResponse {
  final String token;
  final String refreshToken;
  final DateTime expiresAt;
  final UserProfile profile;

  AuthResponse({
    required this.token,
    required this.refreshToken,
    required this.expiresAt,
    required this.profile,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      token: json['token'] as String,
      refreshToken: json['refreshToken'] as String,
      expiresAt: DateTime.parse(json['expiresAt'] as String),
      profile: UserProfile.fromJson(json['profile'] as Map<String, dynamic>),
    );
  }
}

class UserProfile {
  final String id;
  final String phone;
  final String? nickname;
  final String? avatar;
  final String? email;
  final DateTime createdAt;
  final bool isVerified;
  final List<String> roles;

  UserProfile({
    required this.id,
    required this.phone,
    this.nickname,
    this.avatar,
    this.email,
    required this.createdAt,
    this.isVerified = false,
    this.roles = const [],
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String,
      phone: json['phone'] as String,
      nickname: json['nickname'] as String?,
      avatar: json['avatar'] as String?,
      email: json['email'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      isVerified: json['isVerified'] as bool? ?? false,
      roles: (json['roles'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'phone': phone,
    if (nickname != null) 'nickname': nickname,
    if (avatar != null) 'avatar': avatar,
    if (email != null) 'email': email,
    'createdAt': createdAt.toIso8601String(),
    'isVerified': isVerified,
    'roles': roles,
  };

  UserProfile copyWith({
    String? nickname,
    String? avatar,
    String? email,
    bool? isVerified,
    List<String>? roles,
  }) {
    return UserProfile(
      id: id,
      phone: phone,
      nickname: nickname ?? this.nickname,
      avatar: avatar ?? this.avatar,
      email: email ?? this.email,
      createdAt: createdAt,
      isVerified: isVerified ?? this.isVerified,
      roles: roles ?? this.roles,
    );
  }
}

class User {
  final String id;
  final String phone;
  final String nickname;
  final String? avatar;
  final DateTime createdAt;
  final DateTime? lastLoginAt;
  
  User({
    required this.id,
    required this.phone,
    required this.nickname,
    this.avatar,
    required this.createdAt,
    this.lastLoginAt,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      phone: json['phone'] as String,
      nickname: json['nickname'] as String,
      avatar: json['avatar'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      lastLoginAt: json['last_login_at'] == null
          ? null
          : DateTime.parse(json['last_login_at'] as String),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone': phone,
      'nickname': nickname,
      'avatar': avatar,
      'created_at': createdAt.toIso8601String(),
      'last_login_at': lastLoginAt?.toIso8601String(),
    };
  }
  
  User copyWith({
    String? nickname,
    String? avatar,
  }) {
    return User(
      id: id,
      phone: phone,
      nickname: nickname ?? this.nickname,
      avatar: avatar ?? this.avatar,
      createdAt: createdAt,
      lastLoginAt: lastLoginAt,
    );
  }
} 