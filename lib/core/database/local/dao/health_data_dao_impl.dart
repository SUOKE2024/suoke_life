import 'package:logger/logger.dart';
import '../../models/health_data.dart';
import 'base_dao_impl.dart';
import 'health_data_dao.dart';

/// 健康数据访问对象实现
class HealthDataDaoImpl extends BaseDaoImpl<HealthData> implements HealthDataDao {
  final Logger _logger = Logger();

  @override
  String get tableName => HealthData.tableName;

  @override
  HealthData fromMap(Map<String, dynamic> map) => HealthData.fromMap(map);

  @override
  Map<String, dynamic> toMap(HealthData entity) => entity.toMap();

  @override
  Future<List<HealthData>> findByUserId(String userId) async {
    try {
      return await findWhere(
        where: 'user_id = ?',
        whereArgs: [userId],
        orderBy: 'time DESC',
      );
    } catch (e) {
      _logger.e('Error finding health data by user ID: $e');
      rethrow;
    }
  }

  @override
  Future<List<HealthData>> findByUserIdAndType(String userId, String type) async {
    try {
      return await findWhere(
        where: 'user_id = ? AND type = ?',
        whereArgs: [userId, type],
        orderBy: 'time DESC',
      );
    } catch (e) {
      _logger.e('Error finding health data by user ID and type: $e');
      rethrow;
    }
  }

  @override
  Future<List<HealthData>> findByTimeRange(int startTime, int endTime) async {
    try {
      return await findWhere(
        where: 'time BETWEEN ? AND ?',
        whereArgs: [startTime, endTime],
        orderBy: 'time ASC',
      );
    } catch (e) {
      _logger.e('Error finding health data by time range: $e');
      rethrow;
    }
  }

  @override
  Future<List<HealthData>> findByUserIdTypeAndTimeRange(
    String userId,
    String type,
    int startTime,
    int endTime,
  ) async {
    try {
      return await findWhere(
        where: 'user_id = ? AND type = ? AND time BETWEEN ? AND ?',
        whereArgs: [userId, type, startTime, endTime],
        orderBy: 'time ASC',
      );
    } catch (e) {
      _logger.e('Error finding health data by user ID, type and time range: $e');
      rethrow;
    }
  }

  @override
  Future<HealthData?> findLatest(String userId, String type) async {
    try {
      final results = await findWhere(
        where: 'user_id = ? AND type = ?',
        whereArgs: [userId, type],
        orderBy: 'time DESC',
        limit: 1,
      );
      return results.isNotEmpty ? results.first : null;
    } catch (e) {
      _logger.e('Error finding latest health data: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getUserDataTypes(String userId) async {
    try {
      final db = await getDatabase();
      final List<Map<String, dynamic>> maps = await db.query(
        tableName,
        distinct: true,
        columns: ['type'],
        where: 'user_id = ?',
        whereArgs: [userId],
      );
      return maps.map((map) => map['type'] as String).toList();
    } catch (e) {
      _logger.e('Error getting user data types: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getDataSources() async {
    try {
      final db = await getDatabase();
      final List<Map<String, dynamic>> maps = await db.query(
        tableName,
        distinct: true,
        columns: ['source'],
      );
      return maps.map((map) => map['source'] as String).toList();
    } catch (e) {
      _logger.e('Error getting data sources: $e');
      rethrow;
    }
  }

  @override
  Future<double?> getAverageValue(String userId, String type, int startTime, int endTime) async {
    try {
      final db = await getDatabase();
      final result = await db.rawQuery('''
        SELECT AVG(value) as avg_value 
        FROM $tableName 
        WHERE user_id = ? AND type = ? AND time BETWEEN ? AND ?
      ''', [userId, type, startTime, endTime]);
      return result.first['avg_value'] as double?;
    } catch (e) {
      _logger.e('Error getting average value: $e');
      rethrow;
    }
  }

  @override
  Future<double?> getMaxValue(String userId, String type, int startTime, int endTime) async {
    try {
      final db = await getDatabase();
      final result = await db.rawQuery('''
        SELECT MAX(value) as max_value 
        FROM $tableName 
        WHERE user_id = ? AND type = ? AND time BETWEEN ? AND ?
      ''', [userId, type, startTime, endTime]);
      return result.first['max_value'] as double?;
    } catch (e) {
      _logger.e('Error getting max value: $e');
      rethrow;
    }
  }

  @override
  Future<double?> getMinValue(String userId, String type, int startTime, int endTime) async {
    try {
      final db = await getDatabase();
      final result = await db.rawQuery('''
        SELECT MIN(value) as min_value 
        FROM $tableName 
        WHERE user_id = ? AND type = ? AND time BETWEEN ? AND ?
      ''', [userId, type, startTime, endTime]);
      return result.first['min_value'] as double?;
    } catch (e) {
      _logger.e('Error getting min value: $e');
      rethrow;
    }
  }

  @override
  Future<void> saveAll(List<HealthData> dataList) async {
    try {
      final batch = (await getDatabase()).batch();
      
      for (var data in dataList) {
        batch.insert(
          tableName,
          toMap(data),
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      
      await batch.commit();
    } catch (e) {
      _logger.e('Error saving multiple health data: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteByUserId(String userId) async {
    try {
      final db = await getDatabase();
      await db.delete(
        tableName,
        where: 'user_id = ?',
        whereArgs: [userId],
      );
    } catch (e) {
      _logger.e('Error deleting health data by user ID: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteByType(String userId, String type) async {
    try {
      final db = await getDatabase();
      await db.delete(
        tableName,
        where: 'user_id = ? AND type = ?',
        whereArgs: [userId, type],
      );
    } catch (e) {
      _logger.e('Error deleting health data by type: $e');
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      final db = await getDatabase();
      await db.delete(tableName);
    } catch (e) {
      _logger.e('Error clearing health data: $e');
      rethrow;
    }
  }
} 