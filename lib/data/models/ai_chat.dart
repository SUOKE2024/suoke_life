import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/hive_type_ids.dart';

part 'ai_chat.g.dart';

@HiveType(typeId: HiveTypeIds.aiChat)
class AIChat {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String role;

  @HiveField(2)
  final String content;

  @HiveField(3)
  final String time;

  AIChat({
    required this.id,
    required this.role,
    required this.content,
    required this.time,
  });
} 