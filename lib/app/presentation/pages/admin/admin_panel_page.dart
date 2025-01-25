import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class AdminPanelPage extends StatelessWidget {
  const AdminPanelPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('管理面板'),
      ),
      body: const Center(
        child: Text('管理面板页面'),
      ),
    );
  }
} 