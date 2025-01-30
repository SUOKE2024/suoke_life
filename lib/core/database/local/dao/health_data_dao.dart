import '../../models/health_data.dart';
import 'base_dao.dart';

/// 健康数据访问对象接口
abstract class HealthDataDao extends BaseDao<HealthData> {
  /// 根据用户ID获取健康数据
  Future<List<HealthData>> findByUserId(String userId);

  /// 根据用户ID和类型获取健康数据
  Future<List<HealthData>> findByUserIdAndType(String userId, String type);

  /// 根据时间范围获取健康数据
  Future<List<HealthData>> findByTimeRange(int startTime, int endTime);

  /// 根据用户ID、类型和时间范围获取健康数据
  Future<List<HealthData>> findByUserIdTypeAndTimeRange(
    String userId,
    String type,
    int startTime,
    int endTime,
  );

  /// 获取最新的健康数据
  Future<HealthData?> findLatest(String userId, String type);

  /// 获取用户的所有健康数据类型
  Future<List<String>> getUserDataTypes(String userId);

  /// 获取数据源列表
  Future<List<String>> getDataSources();

  /// 获取指定类型的平均值
  Future<double?> getAverageValue(String userId, String type, int startTime, int endTime);

  /// 获取指定类型的最大值
  Future<double?> getMaxValue(String userId, String type, int startTime, int endTime);

  /// 获取指定类型的最小值
  Future<double?> getMinValue(String userId, String type, int startTime, int endTime);

  /// 批量保存健康数据
  Future<void> saveAll(List<HealthData> dataList);

  /// 删除用户的所有健康数据
  Future<void> deleteByUserId(String userId);

  /// 删除指定类型的健康数据
  Future<void> deleteByType(String userId, String type);

  /// 清空所有健康数据
  Future<void> clear();
} 