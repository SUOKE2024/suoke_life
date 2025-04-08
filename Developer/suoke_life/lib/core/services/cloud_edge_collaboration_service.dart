import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/core/models/health_insight.dart';
import 'package:suoke_life/core/models/sensor_data.dart';
import 'package:suoke_life/core/services/context_aware_sensing_service.dart';
import 'package:suoke_life/core/services/deepseek_service.dart';
import 'package:suoke_life/core/services/edge_intelligence_service.dart';
import 'package:suoke_life/core/services/multimodal_data_service.dart';
import 'package:suoke_life/core/services/network_service.dart';
import 'package:suoke_life/core/utils/logger.dart';
import 'package:suoke_life/di/providers.dart';

part 'cloud_edge_collaboration_service.g.dart';

/// 云边协同服务提供者
@riverpod
CloudEdgeCollaborationService cloudEdgeCollaborationService(
    CloudEdgeCollaborationServiceRef ref) {
  final edgeService = ref.watch(edgeIntelligenceServiceProvider);
  final multimodalService = ref.watch(multimodalDataServiceProvider);
  final deepSeekService = ref.watch(deepSeekServiceProvider);
  final networkService = ref.watch(networkServiceProvider);

  return CloudEdgeCollaborationService(
    edgeService: edgeService,
    multimodalService: multimodalService,
    cloudService: deepSeekService,
    networkService: networkService,
  );
}

/// 处理策略
enum ProcessingStrategy {
  edgeOnly, // 仅设备端处理
  cloudOnly, // 仅云端处理
  hybrid, // 混合处理
  adaptive, // 自适应处理
}

/// 处理位置
enum ProcessingLocation {
  edge, // 设备端处理
  cloud, // 云端处理
  hybrid, // 混合处理
  unknown, // 未知
}

/// 处理任务
class ProcessingTask {
  /// 会话ID
  final String sessionId;

  /// 数据项
  final List<Map<String, dynamic>> dataItems;

  /// 处理策略
  final ProcessingStrategy strategy;

  /// 时间戳
  final DateTime timestamp;

  /// 重试次数
  int retryCount;

  /// 构造函数
  ProcessingTask({
    required this.sessionId,
    required this.dataItems,
    required this.strategy,
    required this.timestamp,
    this.retryCount = 0,
  });
}

/// 处理结果
class ProcessingResult {
  /// 是否成功
  final bool success;

  /// 错误信息
  final String? error;

  /// 健康洞察
  final HealthInsight insights;

  /// 处理位置
  final ProcessingLocation processingLocation;

  /// 时间戳
  final DateTime timestamp;

  /// 其他数据
  final Map<String, dynamic>? additionalData;

  /// 构造函数
  ProcessingResult({
    required this.success,
    this.error,
    required this.insights,
    required this.processingLocation,
    required this.timestamp,
    this.additionalData,
  });

  /// 创建成功结果
  factory ProcessingResult.success({
    required HealthInsight insights,
    required ProcessingLocation processingLocation,
    required DateTime timestamp,
    Map<String, dynamic>? additionalData,
  }) {
    return ProcessingResult(
      success: true,
      insights: insights,
      processingLocation: processingLocation,
      timestamp: timestamp,
      additionalData: additionalData,
    );
  }

  /// 创建失败结果
  factory ProcessingResult.failure({
    required String error,
    required DateTime timestamp,
  }) {
    return ProcessingResult(
      success: false,
      error: error,
      insights: HealthInsight.empty(),
      processingLocation: ProcessingLocation.unknown,
      timestamp: timestamp,
    );
  }

  /// 从云端响应创建
  factory ProcessingResult.fromCloud(Map<String, dynamic> response) {
    if (response.containsKey('error')) {
      return ProcessingResult.failure(
        error: response['error'],
        timestamp: DateTime.now(),
      );
    }

    return ProcessingResult.success(
      insights: HealthInsight.fromJson(response['insights']),
      processingLocation: ProcessingLocation.cloud,
      timestamp: DateTime.now(),
      additionalData: response['additionalData'],
    );
  }
}

