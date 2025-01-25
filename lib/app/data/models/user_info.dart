class UserInfo {
  final String id;
  final String name;
  final String email;
  final String avatar;
  final String role;

  UserInfo({
    required this.id,
    required this.name,
    required this.email,
    required this.avatar,
    this.role = 'user',
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'email': email,
    'avatar': avatar,
    'role': role,
  };
} 