class LocalizationManager {
  static final instance = LocalizationManager._();
  LocalizationManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _translations = <String, Map<String, String>>{};
  final _currentLocale = Rx<Locale>(const Locale('zh', 'CN'));
  final _fallbackLocale = const Locale('en', 'US');
  
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // 加载翻译资源
    await _loadTranslations();
    
    // 恢复上次语言设置
    await _restoreLocale();
    
    // 监听系统语言变化
    _setupSystemLocaleListener();
    
    _isInitialized = true;
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

  Future<void> _restoreLocale() async {
    final savedLocale = await _storage.getString('selected_locale');
    if (savedLocale != null) {
      final parts = savedLocale.split('_');
      if (parts.length == 2) {
        _currentLocale.value = Locale(parts[0], parts[1]);
      }
    } else {
      // 使用系统语言
      final systemLocale = PlatformDispatcher.instance.locale;
      if (_isSupported(systemLocale)) {
        _currentLocale.value = systemLocale;
      }
    }
  }

  void _setupSystemLocaleListener() {
    // 监听系统语言变化
    PlatformDispatcher.instance.onLocaleChanged = () {
      final systemLocale = PlatformDispatcher.instance.locale;
      if (_isSupported(systemLocale)) {
        setLocale(systemLocale);
      }
    };
  }

  bool _isSupported(Locale locale) {
    return _translations.containsKey('${locale.languageCode}_${locale.countryCode}');
  }

  Future<void> setLocale(Locale locale) async {
    if (!_isSupported(locale)) {
      locale = _fallbackLocale;
    }

    _currentLocale.value = locale;
    await _storage.setString(
      'selected_locale',
      '${locale.languageCode}_${locale.countryCode}',
    );
    
    _eventBus.fire(LocaleChangedEvent(locale));
  }

  String translate(String key, {
    Map<String, String>? args,
    String? context,
  }) {
    final localeKey = '${_currentLocale.value.languageCode}_${_currentLocale.value.countryCode}';
    final translations = _translations[localeKey];
    if (translations == null) return key;

    String value = translations[key] ?? _getFallbackTranslation(key);
    
    if (args != null) {
      args.forEach((argKey, argValue) {
        value = value.replaceAll('{$argKey}', argValue);
      });
    }

    return value;
  }

  String _getFallbackTranslation(String key) {
    final fallbackKey = '${_fallbackLocale.languageCode}_${_fallbackLocale.countryCode}';
    return _translations[fallbackKey]?[key] ?? key;
  }

  List<Locale> get supportedLocales => _translations.keys
      .map((key) {
        final parts = key.split('_');
        return Locale(parts[0], parts[1]);
      })
      .toList();

  Locale get currentLocale => _currentLocale.value;
  Stream<Locale> get localeStream => _currentLocale.stream;
}

class LocaleChangedEvent extends AppEvent {
  final Locale locale;
  LocaleChangedEvent(this.locale);
}

// 国���化扩展
extension LocalizationExtension on String {
  String tr({Map<String, String>? args, String? context}) {
    return LocalizationManager.instance.translate(
      this,
      args: args,
      context: context,
    );
  }
} 