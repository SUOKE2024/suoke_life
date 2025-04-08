import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'visualization_profiler.dart';

class PerformanceReportWidget extends ConsumerWidget {
  final bool showDetails;

  const PerformanceReportWidget({
    Key? key,
    this.showDetails = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profilerFamily = ref.watch(visualizationProfilerProvider);
    final profilerState = ref.watch(profilerFamily(null));
    final report = _generateReport(profilerState);

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(context),
            const SizedBox(height: 16),
            _buildSummary(context, report),
            if (showDetails) ...[
              const SizedBox(height: 16),
              _buildDetailedMetrics(context, profilerState),
              const SizedBox(height: 16),
              _buildPerformanceCharts(context, profilerState),
            ],
            const SizedBox(height: 16),
            _buildActions(context, ref, profilerFamily),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          '性能报告',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        Text(
          DateFormat('yyyy-MM-dd HH:mm').format(DateTime.now()),
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  Widget _buildSummary(BuildContext context, Map<String, dynamic> report) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '性能摘要',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                context,
                '平均帧率',
                '${report['averageFPS']?.toStringAsFixed(1) ?? "0"} FPS',
                _getPerformanceColor(report['averageFPS'] ?? 0, 60, 30),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildMetricCard(
                context,
                '渲染时间',
                '${report['averageRenderTime']?.toStringAsFixed(1) ?? "0"} ms',
                _getPerformanceColor(report['averageRenderTime'] ?? 0, 8, 16, invert: true),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                context,
                '内存使用',
                '${report['averageMemoryUsage']?.toStringAsFixed(1) ?? "0"} MB',
                _getPerformanceColor(report['averageMemoryUsage'] ?? 0, 200, 500, invert: true),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildMetricCard(
                context,
                '图谱规模',
                '${report['lastNodeCount'] ?? 0}节点/${report['lastEdgeCount'] ?? 0}边',
                Colors.blue,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricCard(
    BuildContext context,
    String title,
    String value,
    Color valueColor,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: valueColor,
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailedMetrics(BuildContext context, VisualizationProfilerState state) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '详细指标',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        _buildMetricsSection(
          context,
          '渲染指标',
          {
            '当前帧率': '${state.renderMetrics.frameRate.toStringAsFixed(1)} FPS',
            '渲染时间': '${state.renderMetrics.renderTime.toStringAsFixed(1)} ms',
            '绘制调用': state.renderMetrics.drawCalls.toString(),
            '三角形数': state.renderMetrics.triangles.toString(),
            '顶点数': state.renderMetrics.vertices.toString(),
          },
        ),
        const SizedBox(height: 8),
        _buildMetricsSection(
          context,
          '系统指标',
          {
            '内存使用': '${state.systemMetrics.memoryUsage.toStringAsFixed(1)} MB',
            'CPU使用率': '${state.systemMetrics.cpuUsage.toStringAsFixed(1)}%',
            'GPU使用率': '${state.systemMetrics.gpuUsage.toStringAsFixed(1)}%',
          },
        ),
        const SizedBox(height: 8),
        _buildMetricsSection(
          context,
          '交互指标',
          {
            '选择延迟': '${state.interactionMetrics.selectLatency.toStringAsFixed(1)} ms',
            '拖拽延迟': '${state.interactionMetrics.dragLatency.toStringAsFixed(1)} ms',
            '缩放延迟': '${state.interactionMetrics.zoomLatency.toStringAsFixed(1)} ms',
            '旋转延迟': '${state.interactionMetrics.rotateLatency.toStringAsFixed(1)} ms',
          },
        ),
      ],
    );
  }

  Widget _buildMetricsSection(
    BuildContext context,
    String title,
    Map<String, String> metrics,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.titleSmall,
            ),
            const SizedBox(height: 8),
            ...metrics.entries.map(
              (entry) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(entry.key),
                    Text(
                      entry.value,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceCharts(BuildContext context, VisualizationProfilerState state) {
    if (state.history.isEmpty) {
      return const SizedBox();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '性能趋势',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 200,
          child: LineChart(
            LineChartData(
              gridData: FlGridData(show: true),
              titlesData: FlTitlesData(
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 40,
                  ),
                ),
                rightTitles: AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                topTitles: AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
              ),
              borderData: FlBorderData(show: true),
              lineBarsData: [
                _createFPSLineData(state.history),
                _createMemoryLineData(state.history),
              ],
            ),
          ),
        ),
      ],
    );
  }

  LineChartBarData _createFPSLineData(List<VisualizationProfilerState> history) {
    return LineChartBarData(
      spots: history
          .asMap()
          .entries
          .map((e) => FlSpot(e.key.toDouble(), e.value.renderMetrics.frameRate))
          .toList(),
      isCurved: true,
      color: Colors.green,
      barWidth: 2,
      isStrokeCapRound: true,
      dotData: FlDotData(show: false),
      belowBarData: BarAreaData(show: false),
    );
  }

  LineChartBarData _createMemoryLineData(List<VisualizationProfilerState> history) {
    // 内存使用量可能差距较大，这里除以10进行缩放以便在同一个图表显示
    return LineChartBarData(
      spots: history
          .asMap()
          .entries
          .map((e) => FlSpot(e.key.toDouble(), e.value.systemMetrics.memoryUsage / 10))
          .toList(),
      isCurved: true,
      color: Colors.red,
      barWidth: 2,
      isStrokeCapRound: true,
      dotData: FlDotData(show: false),
      belowBarData: BarAreaData(show: false),
    );
  }

  Widget _buildActions(
    BuildContext context,
    WidgetRef ref,
    StateNotifierProvider<VisualizationProfiler, VisualizationProfilerState> provider,
  ) {
    final state = ref.watch(provider(null));
    
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        OutlinedButton.icon(
          icon: Icon(state.isRunning ? Icons.pause : Icons.play_arrow),
          label: Text(state.isRunning ? '暂停分析' : '开始分析'),
          onPressed: () {
            if (state.isRunning) {
              ref.read(provider(null).notifier).stopProfiling();
            } else {
              ref.read(provider(null).notifier).startProfiling();
            }
          },
        ),
        ElevatedButton.icon(
          icon: const Icon(Icons.save_alt),
          label: const Text('导出报告'),
          onPressed: () {
            _exportReport(ref.read(provider(null).notifier).generatePerformanceReport());
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('性能报告已导出')),
            );
          },
        ),
      ],
    );
  }

  Map<String, dynamic> _generateReport(VisualizationProfilerState state) {
    if (state.history.isEmpty) {
      return {
        'averageFPS': state.renderMetrics.frameRate,
        'averageRenderTime': state.renderMetrics.renderTime,
        'averageMemoryUsage': state.systemMetrics.memoryUsage,
        'lastNodeCount': state.sceneMetrics.nodeCount,
        'lastEdgeCount': state.sceneMetrics.edgeCount,
      };
    }

    final List<double> frameRates = [];
    final List<double> renderTimes = [];
    final List<double> memoryUsages = [];

    for (final sample in state.history) {
      frameRates.add(sample.renderMetrics.frameRate);
      renderTimes.add(sample.renderMetrics.renderTime);
      memoryUsages.add(sample.systemMetrics.memoryUsage);
    }

    return {
      'averageFPS': _calculateAverage(frameRates),
      'minFPS': frameRates.isEmpty ? 0 : frameRates.reduce((a, b) => a < b ? a : b),
      'maxFPS': frameRates.isEmpty ? 0 : frameRates.reduce((a, b) => a > b ? a : b),
      'averageRenderTime': _calculateAverage(renderTimes),
      'averageMemoryUsage': _calculateAverage(memoryUsages),
      'lastNodeCount': state.sceneMetrics.nodeCount,
      'lastEdgeCount': state.sceneMetrics.edgeCount,
    };
  }

  double _calculateAverage(List<double> values) {
    if (values.isEmpty) return 0;
    return values.reduce((a, b) => a + b) / values.length;
  }

  Color _getPerformanceColor(double value, double good, double bad, {bool invert = false}) {
    if (invert) {
      if (value <= good) return Colors.green;
      if (value >= bad) return Colors.red;
      return Colors.orange;
    } else {
      if (value >= good) return Colors.green;
      if (value <= bad) return Colors.red;
      return Colors.orange;
    }
  }

  void _exportReport(Map<String, dynamic> report) {
    // 实际导出逻辑可以实现为保存到文件或分享
    print('导出性能报告: $report');
  }
}