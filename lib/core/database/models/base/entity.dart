/// 数据库实体基类
abstract class Entity {
  /// 实体ID
  dynamic get id;

  /// 将实体转换为Map
  Map<String, dynamic> toMap();

  /// 从Map创建实体
  static Entity fromMap(Map<String, dynamic> map) {
    throw UnimplementedError('Subclasses must implement fromMap');
  }

  /// 获取表名
  static String get tableName {
    throw UnimplementedError('Subclasses must implement tableName');
  }

  /// 获取主键名
  static String get primaryKey => 'id';

  /// 获取创建表的SQL语句
  static String get createTableSql {
    throw UnimplementedError('Subclasses must implement createTableSql');
  }

  /// 获取表的索引SQL语句列表
  static List<String> get createIndexSql => [];

  @override
  String toString() => '${runtimeType}(id: $id)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Entity && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
} 