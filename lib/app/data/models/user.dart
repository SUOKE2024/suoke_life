class User {
  final String id;
  final String name;
  final String? avatar;
  final String? email;
  final String? phone;
  final String? role;
  final Map<String, dynamic>? settings;
  final DateTime createdAt;

  User({
    required this.id,
    required this.name,
    this.avatar,
    this.email,
    this.phone,
    this.role,
    this.settings,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory User.fromMap(Map<String, dynamic> map) {
    return User(
      id: map['id'] as String,
      name: map['name'] as String,
      avatar: map['avatar'] as String?,
      email: map['email'] as String?,
      phone: map['phone'] as String?,
      role: map['role'] as String?,
      settings: map['settings'] != null 
          ? Map<String, dynamic>.from(map['settings'] as Map)
          : null,
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] as int),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'avatar': avatar,
      'email': email,
      'phone': phone,
      'role': role,
      'settings': settings,
      'created_at': createdAt.millisecondsSinceEpoch,
    };
  }
} 