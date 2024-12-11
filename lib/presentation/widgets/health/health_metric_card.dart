import 'package:flutter/material.dart';

class HealthMetricCard extends StatelessWidget {
  final String title;
  final Map<String, dynamic> metrics;
  final bool isRisk;

  const HealthMetricCard({
    Key? key,
    required this.title,
    required this.metrics,
    this.isRisk = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isRisk ? Icons.warning_amber : Icons.favorite,
                  color: isRisk ? Colors.orange : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...metrics.entries.map((entry) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    entry.key,
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  _buildMetricValue(context, entry.value),
                ],
              ),
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricValue(BuildContext context, dynamic value) {
    if (value is num) {
      return Text(
        value.toStringAsFixed(1),
        style: TextStyle(
          color: _getValueColor(value),
          fontWeight: FontWeight.bold,
        ),
      );
    } else if (value is String) {
      return Text(
        value,
        style: const TextStyle(fontWeight: FontWeight.bold),
      );
    } else if (value is Map) {
      return Text(
        value['value'].toString(),
        style: TextStyle(
          color: _getValueColor(value['status']),
          fontWeight: FontWeight.bold,
        ),
      );
    }
    return Text(value.toString());
  }

  Color _getValueColor(dynamic value) {
    if (value is String) {
      switch (value.toLowerCase()) {
        case 'normal':
          return Colors.green;
        case 'warning':
          return Colors.orange;
        case 'danger':
          return Colors.red;
        default:
          return Colors.black;
      }
    } else if (value is num) {
      if (value < 0.3) return Colors.red;
      if (value < 0.7) return Colors.orange;
      return Colors.green;
    }
    return Colors.black;
  }
} 