import 'package:core/services/infrastructure/database_service.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class DatabaseServiceImpl implements DatabaseService {
  static const _databaseName = "suoke_life.db";
  static const _databaseVersion = 1;

  Database? _database;

  @override
  Future<Database> get database async {
    if (_database != null) return _database!;

    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, _databaseName);

    return await openDatabase(
      path,
      version: _databaseVersion,
      onCreate: createTables,
    );
  }

  @override
  Future<void> createTables(Database db, int version) async {
    await db.execute('''
      CREATE TABLE user_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        email TEXT,
        phone_number TEXT,
        address TEXT,
        health_data TEXT,
        life_activity_data TEXT
      )
    ''');
  }
} 