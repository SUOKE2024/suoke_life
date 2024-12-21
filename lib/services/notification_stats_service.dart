import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/redis/redis_cache.dart';

class NotificationStatsService {
  final KnowledgeDatabase _knowledgeDb;
  final RedisCache _redisCache;

  NotificationStatsService(this._knowledgeDb, this._redisCache);

  // 获取通知统计
  Future<NotificationStats> getStats({
    DateTime? startTime,
    DateTime? endTime,
    String? userId,
    NotificationType? type,
    ChannelType? channel,
  }) async {
    var query = '''
      SELECT 
        COUNT(*) as total_count,
        COUNT(CASE WHEN read_at IS NOT NULL THEN 1 END) as read_count,
        COUNT(DISTINCT receiver_id) as user_count,
        AVG(CASE WHEN read_at IS NOT NULL 
            THEN TIMESTAMPDIFF(SECOND, created_at, read_at) 
            END) as avg_read_time
      FROM notifications
      WHERE 1=1
    ''';
    final params = <dynamic>[];

    if (startTime != null) {
      query += ' AND created_at >= ?';
      params.add(startTime.toIso8601String());
    }

    if (endTime != null) {
      query += ' AND created_at <= ?';
      params.add(endTime.toIso8601String());
    }

    if (userId != null) {
      query += ' AND receiver_id = ?';
      params.add(userId);
    }

    if (type != null) {
      query += ' AND type = ?';
      params.add(type.toString());
    }

    if (channel != null) {
      query += ' AND channel = ?';
      params.add(channel.toString());
    }

    final results = await _knowledgeDb._conn.query(query, params);
    return NotificationStats.fromJson(results.first.fields);
  }

  // 获取通知趋势
  Future<List<NotificationTrend>> getTrends({
    required Duration interval,
    required DateTime startTime,
    required DateTime endTime,
    NotificationType? type,
    ChannelType? channel,
  }) async {
    final intervalStr = switch (interval) {
      Duration(days: 1) => 'DAY',
      Duration(hours: 1) => 'HOUR',
      _ => throw ArgumentError('Unsupported interval'),
    };

    var query = '''
      SELECT 
        DATE_FORMAT(created_at, ${intervalStr == 'DAY' ? '%Y-%m-%d' : '%Y-%m-%d %H:00:00'}) as time_slot,
        COUNT(*) as count,
        COUNT(CASE WHEN read_at IS NOT NULL THEN 1 END) as read_count
      FROM notifications
      WHERE created_at BETWEEN ? AND ?
    ''';
    final params = [startTime.toIso8601String(), endTime.toIso8601String()];

    if (type != null) {
      query += ' AND type = ?';
      params.add(type.toString());
    }

    if (channel != null) {
      query += ' AND channel = ?';
      params.add(channel.toString());
    }

    query += ' GROUP BY time_slot ORDER BY time_slot';

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => NotificationTrend.fromJson(r.fields)).toList();
  }

  // 获取渠道统计
  Future<Map<ChannelType, ChannelStats>> getChannelStats({
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    var query = '''
      SELECT 
        channel,
        COUNT(*) as total_count,
        COUNT(CASE WHEN read_at IS NOT NULL THEN 1 END) as read_count,
        COUNT(DISTINCT receiver_id) as user_count,
        AVG(CASE WHEN read_at IS NOT NULL 
            THEN TIMESTAMPDIFF(SECOND, created_at, read_at) 
            END) as avg_read_time
      FROM notifications
      WHERE 1=1
    ''';
    final params = <String>[];

    if (startTime != null) {
      query += ' AND created_at >= ?';
      params.add(startTime.toIso8601String());
    }

    if (endTime != null) {
      query += ' AND created_at <= ?';
      params.add(endTime.toIso8601String());
    }

    query += ' GROUP BY channel';

    final results = await _knowledgeDb._conn.query(query, params);
    
    return Map.fromEntries(
      results.map((r) {
        final stats = ChannelStats.fromJson(r.fields);
        return MapEntry(
          ChannelType.values.byName(r['channel']),
          stats,
        );
      }),
    );
  }

  // 更新统计缓存
  Future<void> updateStatsCache() async {
    // 1. 获取最新统计
    final stats = await getStats(
      startTime: DateTime.now().subtract(Duration(days: 1)),
    );

    // 2. 更新缓存
    await _redisCache.setex(
      'notification:stats:daily',
      jsonEncode(stats.toJson()),
      Duration(hours: 1),
    );

    // 3. 获取渠道统计
    final channelStats = await getChannelStats(
      startTime: DateTime.now().subtract(Duration(days: 1)),
    );

    // 4. 更新渠道统计缓存
    await _redisCache.setex(
      'notification:stats:channels',
      jsonEncode(channelStats.map(
        (k, v) => MapEntry(k.toString(), v.toJson()),
      )),
      Duration(hours: 1),
    );
  }
}

class NotificationStats {
  final int totalCount;
  final int readCount;
  final int userCount;
  final double? avgReadTime;

  NotificationStats({
    required this.totalCount,
    required this.readCount,
    required this.userCount,
    this.avgReadTime,
  });

  factory NotificationStats.fromJson(Map<String, dynamic> json) {
    return NotificationStats(
      totalCount: json['total_count'],
      readCount: json['read_count'],
      userCount: json['user_count'],
      avgReadTime: json['avg_read_time'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_count': totalCount,
      'read_count': readCount,
      'user_count': userCount,
      'avg_read_time': avgReadTime,
    };
  }
}

class NotificationTrend {
  final DateTime timeSlot;
  final int count;
  final int readCount;

  NotificationTrend({
    required this.timeSlot,
    required this.count,
    required this.readCount,
  });

  factory NotificationTrend.fromJson(Map<String, dynamic> json) {
    return NotificationTrend(
      timeSlot: DateTime.parse(json['time_slot']),
      count: json['count'],
      readCount: json['read_count'],
    );
  }
}

class ChannelStats extends NotificationStats {
  final double deliveryRate;
  final double readRate;

  ChannelStats({
    required super.totalCount,
    required super.readCount,
    required super.userCount,
    super.avgReadTime,
    required this.deliveryRate,
    required this.readRate,
  });

  factory ChannelStats.fromJson(Map<String, dynamic> json) {
    final stats = NotificationStats.fromJson(json);
    return ChannelStats(
      totalCount: stats.totalCount,
      readCount: stats.readCount,
      userCount: stats.userCount,
      avgReadTime: stats.avgReadTime,
      deliveryRate: json['delivery_rate'] ?? 0.0,
      readRate: json['read_rate'] ?? 0.0,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      ...super.toJson(),
      'delivery_rate': deliveryRate,
      'read_rate': readRate,
    };
  }
} 