import 'dart:convert';
import 'package:injectable/injectable.dart';
import 'package:sqflite/sqflite.dart';
import '../logger/app_logger.dart';

@singleton
class CacheService {
  final Database _db;
  final AppLogger _logger;

  CacheService(this._db, this._logger);

  Future<void> set(String key, dynamic value, {Duration? ttl}) async {
    try {
      final expiryTime = ttl != null 
          ? DateTime.now().add(ttl).millisecondsSinceEpoch 
          : null;

      await _db.insert(
        'cache',
        {
          'key': key,
          'value': jsonEncode(value),
          'expiry': expiryTime,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    } catch (e, stack) {
      _logger.error('Error setting cache', e, stack);
      rethrow;
    }
  }

  Future<T?> get<T>(String key) async {
    try {
      final result = await _db.query(
        'cache',
        where: 'key = ?',
        whereArgs: [key],
      );

      if (result.isEmpty) return null;

      final row = result.first;
      final expiry = row['expiry'] as int?;
      
      if (expiry != null && expiry < DateTime.now().millisecondsSinceEpoch) {
        await remove(key);
        return null;
      }

      final value = jsonDecode(row['value'] as String);
      return value as T;
    } catch (e, stack) {
      _logger.error('Error getting cache', e, stack);
      return null;
    }
  }

  Future<void> remove(String key) async {
    try {
      await _db.delete(
        'cache',
        where: 'key = ?',
        whereArgs: [key],
      );
    } catch (e, stack) {
      _logger.error('Error removing cache', e, stack);
      rethrow;
    }
  }

  Future<void> clear() async {
    try {
      await _db.delete('cache');
    } catch (e, stack) {
      _logger.error('Error clearing cache', e, stack);
      rethrow;
    }
  }

  Future<void> clearExpired() async {
    try {
      final now = DateTime.now().millisecondsSinceEpoch;
      await _db.delete(
        'cache',
        where: 'expiry < ?',
        whereArgs: [now],
      );
    } catch (e, stack) {
      _logger.error('Error clearing expired cache', e, stack);
      rethrow;
    }
  }
} 