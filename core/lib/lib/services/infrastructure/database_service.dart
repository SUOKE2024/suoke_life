import 'package:sqflite/sqflite.dart';

abstract class DatabaseService {
  Future<Database> get database;
  Future<void> createTables(Database db, int version);
} 