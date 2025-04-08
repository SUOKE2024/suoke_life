import 'dart:async';
import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/theme/tcm_chart_themes.dart';
import 'package:suoke_life/core/widgets/app_widgets.dart' as app_widgets;

// 渲染更新频率常量
const int _kWebUpdatesPerSecond = 10; // Web平台每秒更新10次
const int _kNativeUpdatesPerSecond = 30; // 原生平台每秒更新30次

/// 脉象类型枚举
enum PulseType {
  /// 浮脉 - 脉位于皮肤表面，轻取即得
  floating,

  /// 沉脉 - 脉位于肌肉深处，重按才显
  sinking,

  /// 迟脉 - 一息不足四至
  slow,

  /// 数脉 - 一息五至以上
  rapid,

  /// 虚脉 - 脉来无力
  deficient,

  /// 实脉 - 脉来有力
  excess,

  /// 滑脉 - 如珠走盘，往来流利
  slippery,

  /// 涩脉 - 往来艰涩
  rough,

  /// 弦脉 - 如弦按之不移
  wiry,

  /// 细脉 - 脉细如线
  thin,

  /// 洪脉 - 脉来盛大而有力
  surging,

  /// 微脉 - 脉细而欲绝
  faint,
}

/// 脉象数据模型
class PulseData {
  /// 脉象点数据
  final List<double> values;

  /// 脉象类型
  final PulseType type;

  /// 频率（每分钟次数）
  final int frequency;

  /// 强度（0-1.0）
  final double strength;

  /// 规则性（0-1.0）
  final double regularity;

  /// 构造函数
  const PulseData({
    required this.values,
    required this.type,
    required this.frequency,
    required this.strength,
    required this.regularity,
  });

  /// 从样本数据创建
  factory PulseData.fromSample(PulseType type) {
    final random = math.Random();
    final baseFrequency = 72; // 基础频率

    // 根据脉象类型调整参数
    double strengthFactor = 0.7;
    double regularityFactor = 0.8;
    int frequencyAdjust = 0;

    switch (type) {
      case PulseType.floating:
        strengthFactor = 0.6;
        regularityFactor = 0.85;
        break;
      case PulseType.sinking:
        strengthFactor = 0.8;
        regularityFactor = 0.9;
        break;
      case PulseType.slow:
        frequencyAdjust = -15;
        regularityFactor = 0.75;
        break;
      case PulseType.rapid:
        frequencyAdjust = 20;
        regularityFactor = 0.7;
        break;
      case PulseType.deficient:
        strengthFactor = 0.4;
        regularityFactor = 0.6;
        break;
      case PulseType.excess:
        strengthFactor = 0.9;
        regularityFactor = 0.85;
        break;
      case PulseType.slippery:
        strengthFactor = 0.75;
        regularityFactor = 0.95;
        break;
      case PulseType.rough:
        strengthFactor = 0.65;
        regularityFactor = 0.5;
        break;
      case PulseType.wiry:
        strengthFactor = 0.8;
        regularityFactor = 0.9;
        break;
      case PulseType.thin:
        strengthFactor = 0.3;
        regularityFactor = 0.7;
        break;
      case PulseType.surging:
        strengthFactor = 1.0;
        regularityFactor = 0.8;
        break;
      case PulseType.faint:
        strengthFactor = 0.2;
        regularityFactor = 0.6;
        break;
    }

    // 生成波形数据
    List<double> values = _generatePulseWave(
      type: type,
      points: 100,
      strength: strengthFactor,
      regularity: regularityFactor,
    );

    return PulseData(
      values: values,
      type: type,
      frequency: baseFrequency + frequencyAdjust,
      strength: strengthFactor,
      regularity: regularityFactor,
    );
  }

  /// 生成脉象波形
  static List<double> _generatePulseWave({
    required PulseType type,
    required int points,
    required double strength,
    required double regularity,
  }) {
    final random = math.Random();
    final values = <double>[];
    final cycles = (points / 20).ceil(); // 每20个点一个周期

    // 基础波形函数
    double baseWave(double x) {
      switch (type) {
        case PulseType.wiry:
          // 弦脉 - 尖锐波形
          return math.sin(x) * strength * (math.sin(x) > 0 ? 1 : 0.3);
        case PulseType.slippery:
          // 滑脉 - 圆滑波形
          return 0.5 * strength * (1 + math.sin(x));
        case PulseType.rough:
          // 涩脉 - 不规则波形
          return 0.5 * strength * (1 + math.sin(x) + 0.2 * math.sin(3 * x));
        case PulseType.surging:
          // 洪脉 - 大幅波形
          return 0.7 * strength * (1 + math.sin(x));
        case PulseType.thin:
        case PulseType.faint:
          // 细/微脉 - 小幅波形
          return 0.3 * strength * (1 + math.sin(x));
        case PulseType.floating:
          // 浮脉 - 上高下低
          return 0.5 * strength * (1 + math.sin(x) - 0.3 * math.cos(x));
        case PulseType.sinking:
          // 沉脉 - 上低下高
          return 0.5 * strength * (1 + math.sin(x) + 0.3 * math.cos(x));
        case PulseType.slow:
        case PulseType.rapid:
        case PulseType.deficient:
        case PulseType.excess:
        default:
          // 默认波形
          return 0.5 * strength * (1 + math.sin(x));
      }
    }

    // 生成波形数据
    for (int i = 0; i < points; i++) {
      // 计算基础波形
      final x = 2 * math.pi * i / (points / cycles);
      double value = baseWave(x);

      // 增加随机变化模拟不规则性
      final noise = (1.0 - regularity) * (random.nextDouble() * 0.4 - 0.2);
      value += noise;

      // 限制在0-1范围内
      value = value.clamp(0.0, 1.0);
      values.add(value);
    }

    return values;
  }

