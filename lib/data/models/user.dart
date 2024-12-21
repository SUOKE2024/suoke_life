class User {
  final String id;
  final String name;
  final String? avatar;
  final String? email;
  final String? phone;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  User({
    required this.id,
    required this.name,
    this.avatar,
    this.email,
    this.phone,
    this.createdAt,
    this.updatedAt,
  });

  User copyWith({
    String? name,
    String? avatar,
    String? email,
    String? phone,
  }) {
    return User(
      id: id,
      name: name ?? this.name,
      avatar: avatar ?? this.avatar,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      createdAt: createdAt,
      updatedAt: DateTime.now(),
    );
  }
} 