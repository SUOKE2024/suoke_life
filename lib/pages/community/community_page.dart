import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';

class CommunityPage extends StatelessWidget {
  const CommunityPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('社区'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => Get.toNamed(RoutePaths.moment),
            tooltip: '发布动态',
          ),
          IconButton(
            icon: const Icon(Icons.tag),
            onPressed: () => Get.toNamed(RoutePaths.topic),
            tooltip: '话题',
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              leading: const CircleAvatar(
                child: Icon(Icons.person),
              ),
              title: const Text('欢迎来到社区'),
              subtitle: const Text('这里是社区内容展示区域'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () => Get.toNamed(RoutePaths.moment),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              leading: const CircleAvatar(
                child: Icon(Icons.topic),
              ),
              title: const Text('热门话题'),
              subtitle: const Text('发现感兴趣的话题'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () => Get.toNamed(RoutePaths.topic),
            ),
          ),
        ],
      ),
    );
  }
} 