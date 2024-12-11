/// SharedPreferences存储提供者
class SharedPreferencesProvider implements StorageProvider {
  late final SharedPreferences _prefs;
  
  Future<void> initialize() async {
    _prefs = await SharedPreferences.getInstance();
  }

  @override
  Future<Map<String, dynamic>?> read(String key) async {
    final data = _prefs.getString(key);
    if (data == null) return null;
    return jsonDecode(data) as Map<String, dynamic>;
  }

  @override
  Future<void> write(String key, Map<String, dynamic> value) async {
    await _prefs.setString(key, jsonEncode(value));
  }

  @override
  Future<void> delete(String key) async {
    await _prefs.remove(key);
  }

  @override
  Future<void> clear() async {
    await _prefs.clear();
  }

  @override
  Future<Set<String>> getKeys() async {
    return _prefs.getKeys();
  }
} 