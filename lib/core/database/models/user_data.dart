import '../base/entity.dart';

/// 用户数据实体
class UserData extends Entity {
  final String key;
  final String value;
  final int createdAt;
  final int updatedAt;

  UserData({
    required this.key,
    required this.value,
    required this.createdAt,
    required this.updatedAt,
  });

  @override
  String get id => key;

  @override
  Map<String, dynamic> toMap() {
    return {
      'key': key,
      'value': value,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }

  factory UserData.fromMap(Map<String, dynamic> map) {
    return UserData(
      key: map['key'] as String,
      value: map['value'] as String,
      createdAt: map['created_at'] as int,
      updatedAt: map['updated_at'] as int,
    );
  }

  static String get tableName => 'user_data';

  static String get createTableSql => '''
    CREATE TABLE IF NOT EXISTS user_data(
      key TEXT PRIMARY KEY,
      value TEXT,
      created_at INTEGER,
      updated_at INTEGER
    )
  ''';

  UserData copyWith({
    String? key,
    String? value,
    int? createdAt,
    int? updatedAt,
  }) {
    return UserData(
      key: key ?? this.key,
      value: value ?? this.value,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'UserData(key: $key, value: $value, createdAt: $createdAt, updatedAt: $updatedAt)';
  }
} 