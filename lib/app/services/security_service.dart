import 'package:get/get.dart';
import 'package:crypto/crypto.dart';
import 'dart:convert';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class SecurityService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final isSecurityEnabled = true.obs;
  final securityLevel = 'high'.obs;

  @override
  void onInit() {
    super.onInit();
    _initSecurity();
  }

  Future<void> _initSecurity() async {
    try {
      await _loadSecuritySettings();
      await _checkSecurityStatus();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize security', data: {'error': e.toString()});
    }
  }

  // 加密数据
  Future<String> encryptData(String data, {String? key}) async {
    try {
      final encryptionKey = key ?? await _getEncryptionKey();
      final bytes = utf8.encode(data);
      final hmac = Hmac(sha256, utf8.encode(encryptionKey));
      final digest = hmac.convert(bytes);
      return base64.encode(digest.bytes);
    } catch (e) {
      await _loggingService.log('error', 'Failed to encrypt data', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 解密数据
  Future<String> decryptData(String encryptedData, {String? key}) async {
    try {
      // TODO: 实现数据解密
      return '';
    } catch (e) {
      await _loggingService.log('error', 'Failed to decrypt data', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 验证密码
  Future<bool> verifyPassword(String password) async {
    try {
      final hashedPassword = await _hashPassword(password);
      final storedHash = await _getStoredPasswordHash();
      return hashedPassword == storedHash;
    } catch (e) {
      await _loggingService.log('error', 'Failed to verify password', data: {'error': e.toString()});
      return false;
    }
  }

  // 更新安全设置
  Future<void> updateSecuritySettings(Map<String, dynamic> settings) async {
    try {
      await _storageService.saveLocal('security_settings', settings);
      await _loadSecuritySettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update security settings', data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadSecuritySettings() async {
    try {
      final settings = await _storageService.getLocal('security_settings');
      if (settings != null) {
        isSecurityEnabled.value = settings['enabled'] ?? true;
        securityLevel.value = settings['level'] ?? 'high';
      } else {
        await _saveDefaultSettings();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveDefaultSettings() async {
    try {
      await _storageService.saveLocal('security_settings', {
        'enabled': true,
        'level': 'high',
        'password_required': true,
        'biometric_enabled': true,
        'auto_lock': true,
        'lock_timeout': 300, // 5分钟
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _checkSecurityStatus() async {
    try {
      if (!isSecurityEnabled.value) {
        await _loggingService.log('warning', 'Security is disabled');
        return;
      }

      // 检查密码是否设置
      final hasPassword = await _hasPasswordSet();
      if (!hasPassword) {
        await _loggingService.log('warning', 'Password not set');
      }

      // 检查生物识别是否可用
      final biometricAvailable = await _checkBiometric();
      if (!biometricAvailable) {
        await _loggingService.log('info', 'Biometric not available');
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<String> _getEncryptionKey() async {
    try {
      final key = await _storageService.getLocal('encryption_key');
      if (key != null) return key;

      final newKey = _generateEncryptionKey();
      await _storageService.saveLocal('encryption_key', newKey);
      return newKey;
    } catch (e) {
      rethrow;
    }
  }

  String _generateEncryptionKey() {
    final random = base64.encode(List<int>.generate(32, (i) => DateTime.now().microsecondsSinceEpoch % 256));
    return sha256.convert(utf8.encode(random)).toString();
  }

  Future<String> _hashPassword(String password) async {
    final salt = await _getSalt();
    final bytes = utf8.encode(password + salt);
    return sha256.convert(bytes).toString();
  }

  Future<String> _getSalt() async {
    try {
      final salt = await _storageService.getLocal('password_salt');
      if (salt != null) return salt;

      final newSalt = base64.encode(List<int>.generate(16, (i) => DateTime.now().microsecondsSinceEpoch % 256));
      await _storageService.saveLocal('password_salt', newSalt);
      return newSalt;
    } catch (e) {
      rethrow;
    }
  }

  Future<String?> _getStoredPasswordHash() async {
    try {
      return await _storageService.getLocal('password_hash');
    } catch (e) {
      return null;
    }
  }

  Future<bool> _hasPasswordSet() async {
    try {
      final hash = await _getStoredPasswordHash();
      return hash != null;
    } catch (e) {
      return false;
    }
  }

  Future<bool> _checkBiometric() async {
    // TODO: 实现生物识别检查
    return false;
  }
} 