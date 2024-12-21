import '../data/remote/mysql/knowledge_database.dart';

enum RelationType {
  follow,    // 关注
  friend,    // 好友
  block,     // 拉黑
}

class SocialService {
  final KnowledgeDatabase _knowledgeDb;

  SocialService(this._knowledgeDb);

  // 创建关系
  Future<void> createRelation(
    String userId,
    String targetId,
    RelationType type,
  ) async {
    await _knowledgeDb._conn.query('''
      INSERT INTO user_relations (
        user_id, target_id, type, created_at
      ) VALUES (?, ?, ?, NOW())
    ''', [
      userId,
      targetId,
      type.toString(),
    ]);

    // 如果是好友关系,需要双向建立
    if (type == RelationType.friend) {
      await _knowledgeDb._conn.query('''
        INSERT INTO user_relations (
          user_id, target_id, type, created_at
        ) VALUES (?, ?, ?, NOW())
      ''', [
        targetId,
        userId,
        type.toString(),
      ]);
    }
  }

  // 删除关系
  Future<void> deleteRelation(
    String userId,
    String targetId,
    RelationType type,
  ) async {
    await _knowledgeDb._conn.query('''
      DELETE FROM user_relations 
      WHERE user_id = ? AND target_id = ? AND type = ?
    ''', [
      userId,
      targetId,
      type.toString(),
    ]);

    // 如果是好友关系,需要双向删除
    if (type == RelationType.friend) {
      await _knowledgeDb._conn.query('''
        DELETE FROM user_relations 
        WHERE user_id = ? AND target_id = ? AND type = ?
      ''', [
        targetId,
        userId,
        type.toString(),
      ]);
    }
  }

  // 获取关注列表
  Future<List<UserRelation>> getFollowings(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT ur.*, u.nickname, u.avatar 
      FROM user_relations ur
      LEFT JOIN users u ON u.id = ur.target_id
      WHERE ur.user_id = ? AND ur.type = ?
      ORDER BY ur.created_at DESC
    ''', [userId, RelationType.follow.toString()]);

    return results.map((r) => UserRelation.fromJson(r.fields)).toList();
  }

  // 获取粉丝列表
  Future<List<UserRelation>> getFollowers(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT ur.*, u.nickname, u.avatar 
      FROM user_relations ur
      LEFT JOIN users u ON u.id = ur.user_id
      WHERE ur.target_id = ? AND ur.type = ?
      ORDER BY ur.created_at DESC
    ''', [userId, RelationType.follow.toString()]);

    return results.map((r) => UserRelation.fromJson(r.fields)).toList();
  }

  // 获取好友列表
  Future<List<UserRelation>> getFriends(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT ur.*, u.nickname, u.avatar 
      FROM user_relations ur
      LEFT JOIN users u ON u.id = ur.target_id
      WHERE ur.user_id = ? AND ur.type = ?
      ORDER BY ur.created_at DESC
    ''', [userId, RelationType.friend.toString()]);

    return results.map((r) => UserRelation.fromJson(r.fields)).toList();
  }

  // 检查关系
  Future<bool> checkRelation(
    String userId,
    String targetId,
    RelationType type,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT COUNT(*) as count 
      FROM user_relations
      WHERE user_id = ? AND target_id = ? AND type = ?
    ''', [
      userId,
      targetId,
      type.toString(),
    ]);

    return results.first['count'] > 0;
  }
}

class UserRelation {
  final String userId;
  final String targetId;
  final RelationType type;
  final String? nickname;
  final String? avatar;
  final DateTime createdAt;

  UserRelation({
    required this.userId,
    required this.targetId,
    required this.type,
    this.nickname,
    this.avatar,
    required this.createdAt,
  });

  factory UserRelation.fromJson(Map<String, dynamic> json) {
    return UserRelation(
      userId: json['user_id'],
      targetId: json['target_id'],
      type: RelationType.values.byName(json['type']),
      nickname: json['nickname'],
      avatar: json['avatar'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
} 