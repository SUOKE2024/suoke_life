import 'package:injectable/injectable.dart';
import '../database_service.dart';
import '../models/user.dart';
import 'base_repository.dart';

@singleton
class UserRepository extends BaseRepository {
  UserRepository(DatabaseService db) : super(db);

  Future<User?> getUserById(String id) async {
    final results = await query(
      'users',
      where: 'id = ?',
      whereArgs: [id],
    );
    
    if (results.isEmpty) return null;
    return User.fromJson(results.first);
  }

  Future<List<User>> getAllUsers() async {
    final results = await query('users');
    return results.map((json) => User.fromJson(json)).toList();
  }

  Future<void> createUser(User user) async {
    await insert('users', user.toJson());
  }

  Future<void> updateUser(User user) async {
    await update(
      'users',
      user.toJson(),
      where: 'id = ?',
      whereArgs: [user.id],
    );
  }

  Future<void> deleteUser(String id) async {
    await delete(
      'users',
      where: 'id = ?',
      whereArgs: [id],
    );
  }
} 