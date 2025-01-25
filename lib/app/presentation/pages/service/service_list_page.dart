import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class ServiceListPage extends StatelessWidget {
  final String categoryId;

  const ServiceListPage({
    super.key,
    @PathParam('categoryId') required this.categoryId,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('服务列表')),
      body: Center(child: Text('服务列表页面 分类ID: $categoryId')),
    );
  }
} 