import '../storage/storage_service.dart';
import '../database/database_helper.dart';

class MigrationUtil {
  static Future<void> migrateFromHive() async {
    final storage = Get.find<StorageService>();
    
    // 迁移同步日志
    try {
      // 这里实现从 Hive 读取数据并写入 SQLite 的逻辑
    } catch (e) {
      print('Migration error: $e');
    }
  }
} 