import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/auth/reset_password_controller.dart';

class ResetPasswordPage extends BasePage<ResetPasswordController> {
  const ResetPasswordPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('重置密码'),
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // 邮箱输入框
          TextField(
            controller: controller.emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(
              labelText: '邮箱',
              prefixIcon: Icon(Icons.email),
            ),
          ),
          const SizedBox(height: 32),

          // 发送重置链接按钮
          SizedBox(
            width: double.infinity,
            child: Obx(() => ElevatedButton(
              onPressed: controller.isLoading.value
                ? null
                : controller.sendResetLink,
              child: controller.isLoading.value
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                    ),
                  )
                : const Text('发送重置链接'),
            )),
          ),
          const SizedBox(height: 16),

          // 返回登录
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('返回登录'),
          ),
        ],
      ),
    );
  }
} 