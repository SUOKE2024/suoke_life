import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/core/models/user.dart';
import 'package:suoke_life/core/repositories/user_repository.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class UserRepositoryImpl implements UserRepository {
  final DatabaseService _databaseService;

  UserRepositoryImpl(this._databaseService);

  @override
  Future<List<User>> getAllUsers() async {
    final result = await _databaseService.query('users');
    return result.map((e) => User.fromJson(e)).toList();
  }

  @override
  Future<User> getUser(int id) async {
    final result = await _databaseService.query('users', where: 'id = ?', whereArgs: [id]);
    if (result.isNotEmpty) {
      return User.fromJson(result.first);
    }
    throw Exception('User not found');
  }

  @override
  Future<User> addUser(User user) async {
    final id = await _databaseService.insert('users', user.toJson());
    return user.copyWith(id: id);
  }

  @override
  Future<User> updateUser(User user) async {
    await _databaseService.update('users', user.toJson(), where: 'id = ?', whereArgs: [user.id]);
    return user;
  }

  @override
  Future<void> deleteUser(int id) async {
    await _databaseService.delete('users', where: 'id = ?', whereArgs: [id]);
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
  Future<List<Map<String, dynamic>>> getChatList() async {
    final db = await _databaseService.openDatabase();
    final List<Map<String, dynamic>> maps = await db.query('chats');
    return maps;
  }
} 