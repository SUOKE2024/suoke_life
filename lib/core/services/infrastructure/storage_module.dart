/// Storage module that manages all storage services
class StorageModule extends BaseModule {
  @override
  String get name => 'storage';

  @override
  String get version => '1.0.0';

  @override
  List<String> get dependencies => [
    'network',  // 依赖网络模块
    'core',    // 依赖核心模块
  ];

  @override
  ModuleConfig? get config => _config;
  StorageModuleConfig? _config;

  @override
  Future<void> onInitialize() async {
    try {
      // Load configuration
      _config = await StorageConfigLoader.instance.loadConfig();
      final settings = _config!.settings;

      // Initialize storage services in order
      final fileStorage = await _initializeProvider(
        StorageType.file,
        (config) => FileStorage.initialize(config: config),
      );

      final secureStorage = await _initializeProvider(
        StorageType.secure,
        (config) => SecureStorage.initialize(config: config),
      );

      final cacheStorage = await _initializeProvider(
        StorageType.cache,
        (config) => CacheStorage.initialize(
          config: config,
          defaultExpiration: settings.defaultCacheExpiration,
        ),
      );

      // Initialize NAS storage if enabled
      NasStorage? nasStorage;
      if (StorageConfigLoader.instance.isProviderEnabled(StorageType.nas)) {
        final network = DependencyManager.instance.get<NetworkService>();
        nasStorage = await NasStorage.initialize(
          basePath: StorageConfigLoader.instance.getProviderOptions(
            StorageType.nas,
          )['base_url'],
          network: network,
          cache: cacheStorage!,
          config: StorageConfigLoader.instance.getProviderConfig(StorageType.nas),
        );
      }

      // Initialize unified storage service
      final storageService = StorageService.instance;
      await ServiceLifecycleManager.instance.registerService(storageService);

      // Register individual storage services if initialized
      if (fileStorage != null) {
        await ServiceLifecycleManager.instance.registerService(fileStorage);
      }
      if (secureStorage != null) {
        await ServiceLifecycleManager.instance.registerService(secureStorage);
      }
      if (cacheStorage != null) {
        await ServiceLifecycleManager.instance.registerService(cacheStorage);
      }
      if (nasStorage != null) {
        await ServiceLifecycleManager.instance.registerService(nasStorage);
      }

      LoggerService.info('Storage module initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize storage module', error: e);
      rethrow;
    }
  }

  /// Initialize a storage provider if enabled
  Future<T?> _initializeProvider<T extends BaseStorage>(
    StorageType type,
    Future<T> Function(StorageProviderConfig config) initializer,
  ) async {
    if (!StorageConfigLoader.instance.isProviderEnabled(type)) {
      LoggerService.info('Storage provider $type is disabled');
      return null;
    }

    final config = StorageConfigLoader.instance.getProviderConfig(type);
    if (config == null) {
      throw StorageConfigException(
        'Configuration not found for provider: $type',
      );
    }

    try {
      return await initializer(config);
    } catch (e) {
      LoggerService.error(
        'Failed to initialize storage provider: $type',
        error: e,
      );
      rethrow;
    }
  }

  @override
  Future<void> onDispose() async {
    await StorageConfigLoader.instance.reset();
    _config = null;
  }

  @override
  Map<Type, BaseService> services() => {
    StorageService: StorageService.instance,
  };
}

/// Storage module configuration
class StorageModuleConfig {
  final StorageConfig fileConfig;
  final StorageConfig secureConfig;
  final StorageConfig cacheConfig;
  final StorageConfig nasConfig;
  final String nasBasePath;

  const StorageModuleConfig({
    required this.fileConfig,
    required this.secureConfig,
    required this.cacheConfig,
    required this.nasConfig,
    required this.nasBasePath,
  });

  factory StorageModuleConfig.fromJson(Map<String, dynamic> json) => StorageModuleConfig(
    fileConfig: StorageConfig.fromJson(json['file_config']),
    secureConfig: StorageConfig.fromJson(json['secure_config']),
    cacheConfig: StorageConfig.fromJson(json['cache_config']),
    nasConfig: StorageConfig.fromJson(json['nas_config']),
    nasBasePath: json['nas_base_path'],
  );

  Map<String, dynamic> toJson() => {
    'file_config': fileConfig,
    'secure_config': secureConfig,
    'cache_config': cacheConfig,
    'nas_config': nasConfig,
    'nas_base_path': nasBasePath,
  };
} 