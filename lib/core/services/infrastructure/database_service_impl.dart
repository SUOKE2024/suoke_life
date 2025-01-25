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
    _database = await openDatabase();
    return _database!;
  }

  @override
  Future<Database> getDatabaseInstance() async {
    if (_database != null) {
      return _database!;
    }
    _database = await openDatabase();
    return _database!;
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        address TEXT,
        settings TEXT
      )
    ''');
    await db.execute('''
      CREATE TABLE health_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        type TEXT,
        value TEXT,
        unit TEXT,
        timestamp INTEGER
      )
    ''');
    await db.execute('''
      CREATE TABLE life_activity_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        activity_type TEXT,
        details TEXT,
        start_time INTEGER,
        end_time INTEGER
      )
    ''');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // 执行数据库升级操作
    }
  }

  @override
  Future<void> closeDatabase() async {
    await _database?.close();
    _database = null;
  }

  @override
  Future<void> clearDatabase() async {
    final databasePath = await getDatabasesPath();
    final path = join(databasePath, DatabaseConfig.databaseName);
    await deleteDatabase(path);
    _database = null;
  }

  @override
  Future<List<Map<String, dynamic>>> query(String table, {String? where, List<dynamic>? whereArgs}) async {
    final db = await getDatabaseInstance();
    return await db.query(table, where: where, whereArgs: whereArgs);
  }

  @override
  Future<int> insert(String table, Map<String, dynamic> data) async {
    final db = await getDatabaseInstance();
    final encryptedData = _encryptData(data);
    return await db.insert(table, encryptedData);
  }

  @override
  Future<int> update(String table, Map<String, dynamic> data, {String? where, List<dynamic>? whereArgs}) async {
    final db = await getDatabaseInstance();
    final encryptedData = _encryptData(data);
    return await db.update(table, encryptedData, where: where, whereArgs: whereArgs);
  }

  @override
  Future<int> delete(String table, {String? where, List<dynamic>? whereArgs}) async {
    final db = await getDatabaseInstance();
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
} 