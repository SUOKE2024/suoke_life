import 'package:sqflite/sqflite.dart';

abstract class DatabaseService {
  Future<Database> openDatabase();
  Future<void> closeDatabase();
  Future<void> clearDatabase();
  Future<List<Map<String, dynamic>>> query(String table, {String? where, List<dynamic>? whereArgs});
  Future<int> insert(String table, Map<String, dynamic> values);
  Future<int> update(String table, Map<String, dynamic> values, {String? where, List<dynamic>? whereArgs});
  Future<int> delete(String table, {String? where, List<dynamic>? whereArgs});
} 