import 'dart:async';
import 'dart:io';
import 'dart:math';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image/image.dart' as img;
import 'package:path_provider/path_provider.dart';
import 'package:uuid/uuid.dart';
import 'package:suoke_life/core/widgets/tcm/models/tongue_diagnosis_data.dart';
import 'package:suoke_life/core/widgets/tcm/tongue/tongue_image_processor.dart';
import 'package:suoke_life/core/widgets/tcm/tongue/tongue_diagnosis_state.dart';

/// 舌诊状态提供者
final tongueDiagnosisStateProvider =
    StateNotifierProvider<TongueDiagnosisNotifier, TongueDiagnosisState>((ref) {
  return TongueDiagnosisNotifier();
});

/// 舌诊控制器，管理舌诊分析的业务逻辑
class TongueDiagnosisNotifier extends StateNotifier<TongueDiagnosisState> {
  TongueDiagnosisNotifier() : super(TongueDiagnosisState.initial());

  /// 图像处理器
  final _imageProcessor = TongueImageProcessor();

  /// 处理帧计数器
  int _frameCounter = 0;

  /// 分析计时器
  Timer? _analysisTimer;

  /// 相机分辨率
  ResolutionPreset _resolution = ResolutionPreset.medium;

  /// 舌头检测失败计数
  int _detectionFailureCount = 0;

  /// 分析帧计数
  int _analysisFrameCount = 0;

  /// 分析帧累积的特征数据
  List<TongueDiagnosisFeatures> _accumulatedFeatures = [];

  /// 销毁方法
  @override
  void dispose() {
    _stopAnalysis();
    _disposeCamera();
    super.dispose();
  }

  /// 初始化相机
  Future<void> initializeCamera() async {
    try {
      // 重置状态
      state = TongueDiagnosisState.initial();

      // 获取可用相机列表
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        state = state.copyWith(
          isInitializing: false,
          errorMessage: '没有可用的相机',
        );
        return;
      }

      // 选择前置相机，如果没有则使用第一个相机
      final selectedCamera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
        orElse: () => cameras.first,
      );

      // 创建相机控制器
      final controller = CameraController(
        selectedCamera,
        _resolution,
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid
            ? ImageFormatGroup.yuv420
            : ImageFormatGroup.bgra8888,
      );

      // 初始化相机
      await controller.initialize();

      // 设置闪光灯模式
      await controller.setFlashMode(FlashMode.off);

      // 设置曝光模式
      await controller.setExposureMode(ExposureMode.auto);

