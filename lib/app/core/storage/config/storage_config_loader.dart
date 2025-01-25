/// Loads and manages storage module configuration
class StorageConfigLoader {
  static final instance = StorageConfigLoader._();
  StorageConfigLoader._();

  StorageModuleConfig? _config;
  bool _initialized = false;

  /// Load storage configuration
  Future<StorageModuleConfig> loadConfig() async {
    if (_initialized) return _config!;

    try {
      // Try loading from app config first
      final appConfig = DependencyManager.instance.get<AppConfigManager>();
      final config = await appConfig.getConfig<StorageModuleConfig>('storage');
      
      if (config != null) {
        _config = config;
        _initialized = true;
        return config;
      }

      // Try loading from yaml file
      final yaml = await rootBundle.loadString('assets/config/storage_config.yaml');
      final json = loadYaml(yaml) as Map;
      
      _config = StorageModuleConfig.fromJson(json.cast<String, dynamic>());
      _initialized = true;

      // Cache the config
      await appConfig.setConfig('storage', _config!);

      LoggerService.info('Storage configuration loaded');
      return _config!;
    } catch (e) {
      LoggerService.warning(
        'Failed to load storage config, using default',
        error: e,
      );
      
      // Use default config
      _config = defaultStorageConfig;
      _initialized = true;
      return _config!;
    }
  }

  /// Get provider configuration
  StorageProviderConfig? getProviderConfig(StorageType type) {
    if (!_initialized) {
      throw StateError('StorageConfigLoader not initialized');
    }
    return _config?.providers[type];
  }

  /// Get storage settings
  StorageSettings get settings {
    if (!_initialized) {
      throw StateError('StorageConfigLoader not initialized');
    }
    return _config?.settings ?? const StorageSettings();
  }

  /// Check if provider is enabled
  bool isProviderEnabled(StorageType type) {
    final config = getProviderConfig(type);
    return config?.enabled ?? false;
  }

  /// Get provider options
  Map<String, dynamic> getProviderOptions(StorageType type) {
    final config = getProviderConfig(type);
    return config?.options ?? const {};
  }

  /// Reset configuration
  Future<void> reset() async {
    _config = null;
    _initialized = false;
  }

  /// Update configuration
  Future<void> updateConfig(StorageModuleConfig config) async {
    final appConfig = DependencyManager.instance.get<AppConfigManager>();
    await appConfig.setConfig('storage', config);
    
    _config = config;
    _initialized = true;
  }
}

/// Storage configuration exception
class StorageConfigException implements Exception {
  final String message;
  final dynamic error;

  StorageConfigException(this.message, {this.error});

  @override
  String toString() {
    final buffer = StringBuffer('StorageConfigException: $message');
    if (error != null) {
      buffer.write('\nCaused by: $error');
    }
    return buffer.toString();
  }
} 