import 'package:flutter/material.dart';

class Topic {
  final String id;
  final String name;
  final IconData icon;
  final Color color;
  final List<String> tags;
  final String? description;

  const Topic({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
    required this.tags,
    this.description,
  });

  Topic copyWith({
    String? id,
    String? name,
    IconData? icon,
    Color? color,
    List<String>? tags,
    String? description,
  }) {
    return Topic(
      id: id ?? this.id,
      name: name ?? this.name,
      icon: icon ?? this.icon,
      color: color ?? this.color,
      tags: tags ?? this.tags,
      description: description ?? this.description,
    );
  }
} 