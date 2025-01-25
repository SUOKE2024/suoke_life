import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class ServiceDetailPage extends StatelessWidget {
  final String id;

  const ServiceDetailPage({
    super.key,
    @PathParam('id') required this.id,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('服务详情')),
      body: Center(child: Text('服务详情页面 ID: $id')),
    );
  }
} 