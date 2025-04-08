import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'performance_monitor.dart';
import 'optimization_manager.dart';
import 'visualization_profiler.dart';

/// 自动优化触发条件
class OptimizationTriggerConfig {
  final double lowFpsThreshold;
  final double highMemoryThreshold;
  final int highNodeCountThreshold;
  final double highRenderTimeThreshold;
  final int consecutiveWarningsThreshold;
  final bool enableAutoTrigger;
  final OptimizationLevel initialLevel;
  final OptimizationLevel maxLevel;

  const OptimizationTriggerConfig({
    this.lowFpsThreshold = 30.0,
    this.highMemoryThreshold = 500.0,
    this.highNodeCountThreshold = 1000,
    this.highRenderTimeThreshold = 16.0,
    this.consecutiveWarningsThreshold = 3,
    this.enableAutoTrigger = true,
    this.initialLevel = OptimizationLevel.none,
    this.maxLevel = OptimizationLevel.high,
  });

  OptimizationTriggerConfig copyWith({
    double? lowFpsThreshold,
    double? highMemoryThreshold,
    int? highNodeCountThreshold,
    double? highRenderTimeThreshold,
    int? consecutiveWarningsThreshold,
    bool? enableAutoTrigger,
    OptimizationLevel? initialLevel,
    OptimizationLevel? maxLevel,
  }) {
    return OptimizationTriggerConfig(
      lowFpsThreshold: lowFpsThreshold ?? this.lowFpsThreshold,
      highMemoryThreshold: highMemoryThreshold ?? this.highMemoryThreshold,
      highNodeCountThreshold: highNodeCountThreshold ?? this.highNodeCountThreshold,
      highRenderTimeThreshold: highRenderTimeThreshold ?? this.highRenderTimeThreshold,
      consecutiveWarningsThreshold: consecutiveWarningsThreshold ?? this.consecutiveWarningsThreshold,
      enableAutoTrigger: enableAutoTrigger ?? this.enableAutoTrigger,
      initialLevel: initialLevel ?? this.initialLevel,
      maxLevel: maxLevel ?? this.maxLevel,
    );
  }
}

/// 自动优化触发器状态
class AutoOptimizationTriggerState {
  final OptimizationTriggerConfig config;
  final OptimizationLevel currentLevel;
  final List<String> recentWarnings;
  final bool isEnabled;
  final String? lastTriggeredReason;
  final DateTime? lastOptimizationTime;

  const AutoOptimizationTriggerState({
    required this.config,
    this.currentLevel = OptimizationLevel.none,
    this.recentWarnings = const [],
    this.isEnabled = true,
    this.lastTriggeredReason,
    this.lastOptimizationTime,
  });

  AutoOptimizationTriggerState copyWith({
    OptimizationTriggerConfig? config,
    OptimizationLevel? currentLevel,
    List<String>? recentWarnings,
    bool? isEnabled,
    String? lastTriggeredReason,
    DateTime? lastOptimizationTime,
  }) {
    return AutoOptimizationTriggerState(
      config: config ?? this.config,
      currentLevel: currentLevel ?? this.currentLevel,
      recentWarnings: recentWarnings ?? this.recentWarnings,
      isEnabled: isEnabled ?? this.isEnabled,
      lastTriggeredReason: lastTriggeredReason,
      lastOptimizationTime: lastOptimizationTime ?? this.lastOptimizationTime,
    );
  }
}

/// 自动优化触发器 - 监控性能指标并自动触发优化
class AutoOptimizationTrigger extends StateNotifier<AutoOptimizationTriggerState> {
  final Ref _ref;
  
  AutoOptimizationTrigger(this._ref)
      : super(AutoOptimizationTriggerState(
          config: const OptimizationTriggerConfig(),
        )) {
    // 初始化监听
    _initializeListeners();
  }

  void _initializeListeners() {
    // 监听性能监控数据
    _ref.listen<PerformanceState>(
      performanceMonitorProvider,
      (previous, current) {
        if (!state.isEnabled || !state.config.enableAutoTrigger) return;
        
        if (current.warning != null) {
          _evaluateWarning(current.warning!);
        } else if (state.recentWarnings.isNotEmpty) {
          // 清除警告历史
          state = state.copyWith(recentWarnings: []);
        }
      },
    );
    
    // 监听可视化分析器数据
    _ref.listen<VisualizationProfilerState>(
      visualizationProfilerProvider(null),
      (previous, current) {
        if (!state.isEnabled || !state.config.enableAutoTrigger) return;
        
        // 评估性能指标是否需要优化
        _evaluatePerformanceMetrics(current);
      },
    );
  }
  
  void _evaluateWarning(String warning) {
    // 更新最近警告历史
    final newWarnings = List<String>.from(state.recentWarnings)..add(warning);
    if (newWarnings.length > state.config.consecutiveWarningsThreshold) {
      newWarnings.removeAt(0);
    }
    
    state = state.copyWith(recentWarnings: newWarnings);
    
    // 如果连续警告达到阈值，触发优化
    if (newWarnings.length >= state.config.consecutiveWarningsThreshold) {
      // 分析警告类型
      final warningTypes = _analyzeWarningTypes(newWarnings);
      
      // 根据警告类型确定下一级优化级别
      final nextLevel = _determineNextOptimizationLevel(warningTypes);
      
      // 如果当前级别低于建议级别，触发优化
      if (_shouldApplyOptimization(nextLevel)) {
        _applyOptimization(nextLevel, '连续${newWarnings.length}次性能警告: ${warningTypes.join(", ")}');
      }
    }
  }
  
