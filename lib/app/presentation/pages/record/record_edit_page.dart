import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class RecordEditPage extends StatelessWidget {
  final String? id;

  const RecordEditPage({
    super.key,
    @PathParam('id') this.id,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(id == null ? '新建记录' : '编辑记录'),
      ),
      body: Center(
        child: Text(id == null ? '新建记录页面' : '编辑记录页面 ID: $id'),
      ),
    );
  }
} 