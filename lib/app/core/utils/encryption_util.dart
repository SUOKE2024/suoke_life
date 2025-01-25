import 'package:encrypt/encrypt.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';

class EncryptionUtil {
  static const _storage = FlutterSecureStorage();
  static const _keyName = 'database_key';
  
  // 获取数据库密钥
  static Future<String> getDatabaseKey() async {
    String? key = await _storage.read(key: _keyName);
    if (key == null) {
      key = _generateKey();
      await _storage.write(key: _keyName, value: key);
    }
    return key;
  }

  // 生成随机密钥
  static String _generateKey() {
    final key = Key.fromSecureRandom(32);
    return base64Encode(key.bytes);
  }

  // 加密数据
  static String encrypt(String data) {
    final key = Key.fromSecureRandom(32);
    final iv = IV.fromSecureRandom(16);
    final encrypter = Encrypter(AES(key));
    final encrypted = encrypter.encrypt(data, iv: iv);
    
    return json.encode({
      'data': encrypted.base64,
      'key': base64Encode(key.bytes),
      'iv': base64Encode(iv.bytes),
    });
  }

  // 解密数据
  static String decrypt(String encryptedJson) {
    final Map<String, dynamic> data = json.decode(encryptedJson);
    final key = Key(base64Decode(data['key']));
    final iv = IV(base64Decode(data['iv']));
    final encrypter = Encrypter(AES(key));
    
    return encrypter.decrypt64(data['data'], iv: iv);
  }
} 