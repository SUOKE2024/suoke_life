import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/hive_type_ids.dart';

part 'tag.g.dart';

@HiveType(typeId: HiveTypeIds.tag)
class Tag extends HiveObject {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String name;

  @HiveField(2)
  final DateTime createdAt;

  @HiveField(3)
  final DateTime? updatedAt;

  Tag({
    required this.id,
    required this.name,
    required this.createdAt,
    this.updatedAt,
  });

  factory Tag.fromJson(Map<String, dynamic> json) {
    return Tag(
      id: json['id'],
      name: json['name'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null 
          ? DateTime.parse(json['updatedAt'])
          : null,
    );
  }
} 