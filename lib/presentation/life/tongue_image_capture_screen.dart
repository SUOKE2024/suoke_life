import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';
import 'package:suoke_life/domain/models/tongue_analysis_model.dart';
import 'package:suoke_life/presentation/life/tongue_analysis_result_screen.dart';
import 'package:suoke_life/presentation/widgets/loading_overlay.dart';

/// 舌象采集页面
class TongueImageCaptureScreen extends ConsumerStatefulWidget {
  /// 构造函数
  const TongueImageCaptureScreen({super.key});

  @override
  ConsumerState<TongueImageCaptureScreen> createState() => _TongueImageCaptureScreenState();
}

class _TongueImageCaptureScreenState extends ConsumerState<TongueImageCaptureScreen> {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  bool _isCameraInitialized = false;
  bool _isCapturing = false;
  bool _isFlashOn = false;
  bool _showOverlay = true;
  
  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }
  
  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
  
  /// 初始化相机
  Future<void> _initializeCamera() async {
    try {
      // 获取可用相机列表
      _cameras = await availableCameras();
      
      if (_cameras == null || _cameras!.isEmpty) {
        _showCameraError('未检测到相机设备');
        return;
      }
      
      // 选择后置相机
      final rearCamera = _cameras!.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.back,
        orElse: () => _cameras!.first,
      );
      
      // 初始化相机控制器
      _controller = CameraController(
        rearCamera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );
      
      // 初始化控制器
      await _controller!.initialize();
      
      if (mounted) {
        setState(() {
          _isCameraInitialized = true;
        });
      }
    } catch (e) {
      _showCameraError('相机初始化失败: $e');
    }
  }
  
  /// 显示相机错误
  void _showCameraError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  /// 切换闪光灯
  void _toggleFlash() {
    if (_controller != null && _controller!.value.isInitialized) {
      setState(() {
        _isFlashOn = !_isFlashOn;
        _controller!.setFlashMode(
          _isFlashOn ? FlashMode.torch : FlashMode.off,
        );
      });
    }
  }
  
  /// 切换辅助叠加层
  void _toggleOverlay() {
    setState(() {
      _showOverlay = !_showOverlay;
    });
  }
  
  /// 拍摄舌象照片
  Future<void> _takePicture() async {
    if (_controller == null || !_controller!.value.isInitialized) {
      _showCameraError('相机未初始化');
      return;
    }
    
    if (_isCapturing) {
      return;
    }
    
    try {
      setState(() {
        _isCapturing = true;
      });
      
      // 拍照
      final XFile picture = await _controller!.takePicture();
      
      // 获取图片存储路径
      final directory = await getApplicationDocumentsDirectory();
      final fileName = '${DateTime.now().millisecondsSinceEpoch}.jpg';
      final savedImagePath = path.join(directory.path, 'tongue_images', fileName);
      
      // 确保目录存在
      final imageDir = Directory(path.dirname(savedImagePath));
      if (!await imageDir.exists()) {
        await imageDir.create(recursive: true);
      }
      
      // 保存图片
      await File(picture.path).copy(savedImagePath);
      
      if (mounted) {
        // 导航到结果页面
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => TongueAnalysisResultScreen(
              imagePath: savedImagePath,
            ),
          ),
        );
      }
    } catch (e) {
      _showCameraError('拍照失败: $e');
    } finally {
      if (mounted) {
        setState(() {
          _isCapturing = false;
        });
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('舌象采集'),
        elevation: 0,
        backgroundColor: Colors.transparent,
      ),
      extendBodyBehindAppBar: true,
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // 相机预览
          _isCameraInitialized
              ? Center(
                  child: CameraPreview(_controller!),
                )
              : const Center(
                  child: CircularProgressIndicator(),
                ),
          
          // 舌象辅助叠加层
          if (_showOverlay && _isCameraInitialized)
            Positioned.fill(
              child: CustomPaint(
                painter: TongueGuidePainter(),
              ),
            ),
          
          // 拍照说明
          Positioned(
            top: 100,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
              color: Colors.black.withOpacity(0.5),
              child: const Text(
                '请张开嘴，伸出舌头，将舌头放在引导框中，保持光线充足',
                style: TextStyle(color: Colors.white, fontSize: 16),
                textAlign: TextAlign.center,
              ),
            ),
          ),
          
          // 底部控制栏
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 120,
              padding: const EdgeInsets.all(16),
              color: Colors.black.withOpacity(0.5),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // 闪光灯控制
                  IconButton(
                    icon: Icon(
                      _isFlashOn ? Icons.flash_on : Icons.flash_off,
                      color: Colors.white,
                      size: 28,
                    ),
                    onPressed: _toggleFlash,
                  ),
                  
                  // 拍照按钮
                  GestureDetector(
                    onTap: _isCapturing ? null : _takePicture,
                    child: Container(
                      width: 70,
                      height: 70,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 3),
                        color: _isCapturing ? Colors.grey : Colors.white.withOpacity(0.2),
                      ),
                      child: _isCapturing
                          ? const Center(
                              child: CircularProgressIndicator(
                                color: Colors.white,
                              ),
                            )
                          : const SizedBox(),
                    ),
                  ),
                  
                  // 辅助叠加层控制
                  IconButton(
                    icon: Icon(
                      _showOverlay ? Icons.grid_on : Icons.grid_off,
                      color: Colors.white,
                      size: 28,
                    ),
                    onPressed: _toggleOverlay,
                  ),
                ],
              ),
            ),
          ),
          
          // 加载遮罩
          if (_isCapturing) const LoadingOverlay(message: '正在处理图像...'),
        ],
      ),
    );
  }
}

/// 舌象引导绘制器
class TongueGuidePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.7)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    
    // 绘制舌象辅助框
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width * 0.35; // 圆形辅助区域半径
    
    // 绘制圆形参考线
    canvas.drawCircle(center, radius, paint);
    
    // 绘制十字参考线
    canvas.drawLine(
      Offset(center.dx - radius, center.dy),
      Offset(center.dx + radius, center.dy),
      paint,
    );
    canvas.drawLine(
      Offset(center.dx, center.dy - radius),
      Offset(center.dx, center.dy + radius),
      paint,
    );
    
    // 添加文字指引
    const textStyle = TextStyle(
      color: Colors.white,
      fontSize: 14,
      fontWeight: FontWeight.bold,
    );
    
    final textPainter = TextPainter(
      text: const TextSpan(
        text: '请将舌头置于圆圈中央',
        style: textStyle,
      ),
      textDirection: TextDirection.ltr,
    );
    
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(center.dx - textPainter.width / 2, center.dy + radius + 20),
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return false;
  }
} 