/// 云边协同服务
class CloudEdgeCollaborationService {
  static const String _tag = 'CloudEdgeCollaborationService';

  /// 边缘智能服务
  final EdgeIntelligenceService _edgeService;

  /// 多模态数据服务
  final MultimodalDataService _multimodalService;

  /// 云服务
  final DeepSeekService _cloudService;

  /// 网络服务
  final NetworkService _networkService;

  /// 连接监测
  final Connectivity _connectivity = Connectivity();

  /// 连接状态
  ConnectivityResult _connectionStatus = ConnectivityResult.none;

  /// 处理队列
  final List<ProcessingTask> _processingQueue = [];

  /// 队列处理定时器
  Timer? _queueProcessingTimer;

  /// 队列处理锁
  bool _isProcessingQueue = false;

  /// 构造函数
  CloudEdgeCollaborationService({
    required EdgeIntelligenceService edgeService,
    required MultimodalDataService multimodalService,
    required DeepSeekService cloudService,
    required NetworkService networkService,
  })  : _edgeService = edgeService,
        _multimodalService = multimodalService,
        _cloudService = cloudService,
        _networkService = networkService {
    // 监听连接状态变化
    _connectivity.onConnectivityChanged.listen(_updateConnectionStatus);

    // 初始化连接状态
    _initConnectivity();

    // 启动队列处理
    _startQueueProcessing();
  }

  /// 初始化连接状态
  Future<void> _initConnectivity() async {
    try {
      _connectionStatus = await _connectivity.checkConnectivity();
      Logger.d(_tag, '初始连接状态: $_connectionStatus');
    } catch (e) {
      Logger.e(_tag, '检查连接状态失败: $e');
    }
  }

  /// 更新连接状态
  void _updateConnectionStatus(ConnectivityResult result) {
    _connectionStatus = result;
    Logger.d(_tag, '连接状态变化: $_connectionStatus');

    // 如果连接恢复，处理待处理队列
    if (_connectionStatus != ConnectivityResult.none) {
      _processQueue();
    }
  }

  /// 启动队列处理
  void _startQueueProcessing() {
    // 定期检查队列是否有待处理任务
    _queueProcessingTimer = Timer.periodic(const Duration(minutes: 5), (timer) {
      _processQueue();
    });
  }

  /// 处理多模态数据
  Future<ProcessingResult> processMultimodalData({
    required String sessionId,
    required List<Map<String, dynamic>> dataItems,
    required ProcessingStrategy strategy,
  }) async {
    Logger.d(_tag, '处理多模态数据，会话ID: $sessionId，策略: $strategy');

    try {
      // 如果是自适应策略，根据当前状态决定使用哪种策略
      if (strategy == ProcessingStrategy.adaptive) {
        strategy = _determineOptimalStrategy(dataItems);
        Logger.d(_tag, '自适应策略选择: $strategy');
      }

      // 根据策略决定处理方式
      switch (strategy) {
        case ProcessingStrategy.edgeOnly:
          return await _processOnEdge(sessionId, dataItems);

        case ProcessingStrategy.cloudOnly:
          return await _processOnCloud(sessionId, dataItems);

        case ProcessingStrategy.hybrid:
        default:
          return await _processHybrid(sessionId, dataItems);
      }
    } catch (e) {
      Logger.e(_tag, '数据处理失败: $e');

      // 如果处理失败，将任务加入队列
      _enqueueTask(ProcessingTask(
        sessionId: sessionId,
        dataItems: dataItems,
        strategy: strategy,
        timestamp: DateTime.now(),
      ));

      return ProcessingResult.failure(
        error: e.toString(),
        timestamp: DateTime.now(),
      );
    }
  }

