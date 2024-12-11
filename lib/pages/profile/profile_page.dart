import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Get.toNamed(RoutePaths.settings),
            tooltip: '设置',
          ),
        ],
      ),
      body: ListView(
        children: [
          Card(
            margin: const EdgeInsets.all(16),
            child: ListTile(
              leading: const CircleAvatar(
                child: Icon(Icons.person),
              ),
              title: const Text('未登录'),
              subtitle: const Text('点击登录账号'),
              onTap: () => Get.toNamed(RoutePaths.profileEdit),
            ),
          ),
          Container(
            color: Colors.grey[200],
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: const Text(
              '我的功能',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.shopping_bag),
            title: const Text('我的订单'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Get.toNamed(RoutePaths.orders),
          ),
          ListTile(
            leading: const Icon(Icons.favorite),
            title: const Text('我的收藏'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Get.toNamed(RoutePaths.favorites),
          ),
          Container(
            color: Colors.grey[200],
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: const Text(
              '设置',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.security),
            title: const Text('账号安全'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Get.toNamed(RoutePaths.security),
          ),
          ListTile(
            leading: const Icon(Icons.privacy_tip),
            title: const Text('隐私设置'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Get.toNamed(RoutePaths.privacy),
          ),
        ],
      ),
    );
  }
} 