import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_unity_widget/flutter_unity_widget.dart';
import 'package:suoke_life/presentation/visualization/providers/visualization_providers.dart';
import 'performance_monitor.dart';

/// 可视化分析器 - 专门用于收集和分析3D/VR/AR可视化的性能数据
class VisualizationProfiler extends StateNotifier<VisualizationProfilerState> {
  final Ref _ref;
  Timer? _profilingTimer;
  final int _samplingInterval = 5; // 秒
  final int _historySize = 20; // 保存历史记录条数
  final UnityWidgetController? _unityController;

  VisualizationProfiler(this._ref, this._unityController)
      : super(const VisualizationProfilerState()) {
    _initialize();
  }

  void _initialize() {
    state = VisualizationProfilerState(
      renderMetrics: RenderMetrics(
        frameRate: 0,
        renderTime: 0,
        drawCalls: 0,
        triangles: 0,
        vertices: 0,
      ),
      systemMetrics: SystemMetrics(
        memoryUsage: 0,
        cpuUsage: 0,
        gpuUsage: 0,
      ),
      sceneMetrics: SceneMetrics(
        nodeCount: 0,
        edgeCount: 0,
        visibleNodeCount: 0,
        visibleEdgeCount: 0,
        layoutTime: 0,
      ),
      interactionMetrics: InteractionMetrics(
        selectLatency: 0,
        dragLatency: 0,
        zoomLatency: 0,
        rotateLatency: 0,
      ),
      isRunning: false,
    );
  }

  void startProfiling() {
    if (state.isRunning) return;
    
    state = state.copyWith(isRunning: true);
    
    // 请求Unity发送性能数据
    _requestUnityPerformanceData();
    
    // 定期收集性能数据
    _profilingTimer = Timer.periodic(
      Duration(seconds: _samplingInterval),
      (_) => _collectPerformanceData(),
    );
  }

  void stopProfiling() {
    _profilingTimer?.cancel();
    state = state.copyWith(isRunning: false);
  }

  Future<void> _requestUnityPerformanceData() async {
    if (_unityController == null) return;
    
    _unityController!.postMessage(
      'PerformanceManager',
      'EnableProfiling',
      'true',
    );
  }

  Future<void> _collectPerformanceData() async {
    // 收集Unity渲染数据
    await _collectUnityMetrics();
    
    // 收集系统性能数据
    _collectSystemMetrics();
    
    // 收集场景数据
    _collectSceneMetrics();
    
    // 收集交互性能数据
    _collectInteractionMetrics();
    
    // 更新历史记录
    _updateHistory();
    
    // 更新全局性能监控
    _updateGlobalPerformanceMonitor();
  }

  Future<void> _collectUnityMetrics() async {
    if (_unityController == null) return;
    
    // 请求Unity性能数据
    _unityController!.postMessage(
      'PerformanceManager',
      'GetPerformanceData',
      '',
    );
    
    // 注意：Unity会通过OnUnityMessage回调返回数据
    // 这里模拟从Unity接收到的数据
    final renderMetrics = RenderMetrics(
      frameRate: 60,
      renderTime: 16.7,
      drawCalls: 100,
      triangles: 50000,
      vertices: 100000,
    );
    
    state = state.copyWith(renderMetrics: renderMetrics);
  }

  void _collectSystemMetrics() {
    // 模拟系统性能数据
    final systemMetrics = SystemMetrics(
      memoryUsage: 200 + (DateTime.now().millisecondsSinceEpoch % 100),
      cpuUsage: 20 + (DateTime.now().millisecondsSinceEpoch % 20),
      gpuUsage: 30 + (DateTime.now().millisecondsSinceEpoch % 30),
    );
    
    state = state.copyWith(systemMetrics: systemMetrics);
  }

  void _collectSceneMetrics() {
    // 从VisualizationController获取场景数据
    final visualizationState = _ref.read(visualizationControllerProvider);
    final sceneMetrics = SceneMetrics(
      nodeCount: visualizationState.nodes.length,
      edgeCount: visualizationState.edges.length,
      visibleNodeCount: visualizationState.nodes.length, // 实际值会小于等于总节点数
      visibleEdgeCount: visualizationState.edges.length, // 实际值会小于等于总边数
      layoutTime: 50.0, // 模拟值，实际应从Unity获取
    );
    
    state = state.copyWith(sceneMetrics: sceneMetrics);
  }

  void _collectInteractionMetrics() {
    // 模拟交互性能数据
    final interactionMetrics = InteractionMetrics(
      selectLatency: 10 + (DateTime.now().millisecondsSinceEpoch % 10),
      dragLatency: 15 + (DateTime.now().millisecondsSinceEpoch % 15),
      zoomLatency: 12 + (DateTime.now().millisecondsSinceEpoch % 12),
      rotateLatency: 18 + (DateTime.now().millisecondsSinceEpoch % 18),
    );
    
    state = state.copyWith(interactionMetrics: interactionMetrics);
  }

  void _updateHistory() {
    final newHistory = List<VisualizationProfilerState>.from(state.history)
      ..add(state);
    
    if (newHistory.length > _historySize) {
      newHistory.removeAt(0);
    }
    
    state = state.copyWith(history: newHistory);
  }

