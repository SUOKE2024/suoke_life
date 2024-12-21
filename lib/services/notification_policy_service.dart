import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/redis/redis_cache.dart';

enum PolicyType {
  frequency,  // 频率控制
  channel,    // 渠道控制
  time,       // 时间控制
  priority,   // 优先级控制
}

class NotificationPolicyService {
  final KnowledgeDatabase _knowledgeDb;
  final RedisCache _redisCache;

  NotificationPolicyService(this._knowledgeDb, this._redisCache);

  // 检查通知策略
  Future<bool> checkPolicy(
    String userId,
    NotificationType type,
    NotificationPriority priority,
  ) async {
    // 1. 检查频率限制
    if (!await _checkFrequencyLimit(userId, type)) {
      return false;
    }

    // 2. 检查时间窗口
    if (!await _checkTimeWindow(userId, type)) {
      return false;
    }

    // 3. 检查优先级
    if (!await _checkPriorityThreshold(userId, priority)) {
      return false;
    }

    // 4. 检查用户设置
    if (!await _checkUserSettings(userId, type)) {
      return false;
    }

    return true;
  }

  // 检查频率限制
  Future<bool> _checkFrequencyLimit(String userId, NotificationType type) async {
    final key = 'notification:frequency:$userId:${type.toString()}';
    final count = await _redisCache.get(key);

    if (count == null) {
      await _redisCache.setex(key, '1', Duration(hours: 1));
      return true;
    }

    final policy = await _getFrequencyPolicy(type);
    return int.parse(count) < policy.maxCount;
  }

  // 检查时间窗口
  Future<bool> _checkTimeWindow(String userId, NotificationType type) async {
    final now = DateTime.now();
    final hour = now.hour;

    final policy = await _getTimeWindowPolicy(userId, type);
    return hour >= policy.startHour && hour <= policy.endHour;
  }

  // 检查优先级阈值
  Future<bool> _checkPriorityThreshold(
    String userId,
    NotificationPriority priority,
  ) async {
    final settings = await _getUserNotificationSettings(userId);
    final threshold = NotificationPriority.values.indexOf(settings.minPriority);
    return NotificationPriority.values.indexOf(priority) >= threshold;
  }

  // 检查用户设置
  Future<bool> _checkUserSettings(String userId, NotificationType type) async {
    final settings = await _getUserNotificationSettings(userId);
    return settings.enabledTypes.contains(type);
  }

  // 更新频率计数
  Future<void> incrementFrequencyCount(
    String userId,
    NotificationType type,
  ) async {
    final key = 'notification:frequency:$userId:${type.toString()}';
    await _redisCache.increment(key);
  }

  // 获取频率策略
  Future<FrequencyPolicy> _getFrequencyPolicy(NotificationType type) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM notification_policies
      WHERE type = ? AND policy_type = ?
    ''', [type.toString(), PolicyType.frequency.toString()]);

    if (results.isEmpty) {
      return FrequencyPolicy.defaultPolicy();
    }

    return FrequencyPolicy.fromJson(results.first.fields);
  }

  // 获取时间窗口策略
  Future<TimeWindowPolicy> _getTimeWindowPolicy(
    String userId,
    NotificationType type,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM notification_policies
      WHERE type = ? AND policy_type = ?
    ''', [type.toString(), PolicyType.time.toString()]);

    if (results.isEmpty) {
      return TimeWindowPolicy.defaultPolicy();
    }

    return TimeWindowPolicy.fromJson(results.first.fields);
  }

  // 获取用户通知设置
  Future<NotificationSettings> _getUserNotificationSettings(
    String userId,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM user_notification_settings
      WHERE user_id = ?
    ''', [userId]);

    if (results.isEmpty) {
      return NotificationSettings.defaultSettings();
    }

    return NotificationSettings.fromJson(results.first.fields);
  }

  // 更新用户通知设置
  Future<void> updateUserSettings(
    String userId,
    NotificationSettings settings,
  ) async {
    await _knowledgeDb._conn.query('''
      INSERT INTO user_notification_settings (
        user_id, enabled_types, min_priority, quiet_start,
        quiet_end, updated_at
      ) VALUES (?, ?, ?, ?, ?, NOW())
      ON DUPLICATE KEY UPDATE
        enabled_types = VALUES(enabled_types),
        min_priority = VALUES(min_priority),
        quiet_start = VALUES(quiet_start),
        quiet_end = VALUES(quiet_end),
        updated_at = NOW()
    ''', [
      userId,
      settings.enabledTypes.map((t) => t.toString()).join(','),
      settings.minPriority.toString(),
      settings.quietStart,
      settings.quietEnd,
    ]);
  }
}

class FrequencyPolicy {
  final NotificationType type;
  final int maxCount;
  final Duration window;

  FrequencyPolicy({
    required this.type,
    required this.maxCount,
    required this.window,
  });

  factory FrequencyPolicy.defaultPolicy() {
    return FrequencyPolicy(
      type: NotificationType.system,
      maxCount: 10,
      window: Duration(hours: 1),
    );
  }

  factory FrequencyPolicy.fromJson(Map<String, dynamic> json) {
    return FrequencyPolicy(
      type: NotificationType.values.byName(json['type']),
      maxCount: json['max_count'],
      window: Duration(seconds: json['window_seconds']),
    );
  }
}

class TimeWindowPolicy {
  final NotificationType type;
  final int startHour;
  final int endHour;

  TimeWindowPolicy({
    required this.type,
    required this.startHour,
    required this.endHour,
  });

  factory TimeWindowPolicy.defaultPolicy() {
    return TimeWindowPolicy(
      type: NotificationType.system,
      startHour: 8,
      endHour: 22,
    );
  }

  factory TimeWindowPolicy.fromJson(Map<String, dynamic> json) {
    return TimeWindowPolicy(
      type: NotificationType.values.byName(json['type']),
      startHour: json['start_hour'],
      endHour: json['end_hour'],
    );
  }
}

class NotificationSettings {
  final List<NotificationType> enabledTypes;
  final NotificationPriority minPriority;
  final int quietStart;
  final int quietEnd;

  NotificationSettings({
    required this.enabledTypes,
    required this.minPriority,
    required this.quietStart,
    required this.quietEnd,
  });

  factory NotificationSettings.defaultSettings() {
    return NotificationSettings(
      enabledTypes: NotificationType.values,
      minPriority: NotificationPriority.normal,
      quietStart: 22,
      quietEnd: 8,
    );
  }

  factory NotificationSettings.fromJson(Map<String, dynamic> json) {
    return NotificationSettings(
      enabledTypes: (json['enabled_types'] as String)
          .split(',')
          .map((t) => NotificationType.values.byName(t))
          .toList(),
      minPriority: NotificationPriority.values.byName(json['min_priority']),
      quietStart: json['quiet_start'],
      quietEnd: json['quiet_end'],
    );
  }
} 