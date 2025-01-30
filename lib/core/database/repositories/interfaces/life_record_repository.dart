import '../../models/life_record.dart';
import 'base_repository.dart';

/// 生活记录仓库接口
abstract class LifeRecordRepository extends BaseRepository<LifeRecord> {
  /// 获取用户的生活记录
  Future<List<LifeRecord>> getUserRecords(String userId);

  /// 获取指定分类的记录
  Future<List<LifeRecord>> getRecordsByCategory(String category);

  /// 获取包含指定标签的记录
  Future<List<LifeRecord>> getRecordsByTag(String tag);

  /// 获取指定时间范围的记录
  Future<List<LifeRecord>> getRecordsByTimeRange(String startTime, String endTime);

  /// 获取指定位置的记录
  Future<List<LifeRecord>> getRecordsByLocation(String location);

  /// 搜索记录
  Future<List<LifeRecord>> searchRecords(String keyword);

  /// 获取所有可用分类
  Future<List<String>> getAvailableCategories();

  /// 获取所有使用过的标签
  Future<List<String>> getUsedTags();

  /// 获取所有记录过的位置
  Future<List<String>> getRecordedLocations();

  /// 获取用户的记录统计
  Future<Map<String, int>> getUserStats(String userId);

  /// 批量保存记录
  Future<void> saveRecords(List<LifeRecord> records);

  /// 删除用户的所有记录
  Future<void> deleteUserRecords(String userId);

  /// 清空所有记录
  Future<void> clearAllRecords();

  /// 导出用户记录
  Future<String> exportUserRecords(String userId, String format);

  /// 导入记录
  Future<void> importRecords(String data, String format);

  /// 获取记录的标签统计
  Future<Map<String, int>> getTagStats(String userId);

  /// 获取分类统计
  Future<Map<String, int>> getCategoryStats(String userId);

  /// 获取时间段统计
  Future<Map<String, int>> getTimeStats(String userId, String groupBy);
} 