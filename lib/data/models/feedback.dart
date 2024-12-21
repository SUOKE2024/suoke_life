import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/hive_type_ids.dart';

part 'feedback.g.dart';

@HiveType(typeId: HiveTypeIds.feedback)
class FeedbackRecord extends HiveObject {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String type;

  @HiveField(2)
  final String content;

  @HiveField(3)
  final String? contact;

  @HiveField(4)
  final List<String>? images;

  @HiveField(5)
  final String time;

  @HiveField(6)
  final String status;

  FeedbackRecord({
    required this.id,
    required this.type,
    required this.content,
    this.contact,
    this.images,
    required this.time,
    this.status = '待处理',
  });
} 