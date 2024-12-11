import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../core/di/service_locator.dart';
import '../../core/network/http_client.dart';
import '../../models/health/health_data.dart';

class HealthDataService {
  final HttpClient _httpClient;
  final _healthDataController = StreamController<HealthData>.broadcast();
  Timer? _syncTimer;
  
  Stream<HealthData> get healthDataStream => _healthDataController.stream;
  
  HealthDataService({
    required HttpClient httpClient,
  }) : _httpClient = httpClient {
    _initializeSync();
  }
  
  void _initializeSync() {
    // 每30分钟同步一次数据
    _syncTimer = Timer.periodic(
      const Duration(minutes: 30),
      (_) => syncHealthData(),
    );
  }
  
  // 采集健康数据
  Future<void> collectHealthMetric(HealthMetric metric) async {
    try {
      await _httpClient.post(
        '/api/health/metrics',
        data: metric.toJson(),
      );
      
      // 获取最新的健康数据
      final healthData = await fetchHealthData();
      _healthDataController.add(healthData);
    } catch (e) {
      debugPrint('Failed to collect health metric: $e');
      rethrow;
    }
  }
  
  // 批量采集健康数据
  Future<void> collectHealthMetrics(List<HealthMetric> metrics) async {
    try {
      await _httpClient.post(
        '/api/health/metrics/batch',
        data: {
          'metrics': metrics.map((m) => m.toJson()).toList(),
        },
      );
      
      final healthData = await fetchHealthData();
      _healthDataController.add(healthData);
    } catch (e) {
      debugPrint('Failed to collect health metrics: $e');
      rethrow;
    }
  }
  
  // 获取健康数据
  Future<HealthData> fetchHealthData() async {
    try {
      final response = await _httpClient.get('/api/health/data');
      return HealthData.fromJson(response.data);
    } catch (e) {
      debugPrint('Failed to fetch health data: $e');
      rethrow;
    }
  }
  
  // 同步健康数据
  Future<void> syncHealthData() async {
    try {
      final response = await _httpClient.post('/api/health/sync');
      final healthData = HealthData.fromJson(response.data);
      _healthDataController.add(healthData);
    } catch (e) {
      debugPrint('Failed to sync health data: $e');
      rethrow;
    }
  }
  
  // 分析健康趋势
  Future<Map<String, dynamic>> analyzeHealthTrends({
    required DateTime startDate,
    required DateTime endDate,
    required List<HealthMetricType> metricTypes,
  }) async {
    try {
      final response = await _httpClient.post(
        '/api/health/analyze',
        data: {
          'startDate': startDate.toIso8601String(),
          'endDate': endDate.toIso8601String(),
          'metricTypes': metricTypes.map((t) => t.toString().split('.').last).toList(),
        },
      );
      return response.data;
    } catch (e) {
      debugPrint('Failed to analyze health trends: $e');
      rethrow;
    }
  }
  
  // 获取健康建议
  Future<List<String>> getHealthSuggestions() async {
    try {
      final response = await _httpClient.get('/api/health/suggestions');
      return List<String>.from(response.data['suggestions']);
    } catch (e) {
      debugPrint('Failed to get health suggestions: $e');
      rethrow;
    }
  }
  
  // 设置数据同步间隔
  void setSyncInterval(Duration interval) {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(interval, (_) => syncHealthData());
  }
  
  void dispose() {
    _syncTimer?.cancel();
    _healthDataController.close();
  }
} 