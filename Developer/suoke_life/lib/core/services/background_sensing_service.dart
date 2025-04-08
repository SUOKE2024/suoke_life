import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:flutter_background_service_android/flutter_background_service_android.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:path_provider/path_provider.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/core/constants/app_constants.dart';
import 'package:suoke_life/core/models/sensor_data.dart' as sensor_data;
import 'package:suoke_life/core/models/sensing_config.dart' as sensing_config;
import 'package:suoke_life/core/services/network_service.dart';
import 'package:suoke_life/core/services/privacy_protection_service.dart';
import 'package:suoke_life/core/utils/logger.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:uuid/uuid.dart';
import 'package:workmanager/workmanager.dart';

part 'background_sensing_service.g.dart';

/// 背景感知服务提供者
@riverpod
BackgroundSensingService backgroundSensingService(
    BackgroundSensingServiceRef ref) {
  final networkService = ref.watch(networkServiceProvider);
  final privacyService = ref.watch(privacyProtectionServiceProvider);

  return BackgroundSensingService(
    networkService: networkService,
    privacyService: privacyService,
  );
}

/// 后台服务回调处理函数
@pragma('vm:entry-point')
void backgroundServiceEntryPoint() {
  final service = FlutterBackgroundService();

  service.onStart.listen((event) async {
    // 设置前台服务通知
    if (service is AndroidServiceInstance) {
      if (await service.isForegroundService()) {
        service.setForegroundNotificationInfo(
          title: '索克生活正在后台收集数据',
          content: '数据收集仅用于提供更好的健康服务',
        );
      }
    }

    // 初始化传感器配置
    final configManager = await _loadSensorConfig();

    // 初始化存储路径
    final cachePath = await _initializeStorage();

    // 获取设备ID
    final deviceId = await _getDeviceId();

    // 会话ID
    final sessionId = const Uuid().v4();

    // 传感器数据批次
    final batches = <String, sensor_data.SensorBatch>{};

    // 加速度计传感器监听
    StreamSubscription? accelerometerSubscription;
    if (configManager.getConfig(sensor_data.SensorType.accelerometer).enabled) {
      accelerometerSubscription = accelerometerEvents.listen((event) {
        _processSensorReading(
          sensor_data.SensorReading(
            type: sensor_data.SensorType.accelerometer,
            values: [event.x, event.y, event.z],
            timestamp: DateTime.now(),
            unit: 'm/s²',
            mode: sensor_data.SensorReadingMode.periodic,
          ),
          deviceId,
          sessionId,
          cachePath,
          batches,
          service,
        );
      });
    }

    // 陀螺仪传感器监听
    StreamSubscription? gyroscopeSubscription;
    if (configManager.getConfig(sensor_data.SensorType.gyroscope).enabled) {
      gyroscopeSubscription = gyroscopeEvents.listen((event) {
        _processSensorReading(
          sensor_data.SensorReading(
            type: sensor_data.SensorType.gyroscope,
            values: [event.x, event.y, event.z],
            timestamp: DateTime.now(),
            unit: 'rad/s',
            mode: sensor_data.SensorReadingMode.periodic,
          ),
          deviceId,
          sessionId,
          cachePath,
          batches,
          service,
        );
      });
    }

    // 磁力计传感器监听
    StreamSubscription? magnetometerSubscription;
    if (configManager.getConfig(sensor_data.SensorType.magnetometer).enabled) {
      magnetometerSubscription = magnetometerEvents.listen((event) {
        _processSensorReading(
          sensor_data.SensorReading(
            type: sensor_data.SensorType.magnetometer,
            values: [event.x, event.y, event.z],
            timestamp: DateTime.now(),
            unit: 'μT',
            mode: sensor_data.SensorReadingMode.periodic,
          ),
          deviceId,
          sessionId,
          cachePath,
          batches,
          service,
        );
      });
    }

    // 计时器定时保存数据
    Timer.periodic(const Duration(minutes: 5), (timer) async {
      await _saveBatchesToDisk(batches, cachePath);
      service.invoke('data_saved', {
        'batchCount': batches.length,
        'timestamp': DateTime.now().toIso8601String(),
      });
    });

    // 处理服务命令
    service.on('stop_service').listen((event) {
      accelerometerSubscription?.cancel();
      gyroscopeSubscription?.cancel();
      magnetometerSubscription?.cancel();
      service.stopSelf();
    });

    service.on('update_config').listen((event) async {
      if (event == null) return;

      final configJson = event['config'] as String?;
      if (configJson != null) {
        final newConfig = sensing_config.SensorConfigManager.deserialize(configJson);

        // 保存配置
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('sensor_config', configJson);

        // 重启传感器监听
        accelerometerSubscription?.cancel();
        gyroscopeSubscription?.cancel();
        magnetometerSubscription?.cancel();

        // 重新启动传感器监听
        if (newConfig.getConfig(sensor_data.SensorType.accelerometer).enabled) {
          accelerometerSubscription = accelerometerEvents.listen((event) {
            _processSensorReading(
              sensor_data.SensorReading(
                type: sensor_data.SensorType.accelerometer,
                values: [event.x, event.y, event.z],
                timestamp: DateTime.now(),
                unit: 'm/s²',
                mode: sensor_data.SensorReadingMode.periodic,
              ),
              deviceId,
              sessionId,
              cachePath,
              batches,
              service,
            );
          });
        }

        if (newConfig.getConfig(sensor_data.SensorType.gyroscope).enabled) {
          gyroscopeSubscription = gyroscopeEvents.listen((event) {
            _processSensorReading(
              sensor_data.SensorReading(
                type: sensor_data.SensorType.gyroscope,
                values: [event.x, event.y, event.z],
                timestamp: DateTime.now(),
                unit: 'rad/s',
                mode: sensor_data.SensorReadingMode.periodic,
              ),
              deviceId,
              sessionId,
              cachePath,
              batches,
              service,
            );
          });
        }

        if (newConfig.getConfig(sensor_data.SensorType.magnetometer).enabled) {
          magnetometerSubscription = magnetometerEvents.listen((event) {
            _processSensorReading(
              sensor_data.SensorReading(
                type: sensor_data.SensorType.magnetometer,
                values: [event.x, event.y, event.z],
                timestamp: DateTime.now(),
                unit: 'μT',
                mode: sensor_data.SensorReadingMode.periodic,
              ),
              deviceId,
              sessionId,
              cachePath,
              batches,
              service,
            );
          });
        }
      }
    });
  });
}

