import 'package:hive_flutter/hive_flutter.dart';
import 'package:suoke_life/data/models/sync_config.dart';
import 'package:suoke_life/data/models/sync_log.dart';
import 'package:suoke_life/data/models/sync_conflict.dart';
import 'package:suoke_life/data/models/tag.dart';

/// 初始化 Hive
Future<void> initHive() async {
  // 初始化 Hive
  await Hive.initFlutter();

  // 注册适配器
  Hive.registerAdapter(SyncConfigAdapter());
  Hive.registerAdapter(SyncLogAdapter());
  Hive.registerAdapter(SyncConflictAdapter());
  Hive.registerAdapter(TagAdapter());

  // 打开盒子
  await Hive.openBox<Tag>('tags');
} 