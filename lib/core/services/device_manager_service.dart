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
    // 实现兼容性检查
    if (info['sdkVersion'] < requirements['minSdkVersion']) {
      return false;
    }
    if (info['storage'] < requirements['minStorage']) {
      return false;
    }
    if (info['memory'] < requirements['minMemory']) {
      return false;
    }
    for (final feature in requirements['requiredFeatures']) {
      if (!info['features'].contains(feature)) {
        return false;
      }
    }
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
    // 实现性能监控
    print('监控设备性能 (占位符)');
    // 可以使用性能监控工具或库来实现
  }

  Future<int> _getBatteryLevel() async {
    // 实现电池电量获取
    print('获取电池电量 (占位符)');
    return 85; // 示例返回值
  }

  Future<double> _getStorageUsage() async {
    // 实现存储使用量获取
    print('获取存储使用量 (占位符)');
    return 0.75; // 示例返回值，表示75%已使用
  }

  Future<double> _getMemoryUsage() async {
    // 实现内存使用量获取
    print('获取内存使用量 (占位符)');
    return 0.65; // 示例返回值，表示65%已使用
  }

  Future<double> _getCpuUsage() async {
    // 实现CPU使用率获取
    print('获取CPU使用率 (占位符)');
    return 0.55; // 示例返回值，表示55%已使用
  }

  Future<String> _getNetworkStatus() async {
    // 实现网络状态获取
    print('获取网络状态 (占位符)');
    return 'connected'; // 示例返回值
  }

  Future<List<String>> _detectDeviceIssues() async {
    // 实现设备问题检测
    print('检测设备问题 (占位符)');
    return ['电池电量低', '存储空间不足']; // 示例返回值
  }
} 