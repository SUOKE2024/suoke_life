import 'package:shared_preferences/shared_preferences.dart';

abstract class StorageService {
  Future<void> init();
  Future<void> write(String key, dynamic value);
  Future<T?> read<T>(String key);
  Future<void> delete(String key);
  Future<void> clear();
}

@LazySingleton(as: StorageService)
class StorageServiceImpl implements StorageService {
  SharedPreferences? _prefs;

  @override
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  @override
  Future<void> write(String key, dynamic value) async {
    if (_prefs == null) await init();
    
    if (value is String) {
      await _prefs!.setString(key, value);
    } else if (value is int) {
      await _prefs!.setInt(key, value);
    } else if (value is bool) {
      await _prefs!.setBool(key, value);
    } else if (value is double) {
      await _prefs!.setDouble(key, value);
    } else if (value is List<String>) {
      await _prefs!.setStringList(key, value);
    }
  }

  @override
  Future<T?> read<T>(String key) async {
    if (_prefs == null) await init();
    return _prefs!.get(key) as T?;
  }

  @override
  Future<void> delete(String key) async {
    if (_prefs == null) await init();
    await _prefs!.remove(key);
  }

  @override
  Future<void> clear() async {
    if (_prefs == null) await init();
    await _prefs!.clear();
  }
} 