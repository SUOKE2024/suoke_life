import 'package:logger/logger.dart';
import '../../models/base/entity.dart';
import '../interfaces/base_repository.dart';
import '../../local/dao/base_dao.dart';

/// 仓库实现基类
abstract class BaseRepositoryImpl<T extends Entity> implements BaseRepository<T> {
  final BaseDao<T> _dao;
  final Logger _logger = Logger();

  BaseRepositoryImpl(this._dao);

  @override
  Future<T> save(T entity) async {
    try {
      _logger.i('Saving entity: $entity');
      final id = await _dao.insert(entity);
      final savedEntity = await findById(id);
      if (savedEntity == null) {
        throw Exception('Failed to save entity');
      }
      return savedEntity;
    } catch (e) {
      _logger.e('Error saving entity: $e');
      rethrow;
    }
  }

  @override
  Future<List<T>> saveAll(List<T> entities) async {
    try {
      _logger.i('Saving ${entities.length} entities');
      final ids = await _dao.insertAll(entities);
      final savedEntities = <T>[];
      for (var id in ids) {
        final entity = await findById(id);
        if (entity != null) {
          savedEntities.add(entity);
        }
      }
      return savedEntities;
    } catch (e) {
      _logger.e('Error saving entities: $e');
      rethrow;
    }
  }

  @override
  Future<T?> findById(dynamic id) async {
    try {
      _logger.i('Finding entity by id: $id');
      return await _dao.findById(id);
    } catch (e) {
      _logger.e('Error finding entity by id: $e');
      rethrow;
    }
  }

  @override
  Future<List<T>> findAll() async {
    try {
      _logger.i('Finding all entities');
      return await _dao.findAll();
    } catch (e) {
      _logger.e('Error finding all entities: $e');
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
      _logger.i('Finding entities with conditions: where=$where, whereArgs=$whereArgs');
      return await _dao.findWhere(
        where: where,
        whereArgs: whereArgs,
        orderBy: orderBy,
        limit: limit,
        offset: offset,
      );
    } catch (e) {
      _logger.e('Error finding entities with conditions: $e');
      rethrow;
    }
  }

  @override
  Future<bool> deleteById(dynamic id) async {
    try {
      _logger.i('Deleting entity by id: $id');
      final result = await _dao.delete(id);
      return result > 0;
    } catch (e) {
      _logger.e('Error deleting entity by id: $e');
      rethrow;
    }
  }

  @override
  Future<bool> delete(T entity) async {
    return deleteById(entity.id);
  }

  @override
  Future<bool> deleteAll(List<T> entities) async {
    try {
      _logger.i('Deleting ${entities.length} entities');
      var success = true;
      for (var entity in entities) {
        final result = await delete(entity);
        success = success && result;
      }
      return success;
    } catch (e) {
      _logger.e('Error deleting entities: $e');
      rethrow;
    }
  }

  @override
  Future<bool> exists(dynamic id) async {
    try {
      _logger.i('Checking if entity exists: $id');
      final entity = await findById(id);
      return entity != null;
    } catch (e) {
      _logger.e('Error checking if entity exists: $e');
      rethrow;
    }
  }

  @override
  Future<int> count() async {
    try {
      _logger.i('Counting entities');
      final entities = await findAll();
      return entities.length;
    } catch (e) {
      _logger.e('Error counting entities: $e');
      rethrow;
    }
  }
} 