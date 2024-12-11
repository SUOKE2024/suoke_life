import 'package:flutter/material.dart';
import 'package:camera/camera.dart';

class AROverlay extends StatefulWidget {
  const AROverlay({Key? key}) : super(key: key);

  @override
  State<AROverlay> createState() => _AROverlayState();
}

class _AROverlayState extends State<AROverlay> {
  CameraController? _controller;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) return;

      _controller = CameraController(
        cameras.first,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _controller!.initialize();
      if (mounted) {
        setState(() => _isInitialized = true);
      }
    } catch (e) {
      debugPrint('相机初始化失败: $e');
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized || _controller == null) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    return Stack(
      children: [
        // 相机预览
        CameraPreview(_controller!),

        // AR UI 覆盖层
        CustomPaint(
          painter: ARGuidelinePainter(),
          child: Container(),
        ),

        // AR 信息显示
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // AR 模式提示
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.black54,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.view_in_ar,
                        color: Colors.white,
                        size: 16,
                      ),
                      SizedBox(width: 8),
                      Text(
                        'AR 探索模式',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

                const Spacer(),

                // 底部提示
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.black54,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '探索提示',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        '1. 环顾四周，寻找闪烁的宝藏标记\n'
                        '2. 靠近标记位置，可能触发特殊事件\n'
                        '3. 注意周围环境，确保安全',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class ARGuidelinePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;

    // 绘制网格线
    const gridSize = 50.0;
    for (var i = 0; i < size.width.toInt(); i += gridSize.toInt()) {
      canvas.drawLine(
        Offset(i.toDouble(), 0),
        Offset(i.toDouble(), size.height),
        paint,
      );
    }
    for (var i = 0; i < size.height.toInt(); i += gridSize.toInt()) {
      canvas.drawLine(
        Offset(0, i.toDouble()),
        Offset(size.width, i.toDouble()),
        paint,
      );
    }

    // 绘制中心十字准星
    final centerX = size.width / 2;
    final centerY = size.height / 2;
    const crosshairSize = 20.0;

    canvas.drawLine(
      Offset(centerX - crosshairSize, centerY),
      Offset(centerX + crosshairSize, centerY),
      paint,
    );
    canvas.drawLine(
      Offset(centerX, centerY - crosshairSize),
      Offset(centerX, centerY + crosshairSize),
      paint,
    );
  }

  @override
  bool shouldRepaint(ARGuidelinePainter oldDelegate) => false;
} 