  /// 获取脉象类型描述
  static String getPulseTypeDescription(PulseType type) {
    switch (type) {
      case PulseType.floating:
        return '浮脉';
      case PulseType.sinking:
        return '沉脉';
      case PulseType.slow:
        return '迟脉';
      case PulseType.rapid:
        return '数脉';
      case PulseType.deficient:
        return '虚脉';
      case PulseType.excess:
        return '实脉';
      case PulseType.slippery:
        return '滑脉';
      case PulseType.rough:
        return '涩脉';
      case PulseType.wiry:
        return '弦脉';
      case PulseType.thin:
        return '细脉';
      case PulseType.surging:
        return '洪脉';
      case PulseType.faint:
        return '微脉';
    }
  }

  /// 获取脉象临床意义
  static String getPulseClinicalMeaning(PulseType type) {
    switch (type) {
      case PulseType.floating:
        return '多见于表证、阳盛、气虚';
      case PulseType.sinking:
        return '多见于里证、阴盛、气虚下陷';
      case PulseType.slow:
        return '多见于寒证、阳虚';
      case PulseType.rapid:
        return '多见于热证、阴虚';
      case PulseType.deficient:
        return '多见于气血不足、阴阳两虚';
      case PulseType.excess:
        return '多见于实证、邪气盛';
      case PulseType.slippery:
        return '多见于痰饮、食积、妊娠';
      case PulseType.rough:
        return '多见于气血不足、血瘀';
      case PulseType.wiry:
        return '多见于肝胆病、疼痛、气滞血瘀';
      case PulseType.thin:
        return '多见于气血两虚、津液不足';
      case PulseType.surging:
        return '多见于阳盛、热盛';
      case PulseType.faint:
        return '多见于气血大虚、阴阳欲脱';
    }
  }
}

/// 脉搏图像处理器
class PulseImageProcessor {
  /// 从图像帧中提取的原始信号数据
  final List<double> _rawSignalData = [];

  /// 处理后的信号数据
  final List<double> _processedSignalData = [];

  /// 信号缓冲区大小
  static const int _bufferSize = 150;

  /// 每秒分析帧数
  static const int _framesPerSecond = 30;

  /// 最后检测到的心率
  double _lastDetectedHeartRate = 0;

  /// 最后检测到的脉象类型
  PulseType? _lastDetectedPulseType;

  /// 当前帧索引
  int _frameIndex = 0;

  /// 连续检测到心率的次数
  int _heartRateDetectionCount = 0;

  /// 脉象特征
  Map<String, double> _pulseFeatures = {
    'strength': 0.0, // 脉搏强度
    'regularity': 0.0, // 规律性
    'width': 0.0, // 脉宽
    'rate': 0.0, // 脉率
    'depth': 0.0, // 深浅
    'tension': 0.0, // 紧张度
  };

  /// 处理相机图像帧
  Future<Map<String, dynamic>?> processFrame(CameraImage image) async {
    // 只分析每 _framesPerSecond/10 帧，减少计算压力
    if (_frameIndex++ % (_framesPerSecond ~/ 10) != 0) {
      return null;
    }

    // 从图像中提取红色通道平均值（手指血液中的红色变化）
    final double redChannelValue = _extractRedChannelValue(image);

    // 添加到原始信号数据
    _addToRawSignalBuffer(redChannelValue);

    // 如果没有足够的数据，返回null
    if (_rawSignalData.length < _bufferSize / 2) {
      return null;
    }

    // 处理信号
    _processSignal();

    // 检测特征
    final features = _detectFeatures();

    // 如果特征检测成功，更新最后检测到的心率和脉象类型
    if (features != null) {
      _pulseFeatures = features;
      _lastDetectedHeartRate = features['rate'] ?? 0;
      _lastDetectedPulseType = _determinePulseType(features);
      _heartRateDetectionCount++;
    }

    // 如果已经检测到足够次数的心率，返回分析结果
    if (_heartRateDetectionCount >= 5 && _lastDetectedPulseType != null) {
      return {
        'pulseType': _lastDetectedPulseType,
        'heartRate': _lastDetectedHeartRate.round(),
        'strength': _pulseFeatures['strength'],
        'regularity': _pulseFeatures['regularity'],
        'processedData': List<double>.from(_processedSignalData),
      };
    }

    return null;
  }

