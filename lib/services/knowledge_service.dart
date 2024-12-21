import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/oss/oss_storage.dart';

class KnowledgeService {
  final KnowledgeDatabase _knowledgeDb;
  final OssStorage _ossStorage;

  KnowledgeService(this._knowledgeDb, this._ossStorage);

  // 知识图谱操作
  Future<void> addKnowledgeRelation(
    String sourceId,
    String targetId,
    String relationType,
    double weight,
  ) async {
    await _knowledgeDb._conn.query('''
      INSERT INTO knowledge_relations (
        id, source_id, target_id, relation_type, weight
      ) VALUES (?, ?, ?, ?, ?)
    ''', [
      DateTime.now().millisecondsSinceEpoch.toString(),
      sourceId,
      targetId,
      relationType,
      weight,
    ]);
  }

  // 知识内容管理
  Future<void> addKnowledgeContent(Map<String, dynamic> content) async {
    // 如果包含多媒体内容,先上传到OSS
    if (content['media'] != null) {
      final mediaUrl = await _ossStorage.uploadMedia(
        content['media']['path'],
        content['media']['type'],
      );
      content['media_url'] = mediaUrl;
    }

    // 存储到知识库
    await _knowledgeDb._conn.query('''
      INSERT INTO health_knowledge (
        id, category, title, content, tags
      ) VALUES (?, ?, ?, ?, ?)
    ''', [
      DateTime.now().millisecondsSinceEpoch.toString(),
      content['category'],
      content['title'],
      content['content'],
      content['tags'].join(','),
    ]);
  }

  // 知识检索
  Future<List<Map<String, dynamic>>> searchKnowledge(
    String keyword,
    String category,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM health_knowledge 
      WHERE category = ? 
        AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)
    ''', [
      category,
      '%$keyword%',
      '%$keyword%',
      '%$keyword%',
    ]);

    return results.map((r) => r.fields).toList();
  }
} 