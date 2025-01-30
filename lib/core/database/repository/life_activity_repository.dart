import '../models/life_activity_data.dart';
import 'base_repository.dart';

/// 生活活动数据仓库接口
abstract class LifeActivityRepository extends BaseRepository<LifeActivityData> {
  /// 记录用户活动
  Future<void> recordActivity(LifeActivityData activity);

  /// 获取用户的活动历史
  Future<List<LifeActivityData>> getActivityHistory(String userId, {
    String? type,
    int? startTime,
    int? endTime,
    String? location,
  });

  /// 获取用户的活动统计
  Future<Map<String, dynamic>> getActivityStatistics(String userId, {
    String? type,
    int? startTime,
    int? endTime,
  });

  /// 获取用户的活动趋势
  Future<Map<String, List<dynamic>>> getActivityTrends(String userId, {
    String? type,
    int? startTime,
    int? endTime,
  });

  /// 获取用户的活动建议
  Future<Map<String, String>> getActivityRecommendations(String userId);

  /// 导出用户的活动数据
  Future<String> exportActivityData(String userId, {
    String? type,
    int? startTime,
    int? endTime,
  });

  /// 导入用户的活动数据
  Future<void> importActivityData(String userId, String data);

  /// 同步活动数据到云端
  Future<void> syncToCloud(String userId);

  /// 从云端同步活动数据
  Future<void> syncFromCloud(String userId);

  /// 删除用户的活动数据
  Future<void> deleteUserActivities(String userId, {String? type});

  /// 清空所有活动数据
  Future<void> clearAllActivities();
} 