/// 后台任务回调函数
@pragma('vm:entry-point')
void backgroundTaskCallbackDispatcher() {
  Workmanager().executeTask((taskName, inputData) async {
    switch (taskName) {
      case 'syncSensorData':
        await _syncSensorData();
        break;
      case 'cleanupOldData':
        await _cleanupOldData();
        break;
    }
    return true;
  });
}

/// 处理传感器读数
Future<void> _processSensorReading(
  sensor_data.SensorReading reading,
  String deviceId,
  String sessionId,
  String cachePath,
  Map<String, sensor_data.SensorBatch> batches,
  FlutterBackgroundService service,
) async {
  try {
    final batchId =
        '${reading.type.toString().split('.').last}_${DateTime.now().millisecondsSinceEpoch ~/ (5 * 60 * 1000)}';

    if (!batches.containsKey(batchId)) {
      batches[batchId] = sensor_data.SensorBatch(
        id: batchId,
        sessionId: sessionId,
        deviceId: deviceId,
        startTime: DateTime.now(),
        endTime: DateTime.now(),
        readings: [],
      );
    }

    final batch = batches[batchId]!;
    batch.readings.add(reading);
    batches[batchId] = batch.copyWith(endTime: DateTime.now());

    // 如果读数超过一定数量，保存批次并清空
    if (batch.readings.length >= 1000) {
      await _saveBatchToDisk(batch, cachePath);
      batches.remove(batchId);

      service.invoke('batch_saved', {
        'batchId': batchId,
        'readingCount': batch.readings.length,
        'timestamp': DateTime.now().toIso8601String(),
      });
    }
  } catch (e) {
    print('处理传感器读数失败: $e');
  }
}

/// 将数据批次保存到磁盘
Future<void> _saveBatchToDisk(sensor_data.SensorBatch batch, String cachePath) async {
  try {
    final file = File('$cachePath/${batch.id}.json');
    await file.writeAsString(jsonEncode(batch.toJson()));
  } catch (e) {
    print('保存数据批次失败: $e');
  }
}

/// 将所有数据批次保存到磁盘
Future<void> _saveBatchesToDisk(
    Map<String, sensor_data.SensorBatch> batches, String cachePath) async {
  for (final batch in batches.values) {
    await _saveBatchToDisk(batch, cachePath);
  }
  batches.clear();
}

/// 加载传感器配置
Future<sensing_config.SensorConfigManager> _loadSensorConfig() async {
  try {
    final prefs = await SharedPreferences.getInstance();
    final configJson = prefs.getString('sensor_config');

    if (configJson != null) {
      return sensing_config.SensorConfigManager.deserialize(configJson);
    }
  } catch (e) {
    print('加载传感器配置失败: $e');
  }

  return sensing_config.SensorConfigManager();
}

/// 初始化存储路径
Future<String> _initializeStorage() async {
  final appDir = await getApplicationDocumentsDirectory();
  final cachePath = '${appDir.path}/sensor_data';

  final dir = Directory(cachePath);
  if (!await dir.exists()) {
    await dir.create(recursive: true);
  }

  return cachePath;
}

