import 'dart:convert';
import 'package:injectable/injectable.dart';
import 'package:encrypt/encrypt.dart';
import '../storage/secure_storage.dart';
import '../logger/app_logger.dart';
import 'security_config.dart';

@singleton
class KeyRotationService {
  final SecureStorage _storage;
  final SecurityConfig _config;
  final AppLogger _logger;

  KeyRotationService(this._storage, this._config, this._logger);

  Future<void> rotateKeys() async {
    try {
      // 实现密钥轮换逻辑
      await _storage.write('last_rotation', DateTime.now().toIso8601String());
    } catch (e, stack) {
      _logger.error('Failed to rotate keys', e, stack);
      rethrow;
    }
  }

  Future<bool> needsRotation() async {
    try {
      final lastRotation = await _storage.read('last_rotation');
      if (lastRotation == null) return true;

      final lastRotationDate = DateTime.parse(lastRotation);
      final daysSinceRotation = DateTime.now().difference(lastRotationDate).inDays;
      
      return daysSinceRotation >= _config.keyRotationDays;
    } catch (e, stack) {
      _logger.error('Failed to check key rotation', e, stack);
      return false;
    }
  }
} 