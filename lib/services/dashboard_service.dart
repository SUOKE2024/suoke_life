import '../data/remote/mysql/knowledge_database.dart';
import 'monitoring_service.dart';

class DashboardService {
  final KnowledgeDatabase _knowledgeDb;
  final MonitoringService _monitoringService;

  DashboardService(this._knowledgeDb, this._monitoringService);

  // 获取仪表盘配置
  Future<List<DashboardPanel>> getDashboardConfig(String dashboardId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM dashboard_panels 
      WHERE dashboard_id = ?
      ORDER BY panel_order
    ''', [dashboardId]);

    return results.map((r) => DashboardPanel.fromJson(r.fields)).toList();
  }

  // 获取面板数据
  Future<Map<String, dynamic>> getPanelData(
    DashboardPanel panel,
    Duration timeRange,
  ) async {
    switch (panel.type) {
      case PanelType.metric:
        return await _getMetricData(panel, timeRange);
      case PanelType.alert:
        return await _getAlertData(panel, timeRange);
      case PanelType.chart:
        return await _getChartData(panel, timeRange);
      default:
        throw Exception('不支持的面板类型: ${panel.type}');
    }
  }

  // 获取��标数据
  Future<Map<String, dynamic>> _getMetricData(
    DashboardPanel panel,
    Duration timeRange,
  ) async {
    final metrics = await _monitoringService.getMetricHistory(
      panel.metricName!,
      timeRange,
    );

    // 计算统计数据
    final values = metrics.map((m) => m['value'] as double).toList();
    return {
      'current': values.isEmpty ? 0.0 : values.first,
      'average': values.isEmpty ? 0.0 : values.reduce((a, b) => a + b) / values.length,
      'max': values.isEmpty ? 0.0 : values.reduce((a, b) => a > b ? a : b),
      'min': values.isEmpty ? 0.0 : values.reduce((a, b) => a < b ? a : b),
    };
  }

  // 获取告警数据
  Future<Map<String, dynamic>> _getAlertData(
    DashboardPanel panel,
    Duration timeRange,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT alert_level, COUNT(*) as count
      FROM alert_history
      WHERE created_at >= NOW() - INTERVAL ? SECOND
      GROUP BY alert_level
    ''', [timeRange.inSeconds]);

    final alertCounts = <String, int>{};
    for (final row in results) {
      alertCounts[row['alert_level']] = row['count'] as int;
    }

    return {
      'counts': alertCounts,
      'total': alertCounts.values.fold(0, (sum, count) => sum + count),
    };
  }

  // 获取图表数据
  Future<Map<String, dynamic>> _getChartData(
    DashboardPanel panel,
    Duration timeRange,
  ) async {
    final metrics = await _monitoringService.getMetricHistory(
      panel.metricName!,
      timeRange,
    );

    // 按时间间隔聚合数据
    final interval = _calculateInterval(timeRange);
    final aggregatedData = _aggregateData(metrics, interval);

    return {
      'data': aggregatedData,
      'interval': interval.inSeconds,
    };
  }

  // 计算合适的时间间隔
  Duration _calculateInterval(Duration timeRange) {
    if (timeRange.inHours <= 1) return Duration(minutes: 1);
    if (timeRange.inHours <= 6) return Duration(minutes: 5);
    if (timeRange.inHours <= 24) return Duration(minutes: 15);
    if (timeRange.inDays <= 7) return Duration(hours: 1);
    return Duration(hours: 6);
  }

  // 聚合数据
  List<Map<String, dynamic>> _aggregateData(
    List<Map<String, dynamic>> metrics,
    Duration interval,
  ) {
    // TODO: 实现数据聚合逻辑
    return [];
  }
}

enum PanelType {
  metric,  // 单一指标
  alert,   // 告警统计
  chart,   // 图表
}

class DashboardPanel {
  final String id;
  final PanelType type;
  final String title;
  final int order;
  final String? metricName;
  final Map<String, dynamic> config;

  DashboardPanel({
    required this.id,
    required this.type,
    required this.title,
    required this.order,
    this.metricName,
    required this.config,
  });

  factory DashboardPanel.fromJson(Map<String, dynamic> json) {
    return DashboardPanel(
      id: json['id'],
      type: PanelType.values.byName(json['type']),
      title: json['title'],
      order: json['panel_order'],
      metricName: json['metric_name'],
      config: jsonDecode(json['config']),
    );
  }
} 