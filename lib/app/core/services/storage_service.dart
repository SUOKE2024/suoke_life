import 'package:shared_preferences/shared_preferences.dart';
import 'package:get/get.dart';

class StorageService extends GetxService {
  late SharedPreferences _prefs;

  Future<StorageService> init() async {
    _prefs = await SharedPreferences.getInstance();
    return this;
  }

  // String 操作
  Future<bool> setString(String key, String value) async {
    return await _prefs.setString(key, value);
  }

  String? getString(String key) {
    return _prefs.getString(key);
  }

  // bool 操作
  Future<bool> setBool(String key, bool value) async {
    return await _prefs.setBool(key, value);
  }

  bool? getBool(String key) {
    return _prefs.getBool(key);
  }

  // int 操作
  Future<bool> setInt(String key, int value) async {
    return await _prefs.setInt(key, value);
  }

  int? getInt(String key) {
    return _prefs.getInt(key);
  }

  // double 操作
  Future<bool> setDouble(String key, double value) async {
    return await _prefs.setDouble(key, value);
  }

  double? getDouble(String key) {
    return _prefs.getDouble(key);
  }

  // List<String> 操作
  Future<bool> setStringList(String key, List<String> value) async {
    return await _prefs.setStringList(key, value);
  }

  List<String>? getStringList(String key) {
    return _prefs.getStringList(key);
  }

  // 删除指定key
  Future<bool> remove(String key) async {
    return await _prefs.remove(key);
  }

  // 清空所有数据
  Future<bool> clear() async {
    return await _prefs.clear();
  }

  // 获取所有key
  Set<String> getKeys() {
    return _prefs.getKeys();
  }

  // 判断是否存在某个key
  bool containsKey(String key) {
    return _prefs.containsKey(key);
  }
} 