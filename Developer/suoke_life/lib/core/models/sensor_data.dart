import 'dart:convert';

/// 传感器类型枚举
enum SensorType {
  /// 加速度传感器
  accelerometer,

  /// 陀螺仪传感器
  gyroscope,

  /// 环境光传感器
  light,

  /// 磁力计传感器
  magnetometer,

  /// 温度传感器
  temperature,

  /// 湿度传感器
  humidity,

  /// 心率传感器
  heartRate,

  /// 血氧传感器
  bloodOxygen,

  /// 步数传感器
  steps,

  /// 微信号传感器
  soundLevel,

  /// 位置传感器
  location,

  /// 血压传感器
  bloodPressure,

  /// 睡眠传感器
  sleep,

  /// 体温传感器
  bodyTemperature,

  /// 呼吸传感器
  respiration,

  /// 皮电传感器
  skinConductance,

  /// 自定义传感器
  custom,
}

/// 传感器读取模式
enum SensorReadingMode {
  /// 主动模式 - 用户明确触发
  active,

  /// 被动模式 - 后台自动收集
  passive,

  /// 周期模式 - 定时收集
  periodic,

  /// 变化模式 - 数值变化时收集
  onChanged,

  /// 阈值模式 - 超过阈值时收集
  threshold,
}

/// 传感器读数模型
class SensorReading {
  /// 传感器类型
  final SensorType type;

  /// 传感器读数值（多维数据）
  final List<double> values;

  /// 时间戳
  final DateTime timestamp;

  /// 原始数据的单位
  final String? unit;

  /// 元数据
  final Map<String, dynamic>? metadata;

  /// 读取模式
  final SensorReadingMode? mode;

  /// 精度
  final double? accuracy;

  /// 采样间隔（毫秒）
  final int? samplingInterval;

  /// 构造函数
  SensorReading({
    required this.type,
    required this.values,
    required this.timestamp,
    this.unit,
    this.metadata,
    this.mode,
    this.accuracy,
    this.samplingInterval,
  });

  /// 从JSON创建
  factory SensorReading.fromJson(Map<String, dynamic> json) {
    return SensorReading(
      type: SensorType.values.firstWhere(
        (e) => e.toString() == 'SensorType.${json['type']}',
        orElse: () => SensorType.custom,
      ),
      values:
          (json['values'] as List).map((v) => (v as num).toDouble()).toList(),
      timestamp: DateTime.parse(json['timestamp']),
      unit: json['unit'],
      metadata: json['metadata'],
      mode: json['mode'] != null
          ? SensorReadingMode.values.firstWhere(
              (e) => e.toString() == 'SensorReadingMode.${json['mode']}',
              orElse: () => SensorReadingMode.passive,
            )
          : null,
      accuracy: json['accuracy'] != null
          ? (json['accuracy'] as num).toDouble()
          : null,
      samplingInterval: json['samplingInterval'],
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    final typeStr = type.toString().split('.').last;
    final modeStr = mode?.toString().split('.').last;

    return {
      'type': typeStr,
      'values': values,
      'timestamp': timestamp.toIso8601String(),
      if (unit != null) 'unit': unit,
      if (metadata != null) 'metadata': metadata,
      if (mode != null) 'mode': modeStr,
      if (accuracy != null) 'accuracy': accuracy,
      if (samplingInterval != null) 'samplingInterval': samplingInterval,
    };
  }

  /// 获取特定维度的值
  double getValue(int dimension) {
    if (dimension < 0 || dimension >= values.length) {
      throw ArgumentError(
          '维度索引超出范围: $dimension (可用维度: 0-${values.length - 1})');
    }
    return values[dimension];
  }

  /// 获取摘要
  String getSummary() {
    final typeStr = type.toString().split('.').last;
    final valuesStr = values.map((v) => v.toStringAsFixed(2)).join(', ');
    final timestampStr = timestamp.toString();
    return '[$typeStr] 值: [$valuesStr] 时间: $timestampStr';
  }

  /// 克隆并修改
  SensorReading copyWith({
    SensorType? type,
    List<double>? values,
    DateTime? timestamp,
    String? unit,
    Map<String, dynamic>? metadata,
    SensorReadingMode? mode,
    double? accuracy,
    int? samplingInterval,
  }) {
    return SensorReading(
      type: type ?? this.type,
      values: values ?? this.values,
      timestamp: timestamp ?? this.timestamp,
      unit: unit ?? this.unit,
      metadata: metadata ?? this.metadata,
      mode: mode ?? this.mode,
      accuracy: accuracy ?? this.accuracy,
      samplingInterval: samplingInterval ?? this.samplingInterval,
    );
  }
}

/// 传感器数据批次
class SensorBatch {
  /// 批次ID
  final String id;

