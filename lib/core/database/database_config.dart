import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:suoke_life/core/config/app_config.dart';

class DatabaseConfig {
  static String get databaseName => AppConfig.dbName;
  static int get databaseVersion => AppConfig.dbVersion;
  static bool get databaseEncryption => AppConfig.dbEncryption;
  static String get databasePassword => AppConfig.dbPassword;
  static String get mysqlHost => AppConfig.mysqlHost;
  static int get mysqlPort => AppConfig.mysqlPort;
  static String get mysqlUser => AppConfig.mysqlUser;
  static String get mysqlDatabase => AppConfig.mysqlDatabase;

  static Future<String> getDatabasePath() async {
    final directory = await getApplicationDocumentsDirectory();
    return join(directory.path, databaseName);
  }

  static Future<void> onCreate(Database db, int version) async {
    await db.execute(
      'CREATE TABLE IF NOT EXISTS user_data(key TEXT PRIMARY KEY, value TEXT)',
    );
  }
} 