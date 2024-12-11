import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:vector_math/vector_math.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:latlong2/latlong.dart';
import '../models/treasure.dart';
import '../models/game_config.dart';

class ARService {
  // 单例模式
  static final ARService _instance = ARService._internal();
  factory ARService() => _instance;
  ARService._internal();

  // 流控制器
  final _locationController = StreamController<Position>.broadcast();
  final _compassController = StreamController<double>.broadcast();
  final _arViewController = StreamController<Map<String, dynamic>>.broadcast();

  // 传感器数据
  StreamSubscription? _accelerometerSubscription;
  StreamSubscription? _magnetometerSubscription;
  StreamSubscription? _gyroscopeSubscription;
  StreamSubscription? _locationSubscription;

  // AR状态
  bool _isInitialized = false;
  Position? _currentLocation;
  double _currentBearing = 0.0;
  final Map<String, Treasure> _trackedTreasures = {};

  // 初始化AR服务
  Future<bool> initialize() async {
    if (_isInitialized) return true;

    try {
      // 检查位置权限
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('Location services are disabled.');
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw Exception('Location permissions are denied');
        }
      }

      // 初始化传感器
      _initializeSensors();
      
      // 开始位置追踪
      _startLocationTracking();

      _isInitialized = true;
      return true;
    } catch (e) {
      debugPrint('AR Service initialization failed: $e');
      return false;
    }
  }

  // 初始化传感器
  void _initializeSensors() {
    // 加速度计
    _accelerometerSubscription = accelerometerEvents.listen((event) {
      // 处理加速度数据，用于设备姿态检测
      _updateDeviceOrientation(event);
    });

    // 磁力计
    _magnetometerSubscription = magnetometerEvents.listen((event) {
      // 处理磁力计数据，用于指南针功能
      _updateCompassHeading(event);
    });

    // 陀螺仪
    _gyroscopeSubscription = gyroscopeEvents.listen((event) {
      // 处理陀螺仪数据，用于设备旋转检测
      _updateDeviceRotation(event);
    });
  }

  // 开始位置追踪
  void _startLocationTracking() {
    _locationSubscription = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 5, // 5米更新一次
      ),
    ).listen((Position position) {
      _currentLocation = position;
      _locationController.add(position);
      _updateARView();
    });
  }

  // 更新设备方向
  void _updateDeviceOrientation(AccelerometerEvent event) {
    // 使用加速度计数据计算设备倾斜角度
    double pitch = (event.y / 9.81).clamp(-1.0, 1.0);
    double roll = (event.x / 9.81).clamp(-1.0, 1.0);
    
    // 更新AR视图
    _updateARView();
  }

  // 更新指南针方向
  void _updateCompassHeading(MagnetometerEvent event) {
    // 计算设备朝向
    _currentBearing = degrees(atan2(event.y, event.x));
    _compassController.add(_currentBearing);
    
    // 更新AR视图
    _updateARView();
  }

  // 更新设备旋转
  void _updateDeviceRotation(GyroscopeEvent event) {
    // 处理设备旋转数据
    // 用于平滑AR效果
    _updateARView();
  }

  // 更新AR视图
  void _updateARView() {
    if (_currentLocation == null) return;

    final arData = <String, dynamic>{
      'location': _currentLocation!.toJson(),
      'bearing': _currentBearing,
      'treasures': _getVisibleTreasures(),
      'effects': _getActiveEffects(),
    };

    _arViewController.add(arData);
  }

  // 获取可见的宝藏
  List<Map<String, dynamic>> _getVisibleTreasures() {
    if (_currentLocation == null) return [];

    final visibleTreasures = <Map<String, dynamic>>[];
    final currentLatLng = LatLng(
      _currentLocation!.latitude,
      _currentLocation!.longitude,
    );

    _trackedTreasures.forEach((id, treasure) {
      final distance = treasure.calculateDistance(currentLatLng);
      if (distance <= GameConfig.arConfig['minAccuracy']) {
        visibleTreasures.add({
          'treasure': treasure.toJson(),
          'distance': distance,
          'bearing': _calculateBearing(currentLatLng, treasure.location),
        });
      }
    });

    return visibleTreasures;
  }

  // 计算方位角
  double _calculateBearing(LatLng from, LatLng to) {
    final distance = Distance();
    return distance.bearing(from, to);
  }

  // 获取当前激活的特效
  Map<String, dynamic> _getActiveEffects() {
    return {
      'discovery': GameConfig.arConfig['effects']['discovery'],
      'guidance': GameConfig.arConfig['effects']['guidance'],
      'ambient': GameConfig.arConfig['effects']['ambient'],
    };
  }

  // 添加追踪宝藏
  void trackTreasure(Treasure treasure) {
    _trackedTreasures[treasure.id] = treasure;
    _updateARView();
  }

  // 移除追踪宝藏
  void untrackTreasure(String treasureId) {
    _trackedTreasures.remove(treasureId);
    _updateARView();
  }

  // 获取AR视图流
  Stream<Map<String, dynamic>> get arView => _arViewController.stream;

  // 获取位置流
  Stream<Position> get locationStream => _locationController.stream;

  // 获取指南针流
  Stream<double> get compassStream => _compassController.stream;

  // 释放资源
  void dispose() {
    _accelerometerSubscription?.cancel();
    _magnetometerSubscription?.cancel();
    _gyroscopeSubscription?.cancel();
    _locationSubscription?.cancel();
    _locationController.close();
    _compassController.close();
    _arViewController.close();
  }
} 