/// 获取设备ID
Future<String> _getDeviceId() async {
  final prefs = await SharedPreferences.getInstance();
  var deviceId = prefs.getString('device_id');

  if (deviceId == null) {
    deviceId = const Uuid().v4();
    await prefs.setString('device_id', deviceId);
  }

  return deviceId;
}

/// 同步传感器数据
Future<void> _syncSensorData() async {
  try {
    final appDir = await getApplicationDocumentsDirectory();
    final cachePath = '${appDir.path}/sensor_data';

    final dir = Directory(cachePath);
    if (!await dir.exists()) {
      return;
    }

    final files = await dir
        .list()
        .where((entity) => entity is File && entity.path.endsWith('.json'))
        .toList();

    // TODO: 实现数据同步逻辑
    print('找到 ${files.length} 个数据文件待同步');
  } catch (e) {
    print('同步传感器数据失败: $e');
  }
}

/// 清理旧数据
Future<void> _cleanupOldData() async {
  try {
    final appDir = await getApplicationDocumentsDirectory();
    final cachePath = '${appDir.path}/sensor_data';

    final dir = Directory(cachePath);
    if (!await dir.exists()) {
      return;
    }

    final now = DateTime.now();
    final files = await dir
        .list()
        .where((entity) => entity is File && entity.path.endsWith('.json'))
        .toList();

    for (final entity in files) {
      if (entity is File) {
        final stat = await entity.stat();
        final fileAge = now.difference(stat.modified);

        // 删除30天以上的数据
        if (fileAge.inDays > 30) {
          await entity.delete();
        }
      }
    }
  } catch (e) {
    print('清理旧数据失败: $e');
  }
}

/// 背景感知服务类
class BackgroundSensingService {
  static const String _tag = 'BackgroundSensingService';

  /// 网络服务
  final NetworkService _networkService;

  /// 隐私保护服务
  final PrivacyProtectionService _privacyService;

  /// 后台服务
  late final FlutterBackgroundService _backgroundService;

  /// 本地通知
  late final FlutterLocalNotificationsPlugin _notifications;

  /// 传感器配置管理器
  late final sensing_config.SensorConfigManager _configManager;

  /// 是否初始化完成
  bool _isInitialized = false;

  /// 是否正在运行
  bool _isRunning = false;

  /// 构造函数
  BackgroundSensingService({
    required NetworkService networkService,
    required PrivacyProtectionService privacyService,
  })  : _networkService = networkService,
        _privacyService = privacyService {
    _backgroundService = FlutterBackgroundService();
    _notifications = FlutterLocalNotificationsPlugin();
    _configManager = sensing_config.SensorConfigManager();
  }

  /// 初始化服务
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      Logger.i(_tag, '初始化背景感知服务');

      // 初始化 Workmanager
      await Workmanager().initialize(
        backgroundTaskCallbackDispatcher,
        isInDebugMode: kDebugMode,
      );

      // 初始化本地通知
      await _initializeNotifications();

      // 初始化后台服务
      await _configureBackgroundService();

      // 加载传感器配置
      await _loadConfig();

      // 注册定期任务
      await _registerPeriodicTasks();

