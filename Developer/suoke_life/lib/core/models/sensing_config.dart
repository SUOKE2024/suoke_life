import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:suoke_life/core/constants/app_constants.dart';

/// 传感器类型枚举
enum SensorType {
  /// 加速度计
  accelerometer,
  
  /// 陀螺仪
  gyroscope,
  
  /// 磁力计
  magnetometer,
  
  /// 光照传感器
  light,
  
  /// 接近传感器
  proximity,
  
  /// 步数计
  pedometer,
  
  /// 位置传感器
  location,
  
  /// 气压计
  barometer,
  
  /// 湿度传感器
  humidity,
  
  /// 温度传感器
  temperature,
  
  /// 噪音传感器
  noise,
  
  /// 活动识别
  activity,
}

/// 传感器读取模式
enum SensorReadingMode {
  /// 周期性读取
  periodic,
  
  /// 事件触发读取
  event,
  
  /// 连续读取
  continuous,
  
  /// 单次读取
  oneShot,
  
  /// 阈值触发
  threshold,
}

/// 每个传感器的配置
class SensorConfig {
  /// 传感器类型
  final SensorType type;
  
  /// 是否启用
  final bool enabled;
  
  /// 采样频率 (Hz)
  final double samplingRate;
  
  /// 传感器读取模式
  final SensorReadingMode mode;
  
  /// 批处理大小
  final int batchSize;
  
  /// 额外配置参数
  final Map<String, dynamic> extraParams;
  
  /// 构造函数
  const SensorConfig({
    required this.type,
    this.enabled = true,
    this.samplingRate = 5.0, // 默认5Hz
    this.mode = SensorReadingMode.periodic,
    this.batchSize = AppConstants.sensorDataBatchSize,
    this.extraParams = const {},
  });
  
  /// 复制并修改
  SensorConfig copyWith({
    bool? enabled,
    double? samplingRate,
    SensorReadingMode? mode,
    int? batchSize,
    Map<String, dynamic>? extraParams,
  }) {
    return SensorConfig(
      type: type,
      enabled: enabled ?? this.enabled,
      samplingRate: samplingRate ?? this.samplingRate,
      mode: mode ?? this.mode,
      batchSize: batchSize ?? this.batchSize,
      extraParams: extraParams ?? this.extraParams,
    );
  }
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'type': type.toString().split('.').last,
      'enabled': enabled,
      'samplingRate': samplingRate,
      'mode': mode.toString().split('.').last,
      'batchSize': batchSize,
      'extraParams': extraParams,
    };
  }
  
  /// 从Map创建
  factory SensorConfig.fromMap(Map<String, dynamic> map) {
    return SensorConfig(
      type: SensorType.values.firstWhere(
        (e) => e.toString().split('.').last == map['type'],
        orElse: () => SensorType.accelerometer,
      ),
      enabled: map['enabled'] ?? true,
      samplingRate: map['samplingRate']?.toDouble() ?? 5.0,
      mode: SensorReadingMode.values.firstWhere(
        (e) => e.toString().split('.').last == map['mode'],
        orElse: () => SensorReadingMode.periodic,
      ),
      batchSize: map['batchSize'] ?? AppConstants.sensorDataBatchSize,
      extraParams: Map<String, dynamic>.from(map['extraParams'] ?? {}),
    );
  }
}

/// 传感器配置管理器
class SensorConfigManager {
  /// 传感器配置映射
  final Map<SensorType, SensorConfig> _configs = {};
  
  /// 构造函数
  SensorConfigManager() {
    // 初始化默认配置
    _initializeDefaultConfigs();
  }
  
  /// 初始化默认配置
  void _initializeDefaultConfigs() {
    // 加速度计
    _configs[SensorType.accelerometer] = const SensorConfig(
      type: SensorType.accelerometer,
      samplingRate: 10.0, // 10Hz
    );
    
    // 陀螺仪
    _configs[SensorType.gyroscope] = const SensorConfig(
      type: SensorType.gyroscope,
      samplingRate: 10.0, // 10Hz
    );
    
    // 磁力计
    _configs[SensorType.magnetometer] = const SensorConfig(
      type: SensorType.magnetometer,
      samplingRate: 5.0, // 5Hz
    );
    
    // 光照传感器
    _configs[SensorType.light] = const SensorConfig(
      type: SensorType.light,
      samplingRate: 1.0, // 1Hz
      mode: SensorReadingMode.threshold,
      extraParams: {'threshold': 100}, // 亮度变化100lux触发
    );
    
    // 接近传感器
    _configs[SensorType.proximity] = const SensorConfig(
      type: SensorType.proximity,
      mode: SensorReadingMode.event,
    );
    
    // 步数计
    _configs[SensorType.pedometer] = const SensorConfig(
      type: SensorType.pedometer,
      samplingRate: 1.0, // 1Hz
    );
    
    // 位置传感器
    _configs[SensorType.location] = const SensorConfig(
      type: SensorType.location,
      samplingRate: 0.033, // 每30秒一次
      mode: SensorReadingMode.periodic,
      extraParams: {
        'accuracy': 'low',
        'distanceFilter': 100, // 100米
      },
    );
    
    // 气压计
    _configs[SensorType.barometer] = const SensorConfig(
      type: SensorType.barometer,
      samplingRate: 0.2, // 每5秒一次
    );
    
    // 湿度传感器
    _configs[SensorType.humidity] = const SensorConfig(
      type: SensorType.humidity,
      samplingRate: 0.1, // 每10秒一次
    );
    
    // 温度传感器
    _configs[SensorType.temperature] = const SensorConfig(
      type: SensorType.temperature,
      samplingRate: 0.1, // 每10秒一次
    );
    
    // 噪音传感器
    _configs[SensorType.noise] = const SensorConfig(
      type: SensorType.noise,
      samplingRate: 0.2, // 每5秒一次
      mode: SensorReadingMode.threshold,
      extraParams: {'threshold': 10}, // 声音变化10dB触发
    );
    
    // 活动识别
    _configs[SensorType.activity] = const SensorConfig(
      type: SensorType.activity,
      samplingRate: 0.033, // 每30秒一次
      mode: SensorReadingMode.periodic,
    );
  }
  
