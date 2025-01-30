import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';

class TranslationManager extends Translations {
  static final instance = TranslationManager._();
  TranslationManager._();

  final _translations = <String, Map<String, String>>{};
  final _fallbackLocale = const Locale('en', 'US');
  
  Future<void> initialize() async {
    await _loadTranslations();
  }

  Future<void> _loadTranslations() async {
    // 加载所有语言文件
    final manifestContent = await rootBundle.loadString('AssetManifest.json');
    final Map<String, dynamic> manifestMap = json.decode(manifestContent);
    
    final languageFiles = manifestMap.keys
        .where((String key) => key.startsWith('assets/translations/'))
        .where((String key) => key.endsWith('.json'));

    for (final file in languageFiles) {
      final content = await rootBundle.loadString(file);
      final locale = _getLocaleFromPath(file);
      _translations[locale] = json.decode(content);
    }
  }

  String _getLocaleFromPath(String path) {
    final fileName = path.split('/').last;
    return fileName.split('.').first;
  }

  @override
  Map<String, Map<String, String>> get keys => _translations;

  Locale get fallbackLocale => _fallbackLocale;
} 