import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../core/utils/constants.dart';
import 'theme_providers.dart';

/// 语言提供者
final localeProvider = StateNotifierProvider<LocaleNotifier, Locale>((ref) {
  return LocaleNotifier(ref.watch(sharedPreferencesProvider));
});

/// 支持的语言列表提供者
final supportedLocalesProvider = Provider<List<Locale>>((ref) {
  return const [
    Locale('zh', 'CN'), // 中文简体
    Locale('en', 'US'), // 英文
  ];
});

/// 语言名称映射提供者
final localeNamesProvider = Provider<Map<String, String>>((ref) {
  return const {
    'zh_CN': '简体中文',
    'en_US': 'English',
  };
});

/// 语言状态通知者
class LocaleNotifier extends StateNotifier<Locale> {
  final SharedPreferences _prefs;
  
  /// 构造函数
  LocaleNotifier(this._prefs) : super(_loadLocale(_prefs));
  
  /// 设置语言
  Future<void> setLocale(Locale locale) async {
    state = locale;
    await _prefs.setString(
      PreferenceKeys.userLanguage,
      '${locale.languageCode}_${locale.countryCode}',
    );
  }
  
  /// 重置为系统语言
  Future<void> resetToSystem() async {
    // 默认使用中文
    const defaultLocale = Locale('zh', 'CN');
    await setLocale(defaultLocale);
  }
  
  /// 加载存储的语言设置
  static Locale _loadLocale(SharedPreferences prefs) {
    final savedLocale = prefs.getString(PreferenceKeys.userLanguage);
    if (savedLocale == null) {
      // 默认使用中文
      return const Locale('zh', 'CN');
    }
    
    final parts = savedLocale.split('_');
    if (parts.length == 2) {
      return Locale(parts[0], parts[1]);
    }
    
    // 默认使用中文
    return const Locale('zh', 'CN');
  }
} 