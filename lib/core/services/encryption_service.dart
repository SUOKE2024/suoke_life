import 'package:get/get.dart';
import 'package:encrypt/encrypt.dart';

class EncryptionService extends GetxService {
  late final Key _key;
  late final IV _iv;
  late final Encrypter _encrypter;

  @override
  void onInit() {
    super.onInit();
    _initEncryption();
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
} 