  /// 确定最佳处理策略
  ProcessingStrategy _determineOptimalStrategy(
      List<Map<String, dynamic>> dataItems) {
    // 检查数据类型
    final containsComplexData = dataItems.any((item) {
      final type = item['type'];
      return type == MultimodalDataType.image.name ||
          type == MultimodalDataType.audio.name ||
          type == MultimodalDataType.video.name;
    });

    // 检查连接状态
    final hasConnection = _connectionStatus != ConnectivityResult.none;

    // 检查电池状态 (简化版，实际应该使用电池API)
    final isBatteryLow = false; // 占位，实际项目中应该检查真实电池状态

    // 决策逻辑
    if (containsComplexData && hasConnection && !isBatteryLow) {
      // 复杂数据且有网络连接，使用云端处理
      return ProcessingStrategy.cloudOnly;
    } else if (containsComplexData && !hasConnection) {
      // 复杂数据但无网络连接，只能本地处理
      return ProcessingStrategy.edgeOnly;
    } else if (!containsComplexData && isBatteryLow) {
      // 简单数据但电池低，使用云端处理省电
      return hasConnection
          ? ProcessingStrategy.cloudOnly
          : ProcessingStrategy.edgeOnly;
    } else {
      // 其他情况使用混合处理
      return ProcessingStrategy.hybrid;
    }
  }

  /// 边缘设备处理
  Future<ProcessingResult> _processOnEdge(
      String sessionId, List<Map<String, dynamic>> dataItems) async {
    Logger.d(_tag, '在设备上处理数据，会话ID: $sessionId');

    try {
      // 转换为传感器数据
      final sensorData = dataItems
          .where((item) =>
              item['type'] == SensorType.accelerometer.name ||
              item['type'] == SensorType.gyroscope.name ||
              item['type'] == SensorType.magnetometer.name)
          .map((item) => SensorReading.fromJson(item))
          .toList();

      if (sensorData.isEmpty) {
        Logger.w(_tag, '没有可处理的传感器数据');
        return ProcessingResult.failure(
          error: '没有可处理的传感器数据',
          timestamp: DateTime.now(),
        );
      }

      // 本地处理
      final insight = await _edgeService.processHealthDataLocally(sensorData);

      // 保存处理结果
      await _saveProcessingResult(sessionId, insight);

      return ProcessingResult.success(
        insights: insight,
        processingLocation: ProcessingLocation.edge,
        timestamp: DateTime.now(),
      );
    } catch (e) {
      Logger.e(_tag, '设备端处理失败: $e');
      return ProcessingResult.failure(
        error: '设备端处理失败: $e',
        timestamp: DateTime.now(),
      );
    }
  }

  /// 云端处理
  Future<ProcessingResult> _processOnCloud(
      String sessionId, List<Map<String, dynamic>> dataItems) async {
    Logger.d(_tag, '在云端处理数据，会话ID: $sessionId');

    if (_connectionStatus == ConnectivityResult.none) {
      // 无网络连接，加入队列
      Logger.w(_tag, '无网络连接，任务加入队列');

      _enqueueTask(ProcessingTask(
        sessionId: sessionId,
        dataItems: dataItems,
        strategy: ProcessingStrategy.cloudOnly,
        timestamp: DateTime.now(),
      ));

      return ProcessingResult.failure(
        error: '无网络连接',
        timestamp: DateTime.now(),
      );
    }

    try {
      // 准备云处理请求
      final request = _prepareCloudRequest(sessionId, dataItems);

      // 发送到云端处理
      final response = await _cloudService.processMultimodalData(request);

      // 解析响应
      final result = ProcessingResult.fromCloud(response);

      if (result.success) {
        // 保存处理结果
        await _saveProcessingResult(sessionId, result.insights);
      }

      return result;
    } catch (e) {
      Logger.e(_tag, '云端处理失败: $e');

      // 失败时加入队列稍后重试
      _enqueueTask(ProcessingTask(
        sessionId: sessionId,
        dataItems: dataItems,
        strategy: ProcessingStrategy.cloudOnly,
        timestamp: DateTime.now(),
      ));

      return ProcessingResult.failure(
        error: '云端处理失败: $e',
        timestamp: DateTime.now(),
      );
    }
  }

