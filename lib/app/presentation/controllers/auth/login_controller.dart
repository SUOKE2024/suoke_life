import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../services/auth_service.dart';
import '../../../core/base/base_controller.dart';
import '../../../routes/app_routes.dart';

class LoginController extends BaseController {
  final _authService = Get.find<AuthService>();
  
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  final showPassword = false.obs;

  @override
  void onClose() {
    usernameController.dispose();
    passwordController.dispose();
    super.onClose();
  }

  void togglePasswordVisibility() {
    showPassword.value = !showPassword.value;
  }

  Future<void> login() async {
    if (usernameController.text.isEmpty) {
      showError('请输入用户名');
      return;
    }
    if (passwordController.text.isEmpty) {
      showError('请输入密码');
      return;
    }

    try {
      showLoading();
      await _authService.login(
        username: usernameController.text,
        password: passwordController.text,
      );
      hideLoading();
      Get.offAllNamed(Routes.MAIN);
    } catch (e) {
      hideLoading();
      showError(e.toString());
    }
  }
} 