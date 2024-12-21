class UserInfo {
  final String id;
  final String name;
  final String? avatar;
  final String role;
  final String? email;
  final String? phone;
  final bool isVerified;
  final Map<String, dynamic>? extra;

  UserInfo({
    required this.id,
    required this.name,
    this.avatar,
    required this.role,
    this.email,
    this.phone,
    this.isVerified = false,
    this.extra,
  });

  factory UserInfo.fromJson(Map<String, dynamic> json) => UserInfo(
    id: json['id'],
    name: json['name'],
    avatar: json['avatar'],
    role: json['role'],
    email: json['email'],
    phone: json['phone'],
    isVerified: json['is_verified'] ?? false,
    extra: json['extra'],
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'avatar': avatar,
    'role': role,
    'email': email,
    'phone': phone,
    'is_verified': isVerified,
    'extra': extra,
  };

  UserInfo copyWith({
    String? name,
    String? avatar,
    String? role,
    String? email,
    String? phone,
    bool? isVerified,
    Map<String, dynamic>? extra,
  }) {
    return UserInfo(
      id: id,
      name: name ?? this.name,
      avatar: avatar ?? this.avatar,
      role: role ?? this.role,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      isVerified: isVerified ?? this.isVerified,
      extra: extra ?? this.extra,
    );
  }
} 