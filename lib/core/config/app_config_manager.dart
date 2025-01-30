class AppConfigManager {
  static final instance = AppConfigManager._();
  AppConfigManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  late final AppConfig _config;
  final _remoteConfig = Rxn<RemoteConfig>();
  final _featureFlags = <String, bool>{}.obs;

  Future<void> initialize() async {
    // 加载本地配置
    await _loadLocalConfig();
    
    // 初始化远程配置
    await _initializeRemoteConfig();
    
    // 加载特性开关
    await _loadFeatureFlags();
  }

  Future<void> _loadLocalConfig() async {
    final configFile = await rootBundle.loadString('assets/config/app_config.yaml');
    final yaml = loadYaml(configFile);
    _config = AppConfig.fromYaml(yaml);
  }

  Future<void> _initializeRemoteConfig() async {
    final remoteConfig = FirebaseRemoteConfig.instance;
    await remoteConfig.setConfigSettings(RemoteConfigSettings(
      fetchTimeout: const Duration(minutes: 1),
      minimumFetchInterval: const Duration(hours: 1),
    ));

    await remoteConfig.setDefaults({
      'maintenance_mode': false,
      'api_endpoint': _config.apiEndpoint,
      'app_theme': 'system',
    });

    try {
      await remoteConfig.fetchAndActivate();
      _remoteConfig.value = remoteConfig;
      _eventBus.fire(RemoteConfigUpdatedEvent());
    } catch (e) {
      LoggerManager.instance.error('Remote config fetch failed', e);
    }
  }

  Future<void> _loadFeatureFlags() async {
    final flags = await _storage.getObject<Map<String, bool>>(
      'feature_flags',
      (json) => Map<String, bool>.from(json),
    ) ?? {};

    // 合并远程配置中的特性开关
    if (_remoteConfig.value != null) {
      final remoteFlags = _remoteConfig.value!.getAll();
      for (final entry in remoteFlags.entries) {
        if (entry.key.startsWith('feature_')) {
          flags[entry.key] = entry.value.asBool();
        }
      }
    }

    _featureFlags.value = flags;
  }

  Future<void> updateFeatureFlag(String key, bool value) async {
    _featureFlags[key] = value;
    await _storage.setObject('feature_flags', _featureFlags);
    _eventBus.fire(FeatureFlagUpdatedEvent(key: key, value: value));
  }

  bool isFeatureEnabled(String key) => _featureFlags[key] ?? false;
  
  String get apiEndpoint => _remoteConfig.value?.getString('api_endpoint') ?? _config.apiEndpoint;
  bool get isMaintenanceMode => _remoteConfig.value?.getBool('maintenance_mode') ?? false;
  String get appTheme => _remoteConfig.value?.getString('app_theme') ?? 'system';
}

class AppConfig {
  final String apiEndpoint;
  final String appName;
  final String version;
  final Map<String, dynamic> settings;

  AppConfig({
    required this.apiEndpoint,
    required this.appName,
    required this.version,
    this.settings = const {},
  });

  factory AppConfig.fromYaml(YamlMap yaml) {
    return AppConfig(
      apiEndpoint: yaml['api_endpoint'] as String,
      appName: yaml['app_name'] as String,
      version: yaml['version'] as String,
      settings: Map<String, dynamic>.from(yaml['settings'] ?? {}),
    );
  }
}

class RemoteConfigUpdatedEvent extends AppEvent {}

class FeatureFlagUpdatedEvent extends AppEvent {
  final String key;
  final bool value;

  FeatureFlagUpdatedEvent({
    required this.key,
    required this.value,
  });
} 