  /// 从图像中提取红色通道平均值
  double _extractRedChannelValue(CameraImage image) {
    try {
      // 根据图像格式提取红色通道
      if (image.format.group == ImageFormatGroup.yuv420) {
        // YUV格式处理（大多数Android设备）
        final int width = image.width;
        final int height = image.height;
        final int uvRowStride = image.planes[1].bytesPerRow;
        final int uvPixelStride = image.planes[1].bytesPerPixel ?? 1;

        // 取中心区域的Y值（亮度）
        final Uint8List yBuffer = image.planes[0].bytes;
        final int centerOffset = ((height ~/ 2) * width) + (width ~/ 2);
        final int size = math.min(width, height) ~/ 3;

        double sum = 0;
        int count = 0;

        // 计算中心区域的平均亮度
        for (int y = -size ~/ 2; y < size ~/ 2; y++) {
          for (int x = -size ~/ 2; x < size ~/ 2; x++) {
            final int pos = centerOffset + y * width + x;
            if (pos >= 0 && pos < yBuffer.length) {
              sum += yBuffer[pos];
              count++;
            }
          }
        }

        return count > 0 ? sum / count / 255.0 : 0.5;
      } else if (image.format.group == ImageFormatGroup.bgra8888) {
        // BGRA格式处理（iOS设备）
        final Uint8List buffer = image.planes[0].bytes;
        final int bytesPerPixel = image.planes[0].bytesPerPixel ?? 4;
        final int width = image.width;
        final int height = image.height;

        // 取中心区域的红色通道
        final int centerX = width ~/ 2;
        final int centerY = height ~/ 2;
        final int size = math.min(width, height) ~/ 3;

        double sum = 0;
        int count = 0;

        // 计算中心区域红色通道的平均值
        for (int y = centerY - size ~/ 2; y < centerY + size ~/ 2; y++) {
          for (int x = centerX - size ~/ 2; x < centerX + size ~/ 2; x++) {
            final int pos = (y * width + x) * bytesPerPixel;
            if (pos + 2 < buffer.length) {
              // BGRA格式中，红色在索引2位置
              sum += buffer[pos + 2];
              count++;
            }
          }
        }

        return count > 0 ? sum / count / 255.0 : 0.5;
      }

      // 如果无法识别格式，返回默认值
      return 0.5;
    } catch (e) {
      print('提取红色通道出错: $e');
      return 0.5;
    }
  }

  /// 添加数据到原始信号缓冲区
  void _addToRawSignalBuffer(double value) {
    _rawSignalData.add(value);

    // 限制缓冲区大小
    if (_rawSignalData.length > _bufferSize) {
      _rawSignalData.removeAt(0);
    }
  }

  /// 处理信号（应用平滑和归一化）
  void _processSignal() {
    // 应用移动平均平滑
    final List<double> smoothed = _applyMovingAverage(_rawSignalData, 5);

    // 带通滤波（保留0.5-5Hz的频率，对应30-300 BPM的心率）
    final List<double> filtered = _applyBandpassFilter(smoothed);

    // 归一化到0-1范围
    final List<double> normalized = _normalizeSignal(filtered);

    // 更新处理后的信号
    _processedSignalData.clear();
    _processedSignalData.addAll(normalized);
  }

  /// 应用移动平均平滑
  List<double> _applyMovingAverage(List<double> data, int windowSize) {
    final List<double> result = List<double>.filled(data.length, 0);

    for (int i = 0; i < data.length; i++) {
      double sum = 0;
      int count = 0;

      for (int j = math.max(0, i - windowSize ~/ 2);
          j < math.min(data.length, i + windowSize ~/ 2 + 1);
          j++) {
        sum += data[j];
        count++;
      }

      result[i] = sum / count;
    }

    return result;
  }

  /// 应用简化的带通滤波器
  List<double> _applyBandpassFilter(List<double> data) {
    // 简化的带通滤波实现
    // 在实际应用中，这里可以使用更复杂的滤波器设计

    final List<double> result = List<double>.from(data);

    // 移除长期趋势（高通滤波）
    double mean = result.reduce((a, b) => a + b) / result.length;
    for (int i = 0; i < result.length; i++) {
      result[i] -= mean;
    }

    // 再次应用移动平均（低通滤波）
    return _applyMovingAverage(result, 3);
  }

  /// 归一化信号到0-1范围
  List<double> _normalizeSignal(List<double> data) {
    if (data.isEmpty) return [];

    double min = data.reduce(math.min);
    double max = data.reduce(math.max);

    // 避免除以零
    double range = max - min;
    if (range.abs() < 0.0001) return List<double>.filled(data.length, 0.5);

    return data.map((value) => (value - min) / range).toList();
  }

  /// 检测脉搏特征
  Map<String, double>? _detectFeatures() {
    if (_processedSignalData.length < 30) return null;

    try {
      // 查找峰值
      final List<int> peakIndices = _findPeaks(_processedSignalData);

      // 如果峰值不足，无法检测
      if (peakIndices.length < 2) return null;

      // 计算峰值间隔
      final List<int> intervals = [];
      for (int i = 1; i < peakIndices.length; i++) {
        intervals.add(peakIndices[i] - peakIndices[i - 1]);
      }

      // 计算心率
      double averageInterval =
          intervals.reduce((a, b) => a + b) / intervals.length;
      double heartRate = 60.0 *
          _framesPerSecond /
          (averageInterval * (_framesPerSecond ~/ 10));

      // 限制在合理范围内
      heartRate = heartRate.clamp(40.0, 200.0);

      // 计算振幅（强度）
      double amplitudeSum = 0;
      for (final int peakIndex in peakIndices) {
        if (peakIndex > 0 && peakIndex < _processedSignalData.length) {
          amplitudeSum += _processedSignalData[peakIndex];
        }
      }
      double strength = amplitudeSum / peakIndices.length;

      // 计算规律性（间隔的标准差）
      double meanInterval =
          intervals.reduce((a, b) => a + b) / intervals.length;
      double variance = intervals.fold(0.0,
              (sum, interval) => sum + math.pow(interval - meanInterval, 2)) /
          intervals.length;
      double std = math.sqrt(variance);
      double regularity = 1.0 - math.min(1.0, std / meanInterval);

      // 计算脉宽（峰值宽度）
      double width = _calculatePulseWidth(peakIndices);

      // 深度和紧张度是更复杂的特征，暂时使用随机值和其他特征的组合
      double depth = 0.3 + 0.4 * (1.0 - strength);
      double tension = 0.3 + 0.7 * math.min(1.0, strength + 0.3 * regularity);

      return {
        'strength': strength.clamp(0.0, 1.0),
        'regularity': regularity.clamp(0.0, 1.0),
        'width': width.clamp(0.0, 1.0),
        'rate': heartRate,
        'depth': depth.clamp(0.0, 1.0),
        'tension': tension.clamp(0.0, 1.0),
      };
    } catch (e) {
      print('特征检测出错: $e');
      return null;
    }
  }

