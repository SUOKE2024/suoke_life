import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../services/auth_service.dart';
import '../../../core/base/base_controller.dart';
import '../../../core/utils/validators.dart';

class ResetPasswordController extends BaseController {
  final _authService = Get.find<AuthService>();
  
  final emailController = TextEditingController();
  final cooldown = 0.obs;
  Timer? _timer;

  @override
  void onClose() {
    emailController.dispose();
    _timer?.cancel();
    super.onClose();
  }

  Future<void> sendResetLink() async {
    // 验证邮箱
    final emailError = Validators.email(emailController.text);
    if (emailError != null) {
      showError(emailError);
      return;
    }

    try {
      showLoading();
      await _authService.sendPasswordResetEmail(
        email: emailController.text,
      );
      hideLoading();
      
      // 开始倒计时
      cooldown.value = 60;
      _startCooldown();
      
      Get.snackbar(
        '提示',
        '重置链接已发送到您的邮箱，请注意查收',
        duration: const Duration(seconds: 5),
      );
    } catch (e) {
      hideLoading();
      showError(e.toString());
    }
  }

  void _startCooldown() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (cooldown.value > 0) {
        cooldown.value--;
      } else {
        timer.cancel();
      }
    });
  }
} 