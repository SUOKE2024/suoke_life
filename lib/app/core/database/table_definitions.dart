class TableDefinitions {
  // 用户表
  static const String createUserTable = '''
    CREATE TABLE users (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT UNIQUE,
      phone TEXT UNIQUE,
      avatar TEXT,
      last_active INTEGER,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    )
  ''';

  // 聊天会话表
  static const String createChatSessionTable = '''
    CREATE TABLE chat_sessions (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      title TEXT NOT NULL,
      type TEXT NOT NULL,
      is_pinned INTEGER DEFAULT 0,
      last_message TEXT,
      last_message_time INTEGER,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
  ''';

  // 消息表
  static const String createMessageTable = '''
    CREATE TABLE messages (
      id TEXT PRIMARY KEY,
      session_id TEXT NOT NULL,
      sender_id TEXT NOT NULL,
      content TEXT NOT NULL,
      type TEXT NOT NULL,
      is_read INTEGER DEFAULT 0,
      created_at INTEGER NOT NULL,
      FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE,
      FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
    )
  ''';

  // 健康数据表
  static const String createHealthDataTable = '''
    CREATE TABLE health_data (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      type TEXT NOT NULL,
      value REAL NOT NULL,
      unit TEXT NOT NULL,
      timestamp INTEGER NOT NULL,
      notes TEXT,
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
  ''';

  // 设置表
  static const String createSettingsTable = '''
    CREATE TABLE settings (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      key TEXT NOT NULL,
      value TEXT NOT NULL,
      updated_at INTEGER NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
      UNIQUE(user_id, key)
    )
  ''';

  // 农业数据表
  static const String createAgricultureDataTable = '''
    CREATE TABLE agriculture_data (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      crop_type TEXT NOT NULL,
      planting_date INTEGER NOT NULL,
      harvest_date INTEGER,
      area REAL NOT NULL,
      location TEXT,
      status TEXT NOT NULL,
      notes TEXT,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
  ''';

  // 知识库表
  static const String createKnowledgeBaseTable = '''
    CREATE TABLE knowledge_base (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      category TEXT NOT NULL,
      tags TEXT,
      embeddings BLOB,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    )
  ''';
} 