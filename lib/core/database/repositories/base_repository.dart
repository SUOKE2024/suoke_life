import 'package:injectable/injectable.dart';
import '../database_service.dart';

abstract class BaseRepository {
  final DatabaseService _db;
  
  BaseRepository(this._db);

  Future<List<Map<String, dynamic>>> query(
    String table, {
    bool? distinct,
    List<String>? columns,
    String? where,
    List<Object?>? whereArgs,
    String? groupBy,
    String? having,
    String? orderBy,
    int? limit,
    int? offset,
  }) => _db.query(
    table,
    distinct: distinct,
    columns: columns,
    where: where,
    whereArgs: whereArgs,
    groupBy: groupBy,
    having: having,
    orderBy: orderBy,
    limit: limit,
    offset: offset,
  );

  Future<int> insert(String table, Map<String, Object?> values) => 
    _db.insert(table, values);

  Future<int> update(
    String table,
    Map<String, Object?> values, {
    String? where,
    List<Object?>? whereArgs,
  }) => _db.update(
    table,
    values,
    where: where,
    whereArgs: whereArgs,
  );

  Future<int> delete(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) => _db.delete(
    table,
    where: where,
    whereArgs: whereArgs,
  );
} 