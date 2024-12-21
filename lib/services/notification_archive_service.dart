import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/s3/s3_storage.dart';

enum ArchiveStatus {
  pending,    // 待归档
  archived,   // 已归档
  restored,   // 已恢复
  failed,     // 归档失败
}

class NotificationArchiveService {
  final KnowledgeDatabase _knowledgeDb;
  final S3Storage _s3Storage;

  NotificationArchiveService(this._knowledgeDb, this._s3Storage);

  // 归档通知
  Future<void> archiveNotifications({
    required DateTime beforeDate,
    NotificationType? type,
    int batchSize = 1000,
  }) async {
    var offset = 0;
    while (true) {
      // 1. 获取待归档通知
      final notifications = await _getPendingArchiveNotifications(
        beforeDate: beforeDate,
        type: type,
        limit: batchSize,
        offset: offset,
      );

      if (notifications.isEmpty) {
        break;
      }

      // 2. 批量归档
      for (final notification in notifications) {
        try {
          await _archiveNotification(notification);
        } catch (e) {
          print('Error archiving notification ${notification.id}: $e');
          await _updateArchiveStatus(
            notification.id,
            ArchiveStatus.failed,
            error: e.toString(),
          );
        }
      }

      offset += notifications.length;
    }
  }

  // 恢复归档通知
  Future<Notification?> restoreNotification(String notificationId) async {
    // 1. 获取归档记录
    final archive = await _getArchiveRecord(notificationId);
    if (archive == null) {
      return null;
    }

    try {
      // 2. 从S3恢复数据
      final data = await _s3Storage.getObject(
        bucket: 'notifications-archive',
        key: _getArchiveKey(notificationId),
      );

      // 3. 恢复到数据库
      await _knowledgeDb._conn.query('''
        INSERT INTO notifications (
          id, type, priority, title, content, sender_id,
          receiver_id, channel, metadata, created_at, read_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''', [
        notificationId,
        ...data.values,
      ]);

      // 4. 更新归档状态
      await _updateArchiveStatus(notificationId, ArchiveStatus.restored);

      return Notification.fromJson(data);
    } catch (e) {
      print('Error restoring notification $notificationId: $e');
      await _updateArchiveStatus(
        notificationId,
        ArchiveStatus.failed,
        error: e.toString(),
      );
      return null;
    }
  }

  // 获取待归档通知
  Future<List<Notification>> _getPendingArchiveNotifications({
    required DateTime beforeDate,
    NotificationType? type,
    int? limit,
    int? offset,
  }) async {
    var query = '''
      SELECT n.* 
      FROM notifications n
      LEFT JOIN notification_archives a ON a.notification_id = n.id
      WHERE n.created_at < ?
      AND (a.status IS NULL OR a.status = ?)
    ''';
    final params = [
      beforeDate.toIso8601String(),
      ArchiveStatus.pending.toString(),
    ];

    if (type != null) {
      query += ' AND n.type = ?';
      params.add(type.toString());
    }

    query += ' ORDER BY n.created_at';

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

  // 归档单个通知
  Future<void> _archiveNotification(Notification notification) async {
    // 1. 上传到S3
    await _s3Storage.putObject(
      bucket: 'notifications-archive',
      key: _getArchiveKey(notification.id),
      data: notification.toJson(),
    );

    // 2. 记录归档
    await _knowledgeDb._conn.query('''
      INSERT INTO notification_archives (
        notification_id, status, created_at
      ) VALUES (?, ?, NOW())
      ON DUPLICATE KEY UPDATE
        status = VALUES(status),
        updated_at = NOW()
    ''', [
      notification.id,
      ArchiveStatus.archived.toString(),
    ]);

    // 3. 删除原始数据
    await _knowledgeDb._conn.query('''
      DELETE FROM notifications WHERE id = ?
    ''', [notification.id]);
  }

  // 获取归档记录
  Future<ArchiveRecord?> _getArchiveRecord(String notificationId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM notification_archives
      WHERE notification_id = ?
    ''', [notificationId]);

    if (results.isEmpty) {
      return null;
    }

    return ArchiveRecord.fromJson(results.first.fields);
  }

  // 更新归档状态
  Future<void> _updateArchiveStatus(
    String notificationId,
    ArchiveStatus status, {
    String? error,
  }) async {
    await _knowledgeDb._conn.query('''
      UPDATE notification_archives
      SET status = ?, error = ?, updated_at = NOW()
      WHERE notification_id = ?
    ''', [
      status.toString(),
      error,
      notificationId,
    ]);
  }

  // 获取归档键
  String _getArchiveKey(String notificationId) {
    return 'notifications/$notificationId.json';
  }
}

class ArchiveRecord {
  final String notificationId;
  final ArchiveStatus status;
  final String? error;
  final DateTime createdAt;
  final DateTime? updatedAt;

  ArchiveRecord({
    required this.notificationId,
    required this.status,
    this.error,
    required this.createdAt,
    this.updatedAt,
  });

  factory ArchiveRecord.fromJson(Map<String, dynamic> json) {
    return ArchiveRecord(
      notificationId: json['notification_id'],
      status: ArchiveStatus.values.byName(json['status']),
      error: json['error'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }
} 