  /// 混合处理策略
  Future<ProcessingResult> _processHybrid(
      String sessionId, List<Map<String, dynamic>> dataItems) async {
    Logger.d(_tag, '使用混合策略处理数据，会话ID: $sessionId');

    try {
      // 将数据分为本地处理和云端处理
      final localData = _filterLocalProcessableData(dataItems);
      final cloudData = _filterCloudProcessableData(dataItems);

      // 本地处理
      final localResult = await _processOnEdge(sessionId, localData);

      // 有网络时才进行云处理
      if (_connectionStatus != ConnectivityResult.none &&
          cloudData.isNotEmpty) {
        final cloudResult = await _processOnCloud(sessionId, cloudData);

        // 合并结果
        return _mergeResults(localResult, cloudResult);
      }

      return localResult;
    } catch (e) {
      Logger.e(_tag, '混合处理失败: $e');
      return ProcessingResult.failure(
        error: '混合处理失败: $e',
        timestamp: DateTime.now(),
      );
    }
  }

  /// 将任务加入队列
  void _enqueueTask(ProcessingTask task) {
    Logger.d(_tag, '任务加入队列: ${task.sessionId}');

    // 检查任务是否已经在队列中
    final existingTaskIndex =
        _processingQueue.indexWhere((t) => t.sessionId == task.sessionId);

    if (existingTaskIndex >= 0) {
      // 更新现有任务
      _processingQueue[existingTaskIndex] = task;
    } else {
      // 添加新任务
      _processingQueue.add(task);
    }

    // 保存队列状态
    _persistQueue();

    // 如果有网络连接，尝试处理队列
    if (_connectionStatus != ConnectivityResult.none) {
      _processQueue();
    }
  }

  /// 持久化队列
  Future<void> _persistQueue() async {
    try {
      // 将队列转换为JSON
      final queueJson = _processingQueue
          .map((task) => {
                'sessionId': task.sessionId,
                'strategy': task.strategy.toString(),
                'timestamp': task.timestamp.toIso8601String(),
                'retryCount': task.retryCount,
                // 数据项太大，不保存在持久化中，而是单独保存
              })
          .toList();

      // 保存队列元数据
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('processing_queue', jsonEncode(queueJson));

      // 为每个任务保存数据项
      for (final task in _processingQueue) {
        await _saveTaskData(task.sessionId, task.dataItems);
      }
    } catch (e) {
      Logger.e(_tag, '持久化队列失败: $e');
    }
  }

  /// 保存任务数据
  Future<void> _saveTaskData(
      String sessionId, List<Map<String, dynamic>> dataItems) async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final taskDir = Directory('${appDir.path}/tasks');

      if (!await taskDir.exists()) {
        await taskDir.create(recursive: true);
      }

