import 'package:flutter/material.dart';

class Tag {
  final String id;
  final String name;
  final Color color;
  final DateTime createdAt;

  const Tag({
    required this.id,
    required this.name,
    required this.color,
    required this.createdAt,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'color': color.value.toRadixString(16),
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory Tag.fromJson(Map<String, dynamic> json) {
    return Tag(
      id: json['id'],
      name: json['name'],
      color: Color(int.parse(json['color'], radix: 16)),
      createdAt: DateTime.parse(json['created_at']),
    );
  }
} 