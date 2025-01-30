import 'package:sqflite/sqflite.dart';

/// 数据访问对象基础接口
abstract class BaseDao<T> {
  /// 获取数据库实例
  Future<Database> getDatabase();

  /// 获取表名
  String get tableName;

  /// 插入单条记录
  Future<int> insert(T entity);

  /// 批量插入记录
  Future<List<int>> insertAll(List<T> entities);

  /// 更新记录
  Future<int> update(T entity);

  /// 删除记录
  Future<int> delete(dynamic id);

  /// 根据ID查询记录
  Future<T?> findById(dynamic id);

  /// 查询所有记录
  Future<List<T>> findAll();

  /// 根据条件查询记录
  Future<List<T>> findWhere({
    String? where,
    List<dynamic>? whereArgs,
    String? orderBy,
    int? limit,
    int? offset,
  });

  /// 将实体转换为Map
  Map<String, dynamic> toMap(T entity);

  /// 将Map转换为实体
  T fromMap(Map<String, dynamic> map);
} 