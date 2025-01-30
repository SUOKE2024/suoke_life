import 'package:flutter/material.dart';

class QuickActionGrid extends StatelessWidget {
  const QuickActionGrid({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GridView.count(
        crossAxisCount: 2,
        children: List.generate(4, (index) {
          return Card(
            child: Center(
              child: Text('Action \\${index + 1}'),
            ),
          );
        }),
      ),
    );
  }
} 