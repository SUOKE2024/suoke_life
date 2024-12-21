import 'package:encrypt/encrypt.dart';

class EncryptionService {
  late final Key _key;
  late final IV _iv;
  late final Encrypter _encrypter;

  EncryptionService() {
    _key = Key.fromSecureRandom(32);
    _iv = IV.fromSecureRandom(16);
    _encrypter = Encrypter(AES(_key));
  }

  String encrypt(String data) {
    return _encrypter.encrypt(data, iv: _iv).base64;
  }

  String decrypt(String encrypted) {
    final encrypted = Encrypted.fromBase64(encrypted);
    return _encrypter.decrypt(encrypted, iv: _iv);
  }

  // 针对不同安全级别的加密
  String encryptByLevel(String data, SecurityLevel level) {
    switch (level) {
      case SecurityLevel.S0:
        // 最高级别加密
        return _encryptHighest(data);
      case SecurityLevel.S1:
        // 标准加密
        return encrypt(data);
      case SecurityLevel.S2:
        // 基础加密
        return data; // 公开数据，无需加密
    }
  }

  String _encryptHighest(String data) {
    // 实现多重加密
    final firstPass = encrypt(data);
    return encrypt(firstPass); // 二次加密
  }
}

enum SecurityLevel {
  S0, // 核���隐私数据
  S1, // 一般隐私数据
  S2, // 公开数据
} 