  /// 查找信号中的峰值
  List<int> _findPeaks(List<double> data) {
    final List<int> peaks = [];

    // 简单的峰值检测
    for (int i = 2; i < data.length - 2; i++) {
      if (data[i] > data[i - 1] &&
          data[i] > data[i - 2] &&
          data[i] > data[i + 1] &&
          data[i] > data[i + 2] &&
          data[i] > 0.5) {
        // 只考虑高于中值的峰
        peaks.add(i);
      }
    }

    return peaks;
  }

  /// 计算脉宽（峰值宽度）
  double _calculatePulseWidth(List<int> peakIndices) {
    if (peakIndices.isEmpty || _processedSignalData.isEmpty) return 0.5;

    double widthSum = 0;
    int validPeaks = 0;

    for (final int peakIndex in peakIndices) {
      if (peakIndex > 5 && peakIndex < _processedSignalData.length - 5) {
        // 查找半高宽
        double peakValue = _processedSignalData[peakIndex];
        double halfHeight = peakValue / 2;

        // 向左查找半高点
        int leftIndex = peakIndex;
        while (leftIndex > 0 && _processedSignalData[leftIndex] > halfHeight) {
          leftIndex--;
        }

        // 向右查找半高点
        int rightIndex = peakIndex;
        while (rightIndex < _processedSignalData.length - 1 &&
            _processedSignalData[rightIndex] > halfHeight) {
          rightIndex++;
        }

        // 计算半高宽
        double width = (rightIndex - leftIndex) / (_framesPerSecond / 2.0);
        widthSum += width;
        validPeaks++;
      }
    }

    // 归一化宽度到0-1范围
    if (validPeaks == 0) return 0.5;
    double avgWidth = widthSum / validPeaks;
    return math.min(1.0, avgWidth / 0.3); // 0.3秒作为标准宽度
  }

  /// 根据特征确定脉象类型
  PulseType _determinePulseType(Map<String, double> features) {
    // 根据中医脉象特征规则判断脉象类型
    double rate = features['rate'] ?? 72;
    double strength = features['strength'] ?? 0.5;
    double regularity = features['regularity'] ?? 0.5;
    double width = features['width'] ?? 0.5;
    double depth = features['depth'] ?? 0.5;
    double tension = features['tension'] ?? 0.5;

    // 脉率判断
    if (rate < 60) {
      return PulseType.slow; // 迟脉
    } else if (rate > 90) {
      return PulseType.rapid; // 数脉
    }

    // 脉力判断
    if (strength < 0.4) {
      if (regularity < 0.5) {
        return PulseType.rough; // 涩脉
      } else {
        return strength < 0.3 ? PulseType.faint : PulseType.deficient; // 微脉或虚脉
      }
    } else if (strength > 0.7) {
      if (width > 0.7) {
        return PulseType.surging; // 洪脉
      } else {
        return PulseType.excess; // 实脉
      }
    }

    // 脉位判断
    if (depth < 0.4) {
      return PulseType.floating; // 浮脉
    } else if (depth > 0.7) {
      return PulseType.sinking; // 沉脉
    }

    // 脉体判断
    if (tension > 0.7) {
      return PulseType.wiry; // 弦脉
    } else if (width < 0.4) {
      return PulseType.thin; // 细脉
    } else if (regularity > 0.7 && strength > 0.6) {
      return PulseType.slippery; // 滑脉
    }

    // 默认返回滑脉
    return PulseType.slippery;
  }

  /// 重置分析状态
  void reset() {
    _rawSignalData.clear();
    _processedSignalData.clear();
    _frameIndex = 0;
    _heartRateDetectionCount = 0;
    _lastDetectedHeartRate = 0;
    _lastDetectedPulseType = null;
  }
}

/// 脉诊状态Provider
final pulseDiagnosisStateProvider =
    StateNotifierProvider<PulseDiagnosisNotifier, PulseDiagnosisState>((ref) {
  return PulseDiagnosisNotifier();
});

/// 脉诊状态
class PulseDiagnosisState {
  /// 当前脉象数据
  final PulseData? pulseData;

  /// 是否正在分析
  final bool isAnalyzing;

  /// 是否使用相机
  final bool isUsingCamera;

  /// 相机控制器
  final CameraController? cameraController;

  /// 分析结果
  final List<PulseAnalysisResult>? analysisResults;

  /// 原始信号数据
  final List<double>? signalData;

  /// 信号数据索引（用于动画）
  final int? signalDataIndex;

  /// 构造函数
  const PulseDiagnosisState({
    this.pulseData,
    this.isAnalyzing = false,
    this.isUsingCamera = false,
    this.cameraController,
    this.analysisResults,
    this.signalData,
    this.signalDataIndex,
  });

