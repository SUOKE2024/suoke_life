import 'package:logger/logger.dart';
import '../../models/user_data.dart';
import 'base_dao_impl.dart';
import 'user_data_dao.dart';

/// 用户数据访问对象实现
class UserDataDaoImpl extends BaseDaoImpl<UserData> implements UserDataDao {
  final Logger _logger = Logger();

  @override
  String get tableName => UserData.tableName;

  @override
  UserData fromMap(Map<String, dynamic> map) => UserData.fromMap(map);

  @override
  Map<String, dynamic> toMap(UserData entity) => entity.toMap();

  @override
  Future<String?> getValue(String key) async {
    try {
      final userData = await findById(key);
      return userData?.value;
    } catch (e) {
      _logger.e('Error getting value for key $key: $e');
      rethrow;
    }
  }

  @override
  Future<void> setValue(String key, String value) async {
    try {
      final now = DateTime.now().millisecondsSinceEpoch;
      final userData = UserData(
        key: key,
        value: value,
        createdAt: now,
        updatedAt: now,
      );
      await insert(userData);
    } catch (e) {
      _logger.e('Error setting value for key $key: $e');
      rethrow;
    }
  }

  @override
  Future<void> removeValue(String key) async {
    try {
      await delete(key);
    } catch (e) {
      _logger.e('Error removing value for key $key: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAllKeys() async {
    try {
      final allData = await findAll();
      return allData.map((data) => data.key).toList();
    } catch (e) {
      _logger.e('Error getting all keys: $e');
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      final db = await getDatabase();
      await db.delete(tableName);
    } catch (e) {
      _logger.e('Error clearing user data: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, String>> getValues(List<String> keys) async {
    try {
      final result = <String, String>{};
      final db = await getDatabase();
      final List<Map<String, dynamic>> maps = await db.query(
        tableName,
        where: 'key IN (${List.filled(keys.length, '?').join(', ')})',
        whereArgs: keys,
      );
      for (var map in maps) {
        final userData = fromMap(map);
        result[userData.key] = userData.value;
      }
      return result;
    } catch (e) {
      _logger.e('Error getting values for keys $keys: $e');
      rethrow;
    }
  }

  @override
  Future<void> setValues(Map<String, String> values) async {
    try {
      final now = DateTime.now().millisecondsSinceEpoch;
      final batch = (await getDatabase()).batch();
      
      values.forEach((key, value) {
        final userData = UserData(
          key: key,
          value: value,
          createdAt: now,
          updatedAt: now,
        );
        batch.insert(
          tableName,
          toMap(userData),
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      });
      
      await batch.commit();
    } catch (e) {
      _logger.e('Error setting multiple values: $e');
      rethrow;
    }
  }
} 