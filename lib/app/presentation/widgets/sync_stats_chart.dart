import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class SyncStatsChart extends StatelessWidget {
  final List<SyncStats> stats;
  
  const SyncStatsChart({
    Key? key,
    required this.stats,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(16),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            rightTitles: AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            topTitles: AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  if (value.toInt() >= stats.length) return const Text('');
                  return Text(
                    stats[value.toInt()].date.day.toString(),
                    style: const TextStyle(fontSize: 12),
                  );
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: stats.asMap().entries.map((entry) {
                return FlSpot(entry.key.toDouble(), entry.value.count.toDouble());
              }).toList(),
              isCurved: true,
              color: Theme.of(context).primaryColor,
              barWidth: 2,
              dotData: FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: Theme.of(context).primaryColor.withOpacity(0.2),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class SyncStats {
  final DateTime date;
  final int count;

  const SyncStats({
    required this.date,
    required this.count,
  });
} 