  /// 复制对象
  PulseDiagnosisState copyWith({
    PulseData? pulseData,
    bool? isAnalyzing,
    bool? isUsingCamera,
    CameraController? cameraController,
    List<PulseAnalysisResult>? analysisResults,
    List<double>? signalData,
    int? signalDataIndex,
  }) {
    return PulseDiagnosisState(
      pulseData: pulseData ?? this.pulseData,
      isAnalyzing: isAnalyzing ?? this.isAnalyzing,
      isUsingCamera: isUsingCamera ?? this.isUsingCamera,
      cameraController: cameraController ?? this.cameraController,
      analysisResults: analysisResults ?? this.analysisResults,
      signalData: signalData ?? this.signalData,
      signalDataIndex: signalDataIndex ?? this.signalDataIndex,
    );
  }
}

/// 脉象分析结果
class PulseAnalysisResult {
  /// 脉象类型
  final PulseType type;

  /// 匹配概率 (0-1.0)
  final double probability;

  /// 构造函数
  const PulseAnalysisResult({
    required this.type,
    required this.probability,
  });
}

/// 脉诊状态管理器
class PulseDiagnosisNotifier extends StateNotifier<PulseDiagnosisState> {
  PulseDiagnosisNotifier() : super(const PulseDiagnosisState());

  Timer? _animationTimer;

  /// 图像处理器
  final PulseImageProcessor _imageProcessor = PulseImageProcessor();

  /// 图像处理计时器
  Timer? _processingTimer;

  /// 启动脉象模拟
  void startPulseSimulation(PulseType type) {
    // 停止相机分析（如果正在进行）
    if (state.isUsingCamera) {
      stopCameraAnalysis();
    }

    // 生成模拟脉象数据
    final pulseData = PulseData.fromSample(type);

    // 更新状态
    state = state.copyWith(
      pulseData: pulseData,
      isAnalyzing: false,
      isUsingCamera: false,
    );

    // 模拟分析
    analyzePulse();
  }

  /// 分析脉象
  Future<void> analyzePulse() async {
    // 设置分析状态
    state = state.copyWith(isAnalyzing: true);

    // 模拟分析过程（实际应用中可能需要调用AI服务）
    await Future.delayed(const Duration(seconds: 2));

    // 生成分析结果
    final mainType = state.pulseData?.type ?? PulseType.slippery;
    final analysisResults = <PulseAnalysisResult>[];

    // 主类型结果
    analysisResults.add(PulseAnalysisResult(
      type: mainType,
      probability: 0.85,
    ));

    // 随机添加2-3个次要类型
    final random = math.Random();
    final allTypes = PulseType.values.toList()..remove(mainType);
    allTypes.shuffle();

    for (int i = 0; i < 3; i++) {
      if (i < allTypes.length) {
        analysisResults.add(PulseAnalysisResult(
          type: allTypes[i],
          probability: 0.7 - i * 0.2,
        ));
      }
    }

    // 更新状态
    state = state.copyWith(
      isAnalyzing: false,
      analysisResults: analysisResults,
    );
  }

  /// 初始化相机
  Future<void> initializeCamera() async {
    // 检查当前是否已经在使用相机
    if (state.isUsingCamera && state.cameraController != null) {
      return;
    }

    // 获取可用摄像头
    final cameras = await availableCameras();
    if (cameras.isEmpty) {
      // 没有可用摄像头
      return;
    }

    // 默认使用后置摄像头
    final camera = cameras.firstWhere(
      (camera) => camera.lensDirection == CameraLensDirection.back,
      orElse: () => cameras.first,
    );

    // 创建相机控制器
    final controller = CameraController(
      camera,
      ResolutionPreset.medium,
      enableAudio: false,
      imageFormatGroup: Platform.isAndroid
          ? ImageFormatGroup.yuv420
          : ImageFormatGroup.bgra8888,
    );

    // 初始化相机
    try {
      await controller.initialize();
      // 启用闪光灯辅助照明（如果可用）
      if (controller.value.isInitialized) {
        try {
          await controller.setFlashMode(FlashMode.torch);
        } catch (e) {
          print('无法启用闪光灯: $e');
        }
      }

      // 更新状态
      state = state.copyWith(
        cameraController: controller,
        isUsingCamera: true,
      );

      // 重置图像处理器
      _imageProcessor.reset();
    } catch (e) {
      // 相机初始化失败
      print('相机初始化失败: $e');
    }
  }

  /// 开始通过相机分析脉象
  Future<void> startCameraAnalysis() async {
    // 初始化相机（如果未初始化）
    if (state.cameraController == null ||
        !state.cameraController!.value.isInitialized) {
      await initializeCamera();
    }

    // 确保相机已初始化
    if (state.cameraController != null &&
        state.cameraController!.value.isInitialized) {
      // 设置分析状态
      state = state.copyWith(isAnalyzing: true, isUsingCamera: true);

      // 启动图像流处理
      await _startImageStreamProcessing();
    }
  }

