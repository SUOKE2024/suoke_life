import 'package:flutter/material.dart';
import 'package:json_annotation/json_annotation.dart';

part 'service.g.dart';

@JsonSerializable()
class Service {
  final String id;
  final String name;
  final IconData icon;
  final String type;
  final String? description;
  final Map<String, dynamic>? extra;

  Service({
    required this.id,
    required this.name,
    required this.icon,
    required this.type,
    this.description,
    this.extra,
  });

  factory Service.fromJson(Map<String, dynamic> json) => _$ServiceFromJson(json);
  Map<String, dynamic> toJson() => _$ServiceToJson(this);

  Service copyWith({
    String? id,
    String? name,
    IconData? icon,
    String? type,
    String? description,
    Map<String, dynamic>? extra,
  }) {
    return Service(
      id: id ?? this.id,
      name: name ?? this.name,
      icon: icon ?? this.icon,
      type: type ?? this.type,
      description: description ?? this.description,
      extra: extra ?? this.extra,
    );
  }
} 