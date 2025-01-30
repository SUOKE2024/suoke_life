/// 完整性校验服务
class IntegrityService extends BaseService {
  final _storage = ServiceRegistry.instance.get<StorageService>('secure');
  final _config = ServiceRegistry.instance.get<SecurityConfig>('security');
  
  static const _checksumPrefix = 'checksum_';
  
  @override
  Future<void> onInit() async {
    try {
      if (_config.enableIntegrityCheck) {
        // 初始化时验证所有数据完整性
        await verifyAllData();
      }
      LoggerService.info('Integrity service initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize integrity service', error: e);
      rethrow;
    }
  }

  /// 计算数据校验和
  Future<String> calculateChecksum(String data) async {
    try {
      final bytes = utf8.encode(data);
      final digest = sha256.convert(bytes);
      return digest.toString();
    } catch (e) {
      LoggerService.error('Failed to calculate checksum', error: e);
      throw SecurityException('Failed to calculate checksum', e);
    }
  }

  /// 验证数据完整性
  Future<bool> verifyIntegrity(String key, String data) async {
    if (!_config.enableIntegrityCheck) return true;
    
    try {
      final storedChecksum = await _storage.get<String>('$_checksumPrefix$key');
      if (storedChecksum == null) return false;
      
      final currentChecksum = await calculateChecksum(data);
      return storedChecksum == currentChecksum;
    } catch (e) {
      LoggerService.error('Failed to verify integrity: $key', error: e);
      return false;
    }
  }

  /// 更新数据校验和
  Future<void> updateChecksum(String key, String data) async {
    if (!_config.enableIntegrityCheck) return;
    
    try {
      final checksum = await calculateChecksum(data);
      await _storage.set('$_checksumPrefix$key', checksum);
    } catch (e) {
      LoggerService.error('Failed to update checksum: $key', error: e);
      throw SecurityException('Failed to update checksum', e);
    }
  }

  /// 验证所有数据完整性
  Future<void> verifyAllData() async {
    try {
      final keys = await _storage.getKeys();
      final invalidKeys = <String>[];
      
      for (final key in keys) {
        if (key.startsWith(_checksumPrefix)) continue;
        
        final data = await _storage.get<String>(key);
        if (data != null) {
          final isValid = await verifyIntegrity(key, data);
          if (!isValid) {
            invalidKeys.add(key);
          }
        }
      }
      
      if (invalidKeys.isNotEmpty) {
        LoggerService.error('Data integrity check failed for keys: $invalidKeys');
        throw SecurityException('Data integrity check failed');
      }
    } catch (e) {
      LoggerService.error('Failed to verify all data', error: e);
      rethrow;
    }
  }
} 