import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String name;
  final String? email;
  final String? phone;
  final String? avatar;
  final int? lastActive;
  final int createdAt;
  final int updatedAt;

  User({
    required this.id,
    required this.name,
    this.email,
    this.phone,
    this.avatar,
    this.lastActive,
    required this.createdAt,
    required this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
} 