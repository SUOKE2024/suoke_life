import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/profile/profile_controller.dart';

class ProfilePage extends GetView<ProfileController> {
  const ProfilePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Get.toNamed('/profile/settings'),
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        return ListView(
          children: [
            // 用户信息卡片
            Card(
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 30,
                      backgroundImage: controller.user.value.avatarUrl != null
                          ? NetworkImage(controller.user.value.avatarUrl!)
                          : null,
                      child: controller.user.value.avatarUrl == null
                          ? const Icon(Icons.person)
                          : null,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            controller.user.value.name,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            controller.user.value.email ?? '未设置邮箱',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            // 功能列表
            ListTile(
              leading: const Icon(Icons.person_outline),
              title: const Text('个人资料'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: controller.editProfile,
            ),
            ListTile(
              leading: const Icon(Icons.history),
              title: const Text('历史记录'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: controller.showHistory,
            ),
            ListTile(
              leading: const Icon(Icons.favorite_outline),
              title: const Text('我的收藏'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: controller.showFavorites,
            ),
            ListTile(
              leading: const Icon(Icons.help_outline),
              title: const Text('帮助与反馈'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: controller.showHelp,
            ),
            ListTile(
              leading: const Icon(Icons.info_outline),
              title: const Text('关于'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: controller.showAbout,
            ),
          ],
        );
      }),
    );
  }
} 