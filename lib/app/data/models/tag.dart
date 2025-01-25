import 'package:flutter/material.dart';

class Tag {
  final String id;
  final String name;
  final DateTime createdAt;
  final DateTime? updatedAt;

  Tag({
    required this.id,
    required this.name,
    required this.createdAt,
    this.updatedAt,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'name': name,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt?.toIso8601String(),
  };

  factory Tag.fromMap(Map<String, dynamic> map) => Tag(
    id: map['id'],
    name: map['name'],
    createdAt: DateTime.parse(map['created_at']),
    updatedAt: map['updated_at'] != null 
        ? DateTime.parse(map['updated_at'])
        : null,
  );
} 