import 'package:encrypt/encrypt.dart';
import '../../models/message.dart';

class MessageEncryptionService {
  final Key _key;
  final IV _iv;
  final Encrypter _encrypter;

  MessageEncryptionService() : 
    _key = Key.fromSecureRandom(32),
    _iv = IV.fromSecureRandom(16),
    _encrypter = Encrypter(AES(Key.fromSecureRandom(32)));

  String encrypt(String text) {
    return _encrypter.encrypt(text, iv: _iv).base64;
  }

  String decrypt(String encrypted) {
    return _encrypter.decrypt64(encrypted, iv: _iv);
  }

  Message encryptMessage(Message message) {
    return Message(
      id: message.id,
      type: message.type,
      content: encrypt(message.content),
      isFromUser: message.isFromUser,
      timestamp: message.timestamp,
      duration: message.duration,
      thumbnail: message.thumbnail,
      metadata: message.metadata != null 
        ? _encryptMap(message.metadata!)
        : null,
    );
  }

  Message decryptMessage(Message message) {
    return Message(
      id: message.id,
      type: message.type,
      content: decrypt(message.content),
      isFromUser: message.isFromUser,
      timestamp: message.timestamp,
      duration: message.duration,
      thumbnail: message.thumbnail,
      metadata: message.metadata != null 
        ? _decryptMap(message.metadata!)
        : null,
    );
  }

  Map<String, dynamic> _encryptMap(Map<String, dynamic> map) {
    return map.map((key, value) => MapEntry(
      encrypt(key),
      value is String ? encrypt(value) : value,
    ));
  }

  Map<String, dynamic> _decryptMap(Map<String, dynamic> map) {
    return map.map((key, value) => MapEntry(
      decrypt(key),
      value is String ? decrypt(value) : value,
    ));
  }
} 