class StorageService extends GetxService {
  final SecurityManagerService _securityManager;
  final CacheManagerService _cacheManager;
  final SyncManagerService _syncManager;
  
  // 存储配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _storageConfig = {
    SubscriptionPlan.basic: {
      'max_storage': 100 * 1024 * 1024,  // 100MB
      'backup_enabled': false,
      'encryption': 'basic',
      'retention_days': 30,
    },
    SubscriptionPlan.pro: {
      'max_storage': 1024 * 1024 * 1024,  // 1GB
      'backup_enabled': true,
      'encryption': 'advanced',
      'retention_days': 90,
    },
    SubscriptionPlan.premium: {
      'max_storage': -1,  // 无限制
      'backup_enabled': true,
      'encryption': 'military',
      'retention_days': 365,
    },
  };
  
  // 数据库实例
  late final Database _db;
  
  StorageService({
    required SecurityManagerService securityManager,
    required CacheManagerService cacheManager,
    required SyncManagerService syncManager,
  })  : _securityManager = securityManager,
        _cacheManager = cacheManager,
        _syncManager = syncManager;

  @override
  Future<void> onInit() async {
    super.onInit();
    await _initDatabase();
  }

  Future<void> _initDatabase() async {
    try {
      // 初始化数据库
      _db = await openDatabase(
        'ai_assistant.db',
        version: 1,
        onCreate: (db, version) async {
          // 创建表
          await _createTables(db);
        },
        onUpgrade: (db, oldVersion, newVersion) async {
          // 处理数据库升级
          await _handleUpgrade(db, oldVersion, newVersion);
        },
      );
    } catch (e) {
      throw AIException(
        '初始化数据库失败',
        code: 'DB_INIT_ERROR',
        details: e,
      );
    }
  }

  Future<void> _createTables(Database db) async {
    // 创建聊天记录表
    await db.execute('''
      CREATE TABLE chat_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        assistant_name TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT
      )
    ''');

    // 创建知识库文档表
    await db.execute('''
      CREATE TABLE knowledge_documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        type TEXT NOT NULL,
        collection_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        tags TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT
      )
    ''');

    // 创建知识库集合表
    await db.execute('''
      CREATE TABLE knowledge_collections (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        user_id TEXT NOT NULL,
        tags TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT
      )
    ''');

    // 创建配置表
    await db.execute('''
      CREATE TABLE configs (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        scope TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT
      )
    ''');

    // 创建缓存表
    await db.execute('''
      CREATE TABLE cache_entries (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        type TEXT NOT NULL,
        expiry TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL
      )
    ''');
  }

  Future<void> _handleUpgrade(Database db, int oldVersion, int newVersion) async {
    // TODO: 实现数据库升级逻辑
  }

  Future<void> saveDocument(KnowledgeDocument document) async {
    try {
      final encryptedContent = await _securityManager.encryptData(document.content);
      
      await _db.insert(
        'knowledge_documents',
        {
          ...document.toMap(),
          'content': encryptedContent,
          'tags': document.tags?.join(','),
          'metadata': jsonEncode(document.metadata),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      // 触发同步
      await _syncManager.sync('knowledge');
    } catch (e) {
      throw AIException(
        '保存文档失败',
        code: 'SAVE_DOCUMENT_ERROR',
        details: e,
      );
    }
  }

  Future<void> saveCollection(KnowledgeCollection collection) async {
    try {
      await _db.insert(
        'knowledge_collections',
        {
          ...collection.toMap(),
          'tags': collection.tags?.join(','),
          'metadata': jsonEncode(collection.metadata),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      // 触发同步
      await _syncManager.sync('knowledge');
    } catch (e) {
      throw AIException(
        '保存集合失败',
        code: 'SAVE_COLLECTION_ERROR',
        details: e,
      );
    }
  }

  Future<void> saveChatHistory(ChatMessage message) async {
    try {
      final encryptedContent = await _securityManager.encryptData(message.content);
      
      await _db.insert(
        'chat_history',
        {
          'id': message.id,
          'user_id': message.userId,
          'assistant_name': message.assistantName,
          'message': encryptedContent,
          'type': message.type.toString(),
          'timestamp': message.timestamp.toIso8601String(),
          'metadata': jsonEncode(message.metadata),
          'created_at': DateTime.now().toIso8601String(),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      // 触发同步
      await _syncManager.sync('chat');
    } catch (e) {
      throw AIException(
        '保存聊天记录失败',
        code: 'SAVE_CHAT_ERROR',
        details: e,
      );
    }
  }

  Future<void> saveConfig(
    String key,
    String scope,
    dynamic value, {
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final encryptedValue = await _securityManager.encryptData(jsonEncode(value));
      
      await _db.insert(
        'configs',
        {
          'key': key,
          'value': encryptedValue,
          'scope': scope,
          'metadata': jsonEncode(metadata),
          'created_at': DateTime.now().toIso8601String(),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      // 更新缓存
      await _cacheManager.set(
        key,
        value,
        type: 'config',
        metadata: metadata,
      );
    } catch (e) {
      throw AIException(
        '保存配置失败',
        code: 'SAVE_CONFIG_ERROR',
        details: e,
      );
    }
  }

  Future<void> setCacheEntry(
    String key,
    Map<String, dynamic> entry,
  ) async {
    try {
      await _db.insert(
        'cache_entries',
        {
          'key': key,
          'value': jsonEncode(entry['value']),
          'type': entry['type'],
          'expiry': entry['expiry'],
          'metadata': jsonEncode(entry['metadata']),
          'created_at': DateTime.now().toIso8601String(),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    } catch (e) {
      throw AIException(
        '保存缓存失败',
        code: 'SAVE_CACHE_ERROR',
        details: e,
      );
    }
  }

  Future<void> deleteDocument(String documentId) async {
    try {
      await _db.delete(
        'knowledge_documents',
        where: 'id = ?',
        whereArgs: [documentId],
      );

      // 触发同步
      await _syncManager.sync('knowledge');
    } catch (e) {
      throw AIException(
        '删除文档失败',
        code: 'DELETE_DOCUMENT_ERROR',
        details: e,
      );
    }
  }

  Future<void> cleanExpiredCache() async {
    try {
      final now = DateTime.now().toIso8601String();
      await _db.delete(
        'cache_entries',
        where: 'expiry < ?',
        whereArgs: [now],
      );
    } catch (e) {
      throw AIException(
        '清理过期缓存失败',
        code: 'CLEAN_CACHE_ERROR',
        details: e,
      );
    }
  }

  @override
  void onClose() {
    _db.close();
    super.onClose();
  }
} 