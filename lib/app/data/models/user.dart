import 'package:injectable/injectable.dart';

@injectable
class User {
  final String id;
  final String name;
  final String? email;
  final String? avatarUrl;
  final DateTime createdAt;

  const User({
    required this.id,
    required this.name,
    this.email,
    this.avatarUrl,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      name: json['name'] as String,
      email: json['email'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'avatar_url': avatarUrl,
      'created_at': createdAt.toIso8601String(),
    };
  }
} 