import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../core/utils/constants.dart';
import '../../core/theme/app_theme.dart';

/// 主题模式状态提供者
final themeModeProvider = StateNotifierProvider<ThemeModeNotifier, ThemeMode>(
  (ref) => ThemeModeNotifier(
    ref.watch(sharedPreferencesProvider),
  ),
);

/// 主题数据提供者
final themeDataProvider = Provider<ThemeData>((ref) {
  final themeMode = ref.watch(themeModeProvider);
  switch (themeMode) {
    case ThemeMode.light:
      return AppTheme.lightTheme;
    case ThemeMode.dark:
      return AppTheme.darkTheme;
    case ThemeMode.system:
      final isPlatformDark = PlatformDispatcher.instance.platformBrightness == Brightness.dark;
      return isPlatformDark ? AppTheme.darkTheme : AppTheme.lightTheme;
  }
});

/// SharedPreferences 提供者
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('应该在应用启动时覆盖此提供者');
});

/// 主题模式状态通知者
class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  final SharedPreferences _prefs;
  
  /// 构造函数
  ThemeModeNotifier(this._prefs) : super(_loadThemeMode(_prefs));
  
  /// 设置主题模式
  Future<void> setThemeMode(ThemeMode mode) async {
    state = mode;
    await _prefs.setString(
      PreferenceKeys.themeMode,
      mode.toString().split('.').last,
    );
  }
  
  /// 切换主题模式
  Future<void> toggleThemeMode() async {
    if (state == ThemeMode.light) {
      await setThemeMode(ThemeMode.dark);
    } else {
      await setThemeMode(ThemeMode.light);
    }
  }
  
  /// 加载存储的主题模式
  static ThemeMode _loadThemeMode(SharedPreferences prefs) {
    final savedMode = prefs.getString(PreferenceKeys.themeMode);
    if (savedMode == null) return ThemeMode.system;
    
    return ThemeMode.values.firstWhere(
      (mode) => mode.toString().split('.').last == savedMode,
      orElse: () => ThemeMode.system,
    );
  }
} 