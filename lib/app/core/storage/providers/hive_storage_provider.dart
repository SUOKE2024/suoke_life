/// Hive存储提供者
class HiveStorageProvider implements StorageProvider {
  late final Box<Map> _box;
  static const _boxName = 'app_storage';

  Future<void> initialize() async {
    // 初始化 Hive
    await Hive.initFlutter();
    
    // 打开存储盒子
    _box = await Hive.openBox<Map>(_boxName);
    
    LoggerService.info('Hive storage initialized');
  }

  @override
  Future<Map<String, dynamic>?> read(String key) async {
    try {
      final value = _box.get(key);
      return value?.cast<String, dynamic>();
    } catch (e) {
      LoggerService.error('Failed to read from Hive: $key', error: e);
      rethrow;
    }
  }

  @override
  Future<void> write(String key, Map<String, dynamic> value) async {
    try {
      await _box.put(key, value);
    } catch (e) {
      LoggerService.error('Failed to write to Hive: $key', error: e);
      rethrow;
    }
  }

  @override
  Future<void> delete(String key) async {
    try {
      await _box.delete(key);
    } catch (e) {
      LoggerService.error('Failed to delete from Hive: $key', error: e);
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      await _box.clear();
    } catch (e) {
      LoggerService.error('Failed to clear Hive storage', error: e);
      rethrow;
    }
  }

  @override
  Future<Set<String>> getKeys() async {
    try {
      return _box.keys.cast<String>().toSet();
    } catch (e) {
      LoggerService.error('Failed to get Hive keys', error: e);
      rethrow;
    }
  }

  /// 关闭存储
  Future<void> close() async {
    await _box.close();
  }

  /// 压缩存储
  Future<void> compact() async {
    try {
      await _box.compact();
      LoggerService.info('Hive storage compacted');
    } catch (e) {
      LoggerService.error('Failed to compact Hive storage', error: e);
      rethrow;
    }
  }

  /// 获取存储大小
  Future<int> getSize() async {
    return await File(_box.path!).length();
  }
} 