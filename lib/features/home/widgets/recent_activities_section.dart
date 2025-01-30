import 'package:flutter/material.dart';

class RecentActivitiesSection extends StatelessWidget {
  const RecentActivitiesSection({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Padding(
          padding: EdgeInsets.all(16),
          child: Text('Recent Activities',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
        // TODO: Implement recent activities list
      ],
    );
  }
} 