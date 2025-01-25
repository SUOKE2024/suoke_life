import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class HealthAdviceDetailPage extends StatelessWidget {
  final String id;

  const HealthAdviceDetailPage({
    super.key,
    @PathParam('id') required this.id,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('健康建议详情')),
      body: Center(child: Text('健康建议详情页面 ID: $id')),
    );
  }
} 