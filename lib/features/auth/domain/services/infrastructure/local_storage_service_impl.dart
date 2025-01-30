import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/lib/core/services/infrastructure/local_storage_service.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:suoke_life/lib/core/services/infrastructure/database_service.dart';
import 'package:suoke_life/lib/core/config/database_config.dart';
import 'dart:convert';
import 'package:suoke_life/lib/core/models/chat_message.dart';

class LocalStorageServiceImpl implements LocalStorageService {
  final DatabaseService _databaseService;

  SharedPreferences? _prefs;
  Database? _database;
  static const String _chatHistoryKey = 'chat_history';

  LocalStorageServiceImpl(this._databaseService) {
    init();
  }

  @override
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    _database = await _databaseService.database;
  }

  @override
  Future<int> insert(String table, Map<String, dynamic> values) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    return await db.insert(table, values);
  }

  @override
  Future<List<Map<String, dynamic>>> query(String table,
      {String? where, List<dynamic>? whereArgs}) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    return await db.query(table, where: where, whereArgs: whereArgs);
  }

  @override
  Future<int> update(String table, Map<String, dynamic> values,
      {String? where, List<dynamic>? whereArgs}) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    return await db.update(table, values, where: where, whereArgs: whereArgs);
  }

  @override
  Future<int> delete(String table,
      {String? where, List<dynamic>? whereArgs}) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    return await db.delete(table, where: where, whereArgs: whereArgs);
  }

  @override
  Future<List<Map<String, dynamic>>> getChatList() async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    return await db.query('chats');
  }

  @override
  Future<void> clearChatHistory() async {
    final prefs = _prefs;
    await prefs?.remove('chat_history');
  }

  @override
  Future<SharedPreferences> get prefs async {
    if (_prefs == null) {
      throw Exception('SharedPreferences not initialized. Call init() first.');
    }
    return _prefs!;
  }

  @override
  Future<Database> get database async {
    if (_database == null) {
      throw Exception('Database not initialized. Call init() first.');
    }
    return _database!;
  }

  @override
  Future<void> setIntValue(String key, int value) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    await db.insert(
      'settings',
      {'key': key, 'value': value.toString()},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  @override
  Future<int?> getIntValue(String key) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    final List<Map<String, dynamic>> maps = await db.query(
      'settings',
      where: 'key = ?',
      whereArgs: [key],
    );
    if (maps.isNotEmpty) {
      return int.tryParse(maps.first['value'] as String? ?? '');
    }
    return null;
  }

  @override
  Future<void> setDoubleValue(String key, double value) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    await db.insert(
      'settings',
      {'key': key, 'value': value.toString()},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  @override
  Future<double?> getDoubleValue(String key) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    final List<Map<String, dynamic>> maps = await db.query(
      'settings',
      where: 'key = ?',
      whereArgs: [key],
    );
    if (maps.isNotEmpty) {
      return double.tryParse(maps.first['value'] as String? ?? '');
    }
    return null;
  }

  @override
  Future<void> setBoolValue(String key, bool value) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    await db.insert(
      'settings',
      {'key': key, 'value': value ? 'true' : 'false'},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  @override
  Future<bool?> getBoolValue(String key) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    final List<Map<String, dynamic>> maps = await db.query(
      'settings',
      where: 'key = ?',
      whereArgs: [key],
    );
    if (maps.isNotEmpty) {
      return (maps.first['value'] as String?) == 'true';
    }
    return null;
  }

  @override
  Future<void> setStringListValue(String key, List<String> value) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    await db.insert(
      'settings',
      {'key': key, 'value': value.join(',')},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  @override
  Future<List<String>> getStringListValue(String key) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    final List<Map<String, dynamic>> maps = await db.query(
      'settings',
      where: 'key = ?',
      whereArgs: [key],
    );
    if (maps.isNotEmpty) {
      final valueString = maps.first['value'] as String? ?? '';
      return valueString.split(',');
    }
    return [];
  }

  @override
  Future<void> removeValue(String key) async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    await db.delete(
      'settings',
      where: 'key = ?',
      whereArgs: [key],
    );
  }

  @override
  Future<void> clearAll() async {
    final db = _database;
    if (db == null) throw Exception('Database not initialized');
    await db.delete('settings');
    await db.delete('chats');
    final sharedPrefs = await prefs;
    await sharedPrefs.clear();
  }

  @override
  Future<void> saveChatHistory(List<String> chatList) async {
    final encodedList = jsonEncode(chatList);
    await _prefs?.setString(_chatHistoryKey, encodedList);
  }

  @override
  Future<List<String>> getChatHistory() async {
    final encodedList = _prefs?.getString(_chatHistoryKey);
    if (encodedList != null) {
      return List<String>.from(jsonDecode(encodedList));
    }
    return [];
  }

  @override
  Future<String?> getStringValue(String key) async {
    final sharedPrefs = await prefs;
    return sharedPrefs.getString(key);
  }

  @override
  Future<void> setStringValue(String key, String value) async {
    final sharedPrefs = await prefs;
    await sharedPrefs.setString(key, value);
  }

  @override
  Future<String?> getString(String key) async {
    final sharedPrefs = await prefs;
    return sharedPrefs.getString(key);
  }

  @override
  Future<void> setString(String key, String value) async {
    final sharedPrefs = await prefs;
    await sharedPrefs.setString(key, value);
  }

  @override
  Future<void> saveChat(String message, bool isUser) async {
    final prefs = _prefs;
    List<String> chatHistory = prefs?.getStringList('chat_history') ?? [];
    chatHistory.add('$message|$isUser');
    await prefs?.setStringList('chat_history', chatHistory);
  }

  @override
  Future<List<ChatMessage>> getChatMessages() async {
    final prefs = _prefs;
    List<String> chatHistory = prefs?.getStringList('chat_history') ?? [];
    return chatHistory.map((entry) {
      final parts = entry.split('|');
      return ChatMessage(text: parts[0], isUser: parts[1] == 'true');
    }).toList();
  }
}
