import 'package:flutter/material.dart';


class Service {
  final String id;
  final String name;
  final String description;
  final String iconPath;
  final bool isEnabled;

  Service({
    required this.id,
    required this.name,
    required this.description,
    required this.iconPath,
    this.isEnabled = true,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'name': name,
    'description': description,
    'icon_path': iconPath,
    'is_enabled': isEnabled ? 1 : 0,
  };

  factory Service.fromMap(Map<String, dynamic> map) => Service(
    id: map['id'],
    name: map['name'],
    description: map['description'],
    iconPath: map['icon_path'],
    isEnabled: map['is_enabled'] == 1,
  );
} 