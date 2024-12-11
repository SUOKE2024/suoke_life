import 'package:flutter/material.dart';
import 'package:shared_preferences.dart';

class LocalizationService extends GetxController {
  static const String _keyLocale = 'locale';
  late final SharedPreferences _prefs;

  // 单例模式
  static final LocalizationService _instance = LocalizationService._internal();
  factory LocalizationService() => _instance;
  LocalizationService._internal();

  // 支持的语言列表
  final List<LocaleInfo> supportedLocales = [
    LocaleInfo(
      name: '简体中文',
      locale: const Locale('zh', 'CN'),
      flag: '🇨🇳',
      description: '中国大陆地区',
    ),
    LocaleInfo(
      name: '繁體中文',
      locale: const Locale('zh', 'TW'),
      flag: '🇹🇼',
      description: '港澳台地区',
    ),
    LocaleInfo(
      name: 'English',
      locale: const Locale('en', 'US'),
      flag: '🇺🇸',
      description: 'United States',
    ),
    LocaleInfo(
      name: '日本語',
      locale: const Locale('ja', 'JP'),
      flag: '🇯🇵',
      description: '日本',
    ),
    LocaleInfo(
      name: '한국어',
      locale: const Locale('ko', 'KR'),
      flag: '🇰🇷',
      description: '대한민국',
    ),
    LocaleInfo(
      name: 'Français',
      locale: const Locale('fr', 'FR'),
      flag: '🇫🇷',
      description: 'France',
    ),
    LocaleInfo(
      name: 'Deutsch',
      locale: const Locale('de', 'DE'),
      flag: '🇩🇪',
      description: 'Deutschland',
    ),
    LocaleInfo(
      name: 'Español',
      locale: const Locale('es', 'ES'),
      flag: '🇪🇸',
      description: 'España',
    ),
    LocaleInfo(
      name: 'Italiano',
      locale: const Locale('it', 'IT'),
      flag: '🇮🇹',
      description: 'Italia',
    ),
    LocaleInfo(
      name: 'Русский',
      locale: const Locale('ru', 'RU'),
      flag: '🇷🇺',
      description: 'Россия',
    ),
  ];

  // 当前语言
  Locale _currentLocale = const Locale('zh', 'CN');
  Locale get currentLocale => _currentLocale;

  // 初始化
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    _loadLocale();
  }

  // 加载语言设置
  void _loadLocale() {
    final languageCode = _prefs.getString('${_keyLocale}_language') ?? 'zh';
    final countryCode = _prefs.getString('${_keyLocale}_country') ?? 'CN';
    _currentLocale = Locale(languageCode, countryCode);
    update();
  }

  // 设置语言
  Future<void> setLocale(Locale locale) async {
    if (_currentLocale == locale) return;
    _currentLocale = locale;
    await _prefs.setString('${_keyLocale}_language', locale.languageCode);
    await _prefs.setString('${_keyLocale}_country', locale.countryCode ?? '');
    update();
  }

  // 获取当前语言的显示名称
  String getCurrentLocaleName() {
    return supportedLocales
        .firstWhere(
          (info) => info.locale == _currentLocale,
          orElse: () => supportedLocales.first,
        )
        .name;
  }

  // 获取当前语言的国旗表情
  String getCurrentLocaleFlag() {
    return supportedLocales
        .firstWhere(
          (info) => info.locale == _currentLocale,
          orElse: () => supportedLocales.first,
        )
        .flag;
  }

  // 获取当前语言的描述
  String getCurrentLocaleDescription() {
    return supportedLocales
        .firstWhere(
          (info) => info.locale == _currentLocale,
          orElse: () => supportedLocales.first,
        )
        .description;
  }

  // 重置语言设置
  Future<void> resetLocale() async {
    await setLocale(const Locale('zh', 'CN'));
  }

  // 获取系统语言
  Locale? getDeviceLocale() {
    final systemLocales = WidgetsBinding.instance.window.locales;
    if (systemLocales.isEmpty) return null;

    final deviceLocale = systemLocales.first;
    final matchedLocale = supportedLocales.firstWhere(
      (info) =>
          info.locale.languageCode == deviceLocale.languageCode &&
          info.locale.countryCode == deviceLocale.countryCode,
      orElse: () => supportedLocales.firstWhere(
        (info) => info.locale.languageCode == deviceLocale.languageCode,
        orElse: () => supportedLocales.first,
      ),
    );

    return matchedLocale.locale;
  }

  // 检查是否支持某个语言
  bool isLocaleSupported(Locale locale) {
    return supportedLocales.any((info) => info.locale == locale);
  }

  // 获取语言的本地化名称
  String getLocalizedLanguageName(Locale locale) {
    final translations = {
      'zh': {
        'zh': '中文',
        'en': '英语',
        'ja': '日语',
        'ko': '韩语',
        'fr': '法语',
        'de': '德语',
        'es': '西班牙语',
        'it': '意大利语',
        'ru': '俄语',
      },
      'en': {
        'zh': 'Chinese',
        'en': 'English',
        'ja': 'Japanese',
        'ko': 'Korean',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'it': 'Italian',
        'ru': 'Russian',
      },
    };

    final currentLanguage = _currentLocale.languageCode;
    final targetLanguage = locale.languageCode;

    return translations[currentLanguage]?[targetLanguage] ??
        translations['en']?[targetLanguage] ??
        locale.languageCode;
  }
}

