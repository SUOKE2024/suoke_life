import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.network_check),
            title: const Text('连接测试'),
            subtitle: const Text('检查服务器和数据库连接状态'),
            onTap: () => Get.toNamed(RoutePaths.connectionTest),
          ),
          // ... 其他设置项
        ],
      ),
    );
  }
} 