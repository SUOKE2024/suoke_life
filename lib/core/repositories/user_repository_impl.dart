import 'package:suoke_life/core/models/user.dart';
import 'package:suoke_life/core/repositories/user_repository.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/services/infrastructure/local_storage_service.dart';
import '../../domain/models/chat_message.dart';

class UserRepositoryImpl implements UserRepository {
  final DatabaseService _databaseService;
  final LocalStorageService _localStorageService;
  static const String _userTable = 'users';

  UserRepositoryImpl(this._databaseService, this._localStorageService);

  @override
  Future<User> addUser(User user) async {
    final db = await _databaseService.database;
    final id = await db.insert('users', user.toMap());
    return user.copyWith(id: id);
  }

  @override
  Future<User?> getUserById(int id) async {
    final db = await _databaseService.database;
    final maps = await db.query(
      'users',
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isNotEmpty) {
      return User.fromMap(maps.first);
    }
    return null;
  }

  @override
  Future<List<User>> getAllUsers() async {
    final db = await _databaseService.database;
    final maps = await db.query('users');
    return maps.map((map) => User.fromMap(map)).toList();
  }

  @override
  Future<User> updateUser(User user) async {
    final db = await _databaseService.database;
    await db.update(
      'users',
      user.toMap(),
      where: 'id = ?',
      whereArgs: [user.id],
    );
    return user;
  }

  @override
  Future<void> deleteUser(int id) async {
    final db = await _databaseService.database;
    await db.delete(
      'users',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  @override
  Future<User?> getUserByEmail(String email) async {
    final db = await _databaseService.database;
    List<Map<String, dynamic>> maps = await db.query(
      _userTable,
      where: 'email = ?',
      whereArgs: [email],
    );
    if (maps.isNotEmpty) {
      return User.fromMap(maps.first);
    }
    return null;
  }

  @override
  Future<void> setString(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(key, value);
  }

  @override
  Future<String?> getStringValue(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(key);
  }

  @override
  Future<List<ChatMessage>> getChatHistory() async {
    try {
      final chatList = await _localStorageService.getChatHistory();
      return chatList.map((message) => ChatMessage(text: message)).toList();
    } catch (e) {
      print('Error getting chat history: $e');
      return [];
    }
  }

  @override
  Future<void> saveChatHistory(List<ChatMessage> chatHistory) async {
    try {
      final chatStringList = chatHistory.map((chat) => chat.text).toList();
      await _localStorageService.saveChatHistory(chatStringList);
    } catch (e) {
      print('Error saving chat history: $e');
    }
  }
}
