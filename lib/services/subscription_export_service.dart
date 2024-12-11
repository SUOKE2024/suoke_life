import 'dart:convert';
import 'dart:io';

import 'package:csv/csv.dart';
import 'package:share_plus/share_plus.dart';
import 'subscription_analytics_service.dart';

class SubscriptionExportService {
  final SubscriptionAnalyticsService _analyticsService;

  SubscriptionExportService(this._analyticsService);

  Future<void> exportToJson() async {
    try {
      final analytics = await _analyticsService.analyticsStream.first;
      final data = {
        'timestamp': DateTime.now().toIso8601String(),
        'totalSubscriptions': analytics.totalSubscriptions,
        'activeSubscriptions': analytics.activeSubscriptions,
        'monthlySubscriptions': analytics.monthlySubscriptions,
        'yearlySubscriptions': analytics.yearlySubscriptions,
        'conversionRate': analytics.conversionRate,
        'planDistribution': analytics.planDistribution,
        'revenueByPlan': analytics.revenueByPlan,
        'recentEvents': analytics.recentEvents.map((e) => e.toJson()).toList(),
      };

      final jsonString = const JsonEncoder.withIndent('  ').convert(data);
      final file = await _getExportFile('subscription_analytics.json');
      await file.writeAsString(jsonString);
      await _shareFile(file);
    } catch (e) {
      print('导出JSON失败: $e');
      rethrow;
    }
  }

  Future<void> exportToCsv() async {
    try {
      final analytics = await _analyticsService.analyticsStream.first;
      
      // 准备CSV数据
      final List<List<dynamic>> csvData = [
        // 头部
        ['指标', '数值', '时间'],
        
        // 基本指标
        ['总订阅数', analytics.totalSubscriptions, DateTime.now().toIso8601String()],
        ['活跃订阅', analytics.activeSubscriptions, DateTime.now().toIso8601String()],
        ['月度订阅', analytics.monthlySubscriptions, DateTime.now().toIso8601String()],
        ['年度订阅', analytics.yearlySubscriptions, DateTime.now().toIso8601String()],
        ['转化率', analytics.conversionRate, DateTime.now().toIso8601String()],
        
        // 空行
        [],
        
        // 计划分布
        ['计划', '订阅数'],
        ...analytics.planDistribution.entries.map(
          (e) => [e.key, e.value],
        ),
        
        // 空行
        [],
        
        // 收入分布
        ['计划', '收入'],
        ...analytics.revenueByPlan.entries.map(
          (e) => [e.key, e.value],
        ),
        
        // 空行
        [],
        
        // 最近事件
        ['事件类型', '计划', '时间', '详情'],
        ...analytics.recentEvents.map((e) => [
          e.type,
          e.planId,
          e.timestamp.toIso8601String(),
          e.metadata != null ? json.encode(e.metadata) : '',
        ]),
      ];

      final csvString = const ListToCsvConverter().convert(csvData);
      final file = await _getExportFile('subscription_analytics.csv');
      await file.writeAsString(csvString);
      await _shareFile(file);
    } catch (e) {
      print('导出CSV失败: $e');
      rethrow;
    }
  }

  Future<void> exportToExcel() async {
    try {
      final analytics = await _analyticsService.analyticsStream.first;
      
      // TODO: 实现Excel导出
      // 需要添加excel包依赖并实现相关逻辑
    } catch (e) {
      print('导出Excel失败: $e');
      rethrow;
    }
  }

  Future<File> _getExportFile(String filename) async {
    final directory = await getApplicationDocumentsDirectory();
    return File('${directory.path}/$filename');
  }

  Future<void> _shareFile(File file) async {
    try {
      await Share.shareXFiles(
        [XFile(file.path)],
        subject: '订阅分析数据',
        text: '订阅分析数据导出 - ${DateTime.now().toIso8601String()}',
      );
    } catch (e) {
      print('分享文件失败: $e');
      rethrow;
    }
  }
} 