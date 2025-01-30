import '../../models/user_data.dart';
import 'base_repository.dart';

/// 用户数据仓库接口
abstract class UserDataRepository extends BaseRepository<UserData> {
  /// 获取用户数据值
  Future<String?> getValue(String key);

  /// 设置用户数据值
  Future<void> setValue(String key, String value);

  /// 删除用户数据
  Future<void> removeValue(String key);

  /// 获取所有用户数据键
  Future<List<String>> getAllKeys();

  /// 清空所有用户数据
  Future<void> clear();

  /// 批量获取用户数据值
  Future<Map<String, String>> getValues(List<String> keys);

  /// 批量设置用户数据值
  Future<void> setValues(Map<String, String> values);

  /// 获取用户设置
  Future<Map<String, dynamic>> getSettings();

  /// 更新用户设置
  Future<void> updateSettings(Map<String, dynamic> settings);

  /// 获取用户偏好
  Future<Map<String, dynamic>> getPreferences();

  /// 更新用户偏好
  Future<void> updatePreferences(Map<String, dynamic> preferences);
} 