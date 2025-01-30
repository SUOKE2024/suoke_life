import 'package:injectable/injectable.dart';
import 'package:local_auth/local_auth.dart';
import 'package:local_auth_android/local_auth_android.dart';
import 'package:local_auth_darwin/local_auth_darwin.dart';

@singleton
class BiometricService {
  final LocalAuthentication _auth = LocalAuthentication();

  /// 检查设备是否支持生物识别
  Future<bool> isAvailable() async {
    try {
      return await _auth.canCheckBiometrics && await _auth.isDeviceSupported();
    } catch (e) {
      return false;
    }
  }

  /// 获取可用的生物识别类型
  Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      return await _auth.getAvailableBiometrics();
    } catch (e) {
      return [];
    }
  }

  /// 进行生物识别认证
  Future<bool> authenticate({
    String? localizedReason,
    bool biometricOnly = true,
  }) async {
    try {
      final canAuthenticate = await isAvailable();
      if (!canAuthenticate) {
        return false;
      }

      return await _auth.authenticate(
        localizedReason: localizedReason ?? '请验证生物识别以继续',
        options: AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: biometricOnly,
        ),
        authMessages: const <AuthMessages>[
          AndroidAuthMessages(
            signInTitle: '生物识别验证',
            cancelButton: '取消',
            biometricHint: '触摸传感器验证身份',
            biometricNotRecognized: '未能识别，请重试',
            biometricSuccess: '验证成功',
          ),
          IOSAuthMessages(
            cancelButton: '取消',
            goToSettingsButton: '去设置',
            goToSettingsDescription: '请在设置中配置生物识别',
            lockOut: '生物识别已被锁定，请稍后重试',
          ),
        ],
      );
    } catch (e) {
      return false;
    }
  }

  /// 停止当前的认证过程
  Future<void> stopAuthentication() async {
    try {
      await _auth.stopAuthentication();
    } catch (e) {
      // 忽略停止认证时的错误
    }
  }
} 