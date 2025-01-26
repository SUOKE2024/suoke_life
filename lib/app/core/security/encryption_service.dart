import 'package:injectable/injectable.dart';
import 'package:encrypt/encrypt.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

@singleton
class EncryptionService {
  static const _keyName = 'encryption_key';
  final FlutterSecureStorage _storage;
  late final Encrypter _encrypter;
  final IV _iv = IV.fromLength(16);

  EncryptionService(this._storage);

  Future<void> init() async {
    String? savedKey = await _storage.read(key: _keyName);
    _encrypter = Encrypter(AES(Key.fromBase64(savedKey)));
  }

  String encrypt(String data) {
    return _encrypter.encrypt(data, iv: _iv).base64;
  }

  String decrypt(String encryptedData) {
    return _encrypter.decrypt64(encryptedData, iv: _iv);
  }

  Future<void> rotateKey() async {
    final newKey = Key.fromSecureRandom(32);
    await _storage.write(key: _keyName, value: newKey.base64);
    _encrypter = Encrypter(AES(newKey));
  }
}
