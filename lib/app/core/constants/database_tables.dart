class DatabaseTables {
  static const String users = 'users';
  static const String aiChats = 'ai_chats';
  static const String lifeRecords = 'life_records';
  static const String healthRecords = 'health_records';
  static const String feedbacks = 'feedbacks';
  static const String tags = 'tags';
  static const String settings = 'settings';

  static const Map<String, String> createTableSQL = {
    users: '''
      CREATE TABLE $users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        avatar TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''',

    aiChats: '''
      CREATE TABLE $aiChats (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        assistant_type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
      )
    ''',

    lifeRecords: '''
      CREATE TABLE $lifeRecords (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        is_sync INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
      )
    ''',

    healthRecords: '''
      CREATE TABLE $healthRecords (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        height REAL,
        weight REAL,
        blood_pressure TEXT,
        heart_rate INTEGER,
        recorded_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
      )
    '''
  };
} 