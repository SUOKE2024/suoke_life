import 'dart:async';
import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image/image.dart' as img;
import 'package:suoke_life/core/widgets/tcm/models/tongue_diagnosis_data.dart';

/// 舌诊图像处理器，用于分析舌诊图像并提取特征
/// 采用了更高级的计算机视觉算法
class TongueImageProcessor {
  /// 原始图像
  CameraImage? _rawImage;

  /// 处理后的图像（RGB格式）
  img.Image? _processedImage;

  /// 图像处理缓存
  Map<String, dynamic> _processingCache = {};

  /// 是否检测到舌头
  bool _tongueDetected = false;

  /// 舌头区域
  Rect? _tongueRegion;

  /// 舌质区域
  Rect? _tongueBodyRegion;

  /// 舌苔区域
  Rect? _tongueCoatingRegion;

  /// 舌下区域
  Rect? _tongueVeinRegion;

  /// 清除数据
  void reset() {
    _rawImage = null;
    _processedImage = null;
    _processingCache.clear();
    _tongueDetected = false;
    _tongueRegion = null;
    _tongueBodyRegion = null;
    _tongueCoatingRegion = null;
    _tongueVeinRegion = null;
  }

  /// 处理相机图像帧
  Future<Map<String, dynamic>?> processFrame(CameraImage imageFrame) async {
    // 保存原始图像
    _rawImage = imageFrame;

    // 转换图像格式（YUV/BGRA -> RGB）
    await _convertFrameToImage(imageFrame);

    // 如果转换失败，返回null
    if (_processedImage == null) {
      return null;
    }

    // 使用高级计算机视觉算法检测舌头区域
    await _detectTongueRegionAdvanced();

    // 如果未检测到舌头，则返回指导信息
    if (!_tongueDetected || _tongueRegion == null) {
      return {
        'detected': false,
        'guidance': _getGuidanceMessage(),
      };
    }

    // 分析舌质特征
    final bodyFeature = await _analyzeBodyFeature();

    // 分析舌苔特征
    final coatingFeature = await _analyzeCoatingFeature();

    // 分析舌形特征
    final shapeFeature = await _analyzeShapeFeature();

    // 分析舌下络脉特征
    final veinFeature = await _analyzeVeinFeature();

    // 创建舌诊特征
    final features = TongueDiagnosisFeatures(
      bodyFeature: bodyFeature.feature,
      bodyConfidence: bodyFeature.confidence,
      coatingFeature: coatingFeature.feature,
      coatingConfidence: coatingFeature.confidence,
      shapeFeature: shapeFeature.feature,
      shapeConfidence: shapeFeature.confidence,
      veinFeature: veinFeature.feature,
      veinConfidence: veinFeature.confidence,
    );

    // 生成结果分析
    final result = TongueDiagnosisResult.fromFeatures(features);

    // 返回分析结果
    return {
      'detected': true,
      'features': features,
      'result': result,
      'regions': {
        'tongue': _rectToJson(_tongueRegion!),
        'body': _rectToJson(_tongueBodyRegion!),
        'coating': _rectToJson(_tongueCoatingRegion!),
        'vein': _rectToJson(_tongueVeinRegion!),
      },
      'colors': {
        'body': _getAverageColor(_tongueBodyRegion!),
        'coating': _getAverageColor(_tongueCoatingRegion!),
        'vein': _getAverageColor(_tongueVeinRegion!),
      },
    };
  }

  /// 将相机图像帧转换为图像对象
  Future<void> _convertFrameToImage(CameraImage imageFrame) async {
    try {
      if (imageFrame.format.group == ImageFormatGroup.yuv420) {
        // YUV格式处理
        final width = imageFrame.width;
        final height = imageFrame.height;

        // 创建RGB图像
        final image = img.Image(width: width, height: height);

        // YUV平面
        final yPlane = imageFrame.planes[0].bytes;
        final uPlane = imageFrame.planes[1].bytes;
        final vPlane = imageFrame.planes[2].bytes;

        // YUV平面的行跨度
        final yRowStride = imageFrame.planes[0].bytesPerRow;
        final uvRowStride = imageFrame.planes[1].bytesPerRow;

        // YUV平面的像素跨度
        final uvPixelStride = imageFrame.planes[1].bytesPerPixel!;

        // 转换YUV到RGB
        for (int y = 0; y < height; y++) {
          for (int x = 0; x < width; x++) {
            final int yIndex = y * yRowStride + x;

            // uvPixelStride为2表示每个uv像素占2个字节
            final int uvIndex =
                (y ~/ 2) * uvRowStride + (x ~/ 2) * uvPixelStride;

            // YUV值
            final int yValue = yPlane[yIndex];
            final int uValue = uPlane[uvIndex];
            final int vValue = vPlane[uvIndex];

            // YUV到RGB转换
            // 基于公式:
            // R = Y + 1.402 * (V-128)
            // G = Y - 0.344 * (U-128) - 0.714 * (V-128)
            // B = Y + 1.772 * (U-128)
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
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }

        _processedImage = image;
      } else if (imageFrame.format.group == ImageFormatGroup.bgra8888) {
        // BGRA格式处理
        final width = imageFrame.width;
        final height = imageFrame.height;
        final image = img.Image(width: width, height: height);

        final buffer = imageFrame.planes[0].bytes;
        final int stride = imageFrame.planes[0].bytesPerRow;
        final int bytesPerPixel = imageFrame.planes[0].bytesPerPixel!;

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
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }

        _processedImage = image;
      } else {
        throw Exception('不支持的图像格式: ${imageFrame.format.group}');
      }
    } catch (e) {
      // TODO: 使用正式的日志记录系统替代print
      // print('图像转换失败: $e');
      _processedImage = null;
    }
  }

