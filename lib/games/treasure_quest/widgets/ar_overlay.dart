import 'package:flutter/material.dart';
import '../models/player.dart';
import '../models/treasure.dart';
import 'treasure_marker.dart';
import 'ar_effect.dart';

class AROverlay extends StatelessWidget {
  final Map<String, dynamic> arData;
  final Player player;

  const AROverlay({
    Key? key,
    required this.arData,
    required this.player,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final treasures = arData['treasures'] as List<Map<String, dynamic>>;
    final effects = arData['effects'] as Map<String, dynamic>;

    return Stack(
      children: [
        // 环境效果
        ...effects['ambient'].map<Widget>((effect) => AREffect(
              type: effect,
              position: _getRandomPosition(),
            )),

        // 宝藏标记
        ...treasures.map((treasure) {
          final position = _calculateMarkerPosition(
            treasure['bearing'] as double,
            treasure['distance'] as double,
          );

          return Positioned(
            left: position.dx,
            top: position.dy,
            child: TreasureMarker(
              treasure: Treasure.fromJson(treasure['treasure']),
              distance: treasure['distance'],
              bearing: treasure['bearing'],
              player: player,
            ),
          );
        }),

        // 指引效果
        if (treasures.isNotEmpty)
          ...effects['guidance'].map<Widget>((effect) => AREffect(
                type: effect,
                position: _calculateGuidancePosition(
                  treasures.first['bearing'] as double,
                ),
              )),

        // 发现效果
        ...effects['discovery'].map<Widget>((effect) => AREffect(
              type: effect,
              position: _getRandomPosition(),
            )),

        // 指南针
        Positioned(
          top: 100,
          left: 0,
          right: 0,
          child: Center(
            child: Transform.rotate(
              angle: (arData['bearing'] as double) * 3.14159 / 180,
              child: const Icon(
                Icons.navigation,
                color: Colors.white,
                size: 40,
              ),
            ),
          ),
        ),

        // 环境信息
        Positioned(
          top: MediaQuery.of(context).padding.top + 60,
          left: 16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '海拔: ${arData['location']['altitude']?.toStringAsFixed(1)}米',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  shadows: [
                    Shadow(
                      blurRadius: 4,
                      color: Colors.black,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 4),
              Text(
                '方向: ${_formatBearing(arData['bearing'])}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  shadows: [
                    Shadow(
                      blurRadius: 4,
                      color: Colors.black,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // 计算标记位置
  Offset _calculateMarkerPosition(double bearing, double distance) {
    // 这里需要根据设备方向和距离计算实际的屏幕位置
    // 这是一个简化的示例
    final screenWidth = WidgetsBinding.instance.window.physicalSize.width /
        WidgetsBinding.instance.window.devicePixelRatio;
    final screenHeight = WidgetsBinding.instance.window.physicalSize.height /
        WidgetsBinding.instance.window.devicePixelRatio;

    final angle = bearing * 3.14159 / 180;
    final x = screenWidth / 2 + cos(angle) * distance;
    final y = screenHeight / 2 - sin(angle) * distance;

    return Offset(x, y);
  }

  // 计算指引效果位置
  Offset _calculateGuidancePosition(double bearing) {
    // 简化的位置计算
    final screenWidth = WidgetsBinding.instance.window.physicalSize.width /
        WidgetsBinding.instance.window.devicePixelRatio;
    final screenHeight = WidgetsBinding.instance.window.physicalSize.height /
        WidgetsBinding.instance.window.devicePixelRatio;

    return Offset(screenWidth / 2, screenHeight / 2);
  }

  // 获取随机位置
  Offset _getRandomPosition() {
    final random = Random();
    final screenWidth = WidgetsBinding.instance.window.physicalSize.width /
        WidgetsBinding.instance.window.devicePixelRatio;
    final screenHeight = WidgetsBinding.instance.window.physicalSize.height /
        WidgetsBinding.instance.window.devicePixelRatio;

    return Offset(
      random.nextDouble() * screenWidth,
      random.nextDouble() * screenHeight,
    );
  }

  // 格式化方位角
  String _formatBearing(double bearing) {
    const directions = ['北', '东北', '东', '东南', '南', '西南', '西', '西北'];
    final index = ((bearing + 22.5) % 360 / 45).floor();
    return directions[index];
  }
} 