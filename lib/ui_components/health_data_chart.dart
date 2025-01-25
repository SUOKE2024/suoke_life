import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;

class HealthDataChart extends StatelessWidget {
  final List<charts.Series<dynamic, DateTime>> seriesList;
  final bool animate;

  const HealthDataChart({
    Key? key,
    required this.seriesList,
    this.animate = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return charts.TimeSeriesChart(
      seriesList,
      animate: animate,
      dateTimeFactory: const charts.LocalDateTimeFactory(),
    );
  }
} 