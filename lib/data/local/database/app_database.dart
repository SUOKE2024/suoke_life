import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class AppDatabase {
  static Database? _db;
  
  static Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await initDB();
    return _db!;
  }

  static Future<Database> initDB() async {
    String path = join(await getDatabasesPath(), 'suoke_life.db');
    
    return await openDatabase(
      path,
      version: 1,
      onCreate: (Database db, int version) async {
        // 个人健康记录
        await db.execute('''
          CREATE TABLE health_records (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            value REAL,
            timestamp INTEGER,
            notes TEXT,
            metadata TEXT
          )
        ''');

        // 生活习惯数据
        await db.execute('''
          CREATE TABLE lifestyle_records (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            content TEXT,
            timestamp INTEGER,
            tags TEXT
          )
        ''');

        // 用药记录
        await db.execute('''
          CREATE TABLE medication_records (
            id TEXT PRIMARY KEY,
            medicine_name TEXT NOT NULL,
            dosage TEXT,
            time INTEGER,
            notes TEXT
          )
        ''');

        // 情绪日记
        await db.execute('''
          CREATE TABLE mood_diary (
            id TEXT PRIMARY KEY,
            mood_level INTEGER,
            stress_level INTEGER,
            notes TEXT,
            timestamp INTEGER,
            tags TEXT
          )
        ''');

        // 用户设置
        await db.execute('''
          CREATE TABLE user_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            category TEXT,
            last_updated INTEGER
          )
        ''');
      },
    );
  }
} 