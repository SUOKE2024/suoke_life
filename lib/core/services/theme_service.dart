import 'package:get/get.dart';
import 'package:flutter/material.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class ThemeService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final isDarkMode = false.obs;
  final currentTheme = Rx<ThemeData?>(null);
  final themeMode = ThemeMode.system.obs;
  final customColors = <String, Color>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initTheme();
  }

  Future<void> _initTheme() async {
    try {
      await _loadThemeSettings();
      await _applyTheme();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize theme',
          data: {'error': e.toString()});
    }
  }

  // 切换主题模式
  Future<void> toggleThemeMode() async {
    try {
      isDarkMode.value = !isDarkMode.value;
      themeMode.value = isDarkMode.value ? ThemeMode.dark : ThemeMode.light;

      await _applyTheme();
      await _saveThemeSettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to toggle theme mode',
          data: {'error': e.toString()});
      rethrow;
    }
  }

  // 更新主题
  Future<void> updateTheme(ThemeData theme) async {
    try {
      currentTheme.value = theme;
      await _saveThemeSettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update theme',
          data: {'error': e.toString()});
      rethrow;
    }
  }

  // 更新自定义颜色
  Future<void> updateCustomColors(Map<String, Color> colors) async {
    try {
      customColors.value = colors;
      await _saveThemeSettings();
      await _applyTheme();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update custom colors',
          data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadThemeSettings() async {
    try {
      final settings = await _storageService.getLocal('theme_settings');
      if (settings != null) {
        isDarkMode.value = settings['is_dark_mode'] ?? false;
        themeMode.value = ThemeMode.values[settings['theme_mode'] ?? 0];

        if (settings['custom_colors'] != null) {
          customColors.value = Map<String, Color>.from(
            settings['custom_colors']
                .map((key, value) => MapEntry(key, Color(value))),
          );
        }
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveThemeSettings() async {
    try {
      await _storageService.saveLocal('theme_settings', {
        'is_dark_mode': isDarkMode.value,
        'theme_mode': themeMode.value.index,
        'custom_colors':
            customColors.map((key, value) => MapEntry(key, value.value)),
        'updated_at': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _applyTheme() async {
    try {
      final theme = _buildTheme();
      currentTheme.value = theme;
      Get.changeTheme(theme);
    } catch (e) {
      rethrow;
    }
  }

  ThemeData _buildTheme() {
    final baseTheme = isDarkMode.value ? ThemeData.dark() : ThemeData.light();

    return baseTheme.copyWith(
      colorScheme: _buildColorScheme(baseTheme.colorScheme),
      textTheme: _buildTextTheme(baseTheme.textTheme),
      // 添加其他主题配置
    );
  }

  ColorScheme _buildColorScheme(ColorScheme base) {
    return base.copyWith(
      primary: customColors['primary'] ?? base.primary,
      secondary: customColors['secondary'] ?? base.secondary,
      surface: customColors['surface'] ?? base.surface,
      error: customColors['error'] ?? base.error,
      // 添加其他颜色配置
    );
  }

  TextTheme _buildTextTheme(TextTheme base) {
    return base.copyWith(
      // 自定义文本���式
      bodyLarge: base.bodyLarge?.copyWith(
        fontSize: 16,
        fontWeight: FontWeight.normal,
      ),
      bodyMedium: base.bodyMedium?.copyWith(
        fontSize: 14,
        fontWeight: FontWeight.normal,
      ),
      titleLarge: base.titleLarge?.copyWith(
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
      // 添加其他文本样式配置
    );
  }
}
