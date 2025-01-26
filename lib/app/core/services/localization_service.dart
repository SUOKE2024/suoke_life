import 'package:get/get.dart';
import 'package:flutter/material.dart';

class LocalizationService extends Translations {
  static final locale = _getLocale();
  static const fallbackLocale = Locale('zh', 'CN');

  static final langs = [
    'zh_CN',
    'en_US',
  ];

  static final locales = [
    const Locale('zh', 'CN'),
    const Locale('en', 'US'),
  ];

  @override
  Map<String, Map<String, String>> get keys => {
        'zh_CN': {
          'app_name': '索克生活',
          'home': '首页',
          'explore': '探索',
          'life': '生活',
          'profile': '我的',
          // ... 更多翻译
        },
        'en_US': {
          'app_name': 'Suoke Life',
          'home': 'Home',
          'explore': 'Explore',
          'life': 'Life',
          'profile': 'Profile',
          // ... 更多翻译
        },
      };

  static Locale _getLocale() {
    final String? languageCode = Get.deviceLocale?.languageCode;
    final String? countryCode = Get.deviceLocale?.countryCode;

    if (languageCode == null || countryCode == null) {
      return fallbackLocale;
    }

    final localeKey = '${languageCode}_$countryCode';
    if (langs.contains(localeKey)) {
      return Locale(languageCode, countryCode);
    }

    return fallbackLocale;
  }

  void changeLocale(String lang) {
    final locale = _getLocaleFromString(lang);
    Get.updateLocale(locale);
  }

  Locale _getLocaleFromString(String lang) {
    final codes = lang.split('_');
    return Locale(codes[0], codes[1]);
  }
}
