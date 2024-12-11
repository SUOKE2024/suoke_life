import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:battery_plus/battery_plus.dart';
import 'package:disk_space/disk_space.dart';
import 'package:system_resources/system_resources.dart';
import 'package:network_info_plus/network_info_plus.dart';

/// 设备资源监控器
class ResourceMonitor {
  final _battery = Battery();
  final _deviceInfo = DeviceInfoPlugin();
  final _connectivity = Connectivity();
  final _networkInfo = NetworkInfo();
  
  /// 资源状态流
  final _resourceStatusController = StreamController<ResourceStatus>.broadcast();
  Stream<ResourceStatus> get resourceStatusStream => _resourceStatusController.stream;
  
  /// 初始化监控
  Future<void> initialize() async {
    // 开始定期监控
    Timer.periodic(const Duration(seconds: 30), (_) => _checkResources());
    
    // 监听网络状态变化
    _connectivity.onConnectivityChanged.listen((result) {
      _checkResources();
    });
    
    // 监听电池状态变化
    _battery.onBatteryStateChanged.listen((state) {
      _checkResources();
    });
    
    // 首次检查
    await _checkResources();
  }
  
  /// 检查资源状态
  Future<void> _checkResources() async {
    try {
      final status = await _getResourceStatus();
      _resourceStatusController.add(status);
    } catch (e) {
      print('Failed to check resources: $e');
    }
  }
  
  /// 获取资源状态
  Future<ResourceStatus> _getResourceStatus() async {
    // 获取设备信息
    final deviceInfo = await _deviceInfo.deviceInfo;
    
    // 获取电池信息
    final batteryLevel = await _battery.batteryLevel;
    final batteryState = await _battery.batteryState;
    
    // 获取存储信息
    final diskSpace = await DiskSpace.getFreeDiskSpace;
    
    // 获取系统资源信息
    final cpuUsage = await SystemResources.getCpuUsage();
    final memoryUsage = await SystemResources.getMemoryUsage();
    
    // 获取网络信息
    final connectivity = await _connectivity.checkConnectivity();
    final wifiIP = await _networkInfo.getWifiIP();
    final wifiName = await _networkInfo.getWifiName();
    final wifiStrength = await _networkInfo.getWifiSignalStrength();
    
    return ResourceStatus(
      deviceInfo: deviceInfo,
      batteryLevel: batteryLevel,
      batteryState: batteryState,
      diskSpace: diskSpace,
      cpuUsage: cpuUsage,
      memoryUsage: memoryUsage,
      connectivity: connectivity,
      networkInfo: NetworkStatus(
        wifiIP: wifiIP,
        wifiName: wifiName,
        wifiStrength: wifiStrength,
      ),
    );
  }
  
  /// 判断是否适合执行计算任务
  bool isReadyForComputing(ResourceStatus status) {
    // 电池电量充足（>30%）或正在充电
    final batteryOk = status.batteryLevel > 30 || 
        status.batteryState == BatteryState.charging;
    
    // CPU使用率较低（<70%）
    final cpuOk = status.cpuUsage < 70;
    
    // 内存使用率较低（<80%）
    final memoryOk = status.memoryUsage < 80;
    
    // 存储空间充足（>1GB）
    final diskOk = status.diskSpace > 1024;  // MB
    
    return batteryOk && cpuOk && memoryOk && diskOk;
  }
  
  /// 判断是否适合执行数据同步
  bool isReadyForSync(ResourceStatus status) {
    // 需要WiFi连接
    final networkOk = status.connectivity == ConnectivityResult.wifi &&
        status.networkInfo.wifiStrength != null &&
        status.networkInfo.wifiStrength! > -70;  // dBm
        
    // 电池电量充足（>20%）或正在充电
    final batteryOk = status.batteryLevel > 20 || 
        status.batteryState == BatteryState.charging;
        
    return networkOk && batteryOk;
  }
  
  /// 获取当前可用的计算资源
  ComputeResource getAvailableResource(ResourceStatus status) {
    // 根据设备状态动态分配计算资源
    final cpuCores = status.cpuUsage < 50 ? 2 : 1;
    final memoryMB = status.memoryUsage < 60 ? 512 : 256;
    final storageMB = status.diskSpace > 2048 ? 1024 : 512;
    
    return ComputeResource(
      cpuCores: cpuCores,
      memoryMB: memoryMB,
      storageMB: storageMB,
    );
  }
  
  void dispose() {
    _resourceStatusController.close();
  }
}

/// 资源状态
class ResourceStatus {
  final BaseDeviceInfo deviceInfo;
  final int batteryLevel;
  final BatteryState batteryState;
  final double diskSpace;
  final double cpuUsage;
  final double memoryUsage;
  final ConnectivityResult connectivity;
  final NetworkStatus networkInfo;
  
  ResourceStatus({
    required this.deviceInfo,
    required this.batteryLevel,
    required this.batteryState,
    required this.diskSpace,
    required this.cpuUsage,
    required this.memoryUsage,
    required this.connectivity,
    required this.networkInfo,
  });
}

/// 网络状态
class NetworkStatus {
  final String? wifiIP;
  final String? wifiName;
  final int? wifiStrength;
  
  NetworkStatus({
    this.wifiIP,
    this.wifiName,
    this.wifiStrength,
  });
}

/// 计算资源
class ComputeResource {
  final int cpuCores;
  final int memoryMB;
  final int storageMB;
  
  ComputeResource({
    required this.cpuCores,
    required this.memoryMB,
    required this.storageMB,
  });
} 