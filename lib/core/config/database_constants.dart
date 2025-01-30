class DatabaseConstants {
  // 数据库名称
  static const String dbName = 'suoke.db';
  
  // 数据库版本
  static const int dbVersion = 1;
  
  // 表名
  static const String tableUsers = 'users';
  static const String tableAiChats = 'ai_chats';
  static const String tableLifeRecords = 'life_records';
  static const String tableSyncLogs = 'sync_logs';
  static const String tableTags = 'tags';
  static const String tableSyncConfigs = 'sync_configs';
  static const String tableHealthRecords = 'health_records';
  
  // 创建表的 SQL 语句
  static const String createTableSyncLogs = '''
    CREATE TABLE $tableSyncLogs (
      id TEXT PRIMARY KEY,
      time TEXT NOT NULL,
      type TEXT NOT NULL,
      success INTEGER NOT NULL,
      error TEXT,
      details TEXT
    )
  ''';
  
  static const String createTableTags = '''
    CREATE TABLE $tableTags (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT
    )
  ''';
  
  static const String createTableSyncConfigs = '''
    CREATE TABLE $tableSyncConfigs (
      id TEXT PRIMARY KEY,
      auto_sync INTEGER NOT NULL,
      wifi_only_sync INTEGER NOT NULL,
      sync_ranges TEXT NOT NULL,
      last_sync_time TEXT
    )
  ''';

  static const String createTableAiChats = '''
    CREATE TABLE $tableAiChats (
      id TEXT PRIMARY KEY,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      time TEXT NOT NULL
    )
  ''';

  static const String createTableFeedbacks = '''
    CREATE TABLE feedbacks (
      id TEXT PRIMARY KEY,
      type TEXT NOT NULL,
      content TEXT NOT NULL,
      contact TEXT,
      images TEXT,
      time TEXT NOT NULL,
      status TEXT NOT NULL
    )
  ''';
} 