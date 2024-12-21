import 'package:get/get.dart';
import 'package:flutter/material.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class LocalizationService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final translations = <String, Map<String, String>>{}.obs;
  final currentLocale = Rx<Locale?>(null);
  final supportedLocales = <Locale>[].obs;
  final localeHistory = <Map<String, dynamic>>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initLocalization();
  }

  Future<void> _initLocalization() async {
    try {
      await _loadTranslations();
      await _loadLocaleHistory();
      await _registerDefaultLocales();
      await _applyLastLocale();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize localization', data: {'error': e.toString()});
    }
  }

  // 注册翻译
  Future<void> registerTranslations(String locale, Map<String, String> texts) async {
    try {
      translations[locale] = texts;
      await _saveTranslations();
      
      // 添加到支持的语言列表
      final loc = _parseLocale(locale);
      if (loc != null && !supportedLocales.contains(loc)) {
        supportedLocales.add(loc);
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to register translations', data: {'locale': locale, 'error': e.toString()});
      rethrow;
    }
  }

  // 切换语言
  Future<void> changeLocale(String locale) async {
    try {
      final loc = _parseLocale(locale);
      if (loc == null) {
        throw Exception('Invalid locale: $locale');
      }

      if (!translations.containsKey(locale)) {
        throw Exception('Translations not found for locale: $locale');
      }

      currentLocale.value = loc;
      Get.updateLocale(loc);
      
      await _recordLocaleChange(locale);
    } catch (e) {
      await _loggingService.log('error', 'Failed to change locale', data: {'locale': locale, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取翻译文本
  String? getText(String key, [String? locale]) {
    try {
      final loc = locale ?? currentLocale.value?.toString();
      if (loc == null) return null;

      return translations[loc]?[key];
    } catch (e) {
      _loggingService.log('error', 'Failed to get text', data: {'key': key, 'error': e.toString()});
      return null;
    }
  }

  // 获取语言历史
  Future<List<Map<String, dynamic>>> getLocaleHistory({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = localeHistory.toList();

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
      await _loggingService.log('error', 'Failed to get locale history', data: {'error': e.toString()});
      return [];
    }
  }

  Future<void> _registerDefaultLocales() async {
    try {
      // 注册默认语言
      await registerTranslations('zh_CN', {
        'app_name': '索克生活',
        'welcome': '欢迎使用',
        // 添加更多中文翻译
      });

      await registerTranslations('en_US', {
        'app_name': 'SuoKe Life',
        'welcome': 'Welcome',
        // 添加更多英文翻译
      });
    } catch (e) {
      rethrow;
    }
  }

  Locale? _parseLocale(String locale) {
    try {
      final parts = locale.split('_');
      if (parts.length == 2) {
        return Locale(parts[0], parts[1]);
      } else if (parts.length == 1) {
        return Locale(parts[0]);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<void> _applyLastLocale() async {
    try {
      final lastLocale = await _storageService.getLocal('last_locale');
      if (lastLocale != null) {
        await changeLocale(lastLocale);
      } else {
        // 默认使用中文
        await changeLocale('zh_CN');
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadTranslations() async {
    try {
      final saved = await _storageService.getLocal('translations');
      if (saved != null) {
        translations.value = Map<String, Map<String, String>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveTranslations() async {
    try {
      await _storageService.saveLocal('translations', translations.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadLocaleHistory() async {
    try {
      final history = await _storageService.getLocal('locale_history');
      if (history != null) {
        localeHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveLocaleHistory() async {
    try {
      await _storageService.saveLocal('locale_history', localeHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordLocaleChange(String locale) async {
    try {
      final record = {
        'locale': locale,
        'timestamp': DateTime.now().toIso8601String(),
      };

      localeHistory.insert(0, record);
      
      // 只保留最近100条记录
      if (localeHistory.length > 100) {
        localeHistory.removeRange(100, localeHistory.length);
      }
      
      await _saveLocaleHistory();
      await _storageService.saveLocal('last_locale', locale);
    } catch (e) {
      rethrow;
    }
  }
} 