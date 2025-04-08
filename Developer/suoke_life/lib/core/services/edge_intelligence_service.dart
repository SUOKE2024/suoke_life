import 'dart:io';
import 'dart:math';
import 'dart:typed_data';
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/models/context_data.dart';
import 'package:suoke_life/core/models/health_insight.dart';
import 'package:suoke_life/core/models/sensor_data.dart';
import 'package:suoke_life/core/services/multimodal_data_service.dart';
import 'package:suoke_life/core/utils/logger.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 边缘智能服务提供者
final edgeIntelligenceServiceProvider =
    Provider<EdgeIntelligenceService>((ref) {
  final multimodalDataService = ref.watch(multimodalDataServiceProvider);
  return EdgeIntelligenceService(multimodalDataService: multimodalDataService);
});

/// 分析结果
class AnalyticsResult {
  /// 分析是否成功
  final bool success;

  /// 错误信息（如果有）
  final String? error;

  /// 分析洞察
  final HealthInsight? insights;

  /// 其他结果数据
  final Map<String, dynamic>? data;

  /// 时间戳
  final DateTime timestamp;

  /// 构造函数
  AnalyticsResult({
    required this.success,
    this.error,
    this.insights,
    this.data,
    required this.timestamp,
  });

  /// 创建成功结果
  factory AnalyticsResult.success({
    required HealthInsight insights,
    Map<String, dynamic>? data,
    required DateTime timestamp,
  }) {
    return AnalyticsResult(
      success: true,
      insights: insights,
      data: data,
      timestamp: timestamp,
    );
  }

  /// 创建失败结果
  factory AnalyticsResult.failure({
    required String error,
    required DateTime timestamp,
  }) {
    return AnalyticsResult(
      success: false,
      error: error,
      timestamp: timestamp,
    );
  }
}

/// 本地分析模型
class LocalAnalyticsModel {
  static const String _tag = 'LocalAnalyticsModel';

  /// 分析健康数据
  Future<AnalyticsResult> analyze(
      String userId, Map<String, dynamic> healthData) async {
    try {
      Logger.d(_tag, '分析健康数据: $userId');

      // 简单分析逻辑，实际项目中这里应该实现更复杂的分析
      final now = DateTime.now();
      final random = Random();

      // 提取和分析数据
      final stressLevel = _analyzeStressLevel(healthData);
      final sleepQuality = _analyzeSleepQuality(healthData);
      final activityScore = _analyzeActivity(healthData);

      // 创建健康洞察
      final insight = HealthInsight(
        userId: userId,
        timestamp: now,
        stressLevel: stressLevel,
        sleepQuality: sleepQuality,
        activityLevel: activityScore,
        heartRateVariability: random.nextDouble() * 30 + 40,
        bodyBalance: random.nextDouble() * 50 + 50,
        recoveryIndex: random.nextDouble() * 40 + 60,
        comments:
            _generateInsightComments(stressLevel, sleepQuality, activityScore),
        recommendations:
            _generateRecommendations(stressLevel, sleepQuality, activityScore),
      );

      return AnalyticsResult.success(
        insights: insight,
        timestamp: now,
      );
    } catch (e) {
      Logger.e(_tag, '分析健康数据失败: $e');
      return AnalyticsResult.failure(
        error: e.toString(),
        timestamp: DateTime.now(),
      );
    }
  }

  /// 分析压力水平
  double _analyzeStressLevel(Map<String, dynamic> healthData) {
    // 实际项目中应该实现更复杂的分析算法
    if (healthData.containsKey('heartRate')) {
      final heartRate = healthData['heartRate'] as num;
      // 简单的压力评估，基于心率
      if (heartRate > 90) {
        return 0.8; // 高压力
      } else if (heartRate > 75) {
        return 0.5; // 中等压力
      } else {
        return 0.3; // 低压力
      }
    }

    // 随机值
    return Random().nextDouble() * 0.6 + 0.2;
  }

