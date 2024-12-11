/// 密钥轮换服务
class KeyRotationService extends BaseService {
  final _storage = ServiceRegistry.instance.get<StorageService>('secure');
  final _config = ServiceRegistry.instance.get<SecurityConfig>('security');
  
  static const _keyVersionKey = 'key_version';
  static const _keyPrefix = 'encryption_key_v';
  
  @override
  Future<void> onInit() async {
    try {
      // 检查是否需要轮换密钥
      await _checkKeyRotation();
      
      LoggerService.info('Key rotation service initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize key rotation service', error: e);
      rethrow;
    }
  }

  /// 获取当前密钥版本
  Future<int> getCurrentKeyVersion() async {
    return await _storage.get<int>(_keyVersionKey) ?? 0;
  }

  /// 获取指定版本的密钥
  Future<Key?> getKey(int version) async {
    final keyData = await _storage.get<String>('${_keyPrefix}$version');
    if (keyData == null) return null;
    return Key.fromBase64(keyData);
  }

  /// 轮换密钥
  Future<void> rotateKey() async {
    try {
      final currentVersion = await getCurrentKeyVersion();
      final newVersion = currentVersion + 1;
      
      // 生成新密钥
      final newKey = await _generateKey();
      
      // 获取所有需要重新加密的数据
      final dataKeys = await _storage.getKeys();
      final encryptedData = <String, String>{};
      
      // 使用旧密钥解密数据
      final oldKey = await getKey(currentVersion);
      if (oldKey != null) {
        final oldEncrypter = Encrypter(AES(oldKey, mode: AESMode.cbc));
        for (final key in dataKeys) {
          if (key.startsWith(_keyPrefix)) continue;
          if (key == _keyVersionKey) continue;
          
          final data = await _storage.get<String>(key);
          if (data != null) {
            try {
              final decrypted = oldEncrypter.decrypt64(data, iv: IV.fromLength(16));
              encryptedData[key] = decrypted;
            } catch (e) {
              LoggerService.error('Failed to decrypt data during key rotation: $key', error: e);
            }
          }
        }
      }
      
      // 使用新密钥加密数据
      final newEncrypter = Encrypter(AES(newKey, mode: AESMode.cbc));
      for (final entry in encryptedData.entries) {
        final encrypted = newEncrypter.encrypt(entry.value, iv: IV.fromLength(16)).base64;
        await _storage.set(entry.key, encrypted);
      }
      
      // 保存新密钥
      await _storage.set('${_keyPrefix}$newVersion', newKey.base64);
      await _storage.set(_keyVersionKey, newVersion);
      
      // 清理旧密钥(保留一个版本)
      if (currentVersion > 0) {
        await _storage.remove('${_keyPrefix}${currentVersion - 1}');
      }
      
      LoggerService.info('Key rotated to version $newVersion');
    } catch (e) {
      LoggerService.error('Failed to rotate key', error: e);
      throw SecurityException('Failed to rotate key', e);
    }
  }

  /// 检查是否需要轮换密钥
  Future<void> _checkKeyRotation() async {
    final lastRotation = await _storage.get<String>('last_key_rotation');
    if (lastRotation != null) {
      final lastTime = DateTime.parse(lastRotation);
      final now = DateTime.now();
      
      // 根据配置检查是否需要轮换
      if (now.difference(lastTime) > _config.keyRotationInterval) {
        await rotateKey();
        await _storage.set('last_key_rotation', now.toIso8601String());
      }
    }
  }

  /// 生成新密钥
  Future<Key> _generateKey() async {
    final random = Random.secure();
    final keyBytes = List<int>.generate(_config.keyLength ~/ 8, (i) => random.nextInt(256));
    return Key(Uint8List.fromList(keyBytes));
  }
} 