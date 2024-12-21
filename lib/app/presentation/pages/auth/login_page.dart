import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/auth/login_controller.dart';

class LoginPage extends BasePage<LoginController> {
  const LoginPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('登录'),
      automaticallyImplyLeading: false,
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Logo
          const Icon(
            Icons.account_circle,
            size: 80,
            color: Colors.blue,
          ),
          const SizedBox(height: 32),

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
          const SizedBox(height: 32),

          // 登录按钮
          SizedBox(
            width: double.infinity,
            child: Obx(() => ElevatedButton(
              onPressed: controller.isLoading.value
                ? null
                : controller.login,
              child: controller.isLoading.value
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                    ),
                  )
                : const Text('登录'),
            )),
          ),
          const SizedBox(height: 16),

          // 注册链接
          TextButton(
            onPressed: () => Get.toNamed('/register'),
            child: const Text('还没有账号？立即注册'),
          ),
        ],
      ),
    );
  }
} 