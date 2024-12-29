import 'package:encrypt/encrypt.dart';
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class EncryptionService {
  static const _keyName = 'encryption_key';
  late final Key _key;
  late final IV _iv;
  late final Encrypter _encrypter;
  final _secureStorage = const FlutterSecureStorage();

  Future<void> init() async {
    // 从安全存储获取或生成密钥
    String? storedKey = await _secureStorage.read(key: _keyName);
    if (storedKey == null) {
      final key = Key.fromSecureRandom(32);
      await _secureStorage.write(key: _keyName, value: base64.encode(key.bytes));
      _key = key;
    } else {
      _key = Key(base64.decode(storedKey));
    }

    _iv = IV.fromSecureRandom(16);
    _encrypter = Encrypter(AES(_key));
  }

  Future<String> encrypt(dynamic data) async {
    final jsonStr = jsonEncode(data);
    final encrypted = _encrypter.encrypt(jsonStr, iv: _iv);
    return base64.encode(encrypted.bytes);
  }

  Future<dynamic> decrypt(String encryptedData) async {
    try {
      final encrypted = Encrypted(base64.decode(encryptedData));
      final decrypted = _encrypter.decrypt(encrypted, iv: _iv);
      return jsonDecode(decrypted);
    } catch (e) {
      throw Exception('解密失败: $e');
    }
  }
} 