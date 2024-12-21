import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'package:encrypt/encrypt.dart';

class PrivacyProtectionService extends GetxService {
  final StorageService _storageService = Get.find();
  late final Encrypter _encrypter;
  late final IV _iv;

  @override
  void onInit() {
    super.onInit();
    _initEncryption();
  }

  void _initEncryption() {
    final key = Key.fromSecureRandom(32);
    _iv = IV.fromSecureRandom(16);
    _encrypter = Encrypter(AES(key));
  }

  // 数据加密
  String encryptData(String data) {
    return _encrypter.encrypt(data, iv: _iv).base64;
  }

  // 数据解密
  String decryptData(String encryptedData) {
    return _encrypter.decrypt64(encryptedData, iv: _iv);
  }

  // 数据脱敏
  Map<String, dynamic> anonymizeData(Map<String, dynamic> data) {
    final sensitiveKeys = ['phone', 'email', 'address', 'idCard'];
    final anonymized = Map<String, dynamic>.from(data);
    
    for (final key in sensitiveKeys) {
      if (anonymized.containsKey(key)) {
        anonymized[key] = _maskSensitiveData(anonymized[key]);
      }
    }
    
    return anonymized;
  }

  // 隐私设置管理
  Future<void> updatePrivacySettings(Map<String, bool> settings) async {
    try {
      await _storageService.saveLocal('privacy_settings', settings);
    } catch (e) {
      rethrow;
    }
  }

  // 获取隐私设置
  Future<Map<String, bool>> getPrivacySettings() async {
    try {
      final data = await _storageService.getLocal('privacy_settings');
      return data != null ? Map<String, bool>.from(data) : _getDefaultSettings();
    } catch (e) {
      return _getDefaultSettings();
    }
  }

  String _maskSensitiveData(String data) {
    if (data.length <= 4) return '*' * data.length;
    return '${data.substring(0, 2)}${'*' * (data.length - 4)}${data.substring(data.length - 2)}';
  }

  Map<String, bool> _getDefaultSettings() {
    return {
      'shareLocation': false,
      'shareHealth': false,
      'shareActivity': false,
      'allowAnalytics': true,
      'allowNotifications': true,
    };
  }
} 