  /// 获取指定传感器的配置
  SensorConfig getConfig(SensorType type) {
    return _configs[type] ?? const SensorConfig(
      type: SensorType.accelerometer, 
      enabled: false
    );
  }
  
  /// 更新指定传感器的配置
  void updateConfig(SensorConfig config) {
    _configs[config.type] = config;
  }
  
  /// 启用指定传感器
  void enableSensor(SensorType type, bool enable) {
    final config = getConfig(type);
    _configs[type] = config.copyWith(enabled: enable);
  }
  
  /// 设置采样频率
  void setSamplingRate(SensorType type, double rate) {
    final config = getConfig(type);
    _configs[type] = config.copyWith(samplingRate: rate);
  }
  
  /// 设置传感器模式
  void setSensorMode(SensorType type, SensorReadingMode mode) {
    final config = getConfig(type);
    _configs[type] = config.copyWith(mode: mode);
  }
  
  /// 获取所有启用的传感器
  List<SensorType> getEnabledSensors() {
    return _configs.entries
        .where((entry) => entry.value.enabled)
        .map((entry) => entry.key)
        .toList();
  }
  
  /// 禁用所有传感器
  void disableAllSensors() {
    for (final type in _configs.keys) {
      final config = getConfig(type);
      _configs[type] = config.copyWith(enabled: false);
    }
  }
  
  /// 转换为JSON字符串
  String serialize() {
    final map = <String, dynamic>{};
    for (final entry in _configs.entries) {
      map[entry.key.toString().split('.').last] = entry.value.toMap();
    }
    return jsonEncode(map);
  }
  
  /// 从JSON字符串创建
  static SensorConfigManager deserialize(String json) {
    final manager = SensorConfigManager();
    final map = jsonDecode(json) as Map<String, dynamic>;
    
    for (final entry in map.entries) {
      final type = SensorType.values.firstWhere(
        (e) => e.toString().split('.').last == entry.key,
        orElse: () => SensorType.accelerometer,
      );
      manager._configs[type] = SensorConfig.fromMap(
        Map<String, dynamic>.from(entry.value),
      );
    }
    
    return manager;
  }
  
  /// 重置为默认配置
  void resetToDefaults() {
    _initializeDefaultConfigs();
  }
}

/// 传感器批次
class SensorBatch {
  /// 批次ID
  final String id;
  
  /// 传感器类型
  final SensorType type;
  
  /// 设备ID
  final String deviceId;
  
  /// 会话ID
  final String sessionId;
  
  /// 读数列表
  final List<Map<String, dynamic>> readings;
  
  /// 批次创建时间
  final DateTime createdAt;
  
  /// 是否已同步
  bool synced;
  
  /// 构造函数
  SensorBatch({
    required this.id,
    required this.type,
    required this.deviceId,
    required this.sessionId,
    List<Map<String, dynamic>>? readings,
    DateTime? createdAt,
    this.synced = false,
  }) : 
    readings = readings ?? [],
    createdAt = createdAt ?? DateTime.now();
  
  /// 添加读数
  void addReading(Map<String, dynamic> reading) {
    readings.add(reading);
    synced = false;
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type.toString().split('.').last,
      'deviceId': deviceId,
      'sessionId': sessionId,
      'readings': readings,
      'createdAt': createdAt.toIso8601String(),
      'synced': synced,
    };
  }
  
  /// 从JSON创建
  factory SensorBatch.fromJson(Map<String, dynamic> json) {
    return SensorBatch(
      id: json['id'] as String,
      type: SensorType.values.firstWhere(
        (e) => e.toString().split('.').last == json['type'],
        orElse: () => SensorType.accelerometer,
      ),
      deviceId: json['deviceId'] as String,
      sessionId: json['sessionId'] as String,
      readings: List<Map<String, dynamic>>.from(json['readings'] as List),
      createdAt: DateTime.parse(json['createdAt'] as String),
      synced: json['synced'] as bool,
    );
  }
}

/// 确保配置管理器是单例
/// 用于在没有依赖注入的上下文中访问配置管理器
class SensorConfigSingleton {
  /// 实例
  static SensorConfigManager? _instance;
  
  /// 私有构造函数
  SensorConfigSingleton._();
  
  /// 获取实例
  static SensorConfigManager getInstance() {
    _instance ??= SensorConfigManager();
    return _instance!;
  }
  
  /// 重置实例
  static void reset() {
    _instance = null;
  }
} 