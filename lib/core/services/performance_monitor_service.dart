import 'package:get/get.dart';
import 'dart:async';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class PerformanceMonitorService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final metrics = <String, dynamic>{}.obs;
  final isMonitoring = false.obs;
  final performanceHistory = <Map<String, dynamic>>[].obs;

  Timer? _monitorTimer;
  final _startTimes = <String, DateTime>{};

  @override
  void onInit() {
    super.onInit();
    _initMonitor();
  }

  @override
  void onClose() {
    _stopMonitoring();
    super.onClose();
  }

  Future<void> _initMonitor() async {
    try {
      await _loadPerformanceHistory();
      startMonitoring();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize performance monitor', data: {'error': e.toString()});
    }
  }

  // 开始监控
  void startMonitoring() {
    if (isMonitoring.value) return;

    try {
      isMonitoring.value = true;
      _monitorTimer = Timer.periodic(
        const Duration(seconds: 5),
        (_) => _collectMetrics(),
      );
    } catch (e) {
      _loggingService.log('error', 'Failed to start monitoring', data: {'error': e.toString()});
    }
  }

  // 停止监控
  void _stopMonitoring() {
    _monitorTimer?.cancel();
    isMonitoring.value = false;
  }

  // 开始计时
  void startTimer(String key) {
    _startTimes[key] = DateTime.now();
  }

  // 结束计时
  Future<void> endTimer(String key) async {
    final startTime = _startTimes[key];
    if (startTime == null) return;

    try {
      final duration = DateTime.now().difference(startTime);
      await _recordMetric(key, duration.inMilliseconds);
      _startTimes.remove(key);
    } catch (e) {
      await _loggingService.log('error', 'Failed to end timer', data: {'key': key, 'error': e.toString()});
    }
  }

  // 记录性能指标
  Future<void> recordMetric(String key, dynamic value) async {
    try {
      await _recordMetric(key, value);
    } catch (e) {
      await _loggingService.log('error', 'Failed to record metric', data: {'key': key, 'error': e.toString()});
    }
  }

  Future<void> _collectMetrics() async {
    try {
      final currentMetrics = {
        'memory_usage': await _getMemoryUsage(),
        'cpu_usage': await _getCpuUsage(),
        'frame_rate': await _getFrameRate(),
        'battery_level': await _getBatteryLevel(),
        'network_latency': await _getNetworkLatency(),
        'timestamp': DateTime.now().toIso8601String(),
      };

      metrics.value = currentMetrics;
      await _saveMetrics(currentMetrics);

      // 检查性能问题
      await _checkPerformanceIssues(currentMetrics);
    } catch (e) {
      await _loggingService.log('error', 'Failed to collect metrics', data: {'error': e.toString()});
    }
  }

  Future<void> _recordMetric(String key, dynamic value) async {
    try {
      final metric = {
        'key': key,
        'value': value,
        'timestamp': DateTime.now().toIso8601String(),
      };

      await _saveMetrics(metric);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveMetrics(Map<String, dynamic> metric) async {
    try {
      performanceHistory.insert(0, metric);
      
      // 只保留最近1000条记录
      if (performanceHistory.length > 1000) {
        performanceHistory.removeRange(1000, performanceHistory.length);
      }
      
      await _storageService.saveLocal('performance_history', performanceHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadPerformanceHistory() async {
    try {
      final history = await _storageService.getLocal('performance_history');
      if (history != null) {
        performanceHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _checkPerformanceIssues(Map<String, dynamic> metrics) async {
    try {
      final issues = <String>[];

      // 检查内存使用
      if (metrics['memory_usage'] > 80) {
        issues.add('High memory usage: ${metrics['memory_usage']}%');
      }

      // 检查CPU使用
      if (metrics['cpu_usage'] > 70) {
        issues.add('High CPU usage: ${metrics['cpu_usage']}%');
      }

      // 检查帧率
      if (metrics['frame_rate'] < 30) {
        issues.add('Low frame rate: ${metrics['frame_rate']} FPS');
      }

      // 检查网络延迟
      if (metrics['network_latency'] > 1000) {
        issues.add('High network latency: ${metrics['network_latency']}ms');
      }

      if (issues.isNotEmpty) {
        await _handlePerformanceIssues(issues);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _handlePerformanceIssues(List<String> issues) async {
    try {
      await _loggingService.log(
        'warning',
        'Performance issues detected',
        data: {'issues': issues},
      );
      // TODO: 实现性能问题处理策略
      _handlePerformanceIssues();
    } catch (e) {
      rethrow;
    }
  }

  void _handlePerformanceIssues() {
    print('Handling performance issues...');
    // 示例：根据性能指标采取措施
    // 实际实现中需要根据具体业务逻辑处理性能问题
    if (metrics['cpu_usage'] > 80) {
      print('High CPU usage detected, taking action...');
      // 采取措施降低CPU使用率
    }
  }

  Future<int> _getMemoryUsage() async {
    print('Getting memory usage...');
    // 示例：获取内存使用率
    // 实际实现中需要根据具体平台获取内存使用率
    return 50; // 返回示例值
  }

  Future<int> _getCpuUsage() async {
    print('Getting CPU usage...');
    // 示例：获取CPU使用率
    // 实际实现中需要根据具体平台获取CPU使用率
    return 30; // 返回示例值
  }

  Future<int> _getFrameRate() async {
    print('Getting frame rate...');
    // 示例：获取帧率
    // 实际实现中需要根据具体平台获取帧率
    return 60; // 返回示例值
  }

  Future<int> _getBatteryLevel() async {
    print('Getting battery level...');
    // 示例：获取电池电量
    // 实际实现中需要根据具体平台获取电池电量
    return 80; // 返回示例值
  }

  Future<int> _getNetworkLatency() async {
    print('Getting network latency...');
    // 示例：获取网络延迟
    // 实际实现中需要根据具体平台获取网络延迟
    return 100; // 返回示例值
  }
} 