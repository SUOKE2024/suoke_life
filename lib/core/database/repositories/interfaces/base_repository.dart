import '../../models/base/entity.dart';

/// 仓库接口基类
abstract class BaseRepository<T extends Entity> {
  /// 保存实体
  Future<T> save(T entity);

  /// 批量保存实体
  Future<List<T>> saveAll(List<T> entities);

  /// 根据ID查找实体
  Future<T?> findById(dynamic id);

  /// 查找所有实体
  Future<List<T>> findAll();

  /// 根据条件查找实体
  Future<List<T>> findWhere({
    String? where,
    List<dynamic>? whereArgs,
    String? orderBy,
    int? limit,
    int? offset,
  });

  /// 根据ID删除实体
  Future<bool> deleteById(dynamic id);

  /// 删除实体
  Future<bool> delete(T entity);

  /// 批量删除实体
  Future<bool> deleteAll(List<T> entities);

  /// 检查实体是否存在
  Future<bool> exists(dynamic id);

  /// 获取实体数量
  Future<int> count();
} 