import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/redis/redis_cache.dart';

enum LikeType {
  content,  // 内容点赞
  comment,  // 评论点赞
}

class LikeService {
  final KnowledgeDatabase _knowledgeDb;
  final RedisCache _redisCache;

  LikeService(this._knowledgeDb, this._redisCache);

  // 点赞
  Future<void> like(
    String userId,
    String targetId,
    LikeType type,
  ) async {
    // 1. 检查是否已点赞
    if (await checkLike(userId, targetId, type)) {
      return;
    }

    // 2. 添加点赞记录
    await _knowledgeDb._conn.query('''
      INSERT INTO user_likes (
        user_id, target_id, type, created_at
      ) VALUES (?, ?, ?, NOW())
    ''', [
      userId,
      targetId,
      type.toString(),
    ]);

    // 3. 更新点赞计数
    final cacheKey = _getLikeCacheKey(targetId, type);
    await _redisCache.increment(cacheKey);
  }

  // 取消点赞
  Future<void> unlike(
    String userId,
    String targetId,
    LikeType type,
  ) async {
    // 1. 删除点赞记录
    await _knowledgeDb._conn.query('''
      DELETE FROM user_likes 
      WHERE user_id = ? AND target_id = ? AND type = ?
    ''', [
      userId,
      targetId,
      type.toString(),
    ]);

    // 2. 更新点赞计数
    final cacheKey = _getLikeCacheKey(targetId, type);
    await _redisCache.decrement(cacheKey);
  }

  // 检查是否已点赞
  Future<bool> checkLike(
    String userId,
    String targetId,
    LikeType type,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT COUNT(*) as count FROM user_likes
      WHERE user_id = ? AND target_id = ? AND type = ?
    ''', [
      userId,
      targetId,
      type.toString(),
    ]);

    return results.first['count'] > 0;
  }

  // 获取点赞数量
  Future<int> getLikeCount(String targetId, LikeType type) async {
    final cacheKey = _getLikeCacheKey(targetId, type);
    
    // 1. 尝试从缓存获取
    final cached = await _redisCache.get(cacheKey);
    if (cached != null) {
      return int.parse(cached);
    }

    // 2. 从数据库获取
    final results = await _knowledgeDb._conn.query('''
      SELECT COUNT(*) as count FROM user_likes
      WHERE target_id = ? AND type = ?
    ''', [targetId, type.toString()]);

    final count = results.first['count'] as int;
    
    // 3. 更新缓存
    await _redisCache.set(cacheKey, count.toString());
    
    return count;
  }

  // 获取用户点赞列表
  Future<List<Like>> getUserLikes(
    String userId,
    LikeType type, {
    int? limit,
    int? offset,
  }) async {
    var query = '''
      SELECT l.*, c.title, c.summary 
      FROM user_likes l
      LEFT JOIN contents c ON c.id = l.target_id
      WHERE l.user_id = ? AND l.type = ?
      ORDER BY l.created_at DESC
    ''';
    final params = [userId, type.toString()];

    if (limit != null) {
      query += ' LIMIT ?';
      params.add(limit);

      if (offset != null) {
        query += ' OFFSET ?';
        params.add(offset);
      }
    }

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => Like.fromJson(r.fields)).toList();
  }

  // 获取点赞缓存键
  String _getLikeCacheKey(String targetId, LikeType type) {
    return 'like:${type.toString()}:$targetId';
  }
}

class Like {
  final String userId;
  final String targetId;
  final LikeType type;
  final String? title;
  final String? summary;
  final DateTime createdAt;

  Like({
    required this.userId,
    required this.targetId,
    required this.type,
    this.title,
    this.summary,
    required this.createdAt,
  });

  factory Like.fromJson(Map<String, dynamic> json) {
    return Like(
      userId: json['user_id'],
      targetId: json['target_id'],
      type: LikeType.values.byName(json['type']),
      title: json['title'],
      summary: json['summary'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
} 