import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/database/database_config.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart';
import 'package:encrypt/encrypt.dart';

class DatabaseServiceImpl implements DatabaseService {
  Database? _database;
  final Key _key = Key.fromLength(32);
  final IV _iv = IV.fromLength(16);
  late final Encrypter _encrypter;

  DatabaseServiceImpl() {
    _encrypter = Encrypter(AES(_key));
  }

  @override
  Future<Database> get database async {
    if (_database != null) {
      return _database!;
    }
    await _init();
    return _database!;
  }

  Future<void> _init() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, 'app_database.db');

    _database = await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            avatar TEXT
          )
        ''');
        await db.execute('''
          CREATE TABLE chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER,
            message TEXT,
            timestamp INTEGER
          )
        ''');
        // Add more table creation queries here if needed
      },
    );
  }

  @override
  Future<void> closeDatabase() async {
    await _database?.close();
    _database = null;
  }

  @override
  Future<void> clearDatabase() async {
    if (_database == null) return;
    final tables = ['chats', 'users'];
    for (final table in tables) {
      await _database?.delete(table);
    }
  }

  @override
  Future<List<Map<String, dynamic>>> query(String table,
      {String? where, List<dynamic>? whereArgs}) async {
    final db = await database;
    return await db.query(table, where: where, whereArgs: whereArgs);
  }

  @override
  Future<int> insert(String table, Map<String, dynamic> values) async {
    final db = await database;
    return await db.insert(table, values);
  }

  @override
  Future<int> update(String table, Map<String, dynamic> values,
      {String? where, List<dynamic>? whereArgs}) async {
    final db = await database;
    return await db.update(table, values, where: where, whereArgs: whereArgs);
  }

  @override
  Future<int> delete(String table,
      {String? where, List<dynamic>? whereArgs}) async {
    final db = await database;
    return await db.delete(table, where: where, whereArgs: whereArgs);
  }

  Map<String, dynamic> _encryptData(Map<String, dynamic> data) {
    final encryptedData = <String, dynamic>{};
    data.forEach((key, value) {
      if (value is String) {
        final encrypted = _encrypter.encrypt(value, iv: _iv);
        encryptedData[key] = encrypted.base64;
      } else {
        encryptedData[key] = value;
      }
    });
    return encryptedData;
  }

  Map<String, dynamic> _decryptData(Map<String, dynamic> data) {
    final decryptedData = <String, dynamic>{};
    data.forEach((key, value) {
      if (value is String) {
        try {
          final decrypted = _encrypter.decrypt64(value, iv: _iv);
          decryptedData[key] = decrypted;
        } catch (e) {
          decryptedData[key] = value;
        }
      } else {
        decryptedData[key] = value;
      }
    });
    return decryptedData;
  }

  @override
  Future<void> initializeDatabase() async {
    // 空实现，如果接口 `DatabaseService` 中 `initializeDatabase` 方法不再需要，
    // 也可以直接从接口中移除该方法定义。
    print('initializeDatabase called (empty implementation)');
  }
}
