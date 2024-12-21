import 'package:get/get.dart';
import 'package:device_info_plus/device_info_plus.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class DeviceHealthService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final _deviceInfo = DeviceInfoPlugin();

  final deviceHealth = <String, dynamic>{}.obs;
  final healthHistory = <Map<String, dynamic>>[].obs;
  final isMonitoring = false.obs;

  @override
  void onInit() {
    super.onInit();
    _initDeviceHealth();
  }

  Future<void> _initDeviceHealth() async {
    try {
      await _loadDeviceInfo();
      await _startMonitoring();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize device health', data: {'error': e.toString()});
    }
  }

  // 开始监控
  Future<void> startMonitoring() async {
    if (isMonitoring.value) return;

    try {
      isMonitoring.value = true;
      await _startHealthCheck();
    } catch (e) {
      isMonitoring.value = false;
      await _loggingService.log('error', 'Failed to start monitoring', data: {'error': e.toString()});
    }
  }

  // 停止监控
  Future<void> stopMonitoring() async {
    if (!isMonitoring.value) return;

    try {
      isMonitoring.value = false;
      await _stopHealthCheck();
    } catch (e) {
      await _loggingService.log('error', 'Failed to stop monitoring', data: {'error': e.toString()});
    }
  }

  // 获取设备健康报告
  Future<Map<String, dynamic>> getHealthReport() async {
    try {
      final report = {
        'device_info': await _getDeviceInfo(),
        'health_metrics': await _getHealthMetrics(),
        'performance_metrics': await _getPerformanceMetrics(),
        'issues': await _detectIssues(),
        'recommendations': await _generateRecommendations(),
        'timestamp': DateTime.now().toIso8601String(),
      };

      await _saveHealthReport(report);
      return report;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get health report', data: {'error': e.toString()});
      return {};
    }
  }

  Future<void> _loadDeviceInfo() async {
    try {
      if (GetPlatform.isAndroid) {
        deviceHealth['device_info'] = await _deviceInfo.androidInfo;
      } else if (GetPlatform.isIOS) {
        deviceHealth['device_info'] = await _deviceInfo.iosInfo;
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _startHealthCheck() async {
    try {
      // 定期检查设备健康状态
      Timer.periodic(const Duration(minutes: 15), (timer) async {
        if (!isMonitoring.value) {
          timer.cancel();
          return;
        }

        await _checkDeviceHealth();
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _stopHealthCheck() async {
    try {
      // 保存最后的健康状态
      await _saveHealthReport(deviceHealth.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _checkDeviceHealth() async {
    try {
      deviceHealth.value = {
        ...deviceHealth,
        'health_metrics': await _getHealthMetrics(),
        'performance_metrics': await _getPerformanceMetrics(),
        'updated_at': DateTime.now().toIso8601String(),
      };

      // 检查是否有问题
      final issues = await _detectIssues();
      if (issues.isNotEmpty) {
        await _handleHealthIssues(issues);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _getDeviceInfo() async {
    try {
      // TODO: 实现设备信息获取
      return {};
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _getHealthMetrics() async {
    try {
      // TODO: 实现健康指标获取
      return {};
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _getPerformanceMetrics() async {
    try {
      // TODO: 实现性能指标获取
      return {};
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _detectIssues() async {
    try {
      // TODO: 实现问题检测
      return [];
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _generateRecommendations() async {
    try {
      // TODO: 实现建议生成
      return [];
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _handleHealthIssues(List<Map<String, dynamic>> issues) async {
    try {
      for (final issue in issues) {
        await _loggingService.log('warning', 'Device health issue detected', data: issue);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveHealthReport(Map<String, dynamic> report) async {
    try {
      healthHistory.insert(0, report);

      // 只保留最近100条记录
      if (healthHistory.length > 100) {
        healthHistory.removeRange(100, healthHistory.length);
      }

      await _storageService.saveLocal('device_health_history', healthHistory);
    } catch (e) {
      rethrow;
    }
  }
} 