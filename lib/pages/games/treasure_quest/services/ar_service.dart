import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:math' as math;

class ARService {
  static final ARService _instance = ARService._internal();
  factory ARService() => _instance;
  ARService._internal();

  // 计算两点之间的距离（米）
  double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2);
  }

  // 计算方位角（度数）
  double calculateBearing(double lat1, double lon1, double lat2, double lon2) {
    var dLon = (lon2 - lon1);
    var y = math.sin(dLon) * math.cos(lat2);
    var x = math.cos(lat1) * math.sin(lat2) -
        math.sin(lat1) * math.cos(lat2) * math.cos(dLon);
    var bearing = math.atan2(y, x);
    bearing = bearing * 180 / math.pi; // 转换为度数
    bearing = (bearing + 360) % 360; // 标准化到 0-360
    return bearing;
  }

  // 获取当前位置
  Future<Position> getCurrentLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Location services are disabled.');
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permissions are denied');
      }
    }
    
    if (permission == LocationPermission.deniedForever) {
      throw Exception('Location permissions are permanently denied');
    }

    return await Geolocator.getCurrentPosition();
  }

  // 计算物体在屏幕上的位置
  Offset calculateScreenPosition(double bearing, double deviceBearing, Size screenSize) {
    // 计算相对角度
    double relativeBearing = (bearing - deviceBearing + 360) % 360;
    
    // 将角度转换为屏幕坐标
    double screenX = screenSize.width * (relativeBearing / 360);
    double screenY = screenSize.height / 2; // 保持在屏幕中间高度
    
    return Offset(screenX, screenY);
  }

  // 检查物体是否在视野范围内
  bool isInFieldOfView(double bearing, double deviceBearing, {double fieldOfView = 60}) {
    double relativeBearing = (bearing - deviceBearing + 360) % 360;
    return relativeBearing <= fieldOfView / 2 || relativeBearing >= (360 - fieldOfView / 2);
  }
} 