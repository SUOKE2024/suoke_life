import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:suoke_life_app_app/features/health/models/health_data_model.dart';

class HealthDataChart extends StatelessWidget {
  final HealthProfile healthProfile;

  const HealthDataChart({super.key, required this.healthProfile});

  @override
  Widget build(BuildContext context) {
    return LineChart(
      LineChartData(
        gridData: FlGridData(show: false),
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              interval: 1,
              getTitlesWidget: (value, meta) {
                return Text('Day ${value.toInt()}');
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              interval: 50,
              getTitlesWidget: (value, meta) {
                return Text(value.toInt().toString());
              },
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: healthProfile.heartRateData
                .asMap()
                .entries
                .map((e) => FlSpot(e.key.toDouble(), e.value.toDouble()))
                .toList(),
            isCurved: true,
            color: Colors.red,
            barWidth: 4,
            belowBarData: BarAreaData(show: false),
          ),
          LineChartBarData(
            spots: healthProfile.sleepData
                .asMap()
                .entries
                .map((e) => FlSpot(e.key.toDouble(), e.value.toDouble()))
                .toList(),
            isCurved: true,
            color: Colors.blue,
            barWidth: 4,
            belowBarData: BarAreaData(show: false),
          ),
        ],
      ),
    );
  }
}
