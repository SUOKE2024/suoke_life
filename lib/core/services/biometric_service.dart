import 'package:get/get.dart';
import 'package:local_auth/local_auth.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class BiometricService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final _localAuth = LocalAuthentication();

  final isAvailable = false.obs;
  final supportedBiometrics = <BiometricType>[].obs;
  final isAuthenticated = false.obs;

  @override
  void onInit() {
    super.onInit();
    _initBiometrics();
  }

  Future<void> _initBiometrics() async {
    try {
      isAvailable.value = await _localAuth.canCheckBiometrics;
      if (isAvailable.value) {
        supportedBiometrics.value = await _localAuth.getAvailableBiometrics();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize biometrics', data: {'error': e.toString()});
    }
  }

  // 生物识别认证
  Future<bool> authenticate({
    String localizedReason = '请进行生物识别认证',
    bool useErrorDialogs = true,
    bool stickyAuth = false,
  }) async {
    if (!isAvailable.value) return false;

    try {
      final authenticated = await _localAuth.authenticate(
        localizedReason: localizedReason,
        options: AuthenticationOptions(
          useErrorDialogs: useErrorDialogs,
          stickyAuth: stickyAuth,
          biometricOnly: true,
        ),
      );

      isAuthenticated.value = authenticated;
      await _logAuthenticationResult(authenticated);
      return authenticated;
    } catch (e) {
      await _loggingService.log('error', 'Failed to authenticate', data: {'error': e.toString()});
      return false;
    }
  }

  // 检查生物识别可用性
  Future<bool> checkBiometricAvailability() async {
    try {
      final canCheck = await _localAuth.canCheckBiometrics;
      final canAuth = await _localAuth.isDeviceSupported();
      return canCheck && canAuth;
    } catch (e) {
      await _loggingService.log('error', 'Failed to check biometric availability', data: {'error': e.toString()});
      return false;
    }
  }

  // 获取支持的生物识别类型
  Future<List<BiometricType>> getSupportedBiometrics() async {
    try {
      return await _localAuth.getAvailableBiometrics();
    } catch (e) {
      await _loggingService.log('error', 'Failed to get supported biometrics', data: {'error': e.toString()});
      return [];
    }
  }

  // 停止认证
  Future<void> stopAuthentication() async {
    try {
      await _localAuth.stopAuthentication();
      isAuthenticated.value = false;
    } catch (e) {
      await _loggingService.log('error', 'Failed to stop authentication', data: {'error': e.toString()});
    }
  }

  Future<void> _logAuthenticationResult(bool success) async {
    try {
      final authLog = {
        'success': success,
        'timestamp': DateTime.now().toIso8601String(),
        'biometric_types': supportedBiometrics.map((type) => type.toString()).toList(),
      };

      await _saveToHistory(authLog);
      await _loggingService.log(
        success ? 'info' : 'warning',
        'Biometric authentication ${success ? 'succeeded' : 'failed'}',
        data: authLog,
      );
    } catch (e) {
      // 忽略日志错误
    }
  }

  Future<void> _saveToHistory(Map<String, dynamic> log) async {
    try {
      final history = await _getHistory();
      history.insert(0, log);

      // 只保留最近100条记录
      if (history.length > 100) {
        history.removeRange(100, history.length);
      }

      await _storageService.saveLocal('biometric_history', history);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getHistory() async {
    try {
      final data = await _storageService.getLocal('biometric_history');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }
} 