// 语言信息类
class LocaleInfo {
  final String name;
  final Locale locale;
  final String flag;
  final String description;

  const LocaleInfo({
    required this.name,
    required this.locale,
    required this.flag,
    required this.description,
  });
}

// 翻译文本
class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  // 获取当前语言的翻译实例
  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  // 翻译文本映射表
  static final Map<String, Map<String, String>> _localizedValues = {
    'zh_CN': {
      'app_name': '寻宝探险',
      'settings': '设置',
      'theme': '主题',
      'language': '语言',
      'profile': '个人资料',
      'inventory': '背包',
      'achievements': '成就',
      'leaderboard': '排行榜',
      'privacy': '隐私设置',
      'about': '关于',
      'logout': '退出登录',
      // 添加更多翻译...
    },
    'zh_TW': {
      'app_name': '尋寶探險',
      'settings': '設置',
      'theme': '主題',
      'language': '語言',
      'profile': '個人資料',
      'inventory': '背包',
      'achievements': '成就',
      'leaderboard': '排行榜',
      'privacy': '隱私設置',
      'about': '關於',
      'logout': '退出登錄',
      // 添加更多翻译...
    },
    'en_US': {
      'app_name': 'Treasure Quest',
      'settings': 'Settings',
      'theme': 'Theme',
      'language': 'Language',
      'profile': 'Profile',
      'inventory': 'Inventory',
      'achievements': 'Achievements',
      'leaderboard': 'Leaderboard',
      'privacy': 'Privacy',
      'about': 'About',
      'logout': 'Logout',
      // 添加更多翻译...
    },
    'ja_JP': {
      'app_name': '宝探し',
      'settings': '設定',
      'theme': 'テーマ',
      'language': '言語',
      'profile': 'プロフィール',
      'inventory': 'インベントリ',
      'achievements': '実績',
      'leaderboard': 'ランキング',
      'privacy': 'プライバシー',
      'about': 'について',
      'logout': 'ログアウト',
      // 添加更多翻译...
    },
  };

  // 获取翻译文本
  String translate(String key) {
    final languageCode = locale.languageCode;
    final countryCode = locale.countryCode;
    final fullCode = '${languageCode}_${countryCode}';
    
    return _localizedValues[fullCode]?[key] ??
        _localizedValues['en_US']?[key] ??
        key;
  }
} 