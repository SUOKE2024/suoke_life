import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 首选项管理器，统一管理应用程序持久化存储
class PreferencesManager {
  final SharedPreferences _preferences;
  final FlutterSecureStorage _secureStorage;

  // 密钥常量
  static const String _keyToken = 'auth_token';
  static const String _keyRefreshToken = 'refresh_token';
  static const String _keyUserId = 'user_id';
  static const String _keyUsername = 'username';
  static const String _keyHasSeenWelcome = 'has_seen_welcome';
  static const String _keyAppTheme = 'app_theme';
  static const String _keyLanguage = 'language';
  static const String _keyNotificationsEnabled = 'notifications_enabled';

  PreferencesManager(this._preferences, this._secureStorage);

  // 认证令牌管理
  Future<void> setToken(String token) async {
    await _secureStorage.write(key: _keyToken, value: token);
  }

  Future<String?> getToken() async {
    return await _secureStorage.read(key: _keyToken);
  }

  Future<void> setRefreshToken(String token) async {
    await _secureStorage.write(key: _keyRefreshToken, value: token);
  }

  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: _keyRefreshToken);
  }

  Future<void> clearTokens() async {
    await _secureStorage.delete(key: _keyToken);
    await _secureStorage.delete(key: _keyRefreshToken);
  }

  // 用户信息管理
  Future<void> setUserId(String userId) async {
    await _secureStorage.write(key: _keyUserId, value: userId);
  }

  Future<String?> getUserId() async {
    return await _secureStorage.read(key: _keyUserId);
  }

  Future<void> setUsername(String username) async {
    await _preferences.setString(_keyUsername, username);
  }

  String? getUsername() {
    return _preferences.getString(_keyUsername);
  }

  // 应用程序设置
  Future<void> setHasSeenWelcome(bool hasSeen) async {
    await _preferences.setBool(_keyHasSeenWelcome, hasSeen);
  }

  bool getHasSeenWelcome() {
    return _preferences.getBool(_keyHasSeenWelcome) ?? false;
  }

  Future<void> setAppTheme(String theme) async {
    await _preferences.setString(_keyAppTheme, theme);
  }

  String getAppTheme() {
    return _preferences.getString(_keyAppTheme) ?? 'system';
  }

  Future<void> setLanguage(String language) async {
    await _preferences.setString(_keyLanguage, language);
  }

  String getLanguage() {
    return _preferences.getString(_keyLanguage) ?? 'zh_CN';
  }

  Future<void> setNotificationsEnabled(bool enabled) async {
    await _preferences.setBool(_keyNotificationsEnabled, enabled);
  }

  bool getNotificationsEnabled() {
    return _preferences.getBool(_keyNotificationsEnabled) ?? true;
  }

  // 清除所有数据
  Future<void> clearAll() async {
    await _preferences.clear();
    await _secureStorage.deleteAll();
  }
}

/// 偏好设置管理器Provider
final preferencesManagerProvider = Provider<PreferencesManager>((ref) {
  throw UnimplementedError('需要在ProviderScope中覆盖此Provider');
});

/// 初始化偏好设置管理器
Future<PreferencesManager> initPreferencesManager() async {
  final prefs = await SharedPreferences.getInstance();
  final secureStorage = FlutterSecureStorage();
  return PreferencesManager(prefs, secureStorage);
}
