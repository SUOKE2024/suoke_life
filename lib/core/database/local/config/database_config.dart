import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:logger/logger.dart';
import 'package:suoke_life/lib/core/config/app_config.dart';

class DatabaseConfig {
  static final DatabaseConfig instance = DatabaseConfig._internal();
  final Logger _logger = Logger();
  
  late SharedPreferences _prefs;
  Database? _database;
  bool _initialized = false;

  DatabaseConfig._internal();

  /// 本地数据库名称
  static String get databaseName => AppConfig.dbName;

  /// 本地数据库版本
  static int get databaseVersion => AppConfig.dbVersion;

  /// 获取本地数据库文件路径
  Future<String> _getDatabasePath() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      return join(directory.path, databaseName);
    } catch (e) {
      _logger.e('Error getting database path: $e');
      rethrow;
    }
  }

  /// 数据库创建回调
  Future<void> _onCreate(Database db, int version) async {
    try {
      _logger.i('Creating database tables for version $version');
      await db.transaction((txn) async {
        // 用户数据表
        await txn.execute('''
          CREATE TABLE IF NOT EXISTS user_data(
            key TEXT PRIMARY KEY,
            value TEXT,
            created_at INTEGER,
            updated_at INTEGER
          )
        ''');

        // 聊天历史表
        await txn.execute('''
          CREATE TABLE IF NOT EXISTS chat_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            is_user INTEGER,
            timestamp INTEGER,
            session_id TEXT,
            message_type TEXT
          )
        ''');

        // 生活记录表
        await txn.execute('''
          CREATE TABLE IF NOT EXISTS life_records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            timestamp TEXT,
            category TEXT,
            tags TEXT,
            location TEXT,
            user_id TEXT
          )
        ''');

        // 健康数据表
        await txn.execute('''
          CREATE TABLE IF NOT EXISTS health_data(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            type TEXT,
            value REAL,
            unit TEXT,
            time INTEGER,
            source TEXT,
            notes TEXT
          )
        ''');

        // 生活活动数据表
        await txn.execute('''
          CREATE TABLE IF NOT EXISTS life_activity_data(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            type TEXT,
            value REAL,
            unit TEXT,
            time INTEGER,
            duration INTEGER,
            location TEXT,
            notes TEXT
          )
        ''');

        // 创建索引
        await txn.execute('CREATE INDEX idx_chat_history_session ON chat_history(session_id)');
        await txn.execute('CREATE INDEX idx_life_records_user ON life_records(user_id)');
        await txn.execute('CREATE INDEX idx_health_data_user_type ON health_data(user_id, type)');
        await txn.execute('CREATE INDEX idx_life_activity_user_type ON life_activity_data(user_id, type)');
      });
      _logger.i('Database tables created successfully');
    } catch (e) {
      _logger.e('Error creating database tables: $e');
      rethrow;
    }
  }

  /// 数据库升级回调
  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    try {
      _logger.i('Upgrading database from version $oldVersion to $newVersion');
      // 在这里实现数据库升级逻辑
      if (oldVersion < 2) {
        // 版本1升级到版本2的逻辑
      }
    } catch (e) {
      _logger.e('Error upgrading database: $e');
      rethrow;
    }
  }

  /// 初始化数据库和SharedPreferences
  Future<void> init() async {
    if (_initialized) return;

    try {
      _logger.i('Initializing database configuration');
      _prefs = await SharedPreferences.getInstance();
      final path = await _getDatabasePath();
      _database = await openDatabase(
        path,
        version: databaseVersion,
        onCreate: _onCreate,
        onUpgrade: _onUpgrade,
      );
      _initialized = true;
      _logger.i('Database configuration initialized successfully');
    } catch (e) {
      _logger.e('Error initializing database configuration: $e');
      rethrow;
    }
  }

  /// 获取数据库实例
  Future<Database> get database async {
    if (!_initialized) await init();
    return _database!;
  }

  /// 获取SharedPreferences实例
  Future<SharedPreferences> get prefs async {
    if (!_initialized) await init();
    return _prefs;
  }

  /// 关闭数据库连接
  Future<void> close() async {
    try {
      if (_database != null) {
        await _database!.close();
        _database = null;
        _initialized = false;
        _logger.i('Database connection closed');
      }
    } catch (e) {
      _logger.e('Error closing database connection: $e');
      rethrow;
    }
  }
} 