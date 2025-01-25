import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class TopicDetailPage extends StatelessWidget {
  final String id;

  const TopicDetailPage({
    super.key,
    @PathParam('id') required this.id,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('话题详情')),
      body: Center(child: Text('话题详情页面 ID: $id')),
    );
  }
} 