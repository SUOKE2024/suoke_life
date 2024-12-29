import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../security/encryption_service.dart';

class DatabaseService {
  static Database? _db;
  final EncryptionService _encryption;
  
  DatabaseService(this._encryption);

  Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDatabase();
    return _db!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'suoke.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDb,
      onUpgrade: _upgradeDb,
    );
  }

  Future<void> _createDb(Database db, int version) async {
    // 用户数据表 (加密存储)
    await db.execute('''
      CREATE TABLE users(
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        encrypted_data TEXT,
        created_at INTEGER,
        updated_at INTEGER
      )
    ''');

    // 健康记录表 (加密存储)
    await db.execute('''
      CREATE TABLE health_records(
        id TEXT PRIMARY KEY,
        user_id TEXT,
        type TEXT,
        encrypted_data TEXT,
        created_at INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
      )
    ''');

    // 本地缓存表
    await db.execute('''
      CREATE TABLE cache(
        key TEXT PRIMARY KEY,
        value TEXT,
        expire_at INTEGER
      )
    ''');
  }

  Future<void> _upgradeDb(Database db, int oldVersion, int newVersion) async {
    // 数据库升级逻辑
  }

  // 加密存储用户数据
  Future<void> saveUserData(String userId, Map<String, dynamic> data) async {
    final db = await database;
    final encryptedData = await _encryption.encrypt(data);
    
    await db.insert(
      'users',
      {
        'id': userId,
        'encrypted_data': encryptedData,
        'updated_at': DateTime.now().millisecondsSinceEpoch,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  // 读取用户数据
  Future<Map<String, dynamic>?> getUserData(String userId) async {
    final db = await database;
    final result = await db.query(
      'users',
      where: 'id = ?',
      whereArgs: [userId],
    );

    if (result.isEmpty) return null;

    final encryptedData = result.first['encrypted_data'] as String;
    return await _encryption.decrypt(encryptedData);
  }
} 