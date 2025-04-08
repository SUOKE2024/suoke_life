import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'performance_monitor.dart';
import 'optimization_manager.dart';

class PerformanceMonitorWidget extends ConsumerStatefulWidget {
  const PerformanceMonitorWidget({Key? key}) : super(key: key);

  @override
  ConsumerState<PerformanceMonitorWidget> createState() =>
      _PerformanceMonitorWidgetState();
}

class _PerformanceMonitorWidgetState
    extends ConsumerState<PerformanceMonitorWidget> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(performanceMonitorProvider.notifier).startMonitoring();
    });
  }

  @override
  Widget build(BuildContext context) {
    final performanceState = ref.watch(performanceMonitorProvider);
    final optimizationState = ref.watch(optimizationManagerProvider);

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildHeader(performanceState, optimizationState),
            const SizedBox(height: 16),
            _buildMetricsGrid(performanceState.currentMetrics),
            if (performanceState.history.isNotEmpty) ...[
              const SizedBox(height: 16),
              _buildPerformanceChart(performanceState.history),
            ],
            const SizedBox(height: 16),
            _buildOptimizationControls(optimizationState),
            if (performanceState.warning != null)
              _buildWarningBanner(performanceState.warning!),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(
      PerformanceState performanceState, OptimizationState optimizationState) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Text(
          '性能监控',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        Row(
          children: [
            Switch(
              value: performanceState.isMonitoring,
              onChanged: (value) {
                if (value) {
                  ref.read(performanceMonitorProvider.notifier).startMonitoring();
                } else {
                  ref.read(performanceMonitorProvider.notifier).stopMonitoring();
                }
              },
            ),
            const SizedBox(width: 8),
            Text(
              performanceState.isMonitoring ? '监控中' : '已停止',
              style: TextStyle(
                color: performanceState.isMonitoring
                    ? Colors.green
                    : Colors.grey,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricsGrid(PerformanceMetrics metrics) {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      childAspectRatio: 3,
      children: [
        _buildMetricTile('FPS', '${metrics.fps.toStringAsFixed(1)}'),
        _buildMetricTile('内存使用', '${metrics.memoryUsage.toStringAsFixed(1)} MB'),
        _buildMetricTile('节点数量', '${metrics.nodeCount}'),
        _buildMetricTile('边数量', '${metrics.edgeCount}'),
      ],
    );
  }

  Widget _buildMetricTile(String label, String value) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceChart(List<PerformanceMetrics> history) {
    return SizedBox(
      height: 200,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: true),
          titlesData: FlTitlesData(show: false),
          borderData: FlBorderData(show: true),
          lineBarsData: [
            _createLineBarsData(history, (m) => m.fps, Colors.blue),
            _createLineBarsData(history, (m) => m.memoryUsage / 100, Colors.red),
          ],
        ),
      ),
    );
  }

  LineChartBarData _createLineBarsData(List<PerformanceMetrics> history,
      double Function(PerformanceMetrics) getValue, Color color) {
    return LineChartBarData(
      spots: history
          .asMap()
          .entries
          .map((e) => FlSpot(e.key.toDouble(), getValue(e.value)))
          .toList(),
      isCurved: true,
      color: color,
      barWidth: 2,
      isStrokeCapRound: true,
      dotData: FlDotData(show: false),
      belowBarData: BarAreaData(show: false),
    );
  }

  Widget _buildOptimizationControls(OptimizationState state) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              '优化设置',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            Switch(
              value: state.isAutoOptimizing,
              onChanged: (value) {
                if (value) {
                  ref
                      .read(optimizationManagerProvider.notifier)
                      .enableAutoOptimization();
                } else {
                  ref
                      .read(optimizationManagerProvider.notifier)
                      .disableAutoOptimization();
                }
              },
            ),
          ],
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<OptimizationLevel>(
          value: state.currentLevel,
          decoration: const InputDecoration(
            labelText: '优化级别',
            border: OutlineInputBorder(),
          ),
          items: OptimizationLevel.values
              .map((level) => DropdownMenuItem(
                    value: level,
                    child: Text(_getOptimizationLevelName(level)),
                  ))
              .toList(),
          onChanged: (level) {
            if (level != null) {
              ref
                  .read(optimizationManagerProvider.notifier)
                  .setOptimizationLevel(level);
            }
          },
        ),
        if (state.lastOptimization != null) ...[
          const SizedBox(height: 8),
          Text(
            state.lastOptimization!,
            style: const TextStyle(
              fontSize: 12,
              color: Colors.grey,
            ),
          ),
        ],
      ],
    );
  }

  String _getOptimizationLevelName(OptimizationLevel level) {
    switch (level) {
      case OptimizationLevel.none:
        return '无优化';
      case OptimizationLevel.low:
        return '低级优化';
      case OptimizationLevel.medium:
        return '中级优化';
      case OptimizationLevel.high:
        return '高级优化';
      case OptimizationLevel.extreme:
        return '极限优化';
    }
  }

  Widget _buildWarningBanner(String warning) {
    return Container(
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.warning_amber_rounded,
            color: Colors.orange,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              warning,
              style: const TextStyle(
                color: Colors.orange,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}