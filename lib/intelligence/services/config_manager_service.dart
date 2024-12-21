class ConfigManagerService extends GetxService {
  final StorageService _storageService;
  final SecurityManagerService _securityManager;
  final EventTrackingService _eventTracking;
  final PermissionManagerService _permissionManager;
  
  // 配置缓存
  final Map<String, dynamic> _configCache = {};
  final Map<String, DateTime> _lastUpdate = {};
  
  // 配置模式
  static const Map<String, ConfigMode> _configModes = {
    'system': ConfigMode(
      encrypted: true,
      cached: true,
      syncEnabled: true,
      updateInterval: Duration(hours: 24),
    ),
    'assistant': ConfigMode(
      encrypted: true,
      cached: true,
      syncEnabled: true,
      updateInterval: Duration(hours: 6),
    ),
    'user': ConfigMode(
      encrypted: true,
      cached: true,
      syncEnabled: true,
      updateInterval: Duration(minutes: 30),
    ),
    'temp': ConfigMode(
      encrypted: false,
      cached: true,
      syncEnabled: false,
      updateInterval: Duration(minutes: 5),
    ),
  };
  
  ConfigManagerService({
    required StorageService storageService,
    required SecurityManagerService securityManager,
    required EventTrackingService eventTracking,
    required PermissionManagerService permissionManager,
  })  : _storageService = storageService,
        _securityManager = securityManager,
        _eventTracking = eventTracking,
        _permissionManager = permissionManager {
    _startPeriodicSync();
  }

  Future<T?> getConfig<T>(
    String key,
    String scope, {
    String? userId,
    bool forceRefresh = false,
  }) async {
    try {
      // 检查权限
      if (userId != null) {
        final hasPermission = await _permissionManager.checkPermission(
          userId,
          'config',
          'read',
        );
        if (!hasPermission) {
          throw AIException(
            '无权访问配置',
            code: 'CONFIG_ACCESS_DENIED',
          );
        }
      }

      // 获取配置模式
      final mode = _getConfigMode(scope);
      
      // 检查缓存
      if (!forceRefresh && mode.cached) {
        final cached = await _getFromCache<T>(key, scope);
        if (cached != null) return cached;
      }

      // 从存储获取
      final value = await _getFromStorage<T>(key, scope);
      
      // 更新缓存
      if (mode.cached) {
        await _updateCache(key, scope, value);
      }

      return value;
    } catch (e) {
      await _trackConfigEvent(
        'get',
        key,
        scope,
        success: false,
        error: e,
        userId: userId,
      );
      rethrow;
    }
  }

  Future<void> setConfig<T>(
    String key,
    T value,
    String scope, {
    String? userId,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 检查权限
      if (userId != null) {
        final hasPermission = await _permissionManager.checkPermission(
          userId,
          'config',
          'write',
        );
        if (!hasPermission) {
          throw AIException(
            '无权修改配置',
            code: 'CONFIG_WRITE_DENIED',
          );
        }
      }

      // 获取配置模式
      final mode = _getConfigMode(scope);
      
      // 加密数据
      final data = await _prepareData(value, mode);
      
      // 保存到存储
      await _saveToStorage(key, scope, data, metadata);
      
      // 更新缓存
      if (mode.cached) {
        await _updateCache(key, scope, value);
      }

      // 记录事件
      await _trackConfigEvent(
        'set',
        key,
        scope,
        success: true,
        userId: userId,
        metadata: metadata,
      );
    } catch (e) {
      await _trackConfigEvent(
        'set',
        key,
        scope,
        success: false,
        error: e,
        userId: userId,
      );
      rethrow;
    }
  }

  Future<void> removeConfig(
    String key,
    String scope, {
    String? userId,
  }) async {
    try {
      // 检查权限
      if (userId != null) {
        final hasPermission = await _permissionManager.checkPermission(
          userId,
          'config',
          'delete',
        );
        if (!hasPermission) {
          throw AIException(
            '无权删除配置',
            code: 'CONFIG_DELETE_DENIED',
          );
        }
      }

      // 从存储删除
      await _removeFromStorage(key, scope);
      
      // 从缓存删除
      _removeFromCache(key, scope);

      // 记录事件
      await _trackConfigEvent(
        'remove',
        key,
        scope,
        success: true,
        userId: userId,
      );
    } catch (e) {
      await _trackConfigEvent(
        'remove',
        key,
        scope,
        success: false,
        error: e,
        userId: userId,
      );
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getConfigsByScope(
    String scope, {
    String? userId,
  }) async {
    try {
      // 检查权限
      if (userId != null) {
        final hasPermission = await _permissionManager.checkPermission(
          userId,
          'config',
          'read',
        );
        if (!hasPermission) {
          throw AIException(
            '无权访问配置',
            code: 'CONFIG_ACCESS_DENIED',
          );
        }
      }

      return await _storageService.getConfigsByScope(scope);
    } catch (e) {
      await _trackConfigEvent(
        'get_scope',
        'all',
        scope,
        success: false,
        error: e,
        userId: userId,
      );
      rethrow;
    }
  }

  ConfigMode _getConfigMode(String scope) {
    return _configModes[scope] ?? 
      ConfigMode(
        encrypted: false,
        cached: false,
        syncEnabled: false,
        updateInterval: Duration(minutes: 5),
      );
  }

  Future<T?> _getFromCache<T>(String key, String scope) async {
    final cacheKey = _getCacheKey(key, scope);
    final value = _configCache[cacheKey];
    
    if (value == null) return null;
    
    // 检查更新时间
    final lastUpdate = _lastUpdate[cacheKey];
    if (lastUpdate == null) return null;
    
    final mode = _getConfigMode(scope);
    if (DateTime.now().difference(lastUpdate) > mode.updateInterval) {
      return null;
    }
    
    return value as T;
  }

  Future<void> _updateCache<T>(
    String key,
    String scope,
    T value,
  ) async {
    final cacheKey = _getCacheKey(key, scope);
    _configCache[cacheKey] = value;
    _lastUpdate[cacheKey] = DateTime.now();
  }

  void _removeFromCache(String key, String scope) {
    final cacheKey = _getCacheKey(key, scope);
    _configCache.remove(cacheKey);
    _lastUpdate.remove(cacheKey);
  }

  String _getCacheKey(String key, String scope) => '${scope}_$key';

  Future<T?> _getFromStorage<T>(String key, String scope) async {
    final data = await _storageService.getConfig(key, scope);
    if (data == null) return null;
    
    // 解密数据
    final mode = _getConfigMode(scope);
    return await _decryptData<T>(data, mode);
  }

  Future<void> _saveToStorage(
    String key,
    String scope,
    dynamic data,
    Map<String, dynamic>? metadata,
  ) async {
    await _storageService.setConfig(
      key,
      scope,
      data,
      metadata: metadata,
    );
  }

  Future<void> _removeFromStorage(String key, String scope) async {
    await _storageService.removeConfig(key, scope);
  }

  Future<dynamic> _prepareData(
    dynamic value,
    ConfigMode mode,
  ) async {
    if (!mode.encrypted) return value;
    
    final jsonData = jsonEncode(value);
    return await _securityManager.encryptData(jsonData);
  }

  Future<T?> _decryptData<T>(
    dynamic data,
    ConfigMode mode,
  ) async {
    if (!mode.encrypted) return data as T;
    
    final decrypted = await _securityManager.decryptData(data);
    return jsonDecode(decrypted) as T;
  }

  Future<void> _trackConfigEvent(
    String action,
    String key,
    String scope, {
    required bool success,
    dynamic error,
    String? userId,
    Map<String, dynamic>? metadata,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'config_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId ?? 'system',
      assistantName: 'system',
      type: AIEventType.config,
      data: {
        'action': action,
        'key': key,
        'scope': scope,
        'success': success,
        'error': error?.toString(),
        'metadata': metadata,
      },
    ));
  }

  void _startPeriodicSync() {
    Timer.periodic(Duration(minutes: 15), (_) async {
      await _syncConfigs();
    });
  }

  Future<void> _syncConfigs() async {
    for (final entry in _configModes.entries) {
      final scope = entry.key;
      final mode = entry.value;
      
      if (!mode.syncEnabled) continue;
      
      try {
        await _syncScope(scope);
      } catch (e) {
        debugPrint('同步配置失败: $scope - $e');
      }
    }
  }

  Future<void> _syncScope(String scope) async {
    // TODO: 实现配置同步逻辑
  }
} 