  /// 分析睡眠质量
  double _analyzeSleepQuality(Map<String, dynamic> healthData) {
    // 实际项目中应该实现更复杂的分析算法
    if (healthData.containsKey('sleepDuration')) {
      final sleepDuration = healthData['sleepDuration'] as num;
      // 基于睡眠时长的简单评估
      if (sleepDuration >= 7.5) {
        return 0.9; // 优质睡眠
      } else if (sleepDuration >= 6.0) {
        return 0.7; // 良好睡眠
      } else if (sleepDuration >= 5.0) {
        return 0.5; // 一般睡眠
      } else {
        return 0.3; // 较差睡眠
      }
    }

    // 随机值
    return Random().nextDouble() * 0.5 + 0.3;
  }

  /// 分析活动水平
  double _analyzeActivity(Map<String, dynamic> healthData) {
    // 实际项目中应该实现更复杂的分析算法
    if (healthData.containsKey('steps')) {
      final steps = healthData['steps'] as num;
      // 基于步数的简单评估
      if (steps > 10000) {
        return 0.9; // 很活跃
      } else if (steps > 7500) {
        return 0.8; // 活跃
      } else if (steps > 5000) {
        return 0.6; // 适度活跃
      } else if (steps > 2500) {
        return 0.4; // 轻度活跃
      } else {
        return 0.2; // 不活跃
      }
    }

    // 随机值
    return Random().nextDouble() * 0.7 + 0.1;
  }

  /// 生成洞察评论
  String _generateInsightComments(
      double stressLevel, double sleepQuality, double activityScore) {
    final comments = [];

    if (stressLevel > 0.7) {
      comments.add('您的压力水平较高，可能需要适当放松。');
    } else if (stressLevel < 0.4) {
      comments.add('您的压力水平处于健康范围内。');
    }

    if (sleepQuality > 0.7) {
      comments.add('您的睡眠质量良好，继续保持。');
    } else if (sleepQuality < 0.5) {
      comments.add('您的睡眠质量有待提高，考虑调整睡眠习惯。');
    }

    if (activityScore > 0.7) {
      comments.add('您的活动水平很好，身体活力充沛。');
    } else if (activityScore < 0.4) {
      comments.add('您的活动水平较低，可以适当增加日常活动。');
    }

    if (comments.isEmpty) {
      return '您的健康状况总体良好，继续保持健康的生活方式。';
    }

    return comments.join(' ');
  }

  /// 生成健康建议
  List<String> _generateRecommendations(
      double stressLevel, double sleepQuality, double activityScore) {
    final recommendations = <String>[];

    if (stressLevel > 0.7) {
      recommendations.add('尝试每天进行15分钟的冥想或深呼吸练习');
      recommendations.add('减少咖啡因摄入，尤其是下午和晚上');
    }

    if (sleepQuality < 0.6) {
      recommendations.add('保持规律的睡眠时间，包括周末');
      recommendations.add('睡前一小时避免使用电子设备');
      recommendations.add('使用索克生活APP的"冥想助眠"功能帮助入睡');
    }

    if (activityScore < 0.5) {
      recommendations.add('每天尝试走至少6000步');
      recommendations.add('每周进行150分钟中等强度的有氧运动');
      recommendations.add('工作时每小时起身活动5分钟');
    }

    if (recommendations.isEmpty) {
      recommendations.add('继续保持当前的健康生活方式');
      recommendations.add('定期使用索克生活APP进行健康监测');
    }

    return recommendations;
  }

  /// 创建本地分析模型
  static Future<LocalAnalyticsModel> create() async {
    return LocalAnalyticsModel();
  }
}

/// 边缘智能服务
///
/// 为设备端提供轻量级AI能力，包括文本嵌入、分类等功能
class EdgeIntelligenceService {
  /// 是否已初始化
  bool _initialized = false;

  /// 待处理的任务队列
  final List<_Task> _taskQueue = [];

  /// 处理任务的计时器
  Timer? _processingTimer;

  /// 多模态数据服务
  final MultimodalDataService multimodalDataService;

  // TensorFlow Lite 解释器
  Interpreter? _interpreter;

  // 本地分析模型
  late LocalAnalyticsModel _analyticsModel;

