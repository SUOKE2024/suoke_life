import '../../models/life_record.dart';
import 'base_dao.dart';

/// 生活记录数据访问对象接口
abstract class LifeRecordDao extends BaseDao<LifeRecord> {
  /// 根据用户ID获取生活记录
  Future<List<LifeRecord>> findByUserId(String userId);

  /// 根据分类获取生活记录
  Future<List<LifeRecord>> findByCategory(String category);

  /// 根据标签获取生活记录
  Future<List<LifeRecord>> findByTag(String tag);

  /// 根据时间范围获取生活记录
  Future<List<LifeRecord>> findByTimeRange(String startTime, String endTime);

  /// 根据位置获取生活记录
  Future<List<LifeRecord>> findByLocation(String location);

  /// 搜索生活记录
  Future<List<LifeRecord>> search(String keyword);

  /// 获取所有分类
  Future<List<String>> getAllCategories();

  /// 获取所有标签
  Future<List<String>> getAllTags();

  /// 获取所有位置
  Future<List<String>> getAllLocations();

  /// 获取用户的记录数量
  Future<int> getUserRecordCount(String userId);

  /// 批量保存生活记录
  Future<void> saveAll(List<LifeRecord> records);

  /// 删除用户的所有记录
  Future<void> deleteByUserId(String userId);

  /// 清空所有记录
  Future<void> clear();
} 