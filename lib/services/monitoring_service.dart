import 'dart:async';
import '../data/remote/mysql/knowledge_database.dart';
import 'message_queue_service.dart';

enum AlertLevel {
  info,
  warning,
  error,
  critical,
}

class MonitoringService {
  final KnowledgeDatabase _knowledgeDb;
  final MessageQueueService _messageQueue;
  final Map<String, StreamController<AlertEvent>> _alertStreams = {};
  final Map<String, Timer> _healthChecks = {};

  MonitoringService(this._knowledgeDb, this._messageQueue);

  // 注册监控指标
  Future<void> registerMetric(
    String metricName,
    Duration checkInterval,
    Future<double> Function() collector,
    double threshold,
    AlertLevel alertLevel,
  ) async {
    // 创建告警流
    _alertStreams[metricName] = StreamController<AlertEvent>.broadcast();

    // 设置定时健康检查
    _healthChecks[metricName] = Timer.periodic(checkInterval, (_) async {
      try {
        final value = await collector();
        await _processMetric(metricName, value, threshold, alertLevel);
      } catch (e) {
        print('监控指标收集失败: $e');
      }
    });
  }

  // 处理监控指标
  Future<void> _processMetric(
    String metricName,
    double value,
    double threshold,
    AlertLevel alertLevel,
  ) async {
    // 记录指标
    await _knowledgeDb._conn.query('''
      INSERT INTO monitoring_metrics (
        metric_name, value, timestamp
      ) VALUES (?, ?, NOW())
    ''', [metricName, value]);

    // 检查阈值并触发告警
    if (value > threshold) {
      final alert = AlertEvent(
        metricName: metricName,
        value: value,
        threshold: threshold,
        level: alertLevel,
        timestamp: DateTime.now(),
      );

      // 发送告警
      _alertStreams[metricName]?.add(alert);
      await _sendAlert(alert);
    }
  }

  // 发送告警
  Future<void> _sendAlert(AlertEvent alert) async {
    // 1. 保存告警记录
    await _knowledgeDb._conn.query('''
      INSERT INTO alert_history (
        metric_name, alert_level, value, threshold, created_at
      ) VALUES (?, ?, ?, ?, NOW())
    ''', [
      alert.metricName,
      alert.level.toString(),
      alert.value,
      alert.threshold,
    ]);

    // 2. 发送告警消息
    await _messageQueue.enqueue(
      'alerts',
      {
        'type': 'alert',
        'metric_name': alert.metricName,
        'level': alert.level.toString(),
        'value': alert.value,
        'threshold': alert.threshold,
        'timestamp': alert.timestamp.toIso8601String(),
      },
      priority: MessagePriority.high,
    );
  }

  // 获取监控指标历史
  Future<List<Map<String, dynamic>>> getMetricHistory(
    String metricName,
    Duration timeRange,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM monitoring_metrics 
      WHERE metric_name = ? 
        AND timestamp >= NOW() - INTERVAL ? SECOND
      ORDER BY timestamp DESC
    ''', [
      metricName,
      timeRange.inSeconds,
    ]);

    return results.map((r) => r.fields).toList();
  }

  // 清理资源
  void dispose() {
    for (var timer in _healthChecks.values) {
      timer.cancel();
    }
    for (var controller in _alertStreams.values) {
      controller.close();
    }
  }
}

class AlertEvent {
  final String metricName;
  final double value;
  final double threshold;
  final AlertLevel level;
  final DateTime timestamp;

  AlertEvent({
    required this.metricName,
    required this.value,
    required this.threshold,
    required this.level,
    required this.timestamp,
  });
} 