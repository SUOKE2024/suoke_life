import '../../models/health_data.dart';
import 'base_repository.dart';

/// 健康数据仓库接口
abstract class HealthDataRepository extends BaseRepository<HealthData> {
  /// 获取用户的健康数据
  Future<List<HealthData>> getUserHealthData(String userId);

  /// 获取用户特定类型的健康数据
  Future<List<HealthData>> getUserHealthDataByType(String userId, String type);

  /// 获取时间范围内的健康数据
  Future<List<HealthData>> getHealthDataByTimeRange(int startTime, int endTime);

  /// 获取用户特定类型和时间范围的健康数据
  Future<List<HealthData>> getUserHealthDataByTypeAndTime(
    String userId,
    String type,
    int startTime,
    int endTime,
  );

  /// 获取最新的健康数据
  Future<HealthData?> getLatestHealthData(String userId, String type);

  /// 获取用户的健康数据类型
  Future<List<String>> getUserHealthDataTypes(String userId);

  /// 获取数据来源列表
  Future<List<String>> getHealthDataSources();

  /// 获取健康数据统计
  Future<Map<String, dynamic>> getHealthDataStats(String userId, String type, int startTime, int endTime);

  /// 批量保存健康数据
  Future<void> saveHealthDataList(List<HealthData> dataList);

  /// 删除用户的健康数据
  Future<void> deleteUserHealthData(String userId);

  /// 删除特定类型的健康数据
  Future<void> deleteHealthDataByType(String userId, String type);

  /// 清空所有健康数据
  Future<void> clearAllHealthData();

  /// 导出健康数据
  Future<String> exportHealthData(String userId, String format);

  /// 导入健康数据
  Future<void> importHealthData(String data, String format);

  /// 获取健康数据趋势分析
  Future<Map<String, dynamic>> getHealthDataTrend(
    String userId,
    String type,
    int startTime,
    int endTime,
    String interval,
  );

  /// 检查健康数据是否在正常范围内
  Future<bool> isHealthDataNormal(String type, double value);

  /// 获取异常的健康数据记录
  Future<List<HealthData>> getAbnormalHealthData(
    String userId,
    String type,
    int startTime,
    int endTime,
  );

  /// 同步外部健康数据
  Future<void> syncExternalHealthData(String source, String userId);
} 