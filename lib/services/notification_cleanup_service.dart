import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/redis/redis_cache.dart';

class NotificationCleanupService {
  final KnowledgeDatabase _knowledgeDb;
  final RedisCache _redisCache;

  NotificationCleanupService(this._knowledgeDb, this._redisCache);

  // 清理过期通知
  Future<CleanupResult> cleanupExpiredNotifications({
    required Duration retention,
    bool archive = true,
  }) async {
    final cutoff = DateTime.now().subtract(retention);
    
    // 1. 获取过期通知
    final expired = await _getExpiredNotifications(cutoff);
    
    // 2. 归档通知(如果需要)
    if (archive) {
      await _archiveNotifications(expired);
    }
    
    // 3. 删除通知
    final deleted = await _deleteNotifications(expired);
    
    // 4. 清理缓存
    await _cleanupCache(expired);

    return CleanupResult(
      totalCount: expired.length,
      deletedCount: deleted,
    );
  }

  // 获取过期通知
  Future<List<Notification>> _getExpiredNotifications(DateTime cutoff) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM notifications
      WHERE created_at < ?
      AND (read_at IS NOT NULL OR created_at < ?)
    ''', [
      cutoff.toIso8601String(),
      cutoff.subtract(Duration(days: 30)).toIso8601String(),
    ]);
    return results.map((r) => Notification.fromJson(r.fields)).toList();
  }

  // 归档通知
  Future<void> _archiveNotifications(List<Notification> notifications) async {
    // TODO: 调用归档服务进行归档
  }

  // 删除通知
  Future<int> _deleteNotifications(List<Notification> notifications) async {
    if (notifications.isEmpty) return 0;

    final ids = notifications.map((n) => n.id).join(',');
    final result = await _knowledgeDb._conn.query('''
      DELETE FROM notifications WHERE id IN (?)
    ''', [ids]);

    return result.affectedRows ?? 0;
  }

  // 清理缓存
  Future<void> _cleanupCache(List<Notification> notifications) async {
    final pipeline = _redisCache.pipeline();
    
    for (final notification in notifications) {
      pipeline.del('notification:${notification.id}');
      pipeline.del('notification:read:${notification.id}');
    }

    await pipeline.execute();
  }
}

class CleanupResult {
  final int totalCount;
  final int deletedCount;

  CleanupResult({
    required this.totalCount,
    required this.deletedCount,
  });
} 