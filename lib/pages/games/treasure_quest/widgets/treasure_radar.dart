import 'dart:async';
import 'package:flutter/material.dart';
import '../services/ar_service.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:math' as math;

class TreasureRadar extends StatefulWidget {
  final List<Map<String, dynamic>> treasures;
  
  const TreasureRadar({
    Key? key,
    required this.treasures,
  }) : super(key: key);

  @override
  State<TreasureRadar> createState() => _TreasureRadarState();
}

class _TreasureRadarState extends State<TreasureRadar> {
  final ARService _arService = ARService();
  Position? _currentPosition;
  Timer? _locationTimer;
  List<Map<String, dynamic>> _nearbyTreasures = [];
  
  @override
  void initState() {
    super.initState();
    _startLocationUpdates();
  }

  @override
  void dispose() {
    _locationTimer?.cancel();
    super.dispose();
  }

  void _startLocationUpdates() {
    // 每5秒更新一次位置
    _locationTimer = Timer.periodic(const Duration(seconds: 5), (timer) async {
      try {
        final position = await _arService.getCurrentLocation();
        setState(() {
          _currentPosition = position;
          _updateNearbyTreasures();
        });
      } catch (e) {
        debugPrint('Error getting location: $e');
      }
    });
    
    // 立即获取第一次位置
    _arService.getCurrentLocation().then((position) {
      setState(() {
        _currentPosition = position;
        _updateNearbyTreasures();
      });
    }).catchError((e) {
      debugPrint('Error getting initial location: $e');
    });
  }

  void _updateNearbyTreasures() {
    if (_currentPosition == null) return;
    
    _nearbyTreasures = widget.treasures.where((treasure) {
      final distance = _arService.calculateDistance(
        _currentPosition!.latitude,
        _currentPosition!.longitude,
        treasure['latitude'] as double,
        treasure['longitude'] as double,
      );
      return distance <= 1000; // 1公里范围内的宝藏
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    if (_currentPosition == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return CustomPaint(
      painter: RadarPainter(
        currentPosition: _currentPosition!,
        treasures: _nearbyTreasures,
        arService: _arService,
      ),
      child: Container(),
    );
  }
}

class RadarPainter extends CustomPainter {
  final Position currentPosition;
  final List<Map<String, dynamic>> treasures;
  final ARService arService;

  RadarPainter({
    required this.currentPosition,
    required this.treasures,
    required this.arService,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width < size.height ? size.width / 2 : size.height / 2;

    // 绘制雷达背景
    final bgPaint = Paint()
      ..color = Colors.black.withOpacity(0.1)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, radius, bgPaint);

    // 绘制雷达圈
    final circlePaint = Paint()
      ..color = Colors.green
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    for (var i = 1; i <= 3; i++) {
      canvas.drawCircle(center, radius * i / 3, circlePaint);
    }

    // 绘制宝藏点
    final treasurePaint = Paint()
      ..color = Colors.red
      ..style = PaintingStyle.fill;

    for (var treasure in treasures) {
      final distance = arService.calculateDistance(
        currentPosition.latitude,
        currentPosition.longitude,
        treasure['latitude'] as double,
        treasure['longitude'] as double,
      );

      final bearing = arService.calculateBearing(
        currentPosition.latitude,
        currentPosition.longitude,
        treasure['latitude'] as double,
        treasure['longitude'] as double,
      );

      // 将距离映射到雷达范围内
      final mappedDistance = (distance / 1000) * radius; // 1000米映射到整个雷达范围
      if (mappedDistance <= radius) {
        final angle = bearing * math.pi / 180;
        final x = center.dx + mappedDistance * math.cos(angle);
        final y = center.dy + mappedDistance * math.sin(angle);
        canvas.drawCircle(Offset(x, y), 5, treasurePaint);
      }
    }
  }

  @override
  bool shouldRepaint(RadarPainter oldDelegate) => true;
} 