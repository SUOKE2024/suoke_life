import 'package:shared_preferences.dart';

class SettingsService {
  static const String _keyBackgroundMusic = 'background_music';
  static const String _keySoundEffects = 'sound_effects';
  static const String _keyVibration = 'vibration';
  static const String _keyAutoRotate = 'auto_rotate';
  static const String _keyShowDistance = 'show_distance';
  static const String _keyShowCompass = 'show_compass';
  static const String _keyMusicVolume = 'music_volume';
  static const String _keyEffectsVolume = 'effects_volume';
  static const String _keyMapStyle = 'map_style';
  static const String _keyLanguage = 'language';
  static const String _keyHighQualityGraphics = 'high_quality_graphics';
  static const String _keyPowerSavingMode = 'power_saving_mode';
  static const String _keyShowFPS = 'show_fps';
  static const String _keyShowPing = 'show_ping';

  late final SharedPreferences _prefs;

  // 单例模式
  static final SettingsService _instance = SettingsService._internal();
  factory SettingsService() => _instance;
  SettingsService._internal();

  // 初始化
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // 获取设置值，带默认值
  bool getBackgroundMusic() => _prefs.getBool(_keyBackgroundMusic) ?? true;
  bool getSoundEffects() => _prefs.getBool(_keySoundEffects) ?? true;
  bool getVibration() => _prefs.getBool(_keyVibration) ?? true;
  bool getAutoRotate() => _prefs.getBool(_keyAutoRotate) ?? true;
  bool getShowDistance() => _prefs.getBool(_keyShowDistance) ?? true;
  bool getShowCompass() => _prefs.getBool(_keyShowCompass) ?? true;
  double getMusicVolume() => _prefs.getDouble(_keyMusicVolume) ?? 0.7;
  double getEffectsVolume() => _prefs.getDouble(_keyEffectsVolume) ?? 0.8;
  String getMapStyle() => _prefs.getString(_keyMapStyle) ?? '标准';
  String getLanguage() => _prefs.getString(_keyLanguage) ?? '简体中文';
  bool getHighQualityGraphics() => _prefs.getBool(_keyHighQualityGraphics) ?? true;
  bool getPowerSavingMode() => _prefs.getBool(_keyPowerSavingMode) ?? false;
  bool getShowFPS() => _prefs.getBool(_keyShowFPS) ?? false;
  bool getShowPing() => _prefs.getBool(_keyShowPing) ?? false;

  // 保存设置值
  Future<void> setBackgroundMusic(bool value) => _prefs.setBool(_keyBackgroundMusic, value);
  Future<void> setSoundEffects(bool value) => _prefs.setBool(_keySoundEffects, value);
  Future<void> setVibration(bool value) => _prefs.setBool(_keyVibration, value);
  Future<void> setAutoRotate(bool value) => _prefs.setBool(_keyAutoRotate, value);
  Future<void> setShowDistance(bool value) => _prefs.setBool(_keyShowDistance, value);
  Future<void> setShowCompass(bool value) => _prefs.setBool(_keyShowCompass, value);
  Future<void> setMusicVolume(double value) => _prefs.setDouble(_keyMusicVolume, value);
  Future<void> setEffectsVolume(double value) => _prefs.setDouble(_keyEffectsVolume, value);
  Future<void> setMapStyle(String value) => _prefs.setString(_keyMapStyle, value);
  Future<void> setLanguage(String value) => _prefs.setString(_keyLanguage, value);
  Future<void> setHighQualityGraphics(bool value) => _prefs.setBool(_keyHighQualityGraphics, value);
  Future<void> setPowerSavingMode(bool value) => _prefs.setBool(_keyPowerSavingMode, value);
  Future<void> setShowFPS(bool value) => _prefs.setBool(_keyShowFPS, value);
  Future<void> setShowPing(bool value) => _prefs.setBool(_keyShowPing, value);

  // 重置所有设置
  Future<void> resetAllSettings() async {
    await Future.wait([
      setBackgroundMusic(true),
      setSoundEffects(true),
      setVibration(true),
      setAutoRotate(true),
      setShowDistance(true),
      setShowCompass(true),
      setMusicVolume(0.7),
      setEffectsVolume(0.8),
      setMapStyle('标准'),
      setLanguage('简体中文'),
      setHighQualityGraphics(true),
      setPowerSavingMode(false),
      setShowFPS(false),
      setShowPing(false),
    ]);
  }
} 