      final file = File('${taskDir.path}/$sessionId.json');
      await file.writeAsString(jsonEncode(dataItems));
    } catch (e) {
      Logger.e(_tag, '保存任务数据失败: $e');
    }
  }

  /// 加载任务数据
  Future<List<Map<String, dynamic>>?> _loadTaskData(String sessionId) async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final file = File('${appDir.path}/tasks/$sessionId.json');

      if (await file.exists()) {
        final content = await file.readAsString();
        return List<Map<String, dynamic>>.from(
            jsonDecode(content).map((item) => Map<String, dynamic>.from(item)));
      }
    } catch (e) {
      Logger.e(_tag, '加载任务数据失败: $e');
    }

    return null;
  }

  /// 恢复队列
  Future<void> _restoreQueue() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final queueJson = prefs.getString('processing_queue');

      if (queueJson != null) {
        final queueData = jsonDecode(queueJson) as List;

        for (final taskData in queueData) {
          final taskMap = Map<String, dynamic>.from(taskData);
          final sessionId = taskMap['sessionId'] as String;

          // 加载任务数据
          final dataItems = await _loadTaskData(sessionId);

          if (dataItems != null) {
            final task = ProcessingTask(
              sessionId: sessionId,
              dataItems: dataItems,
              strategy: _parseStrategy(taskMap['strategy']),
              timestamp: DateTime.parse(taskMap['timestamp']),
              retryCount: taskMap['retryCount'] ?? 0,
            );

            _processingQueue.add(task);
          }
        }

        Logger.i(_tag, '恢复了 ${_processingQueue.length} 个处理任务');
      }
    } catch (e) {
      Logger.e(_tag, '恢复队列失败: $e');
    }
  }

  /// 解析处理策略
  ProcessingStrategy _parseStrategy(String strategyStr) {
    for (final strategy in ProcessingStrategy.values) {
      if (strategyStr.contains(strategy.toString())) {
        return strategy;
      }
    }

    return ProcessingStrategy.hybrid;
  }

  /// 处理队列中的任务
  Future<void> _processQueue() async {
    if (_processingQueue.isEmpty || _isProcessingQueue) return;

    // 设置处理锁
    _isProcessingQueue = true;

    Logger.d(_tag, '开始处理队列，有 ${_processingQueue.length} 个待处理任务');

    try {
      // 创建队列副本，避免并发修改
      final tasks = List<ProcessingTask>.from(_processingQueue);
      final processedTaskIds = <String>[];

      for (final task in tasks) {
        // 跳过重试次数过多的任务
        if (task.retryCount >= 5) {
          Logger.w(_tag, '任务 ${task.sessionId} 重试次数过多，已跳过');
          processedTaskIds.add(task.sessionId);
          continue;
        }

        try {
          // 增加重试计数
          task.retryCount++;

          // 根据策略处理任务
          final result = await processMultimodalData(
            sessionId: task.sessionId,
            dataItems: task.dataItems,
            strategy: task.strategy,
          );

          if (result.success) {
            // 处理成功，标记任务完成
            processedTaskIds.add(task.sessionId);
            Logger.i(_tag, '队列任务 ${task.sessionId} 处理成功');

            // 删除任务数据文件
            await _deleteTaskData(task.sessionId);
          }
        } catch (e) {
          Logger.e(_tag, '处理队列任务 ${task.sessionId} 失败: $e');
        }
      }

      // 从队列中移除已处理的任务
      _processingQueue
          .removeWhere((task) => processedTaskIds.contains(task.sessionId));

      // 更新持久化队列
      await _persistQueue();
    } finally {
      // 释放处理锁
      _isProcessingQueue = false;
    }
  }

  /// 删除任务数据
  Future<void> _deleteTaskData(String sessionId) async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final file = File('${appDir.path}/tasks/$sessionId.json');

      if (await file.exists()) {
        await file.delete();
      }
    } catch (e) {
      Logger.e(_tag, '删除任务数据失败: $e');
    }
  }

  /// 过滤本地可处理数据
  List<Map<String, dynamic>> _filterLocalProcessableData(
      List<Map<String, dynamic>> dataItems) {
    // 实现本地可处理数据过滤逻辑
    return dataItems.where((item) {
      final type = item['type'];
      return type == SensorType.accelerometer.name ||
          type == SensorType.gyroscope.name ||
          type == SensorType.magnetometer.name ||
          type == SensorType.pedometer.name ||
          type == SensorType.light.name ||
          type == MultimodalDataType.text.name;
    }).toList();
  }

  /// 过滤云端可处理数据
  List<Map<String, dynamic>> _filterCloudProcessableData(
      List<Map<String, dynamic>> dataItems) {
    // 实现云端可处理数据过滤逻辑
    return dataItems.where((item) {
      final type = item['type'];
      return type == MultimodalDataType.image.name ||
          type == MultimodalDataType.audio.name ||
          type == MultimodalDataType.video.name ||
          type == MultimodalDataType.text.name;
    }).toList();
  }

  /// 准备云处理请求
  Map<String, dynamic> _prepareCloudRequest(
      String sessionId, List<Map<String, dynamic>> dataItems) {
    // 实现云处理请求准备逻辑
    return {
      'sessionId': sessionId,
      'dataItems': dataItems,
      'timestamp': DateTime.now().toIso8601String(),
      'deviceInfo': {
        'model': 'Unknown',
        'platform': Platform.operatingSystem,
        'osVersion': Platform.operatingSystemVersion,
        'appVersion': '1.0.0',
      },
    };
  }

  /// 合并本地和云端结果
  ProcessingResult _mergeResults(
      ProcessingResult localResult, ProcessingResult cloudResult) {
    // 实现结果合并逻辑
    if (!localResult.success) return cloudResult;
    if (!cloudResult.success) return localResult;

    // 合并洞察
    final mergedInsights = HealthInsight.merge(
      localResult.insights,
      cloudResult.insights,
    );

    // 合并额外数据
    final additionalData = <String, dynamic>{};
    if (localResult.additionalData != null) {
      additionalData.addAll(localResult.additionalData!);
    }
    if (cloudResult.additionalData != null) {
      additionalData.addAll(cloudResult.additionalData!);
    }

    return ProcessingResult.success(
      insights: mergedInsights,
      processingLocation: ProcessingLocation.hybrid,
      timestamp: DateTime.now(),
      additionalData: additionalData.isNotEmpty ? additionalData : null,
    );
  }

  /// 保存处理结果
  Future<void> _saveProcessingResult(
      String sessionId, HealthInsight insight) async {
    try {
      // 保存到文件
      final appDir = await getApplicationDocumentsDirectory();
      final resultDir = Directory('${appDir.path}/health_insights');

      if (!await resultDir.exists()) {
        await resultDir.create(recursive: true);
      }

      final file = File('${resultDir.path}/$sessionId.json');
      await file.writeAsString(jsonEncode(insight.toJson()));

      Logger.d(_tag, '保存了处理结果: ${file.path}');
    } catch (e) {
      Logger.e(_tag, '保存处理结果失败: $e');
    }
  }

  /// 加载处理结果
  Future<HealthInsight?> loadProcessingResult(String sessionId) async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final file = File('${appDir.path}/health_insights/$sessionId.json');

      if (await file.exists()) {
        final content = await file.readAsString();
        return HealthInsight.fromJson(jsonDecode(content));
      }
    } catch (e) {
      Logger.e(_tag, '加载处理结果失败: $e');
    }

    return null;
  }

  /// 初始化
  Future<void> initialize() async {
    Logger.i(_tag, '初始化云边协同服务');

    // 恢复队列
    await _restoreQueue();

    // 处理队列中的任务
    if (_connectionStatus != ConnectivityResult.none) {
      _processQueue();
    }
  }

  /// 处理用户上下文
  Future<ProcessingResult> processUserContext(UserContext context) async {
    try {
      // 使用边缘服务处理上下文数据
      final insights = await _edgeService.processUserContext(context);

      // 创建会话ID
      final sessionId = 'context_${DateTime.now().millisecondsSinceEpoch}';

      // 保存结果
      await _saveProcessingResult(sessionId, insights);

      return ProcessingResult.success(
        insights: insights,
        processingLocation: ProcessingLocation.edge,
        timestamp: DateTime.now(),
      );
    } catch (e) {
      Logger.e(_tag, '处理用户上下文失败: $e');
      return ProcessingResult.failure(
        error: '处理用户上下文失败: $e',
        timestamp: DateTime.now(),
      );
    }
  }

  /// 释放资源
  void dispose() {
    _queueProcessingTimer?.cancel();
  }
}
