/// Storage module configuration
class StorageModuleConfig extends ModuleConfig {
  final StorageSettings settings;
  final Map<StorageType, StorageProviderConfig> providers;

  const StorageModuleConfig({
    required this.settings,
    required this.providers,
  });

  factory StorageModuleConfig.fromJson(Map<String, dynamic> json) {
    return StorageModuleConfig(
      settings: StorageSettings.fromJson(json['settings']),
      providers: (json['providers'] as Map<String, dynamic>).map(
        (key, value) => MapEntry(
          StorageType.values.firstWhere((e) => e.name == key),
          StorageProviderConfig.fromJson(value),
        ),
      ),
    );
  }

  @override
  Map<String, dynamic> toJson() => {
    'settings': settings.toJson(),
    'providers': providers.map(
      (key, value) => MapEntry(key.name, value.toJson()),
    ),
  };
}

/// Storage settings
class StorageSettings {
  final Duration defaultCacheExpiration;
  final int maxCacheSize;
  final bool encryptData;
  final String encryptionKey;

  const StorageSettings({
    this.defaultCacheExpiration = const Duration(hours: 1),
    this.maxCacheSize = 100 * 1024 * 1024, // 100MB
    this.encryptData = false,
    this.encryptionKey = '',
  });

  factory StorageSettings.fromJson(Map<String, dynamic> json) {
    return StorageSettings(
      defaultCacheExpiration: Duration(
        milliseconds: json['default_cache_expiration_ms'] ?? 3600000,
      ),
      maxCacheSize: json['max_cache_size'] ?? 104857600,
      encryptData: json['encrypt_data'] ?? false,
      encryptionKey: json['encryption_key'] ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'default_cache_expiration_ms': defaultCacheExpiration.inMilliseconds,
    'max_cache_size': maxCacheSize,
    'encrypt_data': encryptData,
    'encryption_key': encryptionKey,
  };
}

/// Storage provider configuration
class StorageProviderConfig {
  final String path;
  final String name;
  final Map<String, dynamic> options;
  final bool enabled;

  const StorageProviderConfig({
    required this.path,
    required this.name,
    this.options = const {},
    this.enabled = true,
  });

  factory StorageProviderConfig.fromJson(Map<String, dynamic> json) {
    return StorageProviderConfig(
      path: json['path'],
      name: json['name'],
      options: json['options'] ?? {},
      enabled: json['enabled'] ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
    'path': path,
    'name': name,
    'options': options,
    'enabled': enabled,
  };
}

/// Default storage configuration
const defaultStorageConfig = StorageModuleConfig(
  settings: StorageSettings(),
  providers: {
    StorageType.file: StorageProviderConfig(
      path: 'storage/files',
      name: 'file_storage',
    ),
    StorageType.secure: StorageProviderConfig(
      path: 'storage/secure',
      name: 'secure_storage',
    ),
    StorageType.cache: StorageProviderConfig(
      path: 'storage/cache',
      name: 'cache_storage',
    ),
    StorageType.nas: StorageProviderConfig(
      path: 'storage/nas',
      name: 'nas_storage',
      options: {
        'base_url': 'http://nas.example.com',
        'timeout_ms': 5000,
      },
    ),
  },
); 