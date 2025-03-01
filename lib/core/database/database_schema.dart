import 'package:sqflite/sqflite.dart';

/// 数据库架构定义
/// 统一管理所有表结构和版本升级
class DatabaseSchema {
  // 数据库名称与版本
  static const String databaseName = 'suoke_life.db';
  static const int databaseVersion = 1;
  
  // 表名常量
  static const String tableUsers = 'users';
  static const String tableHealthData = 'health_data';
  static const String tableKnowledgeNodes = 'knowledge_nodes';
  static const String tableNodeRelations = 'node_relations';
  static const String tableUserSettings = 'user_settings';
  static const String tableChatMessages = 'chat_messages';
  static const String tableLifeRecords = 'life_records';
  static const String tableHealthPlans = 'health_plans';
  
  // 创建所有表
  static Future<void> createAllTables(Database db) async {
    await db.transaction((txn) async {
      // 用户表
      await txn.execute(createUsersTable);
      
      // 健康数据表
      await txn.execute(createHealthDataTable);
      
      // 知识节点表
      await txn.execute(createKnowledgeNodesTable);
      
      // 节点关系表
      await txn.execute(createNodeRelationsTable);
      
      // 用户设置表
      await txn.execute(createUserSettingsTable);
      
      // 聊天消息表
      await txn.execute(createChatMessagesTable);
      
      // 生活记录表
      await txn.execute(createLifeRecordsTable);
      
      // 健康计划表
      await txn.execute(createHealthPlansTable);
    });
  }
  
  // 数据库升级函数
  static Future<void> upgradeDatabase(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // 未来的版本2升级代码
    }
  }
  
  // 用户表SQL
  static const String createUsersTable = '''
    CREATE TABLE $tableUsers (
      id TEXT PRIMARY KEY,
      username TEXT NOT NULL,
      email TEXT,
      phone TEXT,
      avatar_url TEXT,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL,
      last_login INTEGER,
      account_type TEXT NOT NULL,
      sync_status TEXT DEFAULT 'pending'
    )
  ''';
  
  // 健康数据表SQL
  static const String createHealthDataTable = '''
    CREATE TABLE $tableHealthData (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      type TEXT NOT NULL,
      value REAL NOT NULL,
      unit TEXT NOT NULL,
      timestamp INTEGER NOT NULL,
      source TEXT,
      metadata TEXT,
      tags TEXT,
      notes TEXT,
      synced INTEGER NOT NULL DEFAULT 0,
      is_deleted INTEGER NOT NULL DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES $tableUsers (id) ON DELETE CASCADE
    )
  ''';
  
  // 知识节点表SQL
  static const String createKnowledgeNodesTable = '''
    CREATE TABLE $tableKnowledgeNodes (
      id TEXT PRIMARY KEY,
      type TEXT NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      content TEXT,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL,
      metadata TEXT,
      embedding BLOB,
      language TEXT DEFAULT 'zh-CN'
    )
  ''';
  
  // 节点关系表SQL
  static const String createNodeRelationsTable = '''
    CREATE TABLE $tableNodeRelations (
      id TEXT PRIMARY KEY,
      source_node_id TEXT NOT NULL,
      target_node_id TEXT NOT NULL,
      relation_type TEXT NOT NULL,
      weight REAL,
      metadata TEXT,
      FOREIGN KEY (source_node_id) REFERENCES $tableKnowledgeNodes (id) ON DELETE CASCADE,
      FOREIGN KEY (target_node_id) REFERENCES $tableKnowledgeNodes (id) ON DELETE CASCADE
    )
  ''';
  
  // 用户设置表SQL
  static const String createUserSettingsTable = '''
    CREATE TABLE $tableUserSettings (
      user_id TEXT PRIMARY KEY,
      theme_mode TEXT NOT NULL DEFAULT 'system',
      notification_enabled INTEGER NOT NULL DEFAULT 1,
      language TEXT NOT NULL DEFAULT 'zh_CN',
      last_sync INTEGER,
      security_level TEXT DEFAULT 'medium',
      privacy_settings TEXT,
      ai_preferences TEXT,
      FOREIGN KEY (user_id) REFERENCES $tableUsers (id) ON DELETE CASCADE
    )
  ''';
  
  // 聊天消息表SQL
  static const String createChatMessagesTable = '''
    CREATE TABLE $tableChatMessages (
      id TEXT PRIMARY KEY,
      chat_id TEXT NOT NULL,
      user_id TEXT NOT NULL,
      content TEXT NOT NULL,
      timestamp INTEGER NOT NULL,
      is_user INTEGER NOT NULL DEFAULT 1,
      message_type TEXT DEFAULT 'text',
      metadata TEXT,
      synced INTEGER NOT NULL DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES $tableUsers (id) ON DELETE CASCADE
    )
  ''';
  
  // 生活记录表SQL
  static const String createLifeRecordsTable = '''
    CREATE TABLE $tableLifeRecords (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      record_type TEXT NOT NULL,
      timestamp INTEGER NOT NULL,
      tags TEXT,
      location TEXT,
      media_urls TEXT,
      synced INTEGER NOT NULL DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES $tableUsers (id) ON DELETE CASCADE
    )
  ''';
  
  // 健康计划表SQL
  static const String createHealthPlansTable = '''
    CREATE TABLE $tableHealthPlans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      plan_type TEXT NOT NULL,
      start_date INTEGER NOT NULL,
      end_date INTEGER,
      frequency TEXT,
      targets TEXT,
      progress REAL DEFAULT 0,
      status TEXT DEFAULT 'active',
      metadata TEXT,
      synced INTEGER NOT NULL DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES $tableUsers (id) ON DELETE CASCADE
    )
  ''';
}