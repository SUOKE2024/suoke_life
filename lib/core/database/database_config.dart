/// 数据库配置类，用于配置本地 sqflite 数据库
///
/// 本文件主要负责 sqflite 数据库的配置，例如数据库名称、版本、路径等。
/// MySQL 相关的配置 (例如 host, port, user 等) 暂时保留在此文件中，
/// 但请注意，当前架构主要使用 sqflite 本地存储，Redis 用于缓存等策略。
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/models/chat_message.dart';

class DatabaseConfig {
  /// 本地数据库名称 (从 AppConfig 中获取)
  static String get databaseName => AppConfig.dbName;

  /// 本地数据库版本 (从 AppConfig 中获取)
  static int get databaseVersion => AppConfig.dbVersion;

  /// 本地数据库是否加密 (从 AppConfig 中获取，但 sqflite 默认不加密，需要额外处理)
  static bool get databaseEncryption => AppConfig.dbEncryption;

  /// 本地数据库密码 (从 AppConfig 中获取，但 sqflite 默认不加密，需要额外处理)
  static String get databasePassword => AppConfig.dbPassword;
  // /// MySQL 数据库 Host (从 AppConfig 中获取，远程数据库配置，当前主要使用 sqflite 本地存储)
  // static String get mysqlHost => AppConfig.mysqlHost;
  // /// MySQL 数据库 Port (从 AppConfig 中获取，远程数据库配置，当前主要使用 sqflite 本地存储)
  // static int get mysqlPort => AppConfig.mysqlPort;
  // /// MySQL 数据库 User (从 AppConfig 中获取，远程数据库配置，当前主要使用 sqflite 本地存储)
  // static String get mysqlUser => AppConfig.mysqlUser;
  // /// MySQL 数据库名 (从 AppConfig 中获取，远程数据库配置，当前主要使用 sqflite 本地存储)
  // static String get mysqlDatabase => AppConfig.mysqlDatabase;

  /// 获取本地数据库文件路径
  static Future<String> getDatabasePath() async {
    final directory = await getApplicationDocumentsDirectory();
    return join(directory.path, databaseName);
  }

  static Future<void> onCreate(Database db, int version) async {
    await db.execute(
      'CREATE TABLE IF NOT EXISTS user_data(key TEXT PRIMARY KEY, value TEXT)',
    );
  }

  static Database? _database;

  /// 获取 sqflite 数据库实例 (单例模式)
  static Future<Database> getDatabase() async {
    if (_database != null) {
      return _database!;
    }
    final path = await getDatabasePath();
    _database = await openDatabase(
      path,
      version: databaseVersion,
      onCreate: onCreate,
    );
    return _database!;
  }
}

class LocalStorageServiceImpl implements LocalStorageService {
  late final Future<SharedPreferences> _prefs = SharedPreferences.getInstance();

  @override
  Future<void> saveChat(String message, bool isUser) async {
    final prefs = await _prefs;
    // 保存聊天记录的逻辑
    List<String> chatHistory = prefs.getStringList('chat_history') ?? [];
    chatHistory.add('$message|$isUser');
    await prefs.setStringList('chat_history', chatHistory);
  }

  @override
  Future<List<ChatMessage>> getChatHistory() async {
    final prefs = await _prefs;
    // 获取聊天记录的逻辑
    List<String> chatHistory = prefs.getStringList('chat_history') ?? [];
    return chatHistory.map((entry) {
      final parts = entry.split('|');
      return ChatMessage(text: parts[0], isUser: parts[1] == 'true');
    }).toList();
  }

  @override
  Future<void> clearChatHistory() async {
    final prefs = await _prefs;
    await prefs.remove('chat_history');
  }

  // 实现接口中定义的其他方法（如果有）
}
