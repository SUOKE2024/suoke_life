import 'package:local_auth/local_auth.dart';
import 'package:local_auth_android/local_auth_android.dart';
import 'package:local_auth_ios/local_auth_ios.dart';

class BiometricService {
  final LocalAuthentication _auth;
  
  BiometricService() : _auth = LocalAuthentication();

  Future<bool> isAvailable() async {
    return await _auth.canCheckBiometrics && 
           await _auth.isDeviceSupported();
  }

  Future<List<BiometricType>> getAvailableBiometrics() async {
    return await _auth.getAvailableBiometrics();
  }

  Future<bool> authenticate({
    String localizedReason = '请验证身份',
    bool useErrorDialogs = true,
    bool stickyAuth = false,
  }) async {
    try {
      return await _auth.authenticate(
        localizedReason: localizedReason,
        options: AuthenticationOptions(
          useErrorDialogs: useErrorDialogs,
          stickyAuth: stickyAuth,
          biometricOnly: true,
        ),
        authMessages: const <AuthMessages>[
          AndroidAuthMessages(
            signInTitle: '生物识别验证',
            cancelButton: '取消',
            biometricHint: '触摸传感器',
            biometricNotRecognized: '未能识别',
            biometricSuccess: '验证成功',
          ),
          IOSAuthMessages(
            cancelButton: '取消',
            goToSettingsButton: '设置',
            goToSettingsDescription: '请在设置中启用生物识别',
            lockOut: '请先解锁设备',
          ),
        ],
      );
    } catch (e) {
      print('Biometric authentication error: $e');
      return false;
    }
  }

  Future<void> stopAuthentication() async {
    await _auth.stopAuthentication();
  }
} 