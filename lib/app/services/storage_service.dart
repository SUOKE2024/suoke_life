import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService extends GetxService {
  static StorageService get to => Get.find();
  late final SharedPreferences _prefs;

  Future<StorageService> init() async {
    _prefs = await SharedPreferences.getInstance();
    print('StorageService initialized');
    return this;
  }

  // 存储方法
  Future<bool> setString(String key, String value) async {
    return await _prefs.setString(key, value);
  }

  Future<bool> setInt(String key, int value) async {
    return await _prefs.setInt(key, value);
  }

  Future<bool> setBool(String key, bool value) async {
    return await _prefs.setBool(key, value);
  }

  Future<bool> setDouble(String key, double value) async {
    return await _prefs.setDouble(key, value);
  }

  Future<bool> setStringList(String key, List<String> value) async {
    return await _prefs.setStringList(key, value);
  }

  // 读取方法
  String? getString(String key) {
    return _prefs.getString(key);
  }

  int? getInt(String key) {
    return _prefs.getInt(key);
  }

  bool? getBool(String key) {
    return _prefs.getBool(key);
  }

  double? getDouble(String key) {
    return _prefs.getDouble(key);
  }

  List<String>? getStringList(String key) {
    return _prefs.getStringList(key);
  }

  // 删除方法
  Future<bool> remove(String key) async {
    return await _prefs.remove(key);
  }

  // 清空所有数据
  Future<bool> clear() async {
    return await _prefs.clear();
  }

  // 检查是否包含某个key
  bool hasKey(String key) {
    return _prefs.containsKey(key);
  }

  // 获取所有key
  Set<String> getKeys() {
    return _prefs.getKeys();
  }

  // 常用的存储键
  static const String keyToken = 'token';
  static const String keyUserId = 'userId';
  static const String keyUserInfo = 'userInfo';
  static const String keyLanguage = 'language';
  static const String keyTheme = 'theme';
  static const String keyFirstTime = 'firstTime';
  static const String keyLastLoginTime = 'lastLoginTime';
} 