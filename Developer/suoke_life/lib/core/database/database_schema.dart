/// 数据库架构定义
/// 包含所有表名常量和Schema版本信息

class DatabaseSchema {
  // 私有构造函数，防止实例化
  DatabaseSchema._();
  
  // 当前Schema版本
  static const int schemaVersion = 1;
  
  // 表名常量
  static const String tableUsers = 'users';
  static const String tableHealthData = 'health_data';
  static const String tableKnowledgeNodes = 'knowledge_nodes';
  static const String tableConversations = 'conversations';
  static const String tableMessages = 'messages';
  static const String tableSessions = 'sessions';
  static const String tablePoints = 'points';
  static const String tablePointsTransactions = 'points_transactions';
  static const String tableVouchers = 'vouchers';
  static const String tableSubscriptions = 'subscriptions';
  static const String tableNotifications = 'notifications';
  static const String tableSettings = 'settings';
  
  // 索引名常量
  static const String idxUserEmail = 'idx_user_email';
  static const String idxUserUsername = 'idx_user_username';
  static const String idxHealthDataType = 'idx_health_data_type';
  static const String idxHealthDataUserId = 'idx_health_data_user_id';
  static const String idxKnowledgeNodeCategory = 'idx_knowledge_node_category';
  static const String idxConversationUserId = 'idx_conversation_user_id';
  static const String idxMessageConversationId = 'idx_message_conversation_id';

  // 创建用户表
  static const String createUserTable = '''
    CREATE TABLE IF NOT EXISTS $tableUsers (
      id TEXT PRIMARY KEY,
      username TEXT NOT NULL,
      email TEXT,
      display_name TEXT,
      avatar TEXT,
      phone_number TEXT,
      birthday TEXT,
      gender TEXT,
      height REAL,
      weight REAL,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
  ''';

  // 创建健康数据表
  static const String createHealthDataTable = '''
    CREATE TABLE IF NOT EXISTS $tableHealthData (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      data_type TEXT NOT NULL,
      value TEXT NOT NULL,
      timestamp TEXT NOT NULL,
      source TEXT,
      is_synced INTEGER DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES $tableUsers (id) ON DELETE CASCADE
    )
  ''';

  // 创建知识节点表
  static const String createKnowledgeNodeTable = '''
    CREATE TABLE IF NOT EXISTS $tableKnowledgeNodes (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      node_type TEXT NOT NULL,
      metadata TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
  ''';

  // 创建知识关系表
  static const String createKnowledgeRelationTable = '''
    CREATE TABLE IF NOT EXISTS $tableKnowledgeRelation (
      id TEXT PRIMARY KEY,
      source_id TEXT NOT NULL,
      target_id TEXT NOT NULL,
      relation_type TEXT NOT NULL,
      weight REAL DEFAULT 1.0,
      metadata TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY (source_id) REFERENCES $tableKnowledgeNodes (id) ON DELETE CASCADE,
      FOREIGN KEY (target_id) REFERENCES $tableKnowledgeNodes (id) ON DELETE CASCADE
    )
  ''';

  // 创建向量存储表
  static const String createVectorStoreTable = '''
    CREATE TABLE IF NOT EXISTS $tableVectorStore (
      id TEXT PRIMARY KEY,
      text TEXT NOT NULL,
      embedding TEXT NOT NULL,
      metadata TEXT,
      node_id TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY (node_id) REFERENCES $tableKnowledgeNodes (id) ON DELETE CASCADE
    )
  ''';
}
