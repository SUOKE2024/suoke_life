import '../../models/user_data.dart';
import 'base_dao.dart';

/// 用户数据访问对象接口
abstract class UserDataDao extends BaseDao<UserData> {
  /// 根据键获取值
  Future<String?> getValue(String key);
  
  /// 设置键值对
  Future<void> setValue(String key, String value);
  
  /// 删除键值对
  Future<void> removeValue(String key);
  
  /// 获取所有键
  Future<List<String>> getAllKeys();
  
  /// 清空所有数据
  Future<void> clear();
  
  /// 批量获取值
  Future<Map<String, String>> getValues(List<String> keys);
  
  /// 批量设置值
  Future<void> setValues(Map<String, String> values);
} 