      _isInitialized = true;
      Logger.i(_tag, '背景感知服务初始化完成');
    } catch (e) {
      Logger.e(_tag, '初始化背景感知服务失败: $e');
      rethrow;
    }
  }

  /// 初始化本地通知
  Future<void> _initializeNotifications() async {
    const androidSettings = AndroidInitializationSettings('app_icon');
    const darwinSettings = DarwinInitializationSettings();

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: darwinSettings,
    );

    await _notifications.initialize(initSettings);
  }

  /// 配置后台服务
  Future<void> _configureBackgroundService() async {
    await _backgroundService.configure(
      androidConfiguration: AndroidConfiguration(
        onStart: backgroundServiceEntryPoint,
        autoStart: false,
        isForegroundMode: true,
        initialNotificationTitle: '索克生活',
        initialNotificationContent: '健康数据收集运行中',
        foregroundServiceNotificationId: 888,
      ),
      iosConfiguration: IosConfiguration(
        autoStart: false,
        onForeground: backgroundServiceEntryPoint,
        onBackground: onIosBackground,
      ),
    );
  }

  /// iOS后台处理
  @pragma('vm:entry-point')
  static Future<bool> onIosBackground(ServiceInstance service) async {
    WidgetsFlutterBinding.ensureInitialized();
    return true;
  }

  /// 加载传感器配置
  Future<void> _loadConfig() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final configJson = prefs.getString('sensor_config');

      if (configJson != null) {
        _configManager = sensing_config.SensorConfigManager.deserialize(configJson);
      }
    } catch (e) {
      Logger.e(_tag, '加载传感器配置失败: $e');
    }
  }

  /// 注册定期任务
  Future<void> _registerPeriodicTasks() async {
    // 数据同步任务 (每小时)
    await Workmanager().registerPeriodicTask(
      'sensorDataSync',
      'syncSensorData',
      frequency: const Duration(hours: 1),
      constraints: Constraints(
        networkType: NetworkType.connected,
        requiresBatteryNotLow: true,
      ),
    );

    // 数据清理任务 (每天)
    await Workmanager().registerPeriodicTask(
      'oldDataCleanup',
      'cleanupOldData',
      frequency: const Duration(days: 1),
    );
  }

  /// 启动服务
  Future<bool> startService() async {
    if (!_isInitialized) {
      await initialize();
    }

    if (_isRunning) return true;

    try {
      final isRunning = await _backgroundService.startService();
      _isRunning = isRunning;

      if (isRunning) {
        Logger.i(_tag, '背景感知服务启动成功');
      } else {
        Logger.e(_tag, '背景感知服务启动失败');
      }

      return isRunning;
    } catch (e) {
      Logger.e(_tag, '启动背景感知服务失败: $e');
      return false;
    }
  }

  /// 停止服务
  Future<void> stopService() async {
    if (!_isRunning) return;

    try {
      await _backgroundService.invoke('stop_service');
      _isRunning = false;
      Logger.i(_tag, '背景感知服务已停止');
    } catch (e) {
      Logger.e(_tag, '停止背景感知服务失败: $e');
    }
  }

  /// 更新传感器配置
  Future<void> updateSensorConfig(sensing_config.SensorConfigManager configManager) async {
    try {
      _configManager = configManager;

      // 保存配置
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('sensor_config', configManager.serialize());

      // 通知后台服务更新配置
      await _backgroundService.invoke('update_config', {
        'config': configManager.serialize(),
      });

      Logger.i(_tag, '传感器配置已更新');
    } catch (e) {
      Logger.e(_tag, '更新传感器配置失败: $e');
    }
  }

  /// 检查服务状态
  Future<bool> isServiceRunning() async {
    return await _backgroundService.isRunning();
  }

  /// 手动触发数据同步
  Future<void> triggerDataSync() async {
    await Workmanager().registerOneOffTask(
      'manualSensorDataSync',
      'syncSensorData',
      existingWorkPolicy: ExistingWorkPolicy.replace,
    );
  }

  /// 获取当前传感器配置
  sensing_config.SensorConfigManager getCurrentConfig() {
    return _configManager;
  }

  /// 启用传感器
  Future<void> enableSensor(sensor_data.SensorType type) async {
    _configManager.enableSensor(type);
    await updateSensorConfig(_configManager);
  }

  /// 禁用传感器
  Future<void> disableSensor(sensor_data.SensorType type) async {
    _configManager.disableSensor(type);
    await updateSensorConfig(_configManager);
  }

  /// 设置采样间隔
  Future<void> setSamplingInterval(sensor_data.SensorType type, int intervalMs) async {
    _configManager.setSamplingInterval(type, intervalMs);
    await updateSensorConfig(_configManager);
  }

  /// 设置电池优化级别
  Future<void> setPowerOptimizationLevel(sensor_data.SensorType type, int level) async {
    _configManager.setPowerOptimizationLevel(type, level);
    await updateSensorConfig(_configManager);
  }

  /// 设置读取模式
  Future<void> setReadingMode(sensor_data.SensorType type, sensor_data.SensorReadingMode mode) async {
    _configManager.setReadingMode(type, mode);
    await updateSensorConfig(_configManager);
  }

  /// 获取传感器状态
  Future<Map<String, dynamic>> getSensorStatus() async {
    final isRunning = await isServiceRunning();
    final enabledSensors = _configManager.getEnabledSensors();

    return {
      'isRunning': isRunning,
      'enabledSensors':
          enabledSensors.map((e) => e.toString().split('.').last).toList(),
      'configuredSensors': _configManager._configs.length,
    };
  }

  /// 复制带隐私保护的传感器批次
  Future<sensor_data.SensorBatch> copyBatchWithPrivacyProtection(sensor_data.SensorBatch batch) async {
    try {
      // 应用隐私保护
      final protectedReadings =
          await _privacyService.protectSensorData(batch.readings);

      // 创建新批次
      return sensor_data.SensorBatch(
        id: batch.id,
        sessionId: batch.sessionId,
        deviceId: batch.deviceId,
        userId: batch.userId,
        startTime: batch.startTime,
        endTime: batch.endTime,
        readings: protectedReadings,
        metadata: batch.metadata,
      );
    } catch (e) {
      Logger.e(_tag, '应用隐私保护失败: $e');
      return batch;
    }
  }
}
