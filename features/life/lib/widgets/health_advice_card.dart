import 'package:flutter/material.dart';

class HealthAdviceCard extends StatelessWidget {
  const HealthAdviceCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text(
              'Health Advice',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              'Drink plenty of water and get enough sleep. '
              'Eat a balanced diet and exercise regularly.',
            ),
          ],
        ),
      ),
    );
  }
} 