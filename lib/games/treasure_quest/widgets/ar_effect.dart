import 'package:flutter/material.dart';
import 'dart:math' as math;

class AREffect extends StatefulWidget {
  final String type;
  final Offset position;

  const AREffect({
    Key? key,
    required this.type,
    required this.position,
  }) : super(key: key);

  @override
  State<AREffect> createState() => _AREffectState();
}

class _AREffectState extends State<AREffect> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: _getEffectDuration(),
      vsync: this,
    );

    _animation = _createAnimation();
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Duration _getEffectDuration() {
    switch (widget.type) {
      case '光芒四射':
        return const Duration(milliseconds: 1500);
      case '金币飞舞':
        return const Duration(milliseconds: 2000);
      case '烟花绽放':
        return const Duration(milliseconds: 2500);
      case '路径指引':
        return const Duration(milliseconds: 3000);
      case '区域提示':
        return const Duration(milliseconds: 2000);
      case '方向标记':
        return const Duration(milliseconds: 1500);
      case '自然音效':
        return const Duration(milliseconds: 3000);
      case '氛围光效':
        return const Duration(milliseconds: 4000);
      case '天气特效':
        return const Duration(milliseconds: 5000);
      default:
        return const Duration(milliseconds: 2000);
    }
  }

  Animation<double> _createAnimation() {
    switch (widget.type) {
      case '光芒四射':
        return Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _controller,
            curve: Curves.easeOut,
          ),
        );
      case '金币飞舞':
        return Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _controller,
            curve: Curves.elasticOut,
          ),
        );
      case '烟花绽放':
        return Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _controller,
            curve: Curves.easeInOutBack,
          ),
        );
      default:
        return Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _controller,
            curve: Curves.linear,
          ),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: widget.position.dx,
      top: widget.position.dy,
      child: AnimatedBuilder(
        animation: _animation,
        builder: (context, child) {
          return _buildEffect();
        },
      ),
    );
  }

  Widget _buildEffect() {
    switch (widget.type) {
      case '光芒四射':
        return _buildRadiantEffect();
      case '金币飞舞':
        return _buildCoinEffect();
      case '烟花绽放':
        return _buildFireworkEffect();
      case '路径指引':
        return _buildPathEffect();
      case '区域提示':
        return _buildAreaEffect();
      case '方向标记':
        return _buildDirectionEffect();
      case '自然音效':
        return _buildSoundEffect();
      case '氛围光效':
        return _buildAmbientEffect();
      case '天气特效':
        return _buildWeatherEffect();
      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildRadiantEffect() {
    return Transform.scale(
      scale: _animation.value,
      child: Container(
        width: 100,
        height: 100,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [
              Colors.yellow.withOpacity(1.0 - _animation.value),
              Colors.yellow.withOpacity(0.0),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCoinEffect() {
    return Transform.rotate(
      angle: _animation.value * 2 * math.pi,
      child: Transform.scale(
        scale: math.sin(_animation.value * math.pi),
        child: Icon(
          Icons.monetization_on,
          size: 40,
          color: Colors.amber.withOpacity(1.0 - _animation.value),
        ),
      ),
    );
  }

  Widget _buildFireworkEffect() {
    return CustomPaint(
      size: const Size(200, 200),
      painter: FireworkPainter(
        progress: _animation.value,
        color: Colors.purple,
      ),
    );
  }

  Widget _buildPathEffect() {
    return CustomPaint(
      size: const Size(100, 100),
      painter: PathPainter(
        progress: _animation.value,
        color: Colors.blue,
      ),
    );
  }

  Widget _buildAreaEffect() {
    return Container(
      width: 150,
      height: 150,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: Colors.green.withOpacity(_animation.value),
          width: 2,
        ),
      ),
    );
  }

  Widget _buildDirectionEffect() {
    return Transform.rotate(
      angle: _animation.value * math.pi,
      child: Icon(
        Icons.arrow_forward,
        size: 40,
        color: Colors.white.withOpacity(1.0 - _animation.value),
      ),
    );
  }

  Widget _buildSoundEffect() {
    return CustomPaint(
      size: const Size(100, 100),
      painter: SoundWavePainter(
        progress: _animation.value,
        color: Colors.white,
      ),
    );
  }

  Widget _buildAmbientEffect() {
    return Container(
      width: 200,
      height: 200,
      decoration: BoxDecoration(
        gradient: RadialGradient(
          colors: [
            Colors.blue.withOpacity(0.3 * (1.0 - _animation.value)),
            Colors.transparent,
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherEffect() {
    return CustomPaint(
      size: const Size(300, 300),
      painter: WeatherPainter(
        progress: _animation.value,
        type: 'rain', // 可以根据实际天气改变
      ),
    );
  }
}

// 烟花效果画笔
class FireworkPainter extends CustomPainter {
  final double progress;
  final Color color;

  FireworkPainter({
    required this.progress,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(1.0 - progress)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 * progress;

    for (var i = 0; i < 12; i++) {
      final angle = i * math.pi / 6;
      final x = center.dx + radius * math.cos(angle);
      final y = center.dy + radius * math.sin(angle);
      canvas.drawLine(center, Offset(x, y), paint);
    }
  }

  @override
  bool shouldRepaint(FireworkPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

// 路径效果画笔
class PathPainter extends CustomPainter {
  final double progress;
  final Color color;

  PathPainter({
    required this.progress,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(1.0 - progress)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    final path = Path()
      ..moveTo(0, size.height / 2)
      ..quadraticBezierTo(
        size.width / 2,
        0,
        size.width,
        size.height / 2,
      );

    final pathMetrics = path.computeMetrics().first;
    final extractPath = pathMetrics.extractPath(
      0,
      pathMetrics.length * progress,
    );

    canvas.drawPath(extractPath, paint);
  }

  @override
  bool shouldRepaint(PathPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

// 声波效果画笔
class SoundWavePainter extends CustomPainter {
  final double progress;
  final Color color;

  SoundWavePainter({
    required this.progress,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(1.0 - progress)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final center = Offset(size.width / 2, size.height / 2);
    final maxRadius = size.width / 2;

    for (var i = 0; i < 3; i++) {
      final radius = maxRadius * (progress + i * 0.2) % 1.0;
      canvas.drawCircle(center, radius * maxRadius, paint);
    }
  }

  @override
  bool shouldRepaint(SoundWavePainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

// 天气效果画笔
class WeatherPainter extends CustomPainter {
  final double progress;
  final String type;

  WeatherPainter({
    required this.progress,
    required this.type,
  });

  @override
  void paint(Canvas canvas, Size size) {
    switch (type) {
      case 'rain':
        _paintRain(canvas, size);
        break;
      case 'snow':
        _paintSnow(canvas, size);
        break;
      case 'fog':
        _paintFog(canvas, size);
        break;
    }
  }

  void _paintRain(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue.withOpacity(0.6)
      ..strokeWidth = 1;

    final random = math.Random(42);
    for (var i = 0; i < 100; i++) {
      final x = random.nextDouble() * size.width;
      final y = (progress + random.nextDouble()) * size.height % size.height;
      canvas.drawLine(
        Offset(x, y),
        Offset(x - 5, y + 10),
        paint,
      );
    }
  }

  void _paintSnow(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.8)
      ..style = PaintingStyle.fill;

    final random = math.Random(42);
    for (var i = 0; i < 50; i++) {
      final x = random.nextDouble() * size.width;
      final y = (progress + random.nextDouble()) * size.height % size.height;
      canvas.drawCircle(Offset(x, y), 2, paint);
    }
  }

  void _paintFog(Canvas canvas, Size size) {
    final paint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Colors.white.withOpacity(0.3),
          Colors.white.withOpacity(0.0),
        ],
      ).createShader(Offset.zero & size);

    canvas.drawRect(Offset.zero & size, paint);
  }

  @override
  bool shouldRepaint(WeatherPainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.type != type;
  }
} 