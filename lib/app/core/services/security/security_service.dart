import 'package:get/get.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../base_service.dart';
import 'package:encrypt/encrypt.dart';

class SecurityService extends GetxService implements BaseService {
  late final FlutterSecureStorage _secureStorage;
  late final Key _encryptionKey;
  late final IV _iv;
  late final Encrypter _encrypter;

  @override
  Future<SecurityService> init() async {
    _secureStorage = const FlutterSecureStorage();
    _encryptionKey = Key.fromSecureRandom(32);
    _iv = IV.fromSecureRandom(16);
    _encrypter = Encrypter(AES(_encryptionKey));
    return this;
  }

  @override
  Future<void> dispose() async {
    // Clean up if needed
  }

  Future<void> saveSecure(String key, String value) async {
    final encrypted = _encrypter.encrypt(value, iv: _iv);
    await _secureStorage.write(key: key, value: encrypted.base64);
  }

  Future<String?> getSecure(String key) async {
    final encrypted = await _secureStorage.read(key: key);
    if (encrypted == null) return null;
    return _encrypter.decrypt64(encrypted, iv: _iv);
  }

  Future<void> deleteSecure(String key) async {
    await _secureStorage.delete(key: key);
  }

  Future<void> clearSecure() async {
    await _secureStorage.deleteAll();
  }
} 