/// 加密服务
class EncryptionService extends BaseService {
  late final Encrypter _encrypter;
  late final IV _iv;
  final _config = ServiceRegistry.instance.get<SecurityConfig>('security');

  @override
  Future<void> onInit() async {
    try {
      // 初始化加密器
      final key = await _getOrGenerateKey();
      _encrypter = Encrypter(AES(key, mode: AESMode.cbc));
      _iv = IV.fromLength(16);

      LoggerService.info('Encryption service initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize encryption service', error: e);
      rethrow;
    }
  }

  /// 加密数据
  Future<String> encrypt(String data) async {
    try {
      return _encrypter.encrypt(data, iv: _iv).base64;
    } catch (e) {
      LoggerService.error('Failed to encrypt data', error: e);
      throw SecurityException('Failed to encrypt data', e);
    }
  }

  /// 解密数据
  Future<String> decrypt(String encrypted) async {
    try {
      return _encrypter.decrypt64(encrypted, iv: _iv);
    } catch (e) {
      LoggerService.error('Failed to decrypt data', error: e);
      throw SecurityException('Failed to decrypt data', e);
    }
  }

  /// 获取或生成密钥
  Future<Key> _getOrGenerateKey() async {
    final storage = ServiceRegistry.instance.get<StorageService>('secure');
    
    // 尝试获取已存储的密钥
    final storedKey = await storage.get<String>('encryption_key');
    if (storedKey != null) {
      return Key.fromBase64(storedKey);
    }

    // 生成新密钥
    final key = await _generateKey();
    await storage.set('encryption_key', key.base64);
    return key;
  }

  /// 生成密钥
  Future<Key> _generateKey() async {
    final random = Random.secure();
    final keyBytes = List<int>.generate(32, (i) => random.nextInt(256));
    return Key(Uint8List.fromList(keyBytes));
  }

  @override
  Future<void> onDispose() async {
    // 清理敏感数据
    _encrypter = null;
    _iv = null;
  }
}

/// 安全异常
class SecurityException implements Exception {
  final String message;
  final dynamic cause;

  SecurityException(this.message, [this.cause]);

  @override
  String toString() => 'SecurityException: $message';
}

/// 安全配置
class SecurityConfig {
  /// 加密算法
  final String algorithm;
  
  /// 密钥长度
  final int keyLength;
  
  /// 是否启用安全存储
  final bool enableSecureStorage;

  const SecurityConfig({
    this.algorithm = 'AES',
    this.keyLength = 256,
    this.enableSecureStorage = true,
  });
} 