import '../data/local/database/app_database.dart';
import '../data/local/cache/redis_cache.dart';
import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/oss/oss_storage.dart';

class StorageService {
  final AppDatabase _localDb;
  final RedisCache _cache;
  final KnowledgeDatabase _knowledgeDb;
  final OssStorage _ossStorage;

  StorageService({
    required AppDatabase localDb,
    required RedisCache cache,
    required KnowledgeDatabase knowledgeDb,
    required OssStorage ossStorage,
  })  : _localDb = localDb,
        _cache = cache,
        _knowledgeDb = knowledgeDb,
        _ossStorage = ossStorage;

  Future<void> init() async {
    await _cache.init();
    await _knowledgeDb.init();
    await _ossStorage.init();
  }

  // 健康记录相关操作
  Future<void> saveHealthRecord(Map<String, dynamic> record) async {
    final db = await _localDb.database;
    await db.insert('health_records', record);
  }

  // 生活记录相关操作
  Future<void> saveLifestyleRecord(Map<String, dynamic> record) async {
    final db = await _localDb.database;
    await db.insert('lifestyle_records', record);
  }

  // 缓存操作
  Future<void> cacheSessionData(String key, String value) async {
    await _cache.setSessionData(key, value);
  }

  // 知识库操作
  Future<List<Map<String, dynamic>>> queryHealthKnowledge(String category) async {
    final results = await _knowledgeDb._conn.query(
      'SELECT * FROM health_knowledge WHERE category = ?',
      [category],
    );
    return results.map((r) => r.fields).toList();
  }

  // 文件存储操作
  Future<String> uploadMediaFile(String filePath, String category) async {
    return await _ossStorage.uploadMedia(filePath, category);
  }
} 