  /// 启动图像流处理
  Future<void> _startImageStreamProcessing() async {
    // 确保相机控制器存在且已初始化
    final cameraController = state.cameraController;
    if (cameraController == null || !cameraController.value.isInitialized) {
      return;
    }

    // 重置图像处理器
    _imageProcessor.reset();

    // 创建进度更新计时器
    _processingTimer?.cancel();
    _processingTimer = Timer.periodic(
      const Duration(milliseconds: 100),
      (_) {
        if (state.isAnalyzing && state.signalData != null) {
          state = state.copyWith(
            signalDataIndex: (state.signalDataIndex ?? 0) + 1,
          );
        }
      },
    );

    try {
      // 监听图像流
      await cameraController.startImageStream((CameraImage image) async {
        try {
          if (!state.isAnalyzing || !state.isUsingCamera) return;

          // 处理图像帧
          final result = await _imageProcessor.processFrame(image);

          // 如果有新的分析结果
          if (result != null) {
            final pulseType = result['pulseType'] as PulseType?;
            final heartRate = result['heartRate'] as int?;
            final processedData = result['processedData'] as List<double>?;

            if (pulseType != null &&
                heartRate != null &&
                processedData != null) {
              // 创建脉搏数据
              final pulseData = PulseData(
                values: processedData,
                type: pulseType,
                frequency: heartRate,
                strength: result['strength'] as double? ?? 0.7,
                regularity: result['regularity'] as double? ?? 0.7,
              );

              // 创建分析结果
              final analysisResults = <PulseAnalysisResult>[
                PulseAnalysisResult(
                  type: pulseType,
                  probability: 0.85,
                ),
              ];

              // 随机添加1-2个次要类型
              final allTypes = PulseType.values.toList()..remove(pulseType);
              allTypes.shuffle();
              for (int i = 0; i < 2; i++) {
                if (i < allTypes.length) {
                  analysisResults.add(PulseAnalysisResult(
                    type: allTypes[i],
                    probability: 0.5 - i * 0.15,
                  ));
                }
              }

              // 更新状态
              state = state.copyWith(
                pulseData: pulseData,
                analysisResults: analysisResults,
                signalData: processedData,
                signalDataIndex: 0,
              );
            }
          }
        } catch (e) {
          print('处理图像帧出错: $e');
        }
      });
    } catch (e) {
      print('启动图像流处理出错: $e');

      // 停止分析
      state = state.copyWith(
        isAnalyzing: false,
      );
    }
  }

  /// 停止相机分析
  Future<void> stopCameraAnalysis() async {
    // 取消定时器
    _processingTimer?.cancel();
    _processingTimer = null;

    // 停止图像流
    final cameraController = state.cameraController;
    if (cameraController != null && cameraController.value.isInitialized) {
      try {
        // 先尝试关闭闪光灯
        if (cameraController.value.isStreamingImages) {
          await cameraController.stopImageStream();
        }

        try {
          await cameraController.setFlashMode(FlashMode.off);
        } catch (e) {
          print('关闭闪光灯出错: $e');
        }

        // 最后再释放相机资源
        await cameraController.dispose();
      } catch (e) {
        print('释放相机资源出错: $e');
      }
    }

    // 更新状态
    state = state.copyWith(
      cameraController: null,
      isUsingCamera: false,
      isAnalyzing: false,
    );
  }

  @override
  void dispose() {
    // 清理资源
    _animationTimer?.cancel();
    _processingTimer?.cancel();
    final cameraController = state.cameraController;
    if (cameraController != null) {
      if (cameraController.value.isStreamingImages) {
        try {
          cameraController.stopImageStream();
        } catch (_) {}
      }
      cameraController.dispose();
    }
    super.dispose();
  }
}

/// 脉诊组件
class PulseDiagnosisWidget extends ConsumerStatefulWidget {
  /// 默认脉象类型
  static const PulseType defaultPulseType = PulseType.floating;

  /// 初始脉象类型
  final PulseType? initialPulseType;

  /// 是否启用相机
  final bool enableCamera;

  /// 是否默认启用动画
  final bool enableAnimationByDefault;

  /// 是否展示脉象类型选择器
  final bool showPulseSelector;

  /// 是否展示分析结果
  final bool showAnalysisResult;

  /// 构造函数
  const PulseDiagnosisWidget({
    Key? key,
    this.initialPulseType,
    this.enableCamera = false, // Web平台不建议启用相机
    this.enableAnimationByDefault = true,
    this.showPulseSelector = true,
    this.showAnalysisResult = true,
  }) : super(key: key);

  @override
  ConsumerState<PulseDiagnosisWidget> createState() =>
      _PulseDiagnosisWidgetState();
}

class _PulseDiagnosisWidgetState extends ConsumerState<PulseDiagnosisWidget> {
  // 使用简化版脉象数据源
  late PulseType _selectedPulseType;

  // 相机相关变量
  CameraController? _cameraController;
  bool _isCameraInitialized = false;
  bool _isCameraMode = false;

  // 动画相关变量
  late bool _isAnimationEnabled;
  Timer? _animationTimer;
  int _animationFrame = 0;
  final int _totalAnimationFrames = 100;

  // 波形点
  final List<double> _wavePoints = [];
  final int _maxPoints = 100;

  @override
  void initState() {
    super.initState();
    _selectedPulseType = widget.initialPulseType ?? PulseType.floating;
    _isAnimationEnabled =
        widget.enableAnimationByDefault && !kIsWeb; // Web平台默认禁用动画

    // 初始化波形点
    _initializeWavePoints();

    // 如果启用动画且不是Web平台，启动动画
    if (_isAnimationEnabled) {
      _startAnimation();
    }

    // 如果启用相机且不是Web平台，初始化相机
    if (widget.enableCamera && !kIsWeb) {
      _initializeCamera();
    }
  }

  // 初始化波形点
  void _initializeWavePoints() {
    _wavePoints.clear();
    final pulseData = PulseData.fromSample(_selectedPulseType);

    // 仅使用较少点以降低渲染压力
    final int pointsToUse = kIsWeb ? 50 : _maxPoints;

    for (int i = 0; i < pointsToUse; i++) {
      if (i < pulseData.values.length) {
        _wavePoints.add(pulseData.values[i]);
      } else {
        _wavePoints.add(0.5); // 默认中点
      }
    }
  }