  /// 使用高级计算机视觉算法检测舌头区域
  Future<void> _detectTongueRegionAdvanced() async {
    if (_processedImage == null) return;

    try {
      final image = _processedImage!;
      final width = image.width;
      final height = image.height;

      // 多级特征提取和轮廓检测
      // 步骤1: 颜色空间转换 - 从RGB转换到HSV颜色空间以更好地识别皮肤和舌头颜色
      final hsvImage = _convertToHSV(image);

      // 步骤2: 基于肤色和舌头颜色的像素分类
      final tongueMask = _generateTongueMask(hsvImage, width, height);

      // 步骤3: 使用形态学操作改进掩码
      final improvedMask =
          _applyMorphologicalOperations(tongueMask, width, height);

      // 步骤4: 轮廓检测和最大轮廓提取
      final tongueContour = _findLargestContour(improvedMask, width, height);

      // 步骤5: 计算舌头区域的边界框
      if (tongueContour.isNotEmpty && tongueContour.length > 50) {
        _tongueDetected = true;

        // 找到轮廓的边界
        int minX = width, minY = height, maxX = 0, maxY = 0;
        for (final point in tongueContour) {
          minX = math.min(minX, point.dx.toInt());
          minY = math.min(minY, point.dy.toInt());
          maxX = math.max(maxX, point.dx.toInt());
          maxY = math.max(maxY, point.dy.toInt());
        }

        // 添加一些边距
        final padding = math.min(width, height) ~/ 20;
        minX = math.max(0, minX - padding);
        minY = math.max(0, minY - padding);
        maxX = math.min(width - 1, maxX + padding);
        maxY = math.min(height - 1, maxY + padding);

        // 检查检测区域是否合理 (至少占屏幕的10%)
        final areaRatio = ((maxX - minX) * (maxY - minY)) / (width * height);
        if (areaRatio < 0.05) {
          // 面积太小，可能是误判，使用回退方法
          await _detectTongueRegionFallback();
          return;
        }

        // 设置舌头区域
        _tongueRegion = Rect.fromLTRB(
            minX.toDouble(), minY.toDouble(), maxX.toDouble(), maxY.toDouble());

        // 划分舌体区域
        _divideTongueRegions();
      } else {
        // 如果轮廓检测失败，回退到简单的颜色阈值方法
        await _detectTongueRegionFallback();
      }
    } catch (e) {
      print('高级舌头检测失败: $e');
      // 回退到简单方法
      await _detectTongueRegionFallback();
    }
  }

