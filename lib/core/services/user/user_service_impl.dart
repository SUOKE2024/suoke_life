import '../user/user_service.dart'; // 确保路径正确
import 'package:suoke_life/lib/core/models/user.dart'; // 确保导入 User 模型
import 'package:sqflite/sqflite.dart'; // 确保导入 sqflite 库

class UserServiceImpl implements UserService {
  final Database database;

  UserServiceImpl(this.database);

  @override
  Future<User?> getUser(String userId) async {
    final List<Map<String, dynamic>> maps = await database.query(
      'users',
      where: 'id = ?',
      whereArgs: [userId],
    );

    if (maps.isNotEmpty) {
      return User.fromMap(maps.first);
    }
    return null;
  }

  @override
  Future<void> saveUser(User user) async {
    await database.insert(
      'users',
      user.toMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }
} 