  /// 构造函数
  EdgeIntelligenceService({required this.multimodalDataService});

  /// 初始化
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // 启动任务处理循环
      _startProcessingLoop();

      // 加载TFLite模型
      await _loadTFLiteModel();

      // 初始化本地分析模型
      _analyticsModel = await LocalAnalyticsModel.create();

      _initialized = true;
      debugPrint('边缘智能服务初始化成功');
    } catch (e) {
      debugPrint('边缘智能服务初始化失败: $e');
      rethrow;
    }
  }

  /// 开始处理任务循环
  void _startProcessingLoop() {
    _processingTimer?.cancel();
    _processingTimer = Timer.periodic(
      const Duration(milliseconds: 100),
      (_) => _processBatchTasks(),
    );
  }

  /// 批量处理任务
  Future<void> _processBatchTasks() async {
    if (_taskQueue.isEmpty) return;

    // 取出最多5个任务同时处理
    final tasks = _taskQueue.take(5).toList();
    _taskQueue.removeRange(0, min(_taskQueue.length, 5));

    // 按类型分组任务
    final embedTasks = tasks.where((t) => t.type == _TaskType.embed).toList();
    final classifyTasks =
        tasks.where((t) => t.type == _TaskType.classify).toList();

    // 并行处理不同类型的任务
    await Future.wait([
      if (embedTasks.isNotEmpty) _processBatchEmbeddings(embedTasks),
      if (classifyTasks.isNotEmpty) _processBatchClassifications(classifyTasks),
    ]);
  }

  /// 批量处理嵌入任务
  Future<void> _processBatchEmbeddings(List<_Task> tasks) async {
    try {
      // 收集所有输入文本
      final texts = tasks.map((t) => t.input as String).toList();

      // 批量生成嵌入向量（简化实现，实际应调用TFLite模型）
      final embeddings = await compute(_mockGenerateEmbeddings, texts);

      // 返回结果
      for (int i = 0; i < tasks.length; i++) {
        tasks[i].completer.complete(embeddings[i]);
      }
    } catch (e) {
      // 处理错误
      for (final task in tasks) {
        task.completer.completeError(e);
      }
    }
  }

  /// 批量处理分类任务
  Future<void> _processBatchClassifications(List<_Task> tasks) async {
    try {
      // 收集所有输入文本
      final texts = tasks.map((t) => t.input as String).toList();

      // 批量生成分类结果（简化实现，实际应调用TFLite模型）
      final classifications =
          await compute(_mockGenerateClassifications, texts);

      // 返回结果
      for (int i = 0; i < tasks.length; i++) {
        tasks[i].completer.complete(classifications[i]);
      }
    } catch (e) {
      // 处理错误
      for (final task in tasks) {
        task.completer.completeError(e);
      }
    }
  }

  /// 加载TensorFlow Lite模型
  Future<void> _loadTFLiteModel() async {
    try {
      Logger.d(_tag, '加载TensorFlow Lite模型');

      final modelFile = await _getModel();

      if (modelFile != null) {
        _interpreter = await Interpreter.fromFile(modelFile);
        Logger.i(_tag, 'TensorFlow Lite模型加载成功');
      } else {
        Logger.w(_tag, '模型文件不存在，跳过TensorFlow Lite初始化');
      }
    } catch (e) {
      Logger.e(_tag, '加载TensorFlow Lite模型失败: $e');
    }
  }

  /// 获取模型文件
  Future<File?> _getModel() async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final modelPath =
          path.join(appDir.path, 'models', 'health_analytics.tflite');
      final modelFile = File(modelPath);

      if (await modelFile.exists()) {
        return modelFile;
      }

      // 如果模型不存在，尝试从assets复制
      try {
        final byteData =
            await rootBundle.load('assets/models/health_analytics.tflite');
        final buffer = byteData.buffer;

        // 确保目录存在
        await Directory(path.dirname(modelPath)).create(recursive: true);

        // 写入文件
        await modelFile.writeAsBytes(
            buffer.asUint8List(byteData.offsetInBytes, byteData.lengthInBytes));

        return modelFile;
      } catch (e) {
        Logger.w(_tag, 'Asset中没有找到模型文件: $e');
        return null;
      }
    } catch (e) {
      Logger.e(_tag, '获取模型文件失败: $e');
      return null;
    }
  }

  /// 生成文本嵌入向量
  Future<List<double>> generateEmbedding(String text) async {
    if (!_initialized) {
      await initialize();
    }

    final completer = Completer<List<double>>();
    _taskQueue.add(_Task(
      type: _TaskType.embed,
      input: text,
      completer: completer,
    ));

    return completer.future;
  }

  /// 对文本进行分类
  Future<Map<String, double>> classifyText(
    String text, {
    required List<String> labels,
  }) async {
    if (!_initialized) {
      await initialize();
    }

    final completer = Completer<Map<String, double>>();
    _taskQueue.add(_Task(
      type: _TaskType.classify,
      input: text,
      completer: completer,
      metadata: {'labels': labels},
    ));

    return completer.future;
  }

  /// 释放资源
  void dispose() {
    _interpreter?.close();
    _processingTimer?.cancel();
    _processingTimer = null;
    _taskQueue.clear();
    _initialized = false;
  }
}