  /// 将RGB图像转换为HSV颜色空间
  List<List<Map<String, double>>> _convertToHSV(img.Image image) {
    final width = image.width;
    final height = image.height;
    final hsvImage = List.generate(
        height,
        (_) => List.generate(
            width, (_) => <String, double>{'h': 0, 's': 0, 'v': 0}));

    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        final pixel = image.getPixel(x, y);
        final r = pixel.r / 255.0;
        final g = pixel.g / 255.0;
        final b = pixel.b / 255.0;

        final max = math.max(math.max(r, g), b);
        final min = math.min(math.min(r, g), b);
        final delta = max - min;

        // 色相计算
        double h = 0;
        if (delta > 0) {
          if (max == r) {
            h = ((g - b) / delta) % 6;
          } else if (max == g) {
            h = (b - r) / delta + 2;
          } else {
            h = (r - g) / delta + 4;
          }
          h *= 60;
          if (h < 0) h += 360;
        }

        // 饱和度计算
        final s = max == 0 ? 0 : delta / max;

        // 亮度
        final v = max;

        hsvImage[y]
            [x] = {'h': h.toDouble(), 's': s.toDouble(), 'v': v.toDouble()};
      }
    }

    return hsvImage;
  }

  /// 生成舌头掩码
  List<List<bool>> _generateTongueMask(
      List<List<Map<String, double>>> hsvImage, int width, int height) {
    final mask = List.generate(height, (_) => List.filled(width, false));

    // 舌头颜色范围扩大 - 改进版本
    // H: 红色范围扩大 (0-40或320-360)
    // S: 降低饱和度要求，接受稍微不那么饱和的颜色
    // V: 接受亮度更广的范围
    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        final hsv = hsvImage[y][x];
        final h = hsv['h']!;
        final s = hsv['s']!;
        final v = hsv['v']!;

        // 更宽松的舌头颜色判断，增加检测率
        final isTongueColor = ((h < 40 || h > 320) && s > 0.1 && v > 0.15) ||
            // 增加粉色范围
            (h >= 340 || h <= 20) && s > 0.08 && v > 0.4 ||
            // 增加浅红色范围
            (h >= 0 && h <= 30) && s > 0.05 && v > 0.5;

        mask[y][x] = isTongueColor;
      }
    }

    return mask;
  }

  /// 应用形态学操作改进掩码
  List<List<bool>> _applyMorphologicalOperations(
      List<List<bool>> mask, int width, int height) {
    // 去噪 - 使用中值滤波
    final denoisedMask = _medianFilter(mask, width, height);

    // 膨胀操作 - 填充小空洞
    final dilatedMask = _dilate(denoisedMask, width, height);

    // 腐蚀操作 - 平滑边缘
    final erodedMask = _erode(dilatedMask, width, height);

    return erodedMask;
  }

  /// 中值滤波
  List<List<bool>> _medianFilter(List<List<bool>> mask, int width, int height) {
    final result = List.generate(height, (_) => List.filled(width, false));
    const kernelSize = 3;
    final halfKernel = kernelSize ~/ 2;

    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        final window = <bool>[];

        for (int ky = -halfKernel; ky <= halfKernel; ky++) {
          for (int kx = -halfKernel; kx <= halfKernel; kx++) {
            final ny = y + ky;
            final nx = x + kx;

            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
              window.add(mask[ny][nx]);
            }
          }
        }

        // 排序并取中值
        window.sort();
        result[y][x] = window[window.length ~/ 2];
      }
    }

    return result;
  }

  /// 膨胀操作
  List<List<bool>> _dilate(List<List<bool>> mask, int width, int height) {
    final result = List.generate(height, (_) => List.filled(width, false));
    const kernelSize = 5;
    final halfKernel = kernelSize ~/ 2;

    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        bool anyTrue = false;

        for (int ky = -halfKernel; ky <= halfKernel; ky++) {
          for (int kx = -halfKernel; kx <= halfKernel; kx++) {
            final ny = y + ky;
            final nx = x + kx;

            if (ny >= 0 &&
                ny < height &&
                nx >= 0 &&
                nx < width &&
                mask[ny][nx]) {
              anyTrue = true;
              break;
            }
          }
          if (anyTrue) break;
        }

        result[y][x] = anyTrue;
      }
    }

    return result;
  }

  /// 腐蚀操作
  List<List<bool>> _erode(List<List<bool>> mask, int width, int height) {
    final result = List.generate(height, (_) => List.filled(width, false));
    const kernelSize = 3;
    final halfKernel = kernelSize ~/ 2;

    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        bool allTrue = true;

        for (int ky = -halfKernel; ky <= halfKernel; ky++) {
          for (int kx = -halfKernel; kx <= halfKernel; kx++) {
            final ny = y + ky;
            final nx = x + kx;

            if (ny < 0 ||
                ny >= height ||
                nx < 0 ||
                nx >= width ||
                !mask[ny][nx]) {
              allTrue = false;
              break;
            }
          }
          if (!allTrue) break;
        }

        result[y][x] = allTrue;
      }
    }

    return result;
  }

  /// 查找最大轮廓
  List<Offset> _findLargestContour(
      List<List<bool>> mask, int width, int height) {
    // 使用边缘追踪算法找到轮廓
    final List<List<Offset>> allContours = [];
    final visited = List.generate(height, (_) => List.filled(width, false));

    // 寻找连通区域
    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        if (mask[y][x] && !visited[y][x]) {
          final contour = <Offset>[];
          _traceContour(mask, visited, x, y, width, height, contour);
          if (contour.isNotEmpty) {
            allContours.add(contour);
          }
        }
      }
    }

    // 找到最大轮廓
    if (allContours.isEmpty) return [];
    return allContours
        .reduce((curr, next) => curr.length > next.length ? curr : next);
  }

  /// 递归跟踪轮廓
  void _traceContour(List<List<bool>> mask, List<List<bool>> visited, int x,
      int y, int width, int height, List<Offset> contour) {
    if (x < 0 ||
        x >= width ||
        y < 0 ||
        y >= height ||
        visited[y][x] ||
        !mask[y][x]) {
      return;
    }

    visited[y][x] = true;
    contour.add(Offset(x.toDouble(), y.toDouble()));

    // 八个方向探索
    _traceContour(mask, visited, x + 1, y, width, height, contour);
    _traceContour(mask, visited, x - 1, y, width, height, contour);
    _traceContour(mask, visited, x, y + 1, width, height, contour);
    _traceContour(mask, visited, x, y - 1, width, height, contour);
    _traceContour(mask, visited, x + 1, y + 1, width, height, contour);
    _traceContour(mask, visited, x - 1, y - 1, width, height, contour);
    _traceContour(mask, visited, x + 1, y - 1, width, height, contour);
    _traceContour(mask, visited, x - 1, y + 1, width, height, contour);
  }

  /// 后备的基础舌头检测方法
  Future<void> _detectTongueRegionFallback() async {
    if (_processedImage == null) return;

    try {
      final image = _processedImage!;
      final width = image.width;
      final height = image.height;

      // 舌体通常为粉红色或红色，计算可能的舌头区域
      int minX = width;
      int minY = height;
      int maxX = 0;
      int maxY = 0;
      int tonguePixelCount = 0;

      // 扫描图像中心区域（速度优化）
      final centerX = width ~/ 2;
      final centerY = height ~/ 2;
      // 增大扫描区域以提高检测率
      final scanRadius = math.min(width, height) ~/ 2.5;

      for (int y = centerY - scanRadius; y < centerY + scanRadius; y++) {
        if (y < 0 || y >= height) continue;

        for (int x = centerX - scanRadius; x < centerX + scanRadius; x++) {
          if (x < 0 || x >= width) continue;

          final pixel = image.getPixel(x, y);
          final r = pixel.r.toDouble();
          final g = pixel.g.toDouble();
          final b = pixel.b.toDouble();

          // 检查像素是否可能是舌头
          if (_isTonguePixel(r, g, b)) {
            minX = math.min(minX, x);
            minY = math.min(minY, y);
            maxX = math.max(maxX, x);
            maxY = math.max(maxY, y);
            tonguePixelCount++;
          }
        }
      }

      // 如果检测到足够的舌头像素 - 降低阈值以提高检测率
      if (tonguePixelCount > (scanRadius * scanRadius * 0.1)) {
        // 从0.2降低到0.1
        _tongueDetected = true;

        // 添加边距
        final padding = scanRadius ~/ 10;
        minX = math.max(0, minX - padding);
        minY = math.max(0, minY - padding);
        maxX = math.min(width - 1, maxX + padding);
        maxY = math.min(height - 1, maxY + padding);

        // 设置舌头区域
        _tongueRegion = Rect.fromLTRB(
            minX.toDouble(), minY.toDouble(), maxX.toDouble(), maxY.toDouble());

        // 划分舌体区域
        _divideTongueRegions();
      } else {
        _tongueDetected = false;
        _tongueRegion = null;
      }
    } catch (e) {
      print('舌头检测失败: $e');
      _tongueDetected = false;
      _tongueRegion = null;
    }
  }

  /// 判断像素是否属于舌头
  bool _isTonguePixel(num r, num g, num b) {
    // 舌头颜色阈值放宽，增加检测率
    // 1. 红色分量高的像素 (典型舌色)
    final isRedTongue = r > 120 && r > g * 1.1 && r > b * 1.1;

    // 2. 粉色偏白的舌色 (淡白舌)
    final isPinkTongue = r > 180 && g > 130 && b > 130 && r > g && r > b;

    // 3. 深红色的舌色 (深红舌)
    final isDeepRedTongue = r > 100 && r > g * 1.3 && r > b * 1.3 && r < 180;

    // 4. 紫红色的舌色 (紫舌)
    final isPurpleTongue = r > 100 && b > 80 && r > g * 1.2 && b > g * 1.1;

    return isRedTongue || isPinkTongue || isDeepRedTongue || isPurpleTongue;
  }

  /// 划分舌体区域（舌质、舌苔、舌下）
  void _divideTongueRegions() {
    if (_tongueRegion == null) return;

    final tongueWidth = _tongueRegion!.width;
    final tongueHeight = _tongueRegion!.height;
    final left = _tongueRegion!.left;
    final top = _tongueRegion!.top;
    final right = _tongueRegion!.right;
    final bottom = _tongueRegion!.bottom;

    // 使用解剖学知识改进区域划分
    // 舌质区域（舌的前2/3部分）
    _tongueBodyRegion = Rect.fromLTRB(
      left + tongueWidth * 0.15,
      top + tongueHeight * 0.15,
      right - tongueWidth * 0.15,
      top + tongueHeight * 0.6,
    );

    // 舌苔区域（舌的中后部）
    _tongueCoatingRegion = Rect.fromLTRB(
      left + tongueWidth * 0.25,
      top + tongueHeight * 0.3,
      right - tongueWidth * 0.25,
      bottom - tongueHeight * 0.15,
    );

    // 舌下区域（舌的下部）
    _tongueVeinRegion = Rect.fromLTRB(
      left + tongueWidth * 0.2,
      bottom - tongueHeight * 0.25,
      right - tongueWidth * 0.2,
      bottom,
    );
  }

  /// 分析舌质特征
  Future<({TongueBodyFeature feature, double confidence})>
      _analyzeBodyFeature() async {
    if (_processedImage == null || _tongueBodyRegion == null) {
      return (feature: TongueBodyFeature.normal, confidence: 0.5);
    }

    try {
      // 获取舌质区域的平均颜色和质地特征
      final color = _getAverageColor(_tongueBodyRegion!);
      final r = (color >> 16) & 0xFF;
      final g = (color >> 8) & 0xFF;
      final b = color & 0xFF;

      // 增强的颜色特征分析
      final redRatio = r / math.max(1, math.max(g, b));
      final brightness = (r + g + b) / 3.0 / 255.0;
      final purpleness = (r * 0.5 + b * 0.5) / math.max(1, g);

      // 添加纹理分析
      final textureVariance = _getColorVariance(_tongueBodyRegion!);
      final textureComplexity = math.sqrt(textureVariance) / 50; // 归一化

      // 多特征加权决策
      TongueBodyFeature feature;
      double confidence = 0.7; // 默认可信度

      // 使用更复杂的决策逻辑
      if (redRatio > 1.5 && brightness > 0.7) {
        if (r > 220 && brightness > 0.8) {
          feature = TongueBodyFeature.crimson;
          confidence = 0.7 + redRatio / 10 + brightness / 5;
        } else {
          feature = TongueBodyFeature.red;
          confidence = 0.7 + redRatio / 8;
        }
      } else if (purpleness > 1.3 && b > 100) {
        feature = TongueBodyFeature.purple;
        confidence = 0.7 + purpleness / 8;
      } else if (brightness > 0.85 && redRatio < 1.3) {
        feature = TongueBodyFeature.pale;
        confidence = 0.75 + (1.0 - redRatio) / 4;
      } else if (brightness > 0.6 &&
          brightness < 0.85 &&
          textureComplexity < 0.3) {
        feature = TongueBodyFeature.tender;
        confidence = 0.7 + textureComplexity;
      } else if (textureComplexity > 0.5 && brightness > 0.65) {
        feature = TongueBodyFeature.flaked;
        confidence = 0.65 + textureComplexity / 2;
      } else {
        // 正常舌（淡红舌）
        feature = TongueBodyFeature.normal;
        confidence = 0.75 + (1 - (redRatio - 1.3).abs() / 1.5);
      }

      // 限制可信度范围
      confidence = confidence.clamp(0.6, 0.95);

      return (feature: feature, confidence: confidence);
    } catch (e) {
      print('舌质分析失败: $e');
      return (feature: TongueBodyFeature.normal, confidence: 0.5);
    }
  }

  /// 获取区域的平均颜色（RGB格式）
  int _getAverageColor(Rect region) {
    if (_processedImage == null) return 0xFFFFFFFF;

    try {
      final image = _processedImage!;
      final left = region.left.toInt();
      final top = region.top.toInt();
      final right = region.right.toInt();
      final bottom = region.bottom.toInt();

      double totalR = 0;
      double totalG = 0;
      double totalB = 0;
      int pixelCount = 0;

      for (int y = top; y < bottom; y++) {
        for (int x = left; x < right; x++) {
          if (x >= 0 && x < image.width && y >= 0 && y < image.height) {
            final pixel = image.getPixel(x, y);
            final r = pixel.r.toDouble();
            final g = pixel.g.toDouble();
            final b = pixel.b.toDouble();
            totalR += r;
            totalG += g;
            totalB += b;
            pixelCount++;
          }
        }
      }

      if (pixelCount == 0) return 0xFFFFFFFF;

      final avgR = (totalR / pixelCount).round();
      final avgG = (totalG / pixelCount).round();
      final avgB = (totalB / pixelCount).round();

      return (0xFF << 24) | (avgR << 16) | (avgG << 8) | avgB;
    } catch (e) {
      print('计算平均颜色失败: $e');
      return 0xFFFFFFFF;
    }
  }

  /// 获取区域的颜色方差
  double _getColorVariance(Rect region) {
    if (_processedImage == null) return 0;

    try {
      final image = _processedImage!;
      final left = region.left.toInt();
      final top = region.top.toInt();
      final right = region.right.toInt();
      final bottom = region.bottom.toInt();

      // 首先计算平均RGB
      final averageColor = _getAverageColor(region);
      final avgR = (averageColor >> 16) & 0xFF;
      final avgG = (averageColor >> 8) & 0xFF;
      final avgB = averageColor & 0xFF;

      double sumSquaredDifference = 0;
      int pixelCount = 0;

      for (int y = top; y < bottom; y++) {
        for (int x = left; x < right; x++) {
          if (x >= 0 && x < image.width && y >= 0 && y < image.height) {
            final pixel = image.getPixel(x, y);
            final r = pixel.r.toDouble();
            final g = pixel.g.toDouble();
            final b = pixel.b.toDouble();

            // 计算欧几里得距离的平方
            final dr = r - avgR;
            final dg = g - avgG;
            final db = b - avgB;
            sumSquaredDifference += dr * dr + dg * dg + db * db;
            pixelCount++;
          }
        }
      }

      if (pixelCount == 0) return 0;

      // 返回方差
      return sumSquaredDifference / pixelCount;
    } catch (e) {
      print('计算颜色方差失败: $e');
      return 0;
    }
  }

  /// 获取指导信息
  String _getGuidanceMessage() {
    if (_rawImage == null || _processedImage == null) {
      return '请将舌头置于摄像头前，并保持不动';
    }

    // 高级场景分析
    final avgColor = _getAverageColor(Rect.fromLTWH(0, 0,
        _processedImage!.width.toDouble(), _processedImage!.height.toDouble()));
    final brightness = (((avgColor >> 16) & 0xFF) +
            ((avgColor >> 8) & 0xFF) +
            (avgColor & 0xFF)) /
        (3 * 255);

    // 模糊度检测
    final blurriness = _detectBlurriness();

    if (brightness < 0.2) {
      return '环境光线不足，请移至更明亮的地方';
    } else if (brightness > 0.9) {
      return '光线过强，请避免阳光直射或强灯光';
    } else if (blurriness > 0.7) {
      return '图像模糊，请保持相机稳定并对准舌头';
    } else if (!_tongueDetected) {
      return '未检测到舌头，请将舌头伸出并置于画面中央';
    } else {
      return '检测到舌头，请保持稳定，正在分析...';
    }
  }

  /// 检测图像模糊度
  double _detectBlurriness() {
    if (_processedImage == null) return 1.0;

    try {
      // 使用拉普拉斯算子检测边缘清晰度
      final image = _processedImage!;
      double laplacianVariance = 0;

      // 简化版拉普拉斯边缘检测
      for (int y = 1; y < image.height - 1; y++) {
        for (int x = 1; x < image.width - 1; x++) {
          final center = image.getPixel(x, y);
          final top = image.getPixel(x, y - 1);
          final bottom = image.getPixel(x, y + 1);
          final left = image.getPixel(x - 1, y);
          final right = image.getPixel(x + 1, y);

          // 计算灰度值
          final centerGray = (center.r + center.g + center.b) / 3;
          final topGray = (top.r + top.g + top.b) / 3;
          final bottomGray = (bottom.r + bottom.g + bottom.b) / 3;
          final leftGray = (left.r + left.g + left.b) / 3;
          final rightGray = (right.r + right.g + right.b) / 3;

          // 拉普拉斯算子
          final laplacian =
              4 * centerGray - topGray - bottomGray - leftGray - rightGray;
          laplacianVariance += laplacian * laplacian;
        }
      }

      // 归一化结果
      final normalizedVariance =
          laplacianVariance / ((image.width - 2) * (image.height - 2));
      return 1.0 - math.sqrt(normalizedVariance);
    } catch (e) {
      print('检测模糊度失败: $e');
      return 1.0;
    }
  }

  /// 分析舌苔特征
  Future<({TongueCoatingFeature feature, double confidence})>
      _analyzeCoatingFeature() async {
    if (_processedImage == null || _tongueCoatingRegion == null) {
      return (feature: TongueCoatingFeature.thinWhite, confidence: 0.5);
    }

    try {
      // 获取舌苔区域的平均颜色和质地特征
      final color = _getAverageColor(_tongueCoatingRegion!);
      final r = (color >> 16) & 0xFF;
      final g = (color >> 8) & 0xFF;
      final b = color & 0xFF;

      // 颜色特征
      final colorBrightness = (r + g + b) / 3.0 / 255.0;
      final yellowness = (r + g) / math.max(1, b * 2.0);
      final whiteness = math.min(r, math.min(g, b)) / 255.0;

      // 质地特征 - 舌苔厚度可以通过纹理复杂度判断
      final textureVariance = _getColorVariance(_tongueCoatingRegion!);
      final textureComplexity = math.sqrt(textureVariance) / 60; // 归一化

      // 决策逻辑
      TongueCoatingFeature feature;
      double confidence = 0.7;

      if (yellowness > 1.5 && g > 150 && b < 100) {
        feature = TongueCoatingFeature.yellow;
        confidence = 0.65 + yellowness / 10;
      } else if (whiteness > 0.75 && colorBrightness > 0.8) {
        feature = TongueCoatingFeature.white;
        confidence = 0.7 + whiteness / 5;
      } else if (r < 60 && g < 60 && b < 60) {
        feature = TongueCoatingFeature.blackish;
        confidence = 0.65 + (255 - (r + g + b) / 3) / 255;
      } else if (textureComplexity > 0.4) {
        // 厚苔通常纹理复杂度高
        feature = TongueCoatingFeature.thickWhite;
        confidence = 0.65 + textureComplexity / 2;
      } else if (textureComplexity < 0.2 && colorBrightness > 0.5) {
        // 薄苔通常纹理复杂度低
        feature = TongueCoatingFeature.thinWhite;
        confidence = 0.7 + (1 - textureComplexity);
      } else if (r > 180 && g < 100 && b < 100) {
        feature = TongueCoatingFeature.mirror;
        confidence = 0.65 + r / 255;
      } else {
        // 默认为薄白苔
        feature = TongueCoatingFeature.thinWhite;
        confidence = 0.7;
      }

      confidence = confidence.clamp(0.6, 0.95);
      return (feature: feature, confidence: confidence);
    } catch (e) {
      print('舌苔分析失败: $e');
      return (feature: TongueCoatingFeature.thinWhite, confidence: 0.5);
    }
  }

  /// 分析舌形特征
  Future<({TongueShapeFeature feature, double confidence})>
      _analyzeShapeFeature() async {
    if (_processedImage == null || _tongueRegion == null) {
      return (feature: TongueShapeFeature.normal, confidence: 0.5);
    }

    try {
      // 舌形分析需要考虑舌头的整体形状、边缘特征和比例
      // 获取舌头区域的宽高比
      final aspectRatio = _tongueRegion!.width / _tongueRegion!.height;

      // 获取舌头边缘特征 - 通过边缘像素分析
      final edgeRoughness = _analyzeEdgeRoughness();

      // 获取舌头的体积感 - 通过中心区域和边缘区域的颜色差异估计
      final volumeIndex = _estimateTongueVolume();

      // 决策逻辑
      TongueShapeFeature feature;
      double confidence = 0.7;

      if (aspectRatio > 1.8) {
        // 长舌
        feature = TongueShapeFeature.enlarged;
        confidence = 0.65 + aspectRatio / 10;
      } else if (aspectRatio < 1.2) {
        // 短舌
        feature = TongueShapeFeature.shortened;
        confidence = 0.65 + (1.5 - aspectRatio) / 2;
      } else if (edgeRoughness > 0.4) {
        // 齿痕舌
        feature = TongueShapeFeature.toothMarked;
        confidence = 0.6 + edgeRoughness / 2;
      } else if (volumeIndex < 0.6) {
        // 瘦舌
        feature = TongueShapeFeature.thin;
        confidence = 0.65 + (1 - volumeIndex);
      } else if (volumeIndex > 0.8) {
        // 胖舌
        feature = TongueShapeFeature.enlarged;
        confidence = 0.65 + volumeIndex / 5;
      } else {
        // 正常舌
        feature = TongueShapeFeature.normal;
        confidence = 0.75;
      }

      confidence = confidence.clamp(0.6, 0.95);
      return (feature: feature, confidence: confidence);
    } catch (e) {
      print('舌形分析失败: $e');
      return (feature: TongueShapeFeature.normal, confidence: 0.5);
    }
  }

  /// 分析舌下络脉特征
  Future<({TongueVeinFeature feature, double confidence})>
      _analyzeVeinFeature() async {
    if (_processedImage == null || _tongueVeinRegion == null) {
      return (feature: TongueVeinFeature.normal, confidence: 0.5);
    }

    try {
      // 获取舌下区域的颜色特征
      final color = _getAverageColor(_tongueVeinRegion!);
      final r = (color >> 16) & 0xFF;
      final g = (color >> 8) & 0xFF;
      final b = color & 0xFF;

      // 血管特征 - 通过颜色对比度和纹理特征检测
      final purpleness = (r * 0.5 + b * 0.6) / math.max(1, g);
      final blueness = b / math.max(1, (r + g) / 2);

      // 边缘检测 - 检测血管纹路
      final edgeIntensity = _detectEdgesInRegion(_tongueVeinRegion!);

      // 决策逻辑
      TongueVeinFeature feature;
      double confidence = 0.7;

      if (purpleness > 1.3 && edgeIntensity > 0.4) {
        feature = TongueVeinFeature.purple;
        confidence = 0.65 + purpleness / 8 + edgeIntensity / 10;
      } else if (blueness > 1.2 && b > 120) {
        feature = TongueVeinFeature.swollen;
        confidence = 0.65 + blueness / 5;
      } else if (edgeIntensity > 0.5) {
        feature = TongueVeinFeature.swollen;
        confidence = 0.6 + edgeIntensity / 5;
      } else if (r > 200 && g < 130 && b < 130) {
        feature = TongueVeinFeature.normal;
        confidence = 0.65 + r / 255;
      } else {
        // 正常络脉
        feature = TongueVeinFeature.normal;
        confidence = 0.75;
      }

      confidence = confidence.clamp(0.6, 0.95);
      return (feature: feature, confidence: confidence);
    } catch (e) {
      print('舌下络脉分析失败: $e');
      return (feature: TongueVeinFeature.normal, confidence: 0.5);
    }
  }

  /// 分析舌边缘粗糙度
  double _analyzeEdgeRoughness() {
    if (_processedImage == null || _tongueRegion == null) return 0.0;

    try {
      final image = _processedImage!;
      final region = _tongueRegion!;

      // 提取舌头边缘
      final left = region.left.toInt();
      final top = region.top.toInt();
      final right = region.right.toInt();
      final bottom = region.bottom.toInt();

      // 边缘像素数组
      final List<bool> edgePixels = [];

      // 检查边缘的像素（简化版本）
      for (int y = top; y < bottom; y += 3) {
        // 间隔采样提高性能
        for (int d = -2; d <= 2; d++) {
          final int x1 = left + d;
          final int x2 = right + d;

          if (x1 >= 0 && x1 < image.width && y >= 0 && y < image.height) {
            final pixel = image.getPixel(x1, y);
            edgePixels.add(_isTonguePixel(pixel.r, pixel.g, pixel.b));
          }

          if (x2 >= 0 && x2 < image.width && y >= 0 && y < image.height) {
            final pixel = image.getPixel(x2, y);
            edgePixels.add(_isTonguePixel(pixel.r, pixel.g, pixel.b));
          }
        }
      }

      for (int x = left; x < right; x += 3) {
        for (int d = -2; d <= 2; d++) {
          final int y1 = top + d;
          final int y2 = bottom + d;

          if (x >= 0 && x < image.width && y1 >= 0 && y1 < image.height) {
            final pixel = image.getPixel(x, y1);
            edgePixels.add(_isTonguePixel(pixel.r, pixel.g, pixel.b));
          }

          if (x >= 0 && x < image.width && y2 >= 0 && y2 < image.height) {
            final pixel = image.getPixel(x, y2);
            edgePixels.add(_isTonguePixel(pixel.r, pixel.g, pixel.b));
          }
        }
      }

      // 计算边缘变化频率 - 从舌到非舌的转换次数
      int transitions = 0;
      for (int i = 1; i < edgePixels.length; i++) {
        if (edgePixels[i] != edgePixels[i - 1]) {
          transitions++;
        }
      }

      // 归一化粗糙度值
      final roughness = transitions / math.max(1, edgePixels.length / 2);
      return roughness.clamp(0.0, 1.0);
    } catch (e) {
      print('分析舌边缘粗糙度失败: $e');
      return 0.0;
    }
  }

  /// 评估舌头的体积
  double _estimateTongueVolume() {
    if (_processedImage == null || _tongueRegion == null) return 0.5;

    try {
      // 计算中心区域和边缘区域的颜色差异
      final region = _tongueRegion!;
      final centerRegion = Rect.fromCenter(
        center: region.center,
        width: region.width * 0.6,
        height: region.height * 0.6,
      );

      // 获取中心和整体区域的平均颜色
      final centerColor = _getAverageColor(centerRegion);
      final overallColor = _getAverageColor(region);

      // 提取RGB分量
      final centerR = (centerColor >> 16) & 0xFF;
      final centerG = (centerColor >> 8) & 0xFF;
      final centerB = centerColor & 0xFF;

      final overallR = (overallColor >> 16) & 0xFF;
      final overallG = (overallColor >> 8) & 0xFF;
      final overallB = overallColor & 0xFF;

      // 计算颜色差异
      final diff = math.sqrt(math.pow(centerR - overallR, 2) +
          math.pow(centerG - overallG, 2) +
          math.pow(centerB - overallB, 2));

      // 归一化体积指数
      // 差异越小，舌头越平坦；差异越大，舌头体积感越强
      final volumeIndex = 1.0 - (diff / 150).clamp(0.0, 1.0);
      return volumeIndex;
    } catch (e) {
      print('评估舌头体积失败: $e');
      return 0.5;
    }
  }

  /// 在区域中检测边缘强度
  double _detectEdgesInRegion(Rect region) {
    if (_processedImage == null) return 0.0;

    try {
      final image = _processedImage!;
      final left = region.left.toInt();
      final top = region.top.toInt();
      final right = region.right.toInt();
      final bottom = region.bottom.toInt();

      double totalEdgeStrength = 0.0;
      int pixelCount = 0;

      // 使用Sobel算子检测边缘
      for (int y = top + 1; y < bottom - 1; y++) {
        for (int x = left + 1; x < right - 1; x++) {
          if (x >= 0 && x < image.width && y >= 0 && y < image.height) {
            // 计算水平和垂直梯度
            final gx = _computeGradientX(image, x, y);
            final gy = _computeGradientY(image, x, y);

            // 梯度幅值
            final magnitude = math.sqrt(gx * gx + gy * gy);
            totalEdgeStrength += magnitude;
            pixelCount++;
          }
        }
      }

      if (pixelCount == 0) return 0.0;

      // 归一化边缘强度
      final averageEdgeStrength = totalEdgeStrength / pixelCount;
      return (averageEdgeStrength / 100).clamp(0.0, 1.0);
    } catch (e) {
      print('检测边缘强度失败: $e');
      return 0.0;
    }
  }

  /// 计算水平梯度
  double _computeGradientX(img.Image image, int x, int y) {
    final left = image.getPixel(x - 1, y);
    final right = image.getPixel(x + 1, y);

    final leftGray = (left.r + left.g + left.b) / 3.0;
    final rightGray = (right.r + right.g + right.b) / 3.0;

    return rightGray - leftGray;
  }

  /// 计算垂直梯度
  double _computeGradientY(img.Image image, int x, int y) {
    final top = image.getPixel(x, y - 1);
    final bottom = image.getPixel(x, y + 1);

    final topGray = (top.r + top.g + top.b) / 3.0;
    final bottomGray = (bottom.r + bottom.g + bottom.b) / 3.0;

    return bottomGray - topGray;
  }

  /// 将Rect转换为JSON
  Map<String, double> _rectToJson(Rect rect) {
    return {
      'left': rect.left,
      'top': rect.top,
      'right': rect.right,
      'bottom': rect.bottom,
      'width': rect.width,
      'height': rect.height,
    };
  }

  /// 从图像检测舌头，返回置信度（0-1）
  double detectTongueFromImage(img.Image image) {
    try {
      // 缩放图像以提高处理速度
      final scaledImage = img.copyResize(image, width: 300);

      // 获取红色区域比例作为舌头检测的简单方法
      double redPixelRatio = _calculateRedPixelRatio(scaledImage);

      // 检测圆形/椭圆形状比例
      double shapeScore = _calculateTongueShapeScore(scaledImage);

      // 综合评分（红色占比权重0.7，形状权重0.3）
      double score = redPixelRatio * 0.7 + shapeScore * 0.3;

      // 添加一些边界条件
      // 如果红色太少，降低评分
      if (redPixelRatio < 0.05) score *= 0.5;

      // 如果图像太暗或太亮，降低评分
      double brightness = _calculateBrightness(scaledImage);
      if (brightness < 0.2 || brightness > 0.8) score *= 0.7;

      return score;
    } catch (e) {
      debugPrint('舌头检测失败: $e');
      return 0.0;
    }
  }

  /// 计算图像中红色像素的比例
  double _calculateRedPixelRatio(img.Image image) {
    int redPixels = 0;
    int totalPixels = image.width * image.height;

    for (int y = 0; y < image.height; y++) {
      for (int x = 0; x < image.width; x++) {
        final pixel = image.getPixel(x, y);
        final r = pixel.r;
        final g = pixel.g;
        final b = pixel.b;

        // 红色成分显著高于其他成分
        if (r > 100 && r > g * 1.5 && r > b * 1.5) {
          redPixels++;
        }
      }
    }

    return redPixels / totalPixels;
  }

  /// 计算可能是舌头形状的得分
  double _calculateTongueShapeScore(img.Image image) {
    // 简单实现：通过边缘检测和椭圆拟合来判断
    // 在实际应用中，这需要更复杂的计算机视觉算法

    // 此处为简化实现
    // 真实应用需要使用边缘检测、形状分析等更复杂算法
    return 0.5; // 默认中等可能性
  }

  /// 计算图像亮度
  double _calculateBrightness(img.Image image) {
    int sum = 0;
    int totalPixels = image.width * image.height;

    for (int y = 0; y < image.height; y++) {
      for (int x = 0; x < image.width; x++) {
        final pixel = image.getPixel(x, y);
        final r = pixel.r;
        final g = pixel.g;
        final b = pixel.b;

        // 计算亮度（简化版本）
        int brightness = (0.299 * r + 0.587 * g + 0.114 * b).round();
        sum += brightness;
      }
    }

    // 返回范围0-1的亮度值
    return sum / (totalPixels * 255);
  }
}
