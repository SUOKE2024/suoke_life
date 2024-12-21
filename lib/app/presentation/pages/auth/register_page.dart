import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/auth/register_controller.dart';

class RegisterPage extends BasePage<RegisterController> {
  const RegisterPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('注册'),
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // 用户名输入框
          TextField(
            controller: controller.usernameController,
            decoration: const InputDecoration(
              labelText: '用户名',
              prefixIcon: Icon(Icons.person),
            ),
          ),
          const SizedBox(height: 16),

          // 密码输入框
          Obx(() => TextField(
            controller: controller.passwordController,
            obscureText: !controller.showPassword.value,
            decoration: InputDecoration(
              labelText: '密码',
              prefixIcon: const Icon(Icons.lock),
              suffixIcon: IconButton(
                icon: Icon(
                  controller.showPassword.value
                    ? Icons.visibility_off
                    : Icons.visibility,
                ),
                onPressed: controller.togglePasswordVisibility,
              ),
            ),
          )),
          const SizedBox(height: 16),

          // 确认密码输入框
          Obx(() => TextField(
            controller: controller.confirmPasswordController,
            obscureText: !controller.showConfirmPassword.value,
            decoration: InputDecoration(
              labelText: '确认密码',
              prefixIcon: const Icon(Icons.lock_outline),
              suffixIcon: IconButton(
                icon: Icon(
                  controller.showConfirmPassword.value
                    ? Icons.visibility_off
                    : Icons.visibility,
                ),
                onPressed: controller.toggleConfirmPasswordVisibility,
              ),
            ),
          )),
          const SizedBox(height: 32),

          // 注册按钮
          SizedBox(
            width: double.infinity,
            child: Obx(() => ElevatedButton(
              onPressed: controller.isLoading.value
                ? null
                : controller.register,
              child: controller.isLoading.value
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                    ),
                  )
                : const Text('注册'),
            )),
          ),
          const SizedBox(height: 16),

          // 登录链接
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('已有账号？返回登录'),
          ),
        ],
      ),
    );
  }
} 