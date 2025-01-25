import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/profile/profile_edit_controller.dart';
import '../../widgets/avatar_picker.dart';

class ProfileEditPage extends StatelessWidget {
  const ProfileEditPage({Key? key}) : super(key: key);

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
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // 头像选择
            Center(
              child: AvatarPicker(
                imageUrl: controller.avatar.value,
                onChanged: controller.updateAvatar,
                size: 100,
              ),
            ),
            const SizedBox(height: 32),

            // 基本信息表单
            Form(
              key: controller.formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: controller.nameController,
                    decoration: const InputDecoration(
                      labelText: '昵称',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入昵称';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: controller.bioController,
                    decoration: const InputDecoration(
                      labelText: '个性签名',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 3,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: controller.phoneController,
                    decoration: const InputDecoration(
                      labelText: '手机号码',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.phone,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: controller.emailController,
                    decoration: const InputDecoration(
                      labelText: '邮箱',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.emailAddress,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
} 