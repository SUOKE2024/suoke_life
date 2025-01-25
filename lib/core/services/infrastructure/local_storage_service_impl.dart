import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class LocalStorageServiceImpl implements LocalStorageService {
  SharedPreferences? _prefs;

  Future<SharedPreferences> get _instance async {
    if (_prefs != null) {
      return _prefs!;
    }
    _prefs = await SharedPreferences.getInstance();
    return _prefs!;
  }

  @override
  Future<String?> getString(String key) async {
    final prefs = await _instance;
    return prefs.getString(key);
  }

  @override
  Future<void> setString(String key, String value) async {
    final prefs = await _instance;
    await prefs.setString(key, value);
  }

  @override
  Future<bool> getBool(String key) async {
    final prefs = await _instance;
    return prefs.getBool(key) ?? false;
  }

  @override
  Future<void> setBool(String key, bool value) async {
    final prefs = await _instance;
    await prefs.setBool(key, value);
  }

  @override
  Future<int> getInt(String key) async {
    final prefs = await _instance;
    return prefs.getInt(key) ?? 0;
  }

  @override
  Future<void> setInt(String key, int value) async {
    final prefs = await _instance;
    await prefs.setInt(key, value);
  }

  @override
  Future<double> getDouble(String key) async {
    final prefs = await _instance;
    return prefs.getDouble(key) ?? 0.0;
  }

  @override
  Future<void> setDouble(String key, double value) async {
    final prefs = await _instance;
    await prefs.setDouble(key, value);
  }

  @override
  Future<List<String>> getStringList(String key) async {
    final prefs = await _instance;
    return prefs.getStringList(key) ?? [];
  }

  @override
  Future<void> setStringList(String key, List<String> value) async {
    final prefs = await _instance;
    await prefs.setStringList(key, value);
  }

  @override
  Future<void> remove(String key) async {
    final prefs = await _instance;
    await prefs.remove(key);
  }

  @override
  Future<void> clear() async {
    final prefs = await _instance;
    await prefs.clear();
  }

  @override
  Future<void> saveChat(String text, bool isUser) async {
    final prefs = await _instance;
    final chatList = prefs.getStringList('chat_history') ?? [];
    final chat = '{"text": "$text", "isUser": $isUser}';
    chatList.add(chat);
    await prefs.setStringList('chat_history', chatList);
  }

  @override
  Future<List<Map<String, dynamic>>> getChats() async {
    final prefs = await _instance;
    final chatList = prefs.getStringList('chat_history') ?? [];
    return chatList.map((e) {
      final text = e.substring(e.indexOf('text": "') + 8, e.indexOf('", "isUser"'));
      final isUser = e.substring(e.indexOf('isUser": ') + 8, e.indexOf('}')).toLowerCase() == 'true';
      return {'text': text, 'isUser': isUser};
    }).toList();
  }

  @override
  Future<void> clearChatHistory() async {
    final prefs = await _instance;
    await prefs.remove('chat_history');
  }

  @override
  Future<Database> get database async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, 'suoke_life_database.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (Database db, int version) async {
        await db.execute('''
          CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone_number TEXT,
            profile_image_url TEXT
          )
        ''');
        await db.execute('''
          CREATE TABLE health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            value REAL,
            unit TEXT,
            timestamp INTEGER
          )
        ''');
        await db.execute('''
          CREATE TABLE life_activity_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type TEXT,
            details TEXT,
            timestamp INTEGER
          )
        ''');
      },
    );
  }
} 