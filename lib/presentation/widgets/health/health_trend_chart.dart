import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class HealthTrendChart extends StatelessWidget {
  final String title;
  final Map<String, dynamic> data;

  const HealthTrendChart({
    Key? key,
    required this.title,
    required this.data,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(show: true),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 30,
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
                  lineBarsData: _createLineBarsData(),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 16,
              runSpacing: 8,
              children: _buildLegends(context),
            ),
          ],
        ),
      ),
    );
  }

  List<LineChartBarData> _createLineBarsData() {
    final List<LineChartBarData> lineBars = [];
    int index = 0;
    
    data.forEach((key, values) {
      if (values is List) {
        final spots = List<FlSpot>.generate(
          values.length,
          (i) => FlSpot(i.toDouble(), values[i].toDouble()),
        );

        lineBars.add(
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: _getLineColor(index),
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: FlDotData(show: false),
            belowBarData: BarAreaData(show: false),
          ),
        );
        index++;
      }
    });

    return lineBars;
  }

  List<Widget> _buildLegends(BuildContext context) {
    final List<Widget> legends = [];
    int index = 0;

    data.forEach((key, _) {
      legends.add(
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 16,
              height: 3,
              color: _getLineColor(index),
            ),
            const SizedBox(width: 4),
            Text(
              key,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      );
      index++;
    });

    return legends;
  }

  Color _getLineColor(int index) {
    final colors = [
      Colors.blue,
      Colors.red,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.teal,
    ];
    return colors[index % colors.length];
  }
} 