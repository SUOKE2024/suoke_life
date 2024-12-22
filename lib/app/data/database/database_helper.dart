import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  static Database? _database;

  factory DatabaseHelper() => _instance;

  DatabaseHelper._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    String path = join(await getDatabasesPath(), 'suoke.db');
    return await openDatabase(
      path,
      version: 1,
      onCreate: (Database db, int version) async {
        await db.execute('''
          CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            conversation_id INTEGER,
            content TEXT,
            type TEXT,
            sender_id TEXT,
            sender_avatar TEXT,
            created_at TEXT,
            is_read INTEGER,
            duration INTEGER
          )
        ''');

        await db.execute('''
          CREATE TABLE conversations (
            id INTEGER PRIMARY KEY,
            title TEXT,
            model TEXT,
            avatar TEXT,
            created_at TEXT,
            updated_at TEXT
          )
        ''');
      },
    );
  }
} 