import 'dart:async';
import 'dart:io';
import 'dart:math';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'package:activity_recognition_flutter/activity_recognition_flutter.dart';
import 'package:light/light.dart';
import 'package:noise_meter/noise_meter.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/core/models/context_data.dart';
import 'package:suoke_life/core/models/sensor_data.dart';
import 'package:suoke_life/core/services/background_sensing_service.dart';
import 'package:suoke_life/core/services/edge_intelligence_service.dart';
import 'package:suoke_life/core/utils/logger.dart';
import 'package:uuid/uuid.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 环境类型
enum EnvironmentType {
  /// 室内
  indoor,

  /// 室外
  outdoor,

  /// 移动中
  moving,

  /// 工作场所
  workplace,

  /// 家庭环境
  home,

  /// 社交场所
  social,

  /// 公共交通
  publicTransport,

  /// 医疗环境
  medical,

  /// 自然环境
  nature,

  /// 噪音环境
  noisy,

  /// 安静环境
  quiet,

  /// 未知环境
  unknown,
}

/// 活动状态
enum ActivityState {
  /// 静止
  still,

  /// 行走
  walking,

  /// 跑步
  running,

  /// 骑自行车
  onBicycle,

  /// 驾车
  inVehicle,

  /// 爬楼梯
  onStairs,

  /// 躺下
  lyingDown,

  /// 坐着
  sitting,

  /// 站立
  standing,

  /// 摇晃
  tilting,

  /// 未知状态
  unknown,
}

/// 活动类型
enum ActivityType {
  /// 静止
  still,
  /// 行走
  walking,
  /// 跑步
  running,
  /// 骑行
  cycling,
  /// 驾车
  driving,
  /// 未知
  unknown,
}

/// 环境感知提供者
final contextAwareSensingServiceProvider = Provider<ContextAwareSensingService>((ref) {
  final backgroundService = ref.watch(backgroundSensingServiceProvider);
  final edgeIntelligence = ref.watch(edgeIntelligenceServiceProvider);

  return ContextAwareSensingService(
    backgroundService: backgroundService,
    edgeIntelligence: edgeIntelligence,
  );
});

/// 上下文感知服务
///
/// 提供设备当前环境和用户活动状态的感知功能
class ContextAwareSensingService {
  static const String _tag = 'ContextAwareSensingService';

  /// 背景感知服务
  final BackgroundSensingService? _backgroundService;

  /// 边缘智能服务
  final EdgeIntelligenceService? _edgeIntelligence;

  /// 设备信息
  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();

  /// 环境光传感器
  Light? _lightSensor;

  /// 噪音传感器
  NoiseMeter? _noiseMeter;

  /// 活动识别
  ActivityRecognition? _activityRecognition;

  /// 是否初始化完成
  bool _isInitialized = false;

  /// 是否正在监控
  bool _isMonitoring = false;

  /// 环境光监听器
  StreamSubscription<int>? _lightSubscription;

  /// 噪音监听器
  StreamSubscription<NoiseReading>? _noiseSubscription;

  /// 活动监听器
  StreamSubscription<ActivityEvent>? _activitySubscription;

  /// 位置监听器
  StreamSubscription<Position>? _locationSubscription;

  /// 加速度监听器
  StreamSubscription<AccelerometerEvent>? _accelerometerSubscription;

  /// 当前光照级别 (lux)
  int _currentLux = 0;

  /// 当前噪声级别 (dB)
  double _currentNoiseLevel = 0.0;

  /// 当前位置
  Position? _currentPosition;

  /// 当前活动状态
  ActivityState _currentActivity = ActivityState.unknown;

  /// 活动置信度
  int _activityConfidence = 0;

  /// 活动持续时间（秒）
  int _activityDuration = 0;

  /// 当前环境类型
  EnvironmentType _currentEnvironment = EnvironmentType.unknown;

  /// 上次环境变化时间
  DateTime _lastEnvironmentChange = DateTime.now();

  /// 用户上下文更新流控制器
  final StreamController<UserContext> _contextStreamController =
      StreamController<UserContext>.broadcast();

  /// 用户上下文更新流
  Stream<UserContext> get contextStream => _contextStreamController.stream;

  /// 是否正在运行
  bool _isRunning = false;
  
  /// 上下文数据流控制器
  final _contextDataController = StreamController<Map<String, dynamic>>.broadcast();
  