  // 启动动画
  void _startAnimation() {
    // 停止现有动画
    _stopAnimation();

    // 根据平台调整更新频率
    final int updatesPerSecond =
        kIsWeb ? _kWebUpdatesPerSecond : _kNativeUpdatesPerSecond;

    // 创建新动画计时器
    _animationTimer = Timer.periodic(
      Duration(milliseconds: 1000 ~/ updatesPerSecond),
      (timer) {
        if (mounted) {
          setState(() {
            _updateWavePoints();
            _animationFrame = (_animationFrame + 1) % _totalAnimationFrames;
          });
        }
      },
    );
  }

  // 停止动画
  void _stopAnimation() {
    _animationTimer?.cancel();
    _animationTimer = null;
  }

  // 更新波形点
  void _updateWavePoints() {
    if (_wavePoints.isEmpty) return;

    // 生成新的点
    final pulseData = PulseData.fromSample(_selectedPulseType);
    final double newPoint =
        pulseData.values[_animationFrame % pulseData.values.length];

    // 移除第一个点并添加新点
    _wavePoints.removeAt(0);
    _wavePoints.add(newPoint);
  }

  // 初始化相机
  Future<void> _initializeCamera() async {
    // Web平台不支持或跳过相机初始化
    if (kIsWeb) {
      debugPrint('Web平台不初始化相机功能');
      return;
    }

    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        debugPrint('没有可用的相机');
        return;
      }

