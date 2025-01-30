import 'package:get/get.dart';
import 'package:flutter/material.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class ThemeManagerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final themes = <String, ThemeData>{}.obs;
  final currentTheme = Rx<String?>(null);
  final themeConfigs = <String, Map<String, dynamic>>{}.obs;
  final themeHistory = <Map<String, dynamic>>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initThemeManager();
  }

  Future<void> _initThemeManager() async {
    try {
      await _loadThemeConfigs();
      await _loadThemeHistory();
      await _registerDefaultThemes();
      await _applyLastTheme();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize theme manager', data: {'error': e.toString()});
    }
  }

  // 注册主题
  Future<void> registerTheme(String name, ThemeData theme, [Map<String, dynamic>? config]) async {
    try {
      themes[name] = theme;
      if (config != null) {
        themeConfigs[name] = config;
        await _saveThemeConfigs();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to register theme', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 切换主题
  Future<void> switchTheme(String name) async {
    try {
      final theme = themes[name];
      if (theme == null) {
        throw Exception('Theme not found: $name');
      }

      currentTheme.value = name;
      Get.changeTheme(theme);
      
      await _recordThemeChange(name);
    } catch (e) {
      await _loggingService.log('error', 'Failed to switch theme', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 更新主题配置
  Future<void> updateThemeConfig(String name, Map<String, dynamic> config) async {
    try {
      if (!themes.containsKey(name)) {
        throw Exception('Theme not found: $name');
      }

      themeConfigs[name] = config;
      await _saveThemeConfigs();
      
      // 如果是当前主题,重新应用
      if (currentTheme.value == name) {
        await _applyThemeConfig(name);
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to update theme config', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取主题配置
  Map<String, dynamic>? getThemeConfig(String name) {
    try {
      return themeConfigs[name];
    } catch (e) {
      _loggingService.log('error', 'Failed to get theme config', data: {'name': name, 'error': e.toString()});
      return null;
    }
  }

  // 获取主题历史
  Future<List<Map<String, dynamic>>> getThemeHistory({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = themeHistory.toList();

      if (startDate != null || endDate != null) {
        history = history.where((record) {
          final timestamp = DateTime.parse(record['timestamp']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
          return true;
        }).toList();
      }

      return history;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get theme history', data: {'error': e.toString()});
      return [];
    }
  }

  Future<void> _registerDefaultThemes() async {
    try {
      // 注册默认主题
      await registerTheme('light', _buildLightTheme(), {
        'type': 'light',
        'name': '默认浅色主题',
        'description': '系统默认浅色主题',
      });

      await registerTheme('dark', _buildDarkTheme(), {
        'type': 'dark',
        'name': '默认深色主题',
        'description': '系统默认深色主题',
      });

      await registerTheme('custom', _buildCustomTheme(), {
        'type': 'custom',
        'name': '自定义主题',
        'description': '用户自定义主题',
      });
    } catch (e) {
      rethrow;
    }
  }

  ThemeData _buildLightTheme() {
    return ThemeData.light().copyWith(
      // 自定义浅色主题配置
    );
  }

  ThemeData _buildDarkTheme() {
    return ThemeData.dark().copyWith(
      // 自定义深色主题配置
    );
  }

  ThemeData _buildCustomTheme() {
    return ThemeData(
      // 自定义主题配置
    );
  }

  Future<void> _applyLastTheme() async {
    try {
      final lastTheme = await _storageService.getLocal('last_theme');
      if (lastTheme != null) {
        await switchTheme(lastTheme);
      } else {
        // 默认使用浅色主题
        await switchTheme('light');
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _applyThemeConfig(String name) async {
    try {
      final config = themeConfigs[name];
      if (config == null) return;

      final theme = themes[name];
      if (theme == null) return;

      // 根据配置更新主题逻辑
      // 示例：根据配置文件或数据库中的设置更新主题
      // 实际实现中需要根据具体配置源进行调用
      // 例如：if (config['darkMode']) { await switchTheme('dark'); } else { await switchTheme('light'); }
      await switchTheme(name);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadThemeConfigs() async {
    try {
      final configs = await _storageService.getLocal('theme_configs');
      if (configs != null) {
        themeConfigs.value = Map<String, Map<String, dynamic>>.from(configs);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveThemeConfigs() async {
    try {
      await _storageService.saveLocal('theme_configs', themeConfigs.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadThemeHistory() async {
    try {
      final history = await _storageService.getLocal('theme_history');
      if (history != null) {
        themeHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveThemeHistory() async {
    try {
      await _storageService.saveLocal('theme_history', themeHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordThemeChange(String name) async {
    try {
      final record = {
        'theme': name,
        'config': themeConfigs[name],
        'timestamp': DateTime.now().toIso8601String(),
      };

      themeHistory.insert(0, record);
      
      // 只保留最近100条记录
      if (themeHistory.length > 100) {
        themeHistory.removeRange(100, themeHistory.length);
      }
      
      await _saveThemeHistory();
      await _storageService.saveLocal('last_theme', name);
    } catch (e) {
      rethrow;
    }
  }
} 