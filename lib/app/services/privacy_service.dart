import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import '../core/security/encryption_service.dart';
import 'dart:convert';

class PrivacyService extends GetxService {
  final EncryptionService encryption;
  final StorageService storage;

  Future<void> saveUserData(UserData data) async {
    final encrypted = encryption.encrypt(jsonEncode(data));
    await storage.write(key: 'user_data', value: encrypted);
  }
} 