  /// 会话ID
  final String sessionId;

  /// 设备ID
  final String deviceId;

  /// 用户ID
  final String? userId;

  /// 采集开始时间
  final DateTime startTime;

  /// 采集结束时间
  final DateTime endTime;

  /// 传感器读数集合
  final List<SensorReading> readings;

  /// 元数据
  final Map<String, dynamic>? metadata;

  /// 构造函数
  SensorBatch({
    required this.id,
    required this.sessionId,
    required this.deviceId,
    this.userId,
    required this.startTime,
    required this.endTime,
    required this.readings,
    this.metadata,
  });

  /// 从JSON创建
  factory SensorBatch.fromJson(Map<String, dynamic> json) {
    return SensorBatch(
      id: json['id'],
      sessionId: json['sessionId'],
      deviceId: json['deviceId'],
      userId: json['userId'],
      startTime: DateTime.parse(json['startTime']),
      endTime: DateTime.parse(json['endTime']),
      readings: (json['readings'] as List)
          .map((r) => SensorReading.fromJson(r))
          .toList(),
      metadata: json['metadata'],
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sessionId': sessionId,
      'deviceId': deviceId,
      if (userId != null) 'userId': userId,
      'startTime': startTime.toIso8601String(),
      'endTime': endTime.toIso8601String(),
      'readings': readings.map((r) => r.toJson()).toList(),
      if (metadata != null) 'metadata': metadata,
    };
  }

  /// 获取指定类型的所有读数
  List<SensorReading> getReadingsOfType(SensorType type) {
    return readings.where((r) => r.type == type).toList();
  }

  /// 获取读数数量
  int get readingCount => readings.length;

  /// 获取持续时间（秒）
  double get durationInSeconds =>
      endTime.difference(startTime).inMilliseconds / 1000;

  /// 获取采样率（每秒读数）
  double get samplingRate => readingCount / durationInSeconds;
}

/// 传感器配置
class SensorConfig {
  /// 传感器类型
  final SensorType type;

  /// 读取模式
  final SensorReadingMode mode;

  /// 采样间隔（毫秒）
  final int samplingInterval;

  /// 是否启用
  final bool enabled;

  /// 电池使用优化级别（1-5，1最低，5最高）
  final int powerOptimizationLevel;

  /// 自定义配置参数
  final Map<String, dynamic>? parameters;

  /// 构造函数
  SensorConfig({
    required this.type,
    required this.mode,
    required this.samplingInterval,
    required this.enabled,
    this.powerOptimizationLevel = 3,
    this.parameters,
  });

  /// 默认配置
  factory SensorConfig.defaultConfig(SensorType type) {
    switch (type) {
      case SensorType.accelerometer:
      case SensorType.gyroscope:
      case SensorType.magnetometer:
        return SensorConfig(
          type: type,
          mode: SensorReadingMode.periodic,
          samplingInterval: 100, // 10Hz
          enabled: true,
          powerOptimizationLevel: 3,
        );

      case SensorType.light:
      case SensorType.temperature:
      case SensorType.humidity:
        return SensorConfig(
          type: type,
          mode: SensorReadingMode.onChanged,
          samplingInterval: 1000, // 1Hz
          enabled: true,
          powerOptimizationLevel: 2,
        );

      case SensorType.heartRate:
      case SensorType.bloodOxygen:
      case SensorType.bloodPressure:
      case SensorType.bodyTemperature:
        return SensorConfig(
          type: type,
          mode: SensorReadingMode.periodic,
          samplingInterval: 60000, // 1分钟
          enabled: true,
          powerOptimizationLevel: 4,
        );

      case SensorType.steps:
      case SensorType.sleep:
        return SensorConfig(
          type: type,
          mode: SensorReadingMode.onChanged,
          samplingInterval: 300000, // 5分钟
          enabled: true,
          powerOptimizationLevel: 2,
        );

      case SensorType.location:
        return SensorConfig(
          type: type,
          mode: SensorReadingMode.periodic,
          samplingInterval: 300000, // 5分钟
          enabled: true,
          powerOptimizationLevel: 4,
          parameters: {
            'accuracy': 'medium',
            'distanceFilter': 50, // 50米
          },
        );

      case SensorType.soundLevel:
        return SensorConfig(
          type: type,
          mode: SensorReadingMode.periodic,
          samplingInterval: 60000, // 1分钟
          enabled: true,
          powerOptimizationLevel: 3,
        );

      case SensorType.respiration:
      case SensorType.skinConductance:
        return SensorConfig(
          type: type,
          mode: SensorReadingMode.periodic,
          samplingInterval: 60000, // 1分钟
          enabled: false, // 默认禁用，需要外部设备
          powerOptimizationLevel: 4,
        );

      case SensorType.custom:
      default:
        return SensorConfig(
          type: type,
          mode: SensorReadingMode.passive,
          samplingInterval: 1000, // 1Hz
          enabled: false,
          powerOptimizationLevel: 3,
        );
    }
  }

