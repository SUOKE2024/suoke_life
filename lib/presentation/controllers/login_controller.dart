import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/auth/services/auth_service.dart';
import '../../core/auth/services/third_party_auth_service.dart';
import '../../core/auth/services/biometric_auth_service.dart';
import '../../core/auth/services/voice_auth_service.dart';
import '../../core/routes/route_paths.dart';

class LoginController extends GetxController {
  final phoneController = TextEditingController();
  final codeController = TextEditingController();
  
  final _isLoading = false.obs;
  final _canGetCode = true.obs;
  final _countdown = 60.obs;
  final _supportsBiometric = false.obs;
  final _supportsVoice = false.obs;
  final _rememberLogin = false.obs;
  
  bool get isLoading => _isLoading.value;
  bool get canGetCode => _canGetCode.value;
  int get countdown => _countdown.value;
  bool get supportsBiometric => _supportsBiometric.value;
  bool get supportsVoice => _supportsVoice.value;
  bool get rememberLogin => _rememberLogin.value;
  
  final _authService = Get.find<AuthService>();
  final _thirdPartyAuthService = Get.find<ThirdPartyAuthService>();
  final _biometricAuthService = Get.find<BiometricAuthService>();
  final _voiceAuthService = Get.find<VoiceAuthService>();
  
  // 验证码倒计时定时器
  Worker? _countdownWorker;
  
  @override
  void onInit() {
    super.onInit();
    _checkBiometricSupport();
    _checkVoiceSupport();
    _initAutoLogin();
  }
  
  // 初始化自动登录状态
  Future<void> _initAutoLogin() async {
    _rememberLogin.value = _authService.isAutoLoginEnabled;
  }
  
  // 切换记住登录状态
  Future<void> toggleRememberLogin(bool value) async {
    _rememberLogin.value = value;
    if (value) {
      await _authService.enableAutoLogin();
    } else {
      await _authService.disableAutoLogin();
    }
  }
  
  @override
  void onClose() {
    phoneController.dispose();
    codeController.dispose();
    _countdownWorker?.dispose();
    super.onClose();
  }
  
  // 检查生物识别支持
  Future<void> _checkBiometricSupport() async {
    final isSupported = await _biometricAuthService.checkBiometricSupport();
    final isEnabled = _biometricAuthService.isBiometricEnabled;
    _supportsBiometric.value = isSupported && isEnabled;
    
    // 如果支持且启用了生物识别，自动尝试生物识别登录
    if (_supportsBiometric.value) {
      _tryBiometricLogin();
    }
  }
  
  // 检查声纹支持
  Future<void> _checkVoiceSupport() async {
    final hasPermission = await _voiceAuthService.checkMicrophonePermission();
    final isEnabled = _voiceAuthService.isVoiceEnabled;
    _supportsVoice.value = hasPermission && isEnabled;
  }
  
  // 尝试生物识别登录
  Future<void> _tryBiometricLogin() async {
    try {
      _isLoading.value = true;
      final success = await _biometricAuthService.authenticateWithBiometric();
      
      if (success) {
        _handleLoginSuccess();
      }
    } finally {
      _isLoading.value = false;
    }
  }
  
  // 开始声纹录制
  Future<void> startVoiceRecording() async {
    await _voiceAuthService.startRecording();
  }
  
  // 停止声纹录制并验证
  Future<void> stopVoiceRecordingAndVerify() async {
    try {
      _isLoading.value = true;
      final success = await _voiceAuthService.verifyVoicePrint();
      
      if (success) {
        _handleLoginSuccess();
      } else {
        Get.snackbar('提示', '声纹验证失败，请重试');
      }
    } finally {
      _isLoading.value = false;
    }
  }
  
  // 发送验证码
  Future<void> sendVerificationCode() async {
    if (!canGetCode) return;
    
    final phone = phoneController.text.trim();
    if (phone.isEmpty) {
      Get.snackbar('提示', '请输入手机号');
      return;
    }
    
    if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(phone)) {
      Get.snackbar('提示', '请输入正确的手机号');
      return;
    }
    
