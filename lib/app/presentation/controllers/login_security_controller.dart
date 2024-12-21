import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../services/auth_service.dart';
import '../../services/biometric_service.dart';
import '../../services/login_security_service.dart';
import '../../core/base/base_controller.dart';

class LoginSecurityController extends BaseController {
  final _authService = Get.find<AuthService>();
  final _biometricService = Get.find<BiometricService>();
  final _securityService = Get.find<LoginSecurityService>();

  final biometricEnabled = false.obs;
  final loginVerificationEnabled = false.obs;
  final loginNotificationEnabled = false.obs;
  final passwordChangeReminder = false.obs;

  final oldPasswordController = TextEditingController();
  final newPasswordController = TextEditingController();
  final confirmPasswordController = TextEditingController();

  @override
  void onInit() {
    super.onInit();
    _loadSettings();
  }

  @override
  void onClose() {
    oldPasswordController.dispose();
    newPasswordController.dispose();
    confirmPasswordController.dispose();
    super.onClose();
  }

  Future<void> _loadSettings() async {
    biometricEnabled.value = _biometricService.isEnabled.value;
    loginVerificationEnabled.value = await _storage.getBool('login_verification') ?? false;
    loginNotificationEnabled.value = await _storage.getBool('login_notification') ?? false;
    passwordChangeReminder.value = await _storage.getBool('password_change_reminder') ?? false;
  }

  Future<void> toggleBiometric(bool value) async {
    if (value) {
      await _biometricService.enable();
    } else {
      await _biometricService.disable();
    }
    biometricEnabled.value = _biometricService.isEnabled.value;
  }

  Future<void> toggleLoginVerification(bool value) async {
    await _storage.setBool('login_verification', value);
    loginVerificationEnabled.value = value;
  }

  Future<void> toggleLoginNotification(bool value) async {
    await _storage.setBool('login_notification', value);
    loginNotificationEnabled.value = value;
  }

  Future<void> togglePasswordChangeReminder(bool value) async {
    await _storage.setBool('password_change_reminder', value);
    passwordChangeReminder.value = value;
  }

  void showChangePasswordDialog() {
    oldPasswordController.clear();
    newPasswordController.clear();
    confirmPasswordController.clear();

    Get.dialog(
      AlertDialog(
        title: const Text('修改密码'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: oldPasswordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: '当前密码',
                hintText: '请输入当前密码',
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: newPasswordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: '新密码',
                hintText: '请输入新密码',
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: confirmPasswordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: '确认新密码',
                hintText: '请再次输入新密码',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: _changePassword,
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  Future<void> _changePassword() async {
    if (oldPasswordController.text.isEmpty) {
      showError('请输入当前密码');
      return;
    }
    if (newPasswordController.text.isEmpty) {
      showError('请输入新密码');
      return;
    }
    if (confirmPasswordController.text.isEmpty) {
      showError('请确认新密码');
      return;
    }
    if (newPasswordController.text != confirmPasswordController.text) {
      showError('两次输入的密码不一致');
      return;
    }

    if (!_securityService.isPasswordValid(newPasswordController.text)) {
      showError('密码不符合安全要求');
      return;
    }

    try {
      await _authService.changePassword(
        oldPassword: oldPasswordController.text,
        newPassword: newPasswordController.text,
      );
      Get.back();
      showSuccess('密码修改成功');
    } catch (e) {
      showError(e.toString());
    }
  }
} 