/// 安全擦除服务
class SecureEraser extends BaseService {
  final _storage = ServiceRegistry.instance.get<StorageService>('secure');
  final _config = ServiceRegistry.instance.get<SecurityConfig>('security');
  
  /// 安全擦除数据
  Future<void> secureErase(String key) async {
    if (!_config.enableSecureErase) {
      await _storage.remove(key);
      return;
    }
    
    try {
      // 获取数据大小
      final data = await _storage.get<String>(key);
      if (data == null) return;
      
      // 多次覆写随机数据
      final random = Random.secure();
      for (var i = 0; i < 3; i++) {
        final overwrite = List.generate(
          data.length,
          (i) => String.fromCharCode(random.nextInt(255))
        ).join();
        
        await _storage.set(key, overwrite);
      }
      
      // 最后删除数据
      await _storage.remove(key);
      
      LoggerService.info('Securely erased: $key');
    } catch (e) {
      LoggerService.error('Failed to securely erase: $key', error: e);
      throw SecurityException('Failed to securely erase data', e);
    }
  }

  /// 安全擦除���有数据
  Future<void> secureEraseAll() async {
    try {
      final keys = await _storage.getKeys();
      for (final key in keys) {
        await secureErase(key);
      }
      LoggerService.info('All data securely erased');
    } catch (e) {
      LoggerService.error('Failed to securely erase all data', error: e);
      throw SecurityException('Failed to securely erase all data', e);
    }
  }
} 