import 'package:flutter/material.dart';
import 'package:shared_preferences.dart';
import '../models/theme_config.dart';
import 'dart:convert';

class ThemeService extends GetxController {
  static const String _keyThemeMode = 'theme_mode';
  static const String _keyPrimaryColor = 'primary_color';
  static const String _keyUseMaterial3 = 'use_material3';
  static const String _keyThemeConfig = 'theme_config';
  
  late final SharedPreferences _prefs;
  
  // 单例模式
  static final ThemeService _instance = ThemeService._internal();
  factory ThemeService() => _instance;
  ThemeService._internal();

  // 主题模式
  ThemeMode _themeMode = ThemeMode.system;
  ThemeMode get themeMode => _themeMode;

  // 主色调
  Color _primaryColor = Colors.blue;
  Color get primaryColor => _primaryColor;

  // 是否使用Material 3
  bool _useMaterial3 = true;
  bool get useMaterial3 => _useMaterial3;

  // 主题配置
  ThemeConfig _themeConfig = const ThemeConfig();
  ThemeConfig get themeConfig => _themeConfig;

  // 预设主题颜色
  final List<Color> presetColors = [
    Colors.blue,
    Colors.green,
    Colors.purple,
    Colors.orange,
    Colors.pink,
    Colors.teal,
    Colors.amber,
    Colors.indigo,
    Colors.red,
    Colors.cyan,
  ];

  // 预设主题配置
  final Map<String, ThemeConfig> presetConfigs = {
    '默认': const ThemeConfig(),
    '紧凑': const ThemeConfig(
      borderRadius: 8,
      elevation: 1,
      spacing: 12,
      iconSize: 20,
      fontSize: 13,
      isDense: true,
    ),
    '舒适': const ThemeConfig(
      borderRadius: 16,
      elevation: 4,
      spacing: 20,
      iconSize: 28,
      fontSize: 16,
      isDense: false,
    ),
    '无阴影': const ThemeConfig(
      useShadows: false,
      elevation: 0,
    ),
    '渐变': const ThemeConfig(
      useGradients: true,
      borderRadius: 20,
    ),
  };

  // 初始化
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    _loadThemeSettings();
  }

  // 加载主题设置
  void _loadThemeSettings() {
    final themeModeString = _prefs.getString(_keyThemeMode) ?? 'system';
    _themeMode = ThemeMode.values.firstWhere(
      (mode) => mode.toString() == 'ThemeMode.$themeModeString',
      orElse: () => ThemeMode.system,
    );

    final primaryColorValue = _prefs.getInt(_keyPrimaryColor) ?? Colors.blue.value;
    _primaryColor = Color(primaryColorValue);

    _useMaterial3 = _prefs.getBool(_keyUseMaterial3) ?? true;

    final themeConfigJson = _prefs.getString(_keyThemeConfig);
    if (themeConfigJson != null) {
      try {
        _themeConfig = ThemeConfig.fromJson(json.decode(themeConfigJson));
      } catch (e) {
        print('加载主题配置失败: $e');
        _themeConfig = const ThemeConfig();
      }
    }

    update();
  }

  // 设置主题模式
  Future<void> setThemeMode(ThemeMode mode) async {
    if (_themeMode == mode) return;
    _themeMode = mode;
    await _prefs.setString(_keyThemeMode, mode.toString().split('.').last);
    update();
  }

  // 设置主色调
  Future<void> setPrimaryColor(Color color) async {
    if (_primaryColor == color) return;
    _primaryColor = color;
    await _prefs.setInt(_keyPrimaryColor, color.value);
    update();
  }

  // 设置是否使用Material 3
  Future<void> setUseMaterial3(bool value) async {
    if (_useMaterial3 == value) return;
    _useMaterial3 = value;
    await _prefs.setBool(_keyUseMaterial3, value);
    update();
  }

  // 设置主题配置
  Future<void> setThemeConfig(ThemeConfig config) async {
    _themeConfig = config;
    await _prefs.setString(_keyThemeConfig, json.encode(config.toJson()));
    update();
  }

  // 应用预设主题配置
  Future<void> applyPresetConfig(String presetName) async {
    final config = presetConfigs[presetName];
    if (config != null) {
      await setThemeConfig(config);
    }
  }

  // 获取亮色主题
  ThemeData getLightTheme() {
    return _themeConfig.getThemeData(
      isDark: false,
      primaryColor: _primaryColor,
      useMaterial3: _useMaterial3,
    );
  }

  // 获取暗色主题
  ThemeData getDarkTheme() {
    return _themeConfig.getThemeData(
      isDark: true,
      primaryColor: _primaryColor,
      useMaterial3: _useMaterial3,
    );
  }

  // 重置主题设置
  Future<void> resetThemeSettings() async {
    await Future.wait([
      setThemeMode(ThemeMode.system),
      setPrimaryColor(Colors.blue),
      setUseMaterial3(true),
      setThemeConfig(const ThemeConfig()),
    ]);
  }
} 