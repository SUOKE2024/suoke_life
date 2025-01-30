class ThemeManager {
  static final instance = ThemeManager._();
  ThemeManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _currentTheme = Rx<AppTheme>(AppTheme.light);
  final _themeMode = Rx<ThemeMode>(ThemeMode.system);
  final _customColors = <String, Color>{}.obs;
  
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // 加载主题配置
    await _loadThemeConfig();
    
    // 监听系统主题变化
    _setupSystemThemeListener();
    
    _isInitialized = true;
  }

  Future<void> _loadThemeConfig() async {
    // 加载主题模式
    final savedMode = await _storage.getString('theme_mode');
    if (savedMode != null) {
      _themeMode.value = ThemeMode.values.firstWhere(
        (mode) => mode.toString() == savedMode,
        orElse: () => ThemeMode.system,
      );
    }

    // 加载当前主题
    final savedTheme = await _storage.getString('current_theme');
    if (savedTheme != null) {
      _currentTheme.value = AppTheme.values.firstWhere(
        (theme) => theme.toString() == savedTheme,
        orElse: () => AppTheme.light,
      );
    }

    // 加载自定义颜色
    final customColors = await _storage.getObject<Map<String, dynamic>>(
      'custom_colors',
      (json) => json,
    );
    if (customColors != null) {
      _customColors.addAll(
        customColors.map((key, value) => MapEntry(key, Color(value))),
      );
    }
  }

  void _setupSystemThemeListener() {
    // 监听系统主题变化
    WidgetsBinding.instance.window.onPlatformBrightnessChanged = () {
      if (_themeMode.value == ThemeMode.system) {
        _updateThemeBasedOnSystem();
      }
    };
  }

  void _updateThemeBasedOnSystem() {
    final brightness = WidgetsBinding.instance.window.platformBrightness;
    _currentTheme.value = brightness == Brightness.dark
        ? AppTheme.dark
        : AppTheme.light;
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    _themeMode.value = mode;
    await _storage.setString('theme_mode', mode.toString());
    
    if (mode == ThemeMode.system) {
      _updateThemeBasedOnSystem();
    }
    
    _eventBus.fire(ThemeModeChangedEvent(mode));
  }

  Future<void> setTheme(AppTheme theme) async {
    _currentTheme.value = theme;
    await _storage.setString('current_theme', theme.toString());
    _eventBus.fire(ThemeChangedEvent(theme));
  }

  Future<void> setCustomColor(String key, Color color) async {
    _customColors[key] = color;
    await _saveCustomColors();
    _eventBus.fire(CustomColorChangedEvent(key, color));
  }

  Future<void> _saveCustomColors() async {
    final colors = <String, dynamic>{};
    _customColors.forEach((key, value) {
      colors[key] = value.value;
    });
    await _storage.setObject('custom_colors', colors);
  }

  ThemeData get currentThemeData {
    final theme = _currentTheme.value;
    switch (theme) {
      case AppTheme.light:
        return _getLightTheme();
      case AppTheme.dark:
        return _getDarkTheme();
      case AppTheme.custom:
        return _getCustomTheme();
    }
  }

  ThemeData _getLightTheme() {
    return ThemeData(
      brightness: Brightness.light,
      primaryColor: _customColors['primary'] ?? Colors.blue,
      // 其他主题配置
    );
  }

  ThemeData _getDarkTheme() {
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: _customColors['primary'] ?? Colors.blue,
      // 其他主题配置
    );
  }

  ThemeData _getCustomTheme() {
    return ThemeData(
      primaryColor: _customColors['primary'] ?? Colors.blue,
      // 自定义主题配置
    );
  }

  AppTheme get currentTheme => _currentTheme.value;
  ThemeMode get themeMode => _themeMode.value;
  Stream<AppTheme> get themeStream => _currentTheme.stream;
  Stream<ThemeMode> get themeModeStream => _themeMode.stream;
  Map<String, Color> get customColors => Map.unmodifiable(_customColors);
}

enum AppTheme {
  light,
  dark,
  custom,
}

// 主题相关事件
class ThemeChangedEvent extends AppEvent {
  final AppTheme theme;
  ThemeChangedEvent(this.theme);
}

class ThemeModeChangedEvent extends AppEvent {
  final ThemeMode mode;
  ThemeModeChangedEvent(this.mode);
}

class CustomColorChangedEvent extends AppEvent {
  final String key;
  final Color color;
  CustomColorChangedEvent(this.key, this.color);
} 