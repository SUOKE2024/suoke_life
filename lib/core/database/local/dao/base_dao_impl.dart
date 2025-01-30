import 'package:sqflite/sqflite.dart';
import 'package:logger/logger.dart';
import '../config/database_config.dart';
import 'base_dao.dart';

/// 数据访问对象基础实现
abstract class BaseDaoImpl<T> implements BaseDao<T> {
  final Logger _logger = Logger();
  final DatabaseConfig _databaseConfig = DatabaseConfig.instance;

  @override
  Future<Database> getDatabase() async {
    return await _databaseConfig.database;
  }

  @override
  Future<int> insert(T entity) async {
    try {
      final db = await getDatabase();
      final map = toMap(entity);
      _logger.i('Inserting entity into ${tableName}: $map');
      return await db.insert(tableName, map);
    } catch (e) {
      _logger.e('Error inserting entity into ${tableName}: $e');
      rethrow;
    }
  }

  @override
  Future<List<int>> insertAll(List<T> entities) async {
    try {
      final db = await getDatabase();
      final batch = db.batch();
      for (var entity in entities) {
        batch.insert(tableName, toMap(entity));
      }
      _logger.i('Batch inserting ${entities.length} entities into $tableName');
      final results = await batch.commit();
      return results.cast<int>();
    } catch (e) {
      _logger.e('Error batch inserting entities into $tableName: $e');
      rethrow;
    }
  }

  @override
  Future<int> update(T entity) async {
    try {
      final db = await getDatabase();
      final map = toMap(entity);
      _logger.i('Updating entity in $tableName: $map');
      return await db.update(
        tableName,
        map,
        where: 'id = ?',
        whereArgs: [map['id']],
      );
    } catch (e) {
      _logger.e('Error updating entity in $tableName: $e');
      rethrow;
    }
  }

  @override
  Future<int> delete(dynamic id) async {
    try {
      final db = await getDatabase();
      _logger.i('Deleting entity from $tableName with id: $id');
      return await db.delete(
        tableName,
        where: 'id = ?',
        whereArgs: [id],
      );
    } catch (e) {
      _logger.e('Error deleting entity from $tableName: $e');
      rethrow;
    }
  }

  @override
  Future<T?> findById(dynamic id) async {
    try {
      final db = await getDatabase();
      _logger.i('Finding entity in $tableName with id: $id');
      final maps = await db.query(
        tableName,
        where: 'id = ?',
        whereArgs: [id],
      );
      if (maps.isEmpty) return null;
      return fromMap(maps.first);
    } catch (e) {
      _logger.e('Error finding entity in $tableName by id: $e');
      rethrow;
    }
  }

  @override
  Future<List<T>> findAll() async {
    try {
      final db = await getDatabase();
      _logger.i('Finding all entities in $tableName');
      final maps = await db.query(tableName);
      return maps.map((map) => fromMap(map)).toList();
    } catch (e) {
      _logger.e('Error finding all entities in $tableName: $e');
      rethrow;
    }
  }

  @override
  Future<List<T>> findWhere({
    String? where,
    List<dynamic>? whereArgs,
    String? orderBy,
    int? limit,
    int? offset,
  }) async {
    try {
      final db = await getDatabase();
      _logger.i('Finding entities in $tableName with conditions: where=$where, whereArgs=$whereArgs');
      final maps = await db.query(
        tableName,
        where: where,
        whereArgs: whereArgs,
        orderBy: orderBy,
        limit: limit,
        offset: offset,
      );
      return maps.map((map) => fromMap(map)).toList();
    } catch (e) {
      _logger.e('Error finding entities in $tableName with conditions: $e');
      rethrow;
    }
  }
} 