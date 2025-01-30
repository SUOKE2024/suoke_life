import 'package:sqflite/sqflite.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/lib/core/models/chat_message.dart';

abstract class LocalStorageService {
  Future<void> init();
  Future<int> insert(String table, Map<String, dynamic> values);
  Future<List<Map<String, dynamic>>> query(String table,
      {String? where, List<dynamic>? whereArgs});
  Future<int> update(String table, Map<String, dynamic> values,
      {String? where, List<dynamic>? whereArgs});
  Future<int> delete(String table, {String? where, List<dynamic>? whereArgs});
  Future<List<Map<String, dynamic>>> getChatList();
  Future<void> clearChatHistory();
  Future<SharedPreferences> get prefs;
  Future<Database> get database;
  Future<void> setIntValue(String key, int value);
  Future<int?> getIntValue(String key);
  Future<void> clearAll();
  Future<void> saveChatHistory(List<String> chatList);
  Future<List<String>> getChatHistory();
  Future<String?> getStringValue(String key);
  Future<void> setStringValue(String key, String value);
  Future<String?> getString(String key);
  Future<void> setString(String key, String value);
  Future<void> saveChat(String message, bool isUser);
  Future<List<ChatMessage>> getChatMessages();
}
