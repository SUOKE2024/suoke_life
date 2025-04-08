import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../di/providers/user_providers.dart';
import '../../../domain/entities/user.dart';
import '../../controllers/user_profile_controller.dart';

/// 用户资料页面
class ProfileScreen extends ConsumerWidget {
  /// 用户ID
  final String userId;

  /// 构造函数
  const ProfileScreen({
    Key? key,
    required this.userId,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 监听用户资料
    final userProfileAsync = ref.watch(userProfileProvider(userId));
    final profileController = ref.watch(userProfileControllerProvider.notifier);
    final profileState = ref.watch(userProfileControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('个人资料'),
        backgroundColor: AppColors.primaryColor,
      ),
      body: userProfileAsync.when(
        data: (user) => _buildProfileContent(context, user, profileController, profileState),
        loading: () => const Center(
          child: CircularProgressIndicator(
            color: AppColors.primaryColor,
          ),
        ),
        error: (error, _) => Center(
          child: Text(
            '加载失败: $error',
            style: const TextStyle(color: Colors.red),
          ),
        ),
      ),
    );
  }

  /// 构建资料内容
  Widget _buildProfileContent(
    BuildContext context,
    User user,
    UserProfileController controller,
    UserProfileState state,
  ) {
    // 表单控制器
    final nameController = TextEditingController(text: user.name);
    final emailController = TextEditingController(text: user.email);
    final phoneController = TextEditingController(text: user.phone);

    // 表单key
    final formKey = GlobalKey<FormState>();

    return Stack(
      children: [
        // 主要内容
        SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Form(
            key: formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 头像区域
                Center(
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundImage: user.avatar != null
                            ? NetworkImage(user.avatar!)
                            : null,
                        backgroundColor: AppColors.primaryColor.withAlpha(50),
                        child: user.avatar == null
                            ? Text(
                                user.name?.isNotEmpty == true
                                    ? user.name![0].toUpperCase()
                                    : user.username[0].toUpperCase(),
                                style: const TextStyle(
                                  fontSize: 40,
                                  color: AppColors.primaryColor,
                                ),
                              )
                            : null,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        user.username,
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'ID: ${user.id}',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                // 个人信息
                const Text(
                  '个人信息',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                // 姓名
                TextFormField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: '姓名',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                  validator: (value) {
                    if (value != null && value.length > 20) {
                      return '姓名不能超过20个字符';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                // 邮箱
                TextFormField(
                  controller: emailController,
                  decoration: const InputDecoration(
                    labelText: '电子邮箱',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.email_outlined),
                  ),
                  keyboardType: TextInputType.emailAddress,
                  validator: (value) {
                    if (value != null && value.isNotEmpty) {
                      final emailRegex = RegExp(
                        r'^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-zA-Z]+',
                      );
                      if (!emailRegex.hasMatch(value)) {
                        return '请输入有效的电子邮箱';
                      }
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                // 手机
                TextFormField(
                  controller: phoneController,
                  decoration: const InputDecoration(
                    labelText: '手机号码',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.phone_outlined),
                  ),
                  keyboardType: TextInputType.phone,
                  validator: (value) {
                    if (value != null && value.isNotEmpty) {
                      final phoneRegex = RegExp(r'^1[3-9]\d{9}$');
                      if (!phoneRegex.hasMatch(value)) {
                        return '请输入有效的手机号码';
                      }
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 32),
                // 保存按钮
                Center(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primaryColor,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 32,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    onPressed: () {
                      if (formKey.currentState!.validate()) {
                        // 保存资料
                        controller.updateProfile(
                          userId,
                          {
                            'name': nameController.text,
                            'email': emailController.text,
                            'phone': phoneController.text,
                          },
                        );
                      }
                    },
                    child: const Text(
                      '保存资料',
                      style: TextStyle(fontSize: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        // 加载指示器
        if (state.isLoading)
          Container(
            color: Colors.black26,
            child: const Center(
              child: CircularProgressIndicator(
                color: AppColors.primaryColor,
              ),
            ),
          ),
        // 错误信息
        if (state.errorMessage != null)
          Positioned(
            bottom: 20,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
                decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  state.errorMessage!,
                  style: const TextStyle(color: Colors.white),
                ),
              ),
            ),
          ),
      ],
    );
  }
} 