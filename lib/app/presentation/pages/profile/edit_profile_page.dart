import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/profile/edit_profile_controller.dart';

class EditProfilePage extends StatelessWidget {
  const EditProfilePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('编辑资料'),
        actions: [
          TextButton(
            onPressed: controller.saveProfile,
            child: const Text('保存'),
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 头像
            Center(
              child: Stack(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundImage: controller.avatarUrl.value != null
                        ? NetworkImage(controller.avatarUrl.value!)
                        : null,
                    child: controller.avatarUrl.value == null
                        ? const Icon(Icons.person, size: 50)
                        : null,
                  ),
                  Positioned(
                    right: 0,
                    bottom: 0,
                    child: IconButton(
                      icon: const Icon(Icons.camera_alt),
                      onPressed: controller.changeAvatar,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            // 昵称
            TextField(
              controller: controller.nameController,
              decoration: const InputDecoration(
                labelText: '昵称',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            // 邮箱
            TextField(
              controller: controller.emailController,
              decoration: const InputDecoration(
                labelText: '邮箱',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 16),
            // 手机号
            TextField(
              controller: controller.phoneController,
              decoration: const InputDecoration(
                labelText: '手机号',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 16),
            // 简介
            TextField(
              controller: controller.bioController,
              decoration: const InputDecoration(
                labelText: '个人简介',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
          ],
        );
      }),
    );
  }
} 