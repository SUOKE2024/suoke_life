/// 数据库配置类，用于配置本地 sqflite 数据库
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/lib/core/config/app_config.dart';
import 'package:suoke_life/lib/core/models/chat_message.dart';

class DatabaseConfig {
  late SharedPreferences _prefs;
  late Database _database;

  /// 本地数据库名称 (从 AppConfig 中获取)
  static String get databaseName => AppConfig.dbName;

  /// 本地数据库版本 (从 AppConfig 中获取)
  static int get databaseVersion => AppConfig.dbVersion;

  /// 获取本地数据库文件路径
  Future<String> _getDatabasePath() async {
    final directory = await getApplicationDocumentsDirectory();
    return join(directory.path, databaseName);
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute(
      'CREATE TABLE IF NOT EXISTS user_data(key TEXT PRIMARY KEY, value TEXT)',
    );
    await db.execute(
        'CREATE TABLE IF NOT EXISTS chat_history(id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, is_user INTEGER, timestamp INTEGER)');
    await db.execute(
        'CREATE TABLE IF NOT EXISTS life_records(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, timestamp TEXT)');
    await db.execute(
        'CREATE TABLE IF NOT EXISTS health_data(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, type TEXT, value REAL, unit TEXT, time INTEGER)');
    await db.execute(
        'CREATE TABLE IF NOT EXISTS life_activity_data(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, type TEXT, value REAL, unit TEXT, time INTEGER)');
  }

  Future<Database> _getDatabase() async {
    final path = await _getDatabasePath();
    return await openDatabase(
      path,
      version: databaseVersion,
      onCreate: _onCreate,
    );
  }

  /// 初始化数据库和SharedPreferences
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    _database = await _getDatabase();
  }

  /// 获取数据库实例
  @override
  Future<Database> get database async => _database;

  @override
  Future<SharedPreferences> get prefs async => _prefs;
}
