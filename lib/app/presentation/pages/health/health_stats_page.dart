import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class HealthStatsPage extends StatelessWidget {
  const HealthStatsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('健康统计')),
      body: const Center(child: Text('健康统计页面')),
    );
  }
} 