    try {
      _isLoading.value = true;
      final success = await _authService.sendVerificationCode(phone);
      
      if (success) {
        Get.snackbar('提示', '验证码已发送');
        startCountdown();
      } else {
        Get.snackbar('错误', '验证码发送失败，请重试');
      }
    } catch (e) {
      Get.snackbar('错误', '发送验证码时出错：${e.toString()}');
    } finally {
      _isLoading.value = false;
    }
  }
  
  // 开始倒计时
  void startCountdown() {
    _canGetCode.value = false;
    _countdown.value = 60;
    
    _countdownWorker = ever(_countdown, (count) {
      if (count <= 0) {
        _canGetCode.value = true;
        _countdownWorker?.dispose();
      }
    });
    
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 1));
      if (_countdown.value > 0) {
        _countdown.value--;
        return true;
      }
      return false;
    });
  }
  
  // 手机号登录
  Future<void> login() async {
    final phone = phoneController.text.trim();
    final code = codeController.text.trim();
    
    if (phone.isEmpty || code.isEmpty) {
      Get.snackbar('提示', '请输入手机号和验证码');
      return;
    }
    
    if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(phone)) {
      Get.snackbar('提示', '请输入正确的手机号');
      return;
    }
    
    if (code.length != 6) {
      Get.snackbar('提示', '请输入6位验证码');
      return;
    }
    
    try {
      _isLoading.value = true;
      final success = await _authService.login(
        phone: phone,
        code: code,
      );
      
      if (success) {
        // 如果设备支持生物识别但未启用，询问是否启用
        final canUseBiometric = await _biometricAuthService.checkBiometricSupport();
        if (canUseBiometric && !_biometricAuthService.isBiometricEnabled) {
          final shouldEnable = await Get.dialog<bool>(
            AlertDialog(
              title: const Text('启用生物识别'),
              content: const Text('是否启用生物识别快速登录？'),
              actions: [
                TextButton(
                  onPressed: () => Get.back(result: false),
                  child: const Text('暂不启用'),
                ),
                TextButton(
                  onPressed: () => Get.back(result: true),
                  child: const Text('启用'),
                ),
              ],
            ),
          );
          
          if (shouldEnable == true) {
            await _biometricAuthService.enableBiometric();
          }
        }
        
        // 如果有麦克风权限但未启用声纹，询问是否启用
        final hasMicPermission = await _voiceAuthService.checkMicrophonePermission();
        if (hasMicPermission && !_voiceAuthService.isVoiceEnabled) {
          final shouldEnable = await Get.dialog<bool>(
            AlertDialog(
              title: const Text('启用声纹识别'),
              content: const Text('是否启用声纹快速登录？'),
              actions: [
                TextButton(
                  onPressed: () => Get.back(result: false),
                  child: const Text('暂不启用'),
                ),
                TextButton(
                  onPressed: () => Get.back(result: true),
                  child: const Text('启用'),
                ),
              ],
            ),
          );
          
          if (shouldEnable == true) {
            Get.dialog(
              AlertDialog(
                title: const Text('录制声纹'),
                content: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('请朗读以下文字：\n"智能生活，科技未来"'),
                    const SizedBox(height: 16),
                    Obx(() => Text('录音中：${_voiceAuthService.recordDuration}秒')),
                  ],
                ),
                actions: [
                  TextButton(
                    onPressed: () {
                      _voiceAuthService.stopRecording();
                      Get.back();
                    },
                    child: const Text('取消'),
                  ),
                  TextButton(
                    onPressed: () async {
                      final success = await _voiceAuthService.enrollVoicePrint();
                      Get.back();
                      if (success) {
                        Get.snackbar('提示', '声纹注册成功');
                      } else {
                        Get.snackbar('错误', '声纹注册失败，请重试');
                      }
                    },
                    child: const Text('完成'),
                  ),
                ],
              ),
            );
            await _voiceAuthService.startRecording();
          }
        }
        
        _handleLoginSuccess();
      } else {
        Get.snackbar('错误', '登录失败，请检查验证码是否正确');
      }
    } catch (e) {
      Get.snackbar('错误', '登录时出错：${e.toString()}');
    } finally {
      _isLoading.value = false;
    }
  }

  // 微信登录
  Future<void> loginWithWeChat() async {
    try {
      _isLoading.value = true;
      final success = await _thirdPartyAuthService.loginWithWeChat();
      if (success) {
        _handleLoginSuccess();
      } else {
        Get.snackbar('错误', '微信登录失败，请重试');
      }
    } catch (e) {
      Get.snackbar('错误', '微信登录时出错：${e.toString()}');
    } finally {
      _isLoading.value = false;
    }
  }

  // 支付宝登录
  Future<void> loginWithAlipay() async {
    try {
      _isLoading.value = true;
      final success = await _thirdPartyAuthService.loginWithAlipay();
      if (success) {
        _handleLoginSuccess();
      } else {
        Get.snackbar('错误', '支付宝登录失败，请重试');
      }
    } catch (e) {
      Get.snackbar('错误', '支付宝登录时出错：${e.toString()}');
    } finally {
      _isLoading.value = false;
    }
  }
  
  // 生物识别登录
  Future<void> loginWithBiometric() async {
    if (!_supportsBiometric.value) return;
    await _tryBiometricLogin();
  }
  
  // 声纹登录
  Future<void> loginWithVoice() async {
    if (!_supportsVoice.value) return;
    
    Get.dialog(
      AlertDialog(
        title: const Text('声纹验证'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('请朗读以下文字：\n"智能生活，科技未来"'),
            const SizedBox(height: 16),
            Obx(() => Text('录音中：${_voiceAuthService.recordDuration}秒')),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              _voiceAuthService.stopRecording();
              Get.back();
            },
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              await stopVoiceRecordingAndVerify();
              Get.back();
            },
            child: const Text('完成'),
          ),
        ],
      ),
    );
    
    await startVoiceRecording();
  }

  // 处理登录成功
  void _handleLoginSuccess() {
    final redirectRoute = Get.parameters['redirect'];
    if (redirectRoute != null && redirectRoute.isNotEmpty) {
      Get.offAllNamed(redirectRoute);
    } else {
      Get.offAllNamed(RoutePaths.main);
    }
  }
  
  // 跳转到隐私政策
  void toPrivacyPolicy() {
    Get.toNamed(RoutePaths.privacy);
  }
  
  // 跳转到服务条款
  void toTermsOfService() {
    Get.toNamed(RoutePaths.terms);
  }
} 