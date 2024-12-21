import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/redis/redis_cache.dart';
import 'package:prometheus_client/prometheus_client.dart';
import 'dart:async';
import 'dart:convert';

enum MonitoringMetric {
  sendTotal,         // 发送总数
  deliveryTotal,     // 投递总数
  readTotal,         // 阅读总数
  sendLatency,       // 发送延迟
  deliveryLatency,   // 投递延迟
  readLatency,       // 阅读延迟
  errorTotal,        // 错误总数
  channelStatus,     // 渠道状态
}

enum ChannelType {
  push,      // 推送通知
  sms,       // 短信通知
  email,     // 邮件通知
  inApp,     // 应用内通知
  webhook,   // Webhook通知
}

enum NotificationType {
  alert,     // 警报通知
  info,      // 信息通知
  reminder,  // 提醒通知
  marketing, // 营销通知
  system,    // 系统通知
}

enum AlertSeverity {
  critical,  // 严重告警
  warning,   // 警告告警
  info,      // 信息告警
}

class MonitoringConfig {
  final Duration healthCheckInterval;
  final double errorRateThreshold;
  final double deliveryRateThreshold;
  final Duration latencyThreshold;
  final Map<String, List<double>> histogramBuckets;

  const MonitoringConfig({
    this.healthCheckInterval = const Duration(minutes: 1),
    this.errorRateThreshold = 0.1,
    this.deliveryRateThreshold = 0.9,
    this.latencyThreshold = const Duration(seconds: 5),
    this.histogramBuckets = const {
      'send': [0.1, 0.5, 1, 2, 5, 10],
      'delivery': [0.1, 0.5, 1, 2, 5, 10],
      'read': [1, 5, 15, 30, 60, 300],
    },
  });
}

class NotificationMonitoringService {
  final KnowledgeDatabase _knowledgeDb;
  final RedisCache _redisCache;
  final CollectorRegistry _registry;
  final Map<MonitoringMetric, Collector> _metrics;
  final MonitoringConfig _config;
  Timer? _healthCheckTimer;

  NotificationMonitoringService(
    this._knowledgeDb,
    this._redisCache, {
    MonitoringConfig? config,
  }) : _registry = CollectorRegistry(),
      _metrics = {},
      _config = config ?? const MonitoringConfig() {
    _initMetrics();
    _startHealthCheck();
  }

  // 初始化监控指标
  void _initMetrics() {
    // 计数器
    _metrics[MonitoringMetric.sendTotal] = Counter(
      name: 'notification_send_total',
      help: 'Total number of notifications sent',
      labelNames: ['type', 'channel'],
    )..register(_registry);

    _metrics[MonitoringMetric.deliveryTotal] = Counter(
      name: 'notification_delivery_total',
      help: 'Total number of notifications delivered',
      labelNames: ['type', 'channel', 'status'],
    )..register(_registry);

    _metrics[MonitoringMetric.readTotal] = Counter(
      name: 'notification_read_total',
      help: 'Total number of notifications read',
      labelNames: ['type'],
    )..register(_registry);

    _metrics[MonitoringMetric.errorTotal] = Counter(
      name: 'notification_error_total',
      help: 'Total number of notification errors',
      labelNames: ['type', 'channel', 'error_type'],
    )..register(_registry);

    // 直方图
    _metrics[MonitoringMetric.sendLatency] = Histogram(
      name: 'notification_send_latency_seconds',
      help: 'Notification send latency in seconds',
      labelNames: ['type', 'channel'],
      buckets: _config.histogramBuckets['send']!,
    )..register(_registry);

    _metrics[MonitoringMetric.deliveryLatency] = Histogram(
      name: 'notification_delivery_latency_seconds',
      help: 'Notification delivery latency in seconds',
      labelNames: ['type', 'channel'],
      buckets: _config.histogramBuckets['delivery']!,
    )..register(_registry);

    _metrics[MonitoringMetric.readLatency] = Histogram(
      name: 'notification_read_latency_seconds',
      help: 'Notification read latency in seconds',
      labelNames: ['type'],
      buckets: _config.histogramBuckets['read']!,
    )..register(_registry);

    // 仪表
    _metrics[MonitoringMetric.channelStatus] = Gauge(
      name: 'notification_channel_status',
      help: 'Notification channel status (1=up, 0=down)',
      labelNames: ['channel'],
    )..register(_registry);
  }

  // 记录发送指标
  void recordSend(String notificationId, NotificationType type, ChannelType channel) {
    try {
      (_metrics[MonitoringMetric.sendTotal] as Counter).inc(
        labels: {'type': type.toString(), 'channel': channel.toString()},
      );
    } catch (e) {
      print('Error recording send metric: $e');
    }
  }

  // 记录投递指标
  void recordDelivery(
    String notificationId,
    NotificationType type,
    ChannelType channel,
    bool success,
    String? error,
  ) {
    try {
      final status = success ? 'success' : 'failure';
      (_metrics[MonitoringMetric.deliveryTotal] as Counter).inc(
        labels: {
          'type': type.toString(),
          'channel': channel.toString(),
          'status': status,
        },
      );

      if (!success && error != null) {
        (_metrics[MonitoringMetric.errorTotal] as Counter).inc(
          labels: {
            'type': type.toString(),
            'channel': channel.toString(),
            'error_type': _categorizeError(error),
          },
        );
      }
    } catch (e) {
      print('Error recording delivery metric: $e');
    }
  }

  // 记录阅读指标
  void recordRead(
    String notificationId,
    NotificationType type,
    Duration readLatency,
  ) {
    try {
      (_metrics[MonitoringMetric.readTotal] as Counter).inc(
        labels: {'type': type.toString()},
      );

      (_metrics[MonitoringMetric.readLatency] as Histogram).observe(
        readLatency.inSeconds.toDouble(),
        labels: {'type': type.toString()},
      );
    } catch (e) {
      print('Error recording read metric: $e');
    }
  }

