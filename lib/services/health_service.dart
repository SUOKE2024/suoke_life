import '../data/local/database/app_database.dart';
import '../data/remote/mysql/knowledge_database.dart';

class HealthService {
  final AppDatabase _localDb;
  final KnowledgeDatabase _knowledgeDb;

  HealthService(this._localDb, this._knowledgeDb);

  // 保存健康检测数据
  Future<void> saveHealthDetection(Map<String, dynamic> data) async {
    final db = await _localDb.database;
    await db.insert('health_records', {
      'id': DateTime.now().millisecondsSinceEpoch.toString(),
      'type': 'detection',
      'value': data['value'],
      'metadata': data['metadata'].toString(),
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    });
  }

  // 获取中医体质分析
  Future<Map<String, dynamic>> getTCMConstitution(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM tcm_constitutions 
      WHERE user_id = ? 
      ORDER BY created_at DESC 
      LIMIT 1
    ''', [userId]);

    if (results.isNotEmpty) {
      return results.first.fields;
    }
    return {};
  }

  // 生成健康报告
  Future<Map<String, dynamic>> generateHealthReport(String userId) async {
    // 获取各项健康数据
    final db = await _localDb.database;
    final records = await db.query(
      'health_records',
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'timestamp DESC',
    );

    // 分析数据并生成报告
    return _analyzeHealthData(records);
  }

  Map<String, dynamic> _analyzeHealthData(List<Map<String, dynamic>> records) {
    // 实现健康数据分析逻辑
    return {};
  }
} 