import 'package:get/get.dart';
import '../core/storage/storage_service.dart';

class SystemConfigService extends GetxService {
  final StorageService _storageService = Get.find();

  final systemConfig = <String, dynamic>{}.obs;
  final featureFlags = <String, bool>{}.obs;
  final apiConfig = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _loadConfigurations();
  }

  // 更新系统配置
  Future<void> updateSystemConfig(Map<String, dynamic> config) async {
    try {
      systemConfig.value = {
        ...systemConfig,
        ...config,
        'updated_at': DateTime.now().toIso8601String(),
      };
      await _storageService.saveLocal('system_config', systemConfig.value);
    } catch (e) {
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
    } catch (e) {
      rethrow;
    }
  }

  // 更新API配置
  Future<void> updateApiConfig(Map<String, dynamic> config) async {
    try {
      apiConfig.value = {
        ...apiConfig,
        ...config,
        'updated_at': DateTime.now().toIso8601String(),
      };
      await _storageService.saveLocal('api_config', apiConfig.value);
    } catch (e) {
      rethrow;
    }
  }

  // 获取系统配置
  Map<String, dynamic> getSystemConfig() {
    return systemConfig.value;
  }

  // 检查功能开关
  bool isFeatureEnabled(String feature) {
    return featureFlags[feature] ?? false;
  }

  // 获取API配置
  Map<String, dynamic> getApiConfig() {
    return apiConfig.value;
  }

  Future<void> _loadConfigurations() async {
    try {
      // 加载系统配置
      final config = await _storageService.getLocal('system_config');
      if (config != null) {
        systemConfig.value = Map<String, dynamic>.from(config);
      } else {
        systemConfig.value = _getDefaultSystemConfig();
      }

      // 加载功能开关
      final flags = await _storageService.getLocal('feature_flags');
      if (flags != null) {
        featureFlags.value = Map<String, bool>.from(flags);
      } else {
        featureFlags.value = _getDefaultFeatureFlags();
      }

      // 加载API配置
      final api = await _storageService.getLocal('api_config');
      if (api != null) {
        apiConfig.value = Map<String, dynamic>.from(api);
      } else {
        apiConfig.value = _getDefaultApiConfig();
      }
    } catch (e) {
      // 处理错误
    }
  }

  Map<String, dynamic> _getDefaultSystemConfig() {
    return {
      'theme_mode': 'system',
      'language': 'zh_CN',
      'notification_enabled': true,
      'auto_sync': true,
    };
  }

  Map<String, bool> _getDefaultFeatureFlags() {
    return {
      'enable_ai_chat': true,
      'enable_health_tracking': true,
      'enable_life_recording': true,
      'enable_data_analysis': true,
    };
  }

  Map<String, dynamic> _getDefaultApiConfig() {
    return {
      'base_url': 'https://api.suoke.com',
      'timeout': 30000,
      'retry_count': 3,
      'enable_cache': true,
    };
  }
} 