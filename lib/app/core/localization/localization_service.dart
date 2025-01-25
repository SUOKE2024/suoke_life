import 'package:injectable/injectable.dart';
import 'package:flutter/material.dart';
import '../storage/local_storage.dart';

@singleton
class LocalizationService {
  final LocalStorage _storage;
  static const _languageKey = 'app_language';
  static const fallbackLocale = Locale('zh', 'CN');

  static final supportedLocales = [
    const Locale('zh', 'CN'),
    const Locale('en', 'US'),
  ];

  LocalizationService(this._storage);

  Locale getCurrentLocale() {
    final savedLanguage = _storage.getString(_languageKey);
    if (savedLanguage == null) return fallbackLocale;

    final parts = savedLanguage.split('_');
    if (parts.length != 2) return fallbackLocale;

    return Locale(parts[0], parts[1]);
  }

  Future<void> setLocale(Locale locale) async {
    await _storage.setString(_languageKey, '${locale.languageCode}_${locale.countryCode}');
  }

  bool isSupported(Locale locale) {
    return supportedLocales.contains(locale);
  }

  String getDisplayLanguage(Locale locale) {
    switch ('${locale.languageCode}_${locale.countryCode}') {
      case 'zh_CN':
        return '简体中文';
      case 'en_US':
        return 'English';
      default:
        return locale.languageCode;
    }
  }

  List<Locale> getSupportedLocales() => supportedLocales;
} 