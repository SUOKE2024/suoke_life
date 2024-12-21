import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class AppConfigService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final appConfig = <String, dynamic>{}.obs;
  final featureFlags = <String, bool>{}.obs;
  final remoteConfig = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initConfig();
  }

  Future<void> _initConfig() async {
    try {
      await Future.wait([
        _loadAppConfig(),
        _loadFeatureFlags(),
        _loadRemoteConfig(),
      ]);
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize app config', data: {'error': e.toString()});
    }
  }

  // 更新应用配置
  Future<void> updateAppConfig(Map<String, dynamic> config) async {
    try {
      appConfig.value = {
        ...appConfig,
        ...config,
        'updated_at': DateTime.now().toIso8601String(),
      };
      
      await _storageService.saveLocal('app_config', appConfig.value);
      await _notifyConfigUpdate('app_config');
    } catch (e) {
      await _loggingService.log('error', 'Failed to update app config', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 更新功能开关
  Future<void> updateFeatureFlags(Map<String, bool> flags) async {
    try {
      featureFlags.value = {
        ...featureFlags,
        ...flags,
      };
      
      await _storageService.saveLocal('feature_flags', featureFlags.value);
      await _notifyConfigUpdate('feature_flags');
    } catch (e) {
      await _loggingService.log('error', 'Failed to update feature flags', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 同步远程配置
  Future<void> syncRemoteConfig() async {
    try {
      final config = await _fetchRemoteConfig();
      if (config != null) {
        remoteConfig.value = config;
        await _storageService.saveLocal('remote_config', config);
        await _notifyConfigUpdate('remote_config');
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to sync remote config', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 获取配置值
  T? getValue<T>(String key, {T? defaultValue}) {
    try {
      // 按优先级查找: 远程配置 > 应用配置 > 默认值
      if (remoteConfig.containsKey(key)) {
        return remoteConfig[key] as T;
      }
      
      if (appConfig.containsKey(key)) {
        return appConfig[key] as T;
      }
      
      return defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  // 检查功能开关
  bool isFeatureEnabled(String feature) {
    return featureFlags[feature] ?? false;
  }

  Future<void> _loadAppConfig() async {
    try {
      final config = await _storageService.getLocal('app_config');
      if (config != null) {
        appConfig.value = Map<String, dynamic>.from(config);
      } else {
        await _saveDefaultAppConfig();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadFeatureFlags() async {
    try {
      final flags = await _storageService.getLocal('feature_flags');
      if (flags != null) {
        featureFlags.value = Map<String, bool>.from(flags);
      } else {
        await _saveDefaultFeatureFlags();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadRemoteConfig() async {
    try {
      final config = await _storageService.getLocal('remote_config');
      if (config != null) {
        remoteConfig.value = Map<String, dynamic>.from(config);
      }
      await syncRemoteConfig();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveDefaultAppConfig() async {
    try {
      const defaultConfig = {
        'theme_mode': 'system',
        'language': 'zh_CN',
        'font_size': 'normal',
        'enable_analytics': true,
      };
      await updateAppConfig(defaultConfig);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveDefaultFeatureFlags() async {
    try {
      const defaultFlags = {
        'dark_mode': true,
        'multi_language': true,
        'debug_mode': false,
        'beta_features': false,
      };
      await updateFeatureFlags(defaultFlags);
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> _fetchRemoteConfig() async {
    try {
      // TODO: 实现远程配置获取
      return null;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _notifyConfigUpdate(String type) async {
    try {
      await _loggingService.log(
        'info',
        'Config updated',
        data: {'type': type, 'timestamp': DateTime.now().toIso8601String()},
      );
      // TODO: 通知其他服务配置已更新
    } catch (e) {
      rethrow;
    }
  }
} 