      // 更新状态
      state = state.copyWith(
        isInitializing: false,
        cameraController: controller,
        guidanceText: '准备就绪，请将舌头伸出对准屏幕中央区域',
      );
    } catch (e) {
      state = state.copyWith(
        isInitializing: false,
        errorMessage: '相机初始化失败: $e',
      );
    }
  }

  /// 处理相机图像帧
  Future<void> _processImageFrame(CameraImage image) async {
    try {
      // 限制处理帧的频率，每3帧处理一次
      _frameCounter++;
      if (_frameCounter % 3 != 0) return;

      // 处理图像帧
      final result = await _imageProcessor.processFrame(image);

      // 如果未检测到舌头
      if (result == null || result['detected'] == false) {
        _detectionFailureCount++;

        // 如果连续5次未检测到舌头，更新指导文本
        if (_detectionFailureCount >= 5) {
          _detectionFailureCount = 0; // 重置计数器
          final guidance = result?['guidance'] ?? '未检测到舌头，请尝试:';
          state = state.copyWith(
            guidanceText: '$guidance\n1. 充分伸出舌头\n2. 确保光线充足\n3. 调整距离',
          );
        }
        return;
      }

      // 重置检测失败计数
      _detectionFailureCount = 0;

      // 检测到舌头，提取结果
      final features = result['features'] as TongueDiagnosisFeatures;
      final diagnosisResult = result['result'] as TongueDiagnosisResult;

      // 累积帧数据，每10帧进行一次结果分析
      _analysisFrameCount++;
      _accumulateFeatures(features);

      if (_analysisFrameCount >= 10) {
        // 分析结束，更新状态
        _stopAnalysis();

        // 计算平均特征
        final avgFeatures = _calculateAverageFeatures();
        final finalResult = TongueDiagnosisResult.fromFeatures(avgFeatures);

        // 更新状态
        state = state.copyWith(
          isAnalyzing: false,
          features: avgFeatures,
          result: finalResult,
          guidanceText: '舌诊分析完成',
        );
      } else {
        // 更新进度提示
        state = state.copyWith(
          guidanceText: '分析中，请保持不动 (${_analysisFrameCount * 10}%)',
        );
      }
    } catch (e) {
      // 处理错误
      _stopAnalysis(errorMessage: '分析过程中出错: $e');
    }
  }

  /// 开始舌诊分析
  Future<void> startAnalysis() async {
    if (state.isAnalyzing) return; // 已经在分析中
    if (state.cameraController == null ||
        !state.cameraController!.value.isInitialized) {
      await initializeCamera();
    }

    try {
      // 更新状态
      state = state.copyWith(
        isAnalyzing: true,
        guidanceText: '正在分析，请将舌头伸出并保持不动',
        tongueDetected: false,
        features: null,
        result: null,
        regions: null,
        regionColors: null,
      );

      // 重置图像处理器
      _imageProcessor.reset();

      // 重置帧计数器
      _frameCounter = 0;

      // 开始图像流处理
      await _startImageStreamProcessing();

      // 设置分析计时器 - 15秒后自动停止
      _analysisTimer = Timer(const Duration(seconds: 15), () {
        if (state.isAnalyzing && !state.tongueDetected) {
          _stopAnalysis(
            errorMessage: '未能检测到舌头，请尝试在明亮环境下重新分析',
          );
        }
      });
    } catch (e) {
      state = state.copyWith(
        isAnalyzing: false,
        errorMessage: '启动分析失败: $e',
      );
    }
  }

  /// 停止舌诊分析
  Future<void> stopAnalysis() async {
    if (!state.isAnalyzing) return;

    // 重置状态标志
    state = state.copyWith(isAnalyzing: false);

    // 停止图像流处理
    if (state.cameraController != null &&
        state.cameraController!.value.isStreamingImages) {
      await state.cameraController!.stopImageStream();
    }

    // 清理计时器
    _analysisTimer?.cancel();
    _analysisTimer = null;

    // 重置计数器和累积数据
    _frameCounter = 0;
    _detectionFailureCount = 0;
    _analysisFrameCount = 0;
    _accumulatedFeatures.clear();
  }

  /// 内部用于停止分析的方法
  void _stopAnalysis({String? errorMessage}) {
    try {
      // 停止图像流处理
      if (state.cameraController != null &&
          state.cameraController!.value.isStreamingImages) {
        state.cameraController!.stopImageStream();
      }

      // 如果提供了错误消息，更新状态
      if (errorMessage != null) {
        state = state.copyWith(
          isAnalyzing: false,
          errorMessage: errorMessage,
        );
      } else {
        state = state.copyWith(
          isAnalyzing: false,
        );
      }

      // 清理计时器
      _analysisTimer?.cancel();
      _analysisTimer = null;
    } catch (e) {
      print('停止分析时出错: $e');
    }
  }

  /// 开始图像流处理
  Future<void> _startImageStreamProcessing() async {
    if (state.cameraController == null) return;

    await state.cameraController!.startImageStream((CameraImage image) async {
      // 保存当前图像帧
      state = state.copyWith(currentImage: image);

      // 每3帧处理一次以减轻CPU负担
      if (_frameCounter++ % 3 != 0) return;

      // 处理帧
      await _processImageFrame(image);
    });
  }

  /// 释放相机资源
  Future<void> _disposeCamera() async {
    if (state.cameraController != null) {
      await state.cameraController!.dispose();
    }
  }

  /// 保存舌诊结果
  Future<void> saveResult() async {
    if (state.result == null || state.features == null) return;

    try {
      final uuid = const Uuid().v4();

      // 创建保存目录
      final directory = await getApplicationDocumentsDirectory();
      final tongueDirPath = '${directory.path}/tongue_diagnosis';
      final tongueDir = Directory(tongueDirPath);
      if (!await tongueDir.exists()) {
        await tongueDir.create(recursive: true);
      }

      // 保存舌诊图像
      final imagePath = '$tongueDirPath/$uuid.jpg';

      // 由于CameraController的takePicture方法会刷新相机，所以我们不直接使用它
      // 而是使用当前处理的图像来保存
      if (state.cameraController != null &&
          state.cameraController!.value.isInitialized) {
        try {
          // 确保相机被初始化和未被释放
          if (!state.cameraController!.value.isStreamingImages) {
            await state.cameraController!.startImageStream((image) async {
              try {
                await state.cameraController!.stopImageStream();

                // 处理图像并保存
                // 这里简化处理，实际应用中可能需要更复杂的图像处理
                await _processCameraImageAndSave(image, imagePath);

                // 更新状态
                state = state.copyWith(
                  historyId: uuid,
                );
              } catch (e) {
                print('处理图像出错: $e');
              }
            });
          } else {
            // 如果已经在流处理，则使用当前帧
            final currentImage = state.currentImage;
            if (currentImage != null) {
              await _processCameraImageAndSave(currentImage, imagePath);
              state = state.copyWith(historyId: uuid);
            }
          }
        } catch (e) {
          print('相机拍照出错: $e');
        }
      }

      // TODO: 保存舌诊结果到数据库
    } catch (e) {
      state = state.copyWith(
        errorMessage: '保存结果失败: $e',
      );
    }
  }

  /// 处理相机图像并保存
  Future<void> _processCameraImageAndSave(
      CameraImage image, String path) async {
    try {
      img.Image? processedImage;

      if (image.format.group == ImageFormatGroup.yuv420) {
        final yuvImage = await _convertYUV420ToImage(image);
        processedImage = yuvImage;
      } else if (image.format.group == ImageFormatGroup.bgra8888) {
        final bgraImage = await _convertBGRA8888ToImage(image);
        processedImage = bgraImage;
      }

      if (processedImage != null) {
        final jpgData = img.encodeJpg(processedImage, quality: 90);
        final file = File(path);
        await file.writeAsBytes(jpgData);
      }
    } catch (e) {
      print('保存图像失败: $e');
    }
  }

  /// 将YUV420格式转换为图像
  Future<img.Image?> _convertYUV420ToImage(CameraImage image) async {
    try {
      final width = image.width;
      final height = image.height;

      // 创建RGB图像
      final rgbImage = img.Image(width: width, height: height);

      // YUV平面
      final yPlane = image.planes[0].bytes;
      final uPlane = image.planes[1].bytes;
      final vPlane = image.planes[2].bytes;

      // YUV平面的行跨度
      final yRowStride = image.planes[0].bytesPerRow;
      final uvRowStride = image.planes[1].bytesPerRow;

      // YUV平面的像素跨度
      final uvPixelStride = image.planes[1].bytesPerPixel!;

      // 转换YUV到RGB
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          final int yIndex = y * yRowStride + x;

          // uvPixelStride为2表示每个uv像素占2个字节
          final int uvIndex = (y ~/ 2) * uvRowStride + (x ~/ 2) * uvPixelStride;

          // YUV值
          final int yValue = yPlane[yIndex];
          final int uValue = uPlane[uvIndex];
          final int vValue = vPlane[uvIndex];

          // YUV到RGB转换
          int r = yValue + (1.402 * (vValue - 128)).toInt();
          int g = yValue -
              (0.344 * (uValue - 128)).toInt() -
              (0.714 * (vValue - 128)).toInt();
          int b = yValue + (1.772 * (uValue - 128)).toInt();

          // 限制在0-255范围内
          r = r.clamp(0, 255);
          g = g.clamp(0, 255);
          b = b.clamp(0, 255);

          // 设置像素
          rgbImage.setPixelRgba(x, y, r, g, b, 255);
        }
      }

      return rgbImage;
    } catch (e) {
      print('YUV420转换失败: $e');
      return null;
    }
  }

  /// 将BGRA8888格式转换为图像
  Future<img.Image?> _convertBGRA8888ToImage(CameraImage image) async {
    try {
      final width = image.width;
      final height = image.height;
      final rgbImage = img.Image(width: width, height: height);

      final buffer = image.planes[0].bytes;
      final int stride = image.planes[0].bytesPerRow;
      final int bytesPerPixel = image.planes[0].bytesPerPixel!;

      // 转换BGRA到RGB
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          final int index = y * stride + x * bytesPerPixel;

          // BGRA值
          final int b = buffer[index];
          final int g = buffer[index + 1];
          final int r = buffer[index + 2];
          // A不使用

          // 设置像素
          rgbImage.setPixelRgba(x, y, r, g, b, 255);
        }
      }

      return rgbImage;
    } catch (e) {
      print('BGRA8888转换失败: $e');
      return null;
    }
  }

  /// 累积特征
  void _accumulateFeatures(TongueDiagnosisFeatures features) {
    _accumulatedFeatures.add(features);
  }

  /// 计算平均特征
  TongueDiagnosisFeatures _calculateAverageFeatures() {
    if (_accumulatedFeatures.isEmpty) {
      // 默认返回正常舌诊特征
      return TongueDiagnosisFeatures.normal();
    }

    // 统计各种特征的出现次数
    Map<TongueBodyFeature, int> bodyCount = {};
    Map<TongueCoatingFeature, int> coatingCount = {};
    Map<TongueShapeFeature, int> shapeCount = {};
    Map<TongueVeinFeature, int> veinCount = {};

    // 特征置信度总和
    double bodyConfidenceSum = 0;
    double coatingConfidenceSum = 0;
    double shapeConfidenceSum = 0;
    double veinConfidenceSum = 0;

    // 统计每种特征的出现次数和置信度
    for (final feature in _accumulatedFeatures) {
      bodyCount[feature.bodyFeature] =
          (bodyCount[feature.bodyFeature] ?? 0) + 1;
      coatingCount[feature.coatingFeature] =
          (coatingCount[feature.coatingFeature] ?? 0) + 1;
      shapeCount[feature.shapeFeature] =
          (shapeCount[feature.shapeFeature] ?? 0) + 1;
      veinCount[feature.veinFeature] =
          (veinCount[feature.veinFeature] ?? 0) + 1;

      bodyConfidenceSum += feature.bodyConfidence;
      coatingConfidenceSum += feature.coatingConfidence;
      shapeConfidenceSum += feature.shapeConfidence;
      veinConfidenceSum += feature.veinConfidence;
    }

    // 找出出现次数最多的特征
    TongueBodyFeature mostCommonBody =
        bodyCount.entries.reduce((a, b) => a.value > b.value ? a : b).key;
    TongueCoatingFeature mostCommonCoating =
        coatingCount.entries.reduce((a, b) => a.value > b.value ? a : b).key;
    TongueShapeFeature mostCommonShape =
        shapeCount.entries.reduce((a, b) => a.value > b.value ? a : b).key;
    TongueVeinFeature mostCommonVein =
        veinCount.entries.reduce((a, b) => a.value > b.value ? a : b).key;

    // 计算平均置信度
    final count = _accumulatedFeatures.length;
    final avgBodyConfidence = bodyConfidenceSum / count;
    final avgCoatingConfidence = coatingConfidenceSum / count;
    final avgShapeConfidence = shapeConfidenceSum / count;
    final avgVeinConfidence = veinConfidenceSum / count;

    // 清空累积数据
    _accumulatedFeatures.clear();
    _analysisFrameCount = 0;

    // 返回平均特征
    return TongueDiagnosisFeatures(
      bodyFeature: mostCommonBody,
      bodyConfidence: avgBodyConfidence,
      coatingFeature: mostCommonCoating,
      coatingConfidence: avgCoatingConfidence,
      shapeFeature: mostCommonShape,
      shapeConfidence: avgShapeConfidence,
      veinFeature: mostCommonVein,
      veinConfidence: avgVeinConfidence,
    );
  }

  /// 从路径加载图片
  Future<void> loadImageFromPath(String imagePath) async {
    try {
      // 设置为加载状态
      state = state.copyWith(
        isInitializing: false,
        isAnalyzing: true,
        guidanceText: '正在加载图片...',
      );

      // 读取图片文件
      final file = File(imagePath);
      if (!await file.exists()) {
        throw Exception('图片文件不存在');
      }

      // 读取图片数据
      final bytes = await file.readAsBytes();
      final image = img.decodeImage(bytes);

      if (image == null) {
        throw Exception('无法解码图片');
      }

      // 分析图片
      // 这里应该调用实际的图像分析逻辑
      // 为简化示例，使用随机生成的特征
      await Future.delayed(const Duration(seconds: 1)); // 模拟处理时间

      final features = TongueDiagnosisFeatures.random();
      final result = TongueDiagnosisResult.fromFeatures(features);

      // 更新状态
      state = state.copyWith(
        isAnalyzing: false,
        features: features,
        result: result,
        guidanceText: '图片分析完成',
      );
    } catch (e) {
      debugPrint('从路径加载图片失败: $e');
      state = state.copyWith(
        isAnalyzing: false,
        errorMessage: '加载图片失败: $e',
      );
    }
  }

  /// 分析图片
  Future<Map<String, dynamic>> _analyzeImage(img.Image image) async {
    try {
      // 这里应该调用实际的图像分析逻辑
      // 为简化示例，使用随机生成的特征
      await Future.delayed(const Duration(seconds: 1)); // 模拟处理时间

      final features = TongueDiagnosisFeatures.random();
      final result = TongueDiagnosisResult.fromFeatures(features);

      return {
        'features': features,
        'result': result,
      };
    } catch (e) {
      debugPrint('分析图片失败: $e');
      rethrow;
    }
  }
}
