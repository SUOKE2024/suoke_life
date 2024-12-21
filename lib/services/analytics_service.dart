import 'package:get/get.dart';
import 'package:suoke_life/data/models/life_record.dart';
import 'package:suoke_life/services/life_record_service.dart';
import 'dart:convert';
import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/elasticsearch/es_client.dart';

enum AnalyticsType {
  user,      // 用户分析
  content,   // 内容分析
  behavior,  // 行为分析
  business,  // 业务分析
}

class AnalyticsService extends GetxService {
  final LifeRecordService _recordService = Get.find();
  final KnowledgeDatabase _knowledgeDb;
  final ESClient _esClient;

  AnalyticsService(this._knowledgeDb, this._esClient);

  // 获取记录统计
  Map<String, dynamic> getRecordStats() {
    final records = _recordService.getAllRecords();
    return {
      'total': records.length,
      'hasImage': records.where((r) => r.image != null).length,
      'hasTags': records.where((r) => r.tags.isNotEmpty).length,
      'avgTagsPerRecord': records.isEmpty 
          ? 0.0 
          : records.fold<int>(0, (sum, r) => sum + r.tags.length) / records.length,
    };
  }

  // 获取标签使用频率
  Map<String, int> getTagFrequency() {
    final records = _recordService.getAllRecords();
    final Map<String, int> frequency = {};
    
    for (var record in records) {
      for (var tag in record.tags) {
        frequency[tag] = (frequency[tag] ?? 0) + 1;
      }
    }
    
    return Map.fromEntries(
      frequency.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value))
    );
  }

  // 获取每月记录数量
  Map<String, int> getMonthlyRecordCount() {
    final records = _recordService.getAllRecords();
    final Map<String, int> monthly = {};
    
    for (var record in records) {
      final date = DateTime.parse(record.time);
      final key = '${date.year}-${date.month.toString().padLeft(2, '0')}';
      monthly[key] = (monthly[key] ?? 0) + 1;
    }
    
    return monthly;
  }

  // 获取每日记录时间分布
  Map<int, int> getHourlyDistribution() {
    final records = _recordService.getAllRecords();
    final Map<int, int> hourly = {};
    
    for (var record in records) {
      final date = DateTime.parse(record.time);
      hourly[date.hour] = (hourly[date.hour] ?? 0) + 1;
    }
    
    return hourly;
  }

  // 获取记录内容长度分布
  Map<String, int> getContentLengthDistribution() {
    final records = _recordService.getAllRecords();
    final Map<String, int> distribution = {
      '短(≤50字)': 0,
      '中(51-200字)': 0,
      '长(>200字)': 0,
    };
    
    for (var record in records) {
      final length = record.content.length;
      if (length <= 50) {
        distribution['短(≤50字)'] = (distribution['短(≤50字)'] ?? 0) + 1;
      } else if (length <= 200) {
        distribution['中(51-200字)'] = (distribution['中(51-200字)'] ?? 0) + 1;
      } else {
        distribution['长(>200字)'] = (distribution['长(>200字)'] ?? 0) + 1;
      }
    }
    
    return distribution;
  }

  // 获取记录情感分析统计
  Future<Map<String, double>> getEmotionStats() async {
    final records = _recordService.getAllRecords();
    double positive = 0, neutral = 0, negative = 0;
    
    // TODO: 接入实际的情感分���API
    for (var record in records) {
      // 模拟情感分析结果
      final sentiment = record.content.length % 3;
      switch (sentiment) {
        case 0:
          positive++;
          break;
        case 1:
          neutral++;
          break;
        case 2:
          negative++;
          break;
      }
    }
    
    final total = records.length.toDouble();
    return {
      'positive': positive / total,
      'neutral': neutral / total,
      'negative': negative / total,
    };
  }

  // 获取用户分析数据
  Future<Map<String, dynamic>> getUserAnalytics({
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT 
        COUNT(DISTINCT id) as total_users,
        COUNT(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY) THEN 1 END) as new_users,
        COUNT(CASE WHEN last_active_at >= DATE_SUB(NOW(), INTERVAL 1 DAY) THEN 1 END) as active_users
      FROM users
      WHERE 1=1
      ${startTime != null ? 'AND created_at >= ?' : ''}
      ${endTime != null ? 'AND created_at <= ?' : ''}
    ''', [
      if (startTime != null) startTime.toIso8601String(),
      if (endTime != null) endTime.toIso8601String(),
    ]);

    return results.first.fields;
  }

  // 获取内容分析数据
  Future<Map<String, dynamic>> getContentAnalytics({
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT 
        type,
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
        AVG(view_count) as avg_views,
        AVG(like_count) as avg_likes,
        AVG(comment_count) as avg_comments
      FROM contents
      WHERE 1=1
      ${startTime != null ? 'AND created_at >= ?' : ''}
      ${endTime != null ? 'AND created_at <= ?' : ''}
      GROUP BY type
    ''', [
      if (startTime != null) startTime.toIso8601String(),
      if (endTime != null) endTime.toIso8601String(),
    ]);

    return {
      'by_type': results.map((r) => r.fields).toList(),
    };
  }

  // 获取行为分析数据
  Future<Map<String, dynamic>> getBehaviorAnalytics({
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    // 1. 获取用户行为统计
    final behaviors = await _knowledgeDb._conn.query('''
      SELECT 
        action,
        COUNT(*) as count,
        COUNT(DISTINCT user_id) as unique_users
      FROM user_behaviors
      WHERE 1=1
      ${startTime != null ? 'AND created_at >= ?' : ''}
      ${endTime != null ? 'AND created_at <= ?' : ''}
      GROUP BY action
    ''', [
      if (startTime != null) startTime.toIso8601String(),
      if (endTime != null) endTime.toIso8601String(),
    ]);

    // 2. 获取行为路径分析
    final paths = await _analyzeBehaviorPaths(startTime, endTime);

    return {
      'behaviors': behaviors.map((r) => r.fields).toList(),
      'paths': paths,
    };
  }

  // 获取业务分析数据
  Future<Map<String, dynamic>> getBusinessAnalytics({
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    // 1. 获取订单统计
    final orders = await _knowledgeDb._conn.query('''
      SELECT 
        status,
        COUNT(*) as count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount
      FROM orders
      WHERE 1=1
      ${startTime != null ? 'AND created_at >= ?' : ''}
      ${endTime != null ? 'AND created_at <= ?' : ''}
      GROUP BY status
    ''', [
      if (startTime != null) startTime.toIso8601String(),
      if (endTime != null) endTime.toIso8601String(),
    ]);

    // 2. 获取支付统计
    final payments = await _knowledgeDb._conn.query('''
      SELECT 
        payment_method,
        COUNT(*) as count,
        SUM(amount) as total_amount
      FROM payments
      WHERE status = 'success'
      ${startTime != null ? 'AND created_at >= ?' : ''}
      ${endTime != null ? 'AND created_at <= ?' : ''}
      GROUP BY payment_method
    ''', [
      if (startTime != null) startTime.toIso8601String(),
      if (endTime != null) endTime.toIso8601String(),
    ]);

    return {
      'orders': orders.map((r) => r.fields).toList(),
      'payments': payments.map((r) => r.fields).toList(),
    };
  }

  // 分析行为路径
  Future<List<Map<String, dynamic>>> _analyzeBehaviorPaths(
    DateTime? startTime,
    DateTime? endTime,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      WITH RECURSIVE behavior_path AS (
        SELECT 
          user_id,
          action,
          created_at,
          CAST(action AS CHAR(1000)) as path
        FROM user_behaviors
        WHERE parent_id IS NULL
        
        UNION ALL
        
        SELECT 
          b.user_id,
          b.action,
          b.created_at,
          CONCAT(bp.path, ' -> ', b.action)
        FROM user_behaviors b
        JOIN behavior_path bp ON b.parent_id = bp.id
      )
      SELECT path, COUNT(*) as count
      FROM behavior_path
      WHERE 1=1
      ${startTime != null ? 'AND created_at >= ?' : ''}
      ${endTime != null ? 'AND created_at <= ?' : ''}
      GROUP BY path
      ORDER BY count DESC
      LIMIT 100
    ''', [
      if (startTime != null) startTime.toIso8601String(),
      if (endTime != null) endTime.toIso8601String(),
    ]);

    return results.map((r) => r.fields).toList();
  }

  // 导出分析数据
  Future<String> exportAnalytics(
    AnalyticsType type,
    DateTime startTime,
    DateTime endTime,
  ) async {
    final data = switch (type) {
      AnalyticsType.user => await getUserAnalytics(
          startTime: startTime,
          endTime: endTime,
        ),
      AnalyticsType.content => await getContentAnalytics(
          startTime: startTime,
          endTime: endTime,
        ),
      AnalyticsType.behavior => await getBehaviorAnalytics(
          startTime: startTime,
          endTime: endTime,
        ),
      AnalyticsType.business => await getBusinessAnalytics(
          startTime: startTime,
          endTime: endTime,
        ),
    };

    // TODO: 实现数据导出为CSV或Excel
    return jsonEncode(data);
  }
} 