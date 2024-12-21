import 'package:json_annotation/json_annotation.dart';

part 'explore_item.g.dart';

@JsonSerializable()
class ExploreItem {
  final String id;
  final String title;
  final String subtitle;
  final String? imageUrl;
  final String type;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;

  ExploreItem({
    required this.id,
    required this.title,
    required this.subtitle,
    this.imageUrl,
    required this.type,
    this.metadata,
    required this.createdAt,
  });

  factory ExploreItem.fromJson(Map<String, dynamic> json) => _$ExploreItemFromJson(json);
  Map<String, dynamic> toJson() => _$ExploreItemToJson(this);
} 