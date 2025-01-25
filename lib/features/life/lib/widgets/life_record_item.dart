import 'package:flutter/material.dart';

class LifeRecordItem extends StatelessWidget {
  final String title;
  final String time;
  final String description;

  const LifeRecordItem({
    Key? key,
    required this.title,
    required this.time,
    required this.description,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.access_time, size: 16),
                const SizedBox(width: 4),
                Text(time),
              ],
            ),
            const SizedBox(height: 8),
            Text(description),
          ],
        ),
      ),
    );
  }
} 