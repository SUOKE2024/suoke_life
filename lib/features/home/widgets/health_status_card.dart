import 'package:flutter/material.dart';

class HealthStatusCard extends StatelessWidget {
  const HealthStatusCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: const [
            Text('Health Status', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('All systems operational'),
          ],
        ),
      ),
    );
  }
} 