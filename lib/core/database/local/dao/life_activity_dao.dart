import '../../models/life_activity_data.dart';
import 'base_dao.dart';

/// 生活活动数据访问对象接口
abstract class LifeActivityDao extends BaseDao<LifeActivityData> {
  /// 根据用户ID获取活动数据
  Future<List<LifeActivityData>> findByUserId(String userId);

  /// 根据用户ID和类型获取活动数据
  Future<List<LifeActivityData>> findByUserIdAndType(String userId, String type);

  /// 根据时间范围获取活动数据
  Future<List<LifeActivityData>> findByTimeRange(int startTime, int endTime);

  /// 根据用户ID、类型和时间范围获取活动数据
  Future<List<LifeActivityData>> findByUserIdTypeAndTimeRange(
    String userId,
    String type,
    int startTime,
    int endTime,
  );

  /// 根据位置获取活动数据
  Future<List<LifeActivityData>> findByLocation(String location);

  /// 获取最新的活动数据
  Future<LifeActivityData?> findLatest(String userId, String type);

  /// 获取用户的所有活动类型
  Future<List<String>> getUserActivityTypes(String userId);

  /// 获取所有活动位置
  Future<List<String>> getAllLocations();

  /// 获取指定类型的活动总时长
  Future<int> getTotalDuration(String userId, String type, int startTime, int endTime);

  /// 获取指定类型的活动总量
  Future<double> getTotalValue(String userId, String type, int startTime, int endTime);

  /// 获取活动频率（每天的活动次数）
  Future<Map<String, int>> getActivityFrequency(
    String userId,
    String type,
    int startTime,
    int endTime,
  );

  /// 批量保存活动数据
  Future<void> saveAll(List<LifeActivityData> dataList);

  /// 删除用户的所有活动数据
  Future<void> deleteByUserId(String userId);

  /// 删除指定类型的活动数据
  Future<void> deleteByType(String userId, String type);

  /// 清空所有活动数据
  Future<void> clear();
} 