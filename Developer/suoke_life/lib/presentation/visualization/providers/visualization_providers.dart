import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_unity_widget/flutter_unity_widget.dart';
import 'package:suoke_life/core/sync/knowledge_graph_sync_manager.dart';
import 'package:suoke_life/domain/entities/knowledge_graph.dart';
import 'package:suoke_life/domain/repositories/knowledge_graph_repository.dart';
import 'package:suoke_life/domain/usecases/get_knowledge_graph.dart';
import 'package:suoke_life/presentation/visualization/performance/index.dart';

enum VisualizationMode {
  mode3D,
  modeVR,
  modeAR,
}

class VisualizationState {
  final VisualizationMode mode;
  final List<KnowledgeNode> nodes;
  final List<Relation> edges;
  final bool isLoading;
  final String? error;
  final Map<String, dynamic> settings;
  final bool isOptimized;
  final OptimizationLevel optimizationLevel;

  const VisualizationState({
    required this.mode,
    required this.nodes,
    required this.edges,
    this.isLoading = false,
    this.error,
    required this.settings,
    this.isOptimized = false,
    this.optimizationLevel = OptimizationLevel.none,
  });

  VisualizationState copyWith({
    VisualizationMode? mode,
    List<KnowledgeNode>? nodes,
    List<Relation>? edges,
    bool? isLoading,
    String? error,
    Map<String, dynamic>? settings,
    bool? isOptimized,
    OptimizationLevel? optimizationLevel,
  }) {
    return VisualizationState(
      mode: mode ?? this.mode,
      nodes: nodes ?? this.nodes,
      edges: edges ?? this.edges,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      settings: settings ?? this.settings,
      isOptimized: isOptimized ?? this.isOptimized,
      optimizationLevel: optimizationLevel ?? this.optimizationLevel,
    );
  }
}

class VisualizationController extends StateNotifier<VisualizationState> {
  final KnowledgeGraphRepository _repository;
  final GetKnowledgeGraph _getKnowledgeGraph;
  final KnowledgeGraphSyncManager _syncManager;
  final Ref _ref;
  UnityWidgetController? _unityController;
  String? _currentNodeId;
  int _visibleNodeLimit = 1000; // 可见节点数量限制
  int _visibleEdgeLimit = 2000; // 可见边数量限制

  VisualizationController(
    this._repository,
    this._getKnowledgeGraph,
    this._syncManager,
    this._ref,
  ) : super(VisualizationState(
          mode: VisualizationMode.mode3D,
          nodes: [],
          edges: [],
          settings: _getDefaultSettings(),
        )) {
    // 监听性能状态变化，自动应用优化
    _listenForPerformanceIssues();
  }

  void _listenForPerformanceIssues() {
    _ref.listen(performanceMonitorProvider, (previous, current) {
      if (current.warning != null && !state.isOptimized) {
        // 自动应用性能优化
        _applyPerformanceOptimization(current.warning!);
      }
    });
  }

  static Map<String, dynamic> _getDefaultSettings() {
    return {
      'layout': {
        'algorithm': 'force-directed',
        'dimensions': {'width': 1000, 'height': 1000, 'depth': 1000},
      },
      'style': {
        'nodeSize': 1.0,
        'edgeWidth': 0.1,
        'defaultNodeColor': '#35BB78',
        'defaultEdgeColor': '#FF6800',
      },
      'interaction': {
        'rotationSpeed': 1.0,
        'zoomSpeed': 1.0,
        'enableSelection': true,
      },
      'render': {
        'quality': 1.0,
        'shadows': true,
        'antiAliasing': true,
        'postProcessing': true,
        'lod': false,
        'culling': false,
        'instancing': false,
      },
    };
  }