  void _evaluatePerformanceMetrics(VisualizationProfilerState profilerState) {
    // 检查是否需要基于具体指标进行优化
    final warnings = <String>[];
    
    // 检查帧率
    if (profilerState.renderMetrics.frameRate < state.config.lowFpsThreshold) {
      warnings.add('帧率过低');
    }
    
    // 检查内存使用
    if (profilerState.systemMetrics.memoryUsage > state.config.highMemoryThreshold) {
      warnings.add('内存使用过高');
    }
    
    // 检查节点数量
    if (profilerState.sceneMetrics.nodeCount > state.config.highNodeCountThreshold) {
      warnings.add('节点数量过多');
    }
    
    // 检查渲染时间
    if (profilerState.renderMetrics.renderTime > state.config.highRenderTimeThreshold) {
      warnings.add('渲染时间过长');
    }
    
    // 如果发现性能问题，更新警告并评估是否需要优化
    if (warnings.isNotEmpty) {
      final warning = warnings.join(', ');
      _evaluateWarning(warning);
    }
  }
  
  List<String> _analyzeWarningTypes(List<String> warnings) {
    final warningTypes = <String>{};
    
    for (final warning in warnings) {
      if (warning.contains('帧率过低')) {
        warningTypes.add('低帧率');
      } else if (warning.contains('内存使用过高')) {
        warningTypes.add('高内存使用');
      } else if (warning.contains('节点数量过多')) {
        warningTypes.add('节点过多');
      } else if (warning.contains('渲染时间过长')) {
        warningTypes.add('渲染时间长');
      }
    }
    
    return warningTypes.toList();
  }
  
  OptimizationLevel _determineNextOptimizationLevel(List<String> warningTypes) {
    // 根据警告类型和严重程度确定下一级优化级别
    if (warningTypes.contains('低帧率') && warningTypes.contains('渲染时间长')) {
      // 严重的性能问题
      return _getNextLevel(OptimizationLevel.high);
    } else if (warningTypes.length >= 2) {
      // 多种性能问题
      return _getNextLevel(OptimizationLevel.medium);
    } else {
      // 单一性能问题
      return _getNextLevel(OptimizationLevel.low);
    }
  }
  
  OptimizationLevel _getNextLevel(OptimizationLevel suggestionLevel) {
    // 计算下一级优化级别，确保不超过配置的最大级别
    final currentValue = state.currentLevel.index;
    final suggestedValue = suggestionLevel.index;
    
    // 如果建议的级别低于当前级别，保持当前级别
    if (suggestedValue <= currentValue) {
      return state.currentLevel;
    }
    
    // 逐级提升优化级别
    final nextValue = currentValue + 1;
    
    // 确保不超过最大级别
    if (nextValue > state.config.maxLevel.index) {
      return state.config.maxLevel;
    }
    
    return OptimizationLevel.values[nextValue];
  }
  
  bool _shouldApplyOptimization(OptimizationLevel nextLevel) {
    // 确定是否应该应用优化
    // 1. 只有更高级别的优化才会触发
    // 2. 如果距离上次优化时间太近，可能不触发
    
    // 检查级别
    if (nextLevel.index <= state.currentLevel.index) {
      return false;
    }
    
    // 检查时间限制（避免过于频繁的优化调整）
    if (state.lastOptimizationTime != null) {
      final timeSinceLastOptimization = DateTime.now().difference(state.lastOptimizationTime!);
      // 至少等待5秒再次优化
      if (timeSinceLastOptimization.inSeconds < 5) {
        return false;
      }
    }
    
    return true;
  }
  
  void _applyOptimization(OptimizationLevel level, String reason) {
    // 更新状态
    state = state.copyWith(
      currentLevel: level,
      lastTriggeredReason: reason,
      lastOptimizationTime: DateTime.now(),
    );
    
    // 应用优化设置
    _ref.read(optimizationManagerProvider.notifier).setOptimizationLevel(level);
  }
  
  void updateConfig(OptimizationTriggerConfig config) {
    state = state.copyWith(config: config);
  }
  
  void enable() {
    if (!state.isEnabled) {
      state = state.copyWith(isEnabled: true);
    }
  }
  
  void disable() {
    if (state.isEnabled) {
      state = state.copyWith(isEnabled: false);
    }
  }
  
  void resetWarnings() {
    state = state.copyWith(recentWarnings: []);
  }
  
  void resetToLevel(OptimizationLevel level) {
    state = state.copyWith(
      currentLevel: level,
      recentWarnings: [],
      lastTriggeredReason: '手动重置到${_getLevelName(level)}级别',
      lastOptimizationTime: DateTime.now(),
    );
    
    // 应用优化设置
    _ref.read(optimizationManagerProvider.notifier).setOptimizationLevel(level);
  }
  
  String _getLevelName(OptimizationLevel level) {
    switch (level) {
      case OptimizationLevel.none:
        return '无优化';
      case OptimizationLevel.low:
        return '低级';
      case OptimizationLevel.medium:
        return '中级';
      case OptimizationLevel.high:
        return '高级';
      case OptimizationLevel.extreme:
        return '极限';
    }
  }
}

final autoOptimizationTriggerProvider =
    StateNotifierProvider<AutoOptimizationTrigger, AutoOptimizationTriggerState>((ref) {
  return AutoOptimizationTrigger(ref);
});