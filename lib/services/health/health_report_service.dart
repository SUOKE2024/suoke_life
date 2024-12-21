import 'package:intl/intl.dart';
import 'health_analysis_service.dart';

class HealthReportService {
  final HealthAnalysisService _analysisService;
  
  HealthReportService(this._analysisService);

  Future<Map<String, dynamic>> generateDailyReport(DateTime date) async {
    final analysis = await _analysisService.analyzeHealthData(date);
    
    return {
      'type': 'daily',
      'date': DateFormat('yyyy-MM-dd').format(date),
      'summary': _generateSummary(analysis),
      'details': analysis,
      'recommendations': _generateRecommendations(analysis),
      'trends': await _analyzeTrends(date),
    };
  }

  Future<Map<String, dynamic>> generateWeeklyReport(DateTime startDate) async {
    final reports = <Map<String, dynamic>>[];
    var currentDate = startDate;

    for (int i = 0; i < 7; i++) {
      final analysis = await _analysisService.analyzeHealthData(currentDate);
      reports.add(analysis);
      currentDate = currentDate.add(const Duration(days: 1));
    }

    return {
      'type': 'weekly',
      'startDate': DateFormat('yyyy-MM-dd').format(startDate),
      'endDate': DateFormat('yyyy-MM-dd').format(currentDate.subtract(const Duration(days: 1))),
      'summary': _generateWeeklySummary(reports),
      'dailyReports': reports,
      'trends': _analyzeWeeklyTrends(reports),
      'recommendations': _generateWeeklyRecommendations(reports),
    };
  }

  String _generateSummary(Map<String, dynamic> analysis) {
    final metrics = analysis['metrics'];
    final warnings = analysis['warnings'];
    
    String summary = '今日健康状况总结:\n';

    // 添加主要指标
    if (metrics['steps'] != null) {
      summary += '步数: ${metrics['steps']['value']} 步 (${metrics['steps']['status']})\n';
    }
    
    if (metrics['sleep'] != null) {
      final sleepHours = metrics['sleep']['duration'] / 60;
      summary += '睡眠: ${sleepHours.toStringAsFixed(1)} 小时 (${metrics['sleep']['status']})\n';
    }

    // 添加警告
    if (warnings.isNotEmpty) {
      summary += '\n需要注意:\n';
      for (var warning in warnings) {
        summary += '- $warning\n';
      }
    }

    return summary;
  }

  List<String> _generateRecommendations(Map<String, dynamic> analysis) {
    final recommendations = <String>[];
    final metrics = analysis['metrics'];

    // 基于各项指标生成建议
    if (metrics['steps']?['status'] == 'poor') {
      recommendations.add('增加日常活动量:\n'
          '- 步行上下班\n'
          '- 午休时散步\n'
          '- 使用站立办公桌');
    }

    if (metrics['sleep']?['status'] == 'insufficient') {
      recommendations.add('改善睡眠质量:\n'
          '- 固定作息时间\n'
          '- 睡前避免使用电子设备\n'
          '- 保持安静的睡眠环境');
    }

    return recommendations;
  }

  Future<Map<String, dynamic>> _analyzeTrends(DateTime date) async {
    // 分析最近一周的趋势
    final weekStart = date.subtract(const Duration(days: 6));
    final weeklyReport = await generateWeeklyReport(weekStart);
    
    return {
      'steps': _calculateTrend(weeklyReport['dailyReports'], 'steps'),
      'sleep': _calculateTrend(weeklyReport['dailyReports'], 'sleep'),
    };
  }

  String _calculateTrend(List<Map<String, dynamic>> reports, String metric) {
    // 简单趋势分析
    final values = reports
        .map((r) => r['metrics'][metric]?['value'] ?? 0)
        .toList();
    
    if (values.length < 2) return 'stable';
    
    final first = values.first;
    final last = values.last;
    
    final change = ((last - first) / first * 100).abs();
    
    if (change < 5) return 'stable';
    if (last > first) return 'increasing';
    return 'decreasing';
  }
} 