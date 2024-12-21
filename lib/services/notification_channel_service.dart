import '../data/remote/mysql/knowledge_database.dart';

enum ChannelType {
  app,        // 应用内通知
  push,       // 推送通知
  sms,        // 短信通知
  email,      // 邮件通知
  wechat,     // 微信通知
}

enum ChannelStatus {
  enabled,    // 启用
  disabled,   // 禁用
  limited,    // 受限
}

class NotificationChannelService {
  final KnowledgeDatabase _knowledgeDb;

  NotificationChannelService(this._knowledgeDb);

  // 获取可用渠道
  Future<List<Channel>> getAvailableChannels(
    String userId,
    NotificationType type,
    NotificationPriority priority,
  ) async {
    // 1. 获取所有渠道
    final channels = await _getChannels(type);

    // 2. 过滤不可用渠道
    final available = <Channel>[];
    for (final channel in channels) {
      if (await _isChannelAvailable(channel, userId, type, priority)) {
        available.add(channel);
      }
    }

    // 3. 按优先级排序
    available.sort((a, b) => b.priority.compareTo(a.priority));
    return available;
  }

  // 检查渠道可用性
  Future<bool> _isChannelAvailable(
    Channel channel,
    String userId,
    NotificationType type,
    NotificationPriority priority,
  ) async {
    // 1. 检查渠道状态
    if (channel.status != ChannelStatus.enabled) {
      return false;
    }

    // 2. 检查用户设置
    final settings = await _getUserChannelSettings(userId);
    if (!settings.enabledChannels.contains(channel.type)) {
      return false;
    }

    // 3. 检查通知类型
    if (!channel.supportedTypes.contains(type)) {
      return false;
    }

    // 4. 检查优先级
    if (NotificationPriority.values.indexOf(priority) < 
        NotificationPriority.values.indexOf(channel.minPriority)) {
      return false;
    }

    return true;
  }

  // 获取渠道列表
  Future<List<Channel>> _getChannels(NotificationType type) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT c.*, 
        (SELECT GROUP_CONCAT(type) FROM channel_supported_types 
         WHERE channel_id = c.id) as supported_types
      FROM notification_channels c
      WHERE c.status = ?
    ''', [ChannelStatus.enabled.toString()]);

    return results.map((r) => Channel.fromJson(r.fields)).toList();
  }

  // 获取用户渠道设置
  Future<ChannelSettings> _getUserChannelSettings(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM user_channel_settings
      WHERE user_id = ?
    ''', [userId]);

    if (results.isEmpty) {
      return ChannelSettings.defaultSettings();
    }

    return ChannelSettings.fromJson(results.first.fields);
  }

  // 更新用户渠道设置
  Future<void> updateUserChannelSettings(
    String userId,
    ChannelSettings settings,
  ) async {
    await _knowledgeDb._conn.query('''
      INSERT INTO user_channel_settings (
        user_id, enabled_channels, updated_at
      ) VALUES (?, ?, NOW())
      ON DUPLICATE KEY UPDATE
        enabled_channels = VALUES(enabled_channels),
        updated_at = NOW()
    ''', [
      userId,
      settings.enabledChannels.map((c) => c.toString()).join(','),
    ]);
  }

  // 更新渠道状态
  Future<void> updateChannelStatus(
    String channelId,
    ChannelStatus status,
  ) async {
    await _knowledgeDb._conn.query('''
      UPDATE notification_channels
      SET status = ?, updated_at = NOW()
      WHERE id = ?
    ''', [status.toString(), channelId]);
  }
}

class Channel {
  final String id;
  final ChannelType type;
  final String name;
  final String description;
  final ChannelStatus status;
  final int priority;
  final NotificationPriority minPriority;
  final List<NotificationType> supportedTypes;
  final Map<String, dynamic>? config;

  Channel({
    required this.id,
    required this.type,
    required this.name,
    required this.description,
    required this.status,
    required this.priority,
    required this.minPriority,
    required this.supportedTypes,
    this.config,
  });

  factory Channel.fromJson(Map<String, dynamic> json) {
    return Channel(
      id: json['id'],
      type: ChannelType.values.byName(json['type']),
      name: json['name'],
      description: json['description'],
      status: ChannelStatus.values.byName(json['status']),
      priority: json['priority'],
      minPriority: NotificationPriority.values.byName(json['min_priority']),
      supportedTypes: (json['supported_types'] as String)
          .split(',')
          .map((t) => NotificationType.values.byName(t))
          .toList(),
      config: json['config'] != null ? jsonDecode(json['config']) : null,
    );
  }
}

class ChannelSettings {
  final List<ChannelType> enabledChannels;

  ChannelSettings({
    required this.enabledChannels,
  });

  factory ChannelSettings.defaultSettings() {
    return ChannelSettings(
      enabledChannels: [
        ChannelType.app,
        ChannelType.push,
      ],
    );
  }

  factory ChannelSettings.fromJson(Map<String, dynamic> json) {
    return ChannelSettings(
      enabledChannels: (json['enabled_channels'] as String)
          .split(',')
          .map((c) => ChannelType.values.byName(c))
          .toList(),
    );
  }
} 