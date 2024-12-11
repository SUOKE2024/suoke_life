import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../models/player.dart';
import '../services/ar_service.dart';

class TreasureRadar extends StatefulWidget {
  final double bearing;
  final Player player;
  final ARService arService;

  const TreasureRadar({
    Key? key,
    required this.bearing,
    required this.player,
    required this.arService,
  }) : super(key: key);

  @override
  State<TreasureRadar> createState() => _TreasureRadarState();
}

class _TreasureRadarState extends State<TreasureRadar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _animation = Tween<double>(
      begin: 0.0,
      end: 2 * math.pi,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.linear,
    ));

    _controller.repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _toggleRadarSize,
      child: StreamBuilder<Map<String, dynamic>>(
        stream: widget.arService.arView,
        builder: (context, snapshot) {
          final treasures = snapshot.data?['treasures'] as List<Map<String, dynamic>>? ?? [];
          
          return Container(
            width: 150,
            height: 150,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.7),
              shape: BoxShape.circle,
              border: Border.all(
                color: Colors.green.withOpacity(0.5),
                width: 2,
              ),
            ),
            child: Stack(
              children: [
                // 雷达背景
                _buildRadarBackground(),

                // 扫描动画
                AnimatedBuilder(
                  animation: _animation,
                  builder: (context, child) {
                    return _buildScanLine();
                  },
                ),

                // 宝藏标记
                ...treasures.map((treasure) => _buildTreasureMarker(treasure)),

                // 中心点
                Center(
                  child: Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Colors.green,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),

                // 指北针
                Transform.rotate(
                  angle: -widget.bearing * math.pi / 180,
                  child: const Align(
                    alignment: Alignment.topCenter,
                    child: Padding(
                      padding: EdgeInsets.only(top: 4),
                      child: Icon(
                        Icons.navigation,
                        color: Colors.red,
                        size: 20,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  // 雷达背景
  Widget _buildRadarBackground() {
    return CustomPaint(
      size: const Size(150, 150),
      painter: RadarBackgroundPainter(),
    );
  }

  // 扫描线
  Widget _buildScanLine() {
    return CustomPaint(
      size: const Size(150, 150),
      painter: RadarScanPainter(
        angle: _animation.value,
      ),
    );
  }

  // 宝藏标记
  Widget _buildTreasureMarker(Map<String, dynamic> treasure) {
    final distance = treasure['distance'] as double;
    final bearing = treasure['bearing'] as double;
    final maxDistance = 100.0; // 雷达最大探测范围（米）

    // 计算标记在雷达上的位置
    final radius = (distance / maxDistance) * 67; // 67是雷达半径（150/2 - 8）
    final angle = (bearing - widget.bearing) * math.pi / 180;
    final dx = radius * math.sin(angle);
    final dy = -radius * math.cos(angle);

    return Positioned(
      left: 67 + dx,
      top: 67 + dy,
      child: Container(
        width: 8,
        height: 8,
        decoration: BoxDecoration(
          color: _getTreasureColor(treasure['treasure']['rarity']),
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: _getTreasureColor(treasure['treasure']['rarity'])
                  .withOpacity(0.5),
              blurRadius: 4,
              spreadRadius: 2,
            ),
          ],
        ),
      ),
    );
  }

  // 获取宝藏颜色
  Color _getTreasureColor(String rarity) {
    switch (rarity) {
      case 'common':
        return Colors.grey;
      case 'rare':
        return Colors.blue;
      case 'epic':
        return Colors.purple;
      case 'legendary':
        return Colors.orange;
      default:
        return Colors.white;
    }
  }

  // 切换雷达大小
  void _toggleRadarSize() {
    // TODO: 实现雷达大小切换动画
  }
}

// 雷达背景画笔
class RadarBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 8;
    final paint = Paint()
      ..color = Colors.green.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // 绘制同心圆
    for (var i = 1; i <= 3; i++) {
      canvas.drawCircle(
        center,
        radius * i / 3,
        paint,
      );
    }

    // 绘制十字线
    canvas.drawLine(
      Offset(center.dx, center.dy - radius),
      Offset(center.dx, center.dy + radius),
      paint,
    );
    canvas.drawLine(
      Offset(center.dx - radius, center.dy),
      Offset(center.dx + radius, center.dy),
      paint,
    );
  }

  @override
  bool shouldRepaint(RadarBackgroundPainter oldDelegate) => false;
}

// 雷达扫描线画笔
class RadarScanPainter extends CustomPainter {
  final double angle;

  RadarScanPainter({required this.angle});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 8;
    final rect = Rect.fromCircle(center: center, radius: radius);

    final gradient = SweepGradient(
      colors: [
        Colors.green.withOpacity(0.0),
        Colors.green.withOpacity(0.5),
      ],
      stops: const [0.0, 1.0],
      startAngle: 0,
      endAngle: math.pi / 12,
      transform: GradientRotation(angle),
    );

    final paint = Paint()
      ..shader = gradient.createShader(rect)
      ..style = PaintingStyle.fill;

    canvas.drawCircle(center, radius, paint);
  }

  @override
  bool shouldRepaint(RadarScanPainter oldDelegate) {
    return oldDelegate.angle != angle;
  }
} 