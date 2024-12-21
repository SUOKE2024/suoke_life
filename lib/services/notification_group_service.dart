import '../data/remote/mysql/knowledge_database.dart';

class NotificationGroupService {
  final KnowledgeDatabase _knowledgeDb;

  NotificationGroupService(this._knowledgeDb);

  // 创建通知组
  Future<String> createGroup(NotificationGroup group) async {
    final groupId = DateTime.now().millisecondsSinceEpoch.toString();
    
    await _knowledgeDb._conn.query('''
      INSERT INTO notification_groups (
        id, title, summary, type, count, metadata,
        created_at
      ) VALUES (?, ?, ?, ?, ?, ?, NOW())
    ''', [
      groupId,
      group.title,
      group.summary,
      group.type.toString(),
      group.count,
      group.metadata != null ? jsonEncode(group.metadata) : null,
    ]);

    // 关联通知
    if (group.notificationIds.isNotEmpty) {
      final batch = group.notificationIds.map((notificationId) => [
        groupId,
        notificationId,
      ]).toList();

      await _knowledgeDb._conn.queryMulti('''
        INSERT INTO notification_group_items (
          group_id, notification_id
        ) VALUES (?, ?)
      ''', batch);
    }

    return groupId;
  }

  // 添加通知到��
  Future<void> addToGroup(String groupId, List<String> notificationIds) async {
    final batch = notificationIds.map((notificationId) => [
      groupId,
      notificationId,
    ]).toList();

    await _knowledgeDb._conn.queryMulti('''
      INSERT INTO notification_group_items (
        group_id, notification_id
      ) VALUES (?, ?)
    ''', batch);

    // 更新组计数
    await _knowledgeDb._conn.query('''
      UPDATE notification_groups
      SET count = count + ?,
          updated_at = NOW()
      WHERE id = ?
    ''', [notificationIds.length, groupId]);
  }

  // 从组中移除通知
  Future<void> removeFromGroup(
    String groupId,
    List<String> notificationIds,
  ) async {
    await _knowledgeDb._conn.query('''
      DELETE FROM notification_group_items 
      WHERE group_id = ? AND notification_id IN (?)
    ''', [groupId, notificationIds.join(',')]);

    // 更新组计数
    await _knowledgeDb._conn.query('''
      UPDATE notification_groups
      SET count = count - ?,
          updated_at = NOW()
      WHERE id = ?
    ''', [notificationIds.length, groupId]);
  }

  // 获取通知组列表
  Future<List<NotificationGroup>> getGroups({
    NotificationType? type,
    bool includeItems = false,
  }) async {
    var query = '''
      SELECT g.*, 
      ${includeItems ? '(
        SELECT GROUP_CONCAT(notification_id)
        FROM notification_group_items
        WHERE group_id = g.id
      ) as notification_ids,' : ''}
      COUNT(i.notification_id) as actual_count
      FROM notification_groups g
      LEFT JOIN notification_group_items i ON i.group_id = g.id
      WHERE 1=1
    ''';
    final params = <String>[];

    if (type != null) {
      query += ' AND g.type = ?';
      params.add(type.toString());
    }

    query += ' GROUP BY g.id ORDER BY g.created_at DESC';

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => NotificationGroup.fromJson(r.fields)).toList();
  }

  // 获取组内通知
  Future<List<Notification>> getGroupNotifications(
    String groupId, {
    int? limit,
    int? offset,
  }) async {
    var query = '''
      SELECT n.* FROM notifications n
      INNER JOIN notification_group_items i ON i.notification_id = n.id
      WHERE i.group_id = ?
      ORDER BY n.created_at DESC
    ''';
    final params = [groupId];

    if (limit != null) {
      query += ' LIMIT ?';
      params.add(limit);

      if (offset != null) {
        query += ' OFFSET ?';
        params.add(offset);
      }
    }

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => Notification.fromJson(r.fields)).toList();
  }

  // 删除通知组
  Future<void> deleteGroup(String groupId) async {
    await _knowledgeDb._conn.query('''
      DELETE FROM notification_groups WHERE id = ?
    ''', [groupId]);

    await _knowledgeDb._conn.query('''
      DELETE FROM notification_group_items WHERE group_id = ?
    ''', [groupId]);
  }
}

class NotificationGroup {
  final String id;
  final String title;
  final String summary;
  final NotificationType type;
  final int count;
  final Map<String, dynamic>? metadata;
  final List<String> notificationIds;
  final DateTime createdAt;
  final DateTime? updatedAt;

  NotificationGroup({
    required this.id,
    required this.title,
    required this.summary,
    required this.type,
    required this.count,
    this.metadata,
    this.notificationIds = const [],
    required this.createdAt,
    this.updatedAt,
  });

  factory NotificationGroup.fromJson(Map<String, dynamic> json) {
    return NotificationGroup(
      id: json['id'],
      title: json['title'],
      summary: json['summary'],
      type: NotificationType.values.byName(json['type']),
      count: json['count'],
      metadata: json['metadata'] != null ? jsonDecode(json['metadata']) : null,
      notificationIds: json['notification_ids'] != null
          ? (json['notification_ids'] as String).split(',')
          : [],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }
} 