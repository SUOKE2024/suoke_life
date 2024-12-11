import 'dart:async';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'resource_monitor.dart';

/// 本地AI处理器
class LocalAIProcessor {
  final ResourceMonitor _resourceMonitor;
  final Map<String, AIModel> _loadedModels = {};
  final Map<String, DateTime> _modelLastUsed = {};
  
  /// 最大加载模型数量
  static const int _maxLoadedModels = 3;
  
  /// 模型空闲超时时间（分钟）
  static const int _modelIdleTimeout = 30;
  
  LocalAIProcessor(this._resourceMonitor) {
    // 启动定期清理任务
    Timer.periodic(const Duration(minutes: 5), (_) => _cleanupIdleModels());
  }
  
  /// 处理数据
  Future<AIProcessResult> processData(
    dynamic data,
    String modelType,
    {Map<String, dynamic>? config}
  ) async {
    try {
      // 检查资源状态
      final status = await _checkResourceStatus();
      if (!status.canProcess) {
        return AIProcessResult.resourceLimited(status.reason);
      }
      
      // 获取或加载模型
      final model = await _getModel(modelType);
      if (model == null) {
        return AIProcessResult.error('Failed to load model: $modelType');
      }
      
      // 更新模型使用时间
      _modelLastUsed[modelType] = DateTime.now();
      
      // 预处理数据
      final processedData = await _preprocessData(data);
      
      // 执行推理
      final result = await model.inference(processedData, config);
      
      // 后处理结果
      final finalResult = await _postprocessResult(result);
      
      return AIProcessResult.success(finalResult);
    } catch (e) {
      return AIProcessResult.error('Processing failed: $e');
    }
  }
  
  /// 批量处理数据
  Future<List<AIProcessResult>> batchProcess(
    List<dynamic> dataList,
    String modelType,
    {Map<String, dynamic>? config}
  ) async {
    final results = <AIProcessResult>[];
    
    // 检查资源状态
    final status = await _checkResourceStatus();
    if (!status.canProcess) {
      return List.filled(
        dataList.length,
        AIProcessResult.resourceLimited(status.reason),
      );
    }
    
    // 获取可用计算资源
    final resource = await _getAvailableResource();
    
    // 根据资源情况决定批处理大小
    final batchSize = _calculateBatchSize(resource, dataList.length);
    
    // 分批处理
    for (var i = 0; i < dataList.length; i += batchSize) {
      final end = min(i + batchSize, dataList.length);
      final batch = dataList.sublist(i, end);
      
      // 并行处理当前批次
      final batchResults = await Future.wait(
        batch.map((data) => processData(data, modelType, config: config)),
      );
      
      results.addAll(batchResults);
    }
    
    return results;
  }
  
  /// 检查资源状态
  Future<ResourceStatus> _checkResourceStatus() async {
    try {
      final status = await _resourceMonitor.resourceStatusStream.first;
      
      if (!_resourceMonitor.isReadyForComputing(status)) {
        return ResourceStatus(
          canProcess: false,
          reason: 'Insufficient device resources',
        );
      }
      
      return ResourceStatus(canProcess: true);
    } catch (e) {
      return ResourceStatus(
        canProcess: false,
        reason: 'Failed to check resource status',
      );
    }
  }
  
  /// 获取可用计算资源
  Future<ComputeResource> _getAvailableResource() async {
    final status = await _resourceMonitor.resourceStatusStream.first;
    return _resourceMonitor.getAvailableResource(status);
  }
  
  /// 计算批处理大小
  int _calculateBatchSize(ComputeResource resource, int totalSize) {
    // 根据可用资源动态调整批处理大小
    final baseBatchSize = resource.cpuCores * 2;
    return min(baseBatchSize, totalSize);
  }
  
  /// 获取AI模型
  Future<AIModel?> _getModel(String modelType) async {
    // 检查是否已加载
    if (_loadedModels.containsKey(modelType)) {
      return _loadedModels[modelType];
    }
    
    // 如果已达到最大加载数量，清理最久未使用的模型
    if (_loadedModels.length >= _maxLoadedModels) {
      _cleanupOldestModel();
    }
    
    // 加载新模型
    try {
      final model = await AIModel.load(modelType);
      _loadedModels[modelType] = model;
      _modelLastUsed[modelType] = DateTime.now();
      return model;
    } catch (e) {
      print('Failed to load model $modelType: $e');
      return null;
    }
  }
  
  /// 清理最久未使用的模型
  void _cleanupOldestModel() {
    if (_modelLastUsed.isEmpty) return;
    
    String? oldestModel;
    DateTime? oldestTime;
    
    _modelLastUsed.forEach((model, time) {
      if (oldestTime == null || time.isBefore(oldestTime!)) {
        oldestModel = model;
        oldestTime = time;
      }
    });
    
    if (oldestModel != null) {
      _loadedModels.remove(oldestModel);
      _modelLastUsed.remove(oldestModel);
    }
  }
  
  /// 清理空闲模型
  void _cleanupIdleModels() {
    final now = DateTime.now();
    final idleModels = _modelLastUsed.entries
        .where((entry) => now.difference(entry.value).inMinutes > _modelIdleTimeout)
        .map((entry) => entry.key)
        .toList();
    
    for (final model in idleModels) {
      _loadedModels.remove(model);
      _modelLastUsed.remove(model);
    }
  }
  
  /// 预处理数据
  Future<dynamic> _preprocessData(dynamic data) async {
    // TODO: 实现数据预处理逻辑
    return data;
  }
  
  /// 后处理结果
  Future<dynamic> _postprocessResult(dynamic result) async {
    // TODO: 实现结果后处理逻辑
    return result;
  }
  
  /// 释放资源
  void dispose() {
    _loadedModels.clear();
    _modelLastUsed.clear();
  }
}

/// AI模型
class AIModel {
  final String type;
  
  AIModel(this.type);
  
  /// 加载模型
  static Future<AIModel> load(String type) async {
    // TODO: 实现模型加载逻辑
    return AIModel(type);
  }
  
  /// 执行推理
  Future<dynamic> inference(
    dynamic input,
    Map<String, dynamic>? config,
  ) async {
    // TODO: 实现模型推理逻辑
    return input;
  }
}

/// 资源状态
class ResourceStatus {
  final bool canProcess;
  final String? reason;
  
  ResourceStatus({
    required this.canProcess,
    this.reason,
  });
}

/// AI处理结果
class AIProcessResult {
  final bool success;
  final dynamic result;
  final String? error;
  
  AIProcessResult({
    required this.success,
    this.result,
    this.error,
  });
  
  factory AIProcessResult.success(dynamic result) {
    return AIProcessResult(
      success: true,
      result: result,
    );
  }
  
  factory AIProcessResult.error(String error) {
    return AIProcessResult(
      success: false,
      error: error,
    );
  }
  
  factory AIProcessResult.resourceLimited(String? reason) {
    return AIProcessResult(
      success: false,
      error: reason ?? 'Resource limited',
    );
  }
} 