  void _updateGlobalPerformanceMonitor() {
    // 将可视化性能数据转换为全局性能监控格式
    final performanceMonitor = _ref.read(performanceMonitorProvider.notifier);
    
    // 构建渲染时间映射
    final renderTimes = <String, double>{
      'total': state.renderMetrics.renderTime,
      'layout': state.sceneMetrics.layoutTime,
    };
    
    // 构建交互延迟映射
    final interactionLatencies = <String, double>{
      'select': state.interactionMetrics.selectLatency,
      'drag': state.interactionMetrics.dragLatency,
      'zoom': state.interactionMetrics.zoomLatency,
      'rotate': state.interactionMetrics.rotateLatency,
    };
    
    // 使用反射或其他方式更新全局性能监控
    // 注：这里简化处理，实际实现可能需要调用performanceMonitor的内部方法
  }

  void handleUnityMessage(dynamic message) {
    if (message is Map<String, dynamic> && message['type'] == 'performanceData') {
      final data = message['data'];
      if (data != null) {
        final renderMetrics = RenderMetrics(
          frameRate: data['fps'] ?? 0,
          renderTime: data['renderTime'] ?? 0,
          drawCalls: data['drawCalls'] ?? 0,
          triangles: data['triangles'] ?? 0,
          vertices: data['vertices'] ?? 0,
        );
        
        state = state.copyWith(renderMetrics: renderMetrics);
      }
    }
  }

  // 获取特定时间范围的性能分析数据
  List<VisualizationProfilerState> getProfileDataInRange(DateTime start, DateTime end) {
    return state.history.where((data) {
      return data.timestamp.isAfter(start) && data.timestamp.isBefore(end);
    }).toList();
  }

  // 生成性能报告
  Map<String, dynamic> generatePerformanceReport() {
    if (state.history.isEmpty) return {};
    
    final List<double> frameRates = [];
    final List<double> renderTimes = [];
    final List<double> memoryUsages = [];
    
    for (final sample in state.history) {
      frameRates.add(sample.renderMetrics.frameRate);
      renderTimes.add(sample.renderMetrics.renderTime);
      memoryUsages.add(sample.systemMetrics.memoryUsage);
    }
    
    return {
      'averageFPS': _average(frameRates),
      'minFPS': frameRates.reduce((a, b) => a < b ? a : b),
      'maxFPS': frameRates.reduce((a, b) => a > b ? a : b),
      'averageRenderTime': _average(renderTimes),
      'averageMemoryUsage': _average(memoryUsages),
      'lastNodeCount': state.sceneMetrics.nodeCount,
      'lastEdgeCount': state.sceneMetrics.edgeCount,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  double _average(List<double> values) {
    if (values.isEmpty) return 0;
    return values.reduce((a, b) => a + b) / values.length;
  }

  @override
  void dispose() {
    _profilingTimer?.cancel();
    if (_unityController != null) {
      _unityController!.postMessage(
        'PerformanceManager',
        'EnableProfiling',
        'false',
      );
    }
    super.dispose();
  }
}

class VisualizationProfilerState {
  final RenderMetrics renderMetrics;
  final SystemMetrics systemMetrics;
  final SceneMetrics sceneMetrics;
  final InteractionMetrics interactionMetrics;
  final List<VisualizationProfilerState> history;
  final bool isRunning;
  final DateTime timestamp;

  const VisualizationProfilerState({
    this.renderMetrics = const RenderMetrics(),
    this.systemMetrics = const SystemMetrics(),
    this.sceneMetrics = const SceneMetrics(),
    this.interactionMetrics = const InteractionMetrics(),
    this.history = const [],
    this.isRunning = false,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  VisualizationProfilerState copyWith({
    RenderMetrics? renderMetrics,
    SystemMetrics? systemMetrics,
    SceneMetrics? sceneMetrics,
    InteractionMetrics? interactionMetrics,
    List<VisualizationProfilerState>? history,
    bool? isRunning,
  }) {
    return VisualizationProfilerState(
      renderMetrics: renderMetrics ?? this.renderMetrics,
      systemMetrics: systemMetrics ?? this.systemMetrics,
      sceneMetrics: sceneMetrics ?? this.sceneMetrics,
      interactionMetrics: interactionMetrics ?? this.interactionMetrics,
      history: history ?? this.history,
      isRunning: isRunning ?? this.isRunning,
    );
  }
}

class RenderMetrics {
  final double frameRate;
  final double renderTime;
  final int drawCalls;
  final int triangles;
  final int vertices;

  const RenderMetrics({
    this.frameRate = 0,
    this.renderTime = 0,
    this.drawCalls = 0,
    this.triangles = 0,
    this.vertices = 0,
  });
}

class SystemMetrics {
  final double memoryUsage;
  final double cpuUsage;
  final double gpuUsage;

  const SystemMetrics({
    this.memoryUsage = 0,
    this.cpuUsage = 0,
    this.gpuUsage = 0,
  });
}

class SceneMetrics {
  final int nodeCount;
  final int edgeCount;
  final int visibleNodeCount;
  final int visibleEdgeCount;
  final double layoutTime;

  const SceneMetrics({
    this.nodeCount = 0,
    this.edgeCount = 0,
    this.visibleNodeCount = 0,
    this.visibleEdgeCount = 0,
    this.layoutTime = 0,
  });
}

class InteractionMetrics {
  final double selectLatency;
  final double dragLatency;
  final double zoomLatency;
  final double rotateLatency;

  const InteractionMetrics({
    this.selectLatency = 0,
    this.dragLatency = 0,
    this.zoomLatency = 0,
    this.rotateLatency = 0,
  });
}

final visualizationProfilerProvider = StateNotifierProvider.family<
    VisualizationProfiler, VisualizationProfilerState, UnityWidgetController?>(
  (ref, controller) => VisualizationProfiler(ref, controller),
);