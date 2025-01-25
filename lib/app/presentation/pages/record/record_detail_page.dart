import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class RecordDetailPage extends StatelessWidget {
  final String id;

  const RecordDetailPage({
    super.key,
    @PathParam('id') required this.id,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('记录详情')),
      body: Center(child: Text('记录详情页面 ID: $id')),
    );
  }
} 