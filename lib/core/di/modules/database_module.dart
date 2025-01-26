import 'package:get_it/get_it.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../../services/infrastructure/database_service.dart';
import '../../services/infrastructure/database_service_impl.dart';

class DatabaseModule {
  Future<void> register(GetIt getIt) async {
    final database = await openDatabase(
      join(await getDatabasesPath(), 'suoke_life.db'),
      onCreate: (db, version) {
        db.execute(
          'CREATE TABLE chats(id INTEGER PRIMARY KEY, text TEXT, isUser INTEGER, timestamp INTEGER)',
        );
        db.execute(
          'CREATE TABLE personal_information(id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone_number TEXT, address TEXT)',
        );
        db.execute(
          'CREATE TABLE health_data(id INTEGER PRIMARY KEY, heart_rate REAL, sleep_patterns TEXT, medical_records TEXT)',
        );
        db.execute(
          'CREATE TABLE life_activity_data(id INTEGER PRIMARY KEY, daily_activities TEXT, location_history TEXT, task_completion TEXT)',
        );
      },
      version: 1,
    );
    getIt.registerSingleton<Database>(database);
  }
}

void registerDatabaseModule(GetIt getIt) {
  getIt.registerLazySingleton<DatabaseService>(() => DatabaseServiceImpl());
} 