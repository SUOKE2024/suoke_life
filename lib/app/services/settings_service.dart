import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class SettingsService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final settings = <String, dynamic>{}.obs;
  final defaultSettings = <String, dynamic>{
    'general': {
      'language': 'zh_CN',
      'theme': 'system',
      'font_size': 'normal',
      'notification': true,
      'auto_backup': true,
    },
    'privacy': {
      'data_collection': true,
      'analytics': true,
      'crash_report': true,
      'personalization': true,
    },
    'security': {
      'biometric_auth': true,
      'auto_lock': true,
      'lock_timeout': 300, // 5分钟
      'secure_storage': true,
    },
    'sync': {
      'auto_sync': true,
      'sync_interval': 3600, // 1小时
      'sync_on_wifi_only': true,
      'background_sync': true,
    },
    'performance': {
      'cache_size': 100, // MB
      'keep_history': 30, // 天
      'auto_cleanup': true,
      'optimize_storage': true,
    },
  };

  @override
  void onInit() {
    super.onInit();
  }

  @override
  Future<void> onReady() async {
    super.onReady();
    await _initSettings();
  }

  Future<void> _initSettings() async {
    try {
      await _loadSettings();
      await _validateSettings();
      await _applySettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize settings', data: {'error': e.toString()});
    }
  }

  // 获取设置值
  T? getSetting<T>(String key, {T? defaultValue}) {
    try {
      final keys = key.split('.');
      dynamic value = settings;
      
      for (final k in keys) {
        if (value is! Map) return defaultValue;
        value = value[k];
      }
      
      return value as T? ?? defaultValue;
    } catch (e) {
      _loggingService.log('error', 'Failed to get setting', data: {'key': key, 'error': e.toString()});
      return defaultValue;
    }
  }

  // 更新设置
  Future<void> updateSetting(String key, dynamic value) async {
    try {
      final keys = key.split('.');
      final lastKey = keys.removeLast();
      
      dynamic target = settings;
      for (final k in keys) {
        target = target[k];
      }
      
      if (target is Map) {
        target[lastKey] = value;
        await _saveSettings();
        await _applySettings();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to update setting', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  // 重置设置
  Future<void> resetSettings([String? section]) async {
    try {
      if (section != null) {
        settings[section] = Map<String, dynamic>.from(defaultSettings[section]);
      } else {
        settings.value = Map<String, dynamic>.from(defaultSettings);
      }
      
      await _saveSettings();
      await _applySettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to reset settings', data: {'section': section, 'error': e.toString()});
      rethrow;
    }
  }

  // 导入设置
  Future<void> importSettings(Map<String, dynamic> newSettings) async {
    try {
      settings.value = newSettings;
      await _validateSettings();
      await _saveSettings();
      await _applySettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to import settings', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 导出设置
  Future<Map<String, dynamic>> exportSettings() async {
    try {
      return Map<String, dynamic>.from(settings);
    } catch (e) {
      await _loggingService.log('error', 'Failed to export settings', data: {'error': e.toString()});
      return {};
    }
  }

  Future<void> _loadSettings() async {
    try {
      final saved = await _storageService.getLocal('app_settings');
      if (saved != null) {
        settings.value = Map<String, dynamic>.from(saved);
      } else {
        settings.value = Map<String, dynamic>.from(defaultSettings);
        await _saveSettings();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveSettings() async {
    try {
      await _storageService.saveLocal('app_settings', settings.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _validateSettings() async {
    try {
      // 验证所有必需的设置项是否存在
      for (final section in defaultSettings.keys) {
        if (!settings.containsKey(section)) {
          settings[section] = Map<String, dynamic>.from(defaultSettings[section]);
          continue;
        }

        for (final key in defaultSettings[section].keys) {
          if (!settings[section].containsKey(key)) {
            settings[section][key] = defaultSettings[section][key];
          }
        }
      }

      // 验证设置值类型
      _validateSettingTypes(settings.value, defaultSettings);
    } catch (e) {
      rethrow;
    }
  }

  void _validateSettingTypes(Map<String, dynamic> current, Map<String, dynamic> template) {
    for (final key in template.keys) {
      final templateValue = template[key];
      final currentValue = current[key];

      if (templateValue is Map<String, dynamic>) {
        if (currentValue is! Map) {
          current[key] = Map<String, dynamic>.from(templateValue);
        } else {
          _validateSettingTypes(currentValue as Map<String, dynamic>, templateValue);
        }
      } else {
        if (currentValue.runtimeType != templateValue.runtimeType) {
          current[key] = templateValue;
        }
      }
    }
  }

  void updateLocale(String language) {
    Get.updateLocale(Locale(language));
  }

  void updateThemeMode(String mode) {
    switch (mode) {
      case 'light':
        Get.changeThemeMode(ThemeMode.light);
        break;
      case 'dark':
        Get.changeThemeMode(ThemeMode.dark);
        break;
      default:
        Get.changeThemeMode(ThemeMode.system);
    }
  }

  Future<void> _applySettings() async {
    try {
      final language = getSetting<String>('general.language');
      if (language != null) {
        await Get.updateLocale(Locale(language));
      }

      // 应用主题设置
      final theme = getSetting<String>('general.theme');
      if (theme != null) {
        switch (theme) {
          case 'light':
            Get.changeThemeMode(ThemeMode.light);
            break;
          case 'dark':
            Get.changeThemeMode(ThemeMode.dark);
            break;
          default:
            Get.changeThemeMode(ThemeMode.system);
        }
      }

      // 应用字体大小设置
      final fontSize = getSetting<String>('general.font_size');
      if (fontSize != null) {
        // TODO: 实现字体大小调整
      }

      // 应用其他设置
      await _applySecuritySettings();
      await _applySyncSettings();
      await _applyPerformanceSettings();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _applySecuritySettings() async {
    try {
      // TODO: 实现安全设置应用
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _applySyncSettings() async {
    try {
      // TODO: 实现同步设置应用
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _applyPerformanceSettings() async {
    try {
      // TODO: 实现性能设置应用
    } catch (e) {
      rethrow;
    }
  }
} 