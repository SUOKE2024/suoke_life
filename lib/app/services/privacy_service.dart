import 'package:get/get.dart';
import 'package:encrypt/encrypt.dart';

class PrivacyService extends GetxService {
  late final Key _key;
  late final IV _iv;
  late final Encrypter _encrypter;

  Future<PrivacyService> init() async {
    _initEncryption();
    return this;
  }

  void _initEncryption() {
    _key = Key.fromSecureRandom(32);
    _iv = IV.fromSecureRandom(16);
    _encrypter = Encrypter(AES(_key));
  }

  String encrypt(String data) {
    return _encrypter.encrypt(data, iv: _iv).base64;
  }

  String decrypt(String encrypted) {
    return _encrypter.decrypt64(encrypted, iv: _iv);
  }

  bool isPrivateData(String key) {
    // 判断是否为隐私数据
    final privateKeys = [
      'health_',
      'medicine_',
      'personal_',
    ];
    return privateKeys.any((k) => key.startsWith(k));
  }

  Map<String, dynamic> maskSensitiveData(Map<String, dynamic> data) {
    // 对敏感数据进行脱敏
    final masked = Map<String, dynamic>.from(data);
    final sensitiveKeys = ['phone', 'email', 'address'];
    
    for (final key in sensitiveKeys) {
      if (masked.containsKey(key)) {
        masked[key] = _maskString(masked[key]);
      }
    }
    
    return masked;
  }

  String _maskString(String value) {
    if (value.length <= 4) return '*' * value.length;
    return '${value.substring(0, 2)}${'*' * (value.length - 4)}${value.substring(value.length - 2)}';
  }
} 