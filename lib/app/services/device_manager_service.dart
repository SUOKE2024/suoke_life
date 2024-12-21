import 'package:get/get.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class DeviceManagerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final _deviceInfo = DeviceInfoPlugin();

  final deviceInfo = Rx<BaseDeviceInfo?>(null);
  final packageInfo = Rx<PackageInfo?>(null);
  final deviceStatus = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initDeviceManager();
  }

  Future<void> _initDeviceManager() async {
    try {
      await _loadDeviceInfo();
      await _loadPackageInfo();
      await _checkDeviceStatus();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize device manager', data: {'error': e.toString()});
    }
  }

  // 获取设备信息
  Future<Map<String, dynamic>> getDeviceInfo() async {
    try {
      if (deviceInfo.value == null) {
        await _loadDeviceInfo();
      }
      return deviceInfo.value?.data ?? {};
    } catch (e) {
      await _loggingService.log('error', 'Failed to get device info', data: {'error': e.toString()});
      return {};
    }
  }

  // 获取应用信息
  Future<Map<String, String>> getAppInfo() async {
    try {
      if (packageInfo.value == null) {
        await _loadPackageInfo();
      }
      return {
        'appName': packageInfo.value?.appName ?? '',
        'packageName': packageInfo.value?.packageName ?? '',
        'version': packageInfo.value?.version ?? '',
        'buildNumber': packageInfo.value?.buildNumber ?? '',
      };
    } catch (e) {
      await _loggingService.log('error', 'Failed to get app info', data: {'error': e.toString()});
      return {};
    }
  }

  // 检查设备兼容性
  Future<bool> checkDeviceCompatibility() async {
    try {
      final info = await getDeviceInfo();
      final requirements = await _getDeviceRequirements();
      return _checkCompatibility(info, requirements);
    } catch (e) {
      await _loggingService.log('error', 'Failed to check device compatibility', data: {'error': e.toString()});
      return false;
    }
  }

  // 获取设备状态
  Future<Map<String, dynamic>> getDeviceStatus() async {
    try {
      await _updateDeviceStatus();
      return deviceStatus;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get device status', data: {'error': e.toString()});
      return {};
    }
  }

  Future<void> _loadDeviceInfo() async {
    try {
      if (GetPlatform.isAndroid) {
        deviceInfo.value = await _deviceInfo.androidInfo;
      } else if (GetPlatform.isIOS) {
        deviceInfo.value = await _deviceInfo.iosInfo;
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadPackageInfo() async {
    try {
      packageInfo.value = await PackageInfo.fromPlatform();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _checkDeviceStatus() async {
    try {
      await _updateDeviceStatus();
      await _checkDeviceHealth();
      await _monitorDevicePerformance();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _updateDeviceStatus() async {
    try {
      deviceStatus.value = {
        'battery_level': await _getBatteryLevel(),
        'storage_usage': await _getStorageUsage(),
        'memory_usage': await _getMemoryUsage(),
        'cpu_usage': await _getCpuUsage(),
        'network_status': await _getNetworkStatus(),
        'updated_at': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _getDeviceRequirements() async {
    try {
      final data = await _storageService.getLocal('device_requirements');
      return data != null ? Map<String, dynamic>.from(data) : _getDefaultRequirements();
    } catch (e) {
      return _getDefaultRequirements();
    }
  }

  Map<String, dynamic> _getDefaultRequirements() {
    return {
      'minSdkVersion': 21,
      'minIosVersion': '11.0',
      'minStorage': 500 * 1024 * 1024, // 500MB
      'minMemory': 2 * 1024 * 1024 * 1024, // 2GB
      'requiredFeatures': [
        'camera',
        'location',
        'biometric',
      ],
    };
  }

  bool _checkCompatibility(Map<String, dynamic> info, Map<String, dynamic> requirements) {
    // TODO: 实现兼容性检查
    return true;
  }

  Future<void> _checkDeviceHealth() async {
    try {
      final issues = await _detectDeviceIssues();
      if (issues.isNotEmpty) {
        await _loggingService.log('warning', 'Device health issues detected', data: {'issues': issues});
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _monitorDevicePerformance() async {
    // TODO: 实现性能监控
  }

  Future<int> _getBatteryLevel() async {
    // TODO: 实现电池电量获取
    return 100;
  }

  Future<double> _getStorageUsage() async {
    // TODO: 实现存储使用量获取
    return 0.0;
  }

  Future<double> _getMemoryUsage() async {
    // TODO: 实现内存使用量获取
    return 0.0;
  }

  Future<double> _getCpuUsage() async {
    // TODO: 实现CPU使用率获取
    return 0.0;
  }

  Future<String> _getNetworkStatus() async {
    // TODO: 实现网络状态获取
    return 'connected';
  }

  Future<List<String>> _detectDeviceIssues() async {
    // TODO: 实现设备问题检测
    return [];
  }
} 