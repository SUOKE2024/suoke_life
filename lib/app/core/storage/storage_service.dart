import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static late SharedPreferences _prefs;
  
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  Future<void> clear() async {
    await _prefs.clear();
  }

  Future<void> saveSyncLog(String log) async {
    await _prefs.setString('sync_log', log);
  }

  Future<String?> getSyncLog() async {
    return _prefs.getString('sync_log');
  }

  Future<void> saveData(String key, String value) async {
    await _prefs.setString(key, value);
  }

  Future<String?> getData(String key) async {
    return _prefs.getString(key);
  }
} 