import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';
import '../database/database_helper.dart';

class StorageService extends GetxService {
  late final SharedPreferences _prefs;
  late final Database _db;

  Future<StorageService> init() async {
    try {
      // 初始化 SharedPreferences
      _prefs = await SharedPreferences.getInstance();
      
      // 初始化数据库
      _db = await DatabaseHelper.instance.database;
      
      return this;
    } catch (e) {
      print('Error initializing storage service: $e');
      rethrow;
    }
  }

  // 本地存储
  Future<void> saveLocal(String key, dynamic value) async {
    try {
      if (value is String) {
        await _prefs.setString(key, value);
      } else if (value is int) {
        await _prefs.setInt(key, value);
      } else if (value is double) {
        await _prefs.setDouble(key, value);
      } else if (value is bool) {
        await _prefs.setBool(key, value);
      } else if (value is List<String>) {
        await _prefs.setStringList(key, value);
      } else {
        await _prefs.setString(key, value.toString());
      }
    } catch (e) {
      print('Error saving to local storage: $e');
      rethrow;
    }
  }

  Future<dynamic> getLocal(String key) async {
    try {
      return _prefs.get(key);
    } catch (e) {
      print('Error getting from local storage: $e');
      return null;
    }
  }

  Future<void> removeLocal(String key) async {
    try {
      await _prefs.remove(key);
    } catch (e) {
      print('Error removing from local storage: $e');
      rethrow;
    }
  }

  // 数据库存储
  Future<void> saveDB(String table, Map<String, dynamic> data) async {
    try {
      await _db.insert(
        table,
        data,
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    } catch (e) {
      print('Error saving to database: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> getDB(String table, String id) async {
    try {
      final List<Map<String, dynamic>> maps = await _db.query(
        table,
        where: 'id = ?',
        whereArgs: [id],
      );

      if (maps.isNotEmpty) {
        return maps.first;
      }
      return null;
    } catch (e) {
      print('Error getting from database: $e');
      return null;
    }
  }

  Future<List<Map<String, dynamic>>> getAllDB(String table) async {
    try {
      return await _db.query(table);
    } catch (e) {
      print('Error getting all from database: $e');
      return [];
    }
  }

  Future<void> removeDB(String table, String id) async {
    try {
      await _db.delete(
        table,
        where: 'id = ?',
        whereArgs: [id],
      );
    } catch (e) {
      print('Error removing from database: $e');
      rethrow;
    }
  }

  Future<void> clearDB(String table) async {
    try {
      await _db.delete(table);
    } catch (e) {
      print('Error clearing database table: $e');
      rethrow;
    }
  }
} 