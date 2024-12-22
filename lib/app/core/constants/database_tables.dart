class DatabaseTables {
  static const String feedback = 'feedback';
  static const String syncConflict = 'sync_conflicts';
  static const String lifeRecord = 'life_records';
  static const String aiChat = 'ai_chats';
  static const String tag = 'tags';
  static const String syncConfig = 'sync_config';
  static const String syncLog = 'sync_logs';
  static const String exploreItem = 'explore_items';
  static const String healthSurvey = 'health_surveys';
  static const String service = 'services';

  static const Map<String, String> createTableSql = {
    // ... 表定义保持不变

    healthSurvey: '''
      CREATE TABLE IF NOT EXISTS $healthSurvey (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        type TEXT NOT NULL,
        answers TEXT NOT NULL,
        score INTEGER NOT NULL,
        result TEXT NOT NULL,
        suggestion TEXT,
        created_at TEXT NOT NULL
      )
    ''',

    service: '''
      CREATE TABLE IF NOT EXISTS $service (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        icon TEXT NOT NULL,
        route TEXT NOT NULL,
        config TEXT NOT NULL,
        is_enabled INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''',
  };
} 