/// 任务类型
enum _TaskType {
  embed,
  classify,
}

/// 任务数据结构
class _Task {
  final _TaskType type;
  final dynamic input;
  final Completer completer;
  final Map<String, dynamic>? metadata;

  _Task({
    required this.type,
    required this.input,
    required this.completer,
    this.metadata,
  });
}

/// 模拟生成嵌入向量（实际应使用TFLite模型）
List<List<double>> _mockGenerateEmbeddings(List<String> texts) {
  final random = Random(texts.join().hashCode);

  // 对于每个文本，生成一个模拟的嵌入向量
  return texts.map((text) {
    // 向量维度为64
    final vector = List<double>.generate(64, (i) {
      // 确保相同的文本总是生成相同的向量
      final seedValue = text.hashCode ^ i;
      final r = Random(seedValue);
      return r.nextDouble() * 2 - 1; // 范围 [-1, 1]
    });

    // 归一化向量
    final magnitude = sqrt(vector.fold(0.0, (sum, v) => sum + v * v));
    return vector.map((v) => v / magnitude).toList();
  }).toList();
}

/// 模拟文本分类（实际应使用TFLite模型）
List<Map<String, double>> _mockGenerateClassifications(List<String> texts) {
  return texts.map((text) {
    final keywords = {
      '阴虚': ['燥热', '口干', '咽干', '手足心热', '失眠', '头晕'],
      '阳虚': ['怕冷', '四肢发凉', '疲倦', '精神不振', '尿频'],
      '气虚': ['疲劳', '气短', '懒言', '自汗', '易感冒'],
      '血虚': ['面色苍白', '头晕', '心悸', '失眠', '健忘'],
      '痰湿': ['肥胖', '胸闷', '痰多', '恶心', '乏力'],
      '湿热': ['口苦', '口臭', '尿黄', '大便干', '痤疮'],
      '淤血': ['刺痛', '青紫', '肿块', '经期疼痛', '经血有块'],
      '气郁': ['抑郁', '胸闷', '情绪波动', '叹息', '易怒']
    };

    // 计算文本与每个类别的匹配度
    final result = <String, double>{};
    for (final entry in keywords.entries) {
      final category = entry.key;
      final terms = entry.value;

      // 计算文本中包含的关键词数量
      int matchCount = 0;
      for (final term in terms) {
        if (text.contains(term)) {
          matchCount++;
        }
      }

      // 计算匹配度分数
      final matchRatio = terms.isEmpty ? 0.0 : matchCount / terms.length;
      result[category] = matchRatio.clamp(0.0, 1.0);
    }

    // 确保分数总和为1.0
    final sum = result.values.fold(0.0, (sum, score) => sum + score);
    if (sum > 0) {
      for (final key in result.keys) {
        result[key] = result[key]! / sum;
      }
    }

    return result;
  }).toList();
}
