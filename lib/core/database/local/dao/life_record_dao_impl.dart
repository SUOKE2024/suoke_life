import 'package:logger/logger.dart';
import '../../models/life_record.dart';
import 'base_dao_impl.dart';
import 'life_record_dao.dart';

/// 生活记录数据访问对象实现
class LifeRecordDaoImpl extends BaseDaoImpl<LifeRecord> implements LifeRecordDao {
  final Logger _logger = Logger();

  @override
  String get tableName => LifeRecord.tableName;

  @override
  LifeRecord fromMap(Map<String, dynamic> map) => LifeRecord.fromMap(map);

  @override
  Map<String, dynamic> toMap(LifeRecord entity) => entity.toMap();

  @override
  Future<List<LifeRecord>> findByUserId(String userId) async {
    try {
      return await findWhere(
        where: 'user_id = ?',
        whereArgs: [userId],
        orderBy: 'timestamp DESC',
      );
    } catch (e) {
      _logger.e('Error finding life records by user ID: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> findByCategory(String category) async {
    try {
      return await findWhere(
        where: 'category = ?',
        whereArgs: [category],
        orderBy: 'timestamp DESC',
      );
    } catch (e) {
      _logger.e('Error finding life records by category: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> findByTag(String tag) async {
    try {
      return await findWhere(
        where: 'tags LIKE ?',
        whereArgs: ['%"$tag"%'],
        orderBy: 'timestamp DESC',
      );
    } catch (e) {
      _logger.e('Error finding life records by tag: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> findByTimeRange(String startTime, String endTime) async {
    try {
      return await findWhere(
        where: 'timestamp BETWEEN ? AND ?',
        whereArgs: [startTime, endTime],
        orderBy: 'timestamp ASC',
      );
    } catch (e) {
      _logger.e('Error finding life records by time range: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> findByLocation(String location) async {
    try {
      return await findWhere(
        where: 'location LIKE ?',
        whereArgs: ['%$location%'],
        orderBy: 'timestamp DESC',
      );
    } catch (e) {
      _logger.e('Error finding life records by location: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> search(String keyword) async {
    try {
      return await findWhere(
        where: 'title LIKE ? OR content LIKE ?',
        whereArgs: ['%$keyword%', '%$keyword%'],
        orderBy: 'timestamp DESC',
      );
    } catch (e) {
      _logger.e('Error searching life records: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAllCategories() async {
    try {
      final db = await getDatabase();
      final List<Map<String, dynamic>> maps = await db.query(
        tableName,
        distinct: true,
        columns: ['category'],
      );
      return maps.map((map) => map['category'] as String).toList();
    } catch (e) {
      _logger.e('Error getting all categories: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAllTags() async {
    try {
      final db = await getDatabase();
      final List<Map<String, dynamic>> maps = await db.query(
        tableName,
        columns: ['tags'],
      );
      
      final Set<String> uniqueTags = {};
      for (var map in maps) {
        final tags = List<String>.from(json.decode(map['tags']));
        uniqueTags.addAll(tags);
      }
      
      return uniqueTags.toList();
    } catch (e) {
      _logger.e('Error getting all tags: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAllLocations() async {
    try {
      final db = await getDatabase();
      final List<Map<String, dynamic>> maps = await db.query(
        tableName,
        distinct: true,
        columns: ['location'],
        where: 'location IS NOT NULL',
      );
      return maps.map((map) => map['location'] as String).toList();
    } catch (e) {
      _logger.e('Error getting all locations: $e');
      rethrow;
    }
  }

  @override
  Future<int> getUserRecordCount(String userId) async {
    try {
      final db = await getDatabase();
      final result = await db.rawQuery(
        'SELECT COUNT(*) as count FROM $tableName WHERE user_id = ?',
        [userId],
      );
      return Sqflite.firstIntValue(result) ?? 0;
    } catch (e) {
      _logger.e('Error getting user record count: $e');
      rethrow;
    }
  }

  @override
  Future<void> saveAll(List<LifeRecord> records) async {
    try {
      final batch = (await getDatabase()).batch();
      
      for (var record in records) {
        batch.insert(
          tableName,
          toMap(record),
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      
      await batch.commit();
    } catch (e) {
      _logger.e('Error saving multiple life records: $e');
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
      _logger.e('Error deleting life records by user ID: $e');
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      final db = await getDatabase();
      await db.delete(tableName);
    } catch (e) {
      _logger.e('Error clearing life records: $e');
      rethrow;
    }
  }
} 