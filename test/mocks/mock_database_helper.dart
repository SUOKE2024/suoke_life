import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/core/database/database_helper.dart';

class MockDatabaseHelper extends Mock implements DatabaseHelper {
  final Map<String, List<Map<String, dynamic>>> _data = {};

  @override
  Future<void> init() async {
    // 不需要实际初始化
  }

  @override
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
  }) async {
    return _data[table] ?? [];
  }

  @override
  Future<int> insert(String table, Map<String, Object?> values) async {
    _data[table] ??= [];
    _data[table]!.add(Map<String, dynamic>.from(values));
    return 1;
  }

  @override
  Future<int> update(
    String table,
    Map<String, Object?> values, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    return 1;
  }

  @override
  Future<int> delete(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    return 1;
  }

  @override
  Future<void> execute(String sql) async {
    // 不需要实际执行 SQL
  }
} 