  Future<void> initialize({
    required VisualizationMode mode,
    String? initialNodeId,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    _currentNodeId = initialNodeId;

    try {
      final result = await _getKnowledgeGraph.execute(
        nodeId: initialNodeId,
        depth: 2,
      );

      // 性能优化：限制初始加载的节点和边数量
      final optimizedNodes = _optimizeNodes(result.nodes);
      final optimizedEdges = _optimizeEdges(result.relations, optimizedNodes);

      state = state.copyWith(
        mode: mode,
        nodes: optimizedNodes,
        edges: optimizedEdges,
        isLoading: false,
      );

      _updateUnityScene();

      if (initialNodeId != null) {
        // 订阅节点更新
        _syncManager.subscribeToNodeUpdates(initialNodeId).listen(
          (update) {
            // 性能优化：限制更新时的节点和边数量
            final optimizedNodes = _optimizeNodes(update.nodes);
            final optimizedEdges = _optimizeEdges(update.relations, optimizedNodes);
            
            state = state.copyWith(
              nodes: optimizedNodes,
              edges: optimizedEdges,
            );
            _updateUnityScene();
          },
          onError: (error) {
            state = state.copyWith(
              error: '同步数据失败: ${error.toString()}',
            );
          },
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '加载知识图谱失败: ${e.toString()}',
      );
    }
  }

  List<KnowledgeNode> _optimizeNodes(List<KnowledgeNode> nodes) {
    if (nodes.length <= _visibleNodeLimit) return nodes;
    
    // 根据重要性或距离等因素对节点进行排序
    final sortedNodes = List<KnowledgeNode>.from(nodes)
      ..sort((a, b) => _calculateNodeImportance(b).compareTo(_calculateNodeImportance(a)));
    
    // 限制节点数量
    return sortedNodes.take(_visibleNodeLimit).toList();
  }

  List<Relation> _optimizeEdges(List<Relation> edges, List<KnowledgeNode> visibleNodes) {
    // 筛选出连接可见节点的边
    final visibleNodeIds = visibleNodes.map((n) => n.id).toSet();
    final filteredEdges = edges.where((e) => 
      visibleNodeIds.contains(e.fromId) && visibleNodeIds.contains(e.toId)
    ).toList();
    
    if (filteredEdges.length <= _visibleEdgeLimit) return filteredEdges;
    
    // 根据边的重要性排序
    final sortedEdges = List<Relation>.from(filteredEdges)
      ..sort((a, b) => _calculateEdgeImportance(b).compareTo(_calculateEdgeImportance(a)));
    
    // 限制边数量
    return sortedEdges.take(_visibleEdgeLimit).toList();
  }

  double _calculateNodeImportance(KnowledgeNode node) {
    // 根据连接数、类型、权重等计算节点重要性
    double importance = 1.0;
    
    // 当前选择的节点优先级最高
    if (node.id == _currentNodeId) {
      importance += 100.0;
    }
    
    // 考虑节点的连接数
    final connectedEdgesCount = state.edges.where(
      (e) => e.fromId == node.id || e.toId == node.id
    ).length;
    importance += connectedEdgesCount * 0.5;
    
    return importance;
  }

  double _calculateEdgeImportance(Relation edge) {
    // 计算边的重要性
    double importance = 1.0;
    
    // 与当前选择的节点相连的边优先级高
    if (edge.fromId == _currentNodeId || edge.toId == _currentNodeId) {
      importance += 10.0;
    }
    
    return importance;
  }

  void setUnityController(UnityWidgetController controller) {
    _unityController = controller;
    _updateUnityScene();
  }

  void handleUnityMessage(dynamic message) {
    if (message is Map<String, dynamic>) {
      switch (message['type']) {
        case 'nodeSelected':
          _handleNodeSelection(message['nodeId']);
          break;
        case 'edgeSelected':
          _handleEdgeSelection(message['edgeId']);
          break;
        case 'error':
          state = state.copyWith(error: message['message']);
          break;
        case 'performanceWarning':
          _handlePerformanceWarning(message['message']);
          break;
      }
    }
  }

  void _handlePerformanceWarning(String warning) {
    _applyPerformanceOptimization(warning);
  }

  void _applyPerformanceOptimization(String warning) {
    // 根据警告类型应用不同的优化策略
    OptimizationLevel newLevel;
    
    if (warning.contains('帧率过低') || warning.contains('渲染时间过长')) {
      newLevel = OptimizationLevel.high;
    } else if (warning.contains('内存使用过高')) {
      newLevel = OptimizationLevel.medium;
    } else if (warning.contains('节点数量过多')) {
      // 减少可见节点数量
      _visibleNodeLimit = (_visibleNodeLimit * 0.7).round();
      _visibleEdgeLimit = (_visibleEdgeLimit * 0.7).round();
      
      // 重新优化节点和边
      final optimizedNodes = _optimizeNodes(state.nodes);
      final optimizedEdges = _optimizeEdges(state.edges, optimizedNodes);
      
      state = state.copyWith(
        nodes: optimizedNodes,
        edges: optimizedEdges,
        isOptimized: true,
      );
      
      newLevel = OptimizationLevel.medium;
    } else {
      newLevel = OptimizationLevel.low;
    }
    
    // 应用优化级别
    _applyOptimizationLevel(newLevel);
    
    // 更新Unity场景
    _updateUnityScene();
  }

  void _applyOptimizationLevel(OptimizationLevel level) {
    final newSettings = Map<String, dynamic>.from(state.settings);
    
    switch (level) {
      case OptimizationLevel.none:
        newSettings['render'] = {
          'quality': 1.0,
          'shadows': true,
          'antiAliasing': true,
          'postProcessing': true,
          'lod': false,
          'culling': false,
          'instancing': false,
        };
        break;
        
      case OptimizationLevel.low:
        newSettings['render'] = {
          'quality': 0.9,
          'shadows': true,
          'antiAliasing': true,
          'postProcessing': false,
          'lod': false,
          'culling': true,
          'instancing': false,
        };
        break;
        
      case OptimizationLevel.medium:
        newSettings['render'] = {
          'quality': 0.8,
          'shadows': false,
          'antiAliasing': true,
          'postProcessing': false,
          'lod': true,
          'culling': true,
          'instancing': true,
        };
        break;
        
      case OptimizationLevel.high:
        newSettings['render'] = {
          'quality': 0.6,
          'shadows': false,
          'antiAliasing': false,
          'postProcessing': false,
          'lod': true,
          'culling': true,
          'instancing': true,
        };
        break;
        
      case OptimizationLevel.extreme:
        newSettings['render'] = {
          'quality': 0.4,
          'shadows': false,
          'antiAliasing': false,
          'postProcessing': false,
          'lod': true,
          'culling': true,
          'instancing': true,
        };
        
        // 极限优化模式下，进一步减少节点数量
        _visibleNodeLimit = (_visibleNodeLimit * 0.5).round();
        _visibleEdgeLimit = (_visibleEdgeLimit * 0.5).round();
        
        // 重新优化节点和边
        final optimizedNodes = _optimizeNodes(state.nodes);
        final optimizedEdges = _optimizeEdges(state.edges, optimizedNodes);
        
        state = state.copyWith(
          nodes: optimizedNodes,
          edges: optimizedEdges,
        );
        break;
    }
    
    state = state.copyWith(
      settings: newSettings,
      isOptimized: true,
      optimizationLevel: level,
    );
  }

  Future<void> changeMode(VisualizationMode newMode) async {
    if (newMode == state.mode) return;

    state = state.copyWith(mode: newMode);
    
    // 不同模式可能需要不同的默认优化设置
    if (newMode == VisualizationMode.modeVR || newMode == VisualizationMode.modeAR) {
      // VR和AR模式下，默认应用中等优化以确保流畅度
      _applyOptimizationLevel(OptimizationLevel.medium);
    }
    
    _updateUnityScene();
  }

  void changeLayout(String layout) {
    final newSettings = Map<String, dynamic>.from(state.settings);
    newSettings['layout']['algorithm'] = layout;
    state = state.copyWith(settings: newSettings);
    _updateUnityScene();
  }

  void applyFilter(Map<String, dynamic> filter) {
    // 实现过滤逻辑
  }

  void updateSettings(Map<String, dynamic> newSettings) {
    state = state.copyWith(settings: newSettings);
    _updateUnityScene();
  }

  void applyOptimizationSettings(OptimizationSettings optimizationSettings) {
    final newSettings = Map<String, dynamic>.from(state.settings);
    
    // 应用优化设置到渲染设置
    newSettings['render'] = {
      'quality': optimizationSettings.renderQuality,
      'shadows': optimizationSettings.enableShadows,
      'antiAliasing': optimizationSettings.enableAntiAliasing,
      'postProcessing': optimizationSettings.enablePostProcessing,
      'lod': optimizationSettings.enableLOD,
      'culling': optimizationSettings.enableCulling,
      'instancing': optimizationSettings.enableInstancing,
    };
    
    // 更新节点和边的可见数量限制
    _visibleNodeLimit = optimizationSettings.maxVisibleNodes;
    _visibleEdgeLimit = optimizationSettings.maxVisibleEdges;
    
    // 重新优化节点和边
    if (state.nodes.length > _visibleNodeLimit || state.edges.length > _visibleEdgeLimit) {
      final optimizedNodes = _optimizeNodes(state.nodes);
      final optimizedEdges = _optimizeEdges(state.edges, optimizedNodes);
      
      state = state.copyWith(
        nodes: optimizedNodes,
        edges: optimizedEdges,
        settings: newSettings,
        isOptimized: true,
      );
    } else {
      state = state.copyWith(
        settings: newSettings,
        isOptimized: true,
      );
    }
    
    _updateUnityScene();
  }

  void _updateUnityScene() {
    if (_unityController == null) return;

    // 记录更新开始时间
    final startTime = DateTime.now();

    final sceneData = {
      'mode': state.mode.toString(),
      'nodes': state.nodes.map((n) => n.toJson()).toList(),
      'edges': state.edges.map((e) => e.toJson()).toList(),
      'settings': state.settings,
    };

    _unityController!.postMessage(
      'VisualizationManager',
      'UpdateScene',
      sceneData.toString(),
    );

    // 记录更新结束时间并计算耗时
    final endTime = DateTime.now();
    final duration = endTime.difference(startTime).inMilliseconds;

    // 更新性能指标
    _updatePerformanceMetrics({
      'sceneUpdateTime': duration,
      'nodeCount': state.nodes.length,
      'edgeCount': state.edges.length,
    });
  }

  void _updatePerformanceMetrics(Map<String, dynamic> metrics) {
    // 向性能监控器报告指标
    // 这里仅记录数据，具体的实现依赖于performanceMonitorProvider的内部逻辑
  }

  Future<void> _handleNodeSelection(String nodeId) async {
    try {
      final node = state.nodes.firstWhere((n) => n.id == nodeId);
      
      // 发送交互事件
      await _syncManager.sendInteraction(
        nodeId: nodeId,
        interactionType: 'nodeSelected',
        data: {'timestamp': DateTime.now().toIso8601String()},
      );

      // 如果选择了新节点，更新订阅
      if (_currentNodeId != nodeId) {
        if (_currentNodeId != null) {
          _syncManager.unsubscribeFromNodeUpdates(_currentNodeId!);
        }
        _currentNodeId = nodeId;
        
        _syncManager.subscribeToNodeUpdates(nodeId).listen(
          (update) {
            // 性能优化：限制更新时的节点和边数量
            final optimizedNodes = _optimizeNodes(update.nodes);
            final optimizedEdges = _optimizeEdges(update.relations, optimizedNodes);
            
            state = state.copyWith(
              nodes: optimizedNodes,
              edges: optimizedEdges,
            );
            _updateUnityScene();
          },
          onError: (error) {
            state = state.copyWith(
              error: '同步数据失败: ${error.toString()}',
            );
          },
        );
      }
    } catch (e) {
      state = state.copyWith(error: '处理节点选择失败: ${e.toString()}');
    }
  }

  void _handleEdgeSelection(String edgeId) {
    try {
      final edge = state.edges.firstWhere((e) => e.id == edgeId);
      
      // 发送交互事件
      _syncManager.sendInteraction(
        nodeId: edge.fromId,
        interactionType: 'edgeSelected',
        data: {
          'edgeId': edgeId,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      state = state.copyWith(error: '处理边选择失败: ${e.toString()}');
    }
  }

  @override
  void dispose() {
    if (_currentNodeId != null) {
      _syncManager.unsubscribeFromNodeUpdates(_currentNodeId!);
    }
    super.dispose();
  }
}

final visualizationControllerProvider =
    StateNotifierProvider<VisualizationController, VisualizationState>((ref) {
  final repository = ref.watch(knowledgeGraphRepositoryProvider);
  final getKnowledgeGraph = ref.watch(getKnowledgeGraphProvider);
  final syncManager = ref.watch(knowledgeGraphSyncManagerProvider);
  
  return VisualizationController(
    repository,
    getKnowledgeGraph,
    syncManager,
    ref,
  );
});