  // 开始健康检查
  void _startHealthCheck() {
    _healthCheckTimer?.cancel();
    _healthCheckTimer = Timer.periodic(_config.healthCheckInterval, (_) {
      _checkChannelHealth();
    });
  }

  // 检查渠道健康状态
  Future<void> _checkChannelHealth() async {
    for (final channel in ChannelType.values) {
      try {
        final isHealthy = await _checkChannelStatus(channel);
        (_metrics[MonitoringMetric.channelStatus] as Gauge).set(
          isHealthy ? 1.0 : 0.0,
          labels: {'channel': channel.toString()},
        );

        if (!isHealthy) {
          await _alertChannelUnhealthy(channel);
        }
      } catch (e) {
        print('Error checking channel health: $e');
      }
    }
  }

  // 检查单个渠道状态
  Future<bool> _checkChannelStatus(ChannelType channel) async {
    try {
      // 1. 检查最近的投递成功率
      final stats = await _getChannelStats(channel);
      if (stats.deliveryRate < _config.deliveryRateThreshold) {
        return false;
      }

      // 2. 检查错误率
      if (stats.errorRate > _config.errorRateThreshold) {
        return false;
      }

      // 3. 检查平均延迟
      if (stats.avgLatency > _config.latencyThreshold) {
        return false;
      }

      return true;
    } catch (e) {
      print('Error in channel health check: $e');
      return false;
    }
  }

  // 获取渠道统计
  Future<ChannelStats> _getChannelStats(ChannelType channel) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered,
        COUNT(CASE WHEN error IS NOT NULL THEN 1 END) as errors,
        AVG(TIMESTAMPDIFF(SECOND, created_at, delivered_at)) as avg_latency
      FROM notifications
      WHERE channel = ?
      AND created_at >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
    ''', [channel.toString()]);

    final row = results.first.fields;
    final total = row['total'] as int;
    
    return ChannelStats(
      deliveryRate: total > 0 ? (row['delivered'] as int) / total : 1.0,
      errorRate: total > 0 ? (row['errors'] as int) / total : 0.0,
      avgLatency: Duration(seconds: (row['avg_latency'] as num?)?.toInt() ?? 0),
    );
  }

  // 分类错误类型
  String _categorizeError(String error) {
    if (error.contains('timeout')) return 'timeout';
    if (error.contains('connection')) return 'connection';
    if (error.contains('auth')) return 'authentication';
    return 'other';
  }

  // 发送渠道异常告警
  Future<void> _alertChannelUnhealthy(ChannelType channel) async {
    final stats = await _getChannelStats(channel);
    
    // 根据指标确定告警级别
    final severity = _determineAlertSeverity(stats);
    
    final alert = Alert(
      type: 'channel_unhealthy',
      severity: severity,
      channel: channel.toString(),
      timestamp: DateTime.now(),
      details: {
        'delivery_rate': stats.deliveryRate,
        'error_rate': stats.errorRate,
        'avg_latency': stats.avgLatency.inSeconds,
        'thresholds': {
          'delivery_rate': _config.deliveryRateThreshold,
          'error_rate': _config.errorRateThreshold,
          'latency': _config.latencyThreshold.inSeconds,
        },
      },
    );

    // 1. 记录告警
    await _knowledgeDb._conn.query('''
      INSERT INTO notification_alerts (
        type, severity, channel, details, created_at
      ) VALUES (?, ?, ?, ?, NOW())
    ''', [
      alert.type,
      alert.severity.toString(),
      alert.channel,
      jsonEncode(alert.details),
    ]);

    // 2. 发送告警通知
    await _sendAlertNotification(alert);

    // 3. 更新监控指标
    (_metrics[MonitoringMetric.channelStatus] as Gauge).set(
      0.0,
      labels: {'channel': alert.channel},
    );
  }

  // 确定告警级别
  AlertSeverity _determineAlertSeverity(ChannelStats stats) {
    if (stats.deliveryRate < _config.deliveryRateThreshold * 0.5 ||
        stats.errorRate > _config.errorRateThreshold * 2 ||
        stats.avgLatency > _config.latencyThreshold * 2) {
      return AlertSeverity.critical;
    }
    
    if (stats.deliveryRate < _config.deliveryRateThreshold ||
        stats.errorRate > _config.errorRateThreshold ||
        stats.avgLatency > _config.latencyThreshold) {
      return AlertSeverity.warning;
    }
    
    return AlertSeverity.info;
  }

  // 发送告警通知
  Future<void> _sendAlertNotification(Map<String, dynamic> alert) async {
    // TODO: 实现告警通知逻辑
    // 1. 发送邮件
    // 2. 发送短信
    // 3. 发送Webhook
  }

  // 停止监控
  void dispose() {
    _healthCheckTimer?.cancel();
  }
}

class ChannelStats {
  final double deliveryRate;
  final double errorRate;
  final Duration avgLatency;

  ChannelStats({
    required this.deliveryRate,
    required this.errorRate,
    required this.avgLatency,
  });
}

class Alert {
  final String type;
  final AlertSeverity severity;
  final String channel;
  final DateTime timestamp;
  final Map<String, dynamic> details;

  Alert({
    required this.type,
    required this.severity,
    required this.channel,
    required this.timestamp,
    required this.details,
  });

  Map<String, dynamic> toJson() => {
    'type': type,
    'severity': severity.toString(),
    'channel': channel,
    'timestamp': timestamp.toIso8601String(),
    'details': details,
  };
} 