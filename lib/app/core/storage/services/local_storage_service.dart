/// 本地存储服务实现
class LocalStorageService implements StorageService {
  final StorageProvider _provider;
  final StorageOptions _options;
  final _cache = <String, StorageItem>{};
  int _currentSize = 0;
  final _encrypter = _createEncrypter();
  final _iv = IV.fromLength(16);

  LocalStorageService({
    required StorageProvider provider,
    StorageOptions? options,
  }) : _provider = provider,
       _options = options ?? const StorageOptions();

  @override
  Future<void> onInit() async {
    try {
      // 加载所有存储项到缓存
      final keys = await _provider.getKeys();
      for (final key in keys) {
        final data = await _provider.read(key);
        if (data != null) {
          final item = StorageItem.fromJson(data);
          if (!item.isExpired) {
            _cache[key] = item;
            _currentSize += _calculateSize(data);
          } else {
            // 删除过期数据
            await _provider.delete(key);
          }
        }
      }
      
      LoggerService.info('Local storage initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize local storage', error: e);
      rethrow;
    }
  }

  @override
  Future<T?> get<T>(String key) async {
    try {
      // 先从缓存获取
      final cached = _cache[key];
      if (cached != null) {
        if (cached.isExpired) {
          await remove(key);
          return null;
        }
        return cached.value as T?;
      }

      // 从存储获取
      final data = await _provider.read(key);
      if (data == null) return null;

      final item = StorageItem<T>.fromJson(data);
      if (item.isExpired) {
        await remove(key);
        return null;
      }

      // 添加到缓存
      _cache[key] = item;
      _currentSize += _calculateSize(data);

      return item.value;
    } catch (e) {
      LoggerService.error('Failed to get storage item: $key', error: e);
      throw StorageException('Failed to get item: $key', e);
    }
  }

  @override
  Future<void> set<T>(String key, T value) async {
    try {
      final item = StorageItem<T>(
        key: key,
        value: value,
        expireTime: _options.expireAfter != null
            ? DateTime.now().add(_options.expireAfter!)
            : null,
      );

      final data = item.toJson();
      final size = _calculateSize(data);

      // 检查存储限制
      if (_currentSize + size > _options.maxSize) {
        await _evictCache();
      }

      // 加密处理
      final encryptedData = _options.encrypt
          ? await _encrypt(data)
          : data;

      // 保存到存储
      await _provider.write(key, encryptedData);

      // 更新缓存
      _cache[key] = item;
      _currentSize += size;
    } catch (e) {
      LoggerService.error('Failed to set storage item: $key', error: e);
      throw StorageException('Failed to set item: $key', e);
    }
  }

  @override
  Future<void> remove(String key) async {
    try {
      // 从缓存移除
      final item = _cache.remove(key);
      if (item != null) {
        _currentSize -= _calculateSize(item.toJson());
      }

      // 从存储移除
      await _provider.delete(key);
    } catch (e) {
      LoggerService.error('Failed to remove storage item: $key', error: e);
      throw StorageException('Failed to remove item: $key', e);
    }
  }

  @override
  Future<void> clear() async {
    try {
      // 清空缓存
      _cache.clear();
      _currentSize = 0;

      // 清空存储
      await _provider.clear();
    } catch (e) {
      LoggerService.error('Failed to clear storage', error: e);
      throw StorageException('Failed to clear storage', e);
    }
  }

  @override
  Future<Set<String>> getKeys() async {
    return _cache.keys.toSet();
  }

  @override
  Future<bool> containsKey(String key) async {
    return _cache.containsKey(key);
  }

  @override
  Future<int> size() async {
    return _currentSize;
  }

  /// 计算数据大小
  int _calculateSize(Map<String, dynamic> data) {
    return jsonEncode(data).length;
  }

  /// 清理缓存
  Future<void> _evictCache() async {
    // 按过期时间和访问时间排序
    final entries = _cache.entries.toList()
      ..sort((a, b) {
        if (a.value.isExpired != b.value.isExpired) {
          return a.value.isExpired ? -1 : 1;
        }
        return a.value.createTime.compareTo(b.value.createTime);
      });

    // 移除直到满足大小限制
    for (final entry in entries) {
      if (_currentSize <= _options.maxSize * 0.8) break;
      await remove(entry.key);
    }
  }

  /// 加密数据
  Future<Map<String, dynamic>> _encrypt(Map<String, dynamic> data) async {
    if (!_options.encrypt) return data;
    
    try {
      final json = jsonEncode(data);
      final encrypted = _encrypter.encrypt(json, iv: _iv).base64;
      
      return {
        'data': encrypted,
        'iv': _iv.base64,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      LoggerService.error('Failed to encrypt data', error: e);
      throw StorageException('Failed to encrypt data', e);
    }
  }

  /// 解密数据
  Future<Map<String, dynamic>> _decrypt(Map<String, dynamic> data) async {
    if (!_options.encrypt) return data;
    
    try {
      final encrypted = data['data'] as String;
      final iv = IV.fromBase64(data['iv'] as String);
      
      final decrypted = _encrypter.decrypt64(encrypted, iv: iv);
      return jsonDecode(decrypted) as Map<String, dynamic>;
    } catch (e) {
      LoggerService.error('Failed to decrypt data', error: e);
      throw StorageException('Failed to decrypt data', e);
    }
  }

  @override
  Future<void> onDispose() async {
    _cache.clear();
    _currentSize = 0;
  }
} 