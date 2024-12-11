/// 应用配置管理器
class AppConfigManager {
  static final instance = AppConfigManager._();
  AppConfigManager._();

  final _configs = <String, dynamic>{};
  final _storage = ServiceRegistry.instance.get<StorageService>();
  String _currentEnv = 'dev';

  /// 获取当前环境
  String get currentEnv => _currentEnv;

  /// 初始化配置管理器
  Future<void> initialize({String env = 'dev'}) async {
    try {
      _currentEnv = env;
      
      // 加载基础配置
      await _loadBaseConfig();
      
      // 加载环境配置
      await _loadEnvConfig(env);
      
      // 加载持久化配置
      await _loadStoredConfig();
      
      // 验证配置
      _validateConfigs();

      LoggerService.info('App config initialized for env: $env');
    } catch (e) {
      LoggerService.error('Failed to initialize app config', error: e);
      rethrow;
    }
  }

  /// 加载基础配置
  Future<void> _loadBaseConfig() async {
    final yaml = await rootBundle.loadString('assets/config/app_config.yaml');
    final json = loadYaml(yaml) as Map;
    _configs.addAll(json.cast<String, dynamic>());
  }

  /// 加载环境配置
  Future<void> _loadEnvConfig(String env) async {
    try {
      final envYaml = await rootBundle.loadString('assets/config/$env.yaml');
      final envJson = loadYaml(envYaml) as Map;
      _mergeConfigs(envJson.cast<String, dynamic>());
    } catch (e) {
      LoggerService.warning('No config found for env: $env');
    }
  }

  /// 加载持久化配置
  Future<void> _loadStoredConfig() async {
    final storedConfigs = await _storage.get<Map<String, dynamic>>('app_config');
    if (storedConfigs != null) {
      _mergeConfigs(storedConfigs);
    }
  }

  /// 合并配置
  void _mergeConfigs(Map<String, dynamic> newConfigs) {
    for (final entry in newConfigs.entries) {
      if (entry.value is Map) {
        final existing = _configs[entry.key] as Map?;
        if (existing != null) {
          _configs[entry.key] = _deepMerge(
            existing.cast<String, dynamic>(),
            (entry.value as Map).cast<String, dynamic>(),
          );
        } else {
          _configs[entry.key] = entry.value;
        }
      } else {
        _configs[entry.key] = entry.value;
      }
    }
  }

  /// 深度合并Map
  Map<String, dynamic> _deepMerge(
    Map<String, dynamic> target,
    Map<String, dynamic> source,
  ) {
    for (final key in source.keys) {
      if (source[key] is Map) {
        if (target[key] is! Map) {
          target[key] = <String, dynamic>{};
        }
        target[key] = _deepMerge(
          target[key] as Map<String, dynamic>,
          source[key] as Map<String, dynamic>,
        );
      } else {
        target[key] = source[key];
      }
    }
    return target;
  }

  /// 验证配置
  void _validateConfigs() {
    // 验证应用配置
    final appConfig = getConfig<AppConfig>('app');
    if (appConfig != null) {
      ConfigValidator.validateAppConfig(appConfig);
    }

    // 验证网络配置
    final networkConfig = getConfig<NetworkConfig>('network');
    if (networkConfig != null) {
      ConfigValidator.validateNetworkConfig(networkConfig);
    }

    // 验证AI配置
    final aiConfig = getConfig<AiConfig>('ai');
    if (aiConfig != null) {
      ConfigValidator.validateAiConfig(aiConfig);
    }

    // 验证数据库配置
    final dbConfig = getConfig<DatabaseConfig>('database');
    if (dbConfig != null) {
      ConfigValidator.validateDatabaseConfig(dbConfig);
    }

    // 验证存储配置
    final storageConfig = getConfig<StorageConfig>('storage');
    if (storageConfig != null) {
      ConfigValidator.validateStorageConfig(storageConfig);
    }
  }

  /// 获取配置
  T? getConfig<T>(String key) {
    final value = _configs[key];
    if (value is T) {
      return value;
    }
    return null;
  }

  /// 设置配置
  Future<void> setConfig<T>(String key, T value) async {
    _configs[key] = value;
    
    // 持久化配置
    await _storage.set('app_config', _configs);
  }

  /// 移除配置
  Future<void> removeConfig(String key) async {
    _configs.remove(key);
    
    // 更新持久化配置
    await _storage.set('app_config', _configs);
  }

  /// 清空配置
  Future<void> clear() async {
    _configs.clear();
    await _storage.remove('app_config');
  }

  /// 重置为默认配置
  Future<void> reset() async {
    await clear();
    await initialize();
  }
} 