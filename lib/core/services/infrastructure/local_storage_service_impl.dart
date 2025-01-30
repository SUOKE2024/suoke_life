import 'package:sqflite/sqflite.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/lib/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/lib/core/database/database_config.dart';
import 'package:suoke_life/lib/core/models/chat_message.dart';

class LocalStorageServiceImpl implements LocalStorageService {
  late SharedPreferences _prefs;
  late Database _database;
  bool _isInitialized = false;

  @override
  bool get isInitialized => _isInitialized;

  @override
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    _database = await DatabaseConfig().database;
    _isInitialized = true;
  }

  @override
  Future<void> insertChat(Map<String, dynamic> chat) async {
    await insert('chat_history', chat);
  }

  @override
  Future<int> insert(String table, Map<String, dynamic> values) async {
    return await _database.insert(table, values);
  }

  @override
  Future<List<Map<String, dynamic>>> query(String table,
      {String? where, List<dynamic>? whereArgs}) async {
    return await _database.query(table, where: where, whereArgs: whereArgs);
  }

  @override
  Future<int> update(String table, Map<String, dynamic> values,
      {String? where, List<dynamic>? whereArgs}) async {
    return await _database.update(table, values,
        where: where, whereArgs: whereArgs);
  }

  @override
  Future<int> delete(String table,
      {String? where, List<dynamic>? whereArgs}) async {
    return await _database.delete(table, where: where, whereArgs: whereArgs);
  }

  @override
  Future<List<Map<String, dynamic>>> getChatList() async {
    return await query('chat_history');
  }

  @override
  Future<void> clearChatHistory() async {
    await _database.delete('chat_history');
  }

  @override
  Future<SharedPreferences> get prefs async => _prefs;

  @override
  Future<Database> get database async => _database;

  @override
  Future<void> setIntValue(String key, int value) async {
    await _prefs.setInt(key, value);
  }

  @override
  Future<int?> getIntValue(String key) async {
    return _prefs.getInt(key);
  }

  @override
  Future<void> clearAll() async {
    await _prefs.clear();
  }

  @override
  Future<void> saveChatHistory(List<String> chatList) async {
    await _prefs.setStringList('chat_history', chatList);
  }

  @override
  Future<List<String>> getChatHistory() async {
    return _prefs.getStringList('chat_history') ?? [];
  }

  @override
  Future<String?> getStringValue(String key) async {
    return _prefs.getString(key);
  }

  @override
  Future<void> setStringValue(String key, String value) async {
    await _prefs.setString(key, value);
  }

  @override
  Future<String?> getString(String key) async {
    return _prefs.getString(key);
  }

  @override
  Future<void> setString(String key, String value) async {
    await _prefs.setString(key, value);
  }

  @override
  Future<void> saveChat(String message, bool isUser) async {
    final chat = {
      'message': message,
      'isUser': isUser ? 1 : 0,
      'timestamp': DateTime.now().millisecondsSinceEpoch
    };
    await insert('chat_history', chat);
  }

  @override
  Future<List<ChatMessage>> getChatMessageHistory() async {
    final messages = await query('chat_history');
    return messages.map((e) => ChatMessage.fromJson(e)).toList();
  }

  @override
  Future<void> remove(String key) async {
    await _prefs.remove(key);
  }

  @override
  Future<void> clear() async {
    await _prefs.clear();
  }
}
