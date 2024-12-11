class SecurityManager {
  static final instance = SecurityManager._();
  SecurityManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  late final FlutterSecureStorage _secureStorage;
  late final LocalAuthentication _localAuth;
  
  bool _isInitialized = false;
  bool _isBiometricEnabled = false;
  SecurityLevel _securityLevel = SecurityLevel.standard;

  Future<void> initialize() async {
    if (_isInitialized) return;

    _secureStorage = const FlutterSecureStorage();
    _localAuth = LocalAuthentication();
    
    // 加载安全设置
    await _loadSecuritySettings();
    
    // 检查设备安全状态
    await _checkDeviceSecurity();
    
    _isInitialized = true;
  }

  Future<void> _loadSecuritySettings() async {
    _isBiometricEnabled = await _storage.getBool('biometric_enabled') ?? false;
    final level = await _storage.getString('security_level');
    _securityLevel = SecurityLevel.values.firstWhere(
      (e) => e.toString() == level,
      orElse: () => SecurityLevel.standard,
    );
  }

  Future<void> _checkDeviceSecurity() async {
    if (await DeviceUtils.isRooted) {
      _eventBus.fire(SecurityWarningEvent(
        type: SecurityWarningType.rootedDevice,
        message: 'Device is rooted/jailbroken',
      ));
    }

    if (await DeviceUtils.isEmulator) {
      _eventBus.fire(SecurityWarningEvent(
        type: SecurityWarningType.emulator,
        message: 'Running on emulator',
      ));
    }
  }

  Future<bool> authenticateWithBiometrics() async {
    if (!_isBiometricEnabled) return false;

    try {
      return await _localAuth.authenticate(
        localizedReason: 'Please authenticate to continue',
        options: const AuthenticationOptions(
          biometricOnly: true,
          stickyAuth: true,
        ),
      );
    } catch (e) {
      LoggerManager.instance.error('Biometric authentication failed', e);
      return false;
    }
  }

  Future<void> enableBiometrics(bool enable) async {
    if (enable) {
      final canAuthenticate = await _localAuth.canCheckBiometrics;
      if (!canAuthenticate) {
        throw SecurityException('Biometrics not available');
      }
    }
    
    _isBiometricEnabled = enable;
    await _storage.setBool('biometric_enabled', enable);
  }

  Future<String> encrypt(String data) async {
    final key = await _getOrGenerateKey();
    final encrypter = Encrypter(AES(key));
    final iv = IV.fromSecureRandom(16);
    
    final encrypted = encrypter.encrypt(data, iv: iv);
    return '${encrypted.base64}:${iv.base64}';
  }

  Future<String> decrypt(String encryptedData) async {
    final parts = encryptedData.split(':');
    if (parts.length != 2) {
      throw SecurityException('Invalid encrypted data format');
    }

    final key = await _getOrGenerateKey();
    final encrypter = Encrypter(AES(key));
    
    try {
      final encrypted = Encrypted.fromBase64(parts[0]);
      final iv = IV.fromBase64(parts[1]);
      return encrypter.decrypt(encrypted, iv: iv);
    } catch (e) {
      throw SecurityException('Decryption failed');
    }
  }

  Future<Key> _getOrGenerateKey() async {
    var keyStr = await _secureStorage.read(key: 'encryption_key');
    if (keyStr == null) {
      final key = Key.fromSecureRandom(32);
      await _secureStorage.write(
        key: 'encryption_key',
        value: base64.encode(key.bytes),
      );
      return key;
    }
    return Key(base64.decode(keyStr));
  }

  void setSecurityLevel(SecurityLevel level) {
    _securityLevel = level;
    _storage.setString('security_level', level.toString());
  }

  bool get isBiometricEnabled => _isBiometricEnabled;
  SecurityLevel get securityLevel => _securityLevel;
}

enum SecurityLevel {
  standard,
  high,
  extreme,
}

class SecurityException implements Exception {
  final String message;
  SecurityException(this.message);
}

class SecurityWarningEvent extends AppEvent {
  final SecurityWarningType type;
  final String message;

  SecurityWarningEvent({
    required this.type,
    required this.message,
  });
}

enum SecurityWarningType {
  rootedDevice,
  emulator,
  debugBuild,
  tampering,
} 