import '../data/remote/mysql/knowledge_database.dart';

class CommentService {
  final KnowledgeDatabase _knowledgeDb;

  CommentService(this._knowledgeDb);

  // 创建评论
  Future<String> createComment(Comment comment) async {
    final commentId = DateTime.now().millisecondsSinceEpoch.toString();
    
    await _knowledgeDb._conn.query('''
      INSERT INTO comments (
        id, content_id, user_id, parent_id, content,
        created_at
      ) VALUES (?, ?, ?, ?, ?, NOW())
    ''', [
      commentId,
      comment.contentId,
      comment.userId,
      comment.parentId,
      comment.content,
    ]);

    return commentId;
  }

  // 删除评论
  Future<void> deleteComment(String commentId) async {
    // 同时删除子评论
    await _knowledgeDb._conn.query('''
      DELETE FROM comments WHERE id = ? OR parent_id = ?
    ''', [commentId, commentId]);
  }

  // 获取评论列表
  Future<List<Comment>> getComments(
    String contentId, {
    String? parentId,
    int? limit,
    int? offset,
  }) async {
    var query = '''
      SELECT c.*, u.nickname, u.avatar 
      FROM comments c
      LEFT JOIN users u ON u.id = c.user_id
      WHERE c.content_id = ?
    ''';
    final params = [contentId];

    if (parentId != null) {
      query += ' AND c.parent_id = ?';
      params.add(parentId);
    } else {
      query += ' AND c.parent_id IS NULL';
    }

    query += ' ORDER BY c.created_at DESC';

    if (limit != null) {
      query += ' LIMIT ?';
      params.add(limit);

      if (offset != null) {
        query += ' OFFSET ?';
        params.add(offset);
      }
    }

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => Comment.fromJson(r.fields)).toList();
  }

  // 获取评论数量
  Future<int> getCommentCount(String contentId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT COUNT(*) as count FROM comments
      WHERE content_id = ?
    ''', [contentId]);

    return results.first['count'];
  }

  // 获取用户评论
  Future<List<Comment>> getUserComments(
    String userId, {
    int? limit,
    int? offset,
  }) async {
    var query = '''
      SELECT c.*, u.nickname, u.avatar 
      FROM comments c
      LEFT JOIN users u ON u.id = c.user_id
      WHERE c.user_id = ?
      ORDER BY c.created_at DESC
    ''';
    final params = [userId];

    if (limit != null) {
      query += ' LIMIT ?';
      params.add(limit);

      if (offset != null) {
        query += ' OFFSET ?';
        params.add(offset);
      }
    }

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => Comment.fromJson(r.fields)).toList();
  }
}

class Comment {
  final String id;
  final String contentId;
  final String userId;
  final String? parentId;
  final String content;
  final String? userNickname;
  final String? userAvatar;
  final DateTime createdAt;

  Comment({
    required this.id,
    required this.contentId,
    required this.userId,
    this.parentId,
    required this.content,
    this.userNickname,
    this.userAvatar,
    required this.createdAt,
  });

  factory Comment.fromJson(Map<String, dynamic> json) {
    return Comment(
      id: json['id'],
      contentId: json['content_id'],
      userId: json['user_id'],
      parentId: json['parent_id'],
      content: json['content'],
      userNickname: json['nickname'],
      userAvatar: json['avatar'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
} 