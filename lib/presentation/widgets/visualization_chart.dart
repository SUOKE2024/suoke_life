import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../services/realtime_visualization_service.dart';

class VisualizationChart extends StatelessWidget {
  final VisualizationData data;
  final LineChartData chartData;

  const VisualizationChart({
    Key? key,
    required this.data,
    required this.chartData,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 图表标题和时间戳
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  data.title,
                  style: Theme.of(context).textTheme.subtitle1?.copyWith(
                    color: data.color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  _formatTimestamp(data.timestamp),
                  style: Theme.of(context).textTheme.caption,
                ),
              ],
            ),
            const SizedBox(height: 8),
            // 图表
            Expanded(
              child: LineChart(
                chartData,
                swapAnimationDuration: const Duration(milliseconds: 250),
              ),
            ),
            if (data.unit != null) ...[
              const SizedBox(height: 8),
              // 单位显示
              Text(
                '单位: ${data.unit}',
                style: Theme.of(context).textTheme.caption,
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    return '${timestamp.hour.toString().padLeft(2, '0')}:' 
           '${timestamp.minute.toString().padLeft(2, '0')}:' 
           '${timestamp.second.toString().padLeft(2, '0')}';
  }
} 