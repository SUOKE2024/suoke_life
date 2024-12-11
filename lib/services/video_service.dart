import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'health/health_analyzer_service.dart';
import 'api/health_check_service.dart';

class VideoService {
  late final HealthAnalyzerService _healthAnalyzer;
  CameraController? _controller;
  bool _isInitialized = false;
  Timer? _healthCheckTimer;
  final StreamController<List<int>> _videoStreamController = StreamController<List<int>>.broadcast();
  final StreamController<Map<String, dynamic>> _healthDataController = StreamController<Map<String, dynamic>>.broadcast();

  Stream<List<int>> get videoStream => _videoStreamController.stream;
  Stream<Map<String, dynamic>> get healthDataStream => _healthDataController.stream;

  VideoService() {
    final healthCheckService = HealthCheckService();
    _healthAnalyzer = HealthAnalyzerService(healthCheckService);
    
    // 订阅健康数据流
    _healthAnalyzer.healthDataStream.listen((healthData) {
      _healthDataController.add(healthData);
    });
  }

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        throw Exception('没有可用的相机');
      }

      // 默认使用前置摄像头
      final frontCamera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
        orElse: () => cameras.first,
      );

      _controller = CameraController(
        frontCamera,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.yuv420,
      );

      await _controller!.initialize();
      _isInitialized = true;
    } catch (e) {
      throw Exception('视频服务初始化失败: $e');
    }
  }

  Future<void> startVideo() async {
    if (!_isInitialized || _controller == null) {
      throw Exception('视频服务未初始化');
    }

    try {
      await _controller!.startImageStream((image) {
        // 处理视频帧
        _processImageFrame(image);
        // 进行健康分析
        _healthAnalyzer.analyzeVideoFrame(image);
      });

      // 启动定时健康检查
      _startHealthCheck();
    } catch (e) {
      throw Exception('启动视频流失败: $e');
    }
  }

  void _startHealthCheck() {
    _healthCheckTimer?.cancel();
    _healthCheckTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_controller != null && _controller!.value.isStreamingImages) {
        // 健康检查由 HealthAnalyzerService 处理
      }
    });
  }

  Future<void> _processImageFrame(CameraImage image) async {
    try {
      // 将YUV420格式转换为字节流
      final bytes = await compute(_convertYUV420toBytes, image);
      _videoStreamController.add(bytes);
    } catch (e) {
      debugPrint('处理视频帧失败: $e');
    }
  }

  Future<void> stopVideo() async {
    _healthCheckTimer?.cancel();
    await _controller?.stopImageStream();
  }

  void dispose() {
    _healthCheckTimer?.cancel();
    _controller?.dispose();
    _videoStreamController.close();
    _healthDataController.close();
    _healthAnalyzer.dispose();
    _isInitialized = false;
  }
}

// 在隔离区中进行图像转换
List<int> _convertYUV420toBytes(CameraImage image) {
  // TODO: 实现YUV420到字节流的转换
  return [];
} 