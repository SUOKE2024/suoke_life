import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class DeviceManagementPage extends StatelessWidget {
  const DeviceManagementPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('设备管理')),
      body: const Center(child: Text('设备管理页面')),
    );
  }
} 