import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:get/get.dart';
import 'dart:math' as math;
import 'widgets/treasure_radar.dart';
import 'widgets/ar_overlay.dart';
import 'widgets/map_view.dart';
import 'models/location.dart' as app_location;

class ExplorePage extends StatefulWidget {
  const ExplorePage({Key? key}) : super(key: key);

  @override
  State<ExplorePage> createState() => _ExplorePageState();
}

class _ExplorePageState extends State<ExplorePage> {
  bool _isARMode = false;
  List<Map<String, dynamic>> _markers = [];
  Position? _currentPosition;
  
  // 昆明市中心坐标
  static const _defaultLocation = app_location.LatLng(24.8801, 102.8329);

  @override
  void initState() {
    super.initState();
    _checkPermissions();
  }

  Future<void> _checkPermissions() async {
    // 检查位置权限
    final locationStatus = await Permission.location.request();
    if (locationStatus.isGranted) {
      _startLocationUpdates();
    } else {
      // 显示提示并引导用户去设置
      Get.snackbar(
        '需要位置权限',
        '请在设置中开启位置权限以使用地图功能',
        snackPosition: SnackPosition.BOTTOM,
        duration: const Duration(seconds: 5),
        backgroundColor: Colors.black87,
        colorText: Colors.white,
        mainButton: TextButton(
          onPressed: () => openAppSettings(),
          child: const Text(
            '去设置',
            style: TextStyle(color: Colors.blue),
          ),
        ),
      );
    }

    if (_isARMode) {
      final cameraStatus = await Permission.camera.request();
      if (!cameraStatus.isGranted) {
        setState(() => _isARMode = false);
        // 显示相机权限提示
        Get.snackbar(
          '需要相机权限',
          '请在设置中开启相机权限以使用AR功能',
          snackPosition: SnackPosition.BOTTOM,
          duration: const Duration(seconds: 5),
          backgroundColor: Colors.black87,
          colorText: Colors.white,
          mainButton: TextButton(
            onPressed: () => openAppSettings(),
            child: const Text(
              '去设置',
              style: TextStyle(color: Colors.blue),
            ),
          ),
        );
      }
    }
  }

  void _startLocationUpdates() async {
    try {
      // 检查位置服务是否开启
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        Get.snackbar(
          '位置服务未开启',
          '请开启设备的位置服务以使用地图功能',
          snackPosition: SnackPosition.BOTTOM,
          duration: const Duration(seconds: 5),
          backgroundColor: Colors.black87,
          colorText: Colors.white,
        );
        return;
      }

      final position = await Geolocator.getCurrentPosition();
      setState(() {
        _currentPosition = position;
        _updateMarkers();
      });
      
      // 监听位置更新
      Geolocator.getPositionStream().listen((Position position) {
        setState(() {
          _currentPosition = position;
          _updateMarkers();
        });
      });
    } catch (e) {
      Get.snackbar(
        '位置获取失败',
        '无法获取您的位置信息，请检查权限设置',
        snackPosition: SnackPosition.BOTTOM,
        duration: const Duration(seconds: 5),
        backgroundColor: Colors.black87,
        colorText: Colors.white,
      );
    }
  }

  void _updateMarkers() {
    if (_currentPosition == null) return;

    // 模拟附近的宝藏点
    final treasures = [
      _generateTreasure(0.001, 0.001, '翡翠湖公园的宝藏'),
      _generateTreasure(-0.001, 0.002, '圆通山的秘密'),
      _generateTreasure(0.002, -0.001, '金马碧鸡坊的传说'),
    ];

    setState(() {
      _markers = treasures.map((treasure) => {
        'latitude': treasure.location.latitude,
        'longitude': treasure.location.longitude,
        'title': treasure.title,
      }).toList();
    });
  }

  TreasureSpot _generateTreasure(double latOffset, double lngOffset, String title) {
    return TreasureSpot(
      location: app_location.LatLng(
        _currentPosition!.latitude + latOffset,
        _currentPosition!.longitude + lngOffset,
      ),
      title: title,
    );
  }

  void _onTreasureSelected(TreasureSpot treasure) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              treasure.title,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              '距离: ${_calculateDistance(treasure.location)}米',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => _startTreasureHunt(treasure),
              child: const Text('开始寻宝'),
            ),
          ],
        ),
      ),
    );
  }

  double _calculateDistance(app_location.LatLng treasureLocation) {
    if (_currentPosition == null) return 0;
    
    return Geolocator.distanceBetween(
      _currentPosition!.latitude,
      _currentPosition!.longitude,
      treasureLocation.latitude,
      treasureLocation.longitude,
    );
  }

  void _startTreasureHunt(TreasureSpot treasure) {
    Navigator.pop(context);
    setState(() => _isARMode = true);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('老克寻宝记'),
        actions: [
          IconButton(
            icon: const Icon(Icons.leaderboard),
            onPressed: () => Get.toNamed(RoutePaths.gameLeaderboard),
            tooltip: '排行榜',
          ),
        ],
      ),
      body: Stack(
        children: [
          // 地图层
          MapView(
            latitude: _currentPosition?.latitude ?? _defaultLocation.latitude,
            longitude: _currentPosition?.longitude ?? _defaultLocation.longitude,
            markers: _markers,
          ),

          // AR 覆盖层
          if (_isARMode) const AROverlay(),

          // 雷达
          if (_currentPosition != null)
            Positioned(
              right: 16,
              bottom: 100,
              child: TreasureRadar(
                treasures: _markers,
              ),
            ),

          // 控制按钮
          Positioned(
            right: 16,
            bottom: 16,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                FloatingActionButton(
                  heroTag: 'location',
                  onPressed: _startLocationUpdates,
                  child: const Icon(Icons.my_location),
                ),
                const SizedBox(height: 8),
                FloatingActionButton(
                  heroTag: 'ar',
                  onPressed: () {
                    setState(() => _isARMode = !_isARMode);
                    if (_isARMode) {
                      _checkPermissions();
                    }
                  },
                  child: Icon(_isARMode ? Icons.map : Icons.view_in_ar),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class TreasureSpot {
  final app_location.LatLng location;
  final String title;

  TreasureSpot({
    required this.location,
    required this.title,
  });
} 