  /// 从JSON创建
  factory SensorConfig.fromJson(Map<String, dynamic> json) {
    return SensorConfig(
      type: SensorType.values.firstWhere(
        (e) => e.toString() == 'SensorType.${json['type']}',
        orElse: () => SensorType.custom,
      ),
      mode: SensorReadingMode.values.firstWhere(
        (e) => e.toString() == 'SensorReadingMode.${json['mode']}',
        orElse: () => SensorReadingMode.passive,
      ),
      samplingInterval: json['samplingInterval'],
      enabled: json['enabled'],
      powerOptimizationLevel: json['powerOptimizationLevel'] ?? 3,
      parameters: json['parameters'],
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    final typeStr = type.toString().split('.').last;
    final modeStr = mode.toString().split('.').last;

    return {
      'type': typeStr,
      'mode': modeStr,
      'samplingInterval': samplingInterval,
      'enabled': enabled,
      'powerOptimizationLevel': powerOptimizationLevel,
      if (parameters != null) 'parameters': parameters,
    };
  }

  /// 复制并修改
  SensorConfig copyWith({
    SensorType? type,
    SensorReadingMode? mode,
    int? samplingInterval,
    bool? enabled,
    int? powerOptimizationLevel,
    Map<String, dynamic>? parameters,
  }) {
    return SensorConfig(
      type: type ?? this.type,
      mode: mode ?? this.mode,
      samplingInterval: samplingInterval ?? this.samplingInterval,
      enabled: enabled ?? this.enabled,
      powerOptimizationLevel:
          powerOptimizationLevel ?? this.powerOptimizationLevel,
      parameters: parameters ?? this.parameters,
    );
  }
}

/// 传感器配置管理器
class SensorConfigManager {
  /// 所有传感器配置
  final Map<SensorType, SensorConfig> _configs = {};

  /// 构造函数
  SensorConfigManager() {
    // 初始化所有传感器的默认配置
    for (final type in SensorType.values) {
      _configs[type] = SensorConfig.defaultConfig(type);
    }
  }

  /// 获取传感器配置
  SensorConfig getConfig(SensorType type) {
    return _configs[type] ?? SensorConfig.defaultConfig(type);
  }

  /// 更新传感器配置
  void updateConfig(SensorConfig config) {
    _configs[config.type] = config;
  }

  /// 启用传感器
  void enableSensor(SensorType type) {
    final config = getConfig(type);
    _configs[type] = config.copyWith(enabled: true);
  }

  /// 禁用传感器
  void disableSensor(SensorType type) {
    final config = getConfig(type);
    _configs[type] = config.copyWith(enabled: false);
  }

  /// 设置采样间隔
  void setSamplingInterval(SensorType type, int intervalMs) {
    final config = getConfig(type);
    _configs[type] = config.copyWith(samplingInterval: intervalMs);
  }

  /// 设置读取模式
  void setReadingMode(SensorType type, SensorReadingMode mode) {
    final config = getConfig(type);
    _configs[type] = config.copyWith(mode: mode);
  }

  /// 设置电池优化级别
  void setPowerOptimizationLevel(SensorType type, int level) {
    if (level < 1 || level > 5) {
      throw ArgumentError('电池优化级别必须在1-5之间');
    }

    final config = getConfig(type);
    _configs[type] = config.copyWith(powerOptimizationLevel: level);
  }

  /// 获取所有已启用的传感器类型
  List<SensorType> getEnabledSensors() {
    return _configs.entries
        .where((entry) => entry.value.enabled)
        .map((entry) => entry.key)
        .toList();
  }

  /// 序列化所有配置
  String serialize() {
    final configs = _configs.values.map((config) => config.toJson()).toList();
    return jsonEncode(configs);
  }

  /// 从序列化数据创建
  static SensorConfigManager deserialize(String serialized) {
    final manager = SensorConfigManager();

    try {
      final List<dynamic> configs = jsonDecode(serialized);

      for (final config in configs) {
        final sensorConfig = SensorConfig.fromJson(config);
        manager._configs[sensorConfig.type] = sensorConfig;
      }
    } catch (e) {
      // 解析失败时使用默认配置
      print('解析传感器配置失败: $e');
    }

    return manager;
  }
}
