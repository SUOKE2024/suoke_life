/// 安全存储提供者
class SecureStorageProvider implements StorageProvider {
  final FlutterSecureStorage _storage;
  final _encrypter = _createEncrypter();

  SecureStorageProvider() : _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock,
    ),
  );

  @override
  Future<Map<String, dynamic>?> read(String key) async {
    try {
      final encrypted = await _storage.read(key: key);
      if (encrypted == null) return null;

      // 解密数据
      final decrypted = _decrypt(encrypted);
      return jsonDecode(decrypted) as Map<String, dynamic>;
    } catch (e) {
      LoggerService.error('Failed to read secure storage: $key', error: e);
      rethrow;
    }
  }

  @override
  Future<void> write(String key, Map<String, dynamic> value) async {
    try {
      // 加密数据
      final json = jsonEncode(value);
      final encrypted = _encrypt(json);
      await _storage.write(key: key, value: encrypted);
    } catch (e) {
      LoggerService.error('Failed to write secure storage: $key', error: e);
      rethrow;
    }
  }

  @override
  Future<void> delete(String key) async {
    try {
      await _storage.delete(key: key);
    } catch (e) {
      LoggerService.error('Failed to delete secure storage: $key', error: e);
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      await _storage.deleteAll();
    } catch (e) {
      LoggerService.error('Failed to clear secure storage', error: e);
      rethrow;
    }
  }

  @override
  Future<Set<String>> getKeys() async {
    try {
      final all = await _storage.readAll();
      return all.keys.toSet();
    } catch (e) {
      LoggerService.error('Failed to get secure storage keys', error: e);
      rethrow;
    }
  }

  /// 创建加密器
  static Encrypter _createEncrypter() {
    // 从环境变量或配置获取密钥
    const keyString = String.fromEnvironment(
      'STORAGE_ENCRYPTION_KEY',
      defaultValue: 'your-secret-key-32-characters-long',
    );
    
    final key = Key.fromUtf8(keyString);
    final iv = IV.fromLength(16);
    
    return Encrypter(AES(key, mode: AESMode.cbc));
  }

  /// 加密数据
  String _encrypt(String data) {
    return _encrypter.encrypt(data, iv: _iv).base64;
  }

  /// 解密数据
  String _decrypt(String encrypted) {
    return _encrypter.decrypt64(encrypted, iv: _iv);
  }
} 