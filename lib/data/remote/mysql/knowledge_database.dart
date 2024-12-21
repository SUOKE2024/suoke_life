import 'package:mysql1/mysql1.dart';

class KnowledgeDatabase {
  late MySqlConnection _conn;
  
  Future<void> init() async {
    final settings = ConnectionSettings(
      host: 'your-mysql-host',
      port: 3306,
      user: 'your-username',
      password: 'your-password',
      db: 'suoke_knowledge'
    );
    
    _conn = await MySqlConnection.connect(settings);
    
    // 初始化知识库表
    await _initTables();
  }

  Future<void> _initTables() async {
    // 健康知识库
    await _conn.query('''
      CREATE TABLE IF NOT EXISTS health_knowledge (
        id VARCHAR(32) PRIMARY KEY,
        category VARCHAR(32) NOT NULL,
        title VARCHAR(128) NOT NULL,
        content TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // 知识图谱关系
    await _conn.query('''
      CREATE TABLE IF NOT EXISTS knowledge_relations (
        id VARCHAR(32) PRIMARY KEY,
        source_id VARCHAR(32) NOT NULL,
        target_id VARCHAR(32) NOT NULL,
        relation_type VARCHAR(32) NOT NULL,
        weight FLOAT,
        metadata TEXT,
        FOREIGN KEY (source_id) REFERENCES health_knowledge(id),
        FOREIGN KEY (target_id) REFERENCES health_knowledge(id)
      )
    ''');

    // AI训练数据
    await _conn.query('''
      CREATE TABLE IF NOT EXISTS training_data (
        id VARCHAR(32) PRIMARY KEY,
        data_type VARCHAR(32) NOT NULL,
        content TEXT,
        metadata TEXT,
        is_validated BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');
  }
} 