import 'package:get/get.dart';
import 'package:local_auth/local_auth.dart';
import 'package:local_auth_android/local_auth_android.dart';
import 'package:local_auth_ios/local_auth_ios.dart';
import '../../storage/services/secure_storage_service.dart';
import 'auth_service.dart';

class BiometricAuthService extends GetxService {
  static BiometricAuthService get to => Get.find();
  
  final _auth = LocalAuthentication();
  final _storage = Get.find<SecureStorageService>();
  final _authService = Get.find<AuthService>();
  
  final _isBiometricEnabled = false.obs;
  bool get isBiometricEnabled => _isBiometricEnabled.value;
  
  // 初始化服务
  Future<BiometricAuthService> init() async {
    // 检查是否启用了生物识别
    final enabled = await _storage.read('biometric_enabled');
    _isBiometricEnabled.value = enabled == 'true';
    return this;
  }
  
  // 检查设备是否支持生物识别
  Future<bool> checkBiometricSupport() async {
    try {
      // 检查设备是否支持生物识别
      final canAuthenticateWithBiometrics = await _auth.canCheckBiometrics;
      final canAuthenticate = await _auth.isDeviceSupported();
      
      return canAuthenticateWithBiometrics && canAuthenticate;
    } catch (e) {
      return false;
    }
  }
  
  // 获取可用的生物识别类型
  Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      return await _auth.getAvailableBiometrics();
    } catch (e) {
      return [];
    }
  }
  
  // 启用生物识别
  Future<bool> enableBiometric() async {
    try {
      // 验证生物识别
      final didAuthenticate = await _auth.authenticate(
        localizedReason: '请验证生物识别以启用快速登录',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: true,
        ),
        authMessages: const <AuthMessages>[
          AndroidAuthMessages(
            signInTitle: '启用生物识别登录',
            cancelButton: '取消',
            biometricHint: '触摸传感器',
            biometricNotRecognized: '未能识别，请重试',
            biometricSuccess: '验证成功',
          ),
          IOSAuthMessages(
            cancelButton: '取消',
            goToSettingsButton: '去设置',
            goToSettingsDescription: '请在设置中启用生物识别',
            lockOut: '请先解锁设备',
          ),
        ],
      );
      
      if (didAuthenticate) {
        // 保存当前登录凭证
        final token = await _storage.read('auth_token');
        if (token != null) {
          await _storage.write('biometric_token', token);
          await _storage.write('biometric_enabled', 'true');
          _isBiometricEnabled.value = true;
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }
  
  // 禁用生物识别
  Future<void> disableBiometric() async {
    await _storage.delete('biometric_token');
    await _storage.write('biometric_enabled', 'false');
    _isBiometricEnabled.value = false;
  }
  
  // 使用生物识别登录
  Future<bool> authenticateWithBiometric() async {
    try {
      // 检查是否启用了生物识别
      if (!_isBiometricEnabled.value) return false;
      
      // 验证生物识别
      final didAuthenticate = await _auth.authenticate(
        localizedReason: '请验证生物识别以登录',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: true,
        ),
        authMessages: const <AuthMessages>[
          AndroidAuthMessages(
            signInTitle: '生物识别登录',
            cancelButton: '取消',
            biometricHint: '触摸传感器',
            biometricNotRecognized: '未能识别，请重试',
            biometricSuccess: '验证成功',
          ),
          IOSAuthMessages(
            cancelButton: '取消',
            goToSettingsButton: '去设置',
            goToSettingsDescription: '请在设置中启用生物识别',
            lockOut: '请先解锁设备',
          ),
        ],
      );
      
      if (didAuthenticate) {
        // 使用保存的token登录
        final token = await _storage.read('biometric_token');
        if (token != null) {
          await _authService._handleLoginSuccess(token);
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }
  
  // 更新生物识别token
  Future<void> updateBiometricToken() async {
    if (_isBiometricEnabled.value) {
      final token = await _storage.read('auth_token');
      if (token != null) {
        await _storage.write('biometric_token', token);
      }
    }
  }
} 