  /// 模拟上下文数据生成定时器
  Timer? _mockDataTimer;
  
  /// 当前光照强度 (lux)
  double _currentLightLevel = 0;
  
  /// 当前环境温度 (摄氏度)
  double _currentTemperature = 22;
  
  /// 当前环境湿度 (%)
  double _currentHumidity = 50;
  
  /// 当前气压 (hPa)
  double _currentPressure = 1013;
  
  /// 当前空气质量指数
  int _currentAirQualityIndex = 50;

  /// 构造函数
  ContextAwareSensingService({
    BackgroundSensingService? backgroundService,
    EdgeIntelligenceService? edgeIntelligence,
  })  : _backgroundService = backgroundService,
        _edgeIntelligence = edgeIntelligence;

  /// 初始化服务
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      Logger.i(_tag, '初始化上下文感知服务');

      // 初始化传感器
      _lightSensor = Light();
      _noiseMeter = NoiseMeter();
      _activityRecognition = ActivityRecognition.instance;

      // 请求权限
      await _requestPermissions();

      _isInitialized = true;
      Logger.i(_tag, '上下文感知服务初始化完成');
    } catch (e) {
      Logger.e(_tag, '初始化上下文感知服务失败: $e');
      rethrow;
    }
  }

  /// 请求权限
  Future<void> _requestPermissions() async {
    try {
      // 位置权限
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          Logger.w(_tag, '位置权限被拒绝');
        }
      }

      // 活动识别权限
      bool activityRecognitionPermissionGranted =
          await _activityRecognition!.checkPermission();
      if (!activityRecognitionPermissionGranted) {
        activityRecognitionPermissionGranted =
            await _activityRecognition!.requestPermission();
        if (!activityRecognitionPermissionGranted) {
          Logger.w(_tag, '活动识别权限被拒绝');
        }
      }
    } catch (e) {
      Logger.e(_tag, '请求权限失败: $e');
    }
  }

  /// 开始监控
  Future<bool> startMonitoring() async {
    if (!_isInitialized) {
      await initialize();
    }

    if (_isMonitoring) return true;

    try {
      Logger.i(_tag, '开始环境监控');

      // 开始环境光监控
      await _startLightMonitoring();

      // 开始噪音监控
      await _startNoiseMonitoring();

      // 开始活动监控
      await _startActivityMonitoring();

      // 开始位置监控
      await _startLocationMonitoring();

      // 开始加速度监控
      await _startAccelerometerMonitoring();

      // 设置环境分析定时器
      _startEnvironmentAnalysisTimer();

      _isMonitoring = true;
      Logger.i(_tag, '环境监控已启动');

      // 初始化用户上下文
      _updateUserContext();

      return true;
    } catch (e) {
      Logger.e(_tag, '启动环境监控失败: $e');
      await stopMonitoring();
      return false;
    }
  }

  /// 停止监控
  Future<void> stopMonitoring() async {
    if (!_isMonitoring) return;

    try {
      Logger.i(_tag, '停止环境监控');

      // 取消所有订阅
      await _lightSubscription?.cancel();
      await _noiseSubscription?.cancel();
      await _activitySubscription?.cancel();
      await _locationSubscription?.cancel();
      await _accelerometerSubscription?.cancel();

      _lightSubscription = null;
      _noiseSubscription = null;
      _activitySubscription = null;
      _locationSubscription = null;
      _accelerometerSubscription = null;

      _isMonitoring = false;
      Logger.i(_tag, '环境监控已停止');
    } catch (e) {
      Logger.e(_tag, '停止环境监控失败: $e');
    }
  }

  /// 开始环境光监控
  Future<void> _startLightMonitoring() async {
    try {
      _lightSubscription = _lightSensor?.lightSensorStream.listen((lux) {
        _currentLux = lux;
        Logger.d(_tag, '当前光照: $lux lux');
      });
    } catch (e) {
      Logger.e(_tag, '启动环境光监控失败: $e');
    }
  }

  /// 开始噪音监控
  Future<void> _startNoiseMonitoring() async {
    try {
      _noiseSubscription = _noiseMeter?.noiseStream.listen((noiseReading) {
        _currentNoiseLevel = noiseReading.meanDecibel;
        Logger.d(_tag, '当前噪音: ${noiseReading.meanDecibel} dB');
      });
    } catch (e) {
      Logger.e(_tag, '启动噪音监控失败: $e');
    }
  }

  /// 开始活动监控
  Future<void> _startActivityMonitoring() async {
    try {
      _activitySubscription =
          _activityRecognition?.activityStream.listen((ActivityEvent event) {
        // 映射活动类型
        final newActivity = _mapToActivityState(event.type);

        // 只在活动类型变化时更新
        if (newActivity != _currentActivity) {
          _currentActivity = newActivity;
          _activityConfidence = event.confidence;
          _activityDuration = 0;
          Logger.d(_tag, '活动变化: $_currentActivity, 置信度: $_activityConfidence%');

          // 活动变化时更新上下文
          _updateUserContext();
        } else {
          _activityConfidence = event.confidence;
        }
      });
    } catch (e) {
      Logger.e(_tag, '启动活动监控失败: $e');
    }
  }

  /// 开始位置监控
  Future<void> _startLocationMonitoring() async {
    try {
      LocationSettings locationSettings = const LocationSettings(
        accuracy: LocationAccuracy.low,
        distanceFilter: 100, // 100米
      );

      _locationSubscription = Geolocator.getPositionStream(
        locationSettings: locationSettings,
      ).listen((Position position) {
        _currentPosition = position;
        Logger.d(_tag, '当前位置: ${position.latitude}, ${position.longitude}');
      });
    } catch (e) {
      Logger.e(_tag, '启动位置监控失败: $e');
    }
  }

  /// 开始加速度监控
  Future<void> _startAccelerometerMonitoring() async {
    try {
      _accelerometerSubscription = accelerometerEvents.listen((event) {
        // 检测明显运动
        final magnitude =
            sqrt(event.x * event.x + event.y * event.y + event.z * event.z);
        if (magnitude > 15) {
          // 阈值
          Logger.d(_tag, '检测到明显运动: $magnitude');
        }
      });
    } catch (e) {
      Logger.e(_tag, '启动加速度监控失败: $e');
    }
  }

  /// 启动环境分析定时器
  void _startEnvironmentAnalysisTimer() {
    // 每30秒分析一次环境
    Timer.periodic(const Duration(seconds: 30), (timer) {
      if (!_isMonitoring) {
        timer.cancel();
        return;
      }

      _analyzeEnvironment();
      _activityDuration += 30; // 增加活动持续时间
      _updateUserContext();
    });
  }

  /// 分析当前环境
  void _analyzeEnvironment() {
    try {
      EnvironmentType detectedEnvironment = EnvironmentType.unknown;

      // 基于光照级别推断
      if (_currentLux < 50) {
        // 低光照，可能是室内或夜间
        detectedEnvironment = EnvironmentType.indoor;
      } else if (_currentLux > 1000) {
        // 高光照，可能是室外
        detectedEnvironment = EnvironmentType.outdoor;
      }

      // 基于噪音级别调整
      if (_currentNoiseLevel > 70) {
        detectedEnvironment = EnvironmentType.noisy;
      } else if (_currentNoiseLevel < 40) {
        detectedEnvironment = EnvironmentType.quiet;
      }

      // 基于活动状态调整
      if (_currentActivity == ActivityState.inVehicle) {
        if (_currentNoiseLevel > 60) {
          detectedEnvironment = EnvironmentType.publicTransport;
        } else {
          detectedEnvironment = EnvironmentType.moving;
        }
      } else if (_currentActivity == ActivityState.walking ||
          _currentActivity == ActivityState.running ||
          _currentActivity == ActivityState.onBicycle) {
        detectedEnvironment = EnvironmentType.moving;
      }

      // 更新当前环境类型
      if (detectedEnvironment != EnvironmentType.unknown &&
          detectedEnvironment != _currentEnvironment) {
        Logger.i(_tag, '环境变化: $_currentEnvironment -> $detectedEnvironment');
        _currentEnvironment = detectedEnvironment;
        _lastEnvironmentChange = DateTime.now();
      }
    } catch (e) {
      Logger.e(_tag, '分析环境失败: $e');
    }
  }

  /// 更新用户上下文
  void _updateUserContext() {
    try {
      // 创建环境上下文
      final environmentContext = EnvironmentContext(
        type: _currentEnvironment,
        lightLevel: _currentLux.toDouble(),
        noiseLevel: _currentNoiseLevel,
        location: _currentPosition != null
            ? {
                'latitude': _currentPosition!.latitude,
                'longitude': _currentPosition!.longitude,
                'accuracy': _currentPosition!.accuracy,
              }
            : null,
        timestamp: DateTime.now(),
      );

      // 创建活动上下文
      final activityContext = ActivityContext(
        state: _currentActivity,
        confidence: _activityConfidence,
        duration: _activityDuration,
        timestamp: DateTime.now(),
      );

      // 推断用户状态
      final inferredState =
          _inferUserState(environmentContext, activityContext);

      // 创建用户上下文
      final userContext = UserContext(
        activity: activityContext,
        environment: environmentContext,
        inferredState: inferredState,
        timestamp: DateTime.now(),
      );

      // 发送上下文更新
      _contextStreamController.add(userContext);

      Logger.d(_tag, '用户上下文已更新: $inferredState');
    } catch (e) {
      Logger.e(_tag, '更新用户上下文失败: $e');
    }
  }

  /// 推断用户状态
  String _inferUserState(
      EnvironmentContext environment, ActivityContext activity) {
    try {
      // 使用边缘智能进行状态推断
      if (_edgeIntelligence != null) {
        return _edgeIntelligence.inferUserState(environment, activity);
      }

      // 回退到基础推断
      if (activity.state == ActivityState.still ||
          activity.state == ActivityState.sitting ||
          activity.state == ActivityState.standing) {
        if (environment.type == EnvironmentType.quiet) {
          return '用户可能正在休息或工作';
        } else if (environment.type == EnvironmentType.noisy) {
          return '用户可能在嘈杂环境中';
        }
      } else if (activity.state == ActivityState.walking ||
          activity.state == ActivityState.running) {
        return '用户正在进行运动';
      } else if (activity.state == ActivityState.inVehicle) {
        return '用户正在交通工具中';
      }

      return '未知状态';
    } catch (e) {
      Logger.e(_tag, '推断用户状态失败: $e');
      return '状态推断错误';
    }
  }

  /// 获取当前用户上下文
  UserContext getCurrentContext() {
    final environmentContext = EnvironmentContext(
      type: _currentEnvironment,
      lightLevel: _currentLux.toDouble(),
      noiseLevel: _currentNoiseLevel,
      location: _currentPosition != null
          ? {
              'latitude': _currentPosition!.latitude,
              'longitude': _currentPosition!.longitude,
              'accuracy': _currentPosition!.accuracy,
            }
          : null,
      timestamp: DateTime.now(),
    );

    final activityContext = ActivityContext(
      state: _currentActivity,
      confidence: _activityConfidence,
      duration: _activityDuration,
      timestamp: DateTime.now(),
    );

    final inferredState = _inferUserState(environmentContext, activityContext);

    return UserContext(
      activity: activityContext,
      environment: environmentContext,
      inferredState: inferredState,
      timestamp: DateTime.now(),
    );
  }

  /// 手动触发上下文更新
  void triggerContextUpdate() {
    _analyzeEnvironment();
    _updateUserContext();
  }

  /// 映射活动类型
  ActivityState _mapToActivityState(String activityType) {
    switch (activityType.toLowerCase()) {
      case 'still':
        return ActivityState.still;
      case 'on_foot':
      case 'walking':
        return ActivityState.walking;
      case 'running':
        return ActivityState.running;
      case 'on_bicycle':
        return ActivityState.onBicycle;
      case 'in_vehicle':
        return ActivityState.inVehicle;
      case 'tilting':
        return ActivityState.tilting;
      case 'on_stairs':
        return ActivityState.onStairs;
      case 'lying_down':
        return ActivityState.lyingDown;
      case 'sitting':
        return ActivityState.sitting;
      case 'standing':
        return ActivityState.standing;
      default:
        return ActivityState.unknown;
    }
  }

  /// 获取当前环境类型
  EnvironmentType getCurrentEnvironmentType() {
    return _currentEnvironment;
  }

  /// 获取当前活动状态
  ActivityState getCurrentActivityState() {
    return _currentActivity;
  }

  /// 获取当前光照级别
  int getCurrentLuxLevel() {
    return _currentLux;
  }

  /// 获取当前噪音级别
  double getCurrentNoiseLevel() {
    return _currentNoiseLevel;
  }

  /// 获取当前位置
  Position? getCurrentLocation() {
    return _currentPosition;
  }

  /// 检查是否正在监控
  bool isMonitoring() {
    return _isMonitoring;
  }

  /// 释放资源
  void dispose() {
    stopMonitoring();
    _contextStreamController.close();
    _contextDataController.close();
    _mockDataTimer?.cancel();
  }

  /// 获取上下文数据流
  Stream<Map<String, dynamic>> get contextDataStream => _contextDataController.stream;
  
  /// 是否正在运行
  bool get isRunning => _isRunning;
  
  /// 当前环境类型
  EnvironmentType get currentEnvironment => _currentEnvironment;
  
  /// 当前活动类型
  ActivityType get currentActivity => ActivityType.unknown;
  
  /// 开始感知
  Future<bool> startSensing() async {
    if (_isRunning) return true;
    
    try {
      // 在实际应用中，这里应该启动各种传感器的数据收集
      _isRunning = true;
      
      // 暂时使用模拟数据
      _startMockDataGeneration();
      
      debugPrint('上下文感知服务开始运行');
      return true;
    } catch (e) {
      debugPrint('启动上下文感知服务失败: $e');
      _isRunning = false;
      return false;
    }
  }
  
  /// 停止感知
  Future<void> stopSensing() async {
    if (!_isRunning) return;
    
    // 停止模拟数据生成
    _mockDataTimer?.cancel();
    _mockDataTimer = null;
    
    // 实际应用中，这里应该停止各种传感器的数据收集
    
    _isRunning = false;
    debugPrint('上下文感知服务已停止');
  }
  
  /// 获取当前上下文数据
  Map<String, dynamic> getCurrentContextData() {
    return {
      'environment': _currentEnvironment.toString().split('.').last,
      'activity': _currentActivity.toString().split('.').last,
      'lightLevel': _currentLightLevel,
      'temperature': _currentTemperature,
      'humidity': _currentHumidity,
      'noiseLevel': _currentNoiseLevel,
      'pressure': _currentPressure,
      'airQualityIndex': _currentAirQualityIndex,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    };
  }
  
  /// 开始生成模拟数据
  void _startMockDataGeneration() {
    _mockDataTimer?.cancel();
    
    // 初始化随机值
    _updateRandomValues();
    
    // 每3秒生成一次模拟数据
    _mockDataTimer = Timer.periodic(const Duration(seconds: 3), (timer) {
      _updateRandomValues();
      final data = getCurrentContextData();
      _contextDataController.add(data);
    });
  }
  
  /// 更新随机值
  void _updateRandomValues() {
    final random = Random();
    
    // 随机环境类型 (以70%的概率是室内)
    _currentEnvironment = random.nextDouble() < 0.7 
        ? EnvironmentType.indoor 
        : EnvironmentType.outdoor;
    
    // 随机活动类型 (以50%的概率是静止)
    final activityRandom = random.nextDouble();
    if (activityRandom < 0.5) {
      _currentActivity = ActivityState.still;
    } else if (activityRandom < 0.7) {
      _currentActivity = ActivityState.walking;
    } else if (activityRandom < 0.8) {
      _currentActivity = ActivityState.running;
    } else if (activityRandom < 0.9) {
      _currentActivity = ActivityState.onBicycle;
    } else {
      _currentActivity = ActivityState.inVehicle;
    }
    
    // 随机更新其他传感器数据
    _currentLightLevel = (_currentEnvironment == EnvironmentType.indoor)
        ? random.nextDouble() * 400 + 50 // 室内50-450 lux
        : random.nextDouble() * 20000 + 1000; // 室外1000-21000 lux
        
    _currentTemperature = 15 + random.nextDouble() * 20; // 15-35摄氏度
    _currentHumidity = 30 + random.nextDouble() * 50; // 30-80%
    _currentNoiseLevel = (_currentEnvironment == EnvironmentType.indoor)
        ? 30 + random.nextDouble() * 30 // 室内30-60 dB
        : 50 + random.nextDouble() * 40; // 室外50-90 dB
        
    _currentPressure = 990 + random.nextDouble() * 40; // 990-1030 hPa
    _currentAirQualityIndex = random.nextInt(150) + 20; // AQI 20-170
  }
}

/// 上下文数据Provider
final contextDataProvider = StreamProvider<Map<String, dynamic>>((ref) {
  final service = ref.watch(contextAwareSensingServiceProvider);
  
  // 确保服务正在运行
  if (!service.isRunning) {
    service.startSensing();
  }
  
  return service.contextDataStream;
});
