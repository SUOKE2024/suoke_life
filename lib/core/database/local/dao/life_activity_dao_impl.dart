import 'package:logger/logger.dart';
import 'package:sqflite/sqflite.dart';

import '../../models/life_activity_data.dart';
import 'base_dao_impl.dart';
import 'life_activity_dao.dart';

/// 生活活动数据访问对象实现类
class LifeActivityDaoImpl extends BaseDaoImpl<LifeActivityData> implements LifeActivityDao {
  final Logger _logger = Logger();

  LifeActivityDaoImpl(Database database) : super(database);

  @override
  String get tableName => LifeActivityData.tableName;

  @override
  LifeActivityData fromMap(Map<String, dynamic> map) => LifeActivityData.fromMap(map);

  @override
  Future<List<LifeActivityData>> findByUserId(String userId) async {
    try {
      final List<Map<String, dynamic>> maps = await database.query(
        tableName,
        where: 'user_id = ?',
        whereArgs: [userId],
        orderBy: 'time DESC',
      );
      return maps.map((map) => fromMap(map)).toList();
    } catch (e) {
      _logger.e('Error finding activity data by user ID: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeActivityData>> findByUserIdAndType(String userId, String type) async {
    try {
      final List<Map<String, dynamic>> maps = await database.query(
        tableName,
        where: 'user_id = ? AND type = ?',
        whereArgs: [userId, type],
        orderBy: 'time DESC',
      );
      return maps.map((map) => fromMap(map)).toList();
    } catch (e) {
      _logger.e('Error finding activity data by user ID and type: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeActivityData>> findByTimeRange(int startTime, int endTime) async {
    try {
      final List<Map<String, dynamic>> maps = await database.query(
        tableName,
        where: 'time BETWEEN ? AND ?',
        whereArgs: [startTime, endTime],
        orderBy: 'time DESC',
      );
      return maps.map((map) => fromMap(map)).toList();
    } catch (e) {
      _logger.e('Error finding activity data by time range: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeActivityData>> findByUserIdTypeAndTimeRange(
    String userId,
    String type,
    int startTime,
    int endTime,
  ) async {
    try {
      final List<Map<String, dynamic>> maps = await database.query(
        tableName,
        where: 'user_id = ? AND type = ? AND time BETWEEN ? AND ?',
        whereArgs: [userId, type, startTime, endTime],
        orderBy: 'time DESC',
      );
      return maps.map((map) => fromMap(map)).toList();
    } catch (e) {
      _logger.e('Error finding activity data by user ID, type and time range: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeActivityData>> findByLocation(String location) async {
    try {
      final List<Map<String, dynamic>> maps = await database.query(
        tableName,
        where: 'location = ?',
        whereArgs: [location],
        orderBy: 'time DESC',
      );
      return maps.map((map) => fromMap(map)).toList();
    } catch (e) {
      _logger.e('Error finding activity data by location: $e');
      rethrow;
    }
  }

  @override
  Future<LifeActivityData?> findLatest(String userId, String type) async {
    try {
      final List<Map<String, dynamic>> maps = await database.query(
        tableName,
        where: 'user_id = ? AND type = ?',
        whereArgs: [userId, type],
        orderBy: 'time DESC',
        limit: 1,
      );
      return maps.isEmpty ? null : fromMap(maps.first);
    } catch (e) {
      _logger.e('Error finding latest activity data: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getUserActivityTypes(String userId) async {
    try {
      final List<Map<String, dynamic>> maps = await database.rawQuery(
        'SELECT DISTINCT type FROM $tableName WHERE user_id = ?',
        [userId],
      );
      return maps.map((map) => map['type'] as String).toList();
    } catch (e) {
      _logger.e('Error getting user activity types: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAllLocations() async {
    try {
      final List<Map<String, dynamic>> maps = await database.rawQuery(
        'SELECT DISTINCT location FROM $tableName WHERE location IS NOT NULL',
      );
      return maps.map((map) => map['location'] as String).toList();
    } catch (e) {
      _logger.e('Error getting all locations: $e');
      rethrow;
    }
  }

  @override
  Future<int> getTotalDuration(String userId, String type, int startTime, int endTime) async {
    try {
      final List<Map<String, dynamic>> result = await database.rawQuery(
        'SELECT SUM(duration) as total FROM $tableName WHERE user_id = ? AND type = ? AND time BETWEEN ? AND ?',
        [userId, type, startTime, endTime],
      );
      return (result.first['total'] as int?) ?? 0;
    } catch (e) {
      _logger.e('Error getting total duration: $e');
      rethrow;
    }
  }

  @override
  Future<double> getTotalValue(String userId, String type, int startTime, int endTime) async {
    try {
      final List<Map<String, dynamic>> result = await database.rawQuery(
        'SELECT SUM(value) as total FROM $tableName WHERE user_id = ? AND type = ? AND time BETWEEN ? AND ?',
        [userId, type, startTime, endTime],
      );
      return (result.first['total'] as num?)?.toDouble() ?? 0.0;
    } catch (e) {
      _logger.e('Error getting total value: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, int>> getActivityFrequency(
    String userId,
    String type,
    int startTime,
    int endTime,
  ) async {
    try {
      final List<Map<String, dynamic>> result = await database.rawQuery(
        '''
        SELECT date(time/1000, 'unixepoch') as date, COUNT(*) as count 
        FROM $tableName 
        WHERE user_id = ? AND type = ? AND time BETWEEN ? AND ? 
        GROUP BY date
        ''',
        [userId, type, startTime, endTime],
      );
      return Map.fromEntries(
        result.map((row) => MapEntry(row['date'] as String, row['count'] as int)),
      );
    } catch (e) {
      _logger.e('Error getting activity frequency: $e');
      rethrow;
    }
  }

  @override
  Future<void> saveAll(List<LifeActivityData> dataList) async {
    try {
      final batch = database.batch();
      for (final data in dataList) {
        batch.insert(
          tableName,
          data.toMap(),
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      await batch.commit(noResult: true);
    } catch (e) {
      _logger.e('Error saving activity data list: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteByUserId(String userId) async {
    try {
      await database.delete(
        tableName,
        where: 'user_id = ?',
        whereArgs: [userId],
      );
    } catch (e) {
      _logger.e('Error deleting activity data by user ID: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteByType(String userId, String type) async {
    try {
      await database.delete(
        tableName,
        where: 'user_id = ? AND type = ?',
        whereArgs: [userId, type],
      );
    } catch (e) {
      _logger.e('Error deleting activity data by type: $e');
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      await database.delete(tableName);
    } catch (e) {
      _logger.e('Error clearing activity data: $e');
      rethrow;
    }
  }
} 