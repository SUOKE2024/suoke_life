import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService extends GetxService {
  late SharedPreferences _prefs;
  
  Future<StorageService> init() async {
    try {
      _prefs = await SharedPreferences.getInstance();
    } catch (e) {
      // 在测试环境中处理异常
      print('Warning: SharedPreferences initialization failed in test environment');
      _prefs = await SharedPreferences.getInstance();
    }
    return this;
  }

  Future<bool> saveLocal(String key, dynamic value) async {
    if (value is String) {
      return await _prefs.setString(key, value);
    } else if (value is int) {
      return await _prefs.setInt(key, value);
    } else if (value is double) {
      return await _prefs.setDouble(key, value);
    } else if (value is bool) {
      return await _prefs.setBool(key, value);
    } else if (value is List<String>) {
      return await _prefs.setStringList(key, value);
    }
    return false;
  }

  dynamic getLocal(String key) {
    return _prefs.get(key);
  }

  Future<bool> removeLocal(String key) async {
    return await _prefs.remove(key);
  }

  Future<bool> clearLocal() async {
    return await _prefs.clear();
  }

  // 数据库操作方法
  Future<List<Map<String, dynamic>>> getAllDB(String table) async {
    final data = await getLocal(table);
    if (data == null) return [];
    return List<Map<String, dynamic>>.from(data as List);
  }

  Future<Map<String, dynamic>?> getDB(String table, String id) async {
    final allData = await getAllDB(table);
    return allData.firstWhere((item) => item['id'] == id, orElse: () => {});
  }

  Future<void> saveDB(String table, Map<String, dynamic> data) async {
    final allData = await getAllDB(table);
    final index = allData.indexWhere((item) => item['id'] == data['id']);
    if (index >= 0) {
      allData[index] = data;
    } else {
      allData.add(data);
    }
    await saveLocal(table, allData);
  }

  Future<void> removeDB(String table, String id) async {
    final allData = await getAllDB(table);
    allData.removeWhere((item) => item['id'] == id);
    await saveLocal(table, allData);
  }

  Future<void> saveSyncLog(String log) async {
    await saveLocal('sync_log', log);
  }

  Future<String?> getSyncLog() async {
    final value = await getLocal('sync_log');
    return value as String?;
  }

  Future<void> saveData(String key, String value) async {
    await saveLocal(key, value);
  }

  Future<String?> getData(String key) async {
    final value = await getLocal(key);
    return value as String?;
  }

  Future<void> saveRemote(String key, dynamic value) async {
    // TODO: 实现远程存储逻辑
    await saveLocal(key, value); // 临时使用本地存储
  }
} 