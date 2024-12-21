import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../services/auth_service.dart';
import '../../../core/base/base_controller.dart';

class RegisterController extends BaseController {
  final _authService = Get.find<AuthService>();
  
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmPasswordController = TextEditingController();
  
  final showPassword = false.obs;
  final showConfirmPassword = false.obs;

  @override
  void onClose() {
    usernameController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    super.onClose();
  }

  void togglePasswordVisibility() {
    showPassword.value = !showPassword.value;
  }

  void toggleConfirmPasswordVisibility() {
    showConfirmPassword.value = !showConfirmPassword.value;
  }

  Future<void> register() async {
    if (usernameController.text.isEmpty) {
      showError('请输入用户名');
      return;
    }
    if (passwordController.text.isEmpty) {
      showError('请输入密码');
      return;
    }
    if (confirmPasswordController.text.isEmpty) {
      showError('请确认密码');
      return;
    }
    if (passwordController.text != confirmPasswordController.text) {
      showError('两次输入的密码不一致');
      return;
    }

    try {
      showLoading();
      await _authService.register(
        username: usernameController.text,
        password: passwordController.text,
      );
      hideLoading();
      Get.back(); // 返回登录页
      Get.snackbar('提示', '注册成功，请登录');
    } catch (e) {
      hideLoading();
      showError(e.toString());
    }
  }
} 