      // 使用后置相机
      final camera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      // 初始化相机控制器
      _cameraController = CameraController(
        camera,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _cameraController!.initialize();

      if (mounted) {
        setState(() {
          _isCameraInitialized = true;
        });
      }
    } catch (e) {
      debugPrint('相机初始化失败: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(pulseDiagnosisStateProvider);
    final notifier = ref.read(pulseDiagnosisStateProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // 标题
        const Text(
          '脉诊分析',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),

        const SizedBox(height: 16),

        // 脉象波形图
        Container(
          height: 180,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withAlpha(15),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: state.isUsingCamera && state.cameraController != null
              ? _buildCameraView(state.cameraController!)
              : _buildPulseWaveChart(state.pulseData),
        ),

        const SizedBox(height: 16),

        // 控制按钮
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 脉象模拟按钮
            app_widgets.SecondaryButton(
              label: '脉象模拟',
              prefixIcon: Icons.waves,
              onPressed: () => _showPulseTypeSelector(context, notifier),
            ),

            const SizedBox(width: 16),

            // 相机分析按钮
            app_widgets.PrimaryButton(
              label: state.isUsingCamera ? '停止分析' : '相机分析',
              prefixIcon: state.isUsingCamera ? Icons.stop : Icons.camera_alt,
              isLoading: state.isAnalyzing,
              onPressed: state.isAnalyzing
                  ? null
                  : () => state.isUsingCamera
                      ? notifier.stopCameraAnalysis()
                      : notifier.startCameraAnalysis(),
            ),
          ],
        ),

        const SizedBox(height: 24),

        // 分析结果
        if (state.analysisResults != null && state.analysisResults!.isNotEmpty)
          _buildAnalysisResults(context, state.analysisResults!),
      ],
    );
  }

  /// 构建脉象波形图
  Widget _buildPulseWaveChart(PulseData? pulseData) {
    if (pulseData == null) {
      return const Center(
        child: Text(
          '点击下方按钮开始脉象模拟或相机分析',
          style: TextStyle(color: Colors.grey),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 脉象类型和参数
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                PulseData.getPulseTypeDescription(pulseData.type),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              Text(
                '${pulseData.frequency} 次/分钟',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 14,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // 波形图
          Expanded(
            child: Consumer(
              builder: (context, ref, _) {
                final state = ref.watch(pulseDiagnosisStateProvider);

                // 使用信号数据或脉搏数据的值
                final values = state.signalData ?? pulseData.values;

                return CustomPaint(
                  painter: PulseWaveformPainter(
                    values: values,
                    waveColor: TCMChartThemes.pulseChartTheme.waveColor,
                    gridColor: TCMChartThemes.pulseChartTheme.gridColor,
                    animated: true,
                    animationIndex: state.signalDataIndex,
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  /// 构建相机预览
  Widget _buildCameraView(CameraController controller) {
    if (!controller.value.isInitialized) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: Stack(
        children: [
          // 相机预览
          CameraPreview(controller),

          // 半透明指示层
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withAlpha(50),
                    Colors.transparent,
                    Colors.transparent,
                    Colors.black.withAlpha(50),
                  ],
                ),
              ),
              child: Center(
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: AppColors.primaryColor,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(60),
                  ),
                  child: Center(
                    child: Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: Colors.white.withAlpha(150),
                          width: 1,
                        ),
                        borderRadius: BorderRadius.circular(50),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),

          // 提示文本
          const Positioned(
            bottom: 16,
            left: 0,
            right: 0,
            child: Text(
              '将手指放在镜头上，保持稳定',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
                shadows: [
                  Shadow(
                    color: Colors.black,
                    blurRadius: 4,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建分析结果
  Widget _buildAnalysisResults(
      BuildContext context, List<PulseAnalysisResult> results) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '分析结果',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),

        const SizedBox(height: 12),

        // 主要结果
        if (results.isNotEmpty)
          app_widgets.BasicCard(
            title: PulseData.getPulseTypeDescription(results.first.type),
            subtitle: '匹配度 ${(results.first.probability * 100).toInt()}%',
            leadingIcon: Icons.favorite,
            content: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    PulseData.getPulseClinicalMeaning(results.first.type),
                    style: const TextStyle(height: 1.5),
                  ),

                  const SizedBox(height: 16),

                  // 进度条
                  app_widgets.AppProgress(
                    value: results.first.probability,
                    showLabel: true,
                    color: AppColors.primaryColor,
                  ),
                ],
              ),
            ),
          ),

        const SizedBox(height: 16),

        // 次要结果
        if (results.length > 1)
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '其他可能脉象',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 8),

              // 次要脉象列表
              ...results
                  .skip(1)
                  .map((result) => Padding(
                        padding: const EdgeInsets.only(bottom: 8.0),
                        child: Row(
                          children: [
                            Expanded(
                              flex: 2,
                              child: Text(PulseData.getPulseTypeDescription(
                                  result.type)),
                            ),
                            Expanded(
                              flex: 3,
                              child: app_widgets.AppProgress(
                                value: result.probability,
                                showLabel: true,
                                lineHeight: 12,
                                color: AppColors.secondaryColor,
                              ),
                            ),
                          ],
                        ),
                      ))
                  .toList(),
            ],
          ),
      ],
    );
  }

  /// 显示脉象类型选择器
  void _showPulseTypeSelector(
      BuildContext context, PulseDiagnosisNotifier notifier) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '选择脉象类型',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                height: 300,
                width: double.maxFinite,
                child: GridView.count(
                  crossAxisCount: 3,
                  mainAxisSpacing: 10,
                  crossAxisSpacing: 10,
                  childAspectRatio: 2.5,
                  children: PulseType.values
                      .map((type) => InkWell(
                            onTap: () {
                              notifier.startPulseSimulation(type);
                              Navigator.of(context).pop();
                            },
                            borderRadius: BorderRadius.circular(8),
                            child: Container(
                              decoration: BoxDecoration(
                                border:
                                    Border.all(color: AppColors.primaryColor),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              alignment: Alignment.center,
                              child: Text(
                                PulseData.getPulseTypeDescription(type),
                                style: const TextStyle(
                                  color: AppColors.primaryColor,
                                ),
                              ),
                            ),
                          ))
                      .toList(),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  app_widgets.AppTextButton(
                    label: '取消',
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 脉波形绘制器
class PulseWaveformPainter extends CustomPainter {
  final List<double> values;
  final Color waveColor;
  final Color gridColor;
  final bool animated;
  final int? animationIndex;

  /// 动画偏移量
  static double _animationOffset = 0.0;
  static const double _animationSpeed = 0.05;

  /// 构造函数
  PulseWaveformPainter({
    required this.values,
    required this.waveColor,
    required this.gridColor,
    this.animated = true,
    this.animationIndex,
  }) {
    if (animated && animationIndex == null) {
      _animationOffset += _animationSpeed;
      if (_animationOffset >= 1.0) {
        _animationOffset = 0.0;
      }
    }
  }

  @override
  void paint(Canvas canvas, Size size) {
    // 绘制网格
    _drawGrid(canvas, size);

    // 绘制波形
    _drawWaveform(canvas, size);
  }

  /// 绘制网格
  void _drawGrid(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = gridColor
      ..strokeWidth = 0.5;

    // 横线
    final horizontalCount = 5;
    final horizontalStep = size.height / horizontalCount;
    for (int i = 0; i <= horizontalCount; i++) {
      final y = i * horizontalStep;
      canvas.drawLine(
        Offset(0, y),
        Offset(size.width, y),
        paint,
      );
    }

    // 竖线
    final verticalCount = 10;
    final verticalStep = size.width / verticalCount;
    for (int i = 0; i <= verticalCount; i++) {
      final x = i * verticalStep;
      canvas.drawLine(
        Offset(x, 0),
        Offset(x, size.height),
        paint,
      );
    }
  }

  /// 绘制波形
  void _drawWaveform(Canvas canvas, Size size) {
    if (values.isEmpty) return;

    final paint = Paint()
      ..color = waveColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;

    final path = Path();
    final pointCount = values.length;

    // 计算每个点的x坐标步长
    final step = size.width / (pointCount - 1);

    // 如果启用动画，计算起始偏移
    int startIndex = 0;
    if (animated) {
      if (animationIndex != null) {
        // 使用外部提供的动画索引
        startIndex = animationIndex! % pointCount;
      } else {
        // 使用内部动画偏移
        startIndex = (pointCount * _animationOffset).toInt();
      }
    }

    // 绘制波形路径
    for (int i = 0; i < pointCount; i++) {
      // 计算实际索引（考虑动画偏移）
      final actualIndex = (startIndex + i) % pointCount;

      // 获取y值（将0-1范围映射到控件高度）
      final value = values[actualIndex];
      final y = size.height - value * size.height;

      // 添加到路径
      if (i == 0) {
        path.moveTo(0, y);
      } else {
        path.lineTo(i * step, y);
      }
    }

    // 绘制路径
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant PulseWaveformPainter oldDelegate) {
    return oldDelegate.values != values ||
        oldDelegate.waveColor != waveColor ||
        oldDelegate.gridColor != gridColor ||
        oldDelegate.animationIndex != animationIndex ||
        animated; // 如果启用动画，总是重绘
  }
}
